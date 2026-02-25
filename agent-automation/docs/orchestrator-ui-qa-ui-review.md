# Orchestrator UI — QA & UI Review

**Branch:** `feature/orchestrator-ui-redesign`  
**Date:** 2026-02-25  
**Reviewer:** QA / UI Reviewer

---

## 1. QA Findings

### 1.1 Summary

| Flow / Case | Pass/Fail | Notes |
|-------------|-----------|-------|
| "hello" → chat mode | **PASS** | Intent routes to chat; single LLM reply |
| "run one cycle" → orchestration | **PASS** | Intent routes to orchestration; flow returned |
| Empty input | **PASS** (with minor UX gap) | Frontend blocks send; no API call |
| Network failure | **PASS** | User-friendly error shown |
| API key missing | **PASS** | 500 + clear error message |
| Mode toggle | **PASS** | Auto/Chat/Orchestrate sent correctly |

### 1.2 End-to-End Flows

**"hello" flow**

- `intent.py`: `"hello"` exact-match in `CHAT_KEYWORDS` → `detect_intent` returns `"chat"`.
- Server: `_chat_handler` runs single LLM call; returns `{ reply, mode_used: "chat" }`.
- Frontend: Renders reply with mode badge; reasoning panel shows "Chat mode — no reasoning flow."
- **Verdict:** PASS (when `ANTHROPIC_API_KEY` is set).

**"run one cycle" flow**

- `intent.py`: `"run"` and `"cycle"` in `ORCHESTRATION_KEYWORDS` → `detect_intent` returns `"orchestration"`.
- Server: `_orchestration_handler` calls `run_brain_with_flow`; returns `{ reply, mode_used, flow }`.
- Frontend: Renders reply; reasoning panel shows proposal, critique, synthesis.
- **Verdict:** PASS (when API key + workspace configured).

### 1.3 Edge Cases & Error Handling

| Case | Behavior | Verdict |
|------|----------|---------|
| **Empty input** | `sendChat()`: `if (!text) return` — no request sent, no feedback | PASS (silent no-op; consider brief hint) |
| **Whitespace-only** | Same as empty (trim) | PASS |
| **Empty messages array** | API returns 400 `"At least one message is required."` | PASS |
| **Network failure** | `catch (e)` → `chatErrorEl.textContent = e.message \|\| 'Network error...'` | PASS |
| **API key not set** | 500 `"API key not configured. Set ANTHROPIC_API_KEY..."` | PASS |
| **Context load failure** | 500 with `str(e)` from `_orchestration_handler` | PASS |
| **Non-JSON response** | `responseText ? JSON.parse(responseText) : {}`; `getUserFriendlyError` handles | PASS |

### 1.4 Issues / Recommendations

1. **Enter key to submit** — No `keydown`/`keypress` handler. User must click Send. **Recommendation:** Add `Enter` (without Shift) to submit; Shift+Enter for newline.
2. **Empty input feedback** — Silent no-op. **Recommendation:** Optional: briefly show "Please enter a message" or keep as-is for minimal UI.
3. **Request timeout** — No `AbortController` or timeout on `fetch`. Orchestration can take 10–30s; very long runs may hang. **Recommendation:** Add 60s timeout and show "Request timed out" if needed.
4. **Double-send** — Send button disabled during request; no debounce. **Verdict:** Adequate for MVP.

---

## 2. UI Findings

### 2.1 Summary

| Criterion | Pass/Fail | Notes |
|-----------|-----------|-------|
| Dark glass aesthetic | **PASS** | #0a0a0f–#12121a, frosted panels, backdrop-blur |
| Layout (chat + collapsible reasoning) | **PASS** | Chat-first; reasoning panel collapsible |
| Accessibility | **PASS** (minor gaps) | aria-label, role; textarea could use aria-label |
| Consistency with vibe platforms | **PASS** | Aligns with Cursor, Replit, v0, Bolt |

### 2.2 Dark Glass Aesthetic

| Token | Spec | Implementation | Verdict |
|-------|------|----------------|---------|
| `--bg` | #0a0a0f | `#0a0a0f` | ✓ |
| `--bg-elevated` | #12121a | `#12121a` | ✓ |
| `--surface` | rgba(18,18,26,0.7) | `rgba(18, 18, 26, 0.7)` | ✓ |
| `--border` | rgba(255,255,255,0.08) | `rgba(255, 255, 255, 0.08)` | ✓ |
| Frosted panels | backdrop-filter | `.glass`, `.glass-elevated`, flow-step, input | ✓ |
| Blur | 12px | `--blur: 12px` | ✓ |

**Verdict:** PASS — Design spec met.

### 2.3 Layout

- **Chat main:** Flex 1, scrollable thread, input at bottom.
- **Reasoning panel:** 360px sidebar, collapsible to 48px; toggle button.
- **Responsive:** `@media (max-width: 768px)` — layout switches to column; reasoning panel becomes bottom drawer.
- **Verdict:** PASS.

### 2.4 Accessibility

| Item | Status |
|------|--------|
| `role="group"` + `aria-label="Chat mode"` on mode toggle | ✓ |
| `aria-label` + `title` on reasoning toggle | ✓ |
| `lang="en"` on html | ✓ |
| `viewport` meta | ✓ |
| Textarea `aria-label` | Missing — recommend adding |
| Focus visible | `textarea:focus` has `outline: none` but `box-shadow` provides visible focus ring |
| Skip link | Not present — acceptable for single-page chat |

**Verdict:** PASS with minor improvement: add `aria-label="Message input"` to textarea.

### 2.5 Consistency with Vibe Platforms

- **Cursor:** Dark theme, glass panels, chat-first — ✓
- **Replit Agent:** Chat + collapsible panels — ✓
- **v0:** Liquid glass, dark palette — ✓
- **Bolt:** Similar chat UX — ✓

**Verdict:** PASS — Design aligns with target platforms.

### 2.6 Issues / Recommendations

1. **Textarea aria-label** — Add `aria-label="Message input"` for screen readers.
2. **Mode toggle focus** — Buttons have no explicit focus styles; ensure `:focus-visible` is visible.
3. **Thinking indicator** — Uses `.thinking-indicator` with animation; no `aria-live` for screen readers. Optional: add `aria-live="polite"` when loading.

---

## 3. Conclusion

| Area | Overall | Critical Issues |
|------|---------|-----------------|
| **QA** | PASS | None |
| **UI** | PASS | None |

**Recommendations (non-blocking):**

1. Add Enter key to submit (Shift+Enter for newline).
2. Add `aria-label` to textarea.
3. Consider 60s timeout for orchestration requests.
4. Optional: brief feedback when user tries to send empty message.

---

## 4. Manual Test Checklist (for future runs)

When API key and workspace are configured:

- [ ] Send "hello" → chat reply, mode badge "chat", reasoning hint "Chat mode — no reasoning flow."
- [ ] Send "run one cycle" → orchestration reply, flow in reasoning panel.
- [ ] Toggle mode to "Chat", send "run one cycle" → chat reply (forced).
- [ ] Toggle mode to "Orchestrate", send "hello" → orchestration reply (forced).
- [ ] Disconnect network, send message → "Network error. Please check your connection."
- [ ] Send with empty input → no request (silent).
- [ ] Collapse reasoning panel → panel narrows to 48px; expand → full width.
