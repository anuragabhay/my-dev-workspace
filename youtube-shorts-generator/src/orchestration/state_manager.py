"""
Execution state management: save/load progress, ExecutionContext for pipeline.
"""
from pathlib import Path
from typing import Optional, Dict, Any

from src.database import repository
from src.agents.base_agent import ExecutionContext


def create_execution(db_path: Optional[Path] = None) -> int:
    """Create a new execution record; return execution_id."""
    return repository.create_execution(
        status=repository.models.STATUS_PENDING,
        db_path=db_path,
    )


def load_context(execution_id: int, db_path: Optional[Path] = None) -> Optional[ExecutionContext]:
    """Build ExecutionContext from DB for an execution. Data is minimal (stage only)."""
    row = repository.get_execution(execution_id, db_path=db_path)
    if not row:
        return None
    return ExecutionContext(
        execution_id=row["id"],
        current_stage=row.get("current_stage") or "start",
        data={},
    )


def save_stage(execution_id: int, stage: str, db_path: Optional[Path] = None) -> None:
    """Update execution current_stage."""
    repository.update_execution(execution_id, current_stage=stage, db_path=db_path)
