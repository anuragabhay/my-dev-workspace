# Custom Vibe Coding IDE — Architecture Roadmap

**Initiative:** Custom Vibe Coding IDE  
**Vision:** Custom vibe coding IDE with project structure, agent/chat, reasoning panel, code editor, in-process MCP server, full control over rules/skills/hooks, **streaming chat**.

**References:** `custom-ide-research.md`, `orchestrator-ui-research.md`, `orchestrator_ui/`, `mcp-server/`, `orchestrator_client/`

---

## Executive Summary

This roadmap defines a phased path from the current Orchestrator UI to a full custom vibe coding IDE. Each phase builds on the previous, with clear scope, tech choices, and alternatives. The approach favors **incremental enhancement** of the existing web stack (FastAPI + static frontend) before considering a full IDE shell.

---

## Cross-Cutting Tech Choices

### Desktop vs Web Shell

| Option | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| **Web-only (Phases 1–3)** | No install; reuse FastAPI; shareable; fastest path | Limited local FS; no native feel | **Default for Phases 1–3** |
| **Electron** | Full desktop; Monaco; extensions; Cursor/Windsurf pattern | Heavier; multi-process; longer build | **Phase 4** if full IDE shell needed |
| **Tauri** | Lighter than Electron; Rust core | Smaller IDE ecosystem; less Monaco integration | **Alternative** if bundle size critical |

**Decision:** Start web-only. Revisit Electron/Tauri in Phase 4 when full IDE shell is scoped.

### Editor: Monaco vs CodeMirror

| Editor | Best For | Pros | Cons |
|--------|----------|------|------|
| **Monaco** | Desktop IDE, full features | LSP, extensions, VS Code parity | Heavier; Electron-friendly |
| **CodeMirror** | Web-first, lightweight | Modular; good for web; Bolt.new uses it | Fewer extensions |

**Decision:** **CodeMirror** for web-only Phases 2–3 (embedded in Orchestrator UI). **Monaco** if we move to Electron in Phase 4.

### MCP: Stdio vs In-Process

| Transport | Current | Phase 1–3 | Phase 4 (Full IDE) |
|----------|---------|-----------|---------------------|
| **Stdio** | `mcp-server/server.py` subprocess | Keep; UI backend spawns subprocess or uses Cursor MCP | Same |
| **In-process** | N/A | Optional bridge | Embed MCP server in IDE process |

**Decision:** Stdio for Phases 1–3. In-process MCP in Phase 4 if IDE runs as a single process (Electron main or Tauri).

### Streaming: Anthropic + FastAPI SSE

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **LLM streaming** | Anthropic `messages.stream()` | Native streaming; `stream=True` returns async iterator |
| **HTTP transport** | FastAPI `StreamingResponse` + `text/event-stream` | Standard SSE; works with `EventSource` in browser |
| **Protocol** | Custom SSE events or Vercel AI SDK–style | Design for `flow.proposal`, `flow.critique`, `flow.synthesis`, `reply.chunk` |

**Decision:** Anthropic streaming API + FastAPI `StreamingResponse` for SSE. No Vercel AI SDK dependency for backend; frontend may use `EventSource` or fetch with ReadableStream.

---

## Phase 1: MCP Integration + Streaming in Current Orchestrator UI

**PM Feasibility:** See `custom-ide-phase1-feasibility.md` for feasibility, blockers, MVP acceptance criteria, and scope boundaries.

### Scope

- **Brain gets real context from MCP** — Replace stub context with live MCP tool calls (workspace status, tasks, roles, workflow config).
- **Chat and orchestration responses stream in real time** — SSE for both chat and orchestration modes.

### Deliverables

1. **MCP client in Orchestrator UI backend**
   - Connect to `mcp-server` via Stdio (spawn subprocess) or use MCP when provided by environment (e.g. Cursor).
   - Call `get_workspace_status`, `get_pending_orchestrator_prompt`, `get_workflow_config`, `list_roles` at cycle start.
   - Fallback to stub context when MCP unavailable.

2. **Streaming API**
   - `POST /api/chat` with `Accept: text/event-stream` → SSE stream.
   - Events: `flow.proposal`, `flow.critique`, `flow.synthesis`, `reply.chunk`, `reply.done`.
   - Chat mode: `reply.chunk`, `reply.done` only.
   - Non-streaming: keep current JSON response when `Accept: application/json`.

3. **Frontend updates**
   - Use `EventSource` or `fetch` + ReadableStream to consume SSE.
   - Append chunks to assistant message in real time.
   - Stream reasoning (proposal, critique, synthesis) into Reasoning panel as they arrive.

### Dependencies

- Anthropic Python SDK with `messages.stream()`.
- MCP Python SDK (already used by `mcp-server`).
- `orchestrator_client.brain`: refactor to support streaming (yield proposal → critique → synthesis → final chunks).

