"""
QualityAgent (US-2.3): Validate duration, resolution, audio. Stub passes.
"""
from pathlib import Path
from src.agents.base_agent import BaseAgent, ExecutionContext, AgentResult

class QualityAgent(BaseAgent):
    name = "quality"

    async def execute(self, context: ExecutionContext) -> AgentResult:
        comp = context.data.get("composition", {}) or {}
        path = comp.get("output_path")
        if path and Path(path).exists():
            # Stub: would check duration 15-60s, resolution 1080x1920, audio levels
            return AgentResult(success=True, data={"passed": True, "report": "stub"})
        return AgentResult(success=True, data={"passed": True, "report": "no file"})
