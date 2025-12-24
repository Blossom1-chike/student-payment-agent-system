# backend/tools/payment/verify_payment.py
import os
from langchain_core.tools import tool
from datetime import datetime
from utils.supabase_client import supabase

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
            .eq("student_id", student_id) \
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