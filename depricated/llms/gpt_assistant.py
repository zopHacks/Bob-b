from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

assistant = client.beta.assistants.create(
  name="Asaf",
  instructions="You are a personal mentor called Asaf, Help the user achieve their goals and dreams, you are energetic, fun, and empathic",
  model="gpt-4o-mini",
)

thread = client.beta.threads.create()
print(thread.id, assistant.id)

run = client.beta.threads.runs.create_and_poll(
  thread_id="thread_Nt0ZDUgwwRTjDHK0hAkCbdH1",
  assistant_id=assistant.id,
  instructions="okay, what is your goal?"
)

if run.status == 'completed': 
  messages = client.beta.threads.messages.list(
    thread_id="thread_Nt0ZDUgwwRTjDHK0hAkCbdH1"
  )
  print(messages)
else:
  print(run.status)