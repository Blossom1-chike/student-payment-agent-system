# test_appointment.py
from langchain_core.messages import HumanMessage
from agents.appointment_agent import appointment_app # Import the app we just built

print("🧪 STARTING APPOINTMENT AGENT TEST")
print("Type 'quit' to exit. \n")

# Initialize chat history
# In a real app, this persistence is handled by a Checkpointer, 
# but for testing, we just keep passing the updated history manually.
chat_history = []
# Defines a specific conversation thread
config = {"configurable": {"thread_id": "test_user_1"}}

while True:
    user_input = input("User: ")
    if user_input.lower() in ["quit", "exit"]:
        break
    
    # Create the user message
    user_msg = HumanMessage(content=user_input)
    
    # We pass the full history + new message to the graph
    # (Since our state uses 'add_messages', we actually only need to pass the new one 
    # if we were using a checkpointer, but for this simple test, passing the new one works 
    # because the graph output will include the accumulated history)
    
    inputs = {"messages": [user_msg]}
    
    print("--- Graph Running ---")
    
    # stream() allows us to see each step (Agent -> Tool -> Agent)
    for event in appointment_app.stream(inputs, config=config, stream_mode="values"):
        
        # Get the latest message from the current step
        current_messages = event["messages"]
        last_msg = current_messages[-1]
        
        # Print based on who sent the message
        if last_msg.type == "ai":
            # Only print if there is text (sometimes AI just sends tool calls)
            if last_msg.content:
                print(f"🤖 Agent: {last_msg.content}")
            
            # If it has tool calls, indicate that
            if last_msg.tool_calls:
                print(f"   (Agent requesting: {[t['name'] for t in last_msg.tool_calls]})")
                
        elif last_msg.type == "tool":
            print(f"🛠️ Tool Output: {last_msg.content}")
            
    print("---------------------\n")