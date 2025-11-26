# test_payment_agent.py - SIMPLIFIED

import os
import base64
from typing import Optional
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from graph.state import UniversityState
from agents.payment_agent import payment_agent
from dotenv import load_dotenv

load_dotenv()

def build_payment_graph():
    """Build a simple graph with just the payment agent"""
    
    workflow = StateGraph(UniversityState)
    workflow.add_node("payment_agent", payment_agent)
    workflow.set_entry_point("payment_agent")
    
    def should_continue(state: UniversityState):
        if state.get('payment_link'):
            return END
        return "payment_agent"
    
    workflow.add_conditional_edges(
        "payment_agent",
        should_continue,
        {
            "payment_agent": "payment_agent",
            END: END
        }
    )
    
    return workflow.compile()

app = build_payment_graph()

def load_image_as_base64(image_path: str) -> str:
    """Load image file and convert to base64"""
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def create_initial_state():
    """Create a fresh state"""
    return {
        "messages": [],
        "student_id": None,
        "student_name": None,
        "amount": None,
        "payment_link": None,
        "unmatched_payments": None,
        "payment_matched": None,
        "support_ticket_id": None,
        "issue_resolved": None,
        "appointment_time": None,
        "appointment_confirmed": None,
        "agent_route": None
    }

def chat(user_input: str, image_path: Optional[str] = None, state: Optional[UniversityState] = None):
    """
    Chat with payment agent - agent decides which tools to use
    
    YOU just provide:
    - user_input: What the user says
    - image_path: Optional image file
    - state: Previous conversation state
    
    THE AGENT decides:
    - When to call extract_name_from_id
    - When to call create_payment_link
    - What to say to the user
    """
    
    # Build message content
    content = []
    
    # Add image if provided
    if image_path:
        image_base64 = load_image_as_base64(image_path)
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image_base64}"
            }
        })
    
    # Add text
    content.append({
        "type": "text",
        "text": user_input
    })
    
    # Create message
    human_message = HumanMessage(content=content)
    
    # Initialize or update state
    if state is None:
        current_state = create_initial_state()
        current_state["messages"] = [human_message]
    else:
        current_state = state.copy()
        current_state["messages"] = state["messages"] + [human_message]
    
    # Run the agent - IT DECIDES WHAT TO DO
    result = app.invoke(current_state)
    
    # Extract response
    last_message = result["messages"][-1]
    response_text = last_message.content if hasattr(last_message, 'content') else str(last_message)
    
    return response_text, result

# ============================================================================
# INTERACTIVE MODE
# ============================================================================

def main():
    """Interactive testing - just chat naturally"""
    
    print("\n" + "=" * 60)
    print("🧪 PAYMENT AGENT TEST - Interactive Mode")
    print("=" * 60)
    print("\nJust chat naturally! The agent will:")
    print("  - Decide when to extract info from images")
    print("  - Decide when to create payment links")
    print("  - Guide you through the process")
    print("\nCommands:")
    print("  'quit' - Exit")
    print("  'upload <path>' - Upload an image")
    print("  'state' - Show current state")
    print("  'reset' - Start over")
    print("=" * 60 + "\n")
    
    state = None
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        if user_input.lower() == 'state':
            print("\n📊 Current State:")
            if state:
                print(f"   Student ID: {state.get('student_id')}")
                print(f"   Student Name: {state.get('student_name')}")
                print(f"   Amount: {state.get('amount')}")
                print(f"   Payment Link: {state.get('payment_link')}")
            else:
                print("   (No conversation started yet)")
            print()
            continue
        
        if user_input.lower() == 'reset':
            state = None
            print("\n🔄 Conversation reset\n")
            continue
        
        if user_input.lower().startswith('upload '):
            image_path = user_input[7:].strip()
            if not os.path.exists(image_path):
                print(f"\n❌ Image not found: {image_path}\n")
                continue
            
            try:
                # Agent will automatically use extract_student_info tool
                response, state = chat("Here's my student ID", image_path=image_path, state=state)
                print(f"\n🤖 Agent: {response}\n")
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
                import traceback
                traceback.print_exc()
            continue
        
        if not user_input:
            continue
        print(user_input, "---", state)
        try:
            # Just chat - agent decides what tools to use
            response, state = chat(user_input, state=state)
            print(f"\n🤖 Agent: {response}\n")
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
