from tools.appointment.book_meeting import book_meeting
from utils.supabase_client import supabase
from langchain_core.tools import tool

@tool
def book_appointment_ticket(student_email: str, start_iso: str, end_iso: str):
    """
    Books a meeting on Google Calendar AND generates a support ticket in Supabase.
    
    Args:
        student_email: The email of the student.
        start_iso: Start time in ISO 8601 format (e.g. 2023-10-27T14:00:00).
        end_iso: End time in ISO 8601 format.
        
    Returns:
        A string containing the Ticket Number to show the student.
    """
    # --- STEP 1: The Google Calendar Booking (CRITICAL) ---
    # We call the existing logic you already verified works
    try:
        # (Ensure you are using the correct keys as discussed previously)
        calendar_result = book_meeting.invoke({
            "student_email": student_email, 
            "start_time_iso": start_iso,  # <--- MUST MATCH book_meeting definition
            "end_time_iso": end_iso       # <--- MUST MATCH book_meeting definition
        })
        
    except Exception as e:
        # ADD THIS PRINT
        print(f"❌ CRITICAL TOOL ERROR: {e}") 
        return f"Booking Failed (Tool Error): {e}"
    
    # calendar_result = book_meeting.invoke({
    #     "student_email": student_email, 
    #     "start_time_iso": start_iso, 
    #     "end_time_iso": end_iso
    # })
    
    # Safety Check: If Google fails, we STOP here. No ticket is created.
    if "Failed" in str(calendar_result) or "Error" in str(calendar_result):
        return f"Booking Failed: {calendar_result}"

    # --- STEP 2: The Ticket Generation (Supabase) ---
    # We only reach here if Step 1 was successful
    data = supabase.table("appointments").insert({
        "student_email": student_email,
        "appointment_time": start_iso,
        "status": "confirmed"
    }).execute()
    
    ticket_id = data.data[0]['ticket_id']
    
    # --- STEP 3: Return Both ---
    return f"SUCCESS. Calendar Invite sent. Your Ticket Number is #{ticket_id}."