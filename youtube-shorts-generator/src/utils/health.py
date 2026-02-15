"""
MVP health checks: API keys, disk, system resources, DB, API connectivity, YouTube OAuth.
Returns a structure suitable for JSON output with pass/fail and optional details per check.
"""
import os
import shutil
import sqlite3
import sys
from pathlib import Path
from typing import Any

# Minimum required (MVP spec)
MIN_DISK_GB = 10
MIN_RAM_GB = 8
MIN_CPU_CORES = 2


def _project_root() -> Path:
    here = Path(__file__).resolve().parent
    while here.name != "src" and here.parent != here:
        here = here.parent
    return here.parent if here.name == "src" else Path.cwd()


def check_api_keys(root: Path) -> dict[str, Any]:
    """API key validity: present and non-empty for required keys."""
    sys.path.insert(0, str(root))
    from src.utils.config import load_env, validate_env, DEFAULT_ENV_NAME
    load_env(root / DEFAULT_ENV_NAME)
    missing = validate_env()
    return {
        "pass": len(missing) == 0,
        "detail": {"missing": missing} if missing else {},
    }


def check_disk_space(root: Path) -> dict[str, Any]:
    """Disk space: e.g. ≥10GB free on project root's filesystem."""
    try:
        usage = shutil.disk_usage(str(root))
        free_gb = usage.free / (1024**3)
        return {
            "pass": free_gb >= MIN_DISK_GB,
            "detail": {"free_gb": round(free_gb, 2), "required_gb": MIN_DISK_GB},
        }
    except Exception as e:
        return {"pass": False, "detail": {"error": str(e)}}


def _get_ram_gb() -> float | None:
    """Approximate available RAM in GB. None if not measurable."""
    try:
        if sys.platform == "linux":
            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("MemAvailable:"):
                        kb = int(line.split()[1])
                        return kb / (1024 * 1024)
        if sys.platform == "darwin":
            import subprocess
            out = subprocess.run(
                ["sysctl", "-n", "hw.memsize"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if out.returncode == 0 and out.stdout.strip():
                bytes_total = int(out.stdout.strip())
                return bytes_total / (1024**3)
    except Exception:
        pass
    return None


def check_system_resources(root: Path) -> dict[str, Any]:
    """System resources: e.g. 8GB RAM, CPU cores."""
    detail: dict[str, Any] = {}
    cpu = os.cpu_count()
    if cpu is not None:
        detail["cpu_cores"] = cpu
    ram_gb = _get_ram_gb()
    if ram_gb is not None:
        detail["ram_gb"] = round(ram_gb, 2)
        detail["required_ram_gb"] = MIN_RAM_GB
    pass_cpu = cpu is not None and cpu >= MIN_CPU_CORES
    pass_ram = ram_gb is None or ram_gb >= MIN_RAM_GB
    return {
        "pass": pass_cpu and pass_ram,
        "detail": {**detail, "required_cpu_cores": MIN_CPU_CORES},
    }


def check_database(root: Path) -> dict[str, Any]:
    """Database connectivity: SQLite schema + SELECT 1."""
    sys.path.insert(0, str(root))
    from src.database.migrations import run_migrations, DEFAULT_DB, _project_root as mig_root
    db_path = mig_root() / DEFAULT_DB
    try:
        run_migrations(db_path)
        conn = sqlite3.connect(str(db_path))
        try:
            conn.execute("SELECT 1")
            return {"pass": True, "detail": {"db_path": str(db_path)}}
        finally:
            conn.close()
    except Exception as e:
        return {"pass": False, "detail": {"error": str(e), "db_path": str(db_path)}}


def check_openai_connectivity(root: Path) -> dict[str, Any]:
    """OpenAI API connectivity: minimal models list or ping."""
    if not (os.getenv("OPENAI_API_KEY") or "").strip():
        return {"pass": False, "detail": {"error": "OPENAI_API_KEY not set"}}
    sys.path.insert(0, str(root))
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        models = client.models.list()
        next(iter(models), None)  # trigger request
        return {"pass": True, "detail": {}}
    except Exception as e:
        return {"pass": False, "detail": {"error": str(e)}}


def check_elevenlabs_connectivity(root: Path) -> dict[str, Any]:
    """ElevenLabs API connectivity: lightweight call (e.g. get user/voices)."""
    if not (os.getenv("ELEVENLABS_API_KEY") or "").strip():
        return {"pass": False, "detail": {"error": "ELEVENLABS_API_KEY not set"}}
    sys.path.insert(0, str(root))
    try:
        from elevenlabs.client import ElevenLabs
        client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
        client.voices.search()  # lightweight: list voices
        return {"pass": True, "detail": {}}
    except Exception as e:
        return {"pass": False, "detail": {"error": str(e)}}


def check_runwayml(root: Path) -> dict[str, Any]:
    """RunwayML: key present (RUNWAYML_API_KEY or RUNWAYML_API_SECRET)."""
    key = (os.getenv("RUNWAYML_API_KEY") or os.getenv("RUNWAYML_API_SECRET") or "").strip()
    return {
        "pass": bool(key),
        "detail": {} if key else {"error": "RUNWAYML_API_KEY or RUNWAYML_API_SECRET not set"},
    }


def check_youtube_channel_access(root: Path) -> dict[str, Any]:
    """YouTube channel access: OAuth valid if configured."""
    for k in ("YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN"):
        if not (os.getenv(k) or "").strip():
            return {"pass": False, "detail": {"reason": "not_configured", "message": f"Missing {k}"}}
    sys.path.insert(0, str(root))
    try:
        from src.services.youtube_service import get_authenticated_service
        service = get_authenticated_service()
        service.channels().list(part="id", mine=True, maxResults=1).execute()
        return {"pass": True, "detail": {}}
    except FileNotFoundError as e:
        return {"pass": False, "detail": {"error": str(e), "reason": "oauth_file_missing"}}
    except Exception as e:
        return {"pass": False, "detail": {"error": str(e)}}


def run_all_checks(root: Path | None = None) -> dict[str, Any]:
    """
    Run all MVP health checks. Returns dict with "checks" (per-check pass/fail + detail)
    and "ok" (overall: True only if api_keys, disk_space, system_resources, database pass).
    API connectivity and YouTube are reported but do not force ok=False (so pre-config runs still report ok for infra).
    """
    root = root or _project_root()
    checks: dict[str, dict[str, Any]] = {}
    checks["api_keys"] = check_api_keys(root)
    checks["disk_space"] = check_disk_space(root)
    checks["system_resources"] = check_system_resources(root)
    checks["database"] = check_database(root)
    checks["openai"] = check_openai_connectivity(root)
    checks["elevenlabs"] = check_elevenlabs_connectivity(root)
    checks["runwayml"] = check_runwayml(root)
    checks["youtube_channel"] = check_youtube_channel_access(root)

    required_ok = (
        checks["api_keys"]["pass"]
        and checks["disk_space"]["pass"]
        and checks["system_resources"]["pass"]
        and checks["database"]["pass"]
    )
    return {
        "ok": required_ok,
        "checks": checks,
    }
