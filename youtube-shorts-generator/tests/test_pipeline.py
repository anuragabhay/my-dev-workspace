"""
Unit tests for src.orchestration.pipeline (Pipeline orchestrator).
Run from repo root: pytest tests/test_pipeline.py -v
"""
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

import sys
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.agents.base_agent import BaseAgent, ExecutionContext, AgentResult
from src.orchestration.pipeline import Pipeline
from src.database import models


class StubAgent(BaseAgent):
    name = "stub"

    async def execute(self, context: ExecutionContext) -> AgentResult:
        return AgentResult(success=True, data={"stage": "stub"})


class FailingAgent(BaseAgent):
    name = "failing"

    async def execute(self, context: ExecutionContext) -> AgentResult:
        return AgentResult(success=False, message="fail")


@patch("src.orchestration.pipeline.create_execution")
@patch("src.orchestration.pipeline.load_context")
@patch("src.orchestration.pipeline.save_stage")
@patch("src.orchestration.pipeline.repository")
@pytest.mark.asyncio
async def test_pipeline_run_creates_execution_and_returns_id(mock_repo, mock_save, mock_load, mock_create):
    """run() creates execution, runs agents, returns execution_id."""
    mock_create.return_value = 99
    mock_load.return_value = None  # so pipeline builds default context
    pipeline = Pipeline(agents=[StubAgent], db_path=None)
    eid = await pipeline.run()
    mock_create.assert_called_once_with(db_path=None)
    assert eid == 99


@patch("src.orchestration.pipeline.create_execution")
@patch("src.orchestration.pipeline.load_context")
@patch("src.orchestration.pipeline.save_stage")
@patch("src.orchestration.pipeline.repository")
@pytest.mark.asyncio
async def test_pipeline_run_sets_in_progress_then_completed_on_success(mock_repo, mock_save, mock_load, mock_create):
    """run() sets status in_progress, then completed when all agents succeed."""
    mock_create.return_value = 1
    mock_load.return_value = ExecutionContext(execution_id=1, current_stage="start", data={})
    pipeline = Pipeline(agents=[StubAgent])
    await pipeline.run()
    updates = [c[1] for c in mock_repo.update_execution.call_args_list]
    assert any(u.get("status") == models.STATUS_IN_PROGRESS for u in updates)
    assert any(u.get("status") == models.STATUS_COMPLETED for u in updates)


@patch("src.orchestration.pipeline.create_execution")
@patch("src.orchestration.pipeline.load_context")
@patch("src.orchestration.pipeline.save_stage")
@patch("src.orchestration.pipeline.repository")
@pytest.mark.asyncio
async def test_pipeline_run_saves_stage_per_agent(mock_repo, mock_save, mock_load, mock_create):
    """run() calls save_stage with agent name for each agent."""
    mock_create.return_value = 2
    mock_load.return_value = ExecutionContext(execution_id=2, current_stage="start", data={})
    pipeline = Pipeline(agents=[StubAgent])
    await pipeline.run()
    mock_save.assert_called_with(2, "stub", db_path=None)


@patch("src.orchestration.pipeline.create_execution")
@patch("src.orchestration.pipeline.load_context")
@patch("src.orchestration.pipeline.save_stage")
@patch("src.orchestration.pipeline.repository")
@pytest.mark.asyncio
async def test_pipeline_run_on_agent_failure_sets_failed_and_returns(mock_repo, mock_save, mock_load, mock_create):
    """run() on agent failure sets status failed and returns execution_id."""
    mock_create.return_value = 10
    mock_load.return_value = ExecutionContext(execution_id=10, current_stage="start", data={})
    pipeline = Pipeline(agents=[StubAgent, FailingAgent])
    eid = await pipeline.run()
    assert eid == 10
    failed_calls = [c for c in mock_repo.update_execution.call_args_list if c[1].get("status") == models.STATUS_FAILED]
    assert len(failed_calls) == 1
    assert failed_calls[0][1].get("error_message") == "fail"


@patch("src.orchestration.pipeline.create_execution")
@patch("src.orchestration.pipeline.load_context")
@patch("src.orchestration.pipeline.save_stage")
@patch("src.orchestration.pipeline.repository")
@pytest.mark.asyncio
async def test_pipeline_run_passes_db_path_to_helpers(mock_repo, mock_save, mock_load, mock_create):
    """run() passes db_path to create_execution, load_context, save_stage, update_execution."""
    mock_create.return_value = 5
    mock_load.return_value = ExecutionContext(execution_id=5, current_stage="start", data={})
    db = Path("/tmp/pipeline.db")
    pipeline = Pipeline(agents=[StubAgent], db_path=db)
    await pipeline.run()
    mock_create.assert_called_once_with(db_path=db)
    mock_load.assert_called_with(5, db_path=db)
    assert mock_save.call_args[1].get("db_path") == db
    for call in mock_repo.update_execution.call_args_list:
        assert call[1].get("db_path") == db


def test_pipeline_init_default_agents_and_queue():
    """Pipeline with no agents has empty list and MessageQueue."""
    pipeline = Pipeline()
    assert pipeline.agents == []
    assert pipeline.queue is not None
    assert pipeline.db_path is None


def test_pipeline_init_with_agents_and_db_path():
    """Pipeline stores agents and db_path."""
    pipeline = Pipeline(agents=[StubAgent], db_path=Path("/x.db"))
    assert pipeline.agents == [StubAgent]
    assert pipeline.db_path == Path("/x.db")
