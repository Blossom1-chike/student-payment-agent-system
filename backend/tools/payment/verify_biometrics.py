import face_recognition
import requests
import numpy as np
from io import BytesIO
from langchain_core.tools import tool

@tool
def verify_biometric_match(live_image_url: str, id_card_url: str):
    """
    Compares a Live Webcam Photo (holding ID) against the previously uploaded ID Card Scan.
    Returns: Verification Success or Failure.
    """
    try:
        print(f"📸 BIOMETRIC CHECK:")
        print(f"   1. ID Card Source: {id_card_url}")
        print(f"   2. Live Cam Source: {live_image_url}")

        def load_image(url):
            res = requests.get(url, timeout=10)
            if res.status_code != 200: raise Exception(f"Failed to download {url}")
            return face_recognition.load_image_file(BytesIO(res.content))

        # 1. Load Images
        img_id_source = load_image(id_card_url)
        img_live = load_image(live_image_url)

        # 2. Get Encodings (Faceprints)
        # We assume the ID source has 1 face (the student)
        id_encodings = face_recognition.face_encodings(img_id_source)
        if not id_encodings:
            return "Error: Could not detect a clear face in the original ID card upload."
        
        # The live image might have 2 faces (Real Person + Face on the ID they are holding)
        # We grab ALL faces in the live image
        live_encodings = face_recognition.face_encodings(img_live)
        if not live_encodings:
            return "Error: Could not detect any face in the webcam photo. Ensure good lighting."

        # 3. Compare
        # We check if the ID Face matches ANY face found in the webcam shot
        known_face = id_encodings[0]
        
        # Compare known face against all live faces
        results = face_recognition.compare_faces(live_encodings, known_face, tolerance=0.5)

        if True in results:
            return "✅ BIOMETRIC VERIFIED: The person in the camera matches the ID card."
        else:
            return "❌ VERIFICATION FAILED: The face in the camera does not match the ID card."

    except Exception as e:
        return f"System Error during processing: {e}"