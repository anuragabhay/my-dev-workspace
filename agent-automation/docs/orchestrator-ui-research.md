# Orchestrator UI Redesign — Research Memo

**Initiative:** Conversational + Orchestration Modes  
**Problem:** Every message triggers a full orchestration cycle (3 LLM calls). Simple greetings cause unnecessary cost and latency. No distinction between "chat" (conversation) and "orchestration" (run cycle).

**References:** `agent-automation/orchestrator_ui/`, `orchestrator_client/brain.py`, `workflow.yml`, `roles.yml`, `orchestrator_patterns.md`

---

## 1. Vibe Coding Platforms & Dark Glass UI

### Platforms Inspected

| Platform | Layout | Dark / Glass | Typography | Chat Layout |
|----------|--------|--------------|------------|-------------|
| **Cursor** | IDE-style: editor + AI panel. Liquid glass themes (vibrancy/acrylic). | Dark Midnight palette, frosted panels via `vscode-vibrancy-continued`. | SF Mono, Fira Code, Consolas. | Chat as primary surface; tool calls behind the scenes. |
| **Replit Agent** | Centered chat, realtime app preview. | Dark theme support via design system. | Standard system fonts. | Chat-first; animated agent icon during work; planning phase feedback. |
| **v0.dev** | Prompt → Build → Publish flow. Design Mode for visual tweaks. | Dark mode, Liquid Glass template (glassmorphism). shadcn/ui components. | Tailwind design tokens. | Chat-driven; templates; Design Mode for refinement. |
| **Bolt.new** | Single interface: chat + file editor + terminal + preview. | Dark theme, minimal chrome. | Clean sans-serif. | Chat primary; "enhance prompt" before submit; batch instructions. |

### Patterns & Recommendations

**Layout**
- **Chat-first:** Main view is the conversation; secondary areas for reasoning, flow, or preview.
- **Sidebar / panel:** Proposal, critique, synthesis in a collapsible sidebar (current Orchestrator UI pattern).
- **Single-column fallback:** On narrow viewports, collapse sidebar to bottom drawer or modal.

**Dark Glass / Frosted UI**
- **Glassmorphism:** `backdrop-filter: blur()`, semi-transparent backgrounds (`rgba`), subtle borders, rounded corners.
- **CSS pattern:**
  ```css
  .glass {
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 12px;
  }
  ```
- **Dark palette:** `#0f1419`–`#1a2332` backgrounds, `#e6edf3` text, `#58a6ff` accent (current Orchestrator UI).

**Typography**
- Monospace for code/technical content (SF Mono, Fira Code).
- Sans-serif for chat and labels.
- Clear hierarchy: muted secondary text, accent for CTAs.

**Recommendation for Orchestrator UI**
- Apply glassmorphism to chat bubbles, sidebar, and input area.
- Keep chat-first layout; reasoning in a frosted sidebar.
- Use existing dark palette; add `backdrop-filter` for panels.

---

## 2. Intent Detection (Chat vs Orchestration)

### Problem
Distinguish:
- **Chat:** Greetings, thanks, questions, clarifications → lightweight reply (no `run_brain_with_flow`).
- **Orchestration:** "Run one cycle", "continue", "delegate to Lead Engineer", etc. → full cycle (3 LLM calls).

### Options

| Approach | Pros | Cons | Extra API? |
|----------|------|------|------------|
| **Keyword heuristics** | Simple, fast, no dependencies. | May misclassify edge cases. | No |
| **Lightweight classifier** | Better accuracy. | Needs training data; adds dependency. | Possibly (local model) |
| **Simple rules** | Transparent, easy to tune. | Manual maintenance. | No |
| **LLM pre-classifier** | Flexible, handles nuance. | Adds 1 LLM call per message. | Yes (Anthropic) |

### Feasibility with Current Stack (No Extra API)

**Recommended: Keyword heuristics + simple rules**

1. **Chat (conversation) triggers**
   - Exact or normalized match: `hi`, `hello`, `hey`, `thanks`, `thank you`, `ok`, `okay`, `got it`, `bye`, `goodbye`, `what can you do`, `help`.
   - Very short messages (e.g. &lt; 15 chars) that match greeting patterns.
   - Question-only patterns: "what is...", "how do I...", "can you explain..." (optional; may overlap with orchestration).

2. **Orchestration triggers**
   - Contains slash command: `/lead-engineer`, `/architect`, etc. (from `roles.yml`).
   - Keywords: `run`, `cycle`, `continue`, `delegate`, `orchestrate`, `next`, `proceed`, `start`.
   - Longer messages that look like task instructions.

3. **Default**
   - Ambiguous → treat as **orchestration** (conservative: user likely wants action).

### Implementation Sketch

```python
CHAT_KEYWORDS = {"hi", "hello", "hey", "thanks", "thank you", "ok", "okay", "got it", "bye", "goodbye"}
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
    # Default: orchestration (user probably wants action)
    return "orchestration"
```

