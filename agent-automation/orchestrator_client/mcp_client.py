"""
MCP client for orchestrator - connects to agent-automation MCP server over stdio.
"""

import json
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Add agent-automation to path for config
_client_dir = Path(__file__).resolve().parent
_agent_automation = _client_dir.parent
if str(_agent_automation) not in sys.path:
    sys.path.insert(0, str(_agent_automation))

from orchestrator_client.config import get_mcp_server_env, get_mcp_server_path


def _extract_text_from_result(result: Any) -> str:
    """Extract text from MCP CallToolResult."""
    if not result or not hasattr(result, "content"):
        return ""
    content = result.content
    if not content:
        return ""
    parts = []
    for block in content:
        if hasattr(block, "text"):
            parts.append(block.text)
    return "\n".join(parts)


@asynccontextmanager
async def create_mcp_session():
    """
    Create an MCP client session connected to the agent-automation server.
    Yields (session, call_tool_helper).
    """
    server_path = get_mcp_server_path()
    if not server_path.exists():
        raise FileNotFoundError(f"MCP server not found: {server_path}")

    env = get_mcp_server_env()
    # Merge with current env
    import os
    full_env = {**os.environ, **env}


    from workspace_config import get_workspace_root
    workspace_root = get_workspace_root()

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(server_path)],
        env=full_env,
        cwd=str(workspace_root),
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            async def call_tool(name: str, arguments: Optional[dict[str, Any]] = None) -> dict[str, Any]:
                """Call MCP tool and return parsed JSON."""
                result = await session.call_tool(name, arguments or {})
                text = _extract_text_from_result(result)
                if result.isError:
                    return {"error": text or "Tool call failed", "is_error": True}
                try:
                    return json.loads(text) if text else {}
                except json.JSONDecodeError:
                    return {"raw": text}

            yield session, call_tool


async def run_orchestrator_tools(call_tool, workspace_root: Optional[str] = None) -> dict[str, Any]:
    """
    Run the required MCP tools for one orchestrator cycle.
    Returns: {pending_prompt, workspace_status, workflow_config, ...}
    """
    pending = await call_tool("get_pending_orchestrator_prompt")
    workspace_status = await call_tool("get_workspace_status")
    workflow_config = await call_tool(
        "get_workflow_config",
        {"workspace_root": workspace_root} if workspace_root else {},
    )

    # Optionally check pending tasks for role from Next Actions if we had it
    # For simplicity, we include workflow_config which has role list
    return {
        "pending_prompt": pending,
        "workspace_status": workspace_status,
        "workflow_config": workflow_config,
    }
