"""
CompositionAgent (US-2.2): Combine audio + video. FFmpeg/MoviePy stub.
"""
from pathlib import Path
from src.agents.base_agent import BaseAgent, ExecutionContext, AgentResult

class CompositionAgent(BaseAgent):
    name = "composition"

    async def execute(self, context: ExecutionContext) -> AgentResult:
        audio = (context.data.get("tts") or {}).get("audio_path")
        video = (context.data.get("video") or {}).get("video_path")
        out = Path("tmp") / "final.mp4"
        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            if audio and Path(audio).exists():
                # Stub: would use moviepy or ffmpeg to merge
                out.write_bytes(b"")
            return AgentResult(success=True, data={"output_path": str(out)})
        except Exception as e:
            return AgentResult(success=False, message=str(e))
