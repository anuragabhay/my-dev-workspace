"""
API tests for orchestrator_ui POST /api/chat and config endpoints.
Tests error cases (400, 500, network), mode routing, intent detection,
streaming SSE, and MCP fallback.
"""

import json
import os
import re
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add agent-automation to path
_agent_automation = Path(__file__).resolve().parent.parent.parent
if str(_agent_automation) not in sys.path:
    sys.path.insert(0, str(_agent_automation))

from fastapi.testclient import TestClient

# Import app after path setup
from orchestrator_ui.server import app

client = TestClient(app)


def _chat_request(messages, mode="auto", include_flow=True):
    payload = {"messages": messages, "mode": mode, "include_flow": include_flow}
    return client.post("/api/chat", json=payload)


class TestChatEndpointErrors:
    """Test 400 and 500 error cases."""

    def test_400_empty_messages(self):
        """Empty messages → 400."""
        r = _chat_request([])
        assert r.status_code == 400
        data = r.json()
        assert "error" in data or "detail" in data

    def test_400_empty_messages_list(self):
        """Explicit empty list → 400."""
        r = client.post("/api/chat", json={"messages": [], "mode": "auto"})
        assert r.status_code == 400

    def test_500_no_api_key(self):
        """No API key in env → 500."""
        env_patch = {
            "ANTHROPIC_API_KEY": "",
            "ORCHESTRATOR_LLM_API_KEY": "",
            "OPENAI_API_KEY": "",
            "ORCHESTRATOR_OPENAI_API_KEY": "",
            "ORCHESTRATOR_LLM_PROVIDER": "local",
        }
        with patch.dict(os.environ, env_patch, clear=False):
            r = _chat_request([{"role": "user", "content": "hello"}])
            assert r.status_code == 500
            data = r.json()
            assert "error" in data or "detail" in data
            err = data.get("error") or data.get("detail", "")
            assert "API key" in str(err) or "key" in str(err).lower()


class TestChatEndpointModeRouting:
    """Test mode=auto routes to chat vs orchestration based on intent."""

    @pytest.fixture(autouse=True)
    def ensure_api_key(self):
        """Ensure API key is set so handlers run (provider=local, openai key satisfies active_key check)."""
        os.environ["ORCHESTRATOR_LLM_PROVIDER"] = "local"
        os.environ["OPENAI_API_KEY"] = "sk-test-fake-key-for-testing"
        yield
        # Don't clear - other tests may need it

    def test_mode_auto_hello_routes_to_chat(self):
        """'hello' with mode=auto → chat handler (mocked)."""
        with patch("orchestrator_ui.server._chat_handler") as mock_chat:
            mock_chat.return_value = {"reply": "Hello! How can I help?", "mode_used": "chat"}
            r = _chat_request([{"role": "user", "content": "hello"}])
            assert r.status_code == 200
            data = r.json()
            assert data["mode_used"] == "chat"
            assert data["reply"] == "Hello! How can I help?"
            mock_chat.assert_called_once()

    def test_mode_auto_run_cycle_routes_to_orchestration(self):
        """'run one cycle' with mode=auto → orchestration handler (mocked)."""
        with patch("orchestrator_ui.server._orchestration_handler") as mock_orch:
            mock_orch.return_value = {
                "reply": "/lead-engineer Add tests",
                "mode_used": "orchestration",
                "flow": {"proposal": "p", "critique": "c", "synthesis": "s"},
            }
            r = _chat_request([{"role": "user", "content": "run one cycle"}])
            assert r.status_code == 200
            data = r.json()
            assert data["mode_used"] == "orchestration"
            assert "flow" in data
            assert data["flow"]["proposal"] == "p"
            mock_orch.assert_called_once()

    def test_mode_force_chat(self):
        """mode=chat forces chat handler regardless of message."""
        with patch("orchestrator_ui.server._chat_handler") as mock_chat:
            mock_chat.return_value = {"reply": "Forced chat reply", "mode_used": "chat"}
            r = _chat_request([{"role": "user", "content": "run one cycle"}], mode="chat")
            assert r.status_code == 200
            assert r.json()["mode_used"] == "chat"
            mock_chat.assert_called_once()

    def test_mode_force_orchestration(self):
        """mode=orchestration forces orchestration handler regardless of message."""
        with patch("orchestrator_ui.server._orchestration_handler") as mock_orch:
            mock_orch.return_value = {
                "reply": "Orchestration reply",
                "mode_used": "orchestration",
                "flow": {"proposal": "p", "critique": "c", "synthesis": "s"},
            }
            r = _chat_request([{"role": "user", "content": "hello"}], mode="orchestration")
            assert r.status_code == 200
            assert r.json()["mode_used"] == "orchestration"
            mock_orch.assert_called_once()


