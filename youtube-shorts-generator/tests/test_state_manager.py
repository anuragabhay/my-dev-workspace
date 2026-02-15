"""
Unit tests for src.orchestration.state_manager (create_execution, load_context, save_stage).
Run from repo root: pytest tests/test_state_manager.py -v
"""
from pathlib import Path
from unittest.mock import MagicMock, patch

import sys
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.agents.base_agent import ExecutionContext
from src.orchestration import state_manager
from src.database import models


@patch("src.orchestration.state_manager.repository")
def test_create_execution_calls_repository_returns_id(mock_repo):
    """create_execution calls repository.create_execution with STATUS_PENDING and returns execution_id."""
    mock_repo.models.STATUS_PENDING = models.STATUS_PENDING
    mock_repo.create_execution.return_value = 42
    eid = state_manager.create_execution()
    mock_repo.create_execution.assert_called_once()
    call_kw = mock_repo.create_execution.call_args[1]
    assert call_kw["status"] == models.STATUS_PENDING
    assert eid == 42


@patch("src.orchestration.state_manager.repository")
def test_create_execution_passes_db_path(mock_repo):
    """create_execution passes db_path to repository."""
    mock_repo.models.STATUS_PENDING = models.STATUS_PENDING
    mock_repo.create_execution.return_value = 1
    db = Path("/tmp/test.db")
    state_manager.create_execution(db_path=db)
    assert mock_repo.create_execution.call_args[1]["db_path"] == db


@patch("src.orchestration.state_manager.repository")
def test_load_context_returns_none_when_no_execution(mock_repo):
    """load_context returns None when get_execution returns None."""
    mock_repo.get_execution.return_value = None
    assert state_manager.load_context(99) is None
    mock_repo.get_execution.assert_called_once_with(99, db_path=None)


@patch("src.orchestration.state_manager.repository")
def test_load_context_returns_execution_context_from_row(mock_repo):
    """load_context builds ExecutionContext from get_execution row."""
    mock_repo.get_execution.return_value = {
        "id": 10,
        "current_stage": "script",
        "status": "in_progress",
    }
    ctx = state_manager.load_context(10)
    assert isinstance(ctx, ExecutionContext)
    assert ctx.execution_id == 10
    assert ctx.current_stage == "script"
    assert ctx.data == {}


@patch("src.orchestration.state_manager.repository")
def test_load_context_default_stage_when_missing(mock_repo):
    """load_context uses 'start' when current_stage is missing or empty."""
    mock_repo.get_execution.return_value = {"id": 5, "current_stage": None}
    ctx = state_manager.load_context(5)
    assert ctx.current_stage == "start"
    mock_repo.get_execution.return_value = {"id": 6}
    ctx2 = state_manager.load_context(6)
    assert ctx2.current_stage == "start"


@patch("src.orchestration.state_manager.repository")
def test_load_context_passes_db_path(mock_repo):
    """load_context passes db_path to get_execution."""
    mock_repo.get_execution.return_value = None
    db = Path("/var/db/run.db")
    state_manager.load_context(1, db_path=db)
    mock_repo.get_execution.assert_called_once_with(1, db_path=db)


@patch("src.orchestration.state_manager.repository")
def test_save_stage_calls_update_execution(mock_repo):
    """save_stage calls repository.update_execution with execution_id and current_stage."""
    state_manager.save_stage(execution_id=7, stage="quality")
    mock_repo.update_execution.assert_called_once_with(
        7, current_stage="quality", db_path=None
    )


@patch("src.orchestration.state_manager.repository")
def test_save_stage_passes_db_path(mock_repo):
    """save_stage passes db_path to update_execution."""
    db = Path("/tmp/state.db")
    state_manager.save_stage(3, "publish", db_path=db)
    mock_repo.update_execution.assert_called_once_with(
        3, current_stage="publish", db_path=db
    )
