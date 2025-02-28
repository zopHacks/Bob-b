from fastapi.responses import StreamingResponse
from io import BytesIO
import aiohttp
from dotenv import load_dotenv
import os
import asyncio

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
    

import os
import json
import asyncio
import websockets
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELELVENLABS_API_KEY")


# Set your preferred voice and model IDs
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
        
        # Listen for incoming audio data
        while True:
            try:
                message = await ws.recv()
            except websockets.exceptions.ConnectionClosed:
                break

            if isinstance(message, bytes):
                # Append raw binary audio data
                generated_audio.extend(message)
            else:
                try:
                    data = json.loads(message)
                    # If the message contains an 'audio' field, decode and append it
                    if "audio" in data:
                        audio_chunk = base64.b64decode(data["audio"])
                        generated_audio.extend(audio_chunk)
                    # Optionally, break if the response indicates the stream is finished
                    if data.get("isFinal"):
                        break
                except Exception:
                    # Ignore non-JSON messages
                    pass
    print(bytes(generated_audio))
    return bytes(generated_audio)

# asyncio.run(tts_elevenlabs("hey 231"))



# async def tts_unreal(text: str):
#     url = 'https://api.v8.unrealspeech.com/synthesisTasks'
#     headers = {
#         'Authorization': f'Bearer {os.getenv("UNREAL_SPEECH")}'
#     }
#     payload = {
#         'Text': text,  # Up to 500,000 characters
#         'VoiceId': 'Ethan',     # Scarlett, Dan, Liv, Will, Amy
#         'Bitrate': '128k',           # 320k, 256k, 192k, ...
#         'Speed': '0.1',                # -1.0 to 1.0
#         'Pitch': '1',                # 0.5 to 1.5
#         'TimestampType': 'sentence',  # word or sentence
#         # 'CallbackUrl': '<URL>',    # pinged when ready
#         "OutputFormat": 'opus'
#     }

#     async with aiohttp.ClientSession() as session:
#         async with session.post(url, json=payload, headers=headers) as response:
#             response_json = await response.json()
#             print(response_json)



async def tts_unreal(text: str):
    url = "https://api.v8.unrealspeech.com/speech"
    payload = {
        'Text': text,  # Up to 500,000 characters
        'VoiceId': 'Ethan',     # Options: Scarlett, Dan, Liv, Will, Amy, etc.
        'Bitrate': '128k',      # Options: 320k, 256k, 192k, etc.
        'Speed': '0.1',         # Range: -1.0 to 1.0
        'Pitch': '1',           # Range: 0.5 to 1.5
        'TimestampType': 'sentence',  # 'word' or 'sentence'
        # 'CallbackUrl': '<URL>',  # Optional callback URL when ready
        "OutputFormat": 'opus',
        'sync': False
    }
    headers = {
        "Authorization": f"Bearer {os.getenv('UNREAL_SPEECH')}"
    }
    
    async with aiohttp.ClientSession() as session:
        # Post the TTS request
        async with session.post(url, headers=headers, json=payload) as response:
            # Check if the request was successful
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"HTTP {response.status} error: {error_text}")
            try:
                result = await response.json()
            except Exception as e:
                error_text = await response.text()
                raise Exception(f"Error decoding JSON: {error_text}") from e

            audio_uri = result.get("uri")
            if not audio_uri:
                raise Exception("Audio URI not returned from Unreal Speech API.")
        
        # Fetch the audio bytes from the returned URI
        async with session.get(audio_uri) as audio_response:
            audio_data = await audio_response.read()
    
    return audio_data

