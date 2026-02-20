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


def cmd_health(json_output: bool = False) -> int:
    """Health check: MVP checks (API keys, disk, resources, DB, API connectivity, YouTube). Return 0 ok, 1 fail."""
    root = _project_root()
    sys.path.insert(0, str(root))
    # Load .env from project root so API keys and YouTube credentials are available to checks
    from src.utils.config import load_env, DEFAULT_ENV_NAME
    env_file = root / DEFAULT_ENV_NAME
    if not env_file.exists():
        example = root / ".env.example"
        if example.exists():
            import shutil
            shutil.copy(example, env_file)
    load_env(env_file)
    from src.utils.health import run_all_checks
    result = run_all_checks(root)
    
    if json_output:
        print(json.dumps(result, indent=2))
    else:
        from src.utils.ui import format_health_check_result
        format_health_check_result(result, show_json=False)
    
    return 0 if result.get("ok") else 1


def cmd_status(json_output: bool = False) -> int:
    """Last execution status."""
    root = _project_root()
    sys.path.insert(0, str(root))
    from src.database import repository
    repository.ensure_schema()
    last = repository.get_last_executions(1)
    if not last:
        status_data = {"status": "no_executions"}
    else:
        status_data = {"last": last[0]}
    
    if json_output:
        print(json.dumps(status_data))
    else:
        from src.utils.ui import format_status_result
        format_status_result(status_data)
    
    return 0


def cmd_generate() -> int:
    """Run pipeline once."""
    root = _project_root()
    sys.path.insert(0, str(root))
    # Load .env so API keys (OpenAI, ElevenLabs, Runway, YouTube) are available to pipeline
    from src.utils.config import load_env, DEFAULT_ENV_NAME
    env_file = root / DEFAULT_ENV_NAME
    if not env_file.exists() and (root / ".env.example").exists():
        import shutil
        shutil.copy(root / ".env.example", env_file)
    load_env(env_file)
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


def _ensure_config_for_command(command: str) -> tuple[bool, list[str]]:
    """
    For commands that need config (health, generate), load and validate.
    Returns (ok, errors). If not ok, errors is a non-empty list of messages.
    """
    root = _project_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from src.utils.config import get_config
    _, errors = get_config()
    return (len(errors) == 0, errors)


def main() -> int:
    p = argparse.ArgumentParser(prog="youtube-shorts")
    p.add_argument("command", choices=["generate", "status", "health"])
    p.add_argument("--json", action="store_true", help="Output raw JSON instead of formatted display")
    args = p.parse_args()

    # Validate config on startup for commands that need API keys and settings
    if args.command in ("health", "generate"):
        ok, errors = _ensure_config_for_command(args.command)
        if not ok:
            msg = "Configuration invalid or missing. Fix the following and try again:\n  " + "\n  ".join(errors)
            print(msg, file=sys.stderr)
            return 1

    if args.command == "health":
        return cmd_health(json_output=args.json)
    if args.command == "status":
        return cmd_status(json_output=args.json)
    if args.command == "generate":
        return cmd_generate()
    return 0


if __name__ == "__main__":
    sys.exit(main())
