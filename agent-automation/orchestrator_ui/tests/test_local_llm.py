"""
Tests for Phase A: local Ollama provider in llm_provider.py and server.py 503 handling.
"""
import os
import sys
import json
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock

import pytest

# ensure agent-automation is in path
_aa = Path(__file__).resolve().parent.parent.parent
if str(_aa) not in sys.path:
    sys.path.insert(0, str(_aa))

from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def local_env(monkeypatch):
    """Set ORCHESTRATOR_LLM_PROVIDER=local for all tests in this module."""
    monkeypatch.setenv("ORCHESTRATOR_LLM_PROVIDER", "local")
    monkeypatch.setenv("ORCHESTRATOR_LLM_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setenv("ORCHESTRATOR_LLM_MODEL", "mistral-nemo")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")


@pytest.fixture
def client(local_env):
    from orchestrator_ui.server import app
    return TestClient(app)


class TestLocalProviderChatSync:
    """chat_sync with provider=local routes to _call_openai_sync with correct base_url."""

    def test_chat_sync_calls_openai_sync_with_local_base_url(self, local_env):
        with patch("orchestrator_client.llm_provider._call_openai_sync", return_value="hello from local") as mock_sync:
            from orchestrator_client.llm_provider import chat_sync
            result = chat_sync(
                system="sys",
                user="hi",
                model="mistral-nemo",
                anthropic_key=None,
                openai_key=None,
                provider="local",
            )
        assert result == "hello from local"
        mock_sync.assert_called_once()
        call_kwargs = mock_sync.call_args
        # base_url should contain localhost:11434
        base_url_arg = call_kwargs.kwargs.get("base_url") or (call_kwargs.args[4] if len(call_kwargs.args) > 4 else None)
        assert base_url_arg is not None
        assert "localhost:11434" in base_url_arg

    def test_chat_sync_uses_ollama_dummy_key_when_no_key_provided(self, local_env):
        with patch("orchestrator_client.llm_provider._call_openai_sync", return_value="ok") as mock_sync:
            from orchestrator_client.llm_provider import chat_sync
            chat_sync(system="s", user="u", model="mistral-nemo",
                      anthropic_key=None, openai_key=None, provider="local")
        call_kwargs = mock_sync.call_args
        # api_key should be "ollama" (dummy)
        api_key_arg = call_kwargs.args[3] if len(call_kwargs.args) > 3 else call_kwargs.kwargs.get("api_key")
        assert api_key_arg == "ollama"


class TestLocalProviderChatStream:
    """chat_stream with provider=local routes to _call_openai_stream with correct base_url."""

    def test_chat_stream_calls_openai_stream_with_local_base_url(self, local_env):
        async def _fake_stream(*args, **kwargs):
            yield "chunk1"
            yield "chunk2"

        with patch("orchestrator_client.llm_provider._call_openai_stream", side_effect=_fake_stream) as mock_stream:
            from orchestrator_client.llm_provider import chat_stream
            import asyncio

            async def collect():
                chunks = []
                async for c in chat_stream(
                    system="sys",
                    messages=[{"role": "user", "content": "hi"}],
                    model="mistral-nemo",
                    anthropic_key=None,
                    openai_key=None,
                    provider="local",
                ):
                    chunks.append(c)
                return chunks

            chunks = asyncio.get_event_loop().run_until_complete(collect())

        assert chunks == ["chunk1", "chunk2"]
        mock_stream.assert_called_once()
        base_url_arg = mock_stream.call_args.kwargs.get("base_url")
        assert base_url_arg is not None
        assert "localhost:11434" in base_url_arg


class TestOllamaUnreachable:
    """When Ollama is unreachable, /api/chat returns 503."""

    def test_503_when_ollama_unreachable(self, client):
        try:
            import openai
            conn_error = openai.APIConnectionError(request=MagicMock())
        except Exception:
            import httpx
            conn_error = httpx.ConnectError("Connection refused")

        with patch("orchestrator_ui.server._chat_handler", side_effect=conn_error), \
             patch("orchestrator_ui.server._orchestration_handler", side_effect=conn_error):
            resp = client.post(
                "/api/chat",
                json={"messages": [{"role": "user", "content": "hello"}], "mode": "chat"},
            )
        assert resp.status_code == 503
        assert "Local LLM unavailable" in resp.json().get("detail", "") or \
               "Local LLM unavailable" in resp.json().get("error", "")


class TestStartupGuardStillPasses:
    """Startup guard still exits for non-local providers after Phase A changes."""

    def test_startup_exits_if_provider_is_anthropic(self):
        import subprocess
        result = subprocess.run(
            [sys.executable, "-c", "import orchestrator_ui.server"],
            capture_output=True, text=True,
            env={**os.environ,
                 "ORCHESTRATOR_LLM_PROVIDER": "anthropic",
                 "PYTHONPATH": str(_aa)},
        )
        assert result.returncode != 0
        assert "local-only" in result.stderr


class TestModelResolution:
    """Model resolution for provider=local."""

    def test_empty_model_resolves_to_mistral_nemo(self, local_env):
        with patch.dict(os.environ, {"ORCHESTRATOR_LLM_MODEL": "mistral-nemo"}):
            with patch("orchestrator_client.llm_provider._call_openai_sync", return_value="ok") as mock:
                from orchestrator_client.llm_provider import chat_sync
                chat_sync(system="s", user="u", model="",
                          anthropic_key=None, openai_key=None, provider="local")
            # model passed to _call_openai_sync should be "mistral-nemo" (not empty)
            model_arg = mock.call_args.args[2] if len(mock.call_args.args) > 2 else None
            assert model_arg == "mistral-nemo"

    def test_local_model_string_resolves_to_env_model(self, local_env):
        with patch.dict(os.environ, {"ORCHESTRATOR_LLM_MODEL": "phi4-mini"}):
            with patch("orchestrator_client.llm_provider._call_openai_sync", return_value="ok") as mock:
                from orchestrator_client.llm_provider import chat_sync
                chat_sync(system="s", user="u", model="local",
                          anthropic_key=None, openai_key=None, provider="local")
            model_arg = mock.call_args.args[2] if len(mock.call_args.args) > 2 else None
            assert model_arg == "phi4-mini"

    def test_explicit_model_is_passed_through(self, local_env):
        with patch("orchestrator_client.llm_provider._call_openai_sync", return_value="ok") as mock:
            from orchestrator_client.llm_provider import chat_sync
            chat_sync(system="s", user="u", model="phi4-mini",
                      anthropic_key=None, openai_key=None, provider="local")
        model_arg = mock.call_args.args[2] if len(mock.call_args.args) > 2 else None
        assert model_arg == "phi4-mini"

    def test_claude_model_maps_to_orchestrator_llm_model_not_gpt4o_mini(self, local_env):
        """When provider=local and model=claude-*, mock receives ORCHESTRATOR_LLM_MODEL (mistral-nemo), NOT gpt-4o-mini."""
        with patch.dict(os.environ, {"ORCHESTRATOR_LLM_MODEL": "mistral-nemo"}):
            with patch("orchestrator_client.llm_provider._call_openai_sync", return_value="ok") as mock:
                from orchestrator_client.llm_provider import chat_sync
                chat_sync(system="s", user="u", model="claude-sonnet-4-20250514",
                          anthropic_key=None, openai_key=None, provider="local",
                          openai_fallback_model="gpt-4o-mini")
            model_arg = mock.call_args.args[2] if len(mock.call_args.args) > 2 else None
            assert model_arg == "mistral-nemo", "claude-* must map to ORCHESTRATOR_LLM_MODEL, not gpt-4o-mini"
