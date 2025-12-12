from services.appointment.google_service import get_google_service
from langchain_core.tools import tool

@tool
def book_meeting(student_email: str, start_time_iso: str, end_time_iso: str):
    """
    Books a meeting between the Finance Team and a Student.
    start_time_iso/end_time_iso must be ISO format (e.g. 2023-10-27T14:00:00).
    """
    service = get_google_service()
    
    # Google requires explicit timezone or 'Z' for UTC. 
    # For simplicity, we assume the input is local or append 'Z' if missing.
    if not start_time_iso.endswith('Z'): start_time_iso += 'Z'
    if not end_time_iso.endswith('Z'): end_time_iso += 'Z'

    event = {
        'summary': 'Finance Consultation',
        'location': 'Finance Office / Online',
        'description': 'Meeting with Student regarding tuition/fees.',
        'start': {
            'dateTime': start_time_iso,
            'timeZone': 'UTC', # Adjust if you want specific timezone like 'America/New_York'
        },
        'end': {
            'dateTime': end_time_iso,
            'timeZone': 'UTC',
        },
        'attendees': [
            {'email': student_email},
        ],
    }

    try:
        event = service.events().insert(calendarId='primary', body=event, sendUpdates='all').execute()
        return f"Meeting created! Link: {event.get('htmlLink')}"
    except Exception as e:
        return f"Failed to book meeting: {str(e)}"

