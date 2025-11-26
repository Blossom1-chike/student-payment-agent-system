# main.py

from typing import Optional
from langchain_core.messages import HumanMessage
from graph import UniversityState, build_graph
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build the workflow graph
app = build_graph()

def chat(user_input: str, state: Optional[UniversityState] = None):
    """Chat with the multi-agent system"""
    
    human_message = HumanMessage(content=user_input)
    
    if state is None:
        # Initialize new conversation
        current_state = {
            "messages": [human_message],
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
    else:
        # Continue existing conversation
        current_state = state.copy()
        current_state["messages"] = state["messages"] + [human_message]
    
    # Run the graph
    result = app.invoke(current_state)
    
    # Extract last response
    last_message = result["messages"][-1]
    response_text = last_message.content if hasattr(last_message, 'content') else str(last_message)
    
    return response_text, result

def main():
    """Run interactive chat session"""
    
    print("🎓 Northumbria University Payment System")
    print("=" * 60)
    print("Multi-Agent System with:")
    print("  💳 Payment Agent")
    print("  🔄 Reconciliation Agent")
    print("  🆘 Support Agent")
    print("  📅 Appointment Agent")
    print("=" * 60)
    print("Type 'quit' to exit\n")
    
    state = None
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        if not user_input:
            continue
        
        try:
            print()  # Blank line for readability
            response, state = chat(user_input, state)
            print(f"\n🤖 Agent: {response}\n")
            print("-" * 60)
            
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()