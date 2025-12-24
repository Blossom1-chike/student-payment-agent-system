import stripe
import os
from typing_extensions import TypedDict
from langchain.tools import tool
from graph.state import UniversityState
from utils.supabase_client import supabase

class PaymentDTO(TypedDict):
    student_name: str | None
    email:  str | None
    amount:  float | None
    currency:  str | None = "gbp"
    card_name:  str | None

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")  # set your secret key

@tool("create_payment_link", return_direct=False, description="Generates a stripe payment link for student to make payment with")
def create_payment_link(amount: float, student_id: str):
    """
    Generates a Stripe Payment Link and logs the pending transaction to Supabase.
    Amount should be in GBP (e.g., 50.00).
    """
    print(f"💳 Stripe: Creating link for £{amount} for {student_id}...")
    
    try:
        # 1. Convert to cents/pence (Stripe requires integers)
        amount_cents = int(amount * 100)
        
        # 2. Create Stripe Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'gbp',
                    'product_data': {
                        'name': 'Tuition Fee Payment',
                        'description': f'Payment for Student ID: {student_id}',
                    },
                    'unit_amount': amount_cents,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://your-university.edu/success', # Replace with your frontend URL
            cancel_url='https://your-university.edu/cancel',
            metadata={'student_id': student_id} # Helps tracking on Stripe Dashboard
        )
        
        # 3. Log 'Pending' Record in Supabase
        supabase.table("payments").insert({
            "student_id": student_id,
            "amount": amount,
            "stripe_session_id": session.id,
            "status": "pending"
        }).execute()
        
        return f"Payment Link Created: {session.url}"
        
    except Exception as e:
        return f"Stripe Error: {str(e)}"

@tool
def verify_payment_status(student_id: str):
    """
    Checks if the recent payment was successful and retrieves the remaining balance and due date.
    Use this when the user says "I have paid".
    """
    print(f"🔎 Verifying payment for {student_id}...")
    
    try:
        # 1. Look for the most recent SUCCESSFUL payment
        payment_res = supabase.table("payments") \
            .select("*") \
            .eq("student_number", student_id) \
            .eq("status", "paid") \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()

        if not payment_res.data:
             return "❌ I cannot see the payment yet. Please wait a moment and try again."

        payment = payment_res.data[0]
        amount_paid = payment['amount']
        current_balance = payment['balance_after'] # The webhook calculated this!
        
        # 2. Get the Due Date from Students Table
        student_res = supabase.table("students") \
            .select("next_payment_due") \
            .eq("student_id", student_id) \
            .execute()
            
        due_date = "2025-09-01" # Default fallback
        if student_res.data and student_res.data[0]['next_payment_due']:
            due_date = student_res.data[0]['next_payment_due']

        # 3. Construct the Notification Message
        return (
            f"✅ **Payment Successful!**\n\n"
            f"We have received your payment of **£{amount_paid:,.2f}**.\n"
            f"-----------------------------------\n"
            f"💰 **New Balance:** £{current_balance:,.2f}\n"
            f"📅 **Next Payment Due:** {due_date}\n"
            f"-----------------------------------\n"
            f"A receipt has been emailed to you."
        )

    except Exception as e:
        return f"System Error: {str(e)}"