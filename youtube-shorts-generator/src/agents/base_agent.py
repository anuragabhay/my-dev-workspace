"""
Base agent interface for pipeline agents. All agents inherit from BaseAgent.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

# Lazy imports to avoid circular deps
def _cost_tracker():
    from src.utils import cost_tracker
    return cost_tracker

def _repository():
    from src.database import repository
    return repository


@dataclass
class ExecutionContext:
    """Context passed between agents in the pipeline."""
    execution_id: int
    current_stage: str
    data: dict = field(default_factory=dict)


@dataclass
class AgentResult:
    """Result of an agent execution."""
    success: bool
    message: Optional[str] = None
    data: Optional[dict] = None


@dataclass
class Message:
    """Message queue payload."""
    from_agent: str
    to_agent: str
    message_type: str
    payload: Optional[str] = None
    status: str = "pending"


class BaseAgent(ABC):
    """Base class for all pipeline agents."""

    name: str = "base"

    @abstractmethod
    async def execute(self, context: ExecutionContext) -> AgentResult:
        """Execute agent's primary task."""
        pass

    async def handle_message(self, message: Message) -> None:
        """Process incoming messages. Override in subclass if needed."""
        pass

    def save_progress(self, stage: str, data: dict, context: Optional[ExecutionContext] = None) -> None:
        """Save progress to database (execution state / current_stage)."""
        if context is None:
            return
        repo = _repository()
        repo.update_execution(
            context.execution_id,
            current_stage=stage,
            # Optional: persist data to a state table or leave in context
        )

    def log_cost(self, execution_id: int, component: str, cost: float) -> None:
        """Log API cost to database."""
        _cost_tracker().log_cost(execution_id=execution_id, component=component, cost=cost)
