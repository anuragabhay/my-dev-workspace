#!/usr/bin/env python3
"""
Quick test: load context, connect to MCP, call tools. No LLM call.
Run: PYTHONPATH=./agent-automation python -m orchestrator_client.test_connection
"""

import asyncio
import json
import sys
from pathlib import Path

_client_dir = Path(__file__).resolve().parent
_agent_automation = _client_dir.parent
if str(_agent_automation) not in sys.path:
    sys.path.insert(0, str(_agent_automation))

from orchestrator_client.context_loader import load_context
from orchestrator_client.mcp_client import create_mcp_session, run_orchestrator_tools
from workspace_config import get_workspace_root


async def main():
    print("Loading context...")
    ctx = load_context()
    print(f"  orchestrator_rule: {len(ctx.orchestrator_rule)} chars")
    print(f"  workflow: {len(ctx.workflow)} chars")

    root = get_workspace_root()
    print(f"\nWorkspace root: {root}")

    print("\nConnecting to MCP server...")
    async with create_mcp_session() as (session, call_tool):
        results = await run_orchestrator_tools(call_tool, workspace_root=str(root))
        print("  OK")

    print("\nTool results:")
    print("  pending_prompt:", json.dumps(results["pending_prompt"], indent=2)[:200], "...")
    print("  workspace_status keys:", list(results["workspace_status"].keys()))
    print("  workflow_config keys:", list(results["workflow_config"].keys()))
    print("\nConnection test passed.")


if __name__ == "__main__":
    asyncio.run(main())
