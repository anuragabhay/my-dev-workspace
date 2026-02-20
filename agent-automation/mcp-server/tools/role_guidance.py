"""
Tool: get_role_guidance
Returns role guidance from .cursor/skills/<role>/SKILL.md or .cursor/agents/<role>.md.
"""

from pathlib import Path
from typing import Optional

# Map display name to skill dir / agent file name
_ROLE_TO_DIR = {
    "Lead Engineer": "lead-engineer",
    "Junior Engineer 1": "junior-engineer-1",
    "Junior Engineer 2": "junior-engineer-2",
    "Reviewer": "reviewer",
    "QA Reviewer": "qa-reviewer",
    "UI Reviewer": "ui-reviewer",
    "Tester": "tester",
    "Architect": "architect",
    "PM": "pm",
    "Product Manager": "pm",
    "CTO": "cto",
    "CFO": "cfo",
    "CEO": "ceo",
}


def _workspace_root() -> Path:
    """Resolve workspace root via workspace_config (WORKSPACE_ROOT env or workspace_config.yaml)."""
    try:
        from workspace_config import get_workspace_root
        return get_workspace_root()
    except ImportError:
        return Path(__file__).resolve().parent.parent.parent


def get_role_guidance(role: str, workspace_root: Optional[str] = None) -> dict:
    """
    Get guidance for a role by reading .cursor/skills/<role-dir>/SKILL.md or .cursor/agents/<role>.md.

    Args:
        role: Role name (e.g. "Lead Engineer", "Junior Engineer 1", "Junior Engineer 2", "Reviewer", "Tester", "Architect").
        workspace_root: Workspace root path; defaults to config workspace_path parent or agent-automation parent.

    Returns:
        Dict with keys: role, content (str or summary), source (file path), error (if any).
    """
    root = Path(workspace_root) if workspace_root else _workspace_root()
    # Prefer agent-automation/agents/ (host-agnostic), then .cursor/skills, then .cursor/agents
    agents_auto = root / "agent-automation" / "agents"
    skills_dir = root / ".cursor" / "skills"
    agents_dir = root / ".cursor" / "agents"

    role_stripped = role.strip()
    role_key = _ROLE_TO_DIR.get(role_stripped)
    if not role_key:
        # Support "junior-engineer-1" / "junior-engineer-2" as input
        role_key = role_stripped.lower().replace(" ", "-")
    agent_auto_path = agents_auto / f"{role_key}.md"
    skill_path = skills_dir / role_key / "SKILL.md"
    agent_path = agents_dir / f"{role_key}.md"

    # Prefer agent-automation/agents/ (host-agnostic), then .cursor/skills, then .cursor/agents
    for path in (agent_auto_path, skill_path, agent_path):
        if path.exists():
            try:
                content = path.read_text(encoding="utf-8", errors="replace").strip()
                return {
                    "role": role,
                    "content": content[:4000] if len(content) > 4000 else content,
                    "source": str(path),
                    "error": None,
                }
            except OSError as e:
                return {
                    "role": role,
                    "content": None,
                    "source": str(path),
                    "error": str(e),
                }

    return {
        "role": role,
        "content": None,
        "source": None,
        "error": f"No role file found for '{role}' (tried {agent_auto_path}, {skill_path}, {agent_path})",
    }


def list_roles(workspace_root: Optional[str] = None) -> list:
    """
    Return list of role names and one-line "when to use".
    Uses orchestrator_patterns.md role index if present; else built-in defaults.
    """
    one_liners = {
        "Lead Engineer": "Part 1 of dev split; core implementation, config, venv, main tests",
        "Junior Engineer 1": "Part 2 of dev split; implementation, tests, docs, work log, commit/push",
        "Junior Engineer 2": "Part 3 of dev split; implementation, tests, docs, work log, commit/push",
        "Reviewer": "Code review, quality review",
        "QA Reviewer": "QA-focused review",
        "UI Reviewer": "UI/UX review",
        "Tester": "Test execution, test plans, QA",
        "Architect": "Design, how to implement, architecture validation",
        "PM": "Task breakdown, acceptance criteria, scope",
        "CTO": "Technology, architecture approval",
        "CFO": "Cost tracking and analysis only",
        "CEO": "Strategic, phase transitions",
    }
    return [
        {"role": role, "when_to_use": one_liners.get(role, "—")}
        for role in [
            "Lead Engineer",
            "Junior Engineer 1",
            "Junior Engineer 2",
            "Reviewer",
            "Tester",
            "Architect",
            "PM",
            "CTO",
            "CFO",
        ]
    ]
