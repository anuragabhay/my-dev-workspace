"""
Workspace path resolution for platform-agnostic agent automation.
Uses WORKSPACE_ROOT env var, workspace_config.yaml, or derives from agent-automation parent.
"""
import os
import yaml
from pathlib import Path


def get_workspace_root() -> Path:
    """
    Resolve workspace root (directory containing PROJECT_WORKSPACE.md).
    Priority: WORKSPACE_ROOT env -> workspace_config.yaml workspace_root -> agent-automation parent.
    """
    # 1. Environment variable
    env_root = os.environ.get("WORKSPACE_ROOT")
    if env_root and env_root.strip():
        p = Path(env_root).resolve()
        if p.exists():
            return p

    # 2. workspace_config.yaml (next to this file or in agent-automation)
    this_file = Path(__file__).resolve()
    agent_automation = this_file.parent
    config_paths = [
        agent_automation / "workspace_config.yaml",
        agent_automation.parent / "workspace_config.yaml",
    ]
    for cfg in config_paths:
        if cfg.exists():
            try:
                with open(cfg, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                root = (data or {}).get("workspace_root")
                if root:
                    p = Path(root).resolve()
                    if p.exists():
                        return p
            except (OSError, yaml.YAMLError):
                pass

    # 3. Derive from agent-automation parent (this file is in agent-automation/)
    return agent_automation.parent


def load_config(config_path: str = None) -> dict:
    """
    Load agent-automation config with workspace_path resolved.
    config_path: path to config.yaml; defaults to agent-automation/config.yaml
    """
    root = get_workspace_root()
    agent_automation = root / "agent-automation"
    cfg_path = Path(config_path) if config_path else agent_automation / "config.yaml"

    if not cfg_path.exists():
        cfg_path = agent_automation / "config.yaml"

    if not cfg_path.exists():
        return {
            "workspace_path": str(root / "PROJECT_WORKSPACE.md"),
            "workspace_root": str(root),
            "poll_interval": 30,
            "prompt_dir": str(agent_automation / "prompts"),
            "state_db": str(agent_automation / "state.db"),
            "json_backup": str(agent_automation / "state_backup.json"),
            "agents": {},
            "_config_path": str(agent_automation / "config.yaml"),
        }

    with open(cfg_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    # Resolve workspace_path: if relative, prepend workspace_root
    workspace_path = data.get("workspace_path", "PROJECT_WORKSPACE.md")
    if not Path(workspace_path).is_absolute():
        workspace_path = str(root / workspace_path.lstrip("/"))

    prompt_dir_raw = data.get("prompt_dir")
    if prompt_dir_raw and not Path(prompt_dir_raw).is_absolute():
        prompt_dir = str(agent_automation / prompt_dir_raw.lstrip("./"))
    else:
        prompt_dir = prompt_dir_raw or str(agent_automation / "prompts")

    state_db_raw = data.get("state_db")
    if state_db_raw and not Path(state_db_raw).is_absolute():
        state_db = str(agent_automation / state_db_raw.lstrip("./"))
    else:
        state_db = state_db_raw or str(agent_automation / "state.db")

    json_backup_raw = data.get("json_backup")
    if json_backup_raw and not Path(json_backup_raw).is_absolute():
        json_backup = str(agent_automation / json_backup_raw.lstrip("./"))
    else:
        json_backup = json_backup_raw or str(agent_automation / "state_backup.json")

    result = {
        "workspace_path": workspace_path,
        "workspace_root": str(root),
        "poll_interval": data.get("poll_interval", 30),
        "prompt_dir": prompt_dir,
        "state_db": state_db,
        "json_backup": json_backup,
        "agents": data.get("agents", {}),
        "_config_path": str(cfg_path),
        **{k: v for k, v in data.items() if k not in ("workspace_path", "workspace_root", "poll_interval", "prompt_dir", "state_db", "json_backup", "agents")},
    }
    return result
