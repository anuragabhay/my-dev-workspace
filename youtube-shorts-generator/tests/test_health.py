"""
Unit tests for src.utils.health (MVP health checks).
Run from repo root: pytest tests/test_health.py -v
"""
import os
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure src is on path when running from youtube-shorts-generator root
import sys
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.utils.health import (
    check_disk_space,
    check_runwayml,
    run_all_checks,
    MIN_DISK_GB,
)


def test_check_disk_space_returns_dict_with_pass_and_detail():
    """check_disk_space returns a dict with 'pass' and 'detail' keys."""
    root = Path("/")
    result = check_disk_space(root)
    assert isinstance(result, dict)
    assert "pass" in result
    assert "detail" in result
    assert isinstance(result["pass"], bool)
    assert isinstance(result["detail"], dict)


def test_check_disk_space_detail_has_expected_keys():
    """check_disk_space detail includes free_gb and required_gb on success path."""
    root = Path("/")
    result = check_disk_space(root)
    detail = result["detail"]
    assert "free_gb" in detail or "error" in detail
    if "free_gb" in detail:
        assert "required_gb" in detail
        assert detail["required_gb"] == MIN_DISK_GB


def test_check_runwayml_fails_when_key_missing():
    """check_runwayml returns pass=False when RUNWAYML_API_KEY is not set."""
    with patch.dict(os.environ, {"RUNWAYML_API_KEY": ""}, clear=False):
        result = check_runwayml(Path("."))
    assert result["pass"] is False
    assert "detail" in result


def test_check_runwayml_passes_when_key_set():
    """check_runwayml returns pass=True when RUNWAYML_API_KEY is set."""
    with patch.dict(os.environ, {"RUNWAYML_API_KEY": "test-key"}, clear=False):
        result = check_runwayml(Path("."))
    assert result["pass"] is True
    assert result.get("detail") == {} or "detail" in result


def test_run_all_checks_returns_ok_and_checks():
    """run_all_checks returns dict with 'ok' and 'checks' keys."""
    result = run_all_checks(root=_ROOT)
    assert isinstance(result, dict)
    assert "ok" in result
    assert "checks" in result
    assert isinstance(result["ok"], bool)
    checks = result["checks"]
    assert isinstance(checks, dict)
    for name in ("api_keys", "disk_space", "system_resources", "database",
                 "openai", "elevenlabs", "runwayml", "youtube_channel"):
        assert name in checks
        assert "pass" in checks[name]
        assert "detail" in checks[name]
