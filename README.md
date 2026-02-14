# my-dev-workspace

Multi-agent autonomous development workspace for the **YouTube Shorts generation pipeline**. Coordination is done via **PROJECT_WORKSPACE.md** and the **agent-automation MCP** (status, pending tasks, work log).

## What’s in this repo

| Path | Description |
|------|--------------|
| **PROJECT_WORKSPACE.md** | Shared dashboard, work log, approvals, role status, and implementation plan. |
| **youtube-shorts-generator/** | Pipeline app: agents, services, CLI, config. See [youtube-shorts-generator/README.md](youtube-shorts-generator/README.md) to run the pipeline. |
| **agent-automation/** | MCP server, work log script, and automation docs. |
| **.cursor/** | Orchestrator rule, subagents (Lead Engineer, Architect, CTO, etc.), and hooks for follow-up cycles. |

## Quick start

1. Open this workspace in Cursor.
2. Enable the **agent-automation** MCP server.
3. Start the Orchestrator (see [agent-automation/ORCHESTRATOR_SETUP.md](agent-automation/ORCHESTRATOR_SETUP.md)).

To run the YouTube Shorts pipeline (generate, status, health), use the app in **youtube-shorts-generator/** — see [youtube-shorts-generator/README.md](youtube-shorts-generator/README.md).
