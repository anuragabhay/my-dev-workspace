# Platform-Agnostic Agent Automation

Run orchestration and agent-automation on any host: **Cursor**, **Claude Code**, **Vertex AI**, **Augment**. No hardcoded paths.

## Checklist

- [ ] **WORKSPACE_ROOT**: Set `WORKSPACE_ROOT` env var or `agent-automation/workspace_config.yaml` with `workspace_root`
- [ ] **MCP running**: Start MCP server with `PYTHONPATH=agent-automation` (see `agent-automation/mcp-server/README.md`)
- [ ] **Orchestrator rule**: Use orchestrator instructions from `agent-automation/orchestrator_patterns.md` and `workflow.yml`
- [ ] **Agents**: Use `agent-automation/agents/*.md` for role definitions (host-agnostic; no `.cursor/` paths)
- [ ] **Cycle trigger**: Manual continue, pending prompt file, or cron (see `agent-automation/docs/hooks.md`)

## Cursor

1. Open workspace at project root (contains `PROJECT_WORKSPACE.md` and `agent-automation/`).
2. Use `.cursor/` for rules, agents, hooks, MCP config.
3. Configure MCP in `.cursor/mcp.json`:
   ```json
   {
     "mcpServers": {
       "agent-automation": {
         "command": "python",
         "args": ["agent-automation/mcp-server/server.py"],
         "env": { "PYTHONPATH": "agent-automation" }
       }
     }
   }
   ```
4. Stop hook at `.cursor/hooks/stop_hook.py` provides automatic cycle continuation.

## Claude Code

1. Clone/copy the workspace to your machine.
2. Set `WORKSPACE_ROOT` to the workspace directory (or use `workspace_config.yaml`).
3. Run MCP server:
   ```bash
   cd <workspace>
   PYTHONPATH=agent-automation python agent-automation/mcp-server/server.py
   ```
4. Configure Claude Code to connect to the MCP server (stdio).
5. Use `agent-automation/agents/*.md` for role prompts (no `.cursor/`).
6. Cycle trigger: manually prompt "Run one cycle..." or write to `agent-automation/orchestrator_pending_prompt.txt` when a subagent finishes.

## Vertex AI / Augment

1. Deploy workspace (or mount it) so the agent can read `PROJECT_WORKSPACE.md` and `agent-automation/`.
2. Set `WORKSPACE_ROOT` in the environment.
3. Run MCP server as a sidecar or connect to a shared MCP endpoint.
4. Use `agent-automation/agents/*.md` for role definitions.
5. Cycle trigger: depends on host capabilities (manual, file-based, or API).

## Path Resolution

| Source | Priority |
|--------|----------|
| `WORKSPACE_ROOT` env | 1 |
| `agent-automation/workspace_config.yaml` → `workspace_root` | 2 |
| Parent of `agent-automation/` | 3 (default) |

## Key Files

| File | Purpose |
|------|---------|
| `agent-automation/workspace_config.py` | Path resolution (get_workspace_root, load_config) |
| `agent-automation/workspace_config.yaml.example` | Optional override template |
| `agent-automation/agents/*.md` | Host-agnostic role definitions |
| `agent-automation/docs/hooks.md` | Stop hook behavior, non-Cursor replication |
| `agent-automation/mcp-server/README.md` | MCP standalone setup |

## PROJECT_WORKSPACE.md

All path references in `PROJECT_WORKSPACE.md` use relative paths (e.g. `agent-automation/prompts/...`) or `{WORKSPACE_ROOT}`. No absolute paths like `/Users/...`.
