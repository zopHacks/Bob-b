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

