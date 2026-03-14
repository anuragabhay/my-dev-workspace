# Cursor Subagents + Hooks – Orchestrator Setup

This guide configures **one parent Orchestrator** and **role-based subagents** so all coordination happens in a single Cursor chat, using PROJECT_WORKSPACE.md and MCP.

---

## 1. What Was Created (Project Files)

### Orchestrator (parent agent)

- **File**: `.cursor/rules/orchestrator.mdc`
- **Role**: Reads PROJECT_WORKSPACE.md and MCP (`get_workspace_status`, `check_my_pending_tasks`); decides next step; delegates to the right subagent; updates the workspace after each step.
- **Escalation**: Architect for design, CTO for tech/architecture approval, User only for budget / phase / strategy / blockers.

### Subagents (custom agents)

| Role            | File                                      | When to use |
|-----------------|-------------------------------------------|-------------|
| Lead Engineer   | `.cursor/agents/lead-engineer.md`         | Implementation (code, config, venv, tests) in youtube-shorts-generator |
| Architect       | `.cursor/agents/architect.md`             | Design, “how to implement,” design Approval Requests |
| CTO             | `.cursor/agents/cto.md`                   | Tech/architecture approval, Approval Requests for stack/architecture |
| Junior Engineer 1 | `.cursor/agents/junior-engineer-1.md`     | Part 2 of dev split; implementation (tests, docs, small features), work log, commit/push when assigned |
| Junior Engineer 2 | `.cursor/agents/junior-engineer-2.md`     | Part 3 of dev split; implementation (tests, docs, small features), work log, commit/push when assigned |
| Reviewer        | `.cursor/agents/reviewer.md`             | Code review, quality review |
| Tester          | `.cursor/agents/tester.md`               | Test execution, test plans, QA |
| CFO             | `.cursor/agents/cfo.md`                  | Cost tracking and analysis (no budget approval) |
| PM              | `.cursor/agents/pm.md`                   | Task breakdown, acceptance criteria, roadmap within MVP |

**Skill paths (optional):** `.cursor/skills/<role>/SKILL.md` (e.g. lead-engineer, junior-engineer-1, junior-engineer-2, reviewer, tester, architect; optional qa-reviewer, ui-reviewer). **Workflow YAML:** `agent-automation/workflow.yml`, `roles.yml`, `decisions.yml`; use MCP `get_workflow_config`.

**Orchestrator first read:** `agent-automation/orchestrator_patterns.md` — stages, role index, parallel execution, MCP usage. Read each cycle with PROJECT_WORKSPACE.md.

All paths above are under `.cursor/` when the workspace root contains PROJECT_WORKSPACE.md and agent-automation.

### Hooks

- **File**: `.cursor/hooks.json`
- **Script**: `.cursor/hooks/stop_hook.py`
- **Logic**: On the `stop` hook, the script reads PROJECT_WORKSPACE.md. If **User Intervention Required** is Yes, it does nothing (no follow-up). Otherwise, if there are **Pending Approvals**, **Next Actions** with work, or an explicit **CONTINUE** in Next Actions, and the auto-followup count is under 5, it returns a `followup_message` so Cursor sends a follow-up prompt to the Orchestrator (e.g. “run get_workspace_status, delegate to the right subagent, update workspace”). Cursor enforces a maximum of 5 auto-followups.
- **Prompt enhancer**: Every prompt injected by the stop hook is passed through the prompt enhancer (`agent-automation/prompt_enhancer.py`), which appends requirements from `roles.yml` and division-of-work hints from `workflow.yml` so delegated tasks are detailed and structured. If the enhancer fails to load or run, the hook still returns the raw followup message.

---

## 2. Tool Set Per Subagent (Recommendation)

Cursor does not restrict tools per subagent in the `.md` files; the following is a **recommended** mapping. If your Cursor version supports per-agent tool configuration (e.g. in Settings → Agents), use it; otherwise all subagents inherit the same tools as the parent.

