"""
Tool: get_pending_orchestrator_prompt
Reads the pending orchestrator run-cycle prompt written by the stop hook when a subagent chat stops.
Returns the prompt and clears the file so the Orchestrator can run one cycle without the user pasting.
"""

from pathlib import Path
from typing import Dict, Any

import yaml


def get_pending_orchestrator_prompt(config_path: str = None) -> Dict[str, Any]:
    """
    Read and clear the pending orchestrator prompt file (written by stop hook when subagent stops).

    Returns:
        {"prompt": "<content>"} if file existed and had content, else {"prompt": ""}.
    """
    if config_path is None:
        config_path = str(Path(__file__).resolve().parent.parent.parent / "config.yaml")
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
    except Exception:
        return {"prompt": ""}
    workspace_path = config.get("workspace_path")
    if not workspace_path:
        return {"prompt": ""}
    root = Path(workspace_path).resolve().parent
    pending_file = root / "agent-automation" / "orchestrator_pending_prompt.txt"
    if not pending_file.exists():
        return {"prompt": ""}
    try:
        prompt = pending_file.read_text(encoding="utf-8").strip()
        pending_file.unlink()
    except OSError:
        return {"prompt": ""}
    return {"prompt": prompt}
