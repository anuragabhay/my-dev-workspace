"""
Unit tests for src.utils.config (load_config, validate_env, validate_config, get_config).
Run from repo root: pytest tests/test_config.py -v
"""
import os
from pathlib import Path
from unittest.mock import patch

import pytest

import sys
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.utils.config import (
    load_env,
    load_config,
    validate_env,
    validate_config,
    get_config,
    REQUIRED_ENV_KEYS,
    DEFAULT_CONFIG_NAME,
    DEFAULT_ENV_NAME,
)


def test_validate_env_returns_missing_keys():
    """validate_env returns list of required keys that are missing or empty."""
    with patch.dict(os.environ, {}, clear=True):
        missing = validate_env(required=["A", "B"])
        assert set(missing) == {"A", "B"}
    with patch.dict(os.environ, {"A": "x", "B": ""}, clear=False):
        missing = validate_env(required=["A", "B"])
        assert "B" in missing
        assert "A" not in missing


def test_validate_env_with_all_set_returns_empty():
    """validate_env returns [] when all required keys are set."""
    with patch.dict(os.environ, {k: "set" for k in REQUIRED_ENV_KEYS}, clear=False):
        assert validate_env() == []


def test_validate_config_empty_dict_no_errors():
    """validate_config on empty dict returns no errors."""
    assert validate_config({}) == []


def test_validate_config_timeouts_positive():
    """validate_config accepts positive timeout numbers."""
    assert validate_config({"timeouts": {"research": 30, "script": 60}}) == []


def test_validate_config_timeouts_invalid_adds_error():
    """validate_config returns error when timeout is not positive."""
    errs = validate_config({"timeouts": {"x": 0}})
    assert any("timeouts" in e and "positive" in e for e in errs)
    errs = validate_config({"timeouts": {"x": -1}})
    assert len(errs) >= 1


def test_validate_config_cost_target_per_video():
    """validate_config returns error when cost.target_per_video <= 0."""
    errs = validate_config({"cost": {"target_per_video": 0}})
    assert any("target_per_video" in e for e in errs)
    assert validate_config({"cost": {"target_per_video": 5.0}}) == []


def test_load_config_returns_dict():
    """load_config returns a dict (from project config or example)."""
    with patch("src.utils.config._project_root", return_value=_ROOT):
        result = load_config()
    assert isinstance(result, dict)


def test_load_config_with_nonexistent_path_returns_empty():
    """load_config with path that does not exist returns {} when no fallback."""
    with patch("src.utils.config._project_root", return_value=Path("/nonexistent")):
        result = load_config(config_path=Path("/nonexistent/missing.yaml"))
    assert result == {}


def test_load_config_with_explicit_yaml_content(tmp_path):
    """load_config loads YAML from path and returns dict."""
    cfg_file = tmp_path / "cfg.yaml"
    cfg_file.write_text("timeouts:\n  research: 10\n")
    with patch("src.utils.config._project_root", return_value=tmp_path):
        result = load_config(config_path=cfg_file)
    assert result.get("timeouts", {}).get("research") == 10


def test_get_config_returns_tuple_config_and_errors():
    """get_config returns (config_dict, list of error strings)."""
    with patch("src.utils.config.load_env"), patch("src.utils.config.load_config", return_value={}):
        with patch.dict(os.environ, {}, clear=True):
            config, errors = get_config()
    assert isinstance(config, dict)
    assert isinstance(errors, list)
    assert all(isinstance(e, str) for e in errors)


def test_get_config_includes_missing_env_errors():
    """get_config includes 'Missing or empty env' for unset required keys."""
    with patch("src.utils.config.load_env"), patch("src.utils.config.load_config", return_value={}):
        with patch.dict(os.environ, {}, clear=True):
            _, errors = get_config()
    assert any("Missing or empty env" in e for e in errors)


def test_load_env_with_tmp_env_file(tmp_path):
    """load_env loads .env from given path; no real API keys required."""
    env_file = tmp_path / ".env"
    env_file.write_text("SOME_KEY=value\nANOTHER=test\n")
    # Pass explicit path so no real .env or project root needed
    load_env(env_path=env_file)
    assert os.getenv("SOME_KEY") == "value"
    assert os.getenv("ANOTHER") == "test"


def test_get_config_valid_env_and_config_returns_no_errors():
    """get_config with all required env set and valid config returns empty errors."""
    valid_config = {"timeouts": {"research": 30}, "cost": {"target_per_video": 5.0}}
    with patch("src.utils.config.load_env"):
        with patch("src.utils.config.load_config", return_value=valid_config):
            with patch.dict(os.environ, {k: "set" for k in REQUIRED_ENV_KEYS}, clear=False):
                config, errors = get_config()
    assert config == valid_config
    assert errors == []
