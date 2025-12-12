from services.appointment.google_service import get_google_service
from langchain_core.tools import tool

@tool
def check_finance_availability(date_str: str):
    """
    Checks the Finance Team's availability for a specific date (YYYY-MM-DD).
    Strictly checks the window 13:00 to 16:00 (1 PM to 4 PM).
    """
    print(date_str, "this is the date")
    service = get_google_service()
    
    # 1. Define the 1-4 PM window (RFC3339 format required by Google)
    # e.g., '2023-10-27T13:00:00Z'
    time_min = f"{date_str}T13:00:00Z"
    time_max = f"{date_str}T16:00:00Z"
    
    # 2. Query the 'primary' calendar (The Finance Team's calendar)
    events_result = service.events().list(
        calendarId='primary', 
        timeMin=time_min, 
        timeMax=time_max, 
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])

    if not events:
        return f"The Finance Team is fully open between 1 PM and 4 PM on {date_str}."
    
    # Format busy slots nicely for the LLM
    busy_slots = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        busy_slots.append(f"Busy from {start}")
        
    return f"The Finance Team has bookings: {', '.join(busy_slots)}. Please pick a different time in the 1-4 PM window."