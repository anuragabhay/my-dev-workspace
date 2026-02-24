"""
Orchestrator client configuration.
Resolves workspace root via workspace_config; LLM and MCP via env.
"""

import os
from pathlib import Path
from typing import Optional

# Add agent-automation to path for workspace_config
_client_dir = Path(__file__).resolve().parent
_agent_automation = _client_dir.parent
if str(_agent_automation) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(_agent_automation))

from workspace_config import get_workspace_root


def get_mcp_server_path() -> Path:
    """Path to the MCP server script."""
    root = get_workspace_root()
    return root / "agent-automation" / "mcp-server" / "server.py"


def get_mcp_server_env() -> dict[str, str]:
    """Environment for MCP server subprocess (PYTHONPATH, WORKSPACE_ROOT)."""
    root = get_workspace_root()
    agent_automation = root / "agent-automation"
    return {
        "PYTHONPATH": str(agent_automation),
        "WORKSPACE_ROOT": str(root),
    }


def get_llm_provider() -> str:
    """LLM provider: anthropic or vertex (vertex not yet implemented)."""
    return os.environ.get("ORCHESTRATOR_LLM_PROVIDER", "anthropic").lower()


def get_llm_model() -> str:
    """LLM model name."""
    return os.environ.get(
        "ORCHESTRATOR_LLM_MODEL",
        "claude-sonnet-4-20250514",
    )


def get_anthropic_api_key() -> Optional[str]:
    """Anthropic API key from env."""
    return os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ORCHESTRATOR_LLM_API_KEY")
