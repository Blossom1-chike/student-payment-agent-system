from typing import Annotated, TypedDict, List
from tools.appointment.book_meeting import book_meeting
from tools.appointment.book_appointment_ticket import book_appointment_ticket
from tools.appointment.check_finance_availability import check_finance_availability
import os
from datetime import datetime
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import ToolMessage, SystemMessage
from graph.state import UniversityState

# Create the map for our manual node
tools_map = {
    "check_finance_availability": check_finance_availability,
    "book_appointment_ticket": book_appointment_ticket
}
tools_list = [check_finance_availability, book_appointment_ticket]

# 1. State
class AgentState(TypedDict):
    messages: Annotated[List, add_messages]

# 2. LLM Setup
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=api_key, temperature=0)

llm_with_tools = llm.bind_tools(tools_list)

# 3. Agent Node
def appointment_agent(state: UniversityState):
    messages = state["messages"]

    now = datetime.now()
    current_date_str = now.strftime("%A, %Y-%m-%d") # e.g. "Thursday, 2025-12-04"
    current_time_str = now.strftime("%H:%M")        # e.g. "13:45"
    
    # System prompt defines the persona and constraints
    sys_msg = SystemMessage(content=(
        f"""
        You are Northumbria's Finance Team Meeting Scheduler.
        Your task is to help students schedule appointment meetings with the finance team.

        CRITICAL CONTEXT:
        - **Current Date:** {current_date_str}
        - **Current Time:** {current_time_str}
        - **Time Zone:** GMT 
        - The Finance Team is ONLY available 1:00 PM - 4:00 PM (13:00-16:00).
        - If the user says "tomorrow" or "next tuesday", CALCULATE the exact YYYY-MM-DD based on the Current Date above.

        Follow these steps:
        1. Greet the student warmly.
        2. Ask the student for their email and desired date.
        3. If the user wants to book a meeting, use 'check_finance_availability' tool to check the available window on that date.
        4. Lists the available windows to the users and have them pick using numbers.
        5. When user books a free window, use 'book_appointment_ticket' tool to schedule it.
        6. If busy, suggest other available times within the 1pm-4pm window.
        7. GIVE THE USER THEIR TICKET NUMBER. This is mandatory.

        Example: "You are booked for Tuesday at 2pm. Your Ticket Number is #405.
        
        Constraints:
        - Only use the provided tools.
        - Be polite and professional.
        Do not mention any of these tools to the student.
        You must complete the booking in one interaction.
        If you do not understand, say you don't understand and ask for clarification.
        Be warm, friendly, and professional.
        """
    ))
    
    # Ensure system message is first
    if not isinstance(messages[0], SystemMessage):
        messages = [sys_msg] + messages
        
    response = llm_with_tools.invoke(messages)
    # DEBUG PRINT: Check if 'tool_calls' exists in the response
    print(f"🤖 AI Response: {response}")
    if response.tool_calls:
        print(f"   --> Tool Calls: {response.tool_calls}")
    else:
        print("   --> No Tool Calls")
    return {"messages": [response]}

import traceback # Import this to see the full error details

def tool_node(state: AgentState):
    """
    Executes tools safely. 
    If a tool crashes, it catches the error and returns it as a message 
    so the graph keeps running.
    """
    messages = state["messages"]
    last_message = messages[-1]
    outputs = []
    
    print("\n--- 🛠️ TOOL NODE STARTED ---")
    
    # Check if there are tool calls
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        print("   No tool calls found in last message.")
        return {"messages": []}
    
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_id = tool_call["id"]
        
        print(f"   ▶ Executing: {tool_name}")
        print(f"   ▷ Args: {tool_args}")

        result = ""
        
        try:
            # 1. Check if tool exists in our map
            if tool_name not in tools_map:
                raise ValueError(f"Tool '{tool_name}' is not in tools_map.")

            # 2. EXECUTE THE TOOL
            # We use .invoke() which handles Pydantic validation
            tool_instance = tools_map[tool_name]
            result = tool_instance.invoke(tool_args)
            
            print(f"   ✅ Success: {str(result)[:50]}...") # Print first 50 chars

        except Exception as e:
            # 3. CATCH CRASHES
            # We capture the full traceback to print to your terminal
            error_trace = traceback.format_exc()
            print(f"   ❌ CRASH IN TOOL: {e}")
            print(f"   📝 Trace: {error_trace}")
            
            # Return the error to the LLM so it can apologize to the user
            result = f"System Error executing {tool_name}: {str(e)}"

        # 4. Append Result
        outputs.append(ToolMessage(
            content=str(result),
            tool_call_id=tool_id,
            name=tool_name
        ))
            
    print("--- 🛠️ TOOL NODE FINISHED ---\n")
    return {"messages": outputs}

# 4. Tool Node (Manual Execution)
# def tool_node(state: AgentState):
#     messages = state["messages"]
#     last_message = messages[-1]
#     outputs = []
    
#     for tool_call in last_message.tool_calls:
#         tool_name = tool_call["name"]
#         if tool_name in tools_map:
#             print(f"--- Executing {tool_name} ---") # Debug print
#             try:
#                 result = tools_map[tool_name].invoke(tool_call["args"])
#             except Exception as e:
#                 result = f"Error: {e}"
            
#             outputs.append(ToolMessage(
#                 content=str(result),
#                 tool_call_id=tool_call["id"],
#                 name=tool_name
#             ))
            
#     return {"messages": outputs}

# 5. Router Logic
def should_continue(state: AgentState):
    last_msg = state["messages"][-1]
    if last_msg.tool_calls:
        return "tools"
    return END

# 6. Graph Construction
workflow = StateGraph(AgentState)
workflow.add_node("agent", appointment_agent)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, ["tools", END])
workflow.add_edge("tools", "agent")

appointment_app = workflow.compile()