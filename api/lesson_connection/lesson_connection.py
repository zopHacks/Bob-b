# This script is running on fastapi and websockets in order to connect to the client easily

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from llms.azure_gpt import OpenAI_Azure_Chat_JSON
from utils.stt.stt_if_speech import is_speech
from pydub.exceptions import CouldntDecodeError
from utils.stt.stt_transcribe_groqv2 import transcribe_audio
from api.utils.tts.elevenlabs_tts import tts_elevenlabs
import json
from utils.verify_user_jwt import verify_user, supabase
from create_lesson.create_lesson_notes import info

router = APIRouter(prefix='/ws')

# Code Explanation:
# The api gets a topic, planning notes, and concept explanation which were generated earlier at "create_lesson_notes" and were stored on supabase.
# Then, it convertes the messages into Text To Speech, and streams them to the user.
# Afterwards, the API waits for the user to try out their code.
# After that, the API goes through a phaze of a conversational state, each time, listening and waiting for code, and sending a response.
# Until the LLM decides that the user is ready for the next lesson, and sending a message {"type": "return_button"}, in order for the client to show this.

@router.websocket('/lesson')
async def websocket_endpoint(websocket: WebSocket, token: str, url: str):
    try:
        user = await verify_user(token)
        if not user:
            return HTTPException(status_code=401, detail=str(e))

    except Exception as e:
        return HTTPException(status_code=401, detail=str(e))

    await websocket.accept()    

    response = (
        supabase.table("lessons")
        .select("*")
        .eq("url", url)
        .execute()
    )

    topic = response.data[0]["lesson_topic"]
    planning_notes = response.data[0]["planning_notes"]

    intro = response.data[0]["lesson_intro"]
    init_code = response.data[0]["init_code"]
    concept_explanation = response.data[0]["concept_explanation"]
    concept_explanation_code = response.data[0]["concept_explanation_code"]

    await websocket.send_text(json.dumps({"type": "title", "text": topic}))
    await websocket.send_text(json.dumps({"type": "code", "text": init_code}))

    await websocket.send_text(json.dumps({"type": "assistant_response", "text": intro}))

    generated_speech = await tts_elevenlabs(intro)
    await websocket.send_bytes(generated_speech)

    await wait_for_stop(websocket)

    await websocket.send_text(json.dumps({"type": "assistant_response", "text": concept_explanation}))
    await websocket.send_text(json.dumps({"type": "code", "text": concept_explanation_code}))

    generated_speech = await tts_elevenlabs(concept_explanation)
    await websocket.send_bytes(generated_speech)

    script = await wait_stop_code(websocket)
    code = script["code"]
    output = script["output"]

    await exercise_conversation(websocket=websocket, new_topic=topic, planning_notes=planning_notes, lesson_intro=intro, concept_explanation=concept_explanation, old_code=code, old_output=output)
    await websocket.send_text(json.dumps({"type": "return_button"}))


async def wait_for_stop(websocket: WebSocket): # Waits for receiving a "stopped_playing" message from the client
    while True:
        message = await websocket.receive()
        if "text" in message:
            text = json.loads(message["text"])
            if text["type"] == "stopped_playing":
                break

async def wait_stop_code(websocket: WebSocket): # Waits for both receiving a "stopped_playing", and a "code_response" messages from the client
    is_stopped = False
    got_code = False
    code_response = None
    while True:

        message = await websocket.receive()

        if "text" in message:
            text = json.loads(message["text"])
            if isinstance(text, dict):
                if text["type"] == "stopped_playing":
                    is_stopped = True
                elif text["type"] == "code_response":
                    await websocket.send_text(json.dumps({"type": "processing"}))
                    got_code = True
                    code_response = text

        if is_stopped and got_code:
            return code_response
        
