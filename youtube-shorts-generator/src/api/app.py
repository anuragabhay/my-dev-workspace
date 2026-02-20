"""
FastAPI application for YouTube Shorts Generator web UI.
"""
import asyncio
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.websockets import WebSocket
from pydantic import BaseModel

from src.utils.config import load_config, load_env
from src.utils.health import run_all_checks
from src.database import repository
from src.database.migrations import _project_root, run_migrations, DEFAULT_DB

# Progress broadcast: execution_id -> set of WebSocket connections
_progress_subscribers: dict[int, set[WebSocket]] = {}


def _project_root_api() -> Path:
    here = Path(__file__).resolve().parent
    while here.name != "src" and here.parent != here:
        here = here.parent
    return here.parent if here.name == "src" else Path.cwd()


def _db_path() -> Optional[Path]:
    root = _project_root_api()
    cfg = load_config()
    db_name = (cfg.get("paths") or {}).get("database", DEFAULT_DB)
    p = Path(db_name)
    return root / p if not p.is_absolute() else p


app = FastAPI(title="YouTube Shorts Generator API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Schemas ---


class GenerateRequest(BaseModel):
    topic: Optional[str] = None
    config_overrides: Optional[dict] = None


class GenerateResponse(BaseModel):
    execution_id: int


class ConfigUpdateRequest(BaseModel):
    config: dict


# --- Pipeline runner ---


async def _run_pipeline(execution_id: int, topic: Optional[str], config_overrides: Optional[dict]) -> None:
    """Run pipeline in background; broadcast progress to WebSocket subscribers."""
    from src.agents.research_agent import ResearchAgent
    from src.agents.script_agent import ScriptAgent
    from src.agents.uniqueness_agent import UniquenessAgent
    from src.agents.tts_agent import TTSAgent
    from src.agents.video_agent import VideoAgent
    from src.agents.composition_agent import CompositionAgent
    from src.agents.quality_agent import QualityAgent
    from src.agents.publishing_agent import PublishingAgent
    from src.orchestration.pipeline import Pipeline

    agents = [
        ResearchAgent, ScriptAgent, UniquenessAgent, TTSAgent,
        VideoAgent, CompositionAgent, QualityAgent, PublishingAgent,
    ]
    pipeline = Pipeline(agents=agents, db_path=_db_path())

    async def progress_cb(agent_name: str, step: str, percent: float, log_message: str) -> None:
        subs = _progress_subscribers.get(execution_id, set()).copy()
        msg = {"agent": agent_name, "step": step, "percent": percent, "log": log_message}
        for ws in subs:
            try:
                await ws.send_json(msg)
            except Exception:
                pass

    try:
        await pipeline.run(
            topic=topic,
            config_overrides=config_overrides,
            progress_callback=progress_cb,
            execution_id=execution_id,
        )
    except Exception as e:
        subs = _progress_subscribers.get(execution_id, set()).copy()
        for ws in subs:
            try:
                await ws.send_json({"agent": "pipeline", "step": "error", "percent": 0, "log": str(e)})
            except Exception:
                pass
    finally:
        _progress_subscribers.pop(execution_id, None)


# --- Routes ---


@app.post("/api/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest, background_tasks: BackgroundTasks) -> GenerateResponse:
    """Start generation; returns execution_id. Pipeline runs async."""
    root = _project_root_api()
    load_env(root / ".env")
    run_migrations(_db_path())
    from src.orchestration.state_manager import create_execution
    execution_id = create_execution(db_path=_db_path())
    background_tasks.add_task(_run_pipeline, execution_id, req.topic, req.config_overrides)
    return GenerateResponse(execution_id=execution_id)


@app.get("/api/status/{execution_id}")
async def get_status(execution_id: int) -> dict:
    """Execution status, current_stage, progress %, cost."""
    run_migrations(_db_path())
    row = repository.get_execution(execution_id, db_path=_db_path())
    if not row:
        raise HTTPException(status_code=404, detail="Execution not found")
    cost = repository.get_execution_cost_total(execution_id, db_path=_db_path())
    return {
        "execution_id": execution_id,
        "status": row.get("status"),
        "current_stage": row.get("current_stage"),
        "cost": cost,
        "error_message": row.get("error_message"),
        "output_path": row.get("output_path"),
        "topic": row.get("topic"),
    }


@app.get("/api/history")
async def get_history(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> dict:
    """List past executions (paginated)."""
    run_migrations(_db_path())
    total = repository.get_executions_count(db_path=_db_path())
    rows = repository.get_last_executions(n=limit + offset, db_path=_db_path())
    page = rows[offset : offset + limit]
    return {"executions": page, "total": total}


@app.get("/api/health")
async def health() -> dict:
    """Same as CLI health (run_all_checks). Return JSON."""
    root = _project_root_api()
    load_env(root / ".env")
    return run_all_checks(root)


@app.get("/api/config")
async def get_config_route() -> dict:
    """Current config (non-secret)."""
    cfg = load_config()
    return {k: v for k, v in cfg.items() if k not in ("secrets", "api_keys")}


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base (mutates base)."""
    for k, v in override.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v
    return base


@app.put("/api/config")
async def put_config(req: ConfigUpdateRequest) -> dict:
    """Update config (non-secret). Writes to config.yaml."""
    import copy
    import yaml
    root = _project_root_api()
    current = load_config()
    merged = _deep_merge(copy.deepcopy(current), req.config)
    with open(root / "config.yaml", "w") as f:
        yaml.safe_dump(merged, f, default_flow_style=False, sort_keys=False)
    return {"ok": True}


@app.get("/api/video/{execution_id}")
async def get_video(execution_id: int) -> FileResponse:
    """Serve generated video file for preview."""
    run_migrations(_db_path())
    row = repository.get_execution(execution_id, db_path=_db_path())
    if not row:
        raise HTTPException(status_code=404, detail="Execution not found")
    output_path = row.get("output_path")
    if not output_path or not Path(output_path).exists():
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(output_path, media_type="video/mp4")


@app.websocket("/ws/progress/{execution_id}")
async def websocket_progress(websocket: WebSocket, execution_id: int) -> None:
    """Real-time pipeline progress (agent name, step, %, logs)."""
    await websocket.accept()
    if execution_id not in _progress_subscribers:
        _progress_subscribers[execution_id] = set()
    _progress_subscribers[execution_id].add(websocket)
    try:
        while True:
            _ = await websocket.receive_text()
    except Exception:
        pass
    finally:
        _progress_subscribers.get(execution_id, set()).discard(websocket)
        if not _progress_subscribers.get(execution_id):
            _progress_subscribers.pop(execution_id, None)
