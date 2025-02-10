import webrtcvad
from pydub import AudioSegment
import numpy as np
import io
# Initialize VAD


DURATION = 1.2  # Silence duration to detect speech stop (in seconds)
FRAME_DURATION = 30  # Frame duration in ms (WebRTC VAD supports 10, 20, or 30 ms)
VAD_MODE = 3  # 0: Least aggressive, 3: Most aggressive noise filtering
SPEECH_THRESHOLD = 0.75

vad = webrtcvad.Vad()
vad.set_mode(VAD_MODE)  # 0: Least aggressive, 3: Most aggressive noise filtering

def load_audio(filename: str, sample_rate: int=16000):
    """Converts a .mp3 audio file into a 16kHz mono"""
    audio = AudioSegment.from_mp3(filename)
    audio = audio.set_frame_rate(sample_rate).set_channels(1).set_sample_width(2)  # Convert to 16-bit
    return np.array(audio.get_array_of_samples(), dtype=np.int16)

def frame_generator(audio, sample_rate: int, frame_duration: int):
    """Generates audio frames of the given duration."""
    frame_size = int(sample_rate * (frame_duration / 1000))  # Samples per frame
    for i in range(0, len(audio), frame_size):
        yield audio[i:i+frame_size].tobytes()


async def is_speech(file, sample_rate: int = 16000, duration: int = 1.2, frame_duration: int = 30, speech_threshold: float = 0.75):
    audio = await load_audio(file)
    frames = list(frame_generator(audio, sample_rate, frame_duration))

    frames_in_duration = int((duration*1000)/frame_duration)

    if len(frames) < frames_in_duration:
        return True
    
    picked_frames = frames[-(frames_in_duration):]
    detected_speech = 0
    for frame in picked_frames[:-1]:  # Excludes the last frame
        if await vad.is_speech(frame, 16000):
            detected_speech += 1

    
    required_speech_frames = int(len(picked_frames) * speech_threshold)

    return detected_speech >= required_speech_frames