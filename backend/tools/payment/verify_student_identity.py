from langchain_core.tools import tool
from utils.supabase_client import supabase

@tool
def verify_student_identity(extracted_id: str):
    """
    Checks Supabase to see if the student exists.
    """
    # Query Supabase
    response = supabase.table("students").select("*").eq("student_id", extracted_id).execute()
    print("response", response)
    if not response.data:
        return "Identity Mismatch: Student ID not found in database."
    
    # Optional: Fuzzy match the name
    db_name = response.data[0]['name']
    return f"Identity Verified: Matches {db_name}."