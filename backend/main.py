import uuid  # <--- IMPORT THIS
from utils.supabase_client import supabase
from typing import Optional
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage
from utils.upload_to_supabase import upload_file_to_supabase
from chat import chat 
import stripe
from fastapi import Request, HTTPException
import os
from dotenv import load_dotenv

load_dotenv() 

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
    thread_id: Optional[str] = Form(None),
    type: Optional[str] = Form(None)
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
            file_url=file_url,
            type=type
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

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

@app.post("/webhook")
async def stripe_webhook(request: Request):
    """Stripe sends data here automatically when a payment finishes"""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # 3. Handle the 'Success' Event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # 1. EXTRACT INFO
        student_number = session['metadata'].get('student_id')
        amount_paid = float(session['amount_total'] / 100) # Convert pence to pounds
        stripe_id = session['id']

        print(f"💰 Webhook: Received £{amount_paid} from {student_number}")

        # 2. GET TOTAL FEE FROM STUDENTS TABLE
        # We need to know how much they were supposed to pay in total
        student_res = supabase.table("students").select("total_fees").eq("student_id", student_number).execute()
        
        # Default to 16000 if not found in DB
        total_fee = float(student_res.data[0]['total_fees']) if student_res.data else 16000.00

        # 3. CALCULATE TOTAL PREVIOUSLY PAID
        # Sum up all successful payments (excluding the current one we are processing)
        payments_res = supabase.table("payments").select("amount") \
            .eq("student_id", student_number) \
            .eq("status", "paid") \
            .neq("stripe_session_id", stripe_id) \
            .execute()
        
        previous_paid = sum(record['amount'] for record in payments_res.data)
        
        # 4. MATH: CALCULATE NEW BALANCE
        # Balance = Total Fee - (Previously Paid + Currently Paid)
        new_balance = total_fee - (previous_paid + amount_paid)

        # 5. UPDATE DATABASE
        # We mark it as 'paid' AND save the 'balance_after' for record keeping
        supabase.table("payments").update({
            "status": "paid",
            "balance_after": new_balance
        }).eq("stripe_session_id", stripe_id).execute()
        
        print(f"✅ Balance Updated: Student now owes £{new_balance}")

    return {"status": "success"}