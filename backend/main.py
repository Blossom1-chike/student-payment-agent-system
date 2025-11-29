from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import json
from langchain_core.messages import HumanMessage, AIMessage
from chat import chat 
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper to convert messages to JSON-serializable dicts
def serialize_message(msg):
    return {
        "type": type(msg).__name__,
        "content": getattr(msg, "content", None)
    }

@app.post("/chat")
async def chat_endpoint(
    user_input: str = Form(...),
    state: str = Form('{}'),               # state from client as JSON string
    file: Optional[UploadFile] = File(None)
):
    """
    Handles student general and payment queries with optional uploaded ID file.
    Persists conversation state between requests.
    """

    # --- Parse state ---
    try:
        state_dict = json.loads(state)
    except json.JSONDecodeError:
        state_dict = {}

    # Ensure messages list exists in state
    human_msg = HumanMessage(content=user_input)
    if "messages" not in state_dict:
        state_dict["messages"] = [human_msg]
    else:
        state_dict["messages"].append(human_msg)

    # --- Convert uploaded file to bytes if provided ---
    image_bytes = await file.read() if file else None

    # --- Call your agent/graph ---
    response_text, updated_state = chat(
        user_input=user_input,
        state=state_dict,
        image_bytes=image_bytes
    )

    # Append AI message returned by the agent
    # if "messages" in result and result["messages"]:
    #     state_dict["messages"].append(result["messages"][-1])
    #     response_text = getattr(result["messages"][-1], "content", str(result["messages"][-1]))
    # else:
    #     response_text = ""

    # --- Serialize messages for client ---
    serialized_state = [serialize_message(m) for m in updated_state["messages"]]

    return {
        "response": response_text,
        "state": serialized_state
    }
