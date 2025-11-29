# main.py

from typing import Optional
from langchain_core.messages import HumanMessage
from graph.state import UniversityState
from graph.workflow import build_graph
from dotenv import load_dotenv
from agents.orchestrator import orchestrator, router
from agents.payment_agent import payment_agent
from agents.reconciliation_agent import reconciliation_agent

# Load environment variables
load_dotenv()

# Build the workflow graph
app = build_graph()

AGENTS = {
    "payment_agent": payment_agent,
    "reconciliation_agent": reconciliation_agent,
}

def chat(user_input: str, state: Optional[UniversityState] = None, image_bytes: Optional[bytes] = None):
    """Chat with the multi-agent system"""

    print(state, "message object")
    if state is None:
        # Initialize new conversation
        current_state = {
            "messages": [HumanMessage(content=user_input)],
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
        if image_bytes:
            current_state["image_bytes"] = image_bytes
    
    # Step 1 → orchestrator decides which agent
    classification = orchestrator(current_state)
    current_state.update(classification)  # store chosen agent

    # Step 2 → router maps to actual agent
    agent_name = router(current_state)
    agent_func = AGENTS[agent_name]

    # Step 3 → run the agent
    result = agent_func(current_state)

    # Step 4 → update state with new info (everything except messages)
    for k, v in result.items():
        if k != "messages":
            current_state[k] = v
            
    if "messages" in result:
        current_state["messages"].extend(result["messages"])

    # Step 5 → return last agent message + updated state
    last_message = result["messages"][-1]
    response_text = last_message.content if hasattr(last_message, "content") else str(last_message)
    print("this is current text message", current_state, "message object",  response_text)
    return response_text, current_state

    # # Run the graph
    # result = app.invoke(current_state)
    
    # # Extract last response
    # last_message = result["messages"][-1]
    # response_text = last_message.content if hasattr(last_message, 'content') else str(last_message)
    
    # return response_text, result

# def main():
#     """Run interactive chat session"""
    
#     print("🎓 Northumbria University Payment System")
#     print("=" * 60)
#     print("Multi-Agent System with:")
#     print("  💳 Payment Agent")
#     print("  🔄 Reconciliation Agent")
#     print("  🆘 Support Agent")
#     print("  📅 Appointment Agent")
#     print("=" * 60)
#     print("Type 'quit' to exit\n")
    
#     state = None
    
#     while True:
#         user_input = input("You: ").strip()
        
#         if user_input.lower() in ['quit', 'exit', 'q']:
#             print("\n👋 Goodbye!")
#             break
        
#         if not user_input:
#             continue
        
#         try:
#             print()  # Blank line for readability
#             response, state = chat(user_input, state)
#             print(f"\n🤖 Agent: {response}\n")
#             print("-" * 60)
            
#         except Exception as e:
#             print(f"\n❌ Error: {e}\n")
#             import traceback
#             traceback.print_exc()

# if __name__ == "__main__":
#     main()