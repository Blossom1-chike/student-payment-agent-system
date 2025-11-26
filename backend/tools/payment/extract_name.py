import easyocr
from langchain.tools import tool
""" 
The payment process involves:
User - wants to pay
Agent - requests for ID card upload
User - uploads card
Agent - extracts name from ID card

this function involves the functionality to extract the card
"""
# Load model once globally for efficiency
reader = easyocr.Reader(['en'])

@tool("extract_name_from_id", return_direct=False, description="Generates student name from id image")
def extract_name_from_id(image_bytes: bytes) -> str:
    """Extract text from image using EasyOCR."""
    img = Image.open(io.BytesIO(image_bytes))
    img = img.convert("RGB")

    img_np = np.array(img)

    results = reader.readtext(img_np, detail=0)  # only text
    return " ".join(results)