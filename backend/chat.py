# chat.py 

from typing import Optional
from langchain_core.messages import HumanMessage
from graph.state import UniversityState
from graph.workflow import build_graph
from dotenv import load_dotenv

load_dotenv()

# Build the workflow graph once
app = build_graph()

async def chat(user_input: str, thread_id: str = "chat_user_2", file_url: str=""):
    """
    Chat with the multi-agent system.
    We let the Graph handle all orchestration and routing internally.
    """
    
    # 1. Config for Memory
    config = {"configurable": {"thread_id": thread_id}}
    
    # 1. Base Input
    input_payload = {
        "messages": [HumanMessage(content=user_input)]
    }
    
    # 2. Inject File URL if it exists
    # LangGraph will automatically merge this into the 'UniversityState'
    if file_url:
        input_payload["file_url"] = file_url

    try:
        # 3. Run the Graph
        # The Graph will:
        #   a. Load previous state from Memory
        #   b. Run 'Orchestrator' Node
        #   c. Run 'Router' Edge -> Decides to go to Payment or Appointment
        #   d. Run the specific Agent (handling .ainvoke vs function calls automatically)
        #   e. Return the final state
        result = await app.ainvoke(input_payload, config=config)
        
        # 4. Extract Response
        last_message = result["messages"][-1]
        response_text = last_message.content
        
        return response_text, result

    except Exception as e:
        print(f"Graph Error: {e}")
        print(f"I ran into a problem: {str(e)}", {})
        raise e