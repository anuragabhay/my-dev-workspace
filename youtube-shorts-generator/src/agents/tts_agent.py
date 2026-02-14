"""
TTSAgent (US-1.3): Convert script to voiceover. ElevenLabs.
"""
from pathlib import Path
from src.agents.base_agent import BaseAgent, ExecutionContext, AgentResult
from src.services.elevenlabs_service import text_to_speech

class TTSAgent(BaseAgent):
    name = "tts"

    async def execute(self, context: ExecutionContext) -> AgentResult:
        script_data = context.data.get("script", {})
        script = script_data.get("script", "") if isinstance(script_data, dict) else str(script_data)
        if not script:
            return AgentResult(success=False, message="No script in context")
        try:
            out = Path("tmp") / "tts_output.mp3"
            path, cost = text_to_speech(script, output_path=out)
            self.log_cost(context.execution_id, "tts", cost)
            return AgentResult(success=True, data={"audio_path": str(path)})
        except Exception as e:
            return AgentResult(success=False, message=str(e))
