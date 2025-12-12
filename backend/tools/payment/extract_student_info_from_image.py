import base64
import httpx 
import os
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

api_key = os.getenv("OPENAI_API_KEY")

# Initialize a specific model for Vision tasks
vision_llm = ChatOpenAI(model="gpt-4o", openai_api_key= api_key, temperature=0)

class StudentInfo(BaseModel):
    full_name: str = Field(description="The full name of the student found on the card")
    student_id: str = Field(description="The student registration number")

@tool
def extract_student_info_from_image(image_url: str):
    """
    Analyzes an ID card image URL and extracts the Student Name and Student ID.
    Returns a JSON object with keys: full_name, student_id.
    """

    # 1. Download the image locally using httpx (or requests)
    # We do this to avoid OpenAI 'Timeout' errors on large files
    image_data = None
    media_type = "image/jpeg"
    
    with httpx.Client() as client:
        response = client.get(image_url, timeout=10.0)
        if response.status_code != 200:
            return f"Error: Could not download image. Status: {response.status_code}"
        
        # Get content type (e.g. image/png)
        media_type = response.headers.get("content-type", "image/jpeg")
        image_data = base64.b64encode(response.content).decode("utf-8")

    try:
        # We need to send the image to GPT-4o
        message = {
            "role": "user",
            "content": [
                {"type": "text", "text": "Extract the 'Student Name' and 'Student ID' (or Registration Number) from this ID card. Return ONLY JSON."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{media_type};base64,{image_data}"
                    }
                }
            ]
        }

        # Use structured output to guarantee JSON
        structured_llm = vision_llm.with_structured_output(StudentInfo)
        result = structured_llm.invoke([message])
        
        return {
            "full_name": result.full_name,
            "student_id": result.student_id,
            "success": True
        }

    except Exception as e:
        return {"error": str(e), "success": False}