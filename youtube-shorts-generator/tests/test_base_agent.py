"""
Unit tests for src.agents.base_agent (BaseAgent, ExecutionContext, AgentResult, Message).
Run from repo root: pytest tests/test_base_agent.py -v
"""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import sys
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.agents.base_agent import (
    ExecutionContext,
    AgentResult,
    Message,
    BaseAgent,
)


# --- Dataclass tests ---

def test_execution_context_creation():
    """ExecutionContext stores execution_id, current_stage, and optional data."""
    ctx = ExecutionContext(execution_id=1, current_stage="research", data={"topic": "test"})
    assert ctx.execution_id == 1
    assert ctx.current_stage == "research"
    assert ctx.data == {"topic": "test"}


def test_execution_context_default_data():
    """ExecutionContext data defaults to empty dict."""
    ctx = ExecutionContext(execution_id=2, current_stage="script")
    assert ctx.data == {}


def test_agent_result_creation():
    """AgentResult stores success, optional message and data."""
    r = AgentResult(success=True, message="ok", data={"key": "value"})
    assert r.success is True
    assert r.message == "ok"
    assert r.data == {"key": "value"}


def test_agent_result_defaults():
    """AgentResult message and data default to None."""
    r = AgentResult(success=False)
    assert r.success is False
    assert r.message is None
    assert r.data is None


def test_message_creation():
    """Message stores from_agent, to_agent, message_type, optional payload, status."""
    m = Message(from_agent="research", to_agent="script", message_type="topic", payload="science")
    assert m.from_agent == "research"
    assert m.to_agent == "script"
    assert m.message_type == "topic"
    assert m.payload == "science"
    assert m.status == "pending"


def test_message_status_default():
    """Message status defaults to 'pending'."""
    m = Message(from_agent="a", to_agent="b", message_type="t")
    assert m.status == "pending"


# --- BaseAgent tests (via concrete subclass) ---

class ConcreteAgent(BaseAgent):
    """Minimal concrete agent for testing."""
    name = "concrete"

    async def execute(self, context: ExecutionContext) -> AgentResult:
        return AgentResult(success=True, data={"stage": context.current_stage})


def test_base_agent_subclass_has_name():
    """Concrete subclass has name attribute."""
    assert ConcreteAgent.name == "concrete"


@pytest.mark.asyncio
async def test_concrete_agent_execute_returns_agent_result():
    """execute returns AgentResult with expected shape."""
    agent = ConcreteAgent()
    ctx = ExecutionContext(execution_id=1, current_stage="test_stage")
    result = await agent.execute(ctx)
    assert isinstance(result, AgentResult)
    assert result.success is True
    assert result.data == {"stage": "test_stage"}


@pytest.mark.asyncio
async def test_base_agent_handle_message_no_op():
    """Default handle_message does not raise."""
    agent = ConcreteAgent()
    msg = Message(from_agent="a", to_agent="concrete", message_type="test")
    await agent.handle_message(msg)


def test_save_progress_calls_repository_update_execution():
    """save_progress with context calls repository.update_execution with current_stage."""
    agent = ConcreteAgent()
    ctx = ExecutionContext(execution_id=42, current_stage="research")
    mock_repo = MagicMock()
    with patch("src.agents.base_agent._repository", return_value=mock_repo):
        agent.save_progress("script", {"script": "draft"}, context=ctx)
    mock_repo.update_execution.assert_called_once()
    call_kw = mock_repo.update_execution.call_args[1]
    assert call_kw.get("current_stage") == "script"


def test_save_progress_with_none_context_does_not_call_repo():
    """save_progress with context=None does not call repository."""
    agent = ConcreteAgent()
    mock_repo = MagicMock()
    with patch("src.agents.base_agent._repository", return_value=mock_repo):
        agent.save_progress("script", {}, context=None)
    mock_repo.update_execution.assert_not_called()


def test_log_cost_calls_cost_tracker():
    """log_cost calls cost_tracker.log_cost with execution_id, component, cost."""
    agent = ConcreteAgent()
    mock_tracker = MagicMock()
    with patch("src.agents.base_agent._cost_tracker", return_value=mock_tracker):
        agent.log_cost(execution_id=10, component="openai", cost=0.05)
    mock_tracker.log_cost.assert_called_once_with(execution_id=10, component="openai", cost=0.05)
