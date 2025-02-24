from fastapi.responses import StreamingResponse
from io import BytesIO
import aiohttp
from dotenv import load_dotenv
import os

load_dotenv()

async def tts_neets(text: str):
    async with aiohttp.ClientSession() as client:
      response = await client.post(
        url="https://api.neets.ai/v1/tts",

        headers={
          "Content-Type": "application/json",
          "X-API-Key": os.getenv("NEETS_API_KEY")},

        json={"text": text,
              "voice_id": "vits-eng-999",
              "params": {"model": "vits", "format": "opus"}
        })
      audio_data = await response.read()
      return audio_data