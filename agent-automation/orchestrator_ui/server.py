"""
Orchestrator UI backend: FastAPI server that invokes run_brain_with_flow.
Allows configuring API keys via env or request body (never logged).
Returns proposal, critique, synthesis, final_decision as structured JSON.

MCP: Uses Stdio transport (subprocess). In-process MCP (Phase 4) is documented
for future use; no implementation change for now. See README "MCP: Stdio vs In-Process".
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Add agent-automation to path for orchestrator_client
_ui_dir = Path(__file__).resolve().parent
_agent_automation = _ui_dir.parent
load_dotenv(_ui_dir / ".env", override=True)
load_dotenv(_agent_automation / ".env", override=True)

# Diagnostic: log if API key still unset after load_dotenv (remove after verification)
_env_ui = _ui_dir / ".env"
_env_aa = _agent_automation / ".env"
if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ORCHESTRATOR_LLM_API_KEY")):
    print(
        "[Orchestrator UI] ANTHROPIC_API_KEY/ORCHESTRATOR_LLM_API_KEY unset after load_dotenv. "
        f"orchestrator_ui/.env exists={_env_ui.exists()}, agent-automation/.env exists={_env_aa.exists()}",
        file=sys.stderr,
    )
if str(_agent_automation) not in sys.path:
    sys.path.insert(0, str(_agent_automation))

import json as _json
from typing import Literal, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from orchestrator_client.brain import run_brain_with_flow, run_brain_with_flow_stream
from orchestrator_client.context_loader import load_context
from workspace_config import get_workspace_root

from orchestrator_ui.intent import detect_intent, get_slash_commands_for_workspace, get_slash_commands_list
from orchestrator_ui.tree import build_tree, resolve_path_under_root, validate_path_under_root


def _load_hooks_config(root: Path) -> dict:
    """Load hooks config from .cursor/hooks.json. Returns { hooks: {...}, lifecycle?: [...] }."""
    hooks_json = root / ".cursor" / "hooks.json"
    out: dict = {"hooks": {}, "source": None}
    if hooks_json.exists():
        try:
            data = _json.loads(hooks_json.read_text(encoding="utf-8"))
            out["hooks"] = data.get("hooks") or {}
            out["source"] = str(hooks_json.relative_to(root))
        except (OSError, _json.JSONDecodeError):
            pass
    # Lifecycle hooks from custom-ide-roadmap Phase 5: before_cycle, after_cycle, before_delegate, after_delegate
    out["lifecycle"] = [
        {"name": "before_cycle", "description": "Before orchestrator cycle starts"},
        {"name": "after_cycle", "description": "After orchestrator cycle completes"},
        {"name": "before_delegate", "description": "Before delegating to subagent"},
        {"name": "after_delegate", "description": "After subagent returns"},
    ]
    return out


app = FastAPI(
    title="Orchestrator UI",
    description="Run the A2A brain (propose → critique → synthesize) outside Cursor",
)

# Mount static files if they exist
_static_dir = _ui_dir / "static"
if _static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")


class RunBrainRequest(BaseModel):
    """Request body for /api/run-brain. API key is optional if set via env."""

    anthropic_api_key: Optional[str] = Field(
        default=None,
        description="Anthropic API key (optional if ANTHROPIC_API_KEY or ORCHESTRATOR_LLM_API_KEY is set)",
    )
    workspace_snippet: Optional[str] = Field(
        default=None,
        description="Optional PROJECT_WORKSPACE.md snippet to inject into context",
    )
    pending_prompt: Optional[dict] = Field(
        default=None,
        description="Optional pending prompt (stub for get_pending_orchestrator_prompt)",
    )
    workspace_status: Optional[dict] = Field(
        default=None,
        description="Optional workspace status (stub for get_workspace_status)",
    )
    workflow_config: Optional[dict] = Field(
        default=None,
        description="Optional workflow config (stub for get_workflow_config)",
    )


class ChatMessage(BaseModel):
    """Single chat message. Role and content only; no API key or workspace in body."""

    role: Literal["user", "assistant"]
    content: str


class FileWriteRequest(BaseModel):
    """Request body for PUT /api/file."""

    path: str = Field(..., description="Relative path under workspace root")
    content: str = Field(default="", description="File content to write")


class ChatRequest(BaseModel):
    """Request for POST /api/chat. API key and workspace read only from env."""

    messages: list[ChatMessage] = Field(..., description="Conversation history")
    mode: Literal["auto", "chat", "orchestration"] = Field(
        default="auto",
        description="Force mode or let server infer (auto)",
    )
    include_flow: bool = Field(default=True, description="Include proposal, critique, synthesis in response")


def _stub_context() -> dict:
    """Build stub context when MCP unavailable (brain-only mode)."""
    return {
        "pending_prompt": {},
        "workspace_status": {
            "next_actions": "Run one cycle: get_workspace_status, read PROJECT_WORKSPACE.md, decide next step, delegate if needed.",
            "phase": "dev",
            "pending_approvals": 0,
        },
        "workflow_config": {},
        "workspace_snippet": "(Stub context — no MCP. Set workspace_snippet in request to provide PROJECT_WORKSPACE.md content.)",
    }


def _get_project_workspace_snippet(max_chars: int = 8000) -> str:
    """Read a snippet of PROJECT_WORKSPACE.md for context."""
    root = get_workspace_root()
    path = root / "PROJECT_WORKSPACE.md"
    if not path.exists():
        return "(PROJECT_WORKSPACE.md not found)"
    text = path.read_text(encoding="utf-8")
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[... truncated ...]"


CHAT_SYSTEM_PROMPT = """You are the Orchestrator assistant. Reply briefly to greetings, thanks, and simple questions. For task-related requests, suggest the user say 'run one cycle' or use a slash command like /lead-engineer to get started. Do not delegate or run cycles yourself; suggest the user do so."""


def _chat_handler(messages: list, api_key: str) -> dict:
    """Single LLM call for chat mode. Returns { reply, mode_used: "chat" }."""
    from anthropic import Anthropic

    from orchestrator_client.config import get_proposer_model

    client = Anthropic(api_key=api_key)
    response = client.messages.create(
        model=get_proposer_model(),
        max_tokens=1024,
        system=CHAT_SYSTEM_PROMPT,
        messages=[{"role": m.role, "content": m.content} for m in messages],
    )
    reply = ""
    if response.content:
        parts = [b.text for b in response.content if hasattr(b, "text")]
        reply = "\n".join(parts) if parts else ""
    return {"reply": reply, "mode_used": "chat"}


async def _chat_handler_stream(messages: list, api_key: str):
    """Stream chat reply token-by-token. Yields SSE events: reply.chunk, reply.done."""
    from anthropic import AsyncAnthropic

    from orchestrator_client.config import get_proposer_model

    client = AsyncAnthropic(api_key=api_key)
    async with client.messages.stream(
        model=get_proposer_model(),
        max_tokens=1024,
        system=CHAT_SYSTEM_PROMPT,
        messages=[{"role": m.role, "content": m.content} for m in messages],
    ) as stream:
        async for event in stream:
            text = ""
            if getattr(event, "type", None) == "content_block_delta":
                delta = getattr(event, "delta", None)
                if delta and getattr(delta, "type", None) == "text_delta":
                    text = getattr(delta, "text", "") or ""
            if text:
                yield f"data: {_json.dumps({'type': 'reply.chunk', 'content': text})}\n\n"
    yield f"data: {_json.dumps({'type': 'reply.done'})}\n\n"


async def _orchestration_handler_stream(messages: list, api_key: str):
    """Stream orchestration flow: flow.proposal, flow.critique, flow.synthesis, reply.chunk, reply.done."""
    context = _stub_context()
    root = get_workspace_root()
    if (root / "PROJECT_WORKSPACE.md").exists():
        context["workspace_snippet"] = _get_project_workspace_snippet()
    if messages:
        context["user_message"] = messages[-1].content

    try:
        from orchestrator_client.mcp_client import create_mcp_session, run_orchestrator_tools

        async with create_mcp_session() as (_session, call_tool):
            tool_results = await run_orchestrator_tools(call_tool, workspace_root=str(root))
            context["pending_prompt"] = tool_results.get("pending_prompt", {})
            context["workspace_status"] = tool_results.get("workspace_status", {})
            context["workflow_config"] = tool_results.get("workflow_config", {})
    except Exception:
        pass

    ctx = load_context()
    async for event_type, content in run_brain_with_flow_stream(
        ctx.system_message, context, api_key_override=api_key
    ):
        yield f"data: {_json.dumps({'type': event_type, 'content': content})}\n\n"


async def _orchestration_handler(
    messages: list,
    api_key: str,
    include_flow: bool,
) -> dict:
    """Build context, inject user_message, call run_brain_with_flow. Returns { reply, mode_used, flow }."""
    context = _stub_context()
    root = get_workspace_root()
    if (root / "PROJECT_WORKSPACE.md").exists():
        context["workspace_snippet"] = _get_project_workspace_snippet()
    if messages:
        context["user_message"] = messages[-1].content

    # Try MCP for live context; fallback to stub when unavailable
    try:
        from orchestrator_client.mcp_client import create_mcp_session, run_orchestrator_tools

        async with create_mcp_session() as (_session, call_tool):
            tool_results = await run_orchestrator_tools(call_tool, workspace_root=str(root))
            context["pending_prompt"] = tool_results.get("pending_prompt", {})
            context["workspace_status"] = tool_results.get("workspace_status", {})
            context["workflow_config"] = tool_results.get("workflow_config", {})
    except Exception:
        # MCP unavailable: subprocess fail, timeout, or mcp not installed — keep stub
        pass

    try:
        ctx = load_context()
    except Exception as e:
        raise RuntimeError(f"Failed to load context: {e!s}") from e
    result = run_brain_with_flow(
        ctx.system_message, context, api_key_override=api_key
    )
    reply = result.get("final_decision", "")
    out = {
        "reply": reply,
        "mode_used": "orchestration",
    }
    if include_flow:
        out["flow"] = {
            "proposal": result.get("proposal", ""),
            "critique": result.get("critique", ""),
            "synthesis": result.get("synthesis", ""),
        }
    return out


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the orchestrator UI."""
    index_path = _static_dir / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return HTMLResponse(
        "<h1>Orchestrator UI</h1><p>API running. Add static/index.html for UI.</p>"
        "<p>POST /api/run-brain with optional anthropic_api_key, workspace_snippet.</p>"
    )


