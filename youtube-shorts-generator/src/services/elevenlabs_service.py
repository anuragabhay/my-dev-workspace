"""
ElevenLabs TTS: text to speech, audio file (WAV/MP3). Retry + cost tracking.
"""
import os
from pathlib import Path
from typing import Optional

from src.utils.retry import retry_decorator

def _client():
    from elevenlabs.client import ElevenLabs
    return ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))


@retry_decorator(max_retries=3, base_delay=1.0, max_delay=60.0)
def text_to_speech(
    text: str,
    output_path: Optional[Path] = None,
    voice_id: str = "21m00Tcm4TlvDq8ikWAM",  # Rachel default
) -> tuple[Path, float]:
    """Generate audio from text. Returns (path_to_audio, estimated_cost_usd)."""
    client = _client()
    import tempfile
    path = output_path or Path(tempfile.mkdtemp()) / "tts_output.mp3"
    path.parent.mkdir(parents=True, exist_ok=True)
    audio = client.text_to_speech.convert(voice_id=voice_id, text=text, output_format="mp3_44100_128")
    data = b"".join(audio) if hasattr(audio, "__iter__") else audio
    with open(path, "wb") as f:
        f.write(data)
    # ~$0.18-0.30/min
    chars_per_min = 1500
    minutes = max(0.1, len(text) / chars_per_min)
    cost = minutes * 0.24
    return path, cost
