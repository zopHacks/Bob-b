# This script is for using prompt, and saving their messages on supabase, for the LLM to be able to acess it easily later.
from fastapi import APIRouter, Depends
from api.utils.auth_user_jwt import verify_jwt, supabase
from dotenv import load_dotenv
from api.llms.azure_gpt import azure_message, azure_message_json
from pydantic import BaseModel

load_dotenv()
router = APIRouter(prefix='/lesson')

class Teach(BaseModel):
    read: str
    display_code: str

class TeachContinueExe(BaseModel):
    read: str
    display_code: str
    continue_with_exercise: bool

info = """You are running on a NextJS website with a built-in Python compiler. There is no need to explain how to install Python. When generating your spoken text, do not include any formatting symbols such as asterisks or code block markers. Make the lesson fun and engaging—teach with enthusiasm and a lighthearted tone. Additionally, ensure your instructions are clear and concise."""
async def generate_topic(user_message: str):
    sys_prompt = """You are Bob-e, an engaging and efficient voice assistant and coding tutor. Your task is to convert a given user topic or message into a concise Python lesson topic. Analyze the user's input, extract the key concept, and generate a short, focused lesson topic that clearly defines what the lesson will cover. Your output should be plain text only, without any JSON formatting or extra keys. A topic example would be 'Python If Statements for beginners', or 'Testing and logging code for proffesional workflows'."""

    user_prompt = f"""Convert the following user message into a short Python lesson topic: {user_message}."""
    return await azure_message(sys_prompt, user_prompt, model="gpt-4o-mini")

async def generate_planning_notes(new_topic: str):
    sys_prompt = f"""You are Bob-e, an empathetic and efficient coding tutor. {info} Before engaging with the learner, generate your internal planning notes to structure today's lesson on Python {new_topic}. Your internal notes will not be spoken aloud; they serve solely as your internal guide.
Key Lesson Goal:

Objective: Define the primary concept to teach (e.g., "Teach Python {new_topic}, focusing on syntax, usage, and best practices.").
Desired Outcome: Ensure the learner can confidently understand and apply the core concept related to {new_topic}.

Lesson Outline and Guideline:

Introduction:
- Briefly introduce the topic, explain its importance, and outline what the learner should expect.
Concept Explanation:
- Break down the concept’s structure and details.
- Explain its key components and functionality.
Interactive Example:
- Plan and explain a code example using the integrated code editor.
- Highlight and clarify relevant parts of the code.
Engagement and Checkpoints:
- Design checkpoints to ask questions and confirm understanding.
- Prepare prompts to address common misunderstandings.
Practice and Feedback:
- Instruct the learner to write their own code related to {new_topic}.
- Plan to review the code, provide constructive feedback, and guide improvement.
Conclusion:
- Summarize the key points of the lesson.
- Prepare a congratulatory message to reinforce the learner's progress.
Additional Considerations:

Anticipated Questions:
- Identify common pitfalls and plan brief clarifications.
Tone and Approach:
- Maintain a friendly, supportive, and efficient teaching style.
- Ensure the lesson is fun and engaging.
Adaptive Responses:
- Be ready to adjust your approach if the learner appears confused or needs further explanation."""
    user_prompt = f"""Topic: {new_topic}. Begin the lesson with an overview, introduce the key concepts and components, provide an interactive code example, and include practice exercises with feedback. Keep the explanation clear, concise, engaging, and fun to learn. Now, generate your internal planning notes based on the above guidelines. Focus on creating a coherent, structured roadmap for today's lesson on Python {new_topic}."""
    return await azure_message(sys_prompt, user_prompt, model="gpt-4o")

async def generate_lesson_intro(new_topic: str, planning_notes: str):
    sys_intro_prompt = f"""You are Bob-e, an efficient voice assistant and coding tutor. {info} You have internal planning notes for this lesson: {planning_notes}. Now, introduce the subject {new_topic}. Your introduction should be concise and engaging: explain what {new_topic} is, why it matters, and outline what the learner can expect next. Use clear language and relevant examples. Output your response in JSON with two keys: "read" for your spoken explanation (without extra formatting) and "display_code" for any accompanying code or notes in Python format."""
    user_intro_prompt = f"Introduce {new_topic}. Explain briefly what it is, why it's important, and what I can expect to learn."


    return await azure_message_json(sys_intro_prompt, user_intro_prompt, structure=Teach, model="gpt-4o-mini")

async def generate_concept_explanation(new_topic: str, planning_notes: str, lesson_intro: str):
    sys_prompt = f"""You are Bob-e, an engaging and efficient voice assistant and coding tutor. {info} You have prepared internal planning notes for this lesson: {planning_notes} and a lesson introduction: {lesson_intro}. Today's lesson topic is {new_topic}. Now, provide a clear and detailed explanation of the core concept behind {new_topic}. In your explanation:
- Define the key concept in straightforward terms.
- Explain its main components and how it functions.
- Provide any relevant examples or code to illustrate the concept.
- Instruct the learner to run the provided code to continue.
- Use engaging, clear language suitable for a voice assistant.
- IMPORTANT: In the "read" output, do not include any formatting symbols (such as asterisks, underscores, or markdown code blocks), greetings, or any meta commentary. This message is part of an ongoing conversation, so avoid greetings like 'welcome' or 'welcome again'. Keep the explanation plain, natural, and to the point.

Output your response as JSON with two keys:
"read": Your spoken explanation in plain text.
"display_code": Any accompanying example code or on-screen notes in Python format (or plain text if code is not applicable)."""

    user_prompt = f"""Explain the concept behind {new_topic}, detailing its definition, components, and functionality with any relevant examples or code. Also, instruct me to run the code to continue."""

    return await azure_message_json(sys_prompt, user_prompt, structure=Teach, model="gpt-4o-mini")

# Verifing jwt token, and saving the responses on Supabase.
@router.post('/create-notes')
async def create_notes(topic: str, user=Depends(verify_jwt)): 
    new_topic = await generate_topic(topic)
    planning_notes = await generate_planning_notes(new_topic)
    lesson_intro = await generate_lesson_intro(new_topic, planning_notes)
    concept_explanation = await generate_concept_explanation(new_topic, planning_notes, lesson_intro)

    response = (
        supabase.table("lessons")
        .insert({"planning_notes": planning_notes,
                  "lesson_topic": new_topic,
                    "lesson_intro": lesson_intro.get("read", None),
                    "init_code": lesson_intro.get("display_code", None),
                    "concept_explanation": concept_explanation.get("read", None),
                    "concept_explanation_code": concept_explanation.get("display_code", None)},
                    returning="representation")
        .execute()
    )
    return response.data[0]["url"]