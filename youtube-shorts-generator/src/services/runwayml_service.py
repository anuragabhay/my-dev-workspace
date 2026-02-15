"""
RunwayML: video generation API. Fallback chain: RunwayML → Stock → Animated → Static.
Uses official Runway SDK: text_to_video.create, wait_for_task_output, download to file.
"""
import os
from pathlib import Path
from typing import Optional

import requests

from runwayml import RunwayML, TaskFailedError, TaskTimeoutError

COST_PER_SEC = 0.05
DEFAULT_WAIT_TIMEOUT_SEC = 600


def _get_api_key() -> str:
    """Use RUNWAYML_API_KEY or RUNWAYML_API_SECRET (Runway docs use SECRET)."""
    key = (os.getenv("RUNWAYML_API_KEY") or os.getenv("RUNWAYML_API_SECRET") or "").strip()
    if not key:
        raise ValueError("RUNWAYML_API_KEY or RUNWAYML_API_SECRET must be set")
    return key


def generate_video(
    prompt: str,
    output_path: Optional[Path] = None,
    duration_sec: float = 5.0,
) -> tuple[Path, float]:
    """Generate video from prompt via Runway text-to-video (official SDK). Returns (path_to_video, cost_usd)."""
    if output_path is None:
        output_path = Path("tmp/runway_output.mp4")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    api_key = _get_api_key()
    duration_int = max(2, min(10, int(round(duration_sec))))
    prompt_text = (prompt or "scene").strip()[:1000]

    client = RunwayML(api_key=api_key)

    # Text-to-video: use text_to_video.create (SDK exposes this endpoint). Vertical Shorts: 720:1280.
    created = client.text_to_video.create(
        model="gen4.5",
        prompt_text=prompt_text,
        ratio="720:1280",
        duration=duration_int,
    )

    try:
        task = created.wait_for_task_output(timeout=DEFAULT_WAIT_TIMEOUT_SEC)
    except TaskFailedError as e:
        details = e.task_details
        failure_msg = getattr(details, "failure", None) or "Task failed"
        failure_code = getattr(details, "failure_code", None) or getattr(details, "failureCode", None)
        msg = f"Runway task failed: {failure_msg}"
        if failure_code:
            msg += f" (code: {failure_code})"
        raise RuntimeError(msg) from e
    except TaskTimeoutError as e:
        raise RuntimeError("Runway task timed out waiting for video output") from e

    # task.output is List[str] of ephemeral URLs (Succeeded)
    if not task.output:
        raise RuntimeError("Runway task succeeded but returned no output URL")
    video_url = task.output[0]

    down = requests.get(video_url, timeout=120)
    down.raise_for_status()
    output_path.write_bytes(down.content)

    cost = duration_int * COST_PER_SEC
    return output_path, cost
