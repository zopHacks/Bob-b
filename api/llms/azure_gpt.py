import os
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI
import json
from pydantic import BaseModel

load_dotenv()

client = AsyncAzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version="2025-01-01-preview"
)

class OpenAI_Azure_Chat:
  def __init__(self, client: AsyncAzureOpenAI = client, model: str = "gpt-4o-mini", history: list[dict] | None = None, tools:list = None, max_tokens: int = 8096) -> None:
    self.client = client
    self.history = history
    self.model = model
    self.max_tokens = max_tokens
    self.tools = tools

  async def append_message(self, message: str, role: str) -> list[dict]:
    self.history.append({"role": role, "content": message})
    print(self.history)

  async def respond(self) -> str:
    completion = await self.client.chat.completions.create(
      model=self.model,
      messages=self.history,
      max_tokens=self.max_tokens
    )
    return completion.choices[0].message.content
  
  async def full_response(self) -> str:
    completion = await self.client.chat.completions.create(
      model=self.model,
      messages=self.history,
      max_tokens=self.max_tokens,
      tools=self.tools
    )
    return completion
  
async def azure_message(sys_prompt, user_prompt: str, model: str = "gpt-4o-mini"):

  completion = await client.beta.chat.completions.parse(
      model="gpt-4o-mini",
      messages=[
          {"role": "system", "content": sys_prompt},
          {"role": "user", "content": user_prompt}
      ]
  )
  return completion.choices[0].message.content


async def azure_message_tools(sys_prompt, user_prompt: str, tools, model: str = "gpt-4o-mini"):

  completion = await client.chat.completions.create(
      model="gpt-4o-mini",
      tools=tools,
      tool_choice="auto",
      messages=[
          {"role": "system", "content": sys_prompt},
          {"role": "user", "content": user_prompt}
      ]
  )
  return completion.choices[0].message.content

async def azure_message_json(sys_prompt, user_prompt: str, structure, model: str = "gpt-4o-mini"):

  completion = await client.beta.chat.completions.parse(
      model="gpt-4o-mini",
      response_format=structure,
      messages=[
          {"role": "system", "content": sys_prompt},
          {"role": "user", "content": user_prompt}
      ]
  )
  return json.loads(completion.choices[0].message.content)

class Exercise(BaseModel):
  read: str
  display_code: str
  is_ready_for_next: str

class OpenAI_Azure_Chat_JSON:
  def __init__(self, model: str = "gpt-4o-mini", history: list[dict] | None = None, tools:list = None) -> None:
    self.history = history
    self.model = model

  async def append_message(self, message: str, role: str) -> list[dict]:
    self.history.append({"role": role, "content": message})
    print(self.history)

  async def respond(self) -> str:
    completion = await client.beta.chat.completions.parse(
      model=self.model,
      messages=self.history,
      response_format=Exercise
    )
    return json.loads(completion.choices[0].message.content)
  async def get_history(self):
    return self.history