def _api_key_configured() -> bool:
    return bool(
        os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ORCHESTRATOR_LLM_API_KEY")
    )


def _workspace_configured() -> bool:
    root = get_workspace_root()
    return (root / "PROJECT_WORKSPACE.md").exists()


@app.get("/api/status")
async def status():
    """API status (legacy). Prefer GET /api/config-status for UI."""
    return {
        "status": "ok",
        "api_key_from_env": _api_key_configured(),
        "project_workspace_exists": _workspace_configured(),
    }


@app.get("/api/config-status")
async def config_status():
    """Config status for UI: booleans only, no secrets."""
    return {
        "api_key_configured": _api_key_configured(),
        "workspace_configured": _workspace_configured(),
    }


@app.get("/api/hooks")
async def get_hooks():
    """
    Hooks config (Phase 5 Custom User Actions).
    Returns hooks from .cursor/hooks.json and lifecycle hook definitions.
    """
    root = get_workspace_root()
    return _load_hooks_config(root)


@app.get("/api/slash-commands")
async def slash_commands():
    """
    Slash commands from roles.yml (Phase 5 Custom User Actions).
    Returns list of { slash, role, display_name } for roles with slash.
    """
    root = get_workspace_root()
    commands = get_slash_commands_list(root)
    return {"commands": commands}


