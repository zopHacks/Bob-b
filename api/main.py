from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.lesson_connection import lesson_connection
from api.create_lesson import create_lesson_notes

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
