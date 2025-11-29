from langchain.tools import tool
import io
from PIL import Image
import numpy as np
import easyocr
import re

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

def parse_student_info(ocr_text):
    # name_match = re.search(r"STUDENT\s+([A-Z\s]+)", ocr_text)
    # reg_match = re.search(r"Registration Number:\s*([\w*]+)", ocr_text)
    # Extract name - your improved regex
    name_match = re.search(
        r"STUDENT\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,2})",
        ocr_text,
        re.IGNORECASE
    )
    
    # Extract registration number - your improved regex
    reg_match = re.search(
        r"Registration\s+Number\s*:?\s*([\d\w*]+)",
        ocr_text,
        re.IGNORECASE
    )
    return {
        "student_name": name_match.group(1).strip() if name_match else None,
        "registration_number": reg_match.group(1).strip() if reg_match else None
    }

@tool("extract_name_from_id", return_direct=False, description="Generates student name from id image")
def extract_name_from_id(image_bytes: bytes) -> str:
    """Extract text from image using EasyOCR."""
    img = Image.open(io.BytesIO(image_bytes))
    img = img.convert("RGB")
    img_np = np.array(img)

    results = reader.readtext(img_np, detail=0)  # only text
    extracted_text = " ".join(results)
    print("OCR results:", results)
    return parse_student_info(extracted_text)

# # -----------------------------
# # Test the function with a local image
# # -----------------------------
# if __name__ == "__main__":
#     # Replace with your local image path
#     img_path = "../../images/student_id.jpeg"

#     # Read image as bytes
#     with open(img_path, "rb") as f:
#         image_bytes = f.read()

#     # Call the OCR function
#     extracted_text = extract_name_from_id(image_bytes)
#     return parse_student_info(extracted_text)
