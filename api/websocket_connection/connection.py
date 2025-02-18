from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from utils.stt.stt_if_speech import is_speech
from utils.tts.neets_tts import tts_neets
from pydub.exceptions import CouldntDecodeError
from llms.assistant_gpt_v4 import get_thread_id, send_message
from time import sleep
import json
router = APIRouter(prefix='/ws')

@router.websocket('/live-chat')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        print("got back")
        data = bytearray()
        non_speech_streak = 0
        thread_id = await get_thread_id()
        
        await websocket.send_text(json.dumps({"type": "restart"}))

        while non_speech_streak <= 3:
            try:
                new_data = await websocket.receive_bytes()
                data.extend(new_data)
                if len(data) > 12000:
                    try:   
                        output = await is_speech(data, speech_threshold=0.55)
                        print(output)
                        if not output:
                            non_speech_streak += 1
                        else:
                            non_speech_streak = 0
                    except CouldntDecodeError as e:
                        print("Decoding error (likely due to incomplete data):", e, "ee")
                        break
                    except Exception as e:
                        print("Unexpected error in is_speech:", e)

                
            except WebSocketDisconnect as e:
                print("WebSocket disconnected:", e)
                break

        await websocket.send_text(json.dumps({"type": "stop"}))
        # output = await send_message(thread_id, 'hey, how are you?', 'you are a helpful assistant', 'you are a helpful assistant')
        print("hey")



        # time += 1
        # print("hey1", time)
        # sleep(3)
        # await websocket.send_text(json.dumps({"type": "restart"}))

        

        # print(data, "hi")
        
        # response = await tts_neets("Hey, how are you today?")

        # async for chunk in response.body_iterator:
        #     await websocket.send_bytes(chunk)