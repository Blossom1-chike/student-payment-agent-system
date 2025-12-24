import os
from supabase import create_client
from langchain_core.tools import tool
from utils.supabase_client import supabase

@tool
def lookup_student(email: str):
    """
    Checks if a student email exists in the university registry.
    Returns the student's details if found, or 'NOT_FOUND' if not.
    """
    try:
        # Case-insensitive search
        response = supabase.table("students").select("*").ilike("email", email).execute()
        
        if response.data and len(response.data) > 0:
            student = response.data[0]
            return f"FOUND: Name:  {student['name']}, Course: {student['course']}, Year Admitted: {student['year_admitted']}"
        else:
            return "NOT_FOUND"
            
    except Exception as e:
        return f"Database Error: {e}"