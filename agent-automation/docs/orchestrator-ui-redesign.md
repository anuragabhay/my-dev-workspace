# Orchestrator UI Redesign — Design Document

**Initiative:** Conversational + Orchestration Modes  
**Version:** 1.0  
**Status:** Draft for Implementation  
**References:** `orchestrator-ui-research.md`, `orchestrator_ui/`, `orchestrator_client/brain.py`

---

## 1. Executive Summary

The Orchestrator UI currently triggers a full orchestration cycle (3 LLM calls via `run_brain_with_flow`) for every user message. Simple greetings and clarifications incur unnecessary cost and latency. This design introduces a **dual-mode architecture**: **Chat mode** (1 LLM call for conversation) and **Orchestration mode** (existing brain flow). It also defines a refreshed UI with a dark glass aesthetic inspired by Cursor, Replit Agent, v0, and Bolt.

---

## 2. Dual-Mode Architecture

### 2.1 Mode Definitions

| Mode | Trigger | LLM Calls | Output |
|------|---------|-----------|--------|
| **Chat** | Greetings, thanks, questions, clarifications | 1 | Simple reply |
| **Orchestration** | Task instructions, slash commands, "run cycle", etc. | 3 (propose → critique → synthesize) | Reply + flow (proposal, critique, synthesis) |

### 2.2 Intent Detection Strategy

**Recommended approach:** Keyword heuristics + simple rules (no extra API, no ML dependency).

#### Chat triggers
- **Exact/normalized match:** `hi`, `hello`, `hey`, `thanks`, `thank you`, `ok`, `okay`, `got it`, `bye`, `goodbye`, `what can you do`, `help`
- **Very short messages** (< 15 chars) matching greeting patterns
- **Optional:** Question-only patterns (`what is...`, `how do I...`, `can you explain...`) — may overlap with orchestration; use sparingly

#### Orchestration triggers
- **Slash command:** Message starts with `/role` where `role` is from `roles.yml` (e.g. `/lead-engineer`, `/architect`, `/junior-engineer-1`)
- **Keywords:** `run`, `cycle`, `continue`, `delegate`, `orchestrate`, `next`, `proceed`, `start`
- **Longer task-like messages** (e.g. > 50 chars with imperative phrasing)

#### Default
- **Ambiguous → orchestration.** Conservative: user likely wants action, not small talk.

### 2.3 Implementation Sketch

```python
# Load roles from roles.yml (slash commands)
CHAT_KEYWORDS = {"hi", "hello", "hey", "thanks", "thank you", "ok", "okay", "got it", "bye", "goodbye", "what can you do", "help"}
ORCHESTRATION_KEYWORDS = {"run", "cycle", "continue", "delegate", "orchestrate", "next", "proceed", "start"}

def is_chat_intent(text: str, roles: list[str]) -> str:
    """Returns 'chat' or 'orchestration'."""
    t = text.strip().lower()
    if not t:
        return "chat"
    # Slash command → orchestration
    if any(t.startswith(f"/{r}") for r in roles):
        return "orchestration"
    # Greeting / short chat
    if t in CHAT_KEYWORDS or (len(t) < 20 and t in CHAT_KEYWORDS):
        return "chat"
    # Explicit orchestration
    if any(k in t for k in ORCHESTRATION_KEYWORDS):
        return "orchestration"
    # Default: orchestration
    return "orchestration"
```

### 2.4 User Override (Toggle)

Allow the user to **force mode** via UI toggle:
- **Auto** — Server infers intent (default)
- **Chat** — Always use chat handler (1 LLM call)
- **Orchestrate** — Always use `run_brain_with_flow`

The toggle is sent as part of the request (see §3).

### 2.5 Optional User Message Injection

For orchestration mode, the **last user message** can be injected into the context so the brain considers it when deciding the next action. Current `run_brain_with_flow` receives context (pending_prompt, workspace_status, etc.) but does not receive the raw user message. Extend the context:

```python
context["user_message"] = req.messages[-1].content if req.messages else ""
```

The `_proposer_prompt` in `brain.py` can include:
```
## User message (if any)
{context.get("user_message", "")}
```

