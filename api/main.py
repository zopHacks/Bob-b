from fastapi import FastAPI
# from utils.tts import neets_tts
# from utils import test1
from fastapi.middleware.cors import CORSMiddleware
from lesson_connection import lesson_connection
from create_lesson import create_lesson_notes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "tauri://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(create_lesson_notes.router)
app.include_router(lesson_connection.router)
