from .supabase_client import supabase
from fastapi import UploadFile
import asyncio
import os
from pathlib import Path
import uuid

BUCKET = os.getenv("SUPABASE_BUCKET", "uploads")

async def upload_file_to_supabase(file: UploadFile) -> str:
    """
    Uploads an UploadFile object to Supabase Storage asynchronously
    and returns the public URL of the uploaded file.
    """
    file_bytes = await file.read()
    unique_name = f"{uuid.uuid4()}{file.filename}"

    loop = asyncio.get_event_loop()

    try:
        # Run sync upload in a separate thread to avoid blocking the event loop
        await loop.run_in_executor(
            None,
            lambda: supabase.storage.from_(BUCKET).upload(
                unique_name,
                file_bytes,
                {"content-type": file.content_type}
            )
        )
    except Exception as e:
        print("Supabase upload failed:", e)
        raise e

    return supabase.storage.from_(BUCKET).get_public_url(unique_name)