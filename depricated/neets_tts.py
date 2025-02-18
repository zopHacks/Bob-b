from fastapi import HTTPException, APIRouter, Depends
from utils.auth_user_jwt import verify_jwt
from fastapi.responses import StreamingResponse
from io import BytesIO
import aiohttp
from dotenv import load_dotenv
import os

load_dotenv()
router = APIRouter(prefix='/utils')

@router.get('/stt')
async def tts_neets(text: str, user=Depends(verify_jwt)):
    async with aiohttp.ClientSession() as client:
      response = await client.post(
        url="https://api.neets.ai/v1/tts",

        headers={
          "Content-Type": "application/json",
          "X-API-Key": os.getenv("NEETS_API_KEY")},

        json={"text": text,
              "voice_id": "vits-eng-999",
              "params": {"model": "vits"}
        })
      audio_data = await response.read()  # Read the binary audio data
      return StreamingResponse(BytesIO(audio_data), media_type="audio/mpeg")