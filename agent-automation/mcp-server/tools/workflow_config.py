"""
Tool: get_workflow_config
Reads workflow.yml, roles.yml, decisions.yml and returns workflow stages, role list with slash commands.
"""

from pathlib import Path
from typing import Any, Optional

import yaml


def _workspace_root() -> Path:
    """Resolve workspace root (agent-automation parent)."""
    return Path(__file__).resolve().parent.parent.parent


def get_workflow_config(workspace_root: Optional[str] = None) -> dict[str, Any]:
    """
    Read workflow.yml, roles.yml, decisions.yml (or combined config) and return
    workflow stages, current-stage logic if applicable, and role list with slash commands.

    Args:
        workspace_root: Optional workspace root; defaults to agent-automation parent.

    Returns:
        Dict with workflow (stages), roles (list with display_name, slash, when_to_use),
        decisions (rules list), error if any file missing/invalid.
    """
    root = Path(workspace_root) if workspace_root else _workspace_root()
    base = root / "agent-automation"
    result: dict[str, Any] = {
        "workflow": None,
        "stages": [],
        "roles": [],
        "decisions": [],
        "error": None,
    }

    # workflow.yml
    wf_path = base / "workflow.yml"
    if wf_path.exists():
        try:
            with open(wf_path, "r") as f:
                wf = yaml.safe_load(f)
            result["workflow"] = {"name": wf.get("name"), "description": wf.get("description")}
            stages = wf.get("stages") or {}
            result["stages"] = [
                {
                    "id": s.get("id"),
                    "name": s.get("name"),
                    "description": s.get("description"),
                    "next": s.get("next"),
                    "roles": s.get("roles", []),
                    "parallel_ok": s.get("parallel_ok", []),
                }
                for s in stages.values()
            ]
        except Exception as e:
            result["error"] = f"workflow.yml: {e}"
            return result
    else:
        result["error"] = "workflow.yml not found"
        return result

    # roles.yml
    roles_path = base / "roles.yml"
    if roles_path.exists():
        try:
            with open(roles_path, "r") as f:
                roles_data = yaml.safe_load(f)
            roles_dict = roles_data.get("roles") or {}
            result["roles"] = [
                {
                    "id": rid,
                    "display_name": r.get("display_name"),
                    "slash": r.get("slash"),
                    "when_to_use": r.get("when_to_use"),
                    "concurrency_max": r.get("concurrency_max"),
                    "parallel_ok": r.get("parallel_ok"),
                }
                for rid, r in roles_dict.items()
            ]
        except Exception as e:
            result["error"] = result["error"] or f"roles.yml: {e}"
    else:
        result["error"] = (result["error"] or "") + "; roles.yml not found"

    # decisions.yml
    dec_path = base / "decisions.yml"
    if dec_path.exists():
        try:
            with open(dec_path, "r") as f:
                dec_data = yaml.safe_load(f)
            result["decisions"] = dec_data.get("rules") or []
        except Exception as e:
            result["error"] = (result["error"] or "") + f"; decisions.yml: {e}"

    return result
