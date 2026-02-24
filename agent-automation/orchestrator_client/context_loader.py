"""
Load orchestrator context: system message from orchestrator_rule, patterns, workflow, decisions, roles.
Used by cycle_runner and orchestrator UI when running the brain.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Add agent-automation to path for workspace_config
_client_dir = Path(__file__).resolve().parent
_agent_automation = _client_dir.parent
if str(_agent_automation) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(_agent_automation))

from workspace_config import get_workspace_root


@dataclass
class OrchestratorContext:
    """Orchestrator context with system message for the brain."""

    system_message: str


def _read_file(path: Path, default: str = "") -> str:
    """Read file or return default if not found."""
    if not path.exists():
        return default
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return default


def load_context() -> OrchestratorContext:
    """
    Load orchestrator context: assembles system message from orchestrator_rule,
    orchestrator_patterns, workflow.yml, decisions.yml, roles.yml.

    Returns:
        OrchestratorContext with system_message for run_brain.
    """
    root = get_workspace_root()
    agent_automation = root / "agent-automation"

    rule = _read_file(agent_automation / "orchestrator_rule.md")
    patterns = _read_file(agent_automation / "orchestrator_patterns.md")
    workflow = _read_file(agent_automation / "workflow.yml")
    decisions = _read_file(agent_automation / "decisions.yml")
    roles = _read_file(agent_automation / "roles.yml")

    # Strip HTML comment from orchestrator_rule if present
    if rule.startswith("<!--"):
        idx = rule.find("-->")
        if idx >= 0:
            rule = rule[idx + 3 :].strip()

    parts = [
        rule,
        "\n---\n\n## Orchestrator Patterns\n\n",
        patterns,
        "\n---\n\n## Workflow (workflow.yml)\n\n```yaml\n",
        workflow,
        "\n```\n\n---\n\n## Decision Rules (decisions.yml)\n\n```yaml\n",
        decisions,
        "\n```\n\n---\n\n## Roles (roles.yml)\n\n```yaml\n",
        roles,
        "\n```",
    ]
    system_message = "".join(parts)
    return OrchestratorContext(system_message=system_message)
