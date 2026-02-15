#!/usr/bin/env python3
"""
Cursor stop hook. followup_message is injected into the SAME chat that stopped.
- Subagent chat stopped: return {} so nothing is injected; control returns to Orchestrator automatically.
- Orchestrator chat stopped: return followup to continue the loop (delegation slash command or run-cycle
  prompt), unless Orchestrator wrote ORCHESTRATION_COMPLETE or we hit User Intervention / loop limit.
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
    """True if Next Actions suggests another cycle: contains CONTINUE or 'next cycle'."""
    d = dashboard.upper()
    return "CONTINUE" in d or "NEXT CYCLE" in d


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

# Pattern to extract slash command even in prose (e.g. "run /lead-engineer with: \"task\"").
# Match /role anywhere; we take the last match and normalize.
_DELEGATION_EXTRACT_PATTERN = re.compile(
    r"/(?:lead-engineer|architect|intern|pm|cto|cfo)\s*:?\s*[^\n]+",
    re.IGNORECASE,
)


def _normalize_delegation_command(raw: str) -> str:
    """Remove ' with:', colon after role, and surrounding quotes so runner gets /role task."""
    s = raw.strip()
    role_end = re.search(r"/(?:lead-engineer|architect|intern|pm|cto|cfo)\s*:?\s*", s, re.I)
    if role_end:
        prefix = role_end.group(0).replace(":", " ").replace("  ", " ")
        rest = s[role_end.end() :].strip()
        # "with: \"task\"" or "with: task" -> "task"
        rest = re.sub(r"^with\s*:\s*", "", rest, flags=re.I)
        if rest.startswith('"') and rest.endswith('"'):
            rest = rest[1:-1]
        s = prefix + rest
    return s


def _extract_delegation_command(transcript_content: str) -> str | None:
    """
    Extract the slash command line from the last assistant message.
    Returns e.g. "/lead-engineer Add README ..." or "/intern Commit and push ..."
    or None if no delegation line found.
    """
    recent = transcript_content[-4000:] if len(transcript_content) > 4000 else transcript_content
    matches = _DELEGATION_EXTRACT_PATTERN.findall(recent)
    if matches:
        return _normalize_delegation_command(matches[-1])
    return None


def _last_response_contains_delegation(transcript_content: str) -> bool:
    """True if the last response contains a delegation."""
    return _extract_delegation_command(transcript_content) is not None


def _orchestrator_marked_complete(transcript_content: str) -> bool:
    """True if Orchestrator wrote ORCHESTRATION_COMPLETE (or similar) in recent output."""
    recent = transcript_content[-3000:] if len(transcript_content) > 3000 else transcript_content
    return "orchestration_complete" in recent.lower() or "orchestration complete" in recent.lower()


def _delegated_task_already_done_in_transcript(transcript_content: str) -> bool:
    """True if recent transcript shows the delegated role already finished (avoids re-injecting same delegation).
    Use only markers that indicate the subagent completed, not generic cycle activity (work log, Updated)."""
    recent = transcript_content[-5000:] if len(transcript_content) > 5000 else transcript_content
    r = recent.lower()
    markers = (
        "phase 6 for this scope is done",
        "phase 6 ... is already complete",
        "no further item",
        "no further work",
        "hand off to intern",   # Architect validation done
        "hand off to intern for commit",
        "pushed to origin",
        "pushed to master",
    )
    return any(m in r for m in markers)


def _transcript_shows_recent_completion(transcript_content: str) -> bool:
    """True if recent transcript shows a subagent just finished a task (Done, tests passed, COMPLETED, work log added).
    Used to continue the loop when Next Actions don't say 'next cycle' but the last turn was a completion."""
    recent = transcript_content[-4000:] if len(transcript_content) > 4000 else transcript_content
    r = recent.lower()
    markers = (
        "\ndone.",
        "done.",
        "one cycle done",
        " passed ",
        "passed in ",
        " tests pass",
        "all 7 pass",
        "test_pipeline",
        "pipeline unit tests",
        "status completed",
        "status: completed",
        "lead engineer entry added",
        "work log: lead engineer",
        "implementation: added",
        "phase 2: added",
    )
    return any(m in r for m in markers)


# Subagent role markers in transcript (first 3000 chars)
_SUBAGENT_MARKERS = (
    "You are the **Intern**",
    "You are the **Lead Engineer**",
    "You are the **Architect**",
    "You are the **CTO**",
    "You are the **CFO**",
    "You are the **Product Manager**",
    "name: lead-engineer",
    "name: architect",
    "name: intern",
    "name: cto",
    "name: cfo",
    "name: pm",
)


def _is_subagent_chat(transcript_head: str) -> bool:
    """True if the transcript appears to be from a workspace subagent (Intern, Lead Engineer, etc.)."""
    return any(marker in transcript_head for marker in _SUBAGENT_MARKERS)


def _orchestrator_run_cycle_prompt(root: Path) -> str:
    """Read the canonical orchestrator run-cycle prompt from agent-automation/prompts."""
    path = root / "agent-automation" / "prompts" / "orchestrator_run_cycle.md"
    if path.exists():
        try:
            return path.read_text(encoding="utf-8", errors="replace").strip()
        except OSError:
            pass
    return (
        "Run one cycle: get_workspace_status, read PROJECT_WORKSPACE.md (Dashboard, Next Actions, Role Status). "
        "Determine which role the next action is for from Next Actions; call check_my_pending_tasks(role=\"<that role>\") — e.g. Lead Engineer, Architect, Intern, PM, CTO, CFO. "
        "Then decide next step, delegate if needed, update PROJECT_WORKSPACE.md."
    )


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
    root = _workspace_root(payload)

    # 2a) Prefer Orchestrator: if transcript has Orchestrator markers, treat as Orchestrator (it may also contain subagent content from a prior /intern or /lead-engineer run).
    is_orchestrator = "parent Orchestrator" in head or "orchestrator.mdc" in head
    if not is_orchestrator:
        # 2b) Subagent-only chat → return {} so we don't inject into subagent.
        if _is_subagent_chat(head):
            print(json.dumps({}))
            return
        print(json.dumps({}))
        return

    # 3) Orchestrator marked complete → stop loop
    if _orchestrator_marked_complete(transcript_content):
        print(json.dumps({}))
        return

    # 4) CONTINUE logic (only for Orchestrator)
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
    # Continue when: Next Actions says continue, or pending approvals, or Orchestrator just delegated, or a subagent just completed a task.
    has_continue = _next_actions_has_continue(dashboard) or _has_pending_approvals(dashboard)
    has_delegation = _last_response_contains_delegation(transcript_content)
    just_completed = _transcript_shows_recent_completion(transcript_content)
    if not has_continue and not has_delegation and not just_completed:
        print(json.dumps({}))
        return

    if has_delegation:
        delegation_cmd = _extract_delegation_command(transcript_content)
        if delegation_cmd and not _delegated_task_already_done_in_transcript(transcript_content):
            print(json.dumps({"followup_message": delegation_cmd}))
            return
        # Transcript already shows task done (Done, COMPLETED, work log, etc.) — run a cycle instead of re-injecting same delegation.

    followup = _orchestrator_run_cycle_prompt(root)
    print(json.dumps({"followup_message": followup}))


if __name__ == "__main__":
    main()
