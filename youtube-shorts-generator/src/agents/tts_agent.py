"""
TTSAgent (US-1.3): Convert script to voiceover. ElevenLabs.
Strips bracketed content (e.g. [opening shot]) before TTS so only spoken text is synthesized.
"""
import re
from pathlib import Path

from src.agents.base_agent import BaseAgent, ExecutionContext, AgentResult
from src.services.elevenlabs_service import text_to_speech


def _script_for_tts(raw_script: str) -> str:
    """Remove [...] segments and normalize spaces so TTS never speaks stage directions."""
    cleaned = re.sub(r"\[[^\]]*\]", "", raw_script)
    cleaned = " ".join(cleaned.split())
    return cleaned.strip()


class TTSAgent(BaseAgent):
    name = "tts"

    async def execute(self, context: ExecutionContext) -> AgentResult:
        script_data = context.data.get("script", {})
        script = script_data.get("script", "") if isinstance(script_data, dict) else str(script_data)
        if not script:
            return AgentResult(success=False, message="No script in context")
        script_for_voice = _script_for_tts(script)
        if not script_for_voice:
            return AgentResult(success=False, message="No spoken content after removing directions")
        try:
            out = Path("tmp") / "tts_output.mp3"
            path, cost = text_to_speech(script_for_voice, output_path=out)
            self.log_cost(context.execution_id, "tts", cost)
            return AgentResult(success=True, data={"audio_path": str(path)})
        except Exception as e:
            return AgentResult(success=False, message=str(e))
