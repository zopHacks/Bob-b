from fastapi import FastAPI
# from utils.tts import neets_tts
# from utils import test1
from utils.auth_user_jwt import verify_jwt, supabase
from fastapi.middleware.cors import CORSMiddleware
from websocket_connection import connection

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "tauri://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(connection.router)

# app.include_router(neets_tts.router)
# app.include_router(test1.router)
# app.include_router(assistants_chatgpt.router)