def _discover_rules(root: Path) -> list[dict]:
    """Discover rules from .cursor/rules/*.mdc. Returns [{ name, path }]."""
    rules_dir = root / ".cursor" / "rules"
    if not rules_dir.exists() or not rules_dir.is_dir():
        return []
    result = []
    for p in sorted(rules_dir.glob("*.mdc")):
        if p.is_file():
            try:
                rel = p.relative_to(root)
                path_str = str(rel).replace("\\", "/")
            except ValueError:
                path_str = str(p)
            result.append({"name": p.stem, "path": path_str})
    return result


@app.get("/api/rules")
async def get_rules():
    """
    Rules from workspace config (Phase 5 Custom User Actions).
    Returns { rules: [{ name, path }] } for .cursor/rules/*.mdc.
    """
    root = get_workspace_root()
    rules = _discover_rules(root)
    return {"rules": rules}


def _discover_skills(root: Path) -> list[dict]:
    """Discover skills from .cursor/skills/*/SKILL.md. Returns [{ name, path, description? }]."""
    skills_dir = root / ".cursor" / "skills"
    if not skills_dir.exists() or not skills_dir.is_dir():
        return []
    result = []
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists() or not skill_md.is_file():
            continue
        name = skill_dir.name
        try:
            rel = skill_md.relative_to(root)
            path_str = str(rel).replace("\\", "/")
        except ValueError:
            path_str = str(skill_md)
        description = None
        try:
            text = skill_md.read_text(encoding="utf-8")
            lines = text.strip().split("\n")
            for line in lines[:10]:
                line = line.strip()
                if line.startswith("# "):
                    description = line.lstrip("# ").strip()
                    break
                if line.startswith("**") and ":" in line:
                    # e.g. **Name**: lead-engineer
                    parts = line.split(":", 1)
                    if len(parts) == 2 and "name" in parts[0].lower():
                        description = parts[1].strip().strip("*")
                        break
        except OSError:
            pass
        result.append({"name": name, "path": path_str, "description": description})
    return result