class TestRunBrainEndpoint:
    """Test POST /api/run-brain provider abstraction and key resolution."""

    def test_500_no_api_key_openai(self):
        """provider=openai, no OPENAI_API_KEY → 500 with appropriate error."""
        env_patch = {
            "ANTHROPIC_API_KEY": "",
            "ORCHESTRATOR_LLM_API_KEY": "",
            "OPENAI_API_KEY": "",
            "ORCHESTRATOR_OPENAI_API_KEY": "",
            "ORCHESTRATOR_LLM_PROVIDER": "openai",
        }
        with patch.dict(os.environ, env_patch, clear=False):
            r = client.post("/api/run-brain", json={})
            assert r.status_code == 500
            data = r.json()
            detail = data.get("detail", "")
            assert "API key" in detail or "key" in detail.lower()
            assert "OPENAI" in detail.upper() or "openai" in detail


class TestConfigStatus:
    """Test GET /api/config-status."""

    def test_config_status_returns_booleans(self):
        """Config status returns api_key_configured and workspace_configured."""
        r = client.get("/api/config-status")
        assert r.status_code == 200
        data = r.json()
        assert "api_key_configured" in data
        assert "workspace_configured" in data
        assert isinstance(data["api_key_configured"], bool)
        assert isinstance(data["workspace_configured"], bool)

    def test_config_status_ok_when_key_and_workspace(self):
        """When both configured, values are True."""
        with patch.dict(
            os.environ,
            {"ORCHESTRATOR_LLM_PROVIDER": "local", "ANTHROPIC_API_KEY": "sk-test"},
            clear=False,
        ):
            with patch("orchestrator_ui.server.get_workspace_root") as mock_root:
                mock_root.return_value = Path(__file__).parent.parent.parent.parent
                r = client.get("/api/config-status")
                assert r.status_code == 200
                data = r.json()
                assert data["api_key_configured"] is True
                # workspace_configured depends on PROJECT_WORKSPACE.md existing


class TestInvalidMode:
    """Test invalid mode handling (Pydantic validation)."""

    def test_invalid_mode_rejected(self):
        """Invalid mode value → 422 validation error."""
        r = client.post(
            "/api/chat",
            json={
                "messages": [{"role": "user", "content": "hi"}],
                "mode": "invalid",
            },
        )
        assert r.status_code == 422


class TestServerErrorPropagation:
    """Test 500 when handler raises exception."""

    @pytest.fixture(autouse=True)
    def ensure_api_key(self):
        os.environ["ORCHESTRATOR_LLM_PROVIDER"] = "local"
        os.environ["OPENAI_API_KEY"] = "sk-test-fake-key"
        yield

    def test_500_when_chat_handler_raises(self):
        """Chat handler exception → 500 with error message."""
        with patch("orchestrator_ui.server._chat_handler") as mock_chat:
            mock_chat.side_effect = RuntimeError("LLM API failed")
            r = _chat_request([{"role": "user", "content": "hello"}], mode="chat")
            assert r.status_code == 500
            data = r.json()
            assert "error" in data
            assert "LLM API failed" in data["error"]

    def test_500_when_orchestration_handler_raises(self):
        """Orchestration handler exception → 500 with error message."""
        with patch("orchestrator_ui.server._orchestration_handler") as mock_orch:
            mock_orch.side_effect = RuntimeError("Context load failed")
            r = _chat_request([{"role": "user", "content": "run one cycle"}], mode="orchestration")
            assert r.status_code == 500
            data = r.json()
            assert "error" in data
            assert "Context load failed" in data["error"]


