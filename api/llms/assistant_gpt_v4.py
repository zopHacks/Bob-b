from dotenv import load_dotenv
import os
from openai import AsyncOpenAI

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
history = []

async def get_thread_id():
    thread = await client.beta.threads.create()
    return thread.id

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

        history.append({"role": "assistant", "content": message})

        return messages.data[0].content[0].text.value
    else:
        print(run.status)

# Example: asyncio.run(send_message("thread_V6FXRG0Ge7HAx2mlwGqKap3o", "thanks, so my functions that I just made in python work! it took me a really long time", "You are a helpful assistant", "help the user (your developer) test your api"))