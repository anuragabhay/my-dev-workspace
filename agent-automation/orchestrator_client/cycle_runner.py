"""
Run one orchestrator cycle: load context, call MCP tools, call LLM, output decision.
"""

import json
import os
import sys
from pathlib import Path

# Add agent-automation to path
_client_dir = Path(__file__).resolve().parent
_agent_automation = _client_dir.parent
if str(_agent_automation) not in sys.path:
    sys.path.insert(0, str(_agent_automation))

from orchestrator_client.config import get_anthropic_api_key, get_llm_model
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


def _call_anthropic(system: str, user: str) -> str:
    """Call Anthropic API (Claude) with system and user messages."""
    api_key = get_anthropic_api_key()
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY or ORCHESTRATOR_LLM_API_KEY not set. "
            "Set one of these env vars to run the orchestrator client."
        )

    from anthropic import Anthropic

    client = Anthropic(api_key=api_key)
    model = get_llm_model()

    response = client.messages.create(
        model=model,
        max_tokens=2048,
        system=system,
        messages=[{"role": "user", "content": user}],
    )

    if not response.content:
        return ""
    parts = []
    for block in response.content:
        if hasattr(block, "text"):
            parts.append(block.text)
    return "\n".join(parts)


async def run_one_cycle() -> str:
    """
    Run one full orchestrator cycle:
    1. Load context (orchestrator_rule, patterns, workflow, decisions, roles)
    2. Connect to MCP server, call get_pending_orchestrator_prompt, get_workspace_status, get_workflow_config
    3. Build system + user messages
    4. Call LLM once
    5. Return the orchestrator decision
    """
    from workspace_config import get_workspace_root

    root = get_workspace_root()
    context = load_context()
    workspace_snippet = _get_project_workspace_snippet(root)

    async with create_mcp_session() as (session, call_tool):
        tool_results = await run_orchestrator_tools(call_tool, workspace_root=str(root))

    user_content = f"""Run one orchestrator cycle.

## MCP Tool Results

### get_pending_orchestrator_prompt
```json
{json.dumps(tool_results["pending_prompt"], indent=2)}
```

### get_workspace_status
```json
{json.dumps(tool_results["workspace_status"], indent=2)}
```

### get_workflow_config
```json
{json.dumps(tool_results["workflow_config"], indent=2)}
```

## PROJECT_WORKSPACE.md (snippet)
```
{workspace_snippet}
```

---

Apply the workflow and decision rules from the system context. Decide the single next action. Output exactly one of:
1. A delegation: `/role task` (e.g. `/lead-engineer Add unit tests for health.py`)
2. User Intervention Required: [reason]
3. ORCHESTRATION_COMPLETE: [brief summary]
4. Run one cycle: get_workspace_status, read PROJECT_WORKSPACE.md, decide next step, delegate if needed.

Your decision:"""

    reply = _call_anthropic(context.system_message, user_content)
    return reply.strip()


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
