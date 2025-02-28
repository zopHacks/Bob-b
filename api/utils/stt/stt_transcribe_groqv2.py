import tempfile
import wave
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
# This script uses Groq with whisper large v3 turbo in order to transcribe audio data
async def transcribe_audio(data: bytes) -> str:
    temp_audio_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            temp_audio_path = temp_audio.name

            with wave.open(temp_audio_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(16000)
                wf.writeframes(data)
            
            # Read the file and send it to the transcription API
            with open(temp_audio_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3-turbo",
                    response_format="json",
                    language="en",
                )
            return transcription.text

    except Exception as e:
        print(f"Transcription Error: {e}")
        raise

    finally:
        # Ensure that the temporary file is removed after processing
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
