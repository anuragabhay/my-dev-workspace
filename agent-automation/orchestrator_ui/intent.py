"""
Intent detection for Orchestrator UI: chat vs orchestration.
Keyword heuristics + slash-command detection from roles.yml.
Default ambiguous to orchestration.
"""

from pathlib import Path
from typing import List

# Chat triggers: exact match, prefix/substring for greetings (e.g. "hi there")
CHAT_KEYWORDS = frozenset({
    "hi", "hello", "hey", "thanks", "thank you", "ok", "okay", "got it",
    "bye", "goodbye", "what can you do", "help",
})
# Prefixes for substring matching (e.g. "hi there", "hello world")
CHAT_PREFIXES = frozenset({
    "hi", "hello", "hey", "thanks", "thank", "ok", "okay", "got it",
    "bye", "goodbye", "help",
})
# Substring phrases (e.g. "what can you do")
CHAT_PHRASES = frozenset({"what can you do"})

ORCHESTRATION_KEYWORDS = frozenset({
    "run", "cycle", "continue", "delegate", "orchestrate", "next", "proceed", "start",
})


def _load_slash_commands(workspace_root: Path) -> List[str]:
    """Load slash command values from roles.yml. Returns full slash strings (e.g. /lead-engineer)."""
    try:
        import yaml
    except ImportError:
        return []
    roles_path = workspace_root / "agent-automation" / "roles.yml"
    if not roles_path.exists():
        return []
    try:
        with open(roles_path, "r") as f:
            data = yaml.safe_load(f)
        roles = data.get("roles") or {}
        result = []
        for rid, r in roles.items():
            slash = r.get("slash")
            if slash and isinstance(slash, str) and slash.startswith("/"):
                result.append(slash.strip().lower())
        return result
    except Exception:
        return []


def detect_intent(
    text: str,
    slash_commands: List[str],
) -> str:
    """
    Returns 'chat' or 'orchestration' based on keyword heuristics.
    Default ambiguous to orchestration.
    """
    t = text.strip().lower()
    if not t:
        return "chat"

    # Slash command → orchestration (from roles.yml)
    if slash_commands:
        for slash in slash_commands:
            if t.startswith(slash) or t.startswith(slash + " "):
                return "orchestration"

    # Exact match
    if t in CHAT_KEYWORDS:
        return "chat"

    # Prefix match for greetings (e.g. "hi there", "hello!")
    parts = t.split()
    first_word = parts[0] if parts else ""
    if first_word in CHAT_PREFIXES:
        return "chat"
    for prefix in CHAT_PREFIXES:
        if t.startswith(prefix + " ") or t.startswith(prefix + "!") or t.startswith(prefix + ","):
            return "chat"

    # Substring phrase (e.g. "what can you do")
    for phrase in CHAT_PHRASES:
        if phrase in t:
            return "chat"

    # Orchestration keywords
    if any(k in t for k in ORCHESTRATION_KEYWORDS):
        return "orchestration"

    # Default: orchestration
    return "orchestration"


def get_slash_commands_for_workspace(workspace_root: Path) -> List[str]:
    """Load slash commands from roles.yml for the given workspace."""
    return _load_slash_commands(workspace_root)


def get_slash_commands_list(workspace_root: Path) -> List[dict]:
    """
    Load slash commands with role metadata from roles.yml.
    Returns list of { slash, role, display_name } for roles with slash.
    """
    try:
        import yaml
    except ImportError:
        return []
    roles_path = workspace_root / "agent-automation" / "roles.yml"
    if not roles_path.exists():
        return []
    try:
        with open(roles_path, "r") as f:
            data = yaml.safe_load(f)
        roles = data.get("roles") or {}
        result = []
        for rid, r in roles.items():
            slash = r.get("slash")
            if slash and isinstance(slash, str) and slash.startswith("/"):
                result.append({
                    "slash": slash.strip(),
                    "role": rid,
                    "display_name": r.get("display_name") or rid.replace("-", " ").title(),
                })
        return result
    except Exception:
        return []
