"""
API tests for FastAPI app (src.api.app).
Run from repo root: pytest tests/test_api.py -v
"""
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

import sys
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.api.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_returns_json(client):
    """GET /api/health returns JSON with ok and checks."""
    with patch("src.api.app._project_root_api", return_value=_ROOT):
        resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "ok" in data
    assert "checks" in data
    assert isinstance(data["checks"], dict)


def test_config_get_returns_json(client):
    """GET /api/config returns non-secret config."""
    resp = client.get("/api/config")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)


def test_generate_returns_execution_id(client):
    """POST /api/generate returns execution_id."""
    resp = client.post("/api/generate", json={"topic": "test topic"})
    assert resp.status_code == 200
    data = resp.json()
    assert "execution_id" in data
    assert isinstance(data["execution_id"], int)
    assert data["execution_id"] > 0


def test_status_returns_execution(client):
    """GET /api/status/{id} returns execution status."""
    # Create execution first
    gen = client.post("/api/generate", json={"topic": "status test"})
    assert gen.status_code == 200
    eid = gen.json()["execution_id"]
    resp = client.get(f"/api/status/{eid}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["execution_id"] == eid
    assert "status" in data
    assert "cost" in data


def test_status_404_for_invalid_id(client):
    """GET /api/status/99999 returns 404 when not found."""
    resp = client.get("/api/status/99999")
    assert resp.status_code == 404


def test_history_returns_paginated(client):
    """GET /api/history returns executions and total."""
    resp = client.get("/api/history?limit=5&offset=0")
    assert resp.status_code == 200
    data = resp.json()
    assert "executions" in data
    assert "total" in data
    assert isinstance(data["executions"], list)
    assert isinstance(data["total"], int)


def test_video_404_when_not_found(client):
    """GET /api/video/{id} returns 404 when video doesn't exist."""
    resp = client.get("/api/video/99999")
    assert resp.status_code == 404
