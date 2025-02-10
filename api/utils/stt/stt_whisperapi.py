from utils.stt.stt_if_speech import is_speech

from fastapi import HTTPException, APIRouter, Depends, WebSocket
from utils.auth_user_jwt import verify_jwt
from dotenv import load_dotenv
import os
from pydantic import BaseModel
import tempfile
import wave
from groq import Groq
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
router = APIRouter(prefix='/stt')

@router.websocket('/whisper-ws')
async def get_thread_id(websocket: WebSocket, user=Depends(verify_jwt), speech_detected = Depends(is_speech)):
    await websocket.accept()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio_path = temp_audio.name
        try:
            wf = wave.open(temp_audio_path, "wb")
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(2)  # 16-bit PCM
            wf.setframerate(16000)  # 16kHz
            while True:
                data = await websocket.receive_bytes()
                wf.writeframes(data)  # Write PCM directly to WAV



        except Exception as e:
            print(f"WebSocket error: {e}")

        finally:
            wf.close()
            os.remove(temp_audio_path)  # Cleanup file


"""                with open(temp_audio_path, "rb") as audio_file:
                    transcription = client.audio.transcriptions.create(
                        file=(audio_file.read()),
                        model="whisper-large-v3-turbo",
                        response_format="json",
                        language="en",
                        )
                

                await websocket.send_text(transcription.text)
"""