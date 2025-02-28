import webrtcvad
from pydub import AudioSegment
import numpy as np


VAD_MODE = 2  # 0: Least aggressive, 3: Most aggressive noise filtering

vad = webrtcvad.Vad()
vad.set_mode(VAD_MODE)

def load_pcm(data: bytes):
    """
    Convert raw 16-bit PCM bytes (little endian) into a NumPy array.
    """
    audio_array = np.frombuffer(data, dtype=np.int16)
    return audio_array

def frame_generator(audio, sample_rate: int, frame_duration: int):
    """Generates audio frames of the given duration."""
    frame_size = int(sample_rate * (frame_duration / 1000))  # Samples per frame
    for i in range(0, len(audio), frame_size):
        yield audio[i:i+frame_size].tobytes()


async def is_speech(data: bytes, sample_rate: int = 16000, duration: int = 1.2, frame_duration: int = 30, speech_threshold: float = 0.75):
    audio = load_pcm(data)
    frames = list(frame_generator(audio, sample_rate, frame_duration))

    frames_in_duration = int((duration*1000)/frame_duration)

    if len(frames) < frames_in_duration:
        return False
    
    picked_frames = frames[-(frames_in_duration):]
    detected_speech = 0
    for frame in picked_frames[:-1]:  # Excludes the last frame, because it might not be big enough, this cannot be smaller than the 
        if vad.is_speech(frame, sample_rate):
            detected_speech += 1

    
    required_speech_frames = int(len(picked_frames) * speech_threshold)

    return detected_speech >= required_speech_frames