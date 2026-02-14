"""
Data shapes for database tables (no ORM). Used by repository for type hints and validation.
"""
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

# Execution status values per schema
STATUS_PENDING = "pending"
STATUS_IN_PROGRESS = "in_progress"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"

# Message queue status
QUEUE_PENDING = "pending"
QUEUE_PROCESSING = "processing"
QUEUE_COMPLETED = "completed"
QUEUE_FAILED = "failed"


@dataclass
class Execution:
    id: Optional[int]
    status: str
    start_time: Optional[str]
    end_time: Optional[str]
    current_stage: Optional[str]
    error_message: Optional[str]
    cost_total: Optional[float]


@dataclass
class Cost:
    id: Optional[int]
    execution_id: int
    component: str
    cost: float
    timestamp: str


@dataclass
class Video:
    id: Optional[int]
    execution_id: int
    title: Optional[str]
    description: Optional[str]
    youtube_id: Optional[str]
    publish_date: Optional[str]
    script_text: Optional[str]


@dataclass
class Embedding:
    id: Optional[int]
    video_id: int
    embedding_vector: bytes  # JSON array as bytes
    created_at: str


@dataclass
class MessageQueue:
    id: Optional[int]
    from_agent: str
    to_agent: str
    message_type: str
    payload: Optional[str]
    status: str
    created_at: str
    processed_at: Optional[str]
