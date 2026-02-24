# Orchestrator Client

A **platform-agnostic** orchestrator client that performs one full "orchestrator cycle" using the same rules, workflow, and tools as in Cursor—but **without Cursor**, the stop hook, or any Cursor-specific config. Run orchestration locally, in Claude Code, Vertex, or your own app.

## Why Platform-Agnostic?

Today the orchestrator runs inside Cursor (`.cursor/rules`, stop hook, MCP started by Cursor). That ties orchestration to one product. With this client, orchestration is **decoupled**:

- The client only needs: **Python**, our MCP server (stdio), the same curated context (orchestrator_rule, workflow, decisions, roles), and an **LLM API**.
- The same behaviour runs locally, in Claude Code, Vertex, or your own app.
- **No Cursor dependency** — true platform-agnostic orchestration.

## Agent-to-Agent (A2A) Protocol

Agents must be able to communicate with each other (orchestrator delegating to Lead Engineer / Junior Engineers, subagents reporting back or requesting input from other agents) in a **standard, host-independent way**. Claude Code and other environments support agent-to-agent patterns; this client implements the same capability so that when you run the orchestrator on any host, subagents can still be invoked, receive tasks, and respond.

### A2A Message Format

The `a2a.py` module defines a structured **Agent-to-Agent protocol**:

- **Agent identity**: Each participant (orchestrator, lead-engineer, junior-engineer-1, junior-engineer-2, architect, etc.) has a stable identity in messages (`AgentRole`).
- **Request/response**: Structured format for "task for agent X" (`TASK_REQUEST`) and "response from agent X" (`TASK_RESPONSE`).
- **Task handoff**: `task_id`, `payload`, `status` (pending, in_progress, completed, failed).
- **Optional async**: `created_at`, `correlation_id` for request/response pairing.

### Message Types

| Type | Direction | Use |
|------|-----------|-----|
| `TASK_REQUEST` | Orchestrator → subagent | "Do this task" |
| `TASK_RESPONSE` | Subagent → orchestrator | "Done / result" |
| `TASK_HANDOFF` | Subagent → subagent | Hand off work |
| `QUERY` / `QUERY_RESPONSE` | Agent ↔ agent | Request info |

### Enabling Platform-Agnostic Agent Coordination

This A2A layer is **required** for agents to talk among themselves when running outside Cursor. The current implementation provides:

1. **In-process message format** — a minimal spec + implementation that the client can use to represent delegations and responses.
2. **Serialization** — `A2AMessage.to_dict()` / `from_dict()` for JSON/HTTP transport.
3. **Helpers** — `create_task_request()`, `create_task_response()` for common patterns.

A future follow-up can replace the in-process format with HTTP/JSON-RPC/SSE for multi-host, multi-agent setups. The design is compatible with such extensions.

---

## Installation

```bash
cd agent-automation/orchestrator_client
pip install -r requirements.txt
```

Dependencies:

- `mcp` — same as mcp-server (MCP Python SDK client)
- `anthropic` — Claude API
- `python-dotenv` — optional, for `.env` loading

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WORKSPACE_ROOT` | Workspace root (parent of agent-automation) | Derived from agent-automation parent |
| `ANTHROPIC_API_KEY` | Claude API key | Required for LLM |
| `ORCHESTRATOR_LLM_API_KEY` | Alternative API key env | Same as above |
| `ORCHESTRATOR_LLM_PROVIDER` | LLM provider | `anthropic` |
| `ORCHESTRATOR_LLM_MODEL` | Model name | `claude-sonnet-4-20250514` |

### Required Context Files

**workflow.yml, decisions.yml, roles.yml, and the orchestrator rule/patterns are required** for correct, platform-agnostic behaviour. They must not be omitted. The client loads:

- `agent-automation/orchestrator_rule.md`
- `agent-automation/orchestrator_patterns.md`
- `agent-automation/workflow.yml`
- `agent-automation/decisions.yml`
- `agent-automation/roles.yml`

All paths are resolved via `workspace_config.get_workspace_root()` so the client works from any cwd.

## Running One Cycle

From the workspace root:

```bash
# Set API key
export ANTHROPIC_API_KEY=your-key

# Optional: set workspace root if not using default
export WORKSPACE_ROOT=/path/to/your-workspace

# Run one cycle (PYTHONPATH must include agent-automation)
PYTHONPATH=./agent-automation python -m orchestrator_client.main
```

Or from `agent-automation`:

```bash
cd agent-automation
PYTHONPATH=. python -m orchestrator_client.main
```

The client will:

1. Connect to the MCP server at `agent-automation/mcp-server/server.py` over stdio
2. Call `get_pending_orchestrator_prompt`, `get_workspace_status`, `get_workflow_config`
3. Load all orchestrator context files
4. Build system + user messages with tool results and PROJECT_WORKSPACE.md snippet
5. Call the LLM once (Claude)
6. Print the orchestrator decision (delegation, User Intervention Required, ORCHESTRATION_COMPLETE, or "Run one cycle")

## Out of Scope (This Task)

- Running subagents end-to-end
- Writing to PROJECT_WORKSPACE.md
- Multi-cycle loop (can be a follow-up)

Focus: **one cycle** — connect → load context → call tools → call LLM → output decision; plus A2A design/implementation and documentation.

## MCP Server Requirements

The MCP server must be runnable with:

- `PYTHONPATH` including `agent-automation` (for workspace_config, parser, tools)
- `WORKSPACE_ROOT` set to the workspace root

The client spawns the server as a subprocess with these env vars set automatically.