| Subagent       | MCP (agent-automation)     | Terminal | File edit | Read-only (read_file, grep, list_dir) |
|----------------|----------------------------|----------|-----------|----------------------------------------|
| Orchestrator   | Yes (all 4 tools)          | No       | Yes       | Yes                                     |
| Lead Engineer  | Yes                        | Yes      | Yes       | Yes                                     |
| Architect      | Yes                        | No       | Yes       | Yes                                     |
| CTO            | Yes                        | No       | Yes       | Yes                                     |
| Junior Engineer 1 | Yes                    | Yes      | Yes*      | Yes                                     |
| Junior Engineer 2 | Yes                    | Yes      | Yes*      | Yes                                     |
| CFO            | Yes                        | No       | Yes       | Yes                                     |
| PM             | Yes                        | No       | Yes       | Yes                                     |

\* Junior Engineer 1 or 2 may edit only when the task explicitly includes “write” (e.g. docs); otherwise prefer read-only + report.

---

## 3. Cursor Settings / UI (If Needed)

If any of this is configured only in the UI:

1. **Open**: **Cursor Settings → Agents** (or **Rules / Skills / Subagents and Hooks**).
2. **Orchestrator**: Ensure the **project** rule from `.cursor/rules/orchestrator.mdc` is enabled (project rules are usually auto-loaded from `.cursor/rules/*.mdc`). No need to paste text if the file is in place.
3. **Subagents**: Subagents are loaded from `.cursor/agents/*.md`. No need to create them again in the UI if the files exist.
4. **Hooks**: Hooks are loaded from `.cursor/hooks.json`. Ensure the path to `stop_hook.py` is correct and `python3` is in PATH when Cursor runs the hook.

If your Cursor version requires **manually adding** an “Orchestrator” agent:
- **Name**: Orchestrator  
- **Prompt**: Paste the contents of the “Orchestrator Agent” section from `.cursor/rules/orchestrator.mdc` (the main bullet list and the “Each cycle”, “MCP usage”, “Conventions” sections).
- **Tools**: MCP (agent-automation), file edit, read-only.

For each **custom subagent** created in the UI (if file-based subagents are not used):
- **Name**: lead-engineer (or architect, cto, junior-engineer-1, junior-engineer-2, cfo, pm)  
- **Prompt**: Paste the body (below the YAML frontmatter) of the corresponding `.cursor/agents/<name>.md` file.  
- **Tools**: As in the table above.

---

## 4. How to Run

1. Open Cursor with workspace root at the folder that contains PROJECT_WORKSPACE.md and .cursor.
2. Ensure MCP server **agent-automation** is running and configured (see MCP_INTEGRATION.md).
3. In chat, give one instruction to the Orchestrator, e.g.:  
   **“Read PROJECT_WORKSPACE.md and MCP get_workspace_status and check_my_pending_tasks for Lead Engineer. Then delegate the next Phase 1 task to the Lead Engineer subagent and update the workspace.”**
4. After the Orchestrator (and any subagent) responds, the **stop** hook runs. If the condition is met, Cursor will send the configured `followup_message` and the loop continues (up to 5 times).
5. To force another cycle manually, say e.g.:  
   **“Again: get workspace status, decide next step, delegate to the right subagent, update PROJECT_WORKSPACE.md.”**

---

## 5. After subagent completes (trigger next Orchestrator cycle)

When a **subagent** chat (Lead Engineer, Junior Engineer 1, Junior Engineer 2, Architect, etc.) stops, the stop hook detects it and returns:

- `followup_message`: the **orchestrator run-cycle prompt** (same text as in `agent-automation/prompts/orchestrator_run_cycle.md`).
- `orchestrator_cycle`: `true` (so the runner can route this to the Orchestrator chat if supported).

**Canonical prompt file**: `agent-automation/prompts/orchestrator_run_cycle.md` — single line:

