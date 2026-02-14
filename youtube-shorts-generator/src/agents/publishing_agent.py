"""
PublishingAgent (US-3.1): YouTube upload with metadata. Stub returns fake ID.
"""
from pathlib import Path
from src.agents.base_agent import BaseAgent, ExecutionContext, AgentResult

class PublishingAgent(BaseAgent):
    name = "publishing"

    async def execute(self, context: ExecutionContext) -> AgentResult:
        comp = context.data.get("composition", {}) or {}
        path = comp.get("output_path")
        script_data = context.data.get("script", {}) or {}
        title = (script_data.get("topic") or "YouTube Short")[:100]
        try:
            if path and Path(path).exists():
                from src.services.youtube_service import upload_video
                vid = upload_video(Path(path), title=title, description="")
                return AgentResult(success=True, data={"youtube_id": vid})
            return AgentResult(success=True, data={"youtube_id": "stub_no_upload"})
        except Exception as e:
            return AgentResult(success=False, message=str(e))
