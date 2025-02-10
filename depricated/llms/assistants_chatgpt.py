from fastapi import HTTPException, APIRouter, Depends, Header
from utils.auth_user_jwt import verify_jwt
from dotenv import load_dotenv
import os
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
router = APIRouter(prefix='/llms')


default_prompt = "You are a personal mentor called Asaf, Help the user achieve their goals and dreams, you are energetic, fun, and empathic"

@router.get('/get-thread-id')
async def get_thread_id(user=Depends(verify_jwt)):
  thread = client.beta.threads.create()
  return thread.id

class Message(BaseModel):
  thread_id: str 
  prompt: str 
  instructions: str | None

@router.post('/send-message')
async def send_message(request: Message, user=Depends(verify_jwt)): 
  print(request)

  assistant = client.beta.assistants.create(
    name="Asaf",
    instructions=request.instructions,
    model="gpt-4o-mini",
  )
  messages = client.beta.threads.messages.list(thread_id=request.thread_id)

  context = "\n".join([f"{msg.role}: {msg.content}" for msg in messages.data])

  full_prompt = f"{context}\nUser: {request.prompt}"

  run = client.beta.threads.runs.create_and_poll(
    thread_id=request.thread_id,
    assistant_id=assistant.id,
    instructions=full_prompt
  )
  if run.status == 'completed': 
    messages = client.beta.threads.messages.list(
      thread_id=request.thread_id
    )
    print(messages)
    return messages
  else:
    print(run.status)