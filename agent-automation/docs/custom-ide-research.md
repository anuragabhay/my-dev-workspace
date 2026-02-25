# Custom Vibe Coding IDE — Research Memo

**Initiative:** Custom Vibe Coding IDE  
**Vision:** Build a custom vibe coding IDE (like Cursor) with project structure, agent/chat window, reasoning panel, code editor, in-process MCP server, full control over rules/skills/hooks, and **streaming chat**.

**References:** `agent-automation/orchestrator_ui`, `agent-automation/mcp-server`, `agent-automation/orchestrator_client`, `orchestrator_patterns.md`, `workflow.yml`, `docs/orchestrator-ui-research.md`

---

## 1. Executive Summary

This memo synthesizes research on existing vibe coding platforms (Cursor, Replit Agent, v0, Bolt.new, Codeium/Windsurf) and open-source alternatives. It documents architecture, tech stacks, and implementation patterns for project structure, chat/agents, reasoning panels, editors, MCP/tool layers, and streaming. It concludes with options for building our own IDE and recommendations.

---

## 2. Platforms Inspected

### 2.1 Cursor

| Aspect | Details |
|--------|---------|
| **Architecture & Tech Stack** | Multi-process **Electron** app. Processes: Main, Renderer, Extension Host, Shared, Worker, Pty Host, File Watcher. IPC-based coordination. |
| **(a) Project structure** | File tree integrated via VS Code–style Explorer; Monaco-based. |
| **(b) Chat/agents** | Chat as primary surface; Composer for agent mode; tool calls behind the scenes. |
| **(c) Reasoning** | Collapsible panels; reasoning/thinking often inline or in expandable sections. |
| **(d) Editor** | **Monaco** (VS Code editor). Embedded in renderer process. |
| **(e) MCP/tool layer** | **MCP native.** Supports Stdio (local), SSE (remote), Streamable HTTP. Tools exposed via `.cursor/mcp.json`. |
| **(f) Streaming** | **SSE** and Streamable HTTP for chat/LLM responses. Cursor uses `streamableHttp` type for remote MCP. |

**Open Source:** Core Cursor repo is on GitHub (getcursor/cursor); AI integration details are proprietary. Built on VS Code / VSCodium foundation.

---

### 2.2 Replit Agent

| Aspect | Details |
|--------|---------|
| **Architecture & Tech Stack** | **Web-based** (Replit IDE). Multi-agent architecture: Manager, Editor, Verifier agents. ReAct-style agent loop. |
| **(a) Project structure** | File tree in web IDE; integrated with Replit’s cloud filesystem. |
| **(b) Chat/agents** | Chat-first; animated agent icon during work; planning phase feedback. |
| **(c) Reasoning** | Progress shown during agent work; planning/verification phases visible. |
| **(d) Editor** | Web-based code editor (Monaco or similar). |
| **(e) MCP/tool layer** | Constrained to Replit environment; no public MCP. Uses internal tool layer for file ops, run, deploy. |
| **(f) Streaming** | Streaming responses; model stack includes Claude 3.5 Sonnet. |

**Notes:** Agent 3 adds app testing in browser, Max Autonomy mode, agent/automation generation. Not open source; architecture inferred from blog/docs.

---

### 2.3 v0 (Vercel)

| Aspect | Details |
|--------|---------|
| **Architecture & Tech Stack** | **Next.js + React.** Fine-tuned model (`v0-1.0-md`). Tailwind, Shadcn UI. |
| **(a) Project structure** | Not a full IDE; prompt → build → publish. Design Mode for visual refinement. |
| **(b) Chat/agents** | Chat-driven; conversational refinement; templates. |
| **(c) Reasoning** | Minimal; focused on component synthesis. |
| **(d) Editor** | Preview/code view; not a full code editor. |
| **(e) MCP/tool layer** | API at `api.v0.dev`; OpenAI Chat Completions format; tool calling supported. |
| **(f) Streaming** | **Streaming** via Vercel AI SDK; low-latency output. |

**Notes:** UI builder, not a general IDE. Good reference for streaming + chat patterns.

---

### 2.4 Bolt.new (StackBlitz)

| Aspect | Details |
|--------|---------|
| **Architecture & Tech Stack** | **Web-only.** Remix frontend, Vercel AI SDK, **CodeMirror** editor, **xterm** terminal, **WebContainers** (WASM Node.js in browser). |
| **(a) Project structure** | File tree + editor + terminal + preview in single interface. |
| **(b) Chat/agents** | Chat primary; “enhance prompt” before submit; batch instructions. |
| **(c) Reasoning** | Minimal; AI streams file ops. |
| **(d) Editor** | **CodeMirror** (not Monaco). |
| **(e) MCP/tool layer** | No MCP. Orchestration layer: LLM → atomic file ops (create/update/delete) → WebContainer VFS. Auto `npm install` on `package.json` changes. |
| **(f) Streaming** | **Vercel AI SDK** streaming; file operations streamed as atomic ops. |

**Open Source:** Yes (stackblitz/bolt.new). Strong reference for browser-based AI IDE with WebContainers.

---

