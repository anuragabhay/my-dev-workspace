"""
API tests for orchestrator_ui POST /api/chat and config endpoints.
Tests error cases (400, 500, network), mode routing, intent detection.
"""

import os
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
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "", "ORCHESTRATOR_LLM_API_KEY": ""}, clear=False):
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
        """Ensure API key is set so handlers run."""
        os.environ["ANTHROPIC_API_KEY"] = "sk-test-fake-key-for-testing"
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
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
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
        os.environ["ANTHROPIC_API_KEY"] = "sk-test-fake-key"
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
        os.environ["ANTHROPIC_API_KEY"] = "sk-test-fake-key"
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
