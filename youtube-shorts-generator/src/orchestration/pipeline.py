"""
Pipeline orchestrator: sequential agent execution (MVP).
"""
import shutil
from pathlib import Path
from typing import Optional, List, Type, Callable, Awaitable

from src.agents.base_agent import BaseAgent, ExecutionContext, AgentResult
from src.orchestration.state_manager import create_execution, load_context, save_stage
from src.orchestration.message_queue import MessageQueue
from src.database import repository
from src.database import models

ProgressCallback = Callable[[str, str, float, str], Awaitable[None]]


def _project_root() -> Path:
    here = Path(__file__).resolve().parent
    while here.name != "src" and here.parent != here:
        here = here.parent
    return here.parent if here.name == "src" else Path.cwd()


class Pipeline:
    """Runs agents in sequence for one execution."""

    def __init__(self, agents: Optional[List[Type[BaseAgent]]] = None, db_path: Optional[Path] = None):
        self.agents = agents or []
        self.db_path = db_path
        self.queue = MessageQueue(db_path=db_path)

    async def run(
        self,
        topic: Optional[str] = None,
        config_overrides: Optional[dict] = None,
        progress_callback: Optional[ProgressCallback] = None,
        execution_id: Optional[int] = None,
    ) -> int:
        """Create execution (or use provided), run agents in order; return execution_id."""
        if execution_id is None:
            execution_id = create_execution(db_path=self.db_path)
        repository.update_execution(
            execution_id,
            status=models.STATUS_IN_PROGRESS,
            topic=topic,
            db_path=self.db_path,
        )
        context = load_context(execution_id, db_path=self.db_path) or ExecutionContext(
            execution_id=execution_id, current_stage="start", data={}
        )
        if topic:
            context.data["research"] = {"topics": [{"title": topic, "relevance": 0.9}]}
        agents_to_run = self.agents
        if topic:
            agents_to_run = [a for a in self.agents if a.name != "research"]
        total = len(agents_to_run)
        for idx, agent_cls in enumerate(agents_to_run):
            agent = agent_cls()
            save_stage(execution_id, agent.name, db_path=self.db_path)
            pct = (idx / total) * 100.0 if total else 0
            if progress_callback:
                await progress_callback(agent.name, "start", pct, f"Starting {agent.name}")
            result = await agent.execute(context)
            context.data[agent.name] = (result.data or {})
            pct = ((idx + 1) / total) * 100.0 if total else 100.0
            if progress_callback:
                await progress_callback(
                    agent.name,
                    "complete" if result.success else "error",
                    pct,
                    result.message or (f"Completed {agent.name}" if result.success else str(result.message)),
                )
            if not result.success:
                repository.update_execution(
                    execution_id,
                    status=models.STATUS_FAILED,
                    error_message=result.message,
                    db_path=self.db_path,
                )
                return execution_id
        output_path = (context.data.get("composition") or {}).get("output_path")
        final_output_path: Optional[str] = None
        if output_path and Path(output_path).exists():
            root = _project_root()
            from src.utils.config import load_config
            cfg = load_config()
            out_dir = Path(cfg.get("paths", {}).get("output_dir", "output_videos"))
            if not out_dir.is_absolute():
                out_dir = root / out_dir
            out_dir.mkdir(parents=True, exist_ok=True)
            dest = out_dir / f"{execution_id}.mp4"
            shutil.copy2(output_path, dest)
            final_output_path = str(dest)
        from src.utils.cost_tracker import get_execution_cost_total
        cost_total = get_execution_cost_total(execution_id, db_path=self.db_path)
        repository.update_execution(
            execution_id,
            status=models.STATUS_COMPLETED,
            output_path=final_output_path,
            cost_total=cost_total,
            db_path=self.db_path,
        )
        return execution_id