class TestIncludeFlow:
    """Test include_flow parameter."""

    @pytest.fixture(autouse=True)
    def ensure_api_key(self):
        os.environ["ORCHESTRATOR_LLM_PROVIDER"] = "local"
        os.environ["OPENAI_API_KEY"] = "sk-test-fake-key"
        yield

    def test_include_flow_false_omits_flow(self):
        """include_flow=false → no flow in response."""
        with patch("orchestrator_ui.server._orchestration_handler") as mock_orch:
            mock_orch.return_value = {
                "reply": "Reply",
                "mode_used": "orchestration",
                # No flow key when include_flow=False
            }
            r = _chat_request(
                [{"role": "user", "content": "run one cycle"}],
                mode="orchestration",
                include_flow=False,
            )
            assert r.status_code == 200
            data = r.json()
            assert "flow" not in data or data.get("flow") is None


class TestStreamingSSE:
    """Test POST /api/chat with Accept: text/event-stream returns SSE."""

    @pytest.fixture(autouse=True)
    def ensure_api_key(self):
        os.environ["ORCHESTRATOR_LLM_PROVIDER"] = "local"
        os.environ["OPENAI_API_KEY"] = "sk-test-fake-key"
        yield

    async def _fake_chat_stream(self, *args, **kwargs):
        """Fake async generator for chat SSE: reply.chunk, reply.done."""
        yield 'data: {"type": "reply.chunk", "content": "Hi"}\n\n'
        yield 'data: {"type": "reply.chunk", "content": " there"}\n\n'
        yield 'data: {"type": "reply.done"}\n\n'

    def test_chat_mode_sse_returns_reply_chunk_and_done(self):
        """POST /api/chat with Accept: text/event-stream and mode=chat returns SSE with reply.chunk, reply.done."""
        with patch("orchestrator_ui.server._chat_handler_stream", side_effect=lambda *a, **k: self._fake_chat_stream()):
            payload = {
                "messages": [{"role": "user", "content": "hello"}],
                "mode": "chat",
            }
            with client.stream(
                "POST",
                "/api/chat",
                json=payload,
                headers={"Accept": "text/event-stream"},
            ) as response:
                assert response.status_code == 200
                assert "text/event-stream" in response.headers.get("content-type", "")
                lines = list(response.iter_lines())
        data_lines = [l for l in lines if l.startswith("data: ")]
        assert len(data_lines) >= 2
        events = [json.loads(l[6:]) for l in data_lines]
        types = [e.get("type") for e in events]
        assert "reply.chunk" in types
        assert "reply.done" in types

    async def _fake_orchestration_stream(self, *args, **kwargs):
        """Fake async generator for orchestration SSE: flow.*, reply.chunk, reply.done."""
        yield 'data: {"type": "flow.proposal", "content": "Proposal text"}\n\n'
        yield 'data: {"type": "flow.critique", "content": "Critique text"}\n\n'
        yield 'data: {"type": "flow.synthesis", "content": ""}\n\n'
        yield 'data: {"type": "reply.chunk", "content": "Final"}\n\n'
        yield 'data: {"type": "reply.done", "content": ""}\n\n'

    def test_orchestration_mode_sse_returns_flow_and_reply_events(self):
        """POST /api/chat with Accept: text/event-stream and mode=orchestration returns flow.* and reply.* events."""
        with patch(
            "orchestrator_ui.server._orchestration_handler_stream",
            side_effect=lambda *a, **k: self._fake_orchestration_stream(),
        ):
            payload = {
                "messages": [{"role": "user", "content": "run one cycle"}],
                "mode": "orchestration",
            }
            with client.stream(
                "POST",
                "/api/chat",
                json=payload,
                headers={"Accept": "text/event-stream"},
            ) as response:
                assert response.status_code == 200
                assert "text/event-stream" in response.headers.get("content-type", "")
                lines = list(response.iter_lines())
        data_lines = [l for l in lines if l.startswith("data: ")]
        assert len(data_lines) >= 4
        events = [json.loads(l[6:]) for l in data_lines]
        types = [e.get("type") for e in events]
        assert "flow.proposal" in types
        assert "flow.critique" in types
        assert "flow.synthesis" in types
        assert "reply.chunk" in types
        assert "reply.done" in types