This is **optional** for MVP; the brain already receives workspace status and next actions. Injection becomes useful when the user says "delegate to Lead Engineer: add tests for health.py" — the brain should see that text.

---

## 3. API Shape

### 3.1 Recommendation: Single Endpoint + Mode Flag

**Endpoint:** `POST /api/chat` (existing)

**Rationale:** One route, minimal client changes, server-side intent when `mode: "auto"`. Two endpoints (`/api/chat`, `/api/orchestrate`) are cleaner for REST but require client to choose; single endpoint with mode is simpler for MVP.

### 3.2 Request Body

```json
{
  "messages": [
    { "role": "user", "content": "hi" },
    { "role": "assistant", "content": "Hello! How can I help?" },
    { "role": "user", "content": "run one cycle" }
  ],
  "mode": "auto",
  "include_flow": true
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `messages` | `list[ChatMessage]` | required | Conversation history |
| `mode` | `"chat" \| "orchestration" \| "auto"` | `"auto"` | Force mode or let server infer |
| `include_flow` | `bool` | `true` | Include proposal/critique/synthesis in response (only relevant when mode=orchestration) |

### 3.3 Response Body

**Chat mode:**
```json
{
  "reply": "Hello! I'm the Orchestrator. I can run cycles, delegate to agents, and help coordinate the workspace. Say 'run one cycle' or use a slash command like /lead-engineer to get started.",
  "mode_used": "chat"
}
```

**Orchestration mode:**
```json
{
  "reply": "/lead-engineer Add unit tests for health.py",
  "mode_used": "orchestration",
  "flow": {
    "proposal": "...",
    "critique": "...",
    "synthesis": "..."
  }
}
```

| Field | Present when | Description |
|-------|---------------|-------------|
| `reply` | always | Assistant reply (chat or final_decision) |
| `mode_used` | always | Which mode was used (`chat` or `orchestration`) |
| `flow` | `include_flow=true` and mode=orchestration | Proposal, critique, synthesis |

### 3.4 Error Responses

- `400` — Empty messages, invalid mode
- `500` — API key missing, context load failure, brain failure; body `{ "error": "human-readable message" }`

### 3.5 Streaming (Future)

Defer for MVP. Design response shape so streaming can be added later via `Accept: text/event-stream`. Same endpoint; streaming returns SSE events for `flow.proposal`, `flow.critique`, `flow.synthesis`, `reply.chunk`, `reply.done`.

---

## 4. UI/UX Design

### 4.1 Layout (Chat-First)

- **Main area:** Chat thread (user + assistant messages). Primary focus.
- **Secondary area:** Collapsible reasoning panel (orchestration only). Shows proposal, critique, synthesis when available.
- **Input:** Text area + Send button. Optional mode toggle (Auto / Chat / Orchestrate) near input.

### 4.2 Dark Glass Aesthetic

Inspired by Cursor, v0 Liquid Glass, Replit Agent. Palette and components:

| Token | Value | Use |
|-------|-------|-----|
| `--bg` | `#0a0a0f` | Page background |
| `--bg-elevated` | `#12121a` | Elevated surfaces |
| `--surface` | `rgba(18, 18, 26, 0.7)` | Frosted panels |
| `--border` | `rgba(255, 255, 255, 0.08)` | Subtle borders |
| `--text` | `#e6edf3` | Primary text |
| `--muted` | `#8b949e` | Secondary text |
| `--accent` | `#58a6ff` | Links, CTAs, user bubble |
| `--success` | `#3fb950` | Assistant bubble, success |
| `--warning` | `#d29922` | Critique, warnings |

**Glassmorphism pattern:**
```css
.glass {
  background: rgba(18, 18, 26, 0.6);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
}
```

Apply to:
- Chat bubbles (user: accent border; assistant: success border)
- Reasoning panel
- Input area
- Config status bar

### 4.3 Typography

- **Monospace** for code, technical content: `SF Mono`, `Fira Code`, `Consolas`
- **Sans-serif** for chat and labels: `Inter`, `system-ui`, fallback
- Clear hierarchy: muted for secondary, accent for CTAs

### 4.4 Reasoning Panel (Orchestration Only)

