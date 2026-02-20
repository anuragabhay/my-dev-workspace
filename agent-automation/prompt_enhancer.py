"""
Prompt enhancer: appends requirements from roles.yml and division-of-work from workflow.yml
to raw followup prompts (delegation lines or run-cycle prompts).
Used by the stop hook so every injected followup_message is enhanced before return.
"""

from pathlib import Path
from typing import Any


def enhance(raw_prompt: str, context: dict) -> str:
    """
    Enhance a raw followup string with requirements from roles.yml and division-of-work from workflow.yml.

    Args:
        raw_prompt: Followup string (delegation line or run-cycle prompt).
        context: At least workspace_root (Path or str); when delegation: role (e.g. "lead-engineer",
                 "junior-engineer-1", "junior-engineer-2"), optionally stage (e.g. "dev").

    Returns:
        raw_prompt + newline + enhanced block (or raw_prompt unchanged if YAML missing or on error).
    """
    root = context.get("workspace_root")
    if root is None:
        return raw_prompt
    if isinstance(root, str):
        root = Path(root)
    agent_automation = root / "agent-automation"
    workflow_path = agent_automation / "workflow.yml"
    roles_path = agent_automation / "roles.yml"
    if not workflow_path.exists() or not roles_path.exists():
        return raw_prompt

    try:
        import yaml
    except ImportError:
        return raw_prompt

    try:
        with open(roles_path, "r", encoding="utf-8") as f:
            roles_data = yaml.safe_load(f)
        with open(workflow_path, "r", encoding="utf-8") as f:
            workflow_data = yaml.safe_load(f)
    except (OSError, yaml.YAMLError):
        return raw_prompt

    roles = (roles_data or {}).get("roles") or {}
    stages = (workflow_data or {}).get("stages") or {}
    role_key = (context.get("role") or "").strip().lower()
    stage = (context.get("stage") or "").strip().lower()

    parts = []

    # Role-based requirements
    if role_key and role_key in roles:
        r = roles[role_key]
        when = (r.get("when_to_use") or "").strip()
        completion = (r.get("completion_criteria") or "").strip()
        if when or completion:
            req = f"Requirements (from roles): {when}." if when else ""
            if completion:
                req = f"{req} Deliverable: {completion}." if req else f"Deliverable: {completion}."
            if req:
                parts.append(req.strip())

    # Division of work for dev stage
    dev_roles = {"lead-engineer", "junior-engineer-1", "junior-engineer-2"}
    if role_key in dev_roles and (stage == "dev" or not stage):
        parts.append(
            "Division of work: Lead Engineer = part 1, Junior Engineer 1 = part 2, Junior Engineer 2 = part 3; "
            f"this delegation is for {role_key}."
        )

    # Run-cycle prompt (no single delegation): append run-cycle requirements
    is_run_cycle = not _looks_like_delegation_line(raw_prompt)
    if is_run_cycle:
        parts.append(
            "Requirements: Read workflow.yml and orchestrator_patterns.md; for Dev stage divide work into three parts "
            "and delegate to /lead-engineer, /junior-engineer-1, /junior-engineer-2 with clear task text and division of work."
        )

    if not parts:
        return raw_prompt
    block = " ".join(parts)
    return f"{raw_prompt}\n\n{block}"


def _looks_like_delegation_line(text: str) -> bool:
    """True if text looks like a single delegation slash command (e.g. /lead-engineer ...)."""
    t = (text or "").strip()
    if not t.startswith("/"):
        return False
    role_slugs = (
        "lead-engineer",
        "junior-engineer-1",
        "junior-engineer-2",
        "architect",
        "reviewer",
        "tester",
        "pm",
        "cto",
        "cfo",
    )
    rest = t[1:].split(maxsplit=1)[0].lower()
    return rest in role_slugs