def _collect_node_names(node):
    """Recursively collect all node names from tree."""
    names = [node.get("name", "")]
    for c in node.get("children", []):
        names.extend(_collect_node_names(c))
    return names


class TestTreeAPI:
    """Test GET /api/tree (Phase 2 Project Structure Panel)."""

    def test_tree_returns_root_node(self):
        """GET /api/tree returns single root node with name, path, type, children."""
        with patch("orchestrator_ui.server.get_workspace_root") as mock_root:
            mock_root.return_value = Path(__file__).resolve().parent.parent.parent
            r = client.get("/api/tree")
            assert r.status_code == 200
            data = r.json()
            assert isinstance(data, dict)
            assert "name" in data
            assert "path" in data
            assert data["type"] == "dir"
            assert "children" in data
            assert isinstance(data["children"], list)
            for node in data["children"][:3]:
                assert "name" in node
                assert "path" in node
                assert node["type"] in ("file", "dir")

    def test_tree_node_structure(self):
        """Each node has name, path, type; dirs may have children."""
        with patch("orchestrator_ui.server.get_workspace_root") as mock_root:
            mock_root.return_value = Path(__file__).resolve().parent.parent.parent
            r = client.get("/api/tree?depth=2&lazy=false")
            assert r.status_code == 200
            data = r.json()
            children = data.get("children", [])
            dirs = [n for n in children if n.get("type") == "dir"]
            if dirs:
                has_children = any("children" in d for d in dirs)
                assert has_children or len(dirs) == 0

    def test_tree_lazy_omits_children(self):
        """lazy=true: dir nodes in children have no children key."""
        with patch("orchestrator_ui.server.get_workspace_root") as mock_root:
            mock_root.return_value = Path(__file__).resolve().parent.parent.parent
            r = client.get("/api/tree?lazy=true")
            assert r.status_code == 200
            data = r.json()
            for node in data.get("children", []):
                if node.get("type") == "dir":
                    assert "children" not in node

    def test_tree_path_traversal_rejected(self):
        """path with .. is rejected with 400."""
        with patch("orchestrator_ui.server.get_workspace_root") as mock_root:
            mock_root.return_value = Path(__file__).resolve().parent.parent.parent
            r = client.get("/api/tree?path=../etc")
            assert r.status_code == 400
            assert "path" in r.json().get("detail", "").lower() or "invalid" in r.json().get("detail", "").lower()

    def test_tree_subdir_path(self):
        """path=subdir returns root node for that subdir with its children."""
        with patch("orchestrator_ui.server.get_workspace_root") as mock_root:
            root = Path(__file__).resolve().parent.parent.parent
            mock_root.return_value = root
            subdir = "agent-automation"
            if (root / subdir).exists():
                r = client.get(f"/api/tree?path={subdir}")
                assert r.status_code == 200
                data = r.json()
                assert isinstance(data, dict)
                assert data["name"] == subdir
                assert "children" in data

    def test_tree_excludes_git_and_node_modules(self):
        """Default ignore list excludes .git, node_modules."""
        with patch("orchestrator_ui.server.get_workspace_root") as mock_root:
            mock_root.return_value = Path(__file__).resolve().parent.parent.parent
            r = client.get("/api/tree")
            assert r.status_code == 200
            data = r.json()
            names = _collect_node_names(data)
            assert ".git" not in names
            assert "node_modules" not in names

    def test_tree_404_for_nonexistent_path(self):
        """GET /api/tree?path=nonexistent returns 404."""
        r = client.get("/api/tree?path=__nonexistent_folder_xyz_123")
        assert r.status_code == 404


