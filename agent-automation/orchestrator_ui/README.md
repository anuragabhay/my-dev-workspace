# Orchestrator UI

A dedicated UI for the orchestrator A2A brain so you can run the **propose → critique → synthesize** flow outside Cursor, with your own API keys.

## What It Does

The brain runs a three-phase A2A (Agent-to-Agent) protocol:

1. **Proposal** — Proposer (Model A) receives context and proposes the next action (e.g. a delegation, ORCHESTRATION_COMPLETE, or run cycle).
2. **Critique** — Critic (Model B) reviews the proposal against the workflow and plan.
3. **Synthesis** — Proposer incorporates the critique and outputs the final decision.

The UI lets you run this flow and see each step.

## Quick Start

### 1. Install Dependencies

```bash
cd agent-automation/orchestrator_ui
pip install -r requirements.txt
```

Or from workspace root with PYTHONPATH:

```bash
cd agent-automation
pip install orchestrator_ui/requirements.txt
```

### 2. Environment (required for chat)

The app reads **only from environment**; no API key or workspace path in the UI or request body.

- **ANTHROPIC_API_KEY** (or **ORCHESTRATOR_LLM_API_KEY**) — Required to run the brain.
- **WORKSPACE_PATH** or **WORKSPACE_ROOT** (optional) — Workspace root (directory containing `PROJECT_WORKSPACE.md`). If unset, the app derives from the agent-automation parent.

Example: copy `orchestrator_ui/.env.example` to `.env` and set values, or:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
# optional: export WORKSPACE_PATH=/path/to/your-workspace
```

### 3. Start the UI

```bash
cd agent-automation/orchestrator_ui
PYTHONPATH=.. python server.py
```

Or from workspace root:

```bash
PYTHONPATH=agent-automation python agent-automation/orchestrator_ui/server.py
```

The UI runs at **http://localhost:8765**.

### 4. Use the revamped UI

1. Open http://localhost:8765 in a browser.
2. Check the status line: **Config: OK** or a message like **Config: missing (set ANTHROPIC_API_KEY in env)**.
3. Type a message in the chat input and click **Send**. The backend runs one orchestrator cycle (context + brain) and returns the reply.
4. The main chat shows only user messages and assistant replies. Open the **Reasoning** panel (sidebar) to see Proposal, Critique, Synthesis and tool calls for the latest turn.
5. On 400/500 errors, the UI shows the error and you can retry (no key or snippet in the UI).

## What to Look For

- **Proposal**: The Proposer’s initial suggested action (delegation, ORCHESTRATION_COMPLETE, etc.).
- **Critique**: The Critic’s review (alignment with plan, role choice, re-delegation risks).
- **Synthesis**: The Proposer’s revised decision after incorporating the critique.
- **Final Decision**: The final output (same as synthesis).

## MCP: Stdio vs In-Process

- **Current:** MCP uses **Stdio** transport. The UI backend spawns the `mcp-server` as a subprocess or uses MCP when provided by the environment (e.g. Cursor).
- **In-process MCP (Phase 4):** Documented for future use. In-process would run the MCP server inside the IDE process (no subprocess). For web-only deployment we keep Stdio; in-process applies if the IDE runs as a single process (e.g. Electron main or Tauri). No implementation change for now — Stdio remains the default.
- **Stub context**: When PROJECT_WORKSPACE.md is not available or you don’t paste a snippet, the brain uses a minimal stub context. You can paste a snippet in the UI for better results.
- **Single-user**: API keys passed in the request are used only for that request; they are not persisted.

## Phase 4: Full IDE Shell Features

- **Resizable panels** — Project tree (left) and Reasoning (right) panels can be resized by dragging the handles between them. Widths are persisted.
- **Layout persistence** — Panel widths and collapsed states (tree, reasoning, terminal) are saved to `localStorage` and restored on reload. Keys: `ide_tree_width`, `ide_reasoning_width`, `orchestrator-ui-layout`.
- **Terminal panel** — Collapsible terminal section at the bottom (MVP: placeholder "Terminal (coming soon)"; xterm.js integration planned).
- **MCP Stdio** — Backend connects to MCP server via Stdio subprocess when available; falls back to stub context when MCP is unavailable.

## Limitations

- **Brain-only mode**: The UI runs the brain with file-based context (orchestrator_rule, patterns, workflow, decisions, roles). It does **not** connect to the MCP server for live `get_pending_orchestrator_prompt`, `get_workspace_status`, or `get_workflow_config`. For a full cycle with MCP, use `orchestrator_client/cycle_runner.py` (requires `context_loader` and `mcp_client`).

## Dependencies

- **context_loader**: Used to build the orchestrator system message from `orchestrator_rule.md`, `orchestrator_patterns.md`, `workflow.yml`, `decisions.yml`, `roles.yml`.
- **mcp_client**: Not used by the UI. Full-cycle runs (cycle_runner) require it when MCP is available.

## Phase 5: Lifecycle Hooks

The orchestrator supports **lifecycle hooks** for custom automation. Hooks are configured in `.cursor/hooks.json` and can be extended in `workflow.yml` or a separate hooks config.

### Lifecycle Hook Points

| Hook | When | Description |
|------|------|-------------|
| `before_cycle` | Before orchestrator cycle starts | Run scripts or checks before `get_workspace_status` and brain run |
| `after_cycle` | After orchestrator cycle completes | Run scripts after final decision (e.g. logging, notifications) |
| `before_delegate` | Before delegating to subagent | Run before invoking `/lead-engineer`, `/junior-engineer-1`, etc. |
| `after_delegate` | After subagent returns | Run after subagent finishes (e.g. work log, status sync) |

### Cursor Hooks (stop hook)

The **stop** hook in `.cursor/hooks.json` runs when a Cursor chat stops. It reads `PROJECT_WORKSPACE.md`, detects Orchestrator context, and optionally returns a `followup_message` to continue the cycle (e.g. "Run one cycle" or a delegation slash command). This enables automatic loop continuation without user paste.

### API: GET /api/hooks

Returns hooks config from `.cursor/hooks.json` plus lifecycle definitions. Use for UI to show available hooks and their configuration.

## API

- `GET /` — Serve the UI.
- `GET /api/status` — Legacy API status.
- `GET /api/config-status` — Booleans only: `api_key_configured`, `workspace_configured` (no secrets). Use for UI status line.
- `GET /api/hooks` — Hooks config from `.cursor/hooks.json` and lifecycle definitions (Phase 5).
- `GET /api/slash-commands` — Slash commands from `roles.yml`: `{ "commands": [{ "slash", "role", "display_name" }] }` (Phase 5).
- `GET /api/skills` — Skills from `.cursor/skills/*/SKILL.md`: `{ "skills": [{ "name", "path", "description?" }] }` (Phase 5).
- `GET /api/rules` — Rules from `.cursor/rules/*.mdc`: `{ "rules": [{ "name", "path" }] }` (Phase 5).
- `POST /api/chat` — Chat endpoint. Body: `{ "messages": [{ "role": "user"|"assistant", "content": "..." }], "include_flow": true }`. API key and workspace from env only. Returns `{ "reply", "flow": { "proposal", "critique", "synthesis" }, "tool_calls"?: [...] }`. 400 if invalid (e.g. empty messages), 500 with `{ "error": "..." }` on failure.
- `POST /api/run-brain` — Legacy. Body may include `anthropic_api_key`, `workspace_snippet`. Returns `{ "proposal", "critique", "synthesis", "final_decision" }`.
