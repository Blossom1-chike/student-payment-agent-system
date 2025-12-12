# test_payment_agent.py - PURE LLM APPROACH

import os
import base64
from typing import Optional
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from graph.state import UniversityState
from agents.payment_agent import payment_agent
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# BUILD GRAPH
# ============================================================================

def load_image_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()

def build_payment_graph():
    workflow = StateGraph(UniversityState)
    workflow.add_node("payment_agent", payment_agent)
    workflow.set_entry_point("payment_agent")
    
    def should_continue(state: UniversityState):
        last = state["messages"][-1]

        # If assistant spoke last, STOP
        if not isinstance(last, HumanMessage):
            return END

        # Continue only if user spoke AND no payment link exists
        if state.get("payment_link"):
            return END
    
        return "payment_agent"
    
    workflow.add_conditional_edges(
        "payment_agent",
        should_continue,
        {"payment_agent": "payment_agent", END: END}
    )
    
    return workflow.compile()

graph = build_payment_graph()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_image_as_base64(image_path: str) -> str:
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def create_initial_state():
    return {
        "messages": [],
        # "student_id": None,
        # "student_name": None,
        # "amount": None,
        # "payment_link": None,
        # "unmatched_payments": None,
        # "payment_matched": None,
        # "support_ticket_id": None,
        # "issue_resolved": None,
        # "appointment_time": None,
        # "appointment_confirmed": None,
        # "agent_route": None
    }

def chat(user_input: str, image_path: Optional[str] = None, state: Optional[UniversityState] = None):
    """Pure chat - no command parsing"""
    
    content = []
    
    if image_path and os.path.exists(image_path):
        image_base64 = load_image_as_base64(image_path)
        ext = os.path.splitext(image_path)[1].lower()
        media_type = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png'}.get(ext.strip('.'), 'image/jpeg')
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:{media_type};base64,{image_base64}"}
        })
    
    content.append({"type": "text", "text": user_input})
    
    human_message = HumanMessage(content=content)
    
    if state is None:
        current_state = create_initial_state()
        current_state["messages"] = [human_message]
    else:
        current_state = state.copy()
        current_state["messages"] = current_state.get("messages", []) + [human_message]
    
    result = app.invoke(current_state)
    
    last_message = result["messages"][-1]
    if hasattr(last_message, 'content'):
        if isinstance(last_message.content, str):
            response_text = last_message.content
        elif isinstance(last_message.content, list):
            response_text = ""
            for block in last_message.content:
                if isinstance(block, dict) and block.get('type') == 'text':
                    response_text += block.get('text', '')
                elif hasattr(block, 'text'):
                    response_text += block.text
        else:
            response_text = str(last_message.content)
    else:
        response_text = str(last_message)
    
    return response_text, result

# ============================================================================
# PURE CHAT MODE - NO COMMANDS
# ============================================================================

def run():
    # Example
    img_path = "images/student_id.jpeg"
    image = load_image_bytes(img_path)

    state: UniversityState = {"messages":[], "image_bytes": image}

    while True:
        user_input = input("Message: ")
        if user_input == "exit":
            print("Bye..")
            break

        # Create proper message object
        user_message = HumanMessage(content=user_input)
        state["messages"] = state.get("messages",[]) + [user_message] 
        
        # Invoke the graph
        result = graph.invoke(state)
        
        # Update state with results
        state["messages"].append(result["messages"][-1])
        
        # Print the last assistant message
        if result.get("messages") and len(result["messages"])>0:
            last_message = result["messages"][-1]
            if hasattr(last_message, 'content'):
                print(f"Assistant: {last_message.content}")
            else:
                print(f"Assistant: {last_message}")

if __name__ == "__main__":
    run()