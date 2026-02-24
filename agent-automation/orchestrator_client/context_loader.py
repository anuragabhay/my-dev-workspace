"""
Load all required orchestrator context files.
Paths resolved via workspace_config.get_workspace_root().
"""

from pathlib import Path
from typing import NamedTuple

# Add agent-automation to path for workspace_config
_client_dir = Path(__file__).resolve().parent
_agent_automation = _client_dir.parent
import sys
if str(_agent_automation) not in sys.path:
    sys.path.insert(0, str(_agent_automation))

from workspace_config import get_workspace_root


REQUIRED_FILES = [
    "orchestrator_rule.md",
    "orchestrator_patterns.md",
    "workflow.yml",
    "decisions.yml",
    "roles.yml",
]


class OrchestratorContext(NamedTuple):
    """Loaded orchestrator context for one cycle."""

    orchestrator_rule: str
    orchestrator_patterns: str
    workflow: str
    decisions: str
    roles: str
    system_message: str


def load_context() -> OrchestratorContext:
    """
    Load all required orchestrator context files.
    Uses workspace_config.get_workspace_root() for path resolution.
    """
    root = get_workspace_root()
    base = root / "agent-automation"

    def read_file(name: str) -> str:
        path = base / name
        if not path.exists():
            raise FileNotFoundError(f"Required orchestrator context file not found: {path}")
        return path.read_text(encoding="utf-8")

    orchestrator_rule = read_file("orchestrator_rule.md")
    orchestrator_patterns = read_file("orchestrator_patterns.md")
    workflow = read_file("workflow.yml")
    decisions = read_file("decisions.yml")
    roles = read_file("roles.yml")

    system_message = _build_system_message(
        orchestrator_rule=orchestrator_rule,
        orchestrator_patterns=orchestrator_patterns,
        workflow=workflow,
        decisions=decisions,
        roles=roles,
    )

    return OrchestratorContext(
        orchestrator_rule=orchestrator_rule,
        orchestrator_patterns=orchestrator_patterns,
        workflow=workflow,
        decisions=decisions,
        roles=roles,
        system_message=system_message,
    )


def _build_system_message(
    orchestrator_rule: str,
    orchestrator_patterns: str,
    workflow: str,
    decisions: str,
    roles: str,
) -> str:
    """Build the system message from all context files."""
    return f"""# Orchestrator Rule (mandatory)

{orchestrator_rule}

---

# Orchestrator Patterns (canonical reference)

{orchestrator_patterns}

---

# Workflow (workflow.yml)

```yaml
{workflow}
```

---

# Decision Rules (decisions.yml) — priority-ordered

```yaml
{decisions}
```

---

# Roles (roles.yml)

```yaml
{roles}
```

---

You are the Orchestrator. Apply the workflow and decision rules above. Use the MCP tool outputs provided to decide the single next action. Output exactly one of:
- A delegation: `/role task` (e.g. `/lead-engineer Add unit tests for health.py`)
- User Intervention Required: [reason]
- ORCHESTRATION_COMPLETE: [brief summary]
- Run one cycle: get_workspace_status, read PROJECT_WORKSPACE.md, decide next step, delegate if needed."""
