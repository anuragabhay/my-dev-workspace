"""
ScriptAgent (US-1.2): Generate 15-60 second script from research data. GPT-4.
"""
from src.agents.base_agent import BaseAgent, ExecutionContext, AgentResult
from src.services.openai_service import chat_completion

class ScriptAgent(BaseAgent):
    name = "script"

    async def execute(self, context: ExecutionContext) -> AgentResult:
        research = context.data.get("research", {})
        topics = research.get("topics", [])
        topic_line = topics[0]["title"] if topics else "trending topic"
        try:
            content, cost = chat_completion(
                messages=[
                    {"role": "user", "content": f"Write a 15-60 second YouTube Short script (3-5 sentences) on: {topic_line}. Engaging, hook first."}
                ],
                model="gpt-4",
            )
            self.log_cost(context.execution_id, "script", cost)
            return AgentResult(success=True, data={"script": content, "topic": topic_line})
        except Exception as e:
            return AgentResult(success=False, message=str(e))