class TestFileAPI:
    """Test GET /api/file and PUT /api/file (Phase 3 Code Editor)."""

    def test_get_file_returns_content_and_language(self):
        """GET /api/file?path=... returns path, content, language for existing file."""
        with patch("orchestrator_ui.server.get_workspace_root") as mock_root:
            root = Path(__file__).resolve().parent.parent.parent  # agent-automation
            mock_root.return_value = root
            test_file = root / "orchestrator_ui" / "server.py"
            if test_file.exists():
                r = client.get("/api/file?path=orchestrator_ui/server.py")
                assert r.status_code == 200
                data = r.json()
                assert "path" in data
                assert "content" in data
                assert data.get("language") == "python"
                assert "Orchestrator" in data["content"]

    def test_get_file_404_for_nonexistent(self):
        """GET /api/file?path=nonexistent returns 404."""
        with patch("orchestrator_ui.server.get_workspace_root") as mock_root:
            mock_root.return_value = Path(__file__).resolve().parent.parent.parent
            r = client.get("/api/file?path=__nonexistent_file_xyz_123.txt")
            assert r.status_code == 404
            assert "not found" in r.json().get("detail", "").lower()

    def test_get_file_400_for_path_traversal(self):
        """GET /api/file?path=../etc/passwd returns 400."""
        with patch("orchestrator_ui.server.get_workspace_root") as mock_root:
            mock_root.return_value = Path(__file__).resolve().parent.parent.parent
            r = client.get("/api/file?path=../etc/passwd")
            assert r.status_code == 400
            assert "path" in r.json().get("detail", "").lower() or "invalid" in r.json().get("detail", "").lower()

    def test_put_file_creates_file_and_parent_dirs(self):
        """PUT /api/file creates file and parent dirs."""
        with patch("orchestrator_ui.server.get_workspace_root") as mock_root:
            root = Path(__file__).resolve().parent.parent.parent
            mock_root.return_value = root
            test_path = "orchestrator_ui/tests/_phase3_test_file.txt"
            try:
                r = client.put(
                    "/api/file",
                    json={"path": test_path, "content": "hello phase 3"},
                )
                assert r.status_code == 200
                data = r.json()
                assert data.get("ok") is True
                assert "path" in data
                full_path = root / test_path
                assert full_path.exists()
                assert full_path.read_text() == "hello phase 3"
            finally:
                if (root / test_path).exists():
                    (root / test_path).unlink()

    def test_put_file_400_for_path_traversal(self):
        """PUT /api/file with path=../etc/passwd returns 400."""
        with patch("orchestrator_ui.server.get_workspace_root") as mock_root:
            mock_root.return_value = Path(__file__).resolve().parent.parent.parent
            r = client.put(
                "/api/file",
                json={"path": "../etc/passwd", "content": "x"},
            )
            assert r.status_code == 400
            assert "path" in r.json().get("detail", "").lower() or "invalid" in r.json().get("detail", "").lower()

    def test_get_file_404_for_directory(self):
        """GET /api/file?path=dir returns 404 when path is a directory."""
        with patch("orchestrator_ui.server.get_workspace_root") as mock_root:
            root = Path(__file__).resolve().parent.parent.parent
            mock_root.return_value = root
            # orchestrator_ui is a dir
            r = client.get("/api/file?path=orchestrator_ui")
            assert r.status_code == 404

    def test_put_file_overwrites_existing(self):
        """PUT /api/file overwrites existing file content."""
        with patch("orchestrator_ui.server.get_workspace_root") as mock_root:
            root = Path(__file__).resolve().parent.parent.parent
            mock_root.return_value = root
            test_path = "orchestrator_ui/tests/_phase3_overwrite.txt"
            try:
                (root / test_path).parent.mkdir(parents=True, exist_ok=True)
                (root / test_path).write_text("original")
                r = client.put(
                    "/api/file",
                    json={"path": test_path, "content": "updated content"},
                )
                assert r.status_code == 200
                assert (root / test_path).read_text() == "updated content"
            finally:
                if (root / test_path).exists():
                    (root / test_path).unlink()


