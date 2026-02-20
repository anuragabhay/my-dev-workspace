# Stop Hook and Orchestrator Continuation

This document describes the Cursor stop hook behavior and how to replicate the orchestration loop on non-Cursor hosts (Claude Code, Vertex AI, Augment).

## Overview

The stop hook enables the Orchestrator to run multiple cycles automatically: when a subagent finishes, the hook injects a followup message so the Orchestrator continues without the user pasting. On non-Cursor hosts, you replicate this with manual continuation or external triggers.

## Cursor Stop Hook

### Location

- **Config**: `.cursor/hooks.json` — registers the `stop` hook
- **Script**: `.cursor/hooks/stop_hook.py` — the hook implementation

### When It Fires

The stop hook runs when a Cursor chat **stops** (user stops generation, or a subagent returns control to the parent).

### What It Does

1. **Subagent chat stopped**: Writes the run-cycle prompt to `agent-automation/orchestrator_pending_prompt.txt` and returns `{}` (no injection). Control returns to the Orchestrator automatically; the Orchestrator reads the pending prompt via MCP `get_pending_orchestrator_prompt` at the start of the next cycle.

2. **Orchestrator chat stopped**: If the Orchestrator wrote `ORCHESTRATION_COMPLETE`, hit User Intervention, or loop limit (5), returns `{}`. Otherwise:
   - If the last response contained a delegation slash command (e.g. `/lead-engineer ...`): returns that command as `followup_message` so the subagent runs.
   - Else: returns the run-cycle prompt as `followup_message` so the Orchestrator runs another cycle.

### What It Injects

- **Delegation**: The extracted slash command (e.g. `/junior-engineer-1 Append work log, commit, push...`) with optional enhancement from `prompt_enhancer.py` (roles.yml, workflow.yml).
- **Run-cycle**: The content of `agent-automation/prompts/orchestrator_run_cycle.md` or a default prompt instructing the Orchestrator to run one cycle (get_workspace_status, read PROJECT_WORKSPACE.md, decide, delegate, update).

### Workspace Root Resolution

The hook derives workspace root from:
1. `workspace_roots` or `workspace_root` in the JSON payload (from Cursor)
2. Otherwise: parent of `.cursor/hooks/` (i.e. workspace root)

## Replicating on Non-Cursor Hosts

### Option 1: Manual Continue

1. Run the Orchestrator (or equivalent) with the rule/instructions from `agent-automation/orchestrator_patterns.md` and `workflow.yml`.
2. After each subagent returns, manually prompt: *"Run one cycle: get_workspace_status, read PROJECT_WORKSPACE.md, decide next step, delegate if needed, update PROJECT_WORKSPACE.md."*
3. Or use the content of `agent-automation/prompts/orchestrator_run_cycle.md` as the continue prompt.

### Option 2: Pending Prompt File

1. When a subagent finishes, write the run-cycle prompt to `agent-automation/orchestrator_pending_prompt.txt`.
2. At the start of each Orchestrator cycle, read that file. If non-empty, use its content as the cycle instruction and clear the file.
3. MCP tool `get_pending_orchestrator_prompt` does exactly this: reads, returns, and clears.

### Option 3: Cron or Scheduler

1. Use a cron job or scheduler to periodically write a run-cycle prompt to `orchestrator_pending_prompt.txt`.
2. The Orchestrator (when run) reads it via MCP or file read and executes the cycle.
3. Useful for batch runs (e.g. daily) rather than real-time loops.

### Option 4: External MCP Client

1. Run the MCP server standalone (see `agent-automation/README.md`).
2. Connect from Claude Code, Vertex AI, or any MCP client.
3. Call `get_pending_orchestrator_prompt` at cycle start; call `get_workspace_status`, `check_my_pending_tasks` as needed.
4. Manually trigger continuation by writing to `orchestrator_pending_prompt.txt` when a subagent completes (if your host supports file writes from agents).

## Checklist for Non-Cursor

- [ ] Set `WORKSPACE_ROOT` env or `workspace_config.yaml` so paths resolve correctly
- [ ] Use `agent-automation/agents/*.md` for role definitions (no `.cursor/` paths)
- [ ] Run MCP server with `PYTHONPATH` including `agent-automation`
- [ ] Implement a cycle trigger: manual prompt, pending file, or cron
- [ ] Ensure Orchestrator reads `get_pending_orchestrator_prompt` at cycle start