### Tech Choices

| Area | Choice | Notes |
|------|--------|-------|
| **MCP connection** | Stdio subprocess from FastAPI | Spawn `mcp-server` as subprocess; use MCP client to call tools. Alternative: Cursor injects MCP; UI uses when available. |
| **Streaming** | Anthropic `stream=True` + FastAPI `StreamingResponse` | `StreamingResponse(iterable, media_type="text/event-stream")` |
| **SSE format** | `data: {"type":"flow.proposal","content":"..."}\n\n` | JSON per event; frontend parses and routes to UI regions |

### Alternatives Considered

- **WebSocket instead of SSE:** Rejected for Phase 1; SSE is simpler, one-way, sufficient for streaming responses.
- **Vercel AI SDK:** Rejected for backend; adds dependency; our stack is Python/FastAPI. Frontend could use `useChat`-style hook if we adopt React later.
- **MCP via HTTP/SSE:** Deferred; Stdio is sufficient when UI and MCP run on same machine.

---

## Phase 2: Project Structure Panel

### Scope

- **File tree** — Explorer-style panel showing workspace directory structure.
- **Integration** — Click file → future editor (Phase 3) or open in external app.
- **Virtualization** — Handle large repos (1000+ files) without lag.

### Deliverables

1. **Project structure API**
   - `GET /api/tree?path=` — Return directory tree (lazy or full, configurable depth).
   - Optional: `GET /api/file?path=` — Read file content for preview.

2. **File tree component**
   - Collapsible folders; file icons by extension.
   - Root = `WORKSPACE_PATH` or `get_workspace_root()`.
   - Virtualized list (e.g. `react-window`, `@tanstack/react-virtual`, or vanilla IntersectionObserver) for performance.

3. **Layout**
   - Sidebar: Project tree (left) + optional Reasoning panel (right).
   - Main: Chat thread. Reserve space for editor in Phase 3.

### Dependencies

- Phase 1 (streaming + MCP) complete.
- Workspace root resolution (`workspace_config.get_workspace_root()`).

### Tech Choices

| Area | Choice | Notes |
|------|--------|-------|
| **Tree API** | FastAPI endpoint; `pathlib` walk | Return JSON: `{ name, path, type: "file"|"dir", children? }` |
| **Frontend** | Vanilla JS or lightweight framework | Match current `orchestrator_ui` static (no React/Vue unless we adopt in Phase 1) |
| **Virtualization** | `@tanstack/react-virtual` or similar | If we add React; else CSS `overflow: auto` + limit initial load |

### Alternatives Considered

- **Full tree in one request:** May be slow for large repos. Prefer lazy loading: expand folder → fetch children.
- **WebSocket for file watcher:** Deferred; polling or manual refresh sufficient for MVP.

---

## Phase 3: Code Editor Integration

### Scope

- **Embedded code editor** — View and edit files in-app.
- **Sync with project tree** — Click file in tree → open in editor.
- **Basic editing** — Syntax highlighting, save, revert.

### Deliverables

1. **Editor component**
   - CodeMirror 6 embedded in main content area.
   - Syntax highlighting via CodeMirror language packages.
   - Tabs or single-file view.

2. **File read/write API**
   - `GET /api/file?path=` — Read file content.
   - `PUT /api/file` — Write file (with optional backup).

3. **Integration**
   - Project tree click → `GET /api/file` → render in editor.
   - Save button → `PUT /api/file` → update tree if needed.

### Dependencies

- Phase 2 (project structure) complete.
- CodeMirror 6 + language packages.

### Tech Choices

| Area | Choice | Notes |
|------|--------|-------|
| **Editor** | **CodeMirror 6** | Lighter than Monaco; works in browser; Bolt.new uses it |
| **Languages** | `@codemirror/lang-python`, `@codemirror/lang-javascript`, etc. | Add as needed |
| **Bundling** | ES modules, Vite or similar | If we add build step; else script tags for minimal setup |

### Alternatives Considered

- **Monaco:** Heavier; better for full IDE. Defer to Phase 4 if we go Electron.
- **Ace Editor:** Older; CodeMirror 6 is more modern and modular.
- **iframe to external editor:** Rejected; we want in-app editing.

---

## Phase 4: Full IDE Shell (Layout, MCP In-Process)

### Scope

- **Unified IDE shell** — Single application: project tree, chat, reasoning, editor, optional terminal.
- **In-process MCP server** — MCP runs inside IDE process; no subprocess for Stdio.
- **Layout persistence** — Save panel sizes, positions.

### Deliverables

1. **Shell decision**
   - **Option A:** Continue web-only with enhanced layout (resizable panels, persistence).
   - **Option B:** Electron app wrapping web UI + Node MCP client; or Tauri + webview.