class TestPhase5APIs:
    """Test GET /api/slash-commands, /api/skills, /api/rules, /api/hooks (Phase 5 Custom User Actions)."""

    def test_slash_commands_returns_list(self):
        """GET /api/slash-commands returns commands from roles.yml."""
        with patch("orchestrator_ui.server.get_workspace_root") as mock_root:
            mock_root.return_value = Path(__file__).resolve().parent.parent.parent.parent
            r = client.get("/api/slash-commands")
            assert r.status_code == 200
            data = r.json()
            assert "commands" in data
            assert isinstance(data["commands"], list)
            # If roles.yml exists, should have entries
            for cmd in data["commands"][:3]:
                assert "slash" in cmd or isinstance(cmd, str)
                if isinstance(cmd, dict):
                    assert cmd.get("slash", "").startswith("/")

    def test_slash_commands_each_has_slash_field(self):
        """Regression: every command has slash field for display."""
        with patch("orchestrator_ui.server.get_workspace_root") as mock_root:
            mock_root.return_value = Path(__file__).resolve().parent.parent.parent.parent
            r = client.get("/api/slash-commands")
            assert r.status_code == 200
            data = r.json()
            commands = data.get("commands", [])
            for cmd in commands:
                assert isinstance(cmd, dict), f"Command must be dict: {cmd}"
                assert "slash" in cmd, f"Command missing 'slash' field: {cmd}"
                assert isinstance(cmd["slash"], str), f"slash must be string: {cmd}"
                assert cmd["slash"].startswith("/"), f"slash must start with /: {cmd}"

    def test_slash_commands_format_for_display(self):
        """Regression: cmd.slash format used correctly for display (as in index.html)."""
        with patch("orchestrator_ui.server.get_workspace_root") as mock_root:
            mock_root.return_value = Path(__file__).resolve().parent.parent.parent.parent
            r = client.get("/api/slash-commands")
            assert r.status_code == 200
            data = r.json()
            commands = data.get("commands", [])
            for cmd in commands:
                # Mimic index.html: const slash = (cmd && typeof cmd.slash === 'string') ? cmd.slash : String(cmd)
                slash = cmd.get("slash") if isinstance(cmd.get("slash"), str) else str(cmd)
                assert slash.startswith("/"), f"Display slash must start with /: {slash}"
                assert len(slash) > 1, "Display slash must be more than just '/'"

    def test_skills_returns_list(self):
        """GET /api/skills returns skills from .cursor/skills/."""
        with patch("orchestrator_ui.server.get_workspace_root") as mock_root:
            mock_root.return_value = Path(__file__).resolve().parent.parent.parent.parent
            r = client.get("/api/skills")
            assert r.status_code == 200
            data = r.json()
            assert "skills" in data
            assert isinstance(data["skills"], list)
            for skill in data["skills"][:3]:
                assert "name" in skill
                assert "path" in skill

    def test_rules_returns_list(self):
        """GET /api/rules returns rules from .cursor/rules/."""
        with patch("orchestrator_ui.server.get_workspace_root") as mock_root:
            mock_root.return_value = Path(__file__).resolve().parent.parent.parent.parent
            r = client.get("/api/rules")
            assert r.status_code == 200
            data = r.json()
            assert "rules" in data
            assert isinstance(data["rules"], list)
            for rule in data["rules"][:3]:
                assert "name" in rule
                assert "path" in rule

    def test_hooks_returns_config_and_lifecycle(self):
        """GET /api/hooks returns hooks config and lifecycle definitions."""
        with patch("orchestrator_ui.server.get_workspace_root") as mock_root:
            mock_root.return_value = Path(__file__).resolve().parent.parent.parent.parent
            r = client.get("/api/hooks")
            assert r.status_code == 200
            data = r.json()
            assert "hooks" in data
            assert "lifecycle" in data
            assert isinstance(data["hooks"], dict)
            assert isinstance(data["lifecycle"], list)
            lifecycle_names = [h["name"] for h in data["lifecycle"]]
            assert "before_cycle" in lifecycle_names
            assert "after_cycle" in lifecycle_names
            assert "before_delegate" in lifecycle_names
            assert "after_delegate" in lifecycle_names

    def test_hooks_with_missing_cursor_dir(self):
        """GET /api/hooks returns empty hooks when .cursor/hooks.json missing."""
        with patch("orchestrator_ui.server.get_workspace_root") as mock_root:
            mock_root.return_value = Path("/tmp/nonexistent_workspace_xyz")
            r = client.get("/api/hooks")
            assert r.status_code == 200
            data = r.json()
            assert data["hooks"] == {}
            assert len(data["lifecycle"]) >= 4


