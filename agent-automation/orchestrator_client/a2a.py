"""
Agent-to-Agent (A2A) communication layer.

Enables platform-agnostic agent coordination: orchestrator ↔ subagents,
subagent ↔ subagent. Compatible with A2A-style patterns for task handoff,
request/response, and agent identity. This layer allows agents to talk
among themselves when running outside Cursor (e.g. locally, Claude Code,
Vertex, or custom apps).

Message format is designed to be:
- Host-independent (no Cursor-specific hooks or config)
- Extensible (can later use HTTP/JSON-RPC/SSE for multi-host)
- Clear identity and task semantics
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class AgentRole(str, Enum):
    """Stable agent identity for A2A messages."""

    ORCHESTRATOR = "orchestrator"
    LEAD_ENGINEER = "lead-engineer"
    JUNIOR_ENGINEER_1 = "junior-engineer-1"
    JUNIOR_ENGINEER_2 = "junior-engineer-2"
    ARCHITECT = "architect"
    REVIEWER = "reviewer"
    QA_REVIEWER = "qa-reviewer"
    UI_REVIEWER = "ui-reviewer"
    TESTER = "tester"
    PM = "pm"
    CTO = "cto"
    CFO = "cfo"


class MessageType(str, Enum):
    """A2A message types."""

    TASK_REQUEST = "task_request"  # Orchestrator → subagent: "do this"
    TASK_RESPONSE = "task_response"  # Subagent → orchestrator: "done / result"
    TASK_HANDOFF = "task_handoff"  # Subagent → subagent: handoff
    QUERY = "query"  # Agent → agent: request info
    QUERY_RESPONSE = "query_response"  # Agent → agent: info response


class TaskStatus(str, Enum):
    """Status of a task in A2A."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class A2AMessage:
    """
    Structured A2A message for agent-to-agent communication.

    Enables:
    - Agent identity (from_role, to_role)
    - Task handoff (task_id, payload, status)
    - Request/response semantics (message_type)
    - Optional async/long-running (status, created_at)
    """

    message_type: MessageType
    from_role: AgentRole
    to_role: AgentRole
    task_id: str
    payload: dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    correlation_id: Optional[str] = None  # For request/response pairing

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict for JSON/HTTP transport."""
        return {
            "message_type": self.message_type.value,
            "from_role": self.from_role.value,
            "to_role": self.to_role.value,
            "task_id": self.task_id,
            "payload": self.payload,
            "status": self.status.value,
            "created_at": self.created_at,
            "correlation_id": self.correlation_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "A2AMessage":
        """Deserialize from dict."""
        return cls(
            message_type=MessageType(data["message_type"]),
            from_role=AgentRole(data["from_role"]),
            to_role=AgentRole(data["to_role"]),
            task_id=data["task_id"],
            payload=data.get("payload", {}),
            status=TaskStatus(data.get("status", "pending")),
            created_at=data.get("created_at", ""),
            correlation_id=data.get("correlation_id"),
        )


def create_task_request(
    to_role: AgentRole,
    task_id: str,
    task_description: str,
    context: Optional[dict[str, Any]] = None,
) -> A2AMessage:
    """Create a task request from orchestrator to subagent."""
    return A2AMessage(
        message_type=MessageType.TASK_REQUEST,
        from_role=AgentRole.ORCHESTRATOR,
        to_role=to_role,
        task_id=task_id,
        payload={
            "task_description": task_description,
            "context": context or {},
        },
        status=TaskStatus.PENDING,
    )


def create_task_response(
    from_role: AgentRole,
    task_id: str,
    outcome: str,
    result: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
) -> A2AMessage:
    """Create a task response from subagent to orchestrator."""
    return A2AMessage(
        message_type=MessageType.TASK_RESPONSE,
        from_role=from_role,
        to_role=AgentRole.ORCHESTRATOR,
        task_id=task_id,
        payload={
            "outcome": outcome,
            "result": result or {},
        },
        status=TaskStatus.COMPLETED,
        correlation_id=correlation_id,
    )
