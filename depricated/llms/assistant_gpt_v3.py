from dotenv import load_dotenv
import os
from openai import AsyncOpenAI
import asyncio

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
history = []

async def get_thread_id():
    thread = await client.beta.threads.create()
    print(thread.id)
    return thread.id

asyncio.run(get_thread_id())

async def send_message(thread_id: str, prompt: str, instructions: str | None, assistant_instructions: str | None): 
    assistant = await client.beta.assistants.create(
        name="Asaf",
        instructions=instructions,
        model="gpt-4o-mini"
    )

    history.append({"role": "user", "content": prompt})

    message = await client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt
    )

    run = await client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant.id,
        instructions=assistant_instructions
    )

    if run.status == 'completed': 
        messages = await client.beta.threads.messages.list(
        thread_id=thread_id
        )
        # message = run['choices'][0]['message']['content']

        history.append({"role": "assistant", "content": message})
        print(messages)

        return messages[0]
    else:
        print(run.status)

asyncio.run(send_message("thread_Cc87v6n6bguVZDaiZ7PhWzTx", "hey, I'm testing my api, so I have to write the same message over and over again, please just say okay, thanks ahead of time   ", "You are a helpful assistant", "help the user (your developer) test your api"))