`Run one cycle: get_workspace_status, read PROJECT_WORKSPACE.md (Dashboard, Next Actions, Role Status). Determine which role the next action is for from Next Actions; call check_my_pending_tasks(role="<that role>") — e.g. Lead Engineer, Junior Engineer 1, Junior Engineer 2, Reviewer, Tester, Architect, PM, CTO, CFO. Then decide next step, delegate if needed, update PROJECT_WORKSPACE.md.`

**Runner behavior**: Cursor injects the followup into the chat that stopped (often the subagent chat), so the next cycle does not start in the Orchestrator automatically. To close the loop:

1. **Hook** also writes `followup_message` to `agent-automation/orchestrator_pending_prompt.txt` when it returns `orchestrator_cycle: true`.
2. **Orchestrator** calls MCP tool `get_pending_orchestrator_prompt` at the start of each cycle. If it returns a non-empty `prompt`, the Orchestrator executes it (run one cycle). The tool reads and then deletes the file.
3. **User**: After a subagent finishes, switch to the Orchestrator chat and say **"continue"** (or "run one cycle"). The Orchestrator will call `get_pending_orchestrator_prompt`, get the prompt from the file, and run the cycle—no need to paste the long prompt.

---

## 6. Optional: Explicit CONTINUE

To trigger the hook’s follow-up even when there are no pending approvals, set **Next Actions** in PROJECT_WORKSPACE.md to include the word **CONTINUE**, e.g.:

- `**Next Actions**: CONTINUE - Phase 1 config templates and database schema`

The stop hook treats this as a signal to return a `followup_message` (subject to User Intervention and max 5 loops).

---

## 7. Work log (external store)

- **Full log**: `agent-automation/work_log.json` (JSON array, one object per entry: `timestamp`, `role`, `task`, `status`, `content`).
- **In PROJECT_WORKSPACE.md**: Only the last 10 entries are kept under "## 📝 Recent Work Log (last 10)" plus a line "Full log: agent-automation/work_log.json".
- **To add an entry**: run  
  `python agent-automation/append_work_log.py --timestamp "YYYY-MM-DD HH:MM UTC" --role "Role Name" --task "Task name" --status "✅ COMPLETED" [--content "- Bullet one\n- Bullet two"]`  
  (content can be omitted or piped via stdin). Then run with `--update-workspace` to refresh the recent 10 in PROJECT_WORKSPACE.md.
- **Optional**: `--max-entries N` (default 500) trims the JSON file to the last N entries.

---

## 8. Orchestrator client (standalone) — environment variables

When running the orchestrator client (`agent-automation/orchestrator_client/cycle_runner.py`) outside Cursor:

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Anthropic API key (or use `ORCHESTRATOR_LLM_API_KEY`) | — |
| `ORCHESTRATOR_LLM_MODEL` | Fallback model for Proposer and Critic (must be a model ID, e.g. `claude-sonnet-4-20250514`, not the provider name "anthropic") | `claude-sonnet-4-20250514` |
| `ORCHESTRATOR_PROPOSER_MODEL` | Model for Proposer (Phase 1 and 3) | `ORCHESTRATOR_LLM_MODEL` |
| `ORCHESTRATOR_CRITIC_MODEL` | Model for Critic (Phase 2) | `ORCHESTRATOR_LLM_MODEL` |
| `ORCHESTRATOR_OPENAI_MODEL` | When provider=openai: must be a **valid OpenAI model ID** (e.g. `gpt-4o`, `gpt-4o-mini`, `gpt-4.1-mini`), **not** the provider name `anthropic` | `gpt-4o-mini` |

For MVP, both Proposer and Critic use the same model. Set different models to use a dedicated critic (e.g. a smaller/faster model for critique).

**Troubleshooting**: `404 model anthropic does not exist` means `ORCHESTRATOR_OPENAI_MODEL` was set to a provider name; use a real OpenAI model ID.

---

## 9. Orchestrator UI (brain-only, outside Cursor)