- **Collapsible:** Toggle to show/hide. Default: expanded when flow exists.
- **Content:** Proposal, Critique, Synthesis as distinct steps (existing `.flow-step` pattern).
- **Empty state:** "Send a message to see proposal, critique, synthesis." When mode=chat, show "Chat mode — no reasoning flow."
- **Frosted style:** Same glass treatment as chat bubbles.

### 4.5 Loading States

- **Sending:** Disable Send button; show spinner or "Thinking…" in thread.
- **Chat mode:** Short delay (1 LLM call).
- **Orchestration mode:** Longer delay (3 LLM calls); optional progress: "Proposing…" → "Critiquing…" → "Synthesizing…" (future streaming).

### 4.6 Mode Toggle (Optional)

- **Auto** — Default. Server infers.
- **Chat** — Force lightweight reply.
- **Orchestrate** — Force full cycle.

Place near input or in a compact header. Visual: segmented control or dropdown.

### 4.7 Responsive Behavior

- **Desktop:** Chat main + reasoning panel side-by-side.
- **Narrow viewport:** Reasoning panel collapses to bottom drawer or modal. Single-column chat.

---

## 5. Technical Approach

### 5.1 Backend Routing

1. **Extend `ChatRequest`** in `server.py`:
   - Add `mode: Literal["chat", "orchestration", "auto"] = "auto"`
   - Keep `include_flow: bool = True`

2. **Intent detection module** (new file `orchestrator_ui/intent.py`):
   - `is_chat_intent(text, roles)` → `"chat"` or `"orchestration"`
   - Load roles from `roles.yml` (slash commands)

3. **Chat handler** (new):
   - Single LLM call with minimal system prompt: "You are the Orchestrator assistant. Reply briefly to greetings, thanks, and simple questions. For task-related requests, suggest the user say 'run one cycle' or use a slash command."
   - User message = last message content
   - Return `{ "reply": "...", "mode_used": "chat" }`

4. **Orchestration handler** (existing logic):
   - Build context, optionally inject `user_message`
   - Call `run_brain_with_flow`
   - Return `{ "reply", "mode_used": "orchestration", "flow" }`

5. **`POST /api/chat` flow:**
   ```
   if mode == "auto":
       mode = is_chat_intent(last_message, roles)
   if mode == "chat":
       return chat_handler(messages)
   else:
       return orchestration_handler(messages)
   ```

### 5.2 Frontend Structure

- **Single HTML file** (or minimal SPA): `static/index.html`
- **Inline CSS** for glass styles, or `static/styles.css`
- **Inline JS** or `static/app.js`:
  - Send request with `mode` from toggle (or omit for "auto")
  - Render `mode_used` in UI (e.g. badge: "Chat" vs "Orchestration")
  - Show/hide reasoning panel based on `flow` presence
  - Apply glass classes to chat bubbles, panel, input

### 5.3 Performance Considerations

- **Chat mode:** ~1–3s (1 LLM call). No context load beyond minimal.
- **Orchestration mode:** ~10–30s (3 LLM calls + context load). Consider:
  - HTTP timeout: 60s client-side
  - Future: async job + polling or SSE streaming
- **Intent detection:** O(1) keyword lookup; negligible overhead.

### 5.4 Migration Plan

| Step | Action |
|------|--------|
| 1 | Add `intent.py` with `is_chat_intent` |
| 2 | Add chat handler (1 LLM call) in `server.py` |
| 3 | Extend `ChatRequest` with `mode` |
| 4 | Route in `POST /api/chat` based on mode |
| 5 | Optionally inject `user_message` into context for orchestration |
| 6 | Update frontend: glass styles, mode toggle, reasoning panel visibility |
| 7 | Add `mode_used` to response; frontend displays it |

**Rollback:** Revert to always-orchestration by defaulting `mode` to `"orchestration"` or removing intent detection.

---

## 6. Alternatives Considered

### 6.1 Two Endpoints vs Single Endpoint

| Option | Pros | Cons |
|--------|-----|-----|
| **Two endpoints** (`/api/chat`, `/api/orchestrate`) | Clear separation, REST alignment | Client must choose; two routes to maintain |
| **Single endpoint + mode** | One route; server infers when `auto` | Mode flag adds branching; some argue flags are bad API design |

