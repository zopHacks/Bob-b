from utils.auth_user_jwt import supabase, verify_jwt, verify_jwt2
from fastapi import Depends
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional
import asyncio
import os
print(os.getcwd())


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium",
    HIGH = "high",
    EXTREMELY_HIGH = "extremly_high"

class Difficulty(Enum):
    EXTREMELY_EASY = "extremely_easy"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    SUPER_HARD = "super_hard"

class Goal(BaseModel):
    is_done: bool
    title: str
    description: str
    current_status: str
    next_steps: str
    struggles: str
    due_date: int
    # priority: Priority
    # difficulty: Difficulty

async def create_goal(goal: Goal, user_token):
    user = await asyncio.create_task(verify_jwt2(user_token))
    new_goal = {
    "is_done": False,
    "title": "super title",
    "description": "lorem ipsum",
    "current_status": "decent",
    "next_steps": "go to the cinema",
    "struggles": "it's really hard to go to the movies",
    "user_id": user.user.id
    # "due_date": 123,
    #     "priority": Priority.HIGH,
    #     "difficulty": Difficulty.SUPER_HARD,
    }
    response = (
        supabase.table("goals")
        .insert(new_goal)
        .execute()
    )
    print(goal)


new_goal: Goal = {
    "is_done": False,
    "title": "super title",
    "description": "lorem ipsum",
    "current_status": "decent",
    "next_steps": "go to the cinema",
    "struggles": "it's really hard to go to the movies",
    "due_date": 123,
#     "priority": Priority.HIGH,
#     "difficulty": Difficulty.SUPER_HARD,
}

asyncio.run(create_goal(new_goal, "eyJhbGciOiJIUzI1NiIsImtpZCI6ImhuTk95NnNMZVRFSUY1Y1ciLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2ZqcHV1cm92Ym5oeXlrZGJia3BqLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiJlY2M2NTc1OC0xYzExLTRlMDQtOGEwNy1hNmVhMzVhZDViMTQiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzM5MTc3NjE2LCJpYXQiOjE3MzkxNzQwMTYsImVtYWlsIjoiYWxpYW5jZS5yb2JvdGljc0BnbWFpbC5jb20iLCJwaG9uZSI6IiIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6ImVtYWlsIiwicHJvdmlkZXJzIjpbImVtYWlsIl19LCJ1c2VyX21ldGFkYXRhIjp7ImVtYWlsIjoiYWxpYW5jZS5yb2JvdGljc0BnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwicGhvbmVfdmVyaWZpZWQiOmZhbHNlLCJzdWIiOiJlY2M2NTc1OC0xYzExLTRlMDQtOGEwNy1hNmVhMzVhZDViMTQifSwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJhYWwiOiJhYWwxIiwiYW1yIjpbeyJtZXRob2QiOiJwYXNzd29yZCIsInRpbWVzdGFtcCI6MTczODg2MzM4NX1dLCJzZXNzaW9uX2lkIjoiZjRjMmFlOGYtZGNkYS00ZTY0LTgyMjQtNmJiMGMxODQ0ZDBlIiwiaXNfYW5vbnltb3VzIjpmYWxzZX0.RU6YYTG9rCgp-t5mGefoZePaNR32iZXqE3zgbAQ1cxM"))

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

