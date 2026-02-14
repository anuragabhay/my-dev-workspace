"""
Cost tracking: log API costs to database and optional in-memory tally.
"""
from pathlib import Path
from typing import Optional

# Lazy import to avoid circular deps
def _repo():
    from src.database import repository
    return repository


def log_cost(
    execution_id: int,
    component: str,
    cost: float,
    db_path: Optional[Path] = None,
) -> None:
    """Log a single cost entry to the costs table."""
    _repo().insert_cost(execution_id=execution_id, component=component, cost=cost, db_path=db_path)


def get_execution_cost_total(execution_id: int, db_path: Optional[Path] = None) -> float:
    """Sum costs for an execution from the database."""
    return _repo().get_execution_cost_total(execution_id=execution_id, db_path=db_path)