**Chosen:** Single endpoint + mode. Simpler for MVP; client can force mode via toggle.

### 6.2 Intent Detection: LLM vs Heuristics

| Option | Pros | Cons |
|--------|-----|-----|
| **LLM pre-classifier** | Handles nuance, flexible | +1 LLM call per message; defeats cost savings |
| **Keyword heuristics** | No extra API, fast, transparent | May misclassify edge cases |
| **Trained classifier** | Better accuracy | Needs training data; adds dependency |

**Chosen:** Keyword heuristics. Sufficient for MVP; default to orchestration when ambiguous.

### 6.3 Streaming vs Non-Streaming

| Option | Pros | Cons |
|--------|-----|-----|
| **Non-streaming (MVP)** | Simple, current design | User waits for full response |
| **Streaming (future)** | Progressive feedback, better UX | More complex; SSE handling |

**Chosen:** Non-streaming for MVP. Design response shape for future SSE.

### 6.4 Reasoning Panel: Always Visible vs Collapsible

| Option | Pros | Cons |
|--------|-----|-----|
| **Always visible** | Simple | Takes space when empty or in chat mode |
| **Collapsible** | Saves space; focus on chat | Extra interaction |

**Chosen:** Collapsible. Default expanded when flow exists; collapsed when chat mode or empty.

### 6.5 User Message Injection

| Option | Pros | Cons |
|--------|-----|-----|
| **Inject** | Brain sees exact user instruction | Slight context bloat |
| **Don't inject** | Simpler | Brain may miss nuance (e.g. "add tests for X") |

**Chosen:** Optional for MVP. Add when brain prompts are updated to use it; low risk.

---

## 7. Summary

