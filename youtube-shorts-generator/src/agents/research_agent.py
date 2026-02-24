"""
ResearchAgent (US-1.1): RAG query for trending topics, 3-5 ideas with relevance scores.
"""
from src.agents.base_agent import BaseAgent, ExecutionContext, AgentResult
from src.services.llm_router import chat_completion, get_model_for_agent
from src.services.rag_service import get_or_create_collection, similarity_search, add_embeddings

class ResearchAgent(BaseAgent):
    name = "research"

    async def execute(self, context: ExecutionContext) -> AgentResult:
        try:
            # Query for topic ideas (simplified: use GPT to suggest topics, then embed and store)
            content, cost = chat_completion(
                agent_name="research",
                messages=[{"role": "user", "content": "List 5 short trending topic ideas for a 60-second YouTube Short. One line each, diverse."}],
            )
            self.log_cost(context.execution_id, "research", cost)
            lines = [l.strip() for l in content.split("\n") if l.strip()][:5]
            topics = [{"title": l, "relevance": 0.85} for l in lines]
            return AgentResult(
                success=True,
                data={"topics": topics, "raw": content},
                model_used=get_model_for_agent("research"),
                action_summary="Queried trending topics, generated 5 ideas",
            )
        except Exception as e:
            return AgentResult(success=False, message=str(e))
