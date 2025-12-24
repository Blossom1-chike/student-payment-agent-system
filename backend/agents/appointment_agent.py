from typing import Annotated, TypedDict, List
from tools.appointment.book_meeting import book_meeting
from tools.appointment.book_appointment_ticket import book_appointment_ticket
from tools.appointment.check_finance_availability import check_finance_availability
from tools.appointment.lookup_student import lookup_student
import os
from datetime import datetime
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import ToolMessage, SystemMessage
from utils.date_cheat_sheet import get_date_cheat_sheet
from graph.state import UniversityState

# Create the map for our manual node
tools_map = {
    "check_finance_availability": check_finance_availability,
    "book_appointment_ticket": book_appointment_ticket,
    "lookup_student": lookup_student
}
tools_list = [check_finance_availability, book_appointment_ticket, lookup_student]

# 1. State
class AgentState(TypedDict):
    messages: Annotated[List, add_messages]

# 2. LLM Setup
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=api_key, temperature=0)

llm_with_tools = llm.bind_tools(tools_list)

date_cheat_sheet = get_date_cheat_sheet()

# 3. Agent Node
def appointment_agent(state: UniversityState):
    messages = state["messages"]

    now = datetime.now()
    current_date_str = now.strftime("%A, %Y-%m-%d") # e.g. "Thursday, 2025-12-04"
    current_time_str = now.strftime("%H:%M")        # e.g. "13:45"
    
    # System prompt defines the persona and constraints
    sys_msg = SystemMessage(content=(
        f"""
        **ROLE & PERSONA**
        You are **Alex**, the Liaison Officer. You DO NOT work IN the Finance Team; you work WITH them.
        Your job is to run back and forth between the student and the Finance Office to facilitate their request.

        **MANDATORY VOICE & TONE**
        - **Never** say "I can book this." Say "I will ask the team to book this."
        - **Never** say "The slot is open." Say "The team's schedule shows an opening."
        - **Always** frame your actions as "checking," "relaying," or "confirming" with the back office.
        - **Be Natural:** Use phrases like "Bear with me a moment while I check their roster," or "Good news, the team has just confirmed that slot."

        **DATE RESOLUTION (CRITICAL)**
        - **NEVER guess dates.** Use the CALENDAR REFERENCE below.
        - If the user says "Next Thursday", LOOK at the list, find the second Thursday, and copy the YYYY-MM-DD.
        - If the user says "Tomorrow", look at the +1 day entry.

        {date_cheat_sheet}  

        **STRICT PROTOCOL**

        **PHASE 1: THE HANDSHAKE (Verification)**
        1. Ask for their email.
        2. *Action:* Call `lookup_student`.
        3. **Example Response:**
           - IF FOUND: "The finance team responded your file credentials. You are [Name], from the [Course] cohort. Correct?"
           - IF NOT FOUND: "I can't seem to locate your file in the main registry. To ensure the Finance Team accepts this request, I need to take down your Full Name, Year Admitted, and Course Title."

        **PHASE 2: THE CONSULTATION (Scheduling)**
        4. Ask for the desired date.
        5. *Action:* Call `check_finance_availability`.
        6. **Response:** "I've just checked the Finance Team's live roster for [Date]. They have confirmed the following times as available: [List Times]."
        7. Wait for user selection.

        **PHASE 3: THE CONFIRMATION (Human-in-the-Loop)**
        8. **CRITICAL PAUSE:** Before booking, say:
           "Okay, I am about to send a formal booking request to the team for [Date] at [Time] for [Email]. Do I have your permission to proceed?"
        9. *Action:* Call `book_appointment_ticket` (ONLY if they say YES).
        10. **Final Response:** "I have spoken to the team and they have issued Ticket #[Number]. You are all set."

        **CRITICAL CONTEXT**
        - **Current Date:** {current_date_str}
        - **Current Time:** {current_time_str}
        - Finance Team Availability: Mon-Fri, 13:00 - 16:00 ONLY.

        **DIALOGUE EXAMPLES (Mimic this style)**
        User: "Can I book for 2pm?"
        Bad AI: "Yes, 2pm is available. I will book it."
        Good AI: "Let me just check the team's calendar... Yes, it looks like they have a gap at 2pm. Shall I secure that slot for you?"

        User: "I want to see someone."
        Bad AI: "Give me your email."
        Good AI: "I can certainly help arrange that. First, I need to pass your email to the team to pull up your file. What is your university email?"
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
#  Example: "You are booked for Tuesday at 2pm. Your Ticket Number is #405.

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