# backend/agents/info_agent.py
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from graph.state import UniversityState
# Import the tool
from tools.info.info_search import search_university_info

# Setup LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
tools = [search_university_info]
llm_with_tools = llm.bind_tools(tools)

async def info_agent(state: UniversityState):
    """
    Agent that answers general questions by searching the university website.
    """
    messages = state["messages"]
    
    # System Prompt
    system_msg = SystemMessage(content="""
    You are the Northumbria University Information Assistant.
    
    Your goal is to answer student questions accurately using the search tool.
                               
    GUIDELINES:
    1. ALWAYS use the `search_university_info` tool if you don't know the answer. 
    2. **FORMATTING IS CRITICAL:**
       - If listing events, courses, or locations, USE A MARKDOWN TABLE or clear Bullet Points.
       - **Table Format:** | Event Name | Date | Time | Location |
       - **List Format:** * **Event Name**
           - 📅 Date: ...
           - ⏰ Time: ...
           - 📍 Location: ...
    3. If a date is missing, say "Date to be confirmed".
    4. Provide links to the source pages at the bottom.
    5.  If the search results are unclear, advice them to speak to the university Ask4Help team at the reception.
    """)
    
    context = [system_msg] + messages
    
    # --- ReAct Loop (Standard Pattern) ---
    while True:
        response = await llm_with_tools.ainvoke(context)
        
        # If no tool calls, we are done
        if not response.tool_calls:
            # Return new messages (skipping system prompt)
            return {"messages": [response]}
        
        # If tool called, execute it
        context.append(response)
        
        for tool_call in response.tool_calls:
            print(f"🔍 Info Agent searching: {tool_call['args']}")
            
            tool_result = search_university_info.invoke(tool_call['args'])
            
            context.append({
                "role": "tool",
                "content": str(tool_result),
                "tool_call_id": tool_call['id'],
                "name": tool_call['name']
            })