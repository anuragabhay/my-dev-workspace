"""
Unit tests for src.orchestration.message_queue (MessageQueue).
Run from repo root: pytest tests/test_message_queue.py -v
"""
from pathlib import Path
from unittest.mock import MagicMock, patch

import sys
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.orchestration.message_queue import MessageQueue
from src.database import models


def test_message_queue_accepts_optional_db_path():
    """MessageQueue can be constructed with or without db_path."""
    q1 = MessageQueue()
    assert q1._db_path is None
    q2 = MessageQueue(db_path=Path("/tmp/test.db"))
    assert q2._db_path == Path("/tmp/test.db")


@patch("src.orchestration.message_queue.repository")
def test_enqueue_calls_repository_with_pending_status(mock_repo):
    """enqueue calls repository.enqueue with from_agent, to_agent, message_type, payload, QUEUE_PENDING."""
    mock_repo.enqueue.return_value = 101
    q = MessageQueue()
    mid = q.enqueue(from_agent="research", to_agent="script", message_type="topic", payload="science")
    mock_repo.enqueue.assert_called_once()
    call_kw = mock_repo.enqueue.call_args[1]
    assert call_kw["from_agent"] == "research"
    assert call_kw["to_agent"] == "script"
    assert call_kw["message_type"] == "topic"
    assert call_kw["payload"] == "science"
    assert call_kw["status"] == models.QUEUE_PENDING
    assert mid == 101


@patch("src.orchestration.message_queue.repository")
def test_enqueue_without_payload_passes_none(mock_repo):
    """enqueue with no payload passes payload=None."""
    mock_repo.enqueue.return_value = 1
    q = MessageQueue()
    q.enqueue(from_agent="a", to_agent="b", message_type="t")
    assert mock_repo.enqueue.call_args[1]["payload"] is None


@patch("src.orchestration.message_queue.repository")
def test_dequeue_returns_dict_when_message_exists(mock_repo):
    """dequeue returns dict from repository.dequeue_next or None."""
    mock_repo.dequeue_next.return_value = {"id": 1, "from_agent": "research", "to_agent": "script"}
    q = MessageQueue()
    msg = q.dequeue()
    assert msg == {"id": 1, "from_agent": "research", "to_agent": "script"}
    mock_repo.dequeue_next.assert_called_once_with(to_agent=None, db_path=None)


@patch("src.orchestration.message_queue.repository")
def test_dequeue_returns_none_when_empty(mock_repo):
    """dequeue returns None when no pending message."""
    mock_repo.dequeue_next.return_value = None
    q = MessageQueue()
    assert q.dequeue() is None


@patch("src.orchestration.message_queue.repository")
def test_dequeue_with_to_agent_filters_by_agent(mock_repo):
    """dequeue(to_agent=X) calls repository.dequeue_next with to_agent=X."""
    mock_repo.dequeue_next.return_value = None
    q = MessageQueue()
    q.dequeue(to_agent="script")
    mock_repo.dequeue_next.assert_called_once_with(to_agent="script", db_path=None)


@patch("src.orchestration.message_queue.repository")
def test_ack_success_calls_mark_message_processed_completed(mock_repo):
    """ack(message_id, success=True) calls mark_message_processed with QUEUE_COMPLETED."""
    q = MessageQueue()
    q.ack(42, success=True)
    mock_repo.mark_message_processed.assert_called_once_with(
        message_id=42, status=models.QUEUE_COMPLETED, db_path=None
    )


@patch("src.orchestration.message_queue.repository")
def test_ack_failure_calls_mark_message_processed_failed(mock_repo):
    """ack(message_id, success=False) calls mark_message_processed with QUEUE_FAILED."""
    q = MessageQueue()
    q.ack(99, success=False)
    mock_repo.mark_message_processed.assert_called_once_with(
        message_id=99, status=models.QUEUE_FAILED, db_path=None
    )


@patch("src.orchestration.message_queue.repository")
def test_ack_default_success_is_true(mock_repo):
    """ack(message_id) without success arg uses success=True."""
    q = MessageQueue()
    q.ack(7)
    mock_repo.mark_message_processed.assert_called_once_with(
        message_id=7, status=models.QUEUE_COMPLETED, db_path=None
    )


@patch("src.orchestration.message_queue.repository")
def test_queue_passes_db_path_to_repository(mock_repo):
    """When MessageQueue is built with db_path, enqueue/dequeue/ack pass it to repository."""
    db = Path("/tmp/queue.db")
    q = MessageQueue(db_path=db)
    mock_repo.enqueue.return_value = 1
    mock_repo.dequeue_next.return_value = None
    q.enqueue("a", "b", "t")
    q.dequeue()
    q.ack(1)
    assert mock_repo.enqueue.call_args[1]["db_path"] == db
    assert mock_repo.dequeue_next.call_args[1]["db_path"] == db
    assert mock_repo.mark_message_processed.call_args[1]["db_path"] == db
