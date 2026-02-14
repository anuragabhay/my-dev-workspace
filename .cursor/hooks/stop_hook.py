#!/usr/bin/env python3
"""
Cursor stop hook. Returns followup_message only when the conversation that stopped
is the Orchestrator chat (detected via transcript content). Other chats get {}.
"""
import json
import re
import sys
from pathlib import Path


def _workspace_root(payload: dict) -> Path:
    """Resolve workspace root: from payload workspace_roots if provided, else from hook script location."""
    roots = payload.get("workspace_roots") or payload.get("workspace_root")
    if roots:
        if isinstance(roots, list) and roots:
            return Path(roots[0])
        if isinstance(roots, str):
            return Path(roots)
    # Hook lives at .cursor/hooks/stop_hook.py -> parent.parent = workspace root
    return Path(__file__).resolve().parent.parent.parent


def _dashboard_section(content: str) -> str:
    """Extract Dashboard section text (from ## 📊 Project Status Dashboard to next ## or end)."""
    start = content.find("## 📊 Project Status Dashboard")
    if start == -1:
        return ""
    start = content.find("\n", start) + 1
    end = content.find("\n## ", start)
    if end == -1:
        end = len(content)
    return content[start:end]


def _user_intervention_required(dashboard: str) -> bool:
    """True if Dashboard says User Intervention Required: Yes."""
    return "User Intervention Required" in dashboard and "Yes" in dashboard.split("User Intervention Required")[-1].split("\n")[0]


def _next_actions_has_continue(dashboard: str) -> bool:
    """True if Next Actions line contains the word CONTINUE."""
    return "CONTINUE" in dashboard


def _has_pending_approvals(dashboard: str) -> bool:
    """True if Pending Approvals is present and not 0."""
    match = re.search(r"Pending Approvals[:\s]+\*?\*?(\d+)", dashboard, re.IGNORECASE)
    if not match:
        return False
    return int(match.group(1)) > 0


# Regex to detect delegation slash commands in the last assistant message
_DELEGATION_PATTERN = re.compile(
    r"/(?:lead-engineer|architect|intern|pm|cto|cfo)(?:\s|$)",
    re.IGNORECASE,
)

# Pattern to extract the full delegation line (slash command + task text)
_DELEGATION_EXTRACT_PATTERN = re.compile(
    r"(?:^|\n)(/(?:lead-engineer|architect|intern|pm|cto|cfo)\s+[^\n]+)",
    re.MULTILINE | re.IGNORECASE,
)


def _extract_delegation_command(transcript_content: str) -> str | None:
    """
    Extract the slash command line from the last assistant message.
    Returns e.g. "/lead-engineer Add README Troubleshooting/Configuration section to ..."
    or None if no delegation line found.
    """
    recent = transcript_content[-4000:] if len(transcript_content) > 4000 else transcript_content
    matches = _DELEGATION_EXTRACT_PATTERN.findall(recent)
    if matches:
        return matches[-1].strip()
    return None


def _last_response_contains_delegation(transcript_content: str) -> bool:
    """True if the last response contains a delegation."""
    return _extract_delegation_command(transcript_content) is not None


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        print(json.dumps({}))
        return

    transcript_path = payload.get("transcript_path")
    loop_count = int(payload.get("loop_count", 0))

    # 1) No transcript_path or file missing -> no follow-up
    if not transcript_path:
        print(json.dumps({}))
        return
    path = Path(transcript_path)
    if not path.exists():
        print(json.dumps({}))
        return

    # 2) Orchestrator detection: "parent Orchestrator" or "orchestrator.mdc" must appear in the first 3000 chars
    try:
        transcript_content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        print(json.dumps({}))
        return
    head = transcript_content[:3000]
    if "parent Orchestrator" not in head and "orchestrator.mdc" not in head:
        print(json.dumps({}))
        return

    # 3) CONTINUE logic (only for Orchestrator)
    root = _workspace_root(payload)
    workspace_md = root / "PROJECT_WORKSPACE.md"
    if not workspace_md.exists():
        print(json.dumps({}))
        return
    try:
        content = workspace_md.read_text(encoding="utf-8", errors="replace")
    except OSError:
        print(json.dumps({}))
        return

    dashboard = _dashboard_section(content)
    if _user_intervention_required(dashboard):
        print(json.dumps({}))
        return
    if loop_count >= 5:
        print(json.dumps({}))
        return
    if not _next_actions_has_continue(dashboard) and not _has_pending_approvals(dashboard):
        print(json.dumps({}))
        return

    if _last_response_contains_delegation(transcript_content):
        delegation_cmd = _extract_delegation_command(transcript_content)
        if delegation_cmd:
            print(json.dumps({"followup_message": delegation_cmd}))
            return

    followup = (
        "Run one cycle: get_workspace_status, check_my_pending_tasks(Lead Engineer), "
        "read PROJECT_WORKSPACE.md, decide next step, delegate if needed, update PROJECT_WORKSPACE.md."
    )
    print(json.dumps({"followup_message": followup}))


if __name__ == "__main__":
    main()