async def get_user_response(websocket: WebSocket):
    data = bytearray()
    non_speech_streak = 0
    spoke = 0

    while True:
        message = await websocket.receive()
        try:
            if "text" in message:
                text = json.loads(message["text"])
                if isinstance(text, dict):
                    if text["type"] == "code_response":
                        await websocket.send_text(json.dumps({"type": "processing"}))
                        return text

            if "bytes" in message:
                new_data = message["bytes"]
                data.extend(new_data)

                if len(data) > 100000:
                    try:
                        speech_to_check = data[-48000:]
                        speech_detected = await is_speech(speech_to_check, speech_threshold=0.7, duration=1.3)
                        if not speech_detected:
                            non_speech_streak += 1
                            if spoke > 0:
                                spoke = spoke-1
                        else:
                            spoke += 1
                            print("speech detected")
                            non_speech_streak = 0
                    except CouldntDecodeError as e:
                        print("Decoding error (likely due to incomplete data):", e)
                        break
                    
                    except Exception as e:
                        print("Unexpected error in is_speech:", e)

                if non_speech_streak > 4 and spoke > 400:
                    print(spoke)
                    non_speech_streak = 0
                    await websocket.send_text(json.dumps({"type": "processing"}))


                    transcription = await transcribe_audio(data)
                    return {"type": "transcription", "transcription": transcription}

        except WebSocketDisconnect as e:
            print("WebSocket disconnected:", e)
            break


async def exercise_conversation(websocket: WebSocket, new_topic: str, planning_notes: str, lesson_intro: str, concept_explanation: str, old_code: str, old_output: str):
    sys_prompt = f"""You are Bob-e, an engaging and efficient voice assistant and coding tutor. {info} You have already delivered today's lesson using your internal planning notes ({planning_notes}), covering the topic ({new_topic}) with a lesson introduction ({lesson_intro}), a detailed concept explanation ({concept_explanation}), and example code with its output ({old_code} and {old_output}). Now, ask the learner a clear and friendly question to check if they understand the material so far and whether they feel comfortable with the lesson. Your question should ask if they are ready to proceed with a practical exercise or if they need further explanation on any part of the lesson. This conversation is ongoing, so do not include any greetings (e.g., "welcome" or "welcome again"), formatting symbols, or meta commentary in your spoken text. Keep your explanation plain, natural, and to the point.

Output your response as JSON with three keys:
- "read": Your spoken question in plain text.
- "display_code": Any on-screen notes in plain text or Python format, if applicable. For any exercises provided, do not include complete solutions; instead, use Python-style comments (starting with '#') to offer instructions and hints, and remind the learner to press the run button in the interpreter to see the output of the code.
- "is_ready_for_next": A boolean value indicating whether you believe the learner is ready to move on to the next topic (typically, after 2–3 exercises for beginner topics). When setting "is_ready_for_next" to True, include a congratulatory message for the learner on achieving the lesson, and note that you will not be able to respond to further input after this decision.

After receiving the learner's response, continue the conversation by deciding whether the learner needs further explanation or is ready for one or more practical exercises. After approximately two exercises, ask if they are ready to move on to the next lesson.

Proceed based on the learner's response."""


    llm = OpenAI_Azure_Chat_JSON(history=[{"role": "system", "content": sys_prompt}])
    response = await llm.respond()

    read = response["read"]
    display_code = response["display_code"]
    await llm.append_message(f"read: {read} \n\n\n display_code: {display_code}", "assistant")

    new_generated_speech = await tts_elevenlabs(response["read"])
    await websocket.send_bytes(new_generated_speech)

    await websocket.send_text(json.dumps({"type": "assistant_response", "text": response["read"]}))
    await websocket.send_text(json.dumps({"type": "code", "text": response["display_code"]}))

    while True:
        answer = await get_user_response(websocket)
        print(answer)
        if answer["type"] == "transcription":
            transcription = answer['transcription']
            await llm.append_message(f"user response: {transcription}", "user")
            print(f"user response: {transcription}", "user")

        elif answer["type"] == "code_response":
            code = answer['code']
            output = answer['output']
            await llm.append_message(f"code response:\ncode:{code}\noutput:{output}", "user")
            print(f"code response:\ncode:{code}\noutput:{output}", "user")

        response = await llm.respond()
        read = response["read"]
        display_code = response["display_code"]

        new_generated_speech = await tts_elevenlabs(response["read"])
        await websocket.send_bytes(new_generated_speech)

        await websocket.send_text(json.dumps({"type": "assistant_response", "text": response["read"]}))
        await websocket.send_text(json.dumps({"type": "code", "text": response["display_code"]}))

        print(response["is_ready_for_next"])
        if response["is_ready_for_next"]:
            break
        
        await llm.append_message(f"read: {read} \n\n\n display_code: {display_code}", "assistant")
        await wait_for_stop(websocket)