"""
Configuration management: load .env and config.yaml, validate required keys and settings.
"""
from pathlib import Path
from typing import Any, Optional

import yaml
from dotenv import load_dotenv
import os

# Required env var names (no values in code)
REQUIRED_ENV_KEYS = [
    "OPENAI_API_KEY",
    "ELEVENLABS_API_KEY",
    "RUNWAYML_API_KEY",
    "YOUTUBE_CLIENT_ID",
    "YOUTUBE_CLIENT_SECRET",
    "YOUTUBE_REFRESH_TOKEN",
]

# Default config path relative to project root
DEFAULT_CONFIG_NAME = "config.yaml"
DEFAULT_ENV_NAME = ".env"


def _project_root() -> Path:
    """Project root: directory containing src/."""
    here = Path(__file__).resolve().parent
    while here.name != "src" and here.parent != here:
        here = here.parent
    return here.parent if here.name == "src" else Path.cwd()


def load_env(env_path: Optional[Path] = None) -> None:
    """Load .env from path or project root. Idempotent."""
    root = _project_root()
    path = env_path or root / DEFAULT_ENV_NAME
    if path.exists():
        load_dotenv(path)


def load_config(config_path: Optional[Path] = None) -> dict[str, Any]:
    """Load config.yaml; return dict. Uses config.example.yaml if config.yaml missing."""
    root = _project_root()
    path = config_path or root / DEFAULT_CONFIG_NAME
    if not path.exists():
        fallback = root / "config.example.yaml"
        path = fallback if fallback.exists() else path
    if not path.exists():
        return {}
    with open(path) as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def validate_env(required: Optional[list[str]] = None) -> list[str]:
    """
    Check that required env vars are set and non-empty.
    Returns list of missing key names.
    """
    required = required or REQUIRED_ENV_KEYS
    missing = [k for k in required if not (os.getenv(k) or "").strip()]
    return missing


def validate_config(config: dict[str, Any]) -> list[str]:
    """
    Basic validation of config (e.g. timeouts present and positive).
    Returns list of error messages.
    """
    errors: list[str] = []
    timeouts = config.get("timeouts") or {}
    for name, val in timeouts.items():
        if not isinstance(val, (int, float)) or val <= 0:
            errors.append(f"timeouts.{name} must be a positive number")
    cost = config.get("cost") or {}
    if cost and (cost.get("target_per_video") or 0) <= 0:
        errors.append("cost.target_per_video must be positive")
    return errors


def get_config(
    env_path: Optional[Path] = None, config_path: Optional[Path] = None
) -> tuple[dict[str, Any], list[str]]:
    """
    Load .env and config.yaml, validate, return (config_dict, list of validation errors).
    Errors include missing env keys and config validation failures.
    """
    load_env(env_path)
    config = load_config(config_path)
    errors: list[str] = []
    missing_env = validate_env()
    if missing_env:
        errors.extend([f"Missing or empty env: {k}" for k in missing_env])
    errors.extend(validate_config(config))
    return config, errors
