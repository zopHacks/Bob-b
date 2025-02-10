from fastapi import HTTPException, APIRouter, Depends, Header
from utils.auth_user_jwt import verify_jwt, supabase
from dotenv import load_dotenv
import os
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_embedding(text: str):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )

    print(response.data[0].embedding, "\n\n\n")
    print(response)
    return response

create_embedding("hello")

router = APIRouter(prefix='/databases/store')

class Task(BaseModel):
    task_title: str
    task_description: str
    task_progress: str
    task_struggles: str
    task_difficulty: int = Field(le=10)

@router.post('/create-tast')
async def create_task(request: Task, user = Depends(verify_jwt)):
    text_to_embed = f""""task_title": {request.task_title} "task_description": {request.task_description} "task_progress": {request.task_progress} "task_difficulties": {request.task_struggles}"""
    embedding = create_embedding()
    response = (
        supabase.table("tasks")
        .insert({"task_title": request.task_title, "task_description": request.task_description, "task_progress": request.task_progress, "task_difficulties": request.task_struggles})
    )



# @router.get('/achievments')
# def get_achievements(user = Depends(verify_jwt)):
#     response = (
#         supabase.table("userdata")
#         .select("achievements-list")
#         .eq("user_id", user.id)
#         .execute()
#     )
#     print(response)
#     return response

# @router.post('/achievments')
# def add_achievements(achievement: str | None ,user = Depends(verify_jwt)):
#     achievements = get_achievements(user)
#     response = (
#         supabase.table("userdata")
#         .insert({"user_id": user.id, "achievements-list": achievements + '\n' + achievement})
#     )
#     print(response)
#     return response
# @router.get('/achievments')
# def get_achievements(user = Depends(verify_jwt)):
#     pass
    # supabase.rpc

