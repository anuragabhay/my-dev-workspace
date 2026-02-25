# Phase 1: PM Feasibility — MCP Integration + Streaming

**Initiative:** Custom Vibe Coding IDE  
**Phase:** 1 — MCP Integration + Streaming in Current Orchestrator UI  
**Author:** PM (Product Manager)  
**References:** `custom-ide-roadmap.md`, `custom-ide-research.md`, `orchestrator_ui/`, `mcp-server/`, `orchestrator_client/`

---

## 1. Feasibility Summary

| Dimension | Assessment | Notes |
|-----------|------------|-------|
| **MCP integration** | **Feasible** | mcp-server is complete; MCP client for UI backend needs to be added |
| **Streaming (chat)** | **Feasible** | Anthropic `messages.stream()` + FastAPI `StreamingResponse` |
| **Streaming (orchestration)** | **Feasible** | Refactor brain to yield phases + stream synthesis; SSE events |
| **Blockers** | **2 resolvable** | Missing `mcp_client`; brain is sync-only |

---

## 2. Current Capabilities

### 2.1 mcp-server

| Tool | Purpose | Status |
|------|---------|--------|
| `get_workspace_status` | Pending approvals, phase, next actions | ✅ Implemented |
| `get_pending_orchestrator_prompt` | Run-cycle prompt from stop hook | ✅ Implemented |
| `get_workflow_config` | workflow.yml, roles.yml, decisions.yml | ✅ Implemented |
| `list_roles` | Role names + one-line "when to use" | ✅ Implemented |
| `check_my_pending_tasks` | Pending tasks per role | ✅ Implemented |
| `get_my_role_tasks` | All tasks for a role | ✅ Implemented |
| `get_role_guidance` | SKILL.md / agent md per role | ✅ Implemented |
| `mark_task_complete` | Mark task done | ✅ Implemented |

**Transport:** Stdio. Server runs as subprocess; client connects via stdio.

### 2.2 orchestrator_client

| Component | Purpose | Status |
|-----------|---------|--------|
| `brain.py` | Propose → critique → synthesize (3 LLM calls) | ✅ Implemented; **non-streaming** |
| `context_loader.py` | System message from rule, patterns, workflow, decisions, roles | ✅ Implemented |
| `cycle_runner.py` | Load context → MCP tools → brain → decision | ⚠️ **Imports `mcp_client` which does not exist** |

### 2.3 orchestrator_ui

| Component | Purpose | Status |
|-----------|---------|--------|
| `server.py` | FastAPI; `/api/chat`, `/api/run-brain` | ✅ Implemented |
| Chat handler | Single LLM call for greetings/simple Q&A | ✅ Non-streaming |
| Orchestration handler | `run_brain_with_flow` with **stub context only** | ⚠️ **No MCP** |
| Frontend | Chat + collapsible reasoning panel | ✅ Exists; no streaming consumption |

---

## 3. Anthropic `messages.stream()` — Fit

### 3.1 API

```python
with client.messages.stream(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
) as stream:
    for text in stream.text_stream:
        yield text  # token-by-token
```

- **Sync:** `stream.text_stream` yields text chunks.
- **Async:** `async with client.messages.stream(...)` + `async for event in stream` for finer control.
- **Event types:** `message_start`, `content_block_delta` (text_delta), `message_stop`, etc.

### 3.2 Chat Mode

- Replace `client.messages.create()` in `_chat_handler` with `client.messages.stream()`.
- Wrap in `StreamingResponse(iterable, media_type="text/event-stream")`.
- Emit SSE events: `reply.chunk`, `reply.done`.

### 3.3 Orchestration Mode

- **Brain flow:** 3 sequential LLM calls (proposer → critic → synthesizer).
- **Streaming options:**
  1. **Phase progress:** Emit `flow.proposal` when Phase 1 done, `flow.critique` when Phase 2 done, `flow.synthesis` when Phase 3 done. Final reply = `final_decision` (can be streamed token-by-token in Phase 3).
  2. **Synthesis stream:** Only Phase 3 (synthesizer) streams; Phases 1–2 remain blocking. Emit `flow.proposal`, `flow.critique` as they complete, then stream `reply.chunk` for synthesis.

**Recommendation:** Option 2 — stream synthesis (final_decision) token-by-token; emit phase events as each completes. Minimal brain refactor: add `_call_llm_stream()` for Phase 3 only, or refactor all three to support optional streaming.

---

## 4. Blockers and Mitigations

| Blocker | Impact | Mitigation |
|---------|--------|------------|
| **`mcp_client` missing** | `cycle_runner` fails at import; UI has no MCP path | Create `orchestrator_client/mcp_client.py`: spawn mcp-server subprocess, use MCP Python client (`mcp` package) to call tools over stdio. Reuse pattern from Cursor MCP or MCP SDK examples. |
| **Brain is sync-only** | Cannot stream without blocking | Add `run_brain_with_flow_stream()` (or generator) that yields `flow.proposal`, `flow.critique`, then streams `flow.synthesis` chunks. Use `messages.stream()` for Phase 3. Phases 1–2 can stay sync. |
| **UI uses stub context** | Brain never gets live MCP data | In `_orchestration_handler`, before `run_brain_with_flow`: spawn MCP session (or use shared client), call `get_pending_orchestrator_prompt`, `get_workspace_status`, `get_workflow_config`; merge into context. Fallback to stub when MCP unavailable. |

