"""
RunwayML: video generation API. Fallback chain: RunwayML → Stock → Animated → Static.
"""
import os
from pathlib import Path
from typing import Optional

def generate_video(
    prompt: str,
    output_path: Optional[Path] = None,
    duration_sec: float = 5.0,
) -> tuple[Path, float]:
    """Generate video from prompt. Returns (path_to_video, cost_usd). Primary: RunwayML (~$0.05/sec)."""
    # Stub: real implementation would call RunwayML API
    if output_path is None:
        output_path = Path("tmp/runway_output.mp4")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(b"")  # placeholder
    cost = duration_sec * 0.05
    return output_path, cost
