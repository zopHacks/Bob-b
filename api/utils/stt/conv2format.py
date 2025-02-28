import io
from pydub import AudioSegment
async def convert_to_16k_mono(raw_data: bytes, input_sample_rate: int = 48000) -> bytes:
    """
    Convert raw 16-bit PCM audio (recorded at input_sample_rate) to a 16kHz, mono WAV.
    This ensures the audio is in the correct format for Whisper.
    """
    # Create an AudioSegment from the raw PCM bytes.
    # Note: We assume the audio is 16-bit (sample_width=2) and mono.
    audio_segment = AudioSegment.from_raw(
        io.BytesIO(raw_data),
        sample_width=2,
        frame_rate=input_sample_rate,
        channels=2
    )
    # Resample to 16kHz and ensure mono.
    audio_segment = audio_segment.set_frame_rate(16000).set_channels(1)
    
    # Export as WAV into a BytesIO buffer.
    out_buffer = io.BytesIO()
    audio_segment.export(out_buffer, format="wav")
    return out_buffer.getvalue()