**Environment variables** (see `orchestrator_ui/.env.example`):

- `ORCHESTRATOR_OPENAI_MODEL`: When using OpenAI provider, must be a **valid OpenAI model ID** (e.g. `gpt-4o`, `gpt-4o-mini`, `gpt-4.1-mini`), **not** the provider name `anthropic`. See `chat_completions.md` for supported model IDs.

**Troubleshooting**: If you see `404 model anthropic does not exist`, `ORCHESTRATOR_OPENAI_MODEL` was set to a provider name instead of a real model ID. Use a valid OpenAI model ID such as `gpt-4o-mini`.

A web UI to run the A2A brain without Cursor:

```bash
cd agent-automation/orchestrator_ui
pip install -r requirements.txt
PYTHONPATH=.. python server.py
```

Open http://localhost:8765. Set API key via env or in the UI, click "Run brain", and see proposal → critique → synthesis → final decision. See `orchestrator_ui/README.md` for details and limitations (brain-only; no MCP).

---

## 10. Local LLM Setup (Ollama)

The Orchestrator enforces `ORCHESTRATOR_LLM_PROVIDER=local` at startup. All LLM calls route to a locally running Ollama instance. No cloud AI API is used.

### Install Ollama

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

See https://ollama.com for Windows and other platforms.

### Start Ollama

```bash
ollama serve   # runs on http://localhost:11434 by default
```

Ollama starts automatically at login on macOS after `brew install`.

### Pull a model

```bash
# Recommended (12B, Apache 2.0, ~7 GB)
ollama pull mistral-nemo

# Lightweight option (3.8B, MIT, ~3 GB, fast on limited hardware)
ollama pull phi4-mini
```

**Cold-start note:** The first request after a model pull may take 10–30 seconds while the model loads into RAM/VRAM. Subsequent requests are fast.

### Verify Ollama is running

```bash
curl http://localhost:11434/api/tags
```

Returns a JSON list of available models. If it returns `Connection refused`, run `ollama serve` first.

### Environment variables

| Variable | Default | Description |
|---|---|---|
| `ORCHESTRATOR_LLM_PROVIDER` | `local` | Must be `local`. Server exits if set to anything else. |
| `ORCHESTRATOR_LLM_BASE_URL` | `http://localhost:11434/v1` | Ollama API endpoint. Change if Ollama runs on a non-default port or a remote LAN server. |
| `ORCHESTRATOR_LLM_MODEL` | `mistral-nemo` | Model tag as pulled via `ollama pull`. Use exact tag names (e.g. `mistral-nemo`, `phi4-mini`, `phi4`). |

### Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `"Local LLM unavailable"` (HTTP 503) | Ollama is not running | Run `ollama serve` |
| `"model not found"` (HTTP 500) | Model not pulled | Run `ollama pull <model>` |
| `FATAL: ORCHESTRATOR_LLM_PROVIDER='anthropic' is not allowed` | Wrong provider in `.env` | Set `ORCHESTRATOR_LLM_PROVIDER=local` |
| Slow first response | Model loading into memory | Normal; wait 10–30s; subsequent requests are fast |

---

## 11. Summary

- **Orchestrator**: `.cursor/rules/orchestrator.mdc` — one parent agent in one chat.
- **Subagents**: `.cursor/agents/{lead-engineer,junior-engineer-1,junior-engineer-2,architect,cto,reviewer,tester,cfo,pm}.md` — invoked via `/lead-engineer`, `/junior-engineer-1`, `/junior-engineer-2`, etc.
- **Hooks**: `.cursor/hooks.json` + `.cursor/hooks/stop_hook.py` — optional auto-continue until done or user intervention.
- **Brain**: `orchestrator_client/brain.py` — propose → critique → synthesize (A2A-style) when running cycle_runner.
- **Authority**: No User approval for implementation/design/tech within the approved plan; Architect for design, CTO for tech/architecture; User only for budget, phase, strategy, blockers.
