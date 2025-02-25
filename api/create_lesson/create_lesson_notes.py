from fastapi import HTTPException, APIRouter, Depends
from utils.auth_user_jwt import verify_jwt, supabase
from dotenv import load_dotenv
from llms.azure_gpt import azure_message, azure_message_json
from pydantic import BaseModel
import json

load_dotenv()
router = APIRouter(prefix='/lesson')

class Teach(BaseModel):
    read: str
    display_code: str

async def generate_topic(user_message: str):
    sys_prompt = """You are Ezra, an engaging and efficient voice assistant and coding tutor. Your task is to convert a given user topic or message into a concise Python lesson topic. Analyze the user's input, extract the key concept, and generate a short, focused lesson topic that clearly defines what the lesson will cover. Your output should be plain text only, without any JSON formatting or extra keys. a topic example would be 'Python If Statements'"""
    user_prompt = f"""Convert the following user message into a short Python lesson topic: {user_message}."""
    return await azure_message(sys_prompt, user_prompt, model="gpt-4o-mini")

async def generate_planning_notes(new_topic: str):
    sys_prompt = """You are Ezra, an empathetic and efficient coding tutor committed to helping learners master Python. Before engaging with the learner, generate your internal planning notes to structure today's lesson on Python if statements. Your internal notes will not be spoken aloud; they serve solely as your internal guide.

Key Lesson Goal:

Objective: Define the primary concept to teach (e.g., "Teach Python if statements, focusing on syntax, usage, and best practices.").
Desired Outcome: Ensure the learner can confidently write a basic if statement and understand how it controls program flow.
Lesson Outline and Guideline:

Introduction:
Briefly introduce the topic, why it's important, and what the learner should expect.
Concept Explanation:
Break down the structure of if statements, including the 'if', 'elif', and 'else' components.
Explain how conditions are evaluated.
Interactive Example:
Plan to generate and explain a code example using the integrated code editor.
Outline which parts of the code to highlight and how to explain each component.
Engagement and Checkpoints:
Design checkpoints where you ask the learner questions to confirm understanding.
Prepare prompts to clarify any common misunderstandings (e.g., indentation errors, logical conditions).
Practice and Feedback:
Instruct the learner to write their own if statement.
Plan how to review their code, provide constructive feedback, and guide them toward success.
Conclusion:
Summarize the key points of the lesson.
Prepare a congratulatory message to reinforce their progress.
Additional Considerations:

Anticipated Questions:
Identify common pitfalls (e.g., incorrect syntax, misinterpreting conditions) and plan brief clarifications.
Tone and Approach:
Maintain a friendly, supportive, and efficient teaching style throughout.
Adaptive Responses:
Keep in mind potential adjustments if the learner appears confused or needs further explanation.
Now, generate your internal planning notes based on the above guidelines. Focus on creating a coherent, structured roadmap for today's lesson on Python if statements."""
    user_prompt = f"Topic: {new_topic} Begin the lesson with an overview, introduce the key concepts and components, provide an interactive code example, and include practice exercises with feedback. Keep the explanation clear, concise, and engaging."
    
    return await azure_message(sys_prompt, user_prompt, model="gpt-4o")

async def generate_lesson_intro(new_topic: str, planning_notes: str):
        sys_intro_prompt = f"""You are Ezra, an engaging and efficient voice assistant and coding tutor. You have prepared internal planning notes for this lesson: {planning_notes}. Now, begin the lesson by introducing the subject {new_topic}. Your introduction should provide a clear, concise overview of what {new_topic} is and why it is important, highlight key components and terms related to {new_topic}, and set the stage for a deeper dive into the concept by outlining what the learner can expect next. Use engaging language and relevant examples to connect with the learner. When responding, output your answer in JSON format with two keys: "read" for your spoken explanation (without any extra formatting) and "display_code" for any accompanying code, message, or note in Python format."""
        user_intro_prompt = f"Please provide a clear and engaging introduction to {new_topic}. Explain what it is, why it's important, and what I can expect to learn from this lesson."

        return await azure_message_json(sys_intro_prompt, user_intro_prompt, structure=Teach, model="gpt-4o-mini")

@router.post('/create-notes')
async def create_notes(topic: str, user=Depends(verify_jwt)): 
    new_topic = await generate_topic(topic)
    planning_notes = await generate_planning_notes(new_topic)
    lesson_intro = await generate_lesson_intro(new_topic, planning_notes)

    response = (
        supabase.table("lessons")
        .insert({"planning_notes": planning_notes, "lesson_topic": new_topic, "lesson_intro": lesson_intro.get("read", None), "init_code": lesson_intro.get("display_code", None)}, returning="representation")
        .execute()
    )
    return response.data[0]["url"]