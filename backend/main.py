import uuid  # <--- IMPORT THIS
import json
from typing import Optional
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage
from utils.upload_to_supabase import upload_file_to_supabase
from chat import chat 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def serialize_message(msg):
    return {
        "type": type(msg).__name__,
        "content": getattr(msg, "content", None)
    }

@app.post("/chat")
async def chat_endpoint(
    user_input: str = Form(...),
    # We ignore the 'state' from client to avoid round-trip corruption
    state: Optional[str] = Form(None), 
    file: Optional[UploadFile] = File(None),
    # Make thread_id optional so we can generate one if missing
    thread_id: Optional[str] = Form(None) 
):
    """
    Handles student general and payment queries.
    """

    # 1. FORCE FRESH ID (The Fix)
    # If the client sends an empty string or nothing, we generate a new UUID.
    # This ensures we don't load the "Corrupted History".
    if not thread_id:
        thread_id = str(uuid.uuid4())
        print(f"🆔 STARTING NEW SESSION: {thread_id}")
    else:
        print(f"🆔 RESUMING SESSION: {thread_id}")

    # 2. Handle File Upload
    file_url = None
    if file:
        try:
            file_url = await upload_file_to_supabase(file)
            print(f"✅ File uploaded: {file_url}")
        except Exception as e:
            return {"response": f"Error uploading file: {str(e)}", "state": {}}

    # 3. Run Chat
    try:
        response_text, updated_state = await chat(
            user_input=user_input,
            thread_id=thread_id, # We pass the clean/valid ID here
            file_url=file_url
        )
    except Exception as e:
         import traceback
         traceback.print_exc()
         return {"response": f"System Error: {str(e)}", "state": {}}
    
    # 4. Serialize Response
    serialized_messages = [serialize_message(m) for m in updated_state.get("messages", [])]

    return {
        "response": response_text,
        "thread_id": thread_id, # Return the ID so the frontend can reuse it next time
        "state": {**updated_state, "messages": serialized_messages}
    }