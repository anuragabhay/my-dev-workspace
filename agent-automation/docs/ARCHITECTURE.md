# Unified App Architecture

**Initiative:** Custom Vibe Coding IDE — Unified App with Local LLM, Dynamic UI, and Mode Routing  
**Version:** 1.0  
**Date:** 2026-03-01  
**Author:** Architect  
**Status:** Draft — Pending CTO and User Approval

---

## Table of Contents

1. [Vision and Principles](#1-vision-and-principles)
2. [System Diagram](#2-system-diagram)
3. [Data Flows by Use Case](#3-data-flows-by-use-case)
4. [Local LLM Layer](#4-local-llm-layer)
5. [Dynamic UI Subsystem](#5-dynamic-ui-subsystem)
6. [Mode Registry](#6-mode-registry)
7. [Session Persistence](#7-session-persistence)
8. [Embedded Editor](#8-embedded-editor)
9. [Android / PWA Path](#9-android--pwa-path)
10. [Security Model](#10-security-model)
11. [Existing System Preservation](#11-existing-system-preservation)
12. [Non-Negotiable Constraints](#12-non-negotiable-constraints)
13. [Implementation Phases](#13-implementation-phases)
14. [Open Questions for CTO / User](#14-open-questions-for-cto--user)

---

## 1. Vision and Principles

### Vision

Build **one unified app** — the current Orchestrator UI (`agent-automation/orchestrator_ui/`) evolved into a full vibe-coding IDE — that runs entirely on local LLM (Ollama), provides dynamic rich-UI responses beyond plain text, routes user intent to specialized modes, persists conversations in SQLite, and supports an embedded code editor with agent-driven file operations. The YouTube Shorts generator remains its own standalone service; the unified app proxies to it as a first-class "video mode."

### Design Principles

| # | Principle | What it means in practice |
|---|-----------|--------------------------|
| P1 | **One unified app** | Single FastAPI server + static frontend. No new top-level projects. Evolve `orchestrator_ui/`. |
| P2 | **Local LLM only (privacy absolute)** | Ollama on localhost. No cloud AI API calls from this app. The provider abstraction in `llm_provider.py` is preserved for open-source extensibility — future developers may add cloud support — but the unified app enforces local-only at startup. If `ORCHESTRATOR_LLM_PROVIDER` is set to anything other than `'local'`, the server exits with a clear error. |
| P3 | **Build on existing progress** | CodeMirror 6 already present → extend it. `llm_provider.py` already abstracts providers → add `local` branch. Existing routes stay; new routes are additive. |
| P4 | **Dynamic UI** | LLM responses may include a `ui_spec` JSON payload in addition to (or instead of) plain text. The frontend renderer maps component types to DOM — no `eval`, no `innerHTML`. |
| P5 | **Mode-driven architecture** | A lightweight intent router classifies every user message and dispatches to the appropriate handler (chat, orchestration, video, coding, health, ad-hoc). |
| P6 | **Progressive enhancement** | Every feature degrades gracefully: no Ollama → error message, no session DB → localStorage fallback, no ui_spec → plain text reply. |
| P7 | **Preserve running systems** | The Orchestrator (Cursor-based agent automation) and YouTube Shorts FastAPI (port 8766) must continue to work unchanged throughout migration. |

---

## 2. System Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              User Browser                                   │
│                                                                             │
│  ┌──────────────┐  ┌─────────────────────────────────────────────────────┐ │
│  │  Chat Thread │  │  Canvas Tab  (full-width Dynamic UI view)           │ │
│  │  + inline    │  │                                                     │ │
│  │  artifact    │  │  ┌──────────┐ ┌────────────┐ ┌─────────────────┐  │ │
│  │  cards       │  │  │  cards   │ │ video_embed│ │  CodeMirror     │  │ │
│  └──────┬───────┘  │  │  table   │ │ progress   │ │  editor (tabs)  │  │ │
│         │          │  │  status  │ │  steps     │ │  diff view      │  │ │
│         │          │  └──────────┘ └────────────┘ └─────────────────┘  │ │
│         │          └─────────────────────────────────────────────────────┘ │
│         │SSE / fetch                                                        │
└─────────┼───────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Unified App  (FastAPI + static)                          │
│                    agent-automation/orchestrator_ui/server.py               │
│                    port 8765                                                │
│                                                                             │
│   POST /api/chat  ──►  Intent Router (intent.py)                           │
│                            │                                               │
│              ┌─────────────┼──────────────────────────┐                   │
│              ▼             ▼              ▼            ▼                   │
│         chat_handler  orch_handler  video_handler  coding_handler          │
│         (general Q&A) (brain flow)  (proxy→8766)   (CodeMirror ops)       │
│              │             │              │            │                   │
│              └─────────────┴──────────────┴────────────┘                  │
│                                    │                                       │
│                          LLM Provider Abstraction                          │
│                          (llm_provider.py)                                 │
│                                    │                                       │
│                    ┌───────────────┘                                       │
│                    ▼                                                       │
│            ┌───────────────┐                                               │
│            │  Local LLM    │  ◄── ORCHESTRATOR_LLM_PROVIDER=local          │
│            │  (Ollama)     │      ORCHESTRATOR_LLM_BASE_URL                │
│            │  port 11434   │      ORCHESTRATOR_LLM_MODEL                   │
│            └───────────────┘                                               │
│                                                                             │
│   Additional services (same process)                                       │
│   ├── sessions.py  (SQLite, zero deps)                                     │
│   ├── modes.py     (ModeDefinition registry)                               │
│   └── ui_validator.py  (JSON Schema validation for ui_spec)                │
│                                                                             │
│   Existing services (unchanged)                                             │
│   ├── brain.py / context_loader.py / cycle_runner.py                       │
│   └── mcp-server (Stdio subprocess)                                        │
└─────────────────────────────────────────────────────────────────────────────┘
          │                        │
          │ proxy  /api/video/*    │ SQLite
          ▼                        ▼
┌──────────────────┐    ┌──────────────────┐
│  YouTube Shorts  │    │  sessions.db      │
│  FastAPI (8766)  │    │  (local file)     │
│  (UNCHANGED)     │    └──────────────────┘
└──────────────────┘

Mobile / Android
└── PWA (manifest + service worker, Now)
└── Capacitor APK (Phase 1)
└── Capacitor + llama.cpp NDK (Phase 2, on-device LLM)
```

---

## 3. Data Flows by Use Case

### 3.1 "Study tribes of South American forests" → Chat → Ad-hoc UI

```
User types: "Study tribes of South American forests"
     │
     ▼
POST /api/chat  { messages: [...], session_id: "abc" }
     │
     ▼
Intent Router (intent.py)
  rule-based fast path: no slash command, no code keyword, no video keyword
  → LLM fallback: classify as "adhoc" (educational query, rich content possible)
     │
     ▼
chat_handler  (or adhoc_handler, mode=adhoc)
  System prompt includes: "You MAY return a ui_spec JSON block for rich output."
  LLM (Ollama) call → response includes:
  {
    "reply": "The tribes of South American forests ...",
    "ui_spec": {
      "layout": "stack",
      "components": [
        { "type": "heading", "text": "Tribes of the Amazon Basin" },
        { "type": "text",    "content": "..." },
        { "type": "card",    "title": "Yanomami", "body": "...", "image": "/static/..." },
        { "type": "card",    "title": "Kayapó",   "body": "..." },
        { "type": "video_embed", "url": "https://www.youtube.com/watch?v=...", "caption": "..." },
        { "type": "table",   "headers": ["Tribe","Region","Population"], "rows": [[...]] }
      ]
    }
  }
     │
     ▼
Backend: validate ui_spec against JSON Schema (ui_validator.py)
  • All component types must be in registered catalog
  • URLs validated against allowlist domains
  • If validation fails → strip ui_spec, return plain reply only
     │
     ▼
SSE stream to frontend:
  event: reply.chunk  (text)
  event: ui_spec.ready  { "ui_spec": {...} }  (after full response)
  event: reply.done
     │
     ▼
Frontend:
  • Appends text chunks to chat thread message bubble
  • On ui_spec.ready → renders artifact card inline in thread
  • "Open in Canvas" button → full-width Canvas tab
  • Dynamic renderer: stack → div.stack, card → div.card, video_embed → iframe (allowlisted)
     │
     ▼
Session: persist user message + assistant reply (with ui_spec) to SQLite
```

---

### 3.2 "Generate a YouTube short" → Video Mode → SSE Progress

```
User types: "Generate a YouTube short about climate change"
     │
     ▼
POST /api/chat  { messages: [...] }
     │
     ▼
Intent Router
  rule-based: matches "YouTube short" / "generate video" keywords
  → mode = "video"
     │
     ▼
video_handler
  1. Extract parameters: topic = "climate change", style = default
  2. POST to http://localhost:8766/api/generate  (YouTube Shorts FastAPI proxy)
     with SSE pass-through
     │
     ▼
YouTube Shorts backend (port 8766) — UNCHANGED
  Streams pipeline progress events:
  { "type": "flow.step", "agent": "Proposer", "status": "running", ... }
  { "type": "flow.step", "agent": "Proposer", "status": "completed", "summary": "..." }
  ...
  { "type": "done", "video_url": "...", "thumbnail": "..." }
     │
     ▼
video_handler proxies SSE events to client, optionally prepending with
  event: ui_spec.ready  {
    "layout": "stack",
    "components": [
      { "type": "progress_steps", "steps": [...] },
      { "type": "video_embed", "url": "...", "caption": "Your Short is ready" }
    ]
  }
     │
     ▼
Frontend: VideoGeneratorPanel renders progress_steps, then video_embed on completion
```

---

### 3.3 "Check service health" → Health Mode → Status Table

```
User types: "Check service health" (or "/health")
     │
     ▼
Intent Router
  rule-based: matches "/health" slash command or "service health" keyword
  → mode = "health"  (or falls back to "chat" with health system prompt)
     │
     ▼
health_handler
  Probes: Ollama /api/tags, YouTube Shorts /health, MCP server ping
  Assembles status payload:
  {
    "services": [
      { "name": "Ollama", "status": "ok", "latency_ms": 12 },
      { "name": "YouTube Shorts", "status": "ok", "latency_ms": 45 },
      { "name": "MCP Server", "status": "degraded", "error": "..." }
    ]
  }
     │
  Passes payload to LLM with prompt:
  "Given the following service statuses, produce a ui_spec with a table and status_indicators."
     │
     ▼
LLM returns ui_spec:
  {
    "layout": "stack",
    "components": [
      { "type": "status_indicator", "label": "Ollama", "status": "ok" },
      { "type": "status_indicator", "label": "YouTube Shorts", "status": "ok" },
      { "type": "status_indicator", "label": "MCP Server", "status": "degraded" },
      { "type": "table", "headers": ["Service","Status","Latency"], "rows": [...] }
    ]
  }
     │
     ▼
Frontend renders status_indicators (green/red/yellow dots) + table
```

---

### 3.4 "Code a todo app" → Coding Mode → CodeMirror + Diff View

```
User types: "Code a simple todo app in Python"
     │
     ▼
Intent Router
  rule-based: matches "code a", "write code", ".py", "implement" keywords
  → mode = "coding"
     │
     ▼
coding_handler
  System prompt includes Bolt.new Artifacts pattern:
  "Return file_operations: [{path, proposed_content}] for any files to create/edit."
     │
     ▼
LLM (Ollama) returns:
  {
    "reply": "Here's a simple todo app:",
    "file_operations": [
      { "path": "todo.py", "proposed_content": "# todo app\n..." },
      { "path": "test_todo.py", "proposed_content": "import pytest\n..." }
    ]
  }
     │
     ▼
Backend:
  Validates file_operations: paths must be relative, no ../, no absolute paths
  Each proposed_content is plain text (no eval, no shell execution by backend)
     │
     ▼
SSE to frontend:
  event: reply.chunk  (text narration)
  event: file_operations.ready  { file_operations: [...] }
     │
     ▼
Frontend:
  • Chat thread shows narration
  • CodeMirror editor opens (or Canvas tab activates) showing multi-file tabs
  • Each file shown in diff view: @codemirror/merge comparing "" (new) vs proposed_content
  • "Accept All" / "Accept File" / "Reject" buttons
  • On Accept → PUT /api/file  { path, content }  → writes to disk
  • On Reject → nothing written
     │
     ▼
Session: persist assistant reply including file_operations metadata
```

---

## 4. Local LLM Layer

### 4.1 Ollama Setup

```
brew install ollama          # macOS (Apple Silicon: Metal acceleration auto)
ollama serve                 # runs at http://localhost:11434
ollama pull mistral-nemo     # recommended default: 12B, 7GB, Apache 2.0
```

Ollama exposes an OpenAI-compatible API at `http://localhost:11434/v1`, allowing the existing OpenAI SDK path to be reused with zero client-code changes beyond `base_url`.

### 4.2 Provider Abstraction Extension

Current `llm_provider.py` supports `anthropic` and `openai`. Add `local` as a third branch:

```python
# New branch in chat_sync and chat_stream
if provider == "local":
    base_url = os.getenv("ORCHESTRATOR_LLM_BASE_URL", "http://localhost:11434/v1")
    model    = os.getenv("ORCHESTRATOR_LLM_MODEL", "mistral-nemo")
    # Reuse OpenAI SDK — Ollama is OpenAI-compatible
    return _call_openai_sync(system, user, model, api_key="ollama",
                             base_url=base_url, messages=messages)
```

The `api_key="ollama"` is a dummy value; Ollama does not validate keys. The `base_url` override routes the SDK to localhost.

The `anthropic` and `openai` branches in `llm_provider.py` are intentionally preserved. This follows the open/closed principle: the abstraction is open for extension (future developers can add cloud or other providers) but the unified app is closed against cloud calls at runtime via a startup guard in `server.py`.

### 4.3 Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `ORCHESTRATOR_LLM_PROVIDER` | `local` | `anthropic`, `openai`, or `local` |
| `ORCHESTRATOR_LLM_BASE_URL` | `http://localhost:11434/v1` | Ollama (or any OpenAI-compatible) endpoint |
| `ORCHESTRATOR_LLM_MODEL` | `mistral-nemo` | Model name passed to Ollama |
| `ANTHROPIC_API_KEY` | — | Required only when provider=anthropic. Not used by unified app (startup guard enforces local-only). Available for `llm_provider.py` open-source use only. |
| `OPENAI_API_KEY` | — | Required only when provider=openai. Not used by unified app (startup guard enforces local-only). Available for `llm_provider.py` open-source use only. |

### 4.4 Recommended Models

| Model | Size | RAM | License | Best for |
|-------|------|-----|---------|---------|
| `mistral-nemo` | 12B | 7 GB | Apache 2.0 | Default: chat, orchestration, coding |
| `phi4-mini` | 3.8B | 3 GB | MIT | Low-RAM devices, fast responses |
| `phi4` | 14B | 8 GB | MIT | Code generation |

**Excluded models** (do not use by default): DeepSeek, Qwen, Yi, Baichuan (Chinese company ownership, data sovereignty concerns); Llama (Meta, data policy concern; excluded unless company explicitly approves); Codestral, Command R (non-commercial licenses).

### 4.5 Fallback Behavior

```
ORCHESTRATOR_LLM_PROVIDER=local
  → Ollama reachable  → normal operation
  → Ollama unreachable → 503 error with message:
      "Local LLM unavailable. Run: ollama serve && ollama pull mistral-nemo"
  → No cloud fallback by default (local-only principle P2)
```

---

## 5. Dynamic UI Subsystem

### 5.1 Component Catalog (13 types)

| Type | Description | Key fields |
|------|-------------|-----------|
| `grid` | N-column grid container | `columns`, `children` |
| `stack` | Vertical stack (root layout) | `children` |
| `card` | Content card | `title`, `body`, `image?`, `actions?` |
| `heading` | H1–H3 heading | `text`, `level` (1–3) |
| `text` | Paragraph text (markdown allowed) | `content` |
| `image` | Static image | `url`, `alt`, `caption?` |
| `video_embed` | YouTube/Vimeo iframe | `url`, `caption?` |
| `button` | Action button | `label`, `action`, `style?` |
| `code_block` | Syntax-highlighted code | `language`, `code` |
| `status_indicator` | Dot + label (ok/warn/error) | `label`, `status` |
| `progress_steps` | Pipeline steps with statuses | `steps[]` (label, status, summary) |
| `quiz_card` | Multiple-choice question | `question`, `options[]`, `correct?` |
| `table` | Data table | `headers[]`, `rows[][]` |

### 5.2 `ui_spec` JSON Structure

```json
{
  "layout": "stack",
  "components": [
    { "type": "heading", "text": "...", "level": 1 },
    { "type": "card", "title": "...", "body": "...", "image": "https://..." },
    { "type": "video_embed", "url": "https://www.youtube.com/watch?v=..." }
  ],
  "ephemeral": false
}
```

`ephemeral: true` is used for ad-hoc mode responses that should not be persisted long-term.

### 5.3 Backend Schema Validation (`ui_validator.py`)

```python
# JSON Schema snippet (abbreviated)
UI_SPEC_SCHEMA = {
  "type": "object",
  "properties": {
    "layout": { "type": "string", "enum": ["stack", "grid"] },
    "components": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "type": { "type": "string", "enum": REGISTERED_COMPONENT_TYPES }
        },
        "required": ["type"]
      }
    }
  },
  "required": ["layout", "components"]
}

def validate_ui_spec(spec: dict) -> tuple[bool, str]:
    """Returns (is_valid, error_message). Strip spec on failure."""
    try:
        jsonschema.validate(spec, UI_SPEC_SCHEMA)
        # Additional URL allowlist check
        for component in spec.get("components", []):
            if component.get("type") in ("video_embed", "image"):
                url = component.get("url", "")
                if not is_url_allowed(url):
                    return False, f"URL not in allowlist: {url}"
        return True, ""
    except jsonschema.ValidationError as e:
        return False, str(e)
```

### 5.4 URL Allowlist

```python
ALLOWED_URL_DOMAINS = [
    "youtube.com", "www.youtube.com", "youtu.be",
    "vimeo.com",
    "wikimedia.org", "upload.wikimedia.org",
    # Local static assets
    "/static/",
]
```

Dynamic expansion of this list requires a code change (no user-configurable URL allowlist at runtime).

### 5.5 Frontend Renderer (vanilla JS)

```javascript
// renderer.js — no eval, no innerHTML for user content
const COMPONENT_RENDERERS = {
  heading:          renderHeading,
  text:             renderText,
  card:             renderCard,
  image:            renderImage,
  video_embed:      renderVideoEmbed,   // creates <iframe> with allowlisted src
  button:           renderButton,       // calls registered action handlers only
  code_block:       renderCodeBlock,    // uses highlight.js or CodeMirror view-only
  status_indicator: renderStatusIndicator,
  progress_steps:   renderProgressSteps,
  quiz_card:        renderQuizCard,
  table:            renderTable,
  stack:            renderStack,
  grid:             renderGrid,
};

function renderSpec(spec, container) {
  container.innerHTML = "";   // safe: container is known-empty
  const root = COMPONENT_RENDERERS[spec.layout] || renderStack;
  container.appendChild(root(spec));
}

function renderComponent(component) {
  const renderer = COMPONENT_RENDERERS[component.type];
  if (!renderer) {
    console.warn("Unknown component type:", component.type);
    return document.createTextNode("[unsupported component]");
  }
  return renderer(component);
}
```

All text content is set via `.textContent` (never `.innerHTML`). Video embeds create `<iframe>` elements with `src` validated against the allowlist before DOM insertion.

### 5.6 Integration Points

- **Inline artifact card**: Rendered inside the chat thread message bubble (like Claude.ai artifact cards). Small preview; "Open in Canvas" button expands to full-width Canvas tab.
- **Canvas tab**: Full-width view of the current `ui_spec`. Persists across messages; clicking a new artifact replaces Canvas content.
- **Ad-hoc mode**: `ephemeral: true` specs are rendered but not stored in session DB.

---

## 6. Mode Registry

### 6.1 ModeDefinition Schema

```python
@dataclass
class ModeDefinition:
    id: str                          # "chat", "video", "coding", "health", "adhoc"
    name: str                        # Display name
    description: str                 # One-line description
    trigger_keywords: list[str]      # Fast-path rule triggers
    handler: str                     # Handler function name in server.py
    system_prompt_template: str      # Path or inline text
    supports_ui_spec: bool = True    # Whether LLM may return ui_spec
    supports_streaming: bool = True
    ephemeral: bool = False          # Ad-hoc modes are ephemeral
```

### 6.2 `modes.json` Configuration

```json
{
  "modes": [
    {
      "id": "chat",
      "name": "Chat",
      "description": "General conversation and Q&A",
      "trigger_keywords": [],
      "handler": "chat_handler",
      "supports_ui_spec": true
    },
    {
      "id": "orchestration",
      "name": "Orchestration",
      "description": "Multi-agent brain (propose → critique → synthesize)",
      "trigger_keywords": ["/orchestrate", "/brain", "/run"],
      "handler": "orchestration_handler",
      "supports_ui_spec": false
    },
    {
      "id": "video",
      "name": "YouTube Shorts",
      "description": "Generate a YouTube Short via the video pipeline",
      "trigger_keywords": ["youtube short", "generate video", "make a short", "/video"],
      "handler": "video_handler",
      "supports_ui_spec": true
    },
    {
      "id": "coding",
      "name": "Coding",
      "description": "Code generation with embedded editor and diff view",
      "trigger_keywords": ["code a", "write code", "implement", "build a", "/code"],
      "handler": "coding_handler",
      "supports_ui_spec": false
    },
    {
      "id": "health",
      "name": "Health Check",
      "description": "Service and infrastructure health dashboard",
      "trigger_keywords": ["/health", "service health", "check health", "is ollama"],
      "handler": "health_handler",
      "supports_ui_spec": true
    }
  ]
}
```

### 6.3 Hybrid Classifier (`intent.py`)

```
detect_mode(message: str, history: list[dict]) -> str:

1. Rule-based fast path:
   For each ModeDefinition in registry (ordered by priority):
     if any trigger_keyword in message.lower():
       return mode.id
   → O(n·k) scan, sub-millisecond

2. LLM fallback (ambiguous messages only):
   Prompt: "Classify this message into one of: chat, video, coding, health, adhoc.
            Message: {message}
            Reply with JSON: {\"mode\": \"...\", \"confidence\": 0.0–1.0}"
   If confidence < 0.6 → default to "chat"

3. detect_intent() kept as shim:
   def detect_intent(message): return detect_mode(message, [])
   Preserves backward compatibility with existing callers.
```

### 6.4 YouTube Shorts as First-Class Mode

The video mode handler is an API wrapper (Option B from research):

```
video_handler:
  → validates topic extraction from message
  → POST http://localhost:8766/api/generate  { topic, style, ... }
  → proxies SSE events from YT backend to client
  → no coupling: YT app code is never imported or modified
  → if YT backend is down: return 503 with ui_spec status_indicator
```

This preserves isolation: the YouTube Shorts application at port 8766 is unchanged. The unified app acts as a proxy.

### 6.5 Ad-hoc Mode

When the LLM classifier returns `mode = "adhoc"` (or confidence < 0.6 and topic is educational/creative), the LLM is prompted to return a `ui_spec` freely:

```json
{
  "mode": "adhoc",
  "components": [
    { "type": "heading", "text": "..." },
    { "type": "card", "title": "...", "body": "..." }
  ],
  "ephemeral": true
}
```

The backend validates the components against the registered catalog before passing to the frontend. No code execution occurs.

### 6.6 Video Mode and Cloud APIs — Current State and Future Path

The video mode handler proxies requests to the YouTube Shorts FastAPI at port 8766. That application currently uses cloud APIs: OpenAI (script, embeddings), Anthropic (script), ElevenLabs (TTS), and Runway (video generation). When a user triggers video mode, data for that pipeline leaves the local environment. This is a known gap: Phase G (see Implementation Phases) defines a local-only video pipeline as a future phase. Until Phase G is complete, video mode is a cloud-dependent exception. This must be communicated clearly to users in the UI (e.g., a banner: *'Video generation uses cloud services: OpenAI, ElevenLabs, Runway, YouTube.'*).

---

## 7. Session Persistence

### 7.1 SQLite Schema

**New file:** `orchestrator_ui/sessions.py`

```sql
-- sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id          TEXT PRIMARY KEY,           -- UUID v4
    title       TEXT NOT NULL DEFAULT '',   -- auto-generated from first message
    created_at  INTEGER NOT NULL,           -- Unix timestamp
    updated_at  INTEGER NOT NULL
);

-- messages table
CREATE TABLE IF NOT EXISTS messages (
    id          TEXT PRIMARY KEY,           -- UUID v4
    session_id  TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role        TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
    content     TEXT NOT NULL,              -- plain text reply
    ui_spec     TEXT,                       -- JSON string or NULL
    mode        TEXT,                       -- mode that generated this message
    created_at  INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
```

Zero new dependencies: Python stdlib `sqlite3`. DB file path: `$WORKSPACE_ROOT/agent-automation/orchestrator_ui/sessions.db` (gitignored).

### 7.2 API Routes

| Method | Route | Purpose |
|--------|-------|---------|
| `GET` | `/api/sessions` | List sessions (id, title, updated_at), newest first |
| `POST` | `/api/sessions` | Create new session, returns `{id, title, created_at}` |
| `GET` | `/api/sessions/{id}` | Get session + all messages |
| `PATCH` | `/api/sessions/{id}` | Rename session title |
| `DELETE` | `/api/sessions/{id}` | Delete session and all messages |
| `POST` | `/api/sessions/{id}/messages` | Append message (used internally post-reply) |

`POST /api/chat` **stays stateless**: accepts `session_id` in request body; server appends to DB after LLM reply. Chat inference logic is unchanged.

### 7.3 Frontend Integration

```javascript
// On page load:
const sessions = await GET('/api/sessions');
if (sessions.length > 0) {
  loadSession(sessions[0].id);  // auto-load most recent
} else {
  startNewSession();
}

// After each LLM reply:
await POST(`/api/sessions/${currentSessionId}/messages`, {
  role: 'assistant', content: reply, ui_spec: spec
});

// New Chat button:
const s = await POST('/api/sessions', {});
currentSessionId = s.id;
clearChatThread();
```

### 7.4 localStorage Fallback

If SQLite is unavailable (permissions error, read-only FS), the frontend falls back to `localStorage`:

```javascript
const STORAGE = sessionDbAvailable ? dbStorage : localStorageStorage;
```

This allows the app to run in environments where file writes are restricted (e.g., read-only container).

---

## 8. Embedded Editor

### 8.1 CodeMirror 6 Extension Plan

CodeMirror 6 is already present in the codebase. The plan adds three layers of extensions — each independently deployable:

| Layer | Extensions | Effort | Deliverable |
|-------|-----------|--------|-------------|
| **L1: Multi-file tabs** | `EditorState` per tab; tab bar UI | 3 days | Open N files, switch tabs |
| **L2: Diff view** | `@codemirror/merge` | +2 days | Side-by-side or inline diff |
| **L3: Ghost text** | `@marimo-team/codemirror-ai` | +3 days | Inline AI suggestions |

Full suite: ~1.5–2 weeks. Multi-file tabs alone: 3 days.

### 8.2 Multi-File Tabs Architecture

```javascript
// One EditorState per open file
const editorStates = new Map();  // path → EditorState

function openFile(path, content, proposed_content = null) {
  const state = EditorState.create({
    doc: proposed_content || content,
    extensions: [
      /* language, theme, keymap */
      proposed_content
        ? mergeView(content, proposed_content)  // diff view
        : [],
    ]
  });
  editorStates.set(path, state);
  editorView.setState(state);
  renderTabBar();
}
```

### 8.3 Agent File Operations Pattern (Bolt.new Artifacts)

```
LLM response (coding mode):
{
  "reply": "Here is a todo app...",
  "file_operations": [
    { "path": "todo.py",      "proposed_content": "# ..." },
    { "path": "test_todo.py", "proposed_content": "import pytest\n..." }
  ]
}

Frontend receives file_operations.ready event:
  For each op:
    GET /api/file?path={op.path}  → current content (or "" if new file)
    openFile(op.path, current, op.proposed_content)  → diff view tab

User actions:
  "Accept File" → PUT /api/file { path, content: proposed_content }
  "Accept All"  → PUT /api/file for all pending ops
  "Reject"      → discard proposed_content, revert EditorState

Backend /api/file routes:
  GET  /api/file?path=   → read file (path must be under WORKSPACE_ROOT)
  PUT  /api/file         → write file (path validated: relative, no ../)
```

### 8.4 Path Security

All file paths are validated before read/write:
- Must be relative (no leading `/`)
- No `..` path traversal components
- Resolved against `WORKSPACE_ROOT` using `pathlib.Path.resolve()`
- Resolved path must start with `WORKSPACE_ROOT`

---

## 9. Android / PWA Path

### Phase Now: Progressive Web App (4–8 hours)

| Deliverable | Implementation |
|-------------|---------------|
| `manifest.json` | `name`, `short_name`, `start_url`, `display: standalone`, `icons` |
| Service worker | Cache shell + assets; offline fallback page |
| HTTPS | Required for PWA installation; use local cert or Cloudflare Tunnel for dev |

PWA gives "Add to Home Screen" on Android without an APK. No native access.

### Phase 1: Capacitor APK (1–3 days)

```
npm install @capacitor/core @capacitor/cli @capacitor/android
npx cap init "Unified App" com.workspace.unifiedapp
npx cap add android
npx cap sync
npx cap open android   # opens Android Studio
```

Capacitor wraps the existing web app in a WebView. The FastAPI server runs on the same device or LAN. No code changes to the web app.

**Limitation:** Ollama is not available on Android. Options:
- Connect to Ollama running on the same LAN (developer machine)
- Phase 2: embed on-device LLM

### Phase 2: On-Device LLM via llama.cpp NDK (2–4 weeks)

Ollama does not run on Android. On-device inference requires:
1. **llama.cpp** compiled as Android NDK library (`.so`)
2. **Capacitor plugin** (`capacitor-plugin-llama`) bridging JS ↔ JNI ↔ llama.cpp
3. Model file (~3–7 GB) bundled in app or downloaded on first run
4. **Metal / Vulkan acceleration** on newer Android devices

Implementation note: `phi4-mini` (3.8B, 3GB, MIT) is the recommended on-device model for Phase 2 due to size constraints.

---

## 10. Security Model

### 10.1 No `eval`, No Arbitrary Code Execution

- All LLM-returned `ui_spec` content is validated against JSON Schema before rendering.
- Frontend renderer uses `element.textContent` and `element.setAttribute` — never `innerHTML` for LLM content.
- `file_operations` write only relative paths within `WORKSPACE_ROOT`; no shell commands are executed.
- No `eval()`, `new Function()`, or `exec()` anywhere in the rendering pipeline.

### 10.2 JSON Schema Validation (Backend)

Every `ui_spec` from the LLM passes through `ui_validator.validate_ui_spec()` before being forwarded to the client. On failure, the spec is stripped and only the plain text reply is sent.

### 10.3 URL Allowlists

`video_embed` and `image` URLs are checked against `ALLOWED_URL_DOMAINS` before DOM insertion. Unknown domains cause the component to be replaced with a `[blocked: unrecognized domain]` placeholder.

### 10.4 File Path Traversal Prevention

`PUT /api/file` and `GET /api/file`:
```python
resolved = (WORKSPACE_ROOT / path).resolve()
if not str(resolved).startswith(str(WORKSPACE_ROOT)):
    raise HTTPException(400, "Path traversal not allowed")
```

### 10.5 No LLM Code Execution

The backend never `exec()`s or `eval()`s LLM output. `file_operations` write files to disk; it is the user's responsibility to review and run those files. The app does not auto-run any generated code.

### 10.6 Intent Classification Safety

The LLM classifier has a confidence threshold (< 0.6 → default to "chat"). This prevents a low-confidence `video` or `coding` classification from triggering side effects (proxy call, file writes) without clear user intent.

---

## 11. Existing System Preservation

### 11.1 Orchestrator (Cursor Agent Automation)

The Cursor-based Orchestrator (PROJECT_WORKSPACE.md, agent-automation scripts, MCP server, hooks) is independent of the Orchestrator UI web app. It continues to operate unchanged:

- `mcp-server/server.py` — Stdio MCP server, not modified
- `orchestrator_client/brain.py` — Not modified
- `PROJECT_WORKSPACE.md`, `workflow.yml`, `roles.yml` — Not modified
- `.cursor/rules/`, `.cursor/skills/` — Not modified
- Hooks (`stop_hook.py`, etc.) — Not modified

The Orchestrator UI (`orchestrator_ui/`) is enhanced, not replaced. All existing routes (`/api/chat`, `/api/run-brain`, `/api/config-status`) are preserved with identical behavior.

### 11.2 YouTube Shorts Application

The YouTube Shorts FastAPI app (`youtube-shorts-generator/`) is **not touched** during this migration:

- Its codebase, routes, DB, and tests are unchanged
- It continues to run independently at port 8766
- The unified app connects to it only via HTTP proxy in `video_handler`
- If the YT backend is down, video mode returns a graceful error; no other modes are affected

### 11.3 Migration Strategy

All changes are **additive**:
1. New files: `sessions.py`, `modes.py`, `ui_validator.py`, `modes.json`
2. New routes: `/api/sessions/*`, `/api/file`
3. Extended files: `llm_provider.py` (add `local` branch), `intent.py` (add `detect_mode`), `server.py` (add handlers)
4. Existing routes: unchanged behavior; new params (`session_id`, `Accept: text/event-stream`) are optional

Rollback: remove new files and revert the three extended files. No DB migrations needed (SQLite file is a new file).

---

## 12. Non-Negotiable Constraints

These constraints must be respected in every implementation decision. Any proposed change that violates one of these requires explicit CTO or User approval before proceeding.

| # | Constraint | Rationale |
|---|-----------|-----------|
| C1 | **Local LLM only** (Ollama, default) | Privacy, cost, offline capability. No cloud API calls in the default path. |
| C2 | **One unified app** | Single FastAPI server. No new top-level projects; evolve `orchestrator_ui/`. |
| C3 | **Build on existing** | No replace/rewrite of working components. Extend `llm_provider.py`, `intent.py`, CodeMirror. |
| C4 | **Dynamic UI** | Every non-trivial response should consider returning a `ui_spec`. Plain text is the fallback, not the default. |
| C5 | **No eval / no arbitrary LLM code execution** | Security. LLM output is data, not code. |
| C6 | **No external dependencies beyond Ollama** | Zero new Python packages for core features. SQLite = stdlib. JSON Schema = `jsonschema` (already a common dep). |
| C7 | **YouTube Shorts app untouched** | Isolation. Proxy-only integration. |
| C8 | **Orchestrator (Cursor automation) untouched** | The multi-agent Cursor workflow continues to function. |
| C9 | **Graceful degradation** | Ollama down → error, not crash. No session DB → localStorage. No ui_spec → plain text. |
| C10 | **Backward-compatible API** | Existing `/api/chat` callers work without changes. New behavior requires new params. |
| C11 | **No cloud LLM in unified app** | Provider abstraction is preserved for open-source extensibility, but the unified app enforces local-only at startup (`server.py` guard). Any contribution that routes unified app traffic to a cloud LLM API requires explicit CTO and User approval. |

---

## 13. Implementation Phases

This section maps features to implementation order. Each phase is independently deployable.

### Phase A: Local LLM + Provider Abstraction (~2 days)

**Goal:** `ORCHESTRATOR_LLM_PROVIDER=local` works end-to-end.

- [ ] Extend `llm_provider.py`: add `local` branch (reuse OpenAI SDK with `base_url`)
- [ ] Update `.env.example` with `ORCHESTRATOR_LLM_PROVIDER`, `ORCHESTRATOR_LLM_BASE_URL`, `ORCHESTRATOR_LLM_MODEL`
- [ ] Update `ORCHESTRATOR_SETUP.md` with Ollama setup instructions
- [ ] Smoke test: `chat_sync()` with `provider=local` returns a reply

**Dependencies:** None. Can start immediately.

---

### Phase B: Mode Registry + Intent Routing (~2 days)

**Goal:** Every message is classified; correct handler is called.

- [ ] Create `orchestrator_ui/modes.py` (`ModeDefinition` dataclass, registry, loader)
- [ ] Create `orchestrator_ui/modes.json` (5 initial modes)
- [ ] Extend `orchestrator_client/intent.py`: add `detect_mode()`, keep `detect_intent()` as shim
- [ ] Wire mode routing in `server.py`: `POST /api/chat` calls `detect_mode()` then dispatches
- [ ] Unit tests for classifier: rule-based fast path + LLM fallback mock

**Dependencies:** Phase A (LLM needed for LLM fallback classifier).

---

### Phase C: Session Persistence (~1 day)

**Goal:** Conversations survive page reload.

- [ ] Create `orchestrator_ui/sessions.py` (SQLite, `Sessions` and `Messages` classes)
- [ ] Add routes: `GET/POST /api/sessions`, `GET/PATCH/DELETE /api/sessions/{id}`, `POST /api/sessions/{id}/messages`
- [ ] Extend `POST /api/chat` to accept optional `session_id`, append messages post-reply
- [ ] Frontend: on load → fetch sessions → load latest; session list sidebar; New Chat button
- [ ] localStorage fallback

**Dependencies:** None (independent of A and B; can parallelize).

---

### Phase D: Dynamic UI Subsystem (~4 days)

**Goal:** LLM can return `ui_spec`; frontend renders rich cards.

- [ ] Create `orchestrator_ui/ui_validator.py` (JSON Schema, URL allowlist)
- [ ] Extend LLM system prompts to describe `ui_spec` format when `mode.supports_ui_spec`
- [ ] Backend: parse `ui_spec` from LLM JSON response, validate, strip on failure
- [ ] Frontend: `renderer.js` with 13 component renderers
- [ ] Inline artifact card in chat thread + Canvas tab
- [ ] SSE event `ui_spec.ready`

**Dependencies:** Phase B (mode routing needed to know when to prompt for ui_spec).

---

### Phase E: Embedded Editor + File Operations (~1 week)

**Goal:** Coding mode opens multi-file diff view; user can accept/reject.

- [ ] Extend CodeMirror 6: multi-file tabs (`EditorState` per file)
- [ ] Add `@codemirror/merge` for diff view
- [ ] Backend: `GET /api/file`, `PUT /api/file` with path security
- [ ] Coding mode handler: parse `file_operations` from LLM, emit `file_operations.ready`
- [ ] Frontend: accept/reject UI

**Dependencies:** Phase B (coding mode handler).

---

### Phase F: PWA Packaging (4–8 hours)

**Goal:** "Add to Home Screen" on Android.

- [ ] `manifest.json` in `orchestrator_ui/static/`
- [ ] Service worker (`sw.js`) with shell cache
- [ ] HTTPS setup note in README

**Dependencies:** None (can do anytime after frontend stabilizes).

---

### Phase G: Local-Only Video Pipeline (Future)

**Goal:** Replace all cloud API calls in the video pipeline with locally hosted equivalents so the entire unified app runs without any external data dependencies.

**Deliverables:**
- [ ] Local LLM (Ollama) for script generation and research (replacing OpenAI/Anthropic in `youtube-shorts-generator`)
- [ ] Local TTS: Coqui TTS, Kokoro, or Piper (replacing ElevenLabs) — research required to select best option
- [ ] Local video generation: AnimateDiff or comparable local model (replacing Runway) — research required
- [ ] Local YouTube proxy or optional manual upload (replacing YouTube API for data reasons — user decides)
- [ ] Preserved interface: `video_handler` proxy remains; only the `youtube-shorts-generator` internals change
- [ ] Acceptance criteria: a full video can be generated end-to-end with `OLLAMA_ONLY=true` and no cloud API key set

**Dependencies:** Phases A–E complete; user approves scope.  
**Effort estimate:** 3–6 weeks (research-heavy; local video generation is the hardest part).  
**Owner roles:** Researcher (local TTS + video options), Architect (design), Lead Engineer + Junior Engineers (implementation).

---

## 14. Open Questions for CTO / User

The following decisions are outside Architect authority and require CTO or User approval before implementation:

| # | Question | Options | Impact |
|---|----------|---------|--------|
| Q1 | **Default provider at launch** | `local` (Ollama required) vs `anthropic` (cloud, current) | Affects onboarding friction and privacy posture |
| Q2 | **jsonschema dependency** | Already in many Python envs; add explicitly to `requirements.txt`? | Minor; C6 constraint technically allows it |
| Q3 | **Canvas tab vs inline-only** | Full Canvas tab (new UI area) vs inline artifact cards only | Scope of Phase D frontend work |
| Q4 | **Capacitor APK scope** | Phase F = PWA only, or include Capacitor APK? | +1–3 days effort |
| Q5 | **Session DB location** | Inside `orchestrator_ui/` (current proposal) vs user-configurable path | Minor; affects multi-instance setups |
| Q6 | **Ghost text (Phase E L3)** | Include `@marimo-team/codemirror-ai` (ghost text) in scope? | +3 days; adds npm dependency |

---

## Appendix A: File Map (New and Modified Files)

```
agent-automation/
├── orchestrator_client/
│   ├── llm_provider.py           MODIFIED  add `local` provider branch
│   └── intent.py                 MODIFIED  add detect_mode(), keep detect_intent() shim
├── orchestrator_ui/
│   ├── server.py                 MODIFIED  add mode dispatch, file routes, session_id param
│   ├── modes.py                  NEW       ModeDefinition dataclass + registry
│   ├── modes.json                NEW       5 initial mode definitions
│   ├── sessions.py               NEW       SQLite sessions + messages
│   ├── ui_validator.py           NEW       JSON Schema validation + URL allowlist
│   ├── .env.example              MODIFIED  add ORCHESTRATOR_LLM_* vars
│   └── static/
│       ├── renderer.js           NEW       Dynamic UI component renderers
│       ├── editor.js             NEW       CodeMirror multi-file tabs + diff
│       ├── manifest.json         NEW       PWA manifest
│       └── sw.js                 NEW       Service worker
└── docs/
    └── ARCHITECTURE.md           NEW       This document
```

**Unchanged (zero modifications):**
```
youtube-shorts-generator/         UNTOUCHED
agent-automation/mcp-server/      UNTOUCHED
agent-automation/orchestrator_client/brain.py       UNTOUCHED
agent-automation/orchestrator_client/context_loader.py  UNTOUCHED
.cursor/rules/, .cursor/skills/   UNTOUCHED
PROJECT_WORKSPACE.md              UNTOUCHED (runtime state doc)
workflow.yml, roles.yml           UNTOUCHED
```

---

## Appendix B: Key Design Decisions Log

| Decision | Chosen | Rejected alternatives | Reason |
|----------|--------|----------------------|--------|
| LLM backend | Ollama (local) | Cloud APIs, LM Studio | Privacy, cost, offline; Metal acceleration on Apple Silicon |
| OpenAI SDK for Ollama | Reuse existing SDK with `base_url` | New HTTP client | Zero new code; Ollama is OpenAI-compatible |
| UI renderer | Vanilla JS, registered components | React, eval-based | No new framework dep; security |
| Session storage | SQLite (stdlib) | PostgreSQL, Redis, file JSON | Zero deps; sufficient for single-user |
| YT Shorts integration | HTTP proxy (Option B) | Import, fork, or merge | Isolation; YT app untouched |
| Intent classifier | Hybrid (rules + LLM fallback) | LLM-only, rules-only | Speed (fast path) + flexibility (fallback) |
| Editor | CodeMirror 6 (extend existing) | Monaco, replace with new | Already in codebase; web-first |
| Android packaging | PWA now, Capacitor later | Ollama Android (N/A), React Native | Incremental; Ollama not on Android |

---

*Architecture document produced by Architect. Ready for CTO review and User approval before development starts.*
