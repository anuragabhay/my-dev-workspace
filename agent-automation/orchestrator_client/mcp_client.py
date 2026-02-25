"""
MCP client for orchestrator: spawn mcp-server subprocess via stdio, call tools.
Provides create_mcp_session() and run_orchestrator_tools() for brain context.
"""

import json
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncIterator

# Add agent-automation to path
_client_dir = Path(__file__).resolve().parent
_agent_automation = _client_dir.parent
if str(_agent_automation) not in sys.path:
    sys.path.insert(0, str(_agent_automation))

from orchestrator_client.config import get_mcp_server_env, get_mcp_server_path


def _parse_tool_result(result: Any) -> Any:
    """Parse MCP CallToolResult content to Python dict/list."""
    if result is None:
        return {}
    if hasattr(result, "content") and result.content:
        for block in result.content:
            if hasattr(block, "text"):
                try:
                    return json.loads(block.text)
                except json.JSONDecodeError:
                    return {"raw": block.text}
    return {}


@asynccontextmanager
async def create_mcp_session() -> AsyncIterator[tuple[Any, Any]]:
    """
    Spawn mcp-server subprocess via stdio; return async context manager yielding
    (session, call_tool).

    call_tool(name: str, arguments: dict | None) -> awaitable returning tool result.

    Uses MCP Python SDK (mcp package) to connect to stdio server.
    """
    try:
        from mcp import ClientSession
        from mcp.client.stdio import StdioServerParameters, stdio_client
    except ImportError as e:
        raise RuntimeError(
            "MCP SDK not installed. Run: pip install mcp"
        ) from e

    server_path = get_mcp_server_path()
    if not server_path.exists():
        raise FileNotFoundError(f"MCP server not found: {server_path}")

    mcp_env = get_mcp_server_env()
    env = dict(mcp_env)
    # Inherit minimal env for subprocess
    for key in ("PATH", "HOME", "USER", "LANG"):
        if key in os.environ and key not in env:
            env[key] = os.environ[key]

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(server_path)],
        env=env,
        cwd=str(server_path.parent),
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            async def call_tool(name: str, arguments: dict[str, Any] | None = None) -> Any:
                result = await session.call_tool(name, arguments or {})
                return result

            yield (session, call_tool)


async def run_orchestrator_tools(
    call_tool: Any,
    workspace_root: str,
) -> dict[str, Any]:
    """
    Call get_pending_orchestrator_prompt, get_workspace_status, get_workflow_config.
    Return dict: { "pending_prompt", "workspace_status", "workflow_config" } for brain context.
    """
    pending_prompt = {}
    workspace_status = {}
    workflow_config = {}

    try:
        result = await call_tool("get_pending_orchestrator_prompt", {})
        pending_prompt = _parse_tool_result(result)
    except Exception:
        pass

    try:
        result = await call_tool("get_workspace_status", {})
        workspace_status = _parse_tool_result(result)
    except Exception:
        pass

    try:
        result = await call_tool("get_workflow_config", {"workspace_root": workspace_root})
        workflow_config = _parse_tool_result(result)
    except Exception:
        pass

    return {
        "pending_prompt": pending_prompt,
        "workspace_status": workspace_status,
        "workflow_config": workflow_config,
    }
