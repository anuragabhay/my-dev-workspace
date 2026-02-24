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

### 2. Set API Keys

**Option A: Environment (recommended)**

```bash
export ANTHROPIC_API_KEY=sk-ant-...
# or
export ORCHESTRATOR_LLM_API_KEY=sk-ant-...
```

**Option B: UI**

Enter your Anthropic API key in the UI before clicking "Run brain". The key is never logged or stored.

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

### 4. Run the Brain

1. Open http://localhost:8765 in a browser.
2. (Optional) Enter your API key if not set via env.
3. (Optional) Paste a PROJECT_WORKSPACE.md snippet for richer context.
4. Click **Run brain**.
5. View the A2A flow: **Proposal** → **Critique** → **Synthesis** → **Final Decision**.

## What to Look For

- **Proposal**: The Proposer’s initial suggested action (delegation, ORCHESTRATION_COMPLETE, etc.).
- **Critique**: The Critic’s review (alignment with plan, role choice, re-delegation risks).
- **Synthesis**: The Proposer’s revised decision after incorporating the critique.
- **Final Decision**: The final output (same as synthesis).

## Limitations

- **Brain-only mode**: The UI runs the brain with file-based context (orchestrator_rule, patterns, workflow, decisions, roles). It does **not** connect to the MCP server for live `get_pending_orchestrator_prompt`, `get_workspace_status`, or `get_workflow_config`. For a full cycle with MCP, use `orchestrator_client/cycle_runner.py` (requires `context_loader` and `mcp_client`).
- **Stub context**: When PROJECT_WORKSPACE.md is not available or you don’t paste a snippet, the brain uses a minimal stub context. You can paste a snippet in the UI for better results.
- **Single-user**: API keys passed in the request are used only for that request; they are not persisted.

## Dependencies

- **context_loader**: Used to build the orchestrator system message from `orchestrator_rule.md`, `orchestrator_patterns.md`, `workflow.yml`, `decisions.yml`, `roles.yml`.
- **mcp_client**: Not used by the UI. Full-cycle runs (cycle_runner) require it when MCP is available.

## API

- `GET /` — Serve the UI.
- `GET /api/status` — Check API status, env API key, workspace.
- `POST /api/run-brain` — Run the brain. Body: `{ "anthropic_api_key": "…", "workspace_snippet": "…", "pending_prompt": {}, "workspace_status": {}, "workflow_config": {} }`. Returns `{ "proposal", "critique", "synthesis", "final_decision" }`.
