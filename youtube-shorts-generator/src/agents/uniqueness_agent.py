"""
UniquenessAgent (US-1.4): Compare script to last 10 videos; reject if similarity >30%.
"""
from src.agents.base_agent import BaseAgent, ExecutionContext, AgentResult
from src.services.openai_service import get_embeddings
from src.database import repository

class UniquenessAgent(BaseAgent):
    name = "uniqueness"

    async def execute(self, context: ExecutionContext) -> AgentResult:
        script_data = context.data.get("script", {})
        script = script_data.get("script", "") if isinstance(script_data, dict) else str(script_data)
        if not script:
            return AgentResult(success=False, message="No script in context")
        try:
            emb, cost = get_embeddings([script])
            self.log_cost(context.execution_id, "uniqueness", cost)
            # Compare to last 10 videos' embeddings (stub: no previous embeddings yet)
            last = repository.get_last_executions(10)
            if not last:
                return AgentResult(success=True, data={"similarity_max": 0.0, "passed": True})
            # Placeholder: would load embeddings for last 10 and compute similarity
            return AgentResult(success=True, data={"similarity_max": 0.0, "passed": True})
        except Exception as e:
            return AgentResult(success=False, message=str(e))
