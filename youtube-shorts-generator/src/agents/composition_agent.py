"""
CompositionAgent (US-2.2): Combine audio + video. Uses MoviePy 2.x; audio + static frame when video missing/empty.
"""
from pathlib import Path
from typing import Optional

from moviepy import AudioFileClip, ColorClip, VideoFileClip

from src.agents.base_agent import BaseAgent, ExecutionContext, AgentResult


def _compose_audio_video(audio_path: Path, video_path: Optional[Path], output_path: Path) -> None:
    """Produce final.mp4: real video + audio, or audio + static frame if video missing/empty.
    When both exist, output duration = min(audio.duration, video.duration); both tracks trimmed to that
    so composition never fails on duration mismatch.
    """
    audio = AudioFileClip(str(audio_path))
    # Shorts: vertical 9:16 (1080x1920)
    w, h = 1080, 1920
    use_video = video_path and video_path.exists() and video_path.stat().st_size > 0
    if use_video:
        video = VideoFileClip(str(video_path))
        output_duration = min(audio.duration, video.duration)
        # Trim both to shorter duration so we never subclip past clip length
        audio_trimmed = audio.subclipped(0, output_duration)
        video_trimmed = video.subclipped(0, output_duration)
        video_trimmed = video_trimmed.with_audio(audio_trimmed)
        video_trimmed.write_videofile(str(output_path), fps=24, codec="libx264", audio_codec="aac", logger=None)
        video_trimmed.close()
        video.close()
        audio_trimmed.close()
    else:
        # No video or empty: static color frame + full TTS audio
        duration = audio.duration
        color = ColorClip(size=(w, h), color=(30, 30, 40), duration=duration)
        color = color.with_audio(audio)
        color.write_videofile(str(output_path), fps=24, codec="libx264", audio_codec="aac", logger=None)
        color.close()
    audio.close()


class CompositionAgent(BaseAgent):
    name = "composition"

    async def execute(self, context: ExecutionContext) -> AgentResult:
        audio = (context.data.get("tts") or {}).get("audio_path")
        video = (context.data.get("video") or {}).get("video_path")
        out = Path("tmp") / "final.mp4"
        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            if audio and Path(audio).exists():
                vp = Path(video) if video else None
                _compose_audio_video(Path(audio), vp, out)
            else:
                out.write_bytes(b"")
            return AgentResult(success=True, data={"output_path": str(out)})
        except Exception as e:
            return AgentResult(success=False, message=str(e))
