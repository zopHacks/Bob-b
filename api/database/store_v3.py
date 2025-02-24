from depricated.auth_user_jwt import supabase
from datetime import datetime
from enum import Enum

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

class Day(Enum):
    SUNDAY = "sunday"
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    
# datetime(2030, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
async def create_goal(
    title: str, 
    description: str, 
    due_date: str, 
    user_id: str, 
    unfair_advant: str, 
    difficulties: str, 
    priority: Priority, 
    difficulty: Difficulty, 
    has_done: bool, 
    to_do: str, 
    progress_bar: int
):
    new_goal = {
        "user_id": user_id,
        "title": title,
        "description": description,
        "due_date": due_date,
        "unfair_advant": unfair_advant,
        "difficulties": difficulties,
        "priority": priority,
        "difficulty": difficulty,
        "has_done": has_done,
        "to_do": to_do,
        "progress_bar": progress_bar
    }

    response = await (
        supabase.table("goals_v2")
        .insert(new_goal)
        .execute()
    )
    print(response)

async def create_task(
    title: str, 
    description: str, 
    due_date: str, 
    user_id: str, 
    notes: str = "", 
    difficulty: str = "", 
    has_done: bool = False, 
    goal: str = "", 
    progress_bar: int = 0
):
    new_task = {
        "user_id": user_id,
        "title": title,
        "description": description,
        "due_date": due_date,
        "notes": notes,
        "difficulty": difficulty,
        "has_done": has_done,
        "goal": goal,
        "progress_bar": progress_bar
    }
    response = await (
        supabase.table("tasks_v2")
        .insert(new_task)
        .execute()
    )
    print(response)

async def create_routine(
    title: str, 
    description: str, 
    user_id: str, 
    notes: str = "", 
    difficulty: str = "", 
    goal: str = "", 
    day: str = "", 
    time_in_day: str = ""
):
    new_schedule = {
        "id": "",  # Assuming this is auto-generated
        "user_id": user_id,
        "created_at": "",  # Typically generated automatically by Supabase
        "title": title,
        "description": description,
        "notes": notes,
        "difficulty": difficulty,
        "goal": goal,
        "day": day,
        "time_in_day": time_in_day
    }
    
    response = await (
        supabase.table("tasks_v2")
        .insert(new_schedule)
        .execute()
    )
    print(response)