### Trade-offs
- **False positives (chat → orchestration):** User says "hi" but we run cycle. Mitigation: add "hi" to chat list; keep list updated.
- **False negatives (orchestration → chat):** User says "add tests" but we reply with chat. Mitigation: default to orchestration when ambiguous.
- **No ML:** Avoids training data and model dependency; sufficient for MVP.

---

## 3. Dual-Mode API Design

### Options

| Approach | Description | Pros | Cons |
|----------|-------------|------|------|
| **Single endpoint + flag** | `POST /api/chat` with `mode: "chat" \| "orchestration"` or `run_cycle: bool` | One route; client chooses. | Mode flags can obscure behavior; more branching in handler. |
| **Two endpoints** | `POST /api/chat` (conversation) and `POST /api/orchestrate` (run cycle) | Clear separation; single responsibility. | Two routes to maintain. |
| **Single endpoint, intent-derived** | `POST /api/chat`; server infers intent and branches | Client unchanged. | Server owns classification; may surprise client. |

### Recommendation

**Two endpoints** for clarity and REST alignment:

- `POST /api/chat` — Conversation only. Request: `{ "messages": [...] }`. Response: `{ "reply": "..." }`. Uses a single lightweight LLM call (or template) for greetings/simple Q&A. **No** `run_brain_with_flow`.
- `POST /api/orchestrate` — Full cycle. Request: `{ "messages": [...] }`. Response: `{ "reply", "flow": { "proposal", "critique", "synthesis" } }`. Calls `run_brain_with_flow`.

**Alternative (smaller change):** Keep single `POST /api/chat`, add optional `mode` or `run_cycle`:

```json
{ "messages": [...], "mode": "chat" | "orchestration" | "auto" }
```

- `auto`: server runs intent detection and chooses.
- `chat` / `orchestration`: client forces mode.

For MVP, **single endpoint + `mode: "auto"`** is a reasonable compromise: one route, server-side intent detection, no client changes if default is `auto`.

### Request Body Flags

If using a single endpoint:

```python
class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    mode: Literal["chat", "orchestration", "auto"] = "auto"
    include_flow: bool = True  # Only relevant when mode=orchestration
```

### Streaming vs Non-Streaming

| Aspect | Non-Streaming | Streaming |
|--------|---------------|-----------|
| **Chat** | Simple JSON response. | Optional SSE for reply chunks. |
| **Orchestration** | `reply` + `flow` in one JSON. | SSE: `flow.proposal`, `flow.critique`, `flow.synthesis`, `reply.chunk`, `reply.done`. |
| **Implementation** | Current design. | Same endpoint, `Accept: text/event-stream` → stream. |

**Recommendation:** Keep non-streaming for MVP. Design response shape so streaming can be added later (e.g. `reply` as concatenated chunks; `flow` as separate events). No new endpoint needed—streaming is an upgrade via `Accept` header.

---

## Summary & Recommendations

| Area | Recommendation |
|------|----------------|
| **UI** | Dark glass (glassmorphism) for panels; chat-first layout; frosted sidebar for reasoning. |
| **Intent** | Keyword heuristics + rules; default to orchestration when ambiguous; no extra API. |
| **API** | Option A: Two endpoints (`/api/chat`, `/api/orchestrate`). Option B: Single endpoint + `mode: "auto"` for MVP. |
| **Streaming** | Defer; design for future SSE on same endpoint. |

### Next Steps for Implementer

1. Add intent detection (keyword + rules) in `server.py` before calling `run_brain_with_flow`.
2. Implement lightweight chat handler for `chat` intent (template or 1 LLM call with minimal system prompt).
3. Add `mode` to `ChatRequest`; when `auto`, run intent detection and route accordingly.
4. Apply glassmorphism CSS to `static/index.html` (sidebar, chat bubbles, input).

---

## References

- [Cursor Liquid Glass Themes](https://github.com/RMNCLDYO/cursor-ai-liquid-glass-themes)
- [Glassmorphism CSS Guide](https://www.braveachievers.com/post/what-is-glassmorphism-and-why-this-frosted-trend-is-still-heating-up-in-2024)
- [v0 Liquid Glass Template](https://v0.dev/templates/modern-agency-website-liquid-glass-ezmvVsZJxz8)
- [Replit Agent v2](https://blog.replit.com/agent-v2)
- [Bolt.new](https://bolt.new/)
- [Intent Detection: Chat vs Command](https://ranjankumar.in/llm-powered-chatbots-a-practical-guide-to-user-input-classification-and-intent-handling)
- [REST vs Streaming APIs](https://nordicapis.com/rest-vs-streaming-apis-how-they-differ/)
- [Flags are bad API design](https://www.gustavwengel.dk/api-design-flags-are-bad)
