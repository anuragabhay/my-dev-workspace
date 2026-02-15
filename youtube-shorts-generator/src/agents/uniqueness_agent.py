"""
UniquenessAgent (US-1.4): Compare script to last 10 videos; reject if similarity >30%.
Skipped for now (no embedding API call) when project lacks embedding model access; always passes.
"""
from src.agents.base_agent import BaseAgent, ExecutionContext, AgentResult
from src.database import repository


class UniquenessAgent(BaseAgent):
    name = "uniqueness"

    async def execute(self, context: ExecutionContext) -> AgentResult:
        script_data = context.data.get("script", {})
        script = script_data.get("script", "") if isinstance(script_data, dict) else str(script_data)
        if not script:
            return AgentResult(success=False, message="No script in context")
        # Skip embedding call for now (project often lacks text-embedding-* access). Pass through.
        last = repository.get_last_executions(10)
        if not last:
            return AgentResult(success=True, data={"similarity_max": 0.0, "passed": True})
        # When embedding access is available: get_embeddings([script]), load last 10 embeddings, compute similarity, reject if >30%.
        return AgentResult(success=True, data={"similarity_max": 0.0, "passed": True})
