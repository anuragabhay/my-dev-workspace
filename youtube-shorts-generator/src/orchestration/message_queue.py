"""
SQLite-based message queue for agent communication.
"""
from pathlib import Path
from typing import Optional

from src.database import repository
from src.database import models


class MessageQueue:
    """Queue interface: enqueue, dequeue, ack."""

    def __init__(self, db_path: Optional[Path] = None):
        self._db_path = db_path

    def enqueue(
        self,
        from_agent: str,
        to_agent: str,
        message_type: str,
        payload: Optional[str] = None,
    ) -> int:
        """Add message; return message id."""
        return repository.enqueue(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            payload=payload,
            status=models.QUEUE_PENDING,
            db_path=self._db_path,
        )

    def dequeue(self, to_agent: Optional[str] = None) -> Optional[dict]:
        """Get next pending message; mark as processing. Returns row dict or None."""
        return repository.dequeue_next(to_agent=to_agent, db_path=self._db_path)

    def ack(self, message_id: int, success: bool = True) -> None:
        """Mark message completed or failed."""
        status = models.QUEUE_COMPLETED if success else models.QUEUE_FAILED
        repository.mark_message_processed(message_id=message_id, status=status, db_path=self._db_path)
