"""
VideoAgent (US-2.1): Video assets (RunwayML + fallbacks). Stub returns placeholder path.
"""
from pathlib import Path
from src.agents.base_agent import BaseAgent, ExecutionContext, AgentResult
from src.services.runwayml_service import generate_video

class VideoAgent(BaseAgent):
    name = "video"

    async def execute(self, context: ExecutionContext) -> AgentResult:
        script_data = context.data.get("script", {})
        script = script_data.get("script", "")[:200] if isinstance(script_data, dict) else "scene"
        try:
            path, cost = generate_video(script, duration_sec=10.0)
            self.log_cost(context.execution_id, "video", cost)
            return AgentResult(success=True, data={"video_path": str(path)})
        except Exception as e:
            return AgentResult(success=False, message=str(e))
