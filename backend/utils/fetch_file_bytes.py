import httpx  # async HTTP client

async def fetch_file_bytes(url: str) -> bytes:
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()  # raises if not 200
        return resp.content