### 2.5 Codeium / Windsurf

| Aspect | Details |
|--------|---------|
| **Architecture & Tech Stack** | **Electron** (Windsurf). Custom infrastructure; parallel LLM processing; vLLM, FastAPI. |
| **(a) Project structure** | VS Code–style Explorer; full codebase context. |
| **(b) Chat/agents** | **Cascade** agent system; multi-file editing; real-time collaboration. |
| **(c) Reasoning** | Context-aware; Tab autocomplete; “Tab to Jump,” “Tab to Import.” |
| **(d) Editor** | **Monaco**; VS Code–compatible keybindings; Cursor extensions. |
| **(e) MCP/tool layer** | **MCP servers** extend agent capabilities. |
| **(f) Streaming** | Streaming for completions and chat. |

**Notes:** Windsurf = Codeium’s AI-native IDE. Claude for reasoning; custom model for Tab. Not open source.

---

### 2.6 Other Relevant Projects

| Project | Type | Notes |
|---------|------|-------|
| **Flexpilot IDE** | VS Code fork | Open source, MIT/GPL. Bring-your-own-LLM. Panel/inline/terminal chat. Monaco. |
| **codemirror-ai** (marimo-team) | CodeMirror extension | AI inline editing, next-edit prediction, prompt history. Apache 2.0. |
| **Code Web Chat** | GPL-3.0 tool | Streaming from multiple providers; works with VS Code family. |
| **VSCodium** | VS Code build | Open-source VS Code; base for Cursor, Windsurf. |

---

## 3. Synthesis by Dimension

### 3.1 Architecture & Tech Stack

| Approach | Examples | Pros | Cons |
|----------|----------|------|------|
| **Electron** | Cursor, Windsurf, Flexpilot | Full desktop IDE; native feel; Monaco; extensions | Heavier; multi-process complexity |
| **Web-only** | Bolt.new, Replit, v0 | No install; shareable; WebContainers | Limited to browser; no local FS by default |
| **Tauri** | (emerging) | Lighter than Electron; Rust core | Smaller ecosystem for IDE features |

### 3.2 Project Structure (a)

- **Pattern:** File tree (Explorer) + editor tabs + optional sidebar.
- **Implementation:** Tree component (virtualized for large repos) + file watcher.
- **Workspace reference:** `agent-automation` uses `get_workspace_root()`; PROJECT_WORKSPACE.md as state.

### 3.3 Chat / Agents (b)

- **Pattern:** Chat-first; agent mode with tool calls; slash commands.
- **Workspace reference:** `orchestrator_ui` has chat + orchestration modes; `intent.py` for slash commands; `roles.yml` for role list.

### 3.4 Reasoning (c)

- **Patterns:** Collapsible sidebar (proposal, critique, synthesis); inline expandable; progress indicators.
- **Workspace reference:** `run_brain_with_flow` returns `proposal`, `critique`, `synthesis`, `final_decision`; UI shows flow in sidebar.

### 3.5 Editor (d)

| Editor | Used By | Pros | Cons |
|--------|---------|------|------|
| **Monaco** | Cursor, Windsurf, Flexpilot, VS Code | Full-featured; extensions; LSP | Heavier; Electron-friendly |
| **CodeMirror** | Bolt.new, marimo | Lighter; modular; good for web | Fewer extensions than Monaco |

**Recommendation:** Monaco for desktop IDE; CodeMirror for web-first or lightweight builds.

### 3.6 MCP / Tool Layer (e)

| Transport | Use Case | Workspace |
|-----------|----------|-----------|
| **Stdio** | Local subprocess (Python, Node) | `mcp-server/server.py` uses `stdio_server()` |
| **SSE** | Remote HTTP streaming | Cursor supports; MCP spec |
| **Streamable HTTP** | Cloud-hosted MCP | Cursor, MCP spec |

**In-process MCP:** MCP SDKs (Python, TypeScript) support servers in the same process. Our `mcp-server` runs as subprocess via Stdio; in-process would require embedding the server in the IDE process (e.g., Python bridge or Node MCP client in Electron).

### 3.7 Streaming (f)

| Approach | Examples | Implementation |
|----------|----------|----------------|
| **SSE** | Cursor, v0, Vercel AI SDK | `text/event-stream`; chunked tokens |
| **Vercel AI SDK** | Bolt.new, v0 | `streamText` + `toDataStreamResponse()`; `useChat` hook |
| **WebSocket** | Some custom setups | Bidirectional; more complex |

**Workspace:** `orchestrator_ui` uses non-streaming `POST /api/chat`; `orchestrator-ui-research.md` recommends designing for future SSE on same endpoint.

---

## 4. Options for Building Our Own

### Option A: Build IDE Shell from Scratch

**Approach:** New app with Monaco or CodeMirror, chat UI, project tree, MCP client.

| Pros | Cons |
|------|------|
| Full control; no legacy | High effort; reinventing IDE features |
| Can optimize for our workflow | LSP, extensions, debugging from zero |
| Clean integration with orchestrator | Long time to parity |

**Feasibility:** Medium–high effort. Best for web-first MVP using CodeMirror + Vercel AI SDK + our MCP server.

