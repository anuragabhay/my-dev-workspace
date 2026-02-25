"""
Orchestrator UI backend: FastAPI server that invokes run_brain_with_flow.
Allows configuring API keys via env or request body (never logged).
Returns proposal, critique, synthesis, final_decision as structured JSON.
"""

import os
import sys
from pathlib import Path

# Add agent-automation to path for orchestrator_client
_ui_dir = Path(__file__).resolve().parent
_agent_automation = _ui_dir.parent
if str(_agent_automation) not in sys.path:
    sys.path.insert(0, str(_agent_automation))

from typing import Literal, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from orchestrator_client.brain import run_brain_with_flow
from orchestrator_client.context_loader import load_context
from workspace_config import get_workspace_root

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


class ChatRequest(BaseModel):
    """Request for POST /api/chat. API key and workspace read only from env."""

    messages: list[ChatMessage] = Field(..., description="Conversation history")
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


@app.post("/api/chat")
async def chat(req: ChatRequest):
    """
    Run one orchestrator cycle: build context from env, run brain, return reply and flow.
    API key and workspace are read only from env; no key or snippet in request body.
    Returns 400 for invalid request (e.g. empty messages), 500 on brain/context failure
    with body { "error": "human-readable message" }.
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
    context = _stub_context()
    root = get_workspace_root()
    if (root / "PROJECT_WORKSPACE.md").exists():
        context["workspace_snippet"] = _get_project_workspace_snippet()
    try:
        ctx = load_context()
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to load context: {e!s}"},
        )
    try:
        result = run_brain_with_flow(
            ctx.system_message, context, api_key_override=api_key
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Brain run failed: {e!s}"},
        )
    reply = result.get("final_decision", "")
    out = {
        "reply": reply,
        "flow": {
            "proposal": result.get("proposal", ""),
            "critique": result.get("critique", ""),
            "synthesis": result.get("synthesis", ""),
        },
    }
    if req.include_flow is False:
        out.pop("flow", None)
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
