"""
Tool: get_pending_orchestrator_prompt
Reads the pending orchestrator run-cycle prompt written by the stop hook when a subagent chat stops.
Returns the prompt and clears the file so the Orchestrator can run one cycle without the user pasting.
"""

from pathlib import Path
from typing import Dict, Any

# Add parent to path for workspace_config
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from workspace_config import get_workspace_root


def get_pending_orchestrator_prompt(config_path: str = None) -> Dict[str, Any]:
    """
    Read and clear the pending orchestrator prompt file (written by stop hook when subagent stops).

    Returns:
        {"prompt": "<content>"} if file existed and had content, else {"prompt": ""}.
    """
    root = get_workspace_root()
    pending_file = root / "agent-automation" / "orchestrator_pending_prompt.txt"
    if not pending_file.exists():
        return {"prompt": ""}
    try:
        prompt = pending_file.read_text(encoding="utf-8").strip()
        pending_file.unlink()
    except OSError:
        return {"prompt": ""}
    return {"prompt": prompt}