class TestMCPFallback:
    """Verify _orchestration_handler falls back to stub context when MCP unavailable."""

    @pytest.fixture(autouse=True)
    def ensure_api_key(self):
        os.environ["ORCHESTRATOR_LLM_PROVIDER"] = "local"
        os.environ["OPENAI_API_KEY"] = "sk-test-fake-key"
        yield

    def test_orchestration_handler_falls_back_to_stub_when_mcp_fails(self):
        """When MCP raises (e.g. mcp-server not running), brain still runs with stub context."""
        with patch("orchestrator_client.mcp_client.create_mcp_session") as mock_session:
            mock_session.side_effect = RuntimeError("MCP server not running")
            with patch("orchestrator_ui.server.run_brain_with_flow") as mock_brain:
                mock_brain.return_value = {
                    "proposal": "p",
                    "critique": "c",
                    "synthesis": "s",
                    "final_decision": "Stub-based reply",
                }
                r = _chat_request(
                    [{"role": "user", "content": "run one cycle"}],
                    mode="orchestration",
                )
                assert r.status_code == 200
                data = r.json()
                assert data["mode_used"] == "orchestration"
                assert data["reply"] == "Stub-based reply"
                mock_brain.assert_called_once()
                # Context should have stub values (workspace_snippet contains "Stub context" when MCP fails)
                call_args = mock_brain.call_args
                context = call_args[0][1]
                assert "workspace_snippet" in context
                snippet = context.get("workspace_snippet", "")
                assert "Stub" in snippet or "stub" in snippet.lower()

    def test_orchestration_handler_stream_falls_back_when_mcp_fails(self):
        """When MCP fails in stream handler, brain stream still runs with stub context."""
        with patch("orchestrator_client.mcp_client.create_mcp_session") as mock_session:
            mock_session.side_effect = FileNotFoundError("MCP server not found")
            with patch("orchestrator_ui.server.run_brain_with_flow_stream") as mock_stream:
                async def fake_stream(*args, **kwargs):
                    yield ("flow.proposal", "p")
                    yield ("flow.critique", "c")
                    yield ("flow.synthesis", "")
                    yield ("reply.chunk", "ok")
                    yield ("reply.done", "")

                mock_stream.return_value = fake_stream()
                payload = {
                    "messages": [{"role": "user", "content": "run one cycle"}],
                    "mode": "orchestration",
                }
                with client.stream(
                    "POST",
                    "/api/chat",
                    json=payload,
                    headers={"Accept": "text/event-stream"},
                ) as response:
                    assert response.status_code == 200
                    lines = list(response.iter_lines())
                data_lines = [l for l in lines if l.startswith("data: ")]
                assert len(data_lines) >= 4
                events = [json.loads(l[6:]) for l in data_lines]
                types = [e.get("type") for e in events]
                assert "flow.proposal" in types
                assert "reply.done" in types


def _parse_sse_stream_reply_chunks(sse_text: str) -> list[str]:
    """
    Python equivalent of processSSEStream reply.chunk parsing (index.html).
    Mirrors the JS: EVENT_BOUNDARY = /\\r?\\n\\r?\\n/, processOneEvent per event,
    extract data line, parse JSON, append content for reply.chunk.
    Returns list of chunk contents in order.
    """
    chunks = []
    boundary = re.compile(r"\r?\n\r?\n")
    buffer = sse_text

    def process_one_event(event_str: str) -> None:
        for line in event_str.split("\n"):
            if line.startswith("data: "):
                json_str = line[6:]
                if json_str.strip() in ("[DONE]", ""):
                    return
                try:
                    data = json.loads(json_str)
                    if data.get("type") == "reply.chunk":
                        content = data.get("content")
                        if content is not None:
                            chunks.append(str(content))
                except json.JSONDecodeError:
                    pass
                return

    while True:
        match = boundary.search(buffer)
        if match is None:
            break
        sep = match.group(0)
        idx = buffer.index(sep)
        event_str = buffer[:idx]
        buffer = buffer[idx + len(sep) :]
        process_one_event(event_str)

    if buffer.strip():
        process_one_event(buffer)

    return chunks


