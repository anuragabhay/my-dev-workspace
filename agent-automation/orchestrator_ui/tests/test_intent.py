"""
Unit tests for orchestrator_ui/intent.py — intent detection (chat vs orchestration).
"""

import pytest
from pathlib import Path

# Add agent-automation to path
import sys
_agent_automation = Path(__file__).resolve().parent.parent.parent
if str(_agent_automation) not in sys.path:
    sys.path.insert(0, str(_agent_automation))

from orchestrator_ui.intent import detect_intent, get_slash_commands_for_workspace


class TestDetectIntent:
    """Test detect_intent returns 'chat' or 'orchestration' correctly."""

    def test_empty_string_returns_chat(self):
        assert detect_intent("", []) == "chat"
        assert detect_intent("   ", []) == "chat"

    def test_chat_keywords_exact_match(self):
        for word in ["hi", "hello", "hey", "thanks", "thank you", "ok", "okay", "got it", "bye", "goodbye", "help"]:
            assert detect_intent(word, []) == "chat", f"'{word}' should be chat"

    def test_chat_prefix_match(self):
        assert detect_intent("hi there", []) == "chat"
        assert detect_intent("hello world", []) == "chat"
        assert detect_intent("hey!", []) == "chat"
        assert detect_intent("thanks a lot", []) == "chat"

    def test_orchestration_keywords(self):
        assert detect_intent("run one cycle", []) == "orchestration"
        assert detect_intent("continue", []) == "orchestration"
        assert detect_intent("delegate to lead engineer", []) == "orchestration"
        assert detect_intent("orchestrate", []) == "orchestration"
        assert detect_intent("next step", []) == "orchestration"
        assert detect_intent("proceed", []) == "orchestration"
        assert detect_intent("start", []) == "orchestration"

    def test_slash_command_orchestration(self):
        slash_commands = ["/lead-engineer", "/architect", "/junior-engineer-1"]
        assert detect_intent("/lead-engineer add tests", slash_commands) == "orchestration"
        assert detect_intent("/architect review design", slash_commands) == "orchestration"
        assert detect_intent("/junior-engineer-1", slash_commands) == "orchestration"

    def test_slash_takes_precedence_over_chat(self):
        # "hello" is chat, but /hello would be orchestration if in roles
        slash_commands = ["/lead-engineer"]
        assert detect_intent("hello", slash_commands) == "chat"
        assert detect_intent("/lead-engineer hello", slash_commands) == "orchestration"

    def test_default_ambiguous_to_orchestration(self):
        assert detect_intent("add unit tests for health.py", []) == "orchestration"
        assert detect_intent("fix the bug in server.py", []) == "orchestration"
        assert detect_intent("random task instruction", []) == "orchestration"

    def test_case_insensitive(self):
        assert detect_intent("HELLO", []) == "chat"
        assert detect_intent("Run One Cycle", []) == "orchestration"

    def test_what_can_you_do_phrase(self):
        assert detect_intent("what can you do", []) == "chat"
        assert detect_intent("what can you do for me", []) == "chat"


class TestGetSlashCommands:
    """Test get_slash_commands_for_workspace loads from roles.yml."""

    def test_loads_from_workspace(self):
        # Use agent-automation parent (workspace root) which has roles.yml
        workspace_root = Path(__file__).resolve().parent.parent.parent.parent
        slash = get_slash_commands_for_workspace(workspace_root)
        assert isinstance(slash, list)
        # roles.yml has /lead-engineer, /junior-engineer-1, etc.
        if slash:
            assert any("/lead-engineer" in s or s == "/lead-engineer" for s in slash)

    def test_missing_roles_returns_empty(self):
        slash = get_slash_commands_for_workspace(Path("/nonexistent/path"))
        assert slash == []