| Area | Decision |
|------|----------|
| **Dual mode** | Chat (1 LLM) vs Orchestration (run_brain_with_flow) |
| **Intent** | Keyword heuristics + rules; default orchestration |
| **Override** | UI toggle: Auto / Chat / Orchestrate |
| **API** | Single `POST /api/chat` with `mode: "auto" \| "chat" \| "orchestration"` |
| **UI** | Dark glass (#0a0a0f–#12121a), frosted panels, chat-first, collapsible reasoning |
| **Streaming** | Defer; design for future SSE |

---

## 8. References

- `agent-automation/docs/orchestrator-ui-research.md` — Research memo
- `agent-automation/orchestrator_ui/server.py` — Current backend
- `agent-automation/orchestrator_ui/static/index.html` — Current frontend
- `agent-automation/orchestrator_client/brain.py` — `run_brain_with_flow`
- `agent-automation/roles.yml` — Slash commands for intent detection
- `agent-automation/workflow.yml` — Workflow stages

---

## 9. PM Feasibility Notes

**Version:** 1.0  
**Author:** PM  
**Date:** 2026-02-25

### 9.1 Feasibility Summary

| Design Option | Achievable? | Notes |
|---------------|-------------|-------|
| Dual-mode (chat vs orchestration) | ✅ Yes | Current stack: Anthropic, FastAPI, `run_brain_with_flow`. Add 1 LLM chat handler. |
| Intent detection (keyword heuristics) | ✅ Yes | No extra API. Python heuristics; load roles from `roles.yml` for slash commands. |
| Single endpoint + mode flag | ✅ Yes | Extend `ChatRequest` with `mode`; branch in `POST /api/chat`. |
| User message injection (optional) | ✅ Yes | Add `context["user_message"]`; extend `_proposer_prompt` in brain.py. Low effort. |
| Dark glass UI | ✅ Yes | Pure CSS: `backdrop-filter`, `rgba`, design tokens. No new deps. |
| Mode toggle (Auto/Chat/Orchestrate) | ✅ Yes | Simple HTML/JS; send `mode` in request. |
| Collapsible reasoning panel | ✅ Yes | Add toggle; default expanded when flow exists. |
| Streaming | ⏸️ Deferred | Design response shape for future SSE; not in MVP. |

### 9.2 Dependencies

- **No new runtime dependencies** for core dual-mode. Anthropic, FastAPI, uvicorn already in `requirements.txt`.
- **roles.yml parsing:** Intent module must read slash commands. Options: (a) Use `context_loader` or MCP `get_workflow_config` if available; (b) Add `PyYAML` to `orchestrator_ui/requirements.txt` if parsing roles.yml directly. Recommend: parse `roles.yml` via existing agent-automation tooling or add PyYAML (lightweight, widely used).

### 9.3 Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Intent misclassification | Low | Default to orchestration when ambiguous. User can force mode via toggle. |
| Chat mode latency | Low | 1 LLM call ~1–3s; target <5s for greetings. |
| Orchestration latency | Expected | 3 LLM calls ~10–30s; 60s client timeout. No change from current. |
| Cost | Positive | Chat mode reduces cost for greetings (1 vs 3 calls). |

### 9.4 Scope Definition

#### MVP (In Scope)

- **Dual-mode:** Chat (1 LLM) + Orchestration (run_brain_with_flow).
- **Intent detection:** Keyword heuristics + rules; default orchestration.
- **Mode override:** UI toggle Auto / Chat / Orchestrate.
- **API:** Single `POST /api/chat` with `mode`, `include_flow`; response includes `mode_used`.
- **UI:** Dark glass aesthetic, polished layout, collapsible reasoning panel.
- **User message injection:** Include in MVP (low effort; improves brain context for task-like messages).

#### Deferred (Post-MVP)

- **Streaming:** SSE for progressive feedback; design response shape for future.
- **Advanced intent:** LLM pre-classifier, question-only patterns (`what is...`, `how do I...`).
- **Progress indicators:** "Proposing…" → "Critiquing…" → "Synthesizing…" (requires streaming or polling).

#### Out of Scope

- **Auth / OAuth / login** — No user authentication.
- **Multi-user / tenant isolation** — Single-user assumption.
- **Replacing brain logic** — propose → critique → synthesize unchanged.
- **MCP hosting in UI server** — Use MCP when available from environment; no hosting.

### 9.5 Acceptance Criteria (Testable)

| ID | Criterion | How to Verify |
|----|-----------|---------------|
| AC1 | User says "hello" → conversational reply in <5s | Send `{"messages":[{"role":"user","content":"hello"}],"mode":"auto"}`; assert `mode_used === "chat"`; assert `reply` is non-empty; assert response time < 5s. |
| AC2 | User says "run one cycle" → full orchestration | Send `{"messages":[{"role":"user","content":"run one cycle"}],"mode":"auto"}`; assert `mode_used === "orchestration"`; assert `flow.proposal`, `flow.critique`, `flow.synthesis` present; assert `reply` non-empty. |
| AC3 | UI: dark glass, polished layout | Visual: `--bg` ≈ `#0a0a0f`, `--surface` frosted; chat bubbles and reasoning panel use `.glass` (backdrop-filter, rgba). |
| AC4 | Reasoning panel collapsible | Toggle control exists; panel collapses/expands; default expanded when `flow` present, collapsed or "Chat mode — no reasoning flow" when mode=chat. |
| AC5 | Mode toggle functional | Toggle Auto/Chat/Orchestrate; send with `mode`; Chat forces `mode_used === "chat"`; Orchestrate forces `mode_used === "orchestration"`. |

### 9.6 Feedback to Architect

1. **Intent detection edge case:** "hi there" (9 chars) does not exact-match `CHAT_KEYWORDS`. Consider: (a) substring/prefix match for greetings (`t.startswith("hi")` or `t.split()[0] in CHAT_KEYWORDS`); or (b) keep exact match only and document that "hi" works but "hi there" may route to orchestration. Recommend (a) for better UX.

2. **roles.yml loading:** Intent module needs role slash values. Architect to confirm: load via `get_workflow_config` (if MCP/context available) or direct YAML parse. If direct parse, add PyYAML to orchestrator_ui deps.

3. **Chat handler system prompt:** Design §5.1 specifies minimal prompt. Ensure it instructs the model to *not* run orchestration (e.g. "Do not delegate or run cycles; suggest the user say 'run one cycle' or use a slash command for task requests.").

4. **Empty message:** Design §2.3 `is_chat_intent("")` returns `"chat"`. Confirm: empty messages should be rejected by API (400) before intent is called. Current server already returns 400 for empty messages.
