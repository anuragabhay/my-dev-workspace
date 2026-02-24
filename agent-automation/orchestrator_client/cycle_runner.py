"""
Run one orchestrator cycle: load context, call MCP tools, run brain (propose → critique → synthesize), output decision.
"""

import sys
from pathlib import Path

# Add agent-automation to path
_client_dir = Path(__file__).resolve().parent
_agent_automation = _client_dir.parent
if str(_agent_automation) not in sys.path:
    sys.path.insert(0, str(_agent_automation))

from orchestrator_client.brain import run_brain
from orchestrator_client.context_loader import load_context
from orchestrator_client.mcp_client import create_mcp_session, run_orchestrator_tools


def _get_project_workspace_snippet(workspace_root: Path, max_chars: int = 8000) -> str:
    """Read a snippet of PROJECT_WORKSPACE.md for context."""
    path = workspace_root / "PROJECT_WORKSPACE.md"
    if not path.exists():
        return "(PROJECT_WORKSPACE.md not found)"
    text = path.read_text(encoding="utf-8")
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[... truncated ...]"


async def run_one_cycle() -> str:
    """
    Run one full orchestrator cycle:
    1. Load context (orchestrator_rule, patterns, workflow, decisions, roles)
    2. Connect to MCP server, call get_pending_orchestrator_prompt, get_workspace_status, get_workflow_config
    3. Run brain: propose → critique → synthesize (A2A-style handoffs)
    4. Return the orchestrator decision
    """
    from workspace_config import get_workspace_root

    root = get_workspace_root()
    context = load_context()
    workspace_snippet = _get_project_workspace_snippet(root)

    async with create_mcp_session() as (session, call_tool):
        tool_results = await run_orchestrator_tools(call_tool, workspace_root=str(root))

    brain_context = {
        "pending_prompt": tool_results["pending_prompt"],
        "workspace_status": tool_results["workspace_status"],
        "workflow_config": tool_results["workflow_config"],
        "workspace_snippet": workspace_snippet,
    }

    decision = run_brain(context.system_message, brain_context)
    return decision.strip()


def main() -> int:
    """Entry point: run one cycle and print the decision."""
    import asyncio

    try:
        decision = asyncio.run(run_one_cycle())
        print(decision)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