@app.get("/api/skills")
async def get_skills():
    """
    Skills registry (Phase 5 Custom User Actions).
    Discovers .cursor/skills/*/SKILL.md. Returns { skills: [{ name, path, description? }] }.
    """
    root = get_workspace_root()
    skills = _discover_skills(root)
    return {"skills": skills}


@app.get("/api/tree")
async def get_tree(
    path: Optional[str] = None,
    depth: int = 3,
    lazy: bool = False,
):
    """
    Return directory tree for workspace (Phase 2 Project Structure Panel).
    Query params: path (optional, default root), depth (optional, default 5),
    lazy (optional, default false). For lazy=true, dir children omitted until
    expanded via GET /api/tree?path=...
    Response: list of nodes { name, path, type: "file"|"dir", children? }.
    """
    root = get_workspace_root()
    if not root.exists():
        raise HTTPException(status_code=404, detail="Workspace root not found")
    target = resolve_path_under_root(root, path)
    if target is None:
        # Path traversal or invalid → 400; nonexistent path → 404
        if path and ".." not in (path or "") and not (root / path.strip().lstrip("/.")).exists():
            raise HTTPException(status_code=404, detail="Path not found")
        raise HTTPException(
            status_code=400,
            detail="Invalid path: must be under workspace root and not use path traversal (..)",
        )
    depth = max(1, min(depth, 10))
    children = build_tree(root, target, depth, lazy)
    try:
        rel = target.relative_to(root)
        path_str = str(rel).replace("\\", "/") if str(rel) != "." else "."
    except ValueError:
        path_str = "."
    return {
        "name": target.name or root.name,
        "path": path_str,
        "type": "dir",
        "children": children,
    }


# Extension → language hint for CodeMirror (Phase 3 Code Editor)
_EXT_TO_LANGUAGE = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".jsx": "jsx",
    ".json": "json",
    ".md": "markdown",
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".scss": "scss",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".sh": "shell",
    ".bash": "shell",
    ".sql": "sql",
    ".xml": "xml",
    ".toml": "toml",
    ".ini": "ini",
}


def _language_from_path(path: Path) -> str | None:
    """Return language hint from file extension, or None."""
    return _EXT_TO_LANGUAGE.get(path.suffix.lower())


@app.get("/api/file")
async def get_file(path: str):
    """
    Read file content (Phase 3 Code Editor).
    Query param: path (required, relative to workspace root).
    Returns { path, content, language? }. Rejects path traversal (400). 404 if not found.
    """
    root = get_workspace_root()
    if not root.exists():
        raise HTTPException(status_code=404, detail="Workspace root not found")
    resolved = validate_path_under_root(root, path, must_exist=False)
    if resolved is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid path: must be under workspace root and not use path traversal (..)",
        )
    if not resolved.exists():
        raise HTTPException(status_code=404, detail="File not found")
    if resolved.is_dir():
        raise HTTPException(status_code=404, detail="Path is a directory, not a file")
    try:
        content = resolved.read_text(encoding="utf-8")
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {e!s}")
    try:
        rel = resolved.relative_to(root)
        path_str = str(rel).replace("\\", "/")
    except ValueError:
        path_str = path
    language = _language_from_path(resolved)
    return {"path": path_str, "content": content, "language": language}


