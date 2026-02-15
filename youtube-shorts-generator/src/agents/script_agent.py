"""
ScriptAgent (US-1.2): Generate 10-second script from research data. GPT-4.
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
                    {"role": "user", "content": (
                        f"Write a script for a 10-second YouTube Short on: {topic_line}. "
                        "Aim for about 10 seconds of speech when read aloud. Engaging, hook first. "
                        "Output ONLY the spoken lines—nothing else. "
                        "No stage directions, no scene descriptions, and nothing in square brackets "
                        "(e.g. no '[opening shot]', '[cut to]'). Only text that should be read aloud by the voiceover."
                    )}
                ],
            )
            self.log_cost(context.execution_id, "script", cost)
            return AgentResult(success=True, data={"script": content, "topic": topic_line})
        except Exception as e:
            return AgentResult(success=False, message=str(e))
