import os
import json
import asyncio
import aiohttp
import io
import wave

# Ensure your environment variable is set
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
if not DEEPGRAM_API_KEY:
    print("Warning: DEEPGRAM_API_KEY is not set!")

MODEL_ID = "aura-arcas-en"
SAMPLE_RATE = 32000

def wrap_in_wav(audio_data: bytes, sample_rate: int = SAMPLE_RATE) -> bytes:
    """
    Wrap raw PCM audio data in a WAV header.
    """
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(1)     # Mono audio
        wf.setsampwidth(2)     # 16-bit samples
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data)
    return buffer.getvalue()

async def tts_deepgram(text: str) -> bytes:
    """
    Connects to Deepgram’s TTS websocket API using aiohttp, sends the text,
    and accumulates audio data. Wraps raw PCM data in a WAV header.
    """
    # Note: We removed the container parameter.
    uri = f"wss://api.deepgram.com/v1/speak?model={MODEL_ID}&encoding=linear16&sample_rate={SAMPLE_RATE}"
    headers = {"Authorization": f"Token {DEEPGRAM_API_KEY}"}
    raw_audio = bytearray()

    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(uri, headers=headers) as ws:
            payload = {"type": "Speak", "text": text}
            await ws.send_json(payload)
            await ws.send_json({"type": "Flush"})
            print("Sent Speak and Flush messages to Deepgram.")

            # Adjust the timeout if necessary for your network conditions.
            while True:
                try:
                    msg = await ws.receive(timeout=5)
                    print(f"Received message type: {msg.type}")
                except asyncio.TimeoutError:
                    print("Timeout reached, breaking loop.")
                    break

                if msg.type == aiohttp.WSMsgType.BINARY:
                    raw_audio.extend(msg.data)
                    print(f"Appended {len(msg.data)} bytes of binary data.")
                elif msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        print("Received JSON message:", data)
                        if data.get("type") == "Close":
                            print("Received close message, breaking loop.")
                            break
                    except Exception as e:
                        print("Error decoding JSON message:", e)
                elif msg.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.ERROR):
                    print("Received close or error message, breaking loop.")
                    break

    # If the received data does not start with the WAV header (i.e. 'RIFF'),
    # wrap it in a WAV header.
    if raw_audio[:4] != b"RIFF":
        final_audio = wrap_in_wav(bytes(raw_audio), SAMPLE_RATE)
        print("Wrapped raw audio in WAV header.")
    else:
        final_audio = bytes(raw_audio)
    print("Final audio byte length:", len(final_audio))
    return final_audio