@app.put("/api/file")
async def put_file(req: FileWriteRequest):
    """
    Write file content (Phase 3 Code Editor).
    Body: { path, content }. Creates parent dirs if needed.
    Rejects path traversal (400). Returns 200 on success.
    """
    root = get_workspace_root()
    if not root.exists():
        raise HTTPException(status_code=404, detail="Workspace root not found")
    resolved = validate_path_under_root(root, req.path, must_exist=False)
    if resolved is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid path: must be under workspace root and not use path traversal (..)",
        )
    if resolved.exists() and resolved.is_dir():
        raise HTTPException(
            status_code=400,
            detail="Path is a directory; cannot overwrite with file content",
        )
    try:
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(req.content, encoding="utf-8")
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Failed to write file: {e!s}")
    try:
        rel = resolved.relative_to(root)
        path_str = str(rel).replace("\\", "/")
    except ValueError:
        path_str = req.path
    return {"path": path_str, "ok": True}


def _wants_sse(accept: str | None) -> bool:
    """True if client accepts text/event-stream."""
    if not accept:
        return False
    return "text/event-stream" in accept.lower()


@app.post("/api/chat")
async def chat(req: ChatRequest, request: Request):
    """
    Dual-mode: chat (1 LLM) or orchestration (run_brain_with_flow).
    mode=auto: run intent detection and route. mode=chat|orchestration: force.
    Accept: text/event-stream → SSE stream (reply.chunk, reply.done; flow.* for orchestration).
    Else → JSON { reply, mode_used } and optionally flow when orchestration.
    """
    if not req.messages or len(req.messages) == 0:
        return JSONResponse(
            status_code=400,
            content={"error": "At least one message is required."},
        )
    api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ORCHESTRATOR_LLM_API_KEY")
    if not api_key:
        return JSONResponse(
            status_code=500,
            content={"error": "API key not configured. Set ANTHROPIC_API_KEY (or ORCHESTRATOR_LLM_API_KEY) in the environment."},
        )

    mode = req.mode
    if mode == "auto":
        root = get_workspace_root()
        slash_commands = get_slash_commands_for_workspace(root)
        last_content = req.messages[-1].content if req.messages else ""
        mode = detect_intent(last_content, slash_commands)

    stream_sse = _wants_sse(request.headers.get("Accept"))

    if stream_sse and mode == "chat":
        return StreamingResponse(
            _chat_handler_stream(req.messages, api_key),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
        )

    if stream_sse and mode != "chat":
        return StreamingResponse(
            _orchestration_handler_stream(req.messages, api_key),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
        )

    try:
        if mode == "chat":
            out = _chat_handler(req.messages, api_key)
        else:
            out = await _orchestration_handler(req.messages, api_key, req.include_flow)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )
    return out


@app.post("/api/run-brain")
async def run_brain_endpoint(req: RunBrainRequest):
    """
    Run the orchestrator brain: propose → critique → synthesize.
    Returns proposal, critique, synthesis, final_decision as structured JSON.
    API key: from request body or env (ANTHROPIC_API_KEY, ORCHESTRATOR_LLM_API_KEY).
    Never logged.
    """
    api_key = req.anthropic_api_key
    if not api_key:
        api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get(
            "ORCHESTRATOR_LLM_API_KEY"
        )
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="API key required. Set anthropic_api_key in request body or ANTHROPIC_API_KEY / ORCHESTRATOR_LLM_API_KEY in env.",
        )

    # Build context from request or stubs
    context = _stub_context()
    if req.workspace_snippet is not None:
        context["workspace_snippet"] = req.workspace_snippet
    elif (get_workspace_root() / "PROJECT_WORKSPACE.md").exists():
        context["workspace_snippet"] = _get_project_workspace_snippet()
    if req.pending_prompt is not None:
        context["pending_prompt"] = req.pending_prompt
    if req.workspace_status is not None:
        context["workspace_status"] = req.workspace_status
    if req.workflow_config is not None:
        context["workflow_config"] = req.workflow_config

    try:
        ctx = load_context()
        result = run_brain_with_flow(
            ctx.system_message, context, api_key_override=api_key
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8765)