### Option B: Fork / Extend Existing Project

**Candidates:**

| Base | Effort | Fit |
|------|--------|-----|
| **Bolt.new** | Medium | Web-only; CodeMirror; WebContainers; open source. Add MCP client, reasoning panel. |
| **Flexpilot** | Medium | VS Code fork; BYOM; chat; MCP. Add orchestrator flow, reasoning panel. |
| **VSCodium** | High | Clean VS Code base; add AI, MCP, custom UI. |

**Recommendation:**  
- **Web-first:** Fork or extend **Bolt.new** — add MCP client (Stdio/SSE), reasoning sidebar, integrate with `orchestrator_client` + `mcp-server`.  
- **Desktop-first:** Extend **Flexpilot** or **VSCodium** — add orchestrator flow, reasoning panel, in-process or Stdio MCP.

### Option C: Enhance Orchestrator UI (Incremental)

**Approach:** Evolve `orchestrator_ui` into a lightweight IDE: add project tree, embedded editor (Monaco/CodeMirror via iframe or component), streaming chat, reasoning panel.

| Pros | Cons |
|------|------|
| Reuses existing backend | May hit limits of web-only |
| Fastest path to “vibe IDE” | Editor integration non-trivial |
| Already has chat + orchestration | No WebContainers; needs local/remote execution |

**Feasibility:** High for MVP. Add streaming (SSE), project tree, optional embedded editor.

---

## 5. Recommendations

### 5.1 Architecture

1. **Streaming:** Add SSE streaming to `orchestrator_ui` `/api/chat` (and `/api/run-brain` if desired). Use Vercel AI SDK patterns or raw SSE.
2. **MCP:** Keep Stdio for `mcp-server`; add optional in-process bridge if IDE and server share a process.
3. **Editor:** Use **Monaco** for desktop; **CodeMirror** for web-only.

### 5.2 Build Path (Phased)

| Phase | Scope | Approach |
|-------|-------|----------|
| **Phase 1** | Streaming + project tree in Orchestrator UI | Enhance `orchestrator_ui` with SSE, file tree component |
| **Phase 2** | Embedded editor + reasoning panel | Add Monaco or CodeMirror; collapsible reasoning sidebar |
| **Phase 3** | Full IDE shell | Evaluate Bolt.new fork vs Flexpilot extension vs from-scratch |

### 5.3 References for Implementation

- **Streaming:** [Vercel AI SDK Stream Protocol](https://sdk.vercel.ai/docs/ai-sdk-ui/stream-protocol), [Streaming AI Responses](https://www.9.agency/blog/streaming-ai-responses-vercel-ai-sdk)
- **MCP:** [MCP Architecture](https://modelcontextprotocol.io/docs/concepts/architecture), [MCP Python SDK](https://modelcontextprotocol.github.io/python-sdk/)
- **Bolt.new:** [GitHub](https://github.com/stackblitz/bolt.new), [Under the Hood](https://aitoolsinsights.com/articles/stackblitz-bolt-new-infrastructure-explained/)
- **Flexpilot:** [flexpilot.ai](https://flexpilot.ai), [GitHub](https://github.com/flexpilot-ai/flexpilot-ide)
- **Cursor MCP:** Stdio, SSE, Streamable HTTP; `.cursor/mcp.json` config

---

## 6. Workspace Alignment

Our workspace already provides:

- **MCP server** (`mcp-server/server.py`): Stdio transport; tools for workspace status, tasks, roles, workflow config.
- **Orchestrator UI** (`orchestrator_ui/`): FastAPI; chat + orchestration; intent detection; flow (proposal, critique, synthesis).
- **Orchestrator client** (`orchestrator_client/`): `run_brain_with_flow`, A2A handoffs, context loading.
- **Workflow** (`workflow.yml`, `roles.yml`): Stages, roles, slash commands.

**Gaps for full vibe IDE:**

1. **Streaming chat** — Add SSE to `/api/chat`.
2. **Project structure UI** — File tree component.
3. **Reasoning panel** — Collapsible sidebar (already designed in `orchestrator-ui-redesign.md`).
4. **Code editor** — Embedded Monaco or CodeMirror.
5. **In-process MCP** — Optional; current Stdio works with Cursor; for custom IDE, embed or bridge.

---

## 7. Summary Table

| Platform | Stack | Editor | MCP | Streaming | Open Source |
|----------|-------|--------|-----|------------|-------------|
| Cursor | Electron | Monaco | Yes (Stdio/SSE/HTTP) | SSE | Partial |
| Replit Agent | Web | Web editor | No (internal) | Yes | No |
| v0 | Next.js | Preview | API | Vercel AI SDK | No |
| Bolt.new | Remix + WebContainers | CodeMirror | No | Vercel AI SDK | Yes |
| Windsurf | Electron | Monaco | Yes | Yes | No |
| Flexpilot | VS Code fork | Monaco | Extensible | Yes | Yes |

---

*Research memo produced for Custom Vibe Coding IDE initiative. Next: Architect to validate approach; Lead Engineer to implement Phase 1 (streaming + project tree).*
