import os
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI

load_dotenv()

client = AsyncAzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version="2024-02-01"
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
  
# chatclient = OpenAI_Azure_Chat(history=[{"role": "system", "content": "You are a helpful assistant."}])
# chatclient.append_message("can you please remember the word apple", "user")
# print(chatclient.respond())

# chatclient.append_message("what was the word I told you to remember?", "user")
# print(chatclient.respond())
  


# print(response.choices[0].message.content)


# response = client.chat.completions.create(
#     model="gpt-4o-mini",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": "Does Azure OpenAI support customer managed keys?"},
#         {"role": "assistant", "content": "Yes, customer managed keys are supported by Azure OpenAI."},
#         {"role": "user", "content": "Do other Azure AI services support this too?"}
#     ]
# )
