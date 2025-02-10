from dotenv import load_dotenv
import os
from openai import AsyncOpenAI
import asyncio

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def get_thread_id():
  thread = await client.beta.threads.create()
  print(thread.id)
  return thread.id

asyncio.run(get_thread_id())

async def send_message(thread_id: str, prompt: str, instructions: str | None): 

  assistant = await client.beta.assistants.create(
    name="Asaf",
    instructions=instructions,
    model="gpt-4o-mini",
  )

  messages = client.beta.threads.messages.list(thread_id=thread_id)

  context = "\n".join([f"{msg.role}: {msg.content}" for msg in messages.data])

  full_prompt = f"{context}\nUser: {prompt}"

  run = await client.beta.threads.runs.create_and_poll(
    thread_id=thread_id,
    assistant_id=assistant.id,
    instructions=full_prompt
  )
  if run.status == 'completed': 
    messages = client.beta.threads.messages.list(
      thread_id=thread_id
    )
    print(messages)
    return messages.data
  else:
    print(run.status)

asyncio.run(send_message("thread_9QGxtp6eRlwXHemg9b5DR1Fu", "I'm testing my api, so say hi or something", "You are a helpful assistant"))


# SyncCursorPage[Message](data=[Message(id='msg_fg0LXOYE2yKdttdCMQspH2Ku', assistant_id='asst_qNGs50oy2V7KeLhF0c41Yvzz', attachments=[], completed_at=None, content=[TextContentBlock(text=Text(annotations=[], value='Hi there! How can I assist you today?'), type='text')], created_at=1739049380, incomplete_at=None, incomplete_details=None, metadata={}, object='thread.message', role='assistant', run_id='run_Lxo1vZ8XA2NTt4VhYw3uDJrw', status=None, thread_id='thread_9QGxtp6eRlwXHemg9b5DR1Fu'), Message(id='msg_ntd2TIUiRDp8olOm3Ij2hd5y', assistant_id='asst_TmDX97rLvkrPpNio9Udvfev2', attachments=[], completed_at=None, content=[TextContentBlock(text=Text(annotations=[], value="Hello! I'm here to help. What do you need assistance with today?"), type='text')], created_at=1739049310, incomplete_at=None, incomplete_details=None, metadata={}, object='thread.message', role='assistant', run_id='run_afu8b31B6Jeq7iPeMzckNBDR', status=None, thread_id='thread_9QGxtp6eRlwXHemg9b5DR1Fu'), Message(id='msg_UKVBTxfkmB3TCN3YGu6kjHFe', assistant_id='asst_HiW5rKjxJKrnUuCpxnjyxkvq', attachments=[], completed_at=None, content=[TextContentBlock(text=Text(annotations=[], value="I'm just a program, so I don't have feelings, but I'm here and ready to help you! How can I assist you today?"), type='text')], created_at=1739049253, incomplete_at=None, incomplete_details=None, metadata={}, object='thread.message', role='assistant', run_id='run_SXRE9N1mWhPQTmcR2dCD0A7i', status=None, thread_id='thread_9QGxtp6eRlwXHemg9b5DR1Fu')], object='list', first_id='msg_fg0LXOYE2yKdttdCMQspH2Ku', last_id='msg_UKVBTxfkmB3TCN3YGu6kjHFe', has_more=False)