---

## 5. MVP Acceptance Criteria

### 5.1 Config

| Criterion | Status | Notes |
|-----------|--------|-------|
| API key from env | ✅ | Existing |
| Workspace root, PROJECT_WORKSPACE.md | ✅ | Existing |
| `workflow.yml`, `roles.yml`, `decisions.yml` | ✅ | context_loader |

**Verdict:** Config OK (existing).

### 5.2 MCP Context in Brain

| Criterion | Requirement |
|----------|--------------|
| Workspace status | `get_workspace_status` result in brain context |
| Tasks | `get_pending_orchestrator_prompt` (and optionally `check_my_pending_tasks`) in context |
| Roles available | `list_roles` and/or `get_workflow_config` in context when brain runs |

**Implementation:** Before `run_brain_with_flow`, backend calls MCP tools (when available), populates `pending_prompt`, `workspace_status`, `workflow_config`. Fallback to stub when MCP unavailable.

### 5.3 Chat Streams Word-by-Word (or Token-by-Token)

| Criterion | Requirement |
|----------|--------------|
| Chat mode | Assistant reply streams incrementally |
| Transport | SSE (`text/event-stream`) |
| Events | `reply.chunk` (text), `reply.done` |

**Implementation:** `POST /api/chat` with `Accept: text/event-stream` → use `messages.stream()`, yield SSE events. Non-streaming: keep current JSON when `Accept: application/json`.

### 5.4 Orchestration: Streams Synthesis OR Shows Phase Progress

| Criterion | Requirement |
|----------|--------------|
| Phase progress | Emit `flow.proposal`, `flow.critique`, `flow.synthesis` as each completes |
| Synthesis stream | Final decision (synthesis) streams token-by-token |
| Events | `flow.proposal`, `flow.critique`, `flow.synthesis`, `reply.chunk`, `reply.done` |

**Implementation:** Refactor brain to support streaming path: Phases 1–2 block and emit events; Phase 3 uses `messages.stream()` and yields chunks.

---

## 6. Scope Boundaries

### In Scope (Phase 1)

| Item | Description |
|------|-------------|
| MCP integration | UI backend calls MCP tools at cycle start; brain receives live context |
| Streaming chat | Token-by-token streaming for chat mode |
| Streaming orchestration | Phase events + synthesis streaming |
| SSE API | `POST /api/chat` with `Accept: text/event-stream` |
| Frontend | Consume SSE; append chunks to assistant message; show flow in reasoning panel |

### Out of Scope (Phase 1)

| Item | Description |
|------|-------------|
| Project tree | File explorer panel — Phase 2 |
| Code editor | Embedded CodeMirror/Monaco — Phase 3 |
| Full IDE shell | Electron/Tauri, in-process MCP — Phase 4 |
| WebSocket | Use SSE only for Phase 1 |
| Vercel AI SDK | Backend stays Python/FastAPI; no SDK dependency |

---

## 7. Implementation Order (PM Recommendation)

1. **MCP client** — Create `mcp_client.py`; implement `create_mcp_session`, `run_orchestrator_tools` (or equivalent) to call `get_pending_orchestrator_prompt`, `get_workspace_status`, `get_workflow_config`.
2. **UI backend MCP** — In `_orchestration_handler`, call MCP when available; merge results into context; fallback to stub.
3. **Streaming chat** — Add `_chat_handler_stream()` using `messages.stream()`; new route or `Accept`-based branch for SSE.
4. **Streaming orchestration** — Add `run_brain_with_flow_stream()`; yield phase events + synthesis chunks; wire to SSE endpoint.
5. **Frontend** — Use `fetch` + `ReadableStream` or `EventSource` to consume SSE; append chunks to message; render flow in reasoning panel.

---

## 8. Risks and Assumptions

| Risk | Mitigation |
|------|------------|
| MCP subprocess spawn from FastAPI | Run in thread/async; ensure stdio pipes don't block event loop |
| Long-running orchestration (3 LLM calls) | SSE keeps connection alive; frontend shows progress |
| MCP unavailable (e.g. UI run standalone) | Graceful fallback to stub context; document in README |

**Assumptions:**

- Anthropic Python SDK supports `messages.stream()` (confirmed in docs).
- MCP Python SDK can connect to stdio server as client (spawn subprocess, connect read/write streams).
- FastAPI `StreamingResponse` works with async generators for SSE.

---

*Phase 1 feasibility produced by PM. Next: Architect to validate MCP client design; Lead Engineer to implement.*