2. **In-process MCP**
   - If Electron: Run MCP server in main process (Python bridge via `child_process` or Node MCP SDK if we port tools).
   - If Tauri: Rust MCP or spawn Python; bridge to webview.
   - If web-only: Keep Stdio; "in-process" means same machine, not same process.

3. **Layout**
   - Resizable panels: Project | Chat+Editor | Reasoning.
   - Optional: Terminal panel (xterm.js or similar).

### Dependencies

- Phases 1–3 complete.
- Decision: web-only vs Electron vs Tauri.

### Tech Choices

| Area | Choice | Notes |
|------|--------|-------|
| **Shell** | **Web-first** unless desktop required | Electron if: need native FS, extensions, or Cursor-like UX |
| **MCP in-process** | Python in Electron main, or Node port of tools | MCP Python SDK runs in subprocess; "in-process" = same app, possibly same process via bridge |
| **Layout** | CSS Grid + resize handles, or library (e.g. `react-resizable-panels`) | Persist to localStorage or config file |

### Alternatives Considered

- **Fork Bolt.new:** Add MCP, reasoning panel. Pros: WebContainers, CodeMirror. Cons: Remix stack; significant fork effort.
- **Fork Flexpilot:** Add orchestrator flow. Pros: VS Code base, Monaco. Cons: High effort; GPL.
- **Tauri over Electron:** Lighter binary; evaluate if bundle size matters.

---

## Phase 5: Custom User Actions and Rules

### Scope

- **Custom rules** — User-defined rules (e.g. `.cursor/rules/*.mdc`) loaded and applied.
- **Custom skills** — User-defined skills (e.g. `.cursor/skills/*/SKILL.md`) available to agents.
- **Custom hooks** — Pre/post cycle hooks; custom slash commands.
- **User actions** — Buttons or shortcuts that trigger defined workflows.

### Deliverables

1. **Rules engine**
   - Load rules from workspace config path.
   - Inject into system prompt or context for brain/orchestrator.

2. **Skills registry**
   - Discover skills from `.cursor/skills/` or config.
   - Expose to agent as tool or context.

3. **Hooks**
   - Lifecycle hooks: `before_cycle`, `after_cycle`, `before_delegate`, `after_delegate`.
   - Configurable in `workflow.yml` or separate hooks config.

4. **User actions UI**
   - Configurable buttons: "Run cycle", "Delegate to X", custom commands.
   - Optional: User-defined actions in config.

### Dependencies

- Phase 4 (or Phase 3 if we stay web-only).
- `workflow.yml`, `roles.yml`, `decisions.yml` already exist; extend for hooks.

### Tech Choices

| Area | Choice | Notes |
|------|--------|-------|
| **Rules** | File-based; glob `*.mdc` | Same format as Cursor rules |
| **Skills** | Directory-based; `SKILL.md` per skill | Same as current `.cursor/skills/` |
| **Hooks** | Python callbacks or subprocess | Config lists hook scripts; server invokes |

### Alternatives Considered

- **Rules in database:** Overkill for single-user; file-based is sufficient.
- **Plugin system:** Deferred; hooks + config cover MVP.

---

## Roadmap Summary

| Phase | Scope | Key Tech | Deps |
|-------|-------|----------|------|
| **1** | MCP + streaming in Orchestrator UI | Anthropic stream, FastAPI SSE, MCP Stdio | — |
| **2** | Project structure panel | FastAPI tree API, virtualized file tree | Phase 1 |
| **3** | Code editor integration | CodeMirror 6, file read/write API | Phase 2 |
| **4** | Full IDE shell | Web vs Electron; in-process MCP | Phases 1–3 |
| **5** | Custom rules, skills, hooks | File-based rules, skills, hooks config | Phase 4 (or 3) |

---

## Implementation Order

1. **Phase 1** — Highest impact: real MCP context + streaming UX. Unblocks "brain gets real context" and "streaming chat" from vision.
2. **Phase 2** — Project tree is independent of Phase 1; can parallelize after Phase 1 API shape is stable.
3. **Phase 3** — Depends on Phase 2 (tree → editor click).
4. **Phase 4** — After 1–3, reassess: stay web or go Electron.
5. **Phase 5** — Enhances all phases; can start in parallel with Phase 4.

---

## References

- [Anthropic Streaming](https://docs.anthropic.com/en/api/streaming)
- [FastAPI StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [MCP Architecture](https://modelcontextprotocol.io/docs/concepts/architecture)
- [CodeMirror 6](https://codemirror.net/)
- [Vercel AI SDK Stream Protocol](https://sdk.vercel.ai/docs/ai-sdk-ui/stream-protocol)
- `custom-ide-research.md` — Platform synthesis, options
- `orchestrator-ui-research.md` — Intent, API design, streaming design

---

*Architecture roadmap produced for Custom Vibe Coding IDE initiative. Next: Lead Engineer to implement Phase 1 (MCP integration + SSE streaming).*
