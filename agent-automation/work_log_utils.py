"""
Work log: load/save JSON store, format entry to markdown, trim to N entries.
"""
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

WORK_LOG_PATH = Path(__file__).resolve().parent / "work_log.json"
WORKSPACE_PATH = Path(__file__).resolve().parent.parent / "PROJECT_WORKSPACE.md"
MAX_ENTRIES = 500
RECENT_N = 10


# Header: ### [timestamp] [role] [task] [status] — split by "] [" and take last 4 parts (task may contain "] [")
def _parse_header(line: str) -> Optional[Tuple[str, str, str, str]]:
    if not line.strip().startswith("### ["):
        return None
    line = line.strip()
    if not line.startswith("### ["):
        return None
    rest = line[5:]  # after "### ["
    parts = rest.split("] [")
    if len(parts) < 4:
        return None
    timestamp = parts[0].strip()
    role = parts[1].strip()
    status = parts[-1].rstrip("]").strip()
    task = "] [".join(parts[2:-1]).strip()
    return (timestamp, role, task, status)


def load_entries(path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Load work log entries (latest first)."""
    p = path or WORK_LOG_PATH
    if not p.exists():
        return []
    with open(p, encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def save_entries(entries: List[Dict[str, Any]], path: Optional[Path] = None, max_entries: int = MAX_ENTRIES) -> None:
    """Save work log; keep only last max_entries (oldest dropped)."""
    p = path or WORK_LOG_PATH
    trimmed = entries[:max_entries]
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(trimmed, f, indent=2, ensure_ascii=False)


def entry_to_markdown(entry: Dict[str, Any]) -> str:
    """Format one entry as markdown (same format as before)."""
    ts = entry.get("timestamp", "")
    role = entry.get("role", "")
    task = entry.get("task", "")
    status = entry.get("status", "")
    content = entry.get("content", "").strip()
    head = f"### [{ts}] [{role}] [{task}] [{status}]"
    if not content:
        return head
    return head + "\n" + content


def recent_markdown(entries: Optional[List[Dict[str, Any]]] = None, n: int = RECENT_N) -> str:
    """Return markdown for the last n entries (latest first)."""
    entries = entries or load_entries()
    block = []
    for e in entries[:n]:
        block.append(entry_to_markdown(e))
    return "\n\n".join(block)


def append_entry(
    timestamp: str,
    role: str,
    task: str,
    status: str,
    content: str = "",
    path: Optional[Path] = None,
    max_entries: int = MAX_ENTRIES,
) -> None:
    """Prepend one entry (latest first) and save."""
    entries = load_entries(path)
    entries.insert(0, {
        "timestamp": timestamp,
        "role": role,
        "task": task,
        "status": status,
        "content": content.strip(),
    })
    save_entries(entries, path=path, max_entries=max_entries)


def parse_workspace_log_section(text: str) -> List[Dict[str, Any]]:
    """Parse Work Log section markdown into list of entries (latest first)."""
    entries = []
    blocks = re.split(r"\n(?=### \[)", text)
    for block in blocks:
        block = block.strip()
        if not block or not block.startswith("### ["):
            continue
        lines = block.split("\n")
        parsed = _parse_header(lines[0])
        if not parsed:
            continue
        ts, role, task, status = parsed
        content_lines = []
        for line in lines[1:]:
            if line.strip() == "---":
                break
            if line.startswith("### [") and "]" in line:
                break
            content_lines.append(line)
        content = "\n".join(content_lines).strip()
        entries.append({
            "timestamp": ts,
            "role": role,
            "task": task,
            "status": status,
            "content": content,
        })
    return entries
