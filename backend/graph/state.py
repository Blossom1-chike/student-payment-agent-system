from typing import TypedDict, Optional, Annotated
import operator

class UniversityState(TypedDict):
    """Shared state across all agents"""
    messages: Annotated[list, operator.add]
    
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
    
    # Appointment info
    appointment_time: Optional[str]
    appointment_confirmed: Optional[bool]
    
    # Routing
    next_agent: Optional[str]