class TestSSENoDoubleProcess:
    """Regression: processSSEStream (or equivalent) does not double-process reply.chunk events."""

    def test_reply_chunks_appear_exactly_once(self):
        """Mock SSE with multiple chunks; assert each chunk appears exactly once in output."""
        sse = (
            'data: {"type": "reply.chunk", "content": "A"}\n\n'
            'data: {"type": "reply.chunk", "content": "B"}\n\n'
            'data: {"type": "reply.chunk", "content": "C"}\n\n'
            'data: {"type": "reply.done"}\n\n'
        )
        chunks = _parse_sse_stream_reply_chunks(sse)
        assert chunks == ["A", "B", "C"]
        output = "".join(chunks)
        assert output == "ABC"
        assert output.count("A") == 1
        assert output.count("B") == 1
        assert output.count("C") == 1

    def test_mixed_events_only_chunks_collected(self):
        """Flow events and reply.done do not affect chunk collection; no duplication."""
        sse = (
            'data: {"type": "flow.proposal", "content": "Proposal"}\n\n'
            'data: {"type": "reply.chunk", "content": "X"}\n\n'
            'data: {"type": "flow.critique", "content": "Critique"}\n\n'
            'data: {"type": "reply.chunk", "content": "Y"}\n\n'
            'data: {"type": "reply.done"}\n\n'
        )
        chunks = _parse_sse_stream_reply_chunks(sse)
        assert chunks == ["X", "Y"]
        assert "".join(chunks) == "XY"

    def test_empty_and_single_chunk(self):
        """Edge cases: no chunks, single chunk."""
        sse_done = 'data: {"type": "reply.done"}\n\n'
        assert _parse_sse_stream_reply_chunks(sse_done) == []

        sse_single = 'data: {"type": "reply.chunk", "content": "only"}\n\n'
        assert _parse_sse_stream_reply_chunks(sse_single) == ["only"]


class TestLocalOnlyStartupGuard:
    """Verify server.py exits immediately when a non-local provider is configured.

    server.py uses load_dotenv(..., override=True) which overwrites process env vars with
    the .env file value.  To make the startup guard see a non-local provider we temporarily
    write the .env file, run the subprocess, then restore the original content.
    """

    _UI_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
    _PYTHONPATH = str(Path(__file__).resolve().parent.parent.parent)

    def _run_server_import_with_provider(self, provider: str):
        """Write .env with given provider, import server in subprocess, restore .env."""
        import subprocess

        env_file = self._UI_ENV_FILE
        original = env_file.read_text(encoding="utf-8") if env_file.exists() else None
        env_file.write_text(f"ORCHESTRATOR_LLM_PROVIDER={provider}\n", encoding="utf-8")
        try:
            # Remove provider from shell env so load_dotenv (override=True) drives the value
            proc_env = {k: v for k, v in os.environ.items() if k != "ORCHESTRATOR_LLM_PROVIDER"}
            proc_env["PYTHONPATH"] = self._PYTHONPATH
            return subprocess.run(
                [sys.executable, "-c", "import orchestrator_ui.server"],
                capture_output=True, text=True, env=proc_env,
            )
        finally:
            if original is not None:
                env_file.write_text(original, encoding="utf-8")
            elif env_file.exists():
                env_file.unlink()

    def test_startup_exits_if_provider_is_anthropic(self):
        """server.py exits with SystemExit if ORCHESTRATOR_LLM_PROVIDER=anthropic."""
        result = self._run_server_import_with_provider("anthropic")
        assert result.returncode != 0
        assert "local-only" in result.stderr

    def test_startup_exits_if_provider_is_openai(self):
        """server.py exits with SystemExit if ORCHESTRATOR_LLM_PROVIDER=openai."""
        result = self._run_server_import_with_provider("openai")
        assert result.returncode != 0
        assert "local-only" in result.stderr
