from dotenv import load_dotenv
import os
import json
import websockets
import base64
from dotenv import load_dotenv

load_dotenv()

# This code is for Text To Speech with elevenlabs
# Load environment variables from .env file
load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELELVENLABS_API_KEY")


VOICE_ID = 'UgBBYS2sOqTuMpoF3BR0'
MODEL_ID = 'eleven_flash_v2_5'

async def tts_elevenlabs(text: str) -> bytes:
    """
    Connects to the ElevenLabs TTS streaming API via websocket,
    sends the text to be converted to speech, and accumulates the
    incoming audio chunks into a bytes object.
    """
    uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream-input?model_id={MODEL_ID}"
    generated_audio = bytearray()
    
    async with websockets.connect(uri) as ws:
        # Initialize the connection with voice settings and your API key
        init_payload = {
            "text": " ",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8,
                "use_speaker_boost": False
            },
            "generation_config": {
                "chunk_length_schedule": [120, 160, 250, 290]
            },
            "xi_api_key": ELEVENLABS_API_KEY,
        }
        await ws.send(json.dumps(init_payload))
        
        # Send the actual text message
        await ws.send(json.dumps({"text": text}))
        # Send an empty text message to indicate the end of the text sequence
        await ws.send(json.dumps({"text": ""}))
        
        while True:
            try:
                message = await ws.recv()
            except websockets.exceptions.ConnectionClosed:
                break

            if isinstance(message, bytes):
                generated_audio.extend(message)
            else:
                try:
                    data = json.loads(message)
                    if "audio" in data:
                        audio_chunk = base64.b64decode(data["audio"])
                        generated_audio.extend(audio_chunk)
                    if data.get("isFinal"):
                        break
                except Exception:
                    # Ignore non JSON messages
                    pass
    return bytes(generated_audio)