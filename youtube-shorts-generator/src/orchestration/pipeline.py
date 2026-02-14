"""
Pipeline orchestrator: sequential agent execution (MVP).
"""
from pathlib import Path
from typing import Optional, List, Type

from src.agents.base_agent import BaseAgent, ExecutionContext, AgentResult
from src.orchestration.state_manager import create_execution, load_context, save_stage
from src.orchestration.message_queue import MessageQueue
from src.database import repository
from src.database import models


class Pipeline:
    """Runs agents in sequence for one execution."""

    def __init__(self, agents: Optional[List[Type[BaseAgent]]] = None, db_path: Optional[Path] = None):
        self.agents = agents or []
        self.db_path = db_path
        self.queue = MessageQueue(db_path=db_path)

    async def run(self) -> int:
        """Create execution, run agents in order; return execution_id."""
        execution_id = create_execution(db_path=self.db_path)
        repository.update_execution(execution_id, status=models.STATUS_IN_PROGRESS, db_path=self.db_path)
        context = load_context(execution_id, db_path=self.db_path) or ExecutionContext(
            execution_id=execution_id, current_stage="start", data={}
        )
        for agent_cls in self.agents:
            agent = agent_cls()
            save_stage(execution_id, agent.name, db_path=self.db_path)
            result = await agent.execute(context)
            context.data[agent.name] = (result.data or {})
            if not result.success:
                repository.update_execution(
                    execution_id,
                    status=models.STATUS_FAILED,
                    error_message=result.message,
                    db_path=self.db_path,
                )
                return execution_id
        repository.update_execution(execution_id, status=models.STATUS_COMPLETED, db_path=self.db_path)
        return execution_id
