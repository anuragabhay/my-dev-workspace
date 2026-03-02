# Project Plan — Unified App / Custom Vibe Coding IDE

**Initiative:** Custom Vibe Coding IDE — Unified App with Local LLM, Dynamic UI, and Mode Routing  
**Version:** 1.0  
**Date:** 2026-03-01  
**Author:** PM  
**Based on:** `agent-automation/docs/ARCHITECTURE.md` v1.0 (Approved with Conditions — Approval #002)  
**Status:** Ready for User Review and Development Sign-off

---

## Table of Contents

1. [Overview](#1-overview)
2. [Preservation Guarantee](#2-preservation-guarantee)
3. [CTO Conditions — Non-Negotiable Enforcement](#3-cto-conditions--non-negotiable-enforcement)
4. [Phase A — Local LLM Foundation](#4-phase-a--local-llm-foundation)
5. [Phase B — Mode Registry and Intent Routing](#5-phase-b--mode-registry-and-intent-routing)
6. [Phase C — Session Persistence](#6-phase-c--session-persistence)
7. [Phase D — Dynamic UI Renderer](#7-phase-d--dynamic-ui-renderer)
8. [Phase E — Embedded Editor and File Operations](#8-phase-e--embedded-editor-and-file-operations)
9. [Phase F — PWA Packaging](#9-phase-f--pwa-packaging)
10. [Parallelization Map](#10-parallelization-map)
11. [Module Dependency Graph](#11-module-dependency-graph)
12. [Single-Branch Strategy](#12-single-branch-strategy)
13. [Acceptance Criteria Master List](#13-acceptance-criteria-master-list)
14. [Risk Register](#14-risk-register)

---

## 1. Overview

This plan operationalizes the approved architecture (`ARCHITECTURE.md` v1.0) for evolving the existing `agent-automation/orchestrator_ui/` into a unified vibe-coding IDE that runs entirely on a local LLM (Ollama), routes user intent to specialized modes, renders rich dynamic UI responses, persists conversations in SQLite, and provides a CodeMirror-based multi-file editor with diff-and-accept workflow. The YouTube Shorts generator continues to run independently at port 8766 and is integrated only via HTTP proxy. The work is phased so that each phase is independently deployable, tested, and merged before the next begins. Phases A and C are independent and can be developed concurrently; Phases B, D, and E have sequential dependencies on earlier phases. Phase F (PWA) can start any time the frontend is stable. All changes are strictly additive — no existing route, file, or behavior is removed; rollback at any phase requires only reverting the new files and three modified files.

---

## 2. Preservation Guarantee

**Both of the following systems must continue to work — without any behavioral change — throughout every phase of development:**

| System | How It Is Protected |
|--------|-------------------|
| **Orchestrator (Cursor agent automation)** | `mcp-server/server.py`, `brain.py`, `context_loader.py`, `cycle_runner.py`, `workflow.yml`, `roles.yml`, `.cursor/rules/`, `.cursor/skills/`, hooks — all UNTOUCHED. No modifications permitted. |
| **YouTube Shorts FastAPI (port 8766)** | `youtube-shorts-generator/` — UNTOUCHED. Unified app connects only via HTTP proxy in `video_handler`. |

**No-breakage check (mandatory per phase):**

Before any phase is considered done, the following smoke test must pass:

1. `cd youtube-shorts-generator && python -m pytest tests/ -v` — all tests pass, or baseline count is maintained.
2. `cd agent-automation/orchestrator_ui && PYTHONPATH=.. python server.py` starts without errors.
3. `GET /api/config-status` returns `{ has_api_key: bool, has_workspace: bool }` (existing contract).
4. `POST /api/chat` with an existing payload returns a valid reply (no regression).
5. MCP server responds to a ping (Orchestrator automation intact).

If any of these fail, the phase's changes must be reverted or fixed before merging.

---

## 3. CTO Conditions — Non-Negotiable Enforcement

These four conditions were set by CTO in Approval #002. They are not optional; each is mapped to the phase that must implement it.

| # | Condition | Enforced In | Acceptance Test |
|---|-----------|-------------|----------------|
| **CTO-1** | All `video_embed` iframes in `renderer.js` must include `sandbox="allow-scripts allow-same-origin"` | Phase D | Code review: grep for `video_embed` renderer; confirm `sandbox` attribute is set |
| **CTO-2** | Session message truncation/windowing strategy must be defined and documented before Phase C implementation begins | Pre-Phase C (document in this plan — see §6) | Strategy documented in Phase C section; reviewed before first commit |
| **CTO-3** | `/api/file` endpoints must require `WORKSPACE_ROOT` as an explicit env var; no auto-detection from `__file__` | Phase E | `.env.example` updated; server raises `500` if `WORKSPACE_ROOT` unset at startup |
| **CTO-4** | `jsonschema>=4.0` must be added to `requirements.txt` before Phase D | Phase D (pre-condition) | `grep 'jsonschema' requirements.txt` passes; version is `>=4.0` |

**CTO Q1–Q6 Decisions (locked; do not re-open without CTO approval):**

| # | Decision |
|---|---------|
| Q1 | Default `ORCHESTRATOR_LLM_PROVIDER=local` enforced by startup guard in `server.py`. Cloud providers (`anthropic`, `openai`) retained in `llm_provider.py` for open-source extensibility only; not callable from unified app in normal operation. |
| Q2 | `jsonschema>=4.0` added to `requirements.txt` explicitly. |
| Q3 | Both inline artifact cards AND Canvas tab are in scope for Phase D. |
| Q4 | Phase F = PWA only (manifest + service worker). Capacitor APK deferred. |
| Q5 | `orchestrator_ui/sessions.db` as default; `SESSION_DB_PATH` env var supported from Phase C start. |
| Q6 | Ghost text (L3, `@marimo-team/codemirror-ai`) is excluded from Phase E. Phase E = L1 + L2 only. |

---

## 4. Phase A — Local LLM Foundation

**Goal:** `ORCHESTRATOR_LLM_PROVIDER=local` routes to Ollama end-to-end; existing `anthropic` and `openai` paths are unaffected.

### Deliverables Checklist

- [ ] `orchestrator_client/llm_provider.py` — add `local` branch in `chat_sync()` and `chat_stream()`: reuse OpenAI SDK with `base_url=ORCHESTRATOR_LLM_BASE_URL` and `api_key="ollama"` dummy value
- [ ] `orchestrator_ui/.env.example` — add `ORCHESTRATOR_LLM_PROVIDER=local`, `ORCHESTRATOR_LLM_BASE_URL=http://localhost:11434/v1`, `ORCHESTRATOR_LLM_MODEL=mistral-nemo`
- [ ] `agent-automation/ORCHESTRATOR_SETUP.md` — add Ollama setup section: `brew install ollama`, `ollama serve`, `ollama pull mistral-nemo`; document cold-start latency (10–30s for 12B models); add pre-load on server start tip
- [ ] Unit test: `chat_sync(provider="local", ...)` with Ollama mock returns a reply without error
- [ ] Add startup guard in `server.py`: if `ORCHESTRATOR_LLM_PROVIDER != 'local'`, `sys.exit(1)` with clear error. Unit test: env with `ORCHESTRATOR_LLM_PROVIDER=anthropic` causes startup failure.

### Dependencies

None. Phase A can start immediately on a fresh branch.

### Effort Estimate

~2 days (Lead Engineer: 1 day implementation; Junior Engineer: 0.5 days tests + docs; 0.5 days review buffer)

### Owner Roles

- **Lead Engineer**: `llm_provider.py` local branch implementation
- **Junior Engineer 1**: Unit tests, `.env.example` update, `ORCHESTRATOR_SETUP.md` Ollama section
- **Junior Engineer 2**: Work log, commit, push

### Acceptance Criteria

1. Running `ORCHESTRATOR_LLM_PROVIDER=local ORCHESTRATOR_LLM_MODEL=mistral-nemo python server.py` starts without errors.
2. `POST /api/chat` with a short message returns a streaming reply when Ollama is running.
3. When Ollama is unreachable, `/api/chat` returns HTTP 503 with body: `"Local LLM unavailable. Run: ollama serve && ollama pull mistral-nemo"`.
4. If `ORCHESTRATOR_LLM_PROVIDER` is set to `'anthropic'` or `'openai'`, server exits at startup with a message containing `'local-only'`. The `anthropic`/`openai` branches in `llm_provider.py` remain in source (for open-source use) but are not reachable from the unified app.
5. All existing unit tests pass.
6. No-breakage smoke test passes (see §2).

---

## 5. Phase B — Mode Registry and Intent Routing

**Goal:** Every `POST /api/chat` message is classified into a mode; the correct handler is called; `detect_intent()` shim preserves backward compatibility.

### Deliverables Checklist

- [ ] `orchestrator_ui/modes.py` — `ModeDefinition` dataclass; in-memory registry; `load_modes(path)` from JSON; `get_mode(id)` lookup
- [ ] `orchestrator_ui/modes.json` — 5 mode definitions: `chat`, `orchestration`, `video`, `coding`, `health`
- [ ] `orchestrator_client/intent.py` — add `detect_mode(message, history) -> str`; rule-based fast path (keyword scan) then LLM fallback (JSON response, confidence threshold < 0.6 → default `"chat"`); keep `detect_intent()` as a one-line shim calling `detect_mode`
- [ ] `orchestrator_ui/server.py` — wire `detect_mode()` in `POST /api/chat`; dispatch to handler by mode; stub handlers for modes not yet implemented (`video_handler`, `coding_handler`, `health_handler` return placeholder responses)
- [ ] Unit tests:
  - Rule-based: `"youtube short"` → `"video"`, `"/health"` → `"health"`, `"code a todo app"` → `"coding"`, `"/orchestrate"` → `"orchestration"`, ambiguous → `"chat"`
  - LLM fallback mock: low-confidence response → `"chat"`
  - `detect_intent()` shim: returns same result as `detect_mode(message, [])`

### Dependencies

- Phase A must be complete (LLM needed for the fallback LLM classifier).

### Effort Estimate

~2 days (Lead Engineer: 1 day; Junior Engineer 1: 0.5 days tests; 0.5 days review + docs)

### Owner Roles

- **Lead Engineer**: `modes.py`, `modes.json`, `intent.py` `detect_mode`, server wiring
- **Junior Engineer 1**: Unit tests for classifier (rule-based + LLM mock)
- **Junior Engineer 2**: Work log, commit, push

### Acceptance Criteria

1. `detect_mode("generate a youtube short about AI", [])` returns `"video"`.
2. `detect_mode("hello how are you", [])` returns `"chat"`.
3. `detect_mode("/health", [])` returns `"health"`.
4. `detect_intent("code a todo app")` returns `"coding"` (shim backward compat).
5. `POST /api/chat { "messages": [{"role":"user","content":"run /orchestrate"}] }` dispatches to orchestration handler (verify via log or response field `mode_used`).
6. All unit tests for classifier pass.
7. No-breakage smoke test passes (see §2).

---

## 6. Phase C — Session Persistence

**Goal:** Conversations survive page reload; session list sidebar shows history; New Chat creates a fresh session.

### Session Message Truncation Strategy (CTO-2 — Required Before Implementation)

To comply with CTO Condition 2, the following strategy is defined here and must be implemented in `sessions.py` before Phase C is merged:

**Strategy: Sliding Window with Hard Cap**

- When assembling the message history for an LLM call, load only the **last N messages** from the session (default: `SESSION_CONTEXT_WINDOW=20` messages, configurable via env var).
- If the estimated token count of the window exceeds a threshold (`SESSION_MAX_TOKENS=8000` tokens, configurable), drop the oldest messages one at a time until within threshold.
- Token estimation: `len(content) // 4` (character-based heuristic; no tokenizer dependency).
- A `system` message is always prepended and is never truncated.
- This strategy is applied in `sessions.py` in a `get_context_messages(session_id, max_messages, max_tokens)` helper that `server.py` calls before each LLM request.
- The strategy is documented in `ORCHESTRATOR_SETUP.md` under "Session History and Context Window".

### Deliverables Checklist

- [ ] `orchestrator_ui/sessions.py` — SQLite schema (sessions + messages tables); `Sessions` and `Messages` classes; `get_context_messages()` truncation helper per strategy above; `SESSION_DB_PATH` env var support (default: `orchestrator_ui/sessions.db`)
- [ ] `orchestrator_ui/server.py` — add routes: `GET /api/sessions`, `POST /api/sessions`, `GET /api/sessions/{id}`, `PATCH /api/sessions/{id}`, `DELETE /api/sessions/{id}`, `POST /api/sessions/{id}/messages`; extend `POST /api/chat` to accept optional `session_id` and append messages post-reply
- [ ] Frontend (`static/index.html` or separate `sessions.js`) — on load: fetch sessions → load latest; session list sidebar (title, updated_at); New Chat button; `localStorage` fallback when SQLite unavailable
- [ ] `sessions.db` added to `.gitignore`
- [ ] `ORCHESTRATOR_SETUP.md` — document truncation strategy, `SESSION_DB_PATH`, `SESSION_CONTEXT_WINDOW`, `SESSION_MAX_TOKENS` env vars
- [ ] Unit tests: create session, append messages, fetch with truncation, delete cascades

### Dependencies

- Phase C is **independent of Phase B**. It can be developed in parallel with Phase B.
- Phase C must complete before Phase D (Phase D stores `ui_spec` in the messages table).

### Effort Estimate

~1.5 days (Lead Engineer: 1 day; Junior Engineer 1: 0.5 days tests + localStorage fallback)

### Owner Roles

- **Lead Engineer**: `sessions.py`, API routes, `POST /api/chat` session_id extension
- **Junior Engineer 1**: Frontend session sidebar and localStorage fallback; unit tests
- **Junior Engineer 2**: `.gitignore` update, `ORCHESTRATOR_SETUP.md` session docs, work log, commit, push

### Acceptance Criteria

1. `POST /api/sessions` returns `{ id, title, created_at }`.
2. `POST /api/chat { messages: [...], session_id: "<id>" }` appends user + assistant messages to the session.
3. `GET /api/sessions/{id}` returns session with all messages (newest first in sidebar; chronological in thread).
4. `DELETE /api/sessions/{id}` cascade-deletes all messages.
5. `SESSION_DB_PATH=/tmp/test.db python server.py` uses the custom path.
6. `get_context_messages()` with 30 messages returns at most 20 (or configured window).
7. Frontend loads most recent session on page load; New Chat button creates a new session.
8. When `sessions.db` write fails, frontend falls back to `localStorage` without crashing.
9. No-breakage smoke test passes (see §2).

---

## 7. Phase D — Dynamic UI Renderer

**Goal:** LLM can return a `ui_spec` JSON payload; the frontend renders 13 component types inline and in a Canvas tab; invalid specs are stripped silently.

### Pre-conditions (must be done before first Phase D commit)

- [ ] `jsonschema>=4.0` added to `requirements.txt` (CTO-4)
- Phase B complete (mode routing needed to know when to prompt for `ui_spec`)
- Phase C complete (messages table must store `ui_spec` column)

### Deliverables Checklist

- [ ] `orchestrator_ui/ui_validator.py` — JSON Schema for `ui_spec` (13 registered component types); URL allowlist check for `video_embed` and `image`; `validate_ui_spec(spec) -> (bool, str)` strip-on-failure
- [ ] `orchestrator_ui/server.py` — extend LLM system prompts for modes where `supports_ui_spec=true` to describe `ui_spec` format; parse `ui_spec` from LLM JSON response; validate via `ui_validator`; emit SSE event `ui_spec.ready { ui_spec: {...} }` after `reply.done`
- [ ] `orchestrator_ui/static/renderer.js` — 13 component renderers (`renderHeading`, `renderText`, `renderCard`, `renderImage`, `renderVideoEmbed`, `renderButton`, `renderCodeBlock`, `renderStatusIndicator`, `renderProgressSteps`, `renderQuizCard`, `renderTable`, `renderStack`, `renderGrid`); `renderSpec(spec, container)`; all text via `.textContent`; **CTO-1: `video_embed` iframe must include `sandbox="allow-scripts allow-same-origin"`**
- [ ] Frontend — inline artifact card in chat thread (small preview + "Open in Canvas" button); Canvas tab (full-width, replaces on new spec); SSE `ui_spec.ready` handler
- [ ] `requirements.txt` — `jsonschema>=4.0` added (CTO-4)
- [ ] Unit tests: validate valid spec passes; invalid component type is stripped; URL not in allowlist is stripped; `video_embed` renderer produces element with `sandbox` attribute

### Dependencies

- Phase B complete (mode routing for `supports_ui_spec`)
- Phase C complete (`ui_spec` stored in messages table)
- `jsonschema>=4.0` in `requirements.txt` (CTO-4) — must exist before first commit

### Effort Estimate

~4 days (Lead Engineer: 2 days backend + server wiring; Junior Engineer 1: 1.5 days renderer.js + Canvas tab + inline card; Junior Engineer 2: 0.5 days tests + work log)

### Owner Roles

- **Lead Engineer**: `ui_validator.py`, system prompt extension, SSE `ui_spec.ready` event
- **Junior Engineer 1**: `renderer.js` (13 renderers), inline artifact card, Canvas tab
- **Junior Engineer 2**: Unit tests (validator + renderer sandbox check), `requirements.txt` update, work log, commit, push

### Acceptance Criteria

1. `validate_ui_spec({ "layout": "stack", "components": [{ "type": "heading", "text": "Hi", "level": 1 }] })` returns `(True, "")`.
2. `validate_ui_spec({ "layout": "stack", "components": [{ "type": "unknown_type" }] })` returns `(False, ...)`.
3. A `video_embed` component with `url: "https://malicious.example.com/video"` is stripped (URL not in allowlist).
4. `renderVideoEmbed({ url: "https://www.youtube.com/watch?v=abc" })` produces an `<iframe>` with `sandbox="allow-scripts allow-same-origin"` set. (CTO-1)
5. `POST /api/chat` for a `chat` mode message returns SSE with `ui_spec.ready` event when the LLM returns a valid `ui_spec`.
6. Invalid `ui_spec` from LLM is stripped; only the plain text `reply` is returned (no crash, no `ui_spec.ready` event).
7. Canvas tab renders the spec full-width when "Open in Canvas" is clicked.
8. All text in rendered components is set via `.textContent`, never `.innerHTML` (code review check).
9. No-breakage smoke test passes (see §2).

---

## 8. Phase E — Embedded Editor and File Operations

**Goal:** Coding mode opens a multi-file diff view; user can accept or reject agent-proposed file changes; `/api/file` read/write is WORKSPACE_ROOT-scoped and secure.

### Pre-conditions (must be done before first Phase E commit)

- `WORKSPACE_ROOT` must be set as an explicit env var; server must raise an error at startup if it is unset (CTO-3)
- Phase B complete (coding mode handler)

### Deliverables Checklist

- [ ] `orchestrator_ui/server.py` — `GET /api/file?path=` and `PUT /api/file { path, content }` with path security (no `..`, no leading `/`, `pathlib.Path.resolve()` prefix check against `WORKSPACE_ROOT`); **CTO-3: startup check — raise `RuntimeError` if `WORKSPACE_ROOT` not set**
- [ ] `orchestrator_ui/static/editor.js` — CodeMirror 6 multi-file tabs: one `EditorState` per open file (`Map<path, EditorState>`); tab bar UI with close/switch; `openFile(path, content, proposed_content)` with `@codemirror/merge` diff view when `proposed_content` is set
- [ ] Coding mode handler in `server.py` — parse `file_operations` from LLM JSON; validate paths; emit SSE `file_operations.ready { file_operations: [...] }`; `GET /api/file` for each path to load current content for diff
- [ ] Frontend accept/reject UI — "Accept File", "Accept All", "Reject" buttons per diff tab; Accept → `PUT /api/file`; Reject → discard `EditorState`
- [ ] `orchestrator_ui/.env.example` — add `WORKSPACE_ROOT` (required for `/api/file`; document that it must be an absolute path)
- [ ] `ORCHESTRATOR_SETUP.md` — document `WORKSPACE_ROOT` requirement and startup error
- [ ] Unit tests: path traversal blocked (`../etc/passwd` → 400); valid relative path read/write succeeds; `file_operations` with `..` in path is rejected before disk access
- [ ] Ghost text (L3) is explicitly **excluded** from this phase. No `@marimo-team/codemirror-ai` package (CTO Q6).

### Dependencies

- Phase B complete (coding mode dispatch in `server.py`)
- `WORKSPACE_ROOT` env var documented and enforced (CTO-3)

### Effort Estimate

~1 week / 5 days (Lead Engineer: 2 days backend file routes + coding handler; Junior Engineer 1: 2 days `editor.js` multi-file tabs + diff view + accept/reject UI; Junior Engineer 2: 1 day tests + `.env.example` + SETUP.md + work log)

### Owner Roles

- **Lead Engineer**: `/api/file` routes (GET/PUT) with security, coding mode handler, `WORKSPACE_ROOT` startup check
- **Junior Engineer 1**: `editor.js` (multi-file tabs, `@codemirror/merge` diff view, accept/reject UI)
- **Junior Engineer 2**: Path traversal unit tests, `.env.example`, `ORCHESTRATOR_SETUP.md`, work log, commit, push

### Acceptance Criteria

1. Server raises `RuntimeError: WORKSPACE_ROOT env var is required` at startup when `WORKSPACE_ROOT` is unset. (CTO-3)
2. `GET /api/file?path=../etc/passwd` returns HTTP 400 "Path traversal not allowed".
3. `GET /api/file?path=/absolute/path` returns HTTP 400.
4. `PUT /api/file { "path": "todo.py", "content": "# hello" }` writes the file within `WORKSPACE_ROOT`.
5. Coding mode: `POST /api/chat` with `"code a todo app"` returns SSE `file_operations.ready` with at least one entry.
6. Frontend opens a diff view tab for each proposed file operation.
7. "Accept All" button triggers `PUT /api/file` for each pending operation.
8. "Reject" discards the proposed content without writing to disk.
9. Multi-file tab bar correctly switches between open files.
10. No `@marimo-team/codemirror-ai` or ghost text code is present. (CTO Q6)
11. No-breakage smoke test passes (see §2).

---

## 9. Phase F — PWA Packaging

**Goal:** The unified app can be installed to Android home screen via "Add to Home Screen" (PWA); no Capacitor APK (CTO Q4 decision).

### Deliverables Checklist

- [ ] `orchestrator_ui/static/manifest.json` — `name`, `short_name`, `start_url: "/"`, `display: "standalone"`, `background_color`, `theme_color`, `icons` (at least 192×192 and 512×512 PNG)
- [ ] `orchestrator_ui/static/sw.js` — service worker: cache app shell (HTML, CSS, JS, icons) on install; serve from cache on fetch; offline fallback page (`offline.html`)
- [ ] `orchestrator_ui/static/index.html` — add `<link rel="manifest" href="/static/manifest.json">` and `<meta name="theme-color">` tags; register service worker in JS
- [ ] `orchestrator_ui/static/offline.html` — minimal offline fallback page
- [ ] `ORCHESTRATOR_SETUP.md` — add PWA section: HTTPS requirement for production install, `localhost` works for local dev, Cloudflare Tunnel suggestion for remote access
- [ ] Icons: at minimum placeholder 192×192 and 512×512 PNG icons in `static/icons/`

### Dependencies

- No hard dependency on other phases; can be done any time the frontend is stable.
- Recommended: do after Phase D (Canvas tab UI is settled) to avoid re-caching stale assets.

### Effort Estimate

4–8 hours (Junior Engineer 1: manifest + icons; Junior Engineer 2: service worker + offline page + SETUP.md note)

### Owner Roles

- **Junior Engineer 1**: `manifest.json`, icons, `<link rel="manifest">` in HTML
- **Junior Engineer 2**: `sw.js` (cache strategy), `offline.html`, `ORCHESTRATOR_SETUP.md` PWA section, work log, commit, push

### Acceptance Criteria

1. `GET /static/manifest.json` returns a valid PWA manifest (name, icons, display: standalone).
2. Chrome DevTools > Application > Manifest shows no errors.
3. Chrome DevTools > Application > Service Workers shows the SW registered and active.
4. With network offline, navigating to the app serves the cached shell (not a browser error page).
5. On Android Chrome (or iOS Safari), "Add to Home Screen" is offered.
6. No Capacitor, no native APK, no `npm install @capacitor/*` present. (CTO Q4)
7. No-breakage smoke test passes (see §2).

---

## 10. Parallelization Map

```
Timeline →

Phase A (Local LLM)       ████████ (2 days)
Phase C (Sessions)        ████  (1.5 days, concurrent with A)
                               ↓ A + C complete
Phase B (Mode Registry)        ████████ (2 days)
                                        ↓ B complete
Phase D (Dynamic UI)                    ████████████████ (4 days)
Phase E (Editor)                        ████████████████████ (5 days, concurrent with D)
Phase F (PWA)                    ████ (0.5 days, any time after Phase D frontend settles)
```

### Dependency Rules

| Phase | Can start when... | Can run in parallel with... |
|-------|-------------------|-----------------------------|
| A | Immediately (no deps) | C |
| B | A complete | — |
| C | Immediately (no deps) | A |
| D | B + C complete; `jsonschema>=4.0` in requirements | E (after B), F |
| E | B complete; `WORKSPACE_ROOT` enforcement ready | D, F |
| F | Frontend stable (recommend after D) | — |

### Key Parallelism Opportunities

- **A ∥ C**: Local LLM and session persistence are fully independent. Two engineers can develop these simultaneously on separate worktrees of the same branch.
- **D ∥ E**: Once Phase B is done, Dynamic UI renderer and the embedded editor have no shared files and can be developed concurrently (different files: `ui_validator.py` + `renderer.js` vs `editor.js` + `/api/file`).
- **F**: PWA is a thin layer; it can be slotted in by a junior engineer during any quiet period after Phase D.

---

## 11. Module Dependency Graph

```
                    ┌─────────────────────┐
                    │  server.py (entry)  │
                    │  (POST /api/chat,   │
                    │   /api/sessions/*,  │
                    │   /api/file)        │
                    └────────┬────────────┘
                             │ imports
              ┌──────────────┼──────────────────────┐
              ▼              ▼                       ▼
    ┌──────────────┐  ┌─────────────┐     ┌──────────────────┐
    │ intent.py    │  │ sessions.py │     │ ui_validator.py  │
    │ detect_mode()│  │ (SQLite)    │     │ (jsonschema)     │
    │ detect_intent│  └─────────────┘     └──────────────────┘
    └──────┬───────┘         ▲                     ▲
           │                 │ used by              │ used by
           ▼                 │ /api/chat            │ /api/chat
    ┌──────────────┐         │                     │
    │  modes.py    │─────────┘                     │
    │  modes.json  │                               │
    └──────┬───────┘                               │
           │ mode dispatch                         │
    ┌──────▼───────────────────────────────────────┴──┐
    │           llm_provider.py                        │
    │   (anthropic | openai | local → Ollama)          │
    └──────────────────────┬───────────────────────────┘
                           │ calls
                    ┌──────▼──────┐
                    │  Ollama     │
                    │  :11434     │
                    │  (local)    │
                    └─────────────┘

Frontend modules (static/):
    index.html
        ├── renderer.js      (ui_spec → DOM; depends on: none)
        ├── editor.js        (CodeMirror multi-file; depends on: @codemirror/merge)
        └── sw.js            (service worker; depends on: none)

External services (unchanged):
    youtube-shorts-generator/ :8766   ← proxy only from video_handler in server.py
    mcp-server/server.py (Stdio)      ← untouched; used by brain.py
    brain.py / context_loader.py      ← untouched; called from /api/chat orchestration mode
```

### File Ownership Map (New and Modified)

```
agent-automation/
├── orchestrator_client/
│   ├── llm_provider.py       MODIFIED  Phase A  (add local branch)
│   └── intent.py             MODIFIED  Phase B  (add detect_mode, keep detect_intent shim)
└── orchestrator_ui/
    ├── server.py             MODIFIED  Phases B, C, D, E  (additive: new routes, handlers)
    ├── modes.py              NEW       Phase B
    ├── modes.json            NEW       Phase B
    ├── sessions.py           NEW       Phase C
    ├── ui_validator.py       NEW       Phase D
    ├── .env.example          MODIFIED  Phases A, C, E  (new env vars)
    └── static/
        ├── renderer.js       NEW       Phase D
        ├── editor.js         NEW       Phase E
        ├── manifest.json     NEW       Phase F
        ├── sw.js             NEW       Phase F
        ├── offline.html      NEW       Phase F
        └── icons/            NEW       Phase F

Unchanged (zero modifications permitted):
    youtube-shorts-generator/
    agent-automation/mcp-server/
    agent-automation/orchestrator_client/brain.py
    agent-automation/orchestrator_client/context_loader.py
    .cursor/rules/, .cursor/skills/
    workflow.yml, roles.yml
```

---

## 12. Single-Branch Strategy

All implementation work uses **one feature branch** off `staging`:

```
git checkout staging
git fetch origin && git reset --hard origin/staging
git checkout -b feature/holistic-agent-platform
```

### Merge Cadence

Merge to `staging` after **each phase's tests pass** (not after every commit). Do not merge a partial phase.

| Phase | Merge trigger |
|-------|--------------|
| A | Phase A acceptance criteria all pass |
| C | Phase C acceptance criteria all pass |
| B | Phase B acceptance criteria all pass (requires A merged first) |
| D | Phase D acceptance criteria all pass (requires B + C merged first; `jsonschema>=4.0` present) |
| E | Phase E acceptance criteria all pass (requires B merged first) |
| F | Phase F acceptance criteria all pass |

### Merge Procedure (per git-workflow rules)

1. All phase tests pass on `feature/holistic-agent-platform`.
2. No-breakage smoke test passes (§2).
3. Junior Engineer 1 or 2 creates PR: `feature/holistic-agent-platform → staging`.
4. PR is reviewed and squash-merged on GitHub.
5. Post-merge cleanup:
   ```
   git branch -D feature/holistic-agent-platform
   git push origin --delete feature/holistic-agent-platform
   git fetch origin && git reset --hard origin/staging
   ```
6. Cut a new `feature/holistic-agent-platform` branch from the updated `staging` for the next phase:
   ```
   git checkout staging
   git checkout -b feature/holistic-agent-platform
   ```

### Constraints

- Direct push to `staging` or `master` is blocked (branch protection).
- All work goes through PRs.
- One PR per phase (or sub-phase if a phase is large).
- Never merge a stale branch after squash-merge; always cut fresh from `origin/staging`.

---

## 13. Acceptance Criteria Master List

| Phase | One-liner |
|-------|-----------|
| **A** | `ORCHESTRATOR_LLM_PROVIDER=local` routes to Ollama; 503 when Ollama is down; existing anthropic/openai paths unchanged. |
| **B** | `detect_mode()` returns correct mode for all 5 modes; `detect_intent()` shim works; `POST /api/chat` dispatches to correct handler. |
| **C** | Sessions survive page reload; truncation window enforced; localStorage fallback works; `SESSION_DB_PATH` configurable. |
| **D** | Valid `ui_spec` renders inline + Canvas; invalid spec stripped silently; `video_embed` iframe has `sandbox` attribute; `jsonschema>=4.0` in requirements. |
| **E** | `/api/file` rejects path traversal; multi-file tabs + diff view work; accept/reject writes or discards; `WORKSPACE_ROOT` required at startup. |
| **F** | PWA manifest valid; service worker caches shell; offline fallback works; "Add to Home Screen" offered on Android. |

---

## 14. Risk Register

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|-----------|
| R1 | Ollama cold-start latency (10–30s for 12B models) surprises users | Medium | Medium | Document in ORCHESTRATOR_SETUP.md; consider `ollama pull` pre-run in server startup script |
| R2 | LLM returns malformed `ui_spec` JSON frequently | Medium | Low | `ui_validator` strip-on-failure guarantees graceful degradation to plain text |
| R3 | Path traversal vulnerability in `/api/file` | Low | High | `pathlib.resolve()` + `WORKSPACE_ROOT` prefix check; unit test covers `../` and absolute paths |
| R4 | Session message history exceeds context window mid-conversation | Medium | Medium | Sliding window strategy defined in Phase C (§6); env var configurable |
| R5 | `detect_mode()` over-matches keywords (e.g. "code" in a casual message) | Medium | Low | Confidence threshold < 0.6 → `"chat"` default; easy to tune `modes.json` trigger_keywords |
| R6 | Phase D breaks existing `/api/chat` behavior | Low | High | Additive changes only; new params optional; no-breakage smoke test per phase |
| R7 | `@codemirror/merge` npm dependency version conflict | Low | Low | Pin exact version; test in isolation before Phase E merge |
| R8 | YouTube Shorts proxy timeout causes unified app hang | Low | Medium | Set explicit timeout on `video_handler` HTTP proxy call; return 503 `status_indicator` on timeout |
| Video mode cloud dependency | Medium | High | Until Phase G (local video pipeline), video mode sends data to OpenAI, ElevenLabs, Runway, YouTube. Mitigation: UI banner warning users; Phase G scoped as future work; no video mode in privacy-critical deployments until Phase G is complete. |

---

*Project Plan produced by PM. Based on approved ARCHITECTURE.md v1.0 (CTO Approval #002). Ready for User review and development sign-off.*

---

## Section 15: Phase G — Local-Only Video Pipeline (Future)

**Goal:** Replace all cloud API calls in the video pipeline with locally hosted equivalents so the entire unified app operates without any external data dependencies.

**Deliverables:**
- [ ] Research and select local TTS (Coqui TTS, Kokoro, or Piper) to replace ElevenLabs
- [ ] Research and select local video generation (AnimateDiff or comparable) to replace Runway
- [ ] Replace OpenAI/Anthropic calls in `youtube-shorts-generator` with Ollama local LLM
- [ ] Local YouTube proxy or optional manual upload (replacing YouTube API) — user decides
- [ ] `video_handler` proxy interface preserved; only `youtube-shorts-generator` internals change
- [ ] Acceptance: full video generated end-to-end with `OLLAMA_ONLY=true`, no cloud API key required

**Dependencies:** Phases A–E stable; user approves scope.  
**Effort estimate:** 3–6 weeks (research-heavy; local video generation is the hardest part).  
**Owner roles:** Researcher (TTS and video options), Architect (design), Lead Engineer + Junior Engineers (implementation).  
**Note:** This phase is not blocked on any phase except A–E being stable. It can be scoped and started independently once the team has bandwidth. Video mode remains cloud-dependent until this phase is complete. UI must show a warning banner to users.
