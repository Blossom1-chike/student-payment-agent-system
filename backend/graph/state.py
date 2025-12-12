from typing import TypedDict, Optional, Annotated, Dict, Any, List
from langgraph.graph.message import add_messages

class UniversityState(TypedDict, total=False):
    """Shared state across all agents"""
    messages: Annotated[list, add_messages]

    #uploaded image
    image_bytes: Optional[bytes]
    
    # Payment info
    student_id: Optional[str]
    student_name: Optional[str]
    amount: Optional[float]
    payment_link: Optional[str]
    
    # Reconciliation info
    unmatched_payments: Optional[list]
    payment_matched: Optional[bool]
    
    # Support info
    support_ticket_id: Optional[str]
    issue_resolved: Optional[bool]
    
    # Appointment specific
    preferred_date: Optional[str]
    selected_slot: Optional[Dict[str, Any]]
    available_slots: Optional[List[Dict]]
    appointment_reason: Optional[str]
    meeting_id: Optional[str]
    meeting_confirmed: bool
    
    # Control
    error: Optional[str]
    current_step: Optional[str]

    file_url: Optional[str]
    
    # Routing
    agent: Optional[str]
