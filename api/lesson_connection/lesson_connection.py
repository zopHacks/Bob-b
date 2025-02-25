from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from utils.stt.stt_if_speech import is_speech
from utils.tts.neets_tts import tts_neets
from pydub.exceptions import CouldntDecodeError
from llms.azure_gpt import OpenAI_Azure_Chat
from utils.stt.stt_transcribe_groqv2 import transcribe_audio
from utils.tts.neets_tts import tts_neets
import json
from utils.verify_user_jwt import verify_user

router = APIRouter(prefix='/ws')

@router.websocket('/lesson')
async def websocket_endpoint(websocket: WebSocket, token: str):
    try:
        user = await verify_user(token)
        if not user:
            return HTTPException(status_code=401, detail=str(e))

    except Exception as e:
        return HTTPException(status_code=401, detail=str(e))

    await websocket.accept()
    # await websocket.send_text(json.dumps({"type": "restart"}))

    data = bytearray()
    non_speech_streak = 0
    llm = OpenAI_Azure_Chat(history=[{"role": "system", "content": "You are a helpful voice assistant"}])

    while True:
        message = await websocket.receive()
        receiving_audio = True
        try:
            if "bytes" in message and receiving_audio:
                new_data = message["bytes"]
                data.extend(new_data)

                if len(data) > 70000:
                    try:
                        speech_to_check = data[-48000:]
                        speech_detected = await is_speech(speech_to_check, speech_threshold=0.4, duration=1.3)
                        print(speech_detected)
                        if not speech_detected:
                            non_speech_streak += 1
                        else:
                            non_speech_streak = 0
                    except CouldntDecodeError as e:
                        print("Decoding error (likely due to incomplete data):", e, "ee")
                        break
                    
                    except Exception as e:
                        print("Unexpected error in is_speech:", e)

                if non_speech_streak > 4:
                    await websocket.send_text(json.dumps({"type": "stop"}))
                    receiving_audio = False
                    non_speech_streak = 0

                    transcription = await transcribe_audio(data)
                    print(transcription, "user")
                    if transcription:
                        await llm.append_message(transcription, "user")
                        output = await llm.respond()
                        print(output)

                        generated_speech = await tts_neets(output)

                        await websocket.send_text(json.dumps({"type": "assistant_response", "text": output}))
                        await websocket.send_bytes(generated_speech)
                            
                    data.clear()

            elif "text" in message:
                text = message["text"]
                if text == "stopped_playing":
                    data.clear()
                    await websocket.send_text(json.dumps({"type": "restart"}))


        except WebSocketDisconnect as e:
            print("WebSocket disconnected:", e)
            break