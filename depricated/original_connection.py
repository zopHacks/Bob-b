from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import time
router = APIRouter(prefix='/ws')

@router.websocket('/live-chat')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    waiting = True
    while True:
        try:
            if waiting:
                data = await websocket.receive_text()
                print(data)
                await websocket.send_text(f"the message was {data}")
                await websocket.send_text(f"you are about to be disconnected :)")
                waiting = False
                time.sleep(3)
                await websocket.close()

        except WebSocketDisconnect as e:
            print("yay",e, "disconnected successfully")
            break


    

