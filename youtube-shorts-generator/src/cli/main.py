"""
CLI: generate, status, health.
"""
import argparse
import asyncio
import json
import sys
from pathlib import Path

def _project_root() -> Path:
    here = Path(__file__).resolve().parent
    while here.name != "src" and here.parent != here:
        here = here.parent
    return here.parent if here.name == "src" else Path.cwd()


def cmd_health() -> int:
    """Health check: MVP checks (API keys, disk, resources, DB, API connectivity, YouTube). Return 0 ok, 1 fail."""
    root = _project_root()
    sys.path.insert(0, str(root))
    from src.utils.health import run_all_checks
    result = run_all_checks(root)
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


def cmd_status() -> int:
    """Last execution status."""
    root = _project_root()
    sys.path.insert(0, str(root))
    from src.database import repository
    repository.ensure_schema()
    last = repository.get_last_executions(1)
    if not last:
        print(json.dumps({"status": "no_executions"}))
        return 0
    print(json.dumps({"last": last[0]}))
    return 0


def cmd_generate() -> int:
    """Run pipeline once."""
    root = _project_root()
    sys.path.insert(0, str(root))
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
    pipeline = Pipeline(agents=agents)
    try:
        execution_id = asyncio.run(pipeline.run())
        print(json.dumps({"execution_id": execution_id}))
        return 0
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        return 1


def main() -> int:
    p = argparse.ArgumentParser(prog="youtube-shorts")
    p.add_argument("command", choices=["generate", "status", "health"])
    args = p.parse_args()
    if args.command == "health":
        return cmd_health()
    if args.command == "status":
        return cmd_status()
    if args.command == "generate":
        return cmd_generate()
    return 0


if __name__ == "__main__":
    sys.exit(main())
