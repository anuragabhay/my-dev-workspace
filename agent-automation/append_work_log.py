#!/usr/bin/env python3
"""
Append a work log entry to agent-automation/work_log.json and optionally
update PROJECT_WORKSPACE.md "Recent Work Log (last 10)".
Usage:
  python append_work_log.py --timestamp "2026-02-14 25:00 UTC" --role "Lead Engineer" --task "Task name" --status "✅ COMPLETED" --content "- Bullet one\n- Bullet two"
  echo "- Bullet" | python append_work_log.py --timestamp "..." --role "..." --task "..." --status "✅ COMPLETED"  # content from stdin
  python append_work_log.py --migrate  # one-off: parse WORKSPACE Work Log section into work_log.json
  python append_work_log.py --update-workspace  # rewrite Recent Work Log (last 10) in PROJECT_WORKSPACE.md from JSON
"""
import argparse
import sys
from pathlib import Path

# Run from agent-automation or project root
SCRIPT_DIR = Path(__file__).resolve().parent
if (SCRIPT_DIR / "work_log_utils.py").exists():
    sys.path.insert(0, str(SCRIPT_DIR))
from work_log_utils import (
    load_entries,
    save_entries,
    append_entry,
    recent_markdown,
    parse_workspace_log_section,
    WORK_LOG_PATH,
    WORKSPACE_PATH,
    MAX_ENTRIES,
    RECENT_N,
)


def migrate() -> None:
    """Parse PROJECT_WORKSPACE.md Work Log section and save to work_log.json."""
    path = WORKSPACE_PATH
    if not path.exists():
        print(f"Workspace not found: {path}", file=sys.stderr)
        sys.exit(1)
    text = path.read_text(encoding="utf-8")
    # Extract section between "## 📝 Work Log" and "## ✅ Approval"
    start = text.find("## 📝 Work Log")
    end = text.find("## ✅ Approval")
    if start == -1 or end == -1:
        print("Could not find Work Log section boundaries.", file=sys.stderr)
        sys.exit(1)
    section = text[start:end]
    entries = parse_workspace_log_section(section)
    save_entries(entries)
    print(f"Migrated {len(entries)} entries to {WORK_LOG_PATH}")


def update_workspace() -> None:
    """Replace 'Recent Work Log (last 10)' in PROJECT_WORKSPACE.md with last 10 from JSON."""
    path = WORKSPACE_PATH
    if not path.exists():
        print(f"Workspace not found: {path}", file=sys.stderr)
        sys.exit(1)
    entries = load_entries()
    recent = recent_markdown(entries=entries, n=RECENT_N)
    text = path.read_text(encoding="utf-8")
    # Replace the block between "## 📝 Recent Work Log (last 10)" and "Full log:" or next "## "
    import re
    pattern = re.compile(
        r"(## 📝 Recent Work Log \(last 10\)\s*\n\n).*?(\n\nFull log:.*?(\n\n## |\Z))",
        re.DOTALL,
    )
    new_text, n = pattern.subn(lambda m: m.group(1) + recent + m.group(2), text, count=1)
    if n == 0:
        # Maybe section title is different; try replacing from "## 📝" to "Full log:" line then "## "
        pattern2 = re.compile(
            r"(## 📝 Recent Work Log \(last 10\)\s*\n\n).*?(\nFull log: [^\n]+\n\n)(?=## )",
            re.DOTALL,
        )
        new_text, n = pattern2.subn(
            lambda m: m.group(1) + recent + "\n\n" + m.group(2), text, count=1
        )
    if n > 0:
        path.write_text(new_text, encoding="utf-8")
        print(f"Updated {path} with last {RECENT_N} entries.")
    else:
        print("Could not find Recent Work Log section to replace.", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    ap = argparse.ArgumentParser(description="Append work log entry or migrate/update workspace")
    ap.add_argument("--migrate", action="store_true", help="Parse WORKSPACE Work Log into work_log.json")
    ap.add_argument("--update-workspace", action="store_true", help="Write Recent Work Log (last 10) to PROJECT_WORKSPACE.md")
    ap.add_argument("--timestamp", type=str, help="Entry timestamp (e.g. 2026-02-14 25:00 UTC)")
    ap.add_argument("--role", type=str, help="Role (e.g. Lead Engineer)")
    ap.add_argument("--task", type=str, help="Task name")
    ap.add_argument("--status", type=str, help="Status (e.g. ✅ COMPLETED)")
    ap.add_argument("--content", type=str, default="", help="Bullet content (or read from stdin)")
    ap.add_argument("--max-entries", type=int, default=MAX_ENTRIES, help=f"Trim JSON to this many entries (default {MAX_ENTRIES})")
    args = ap.parse_args()

    if args.migrate:
        migrate()
        return
    if args.update_workspace:
        update_workspace()
        return

    if not args.timestamp or not args.role or not args.task or not args.status:
        print("For append: provide --timestamp, --role, --task, --status (and optionally --content or stdin).", file=sys.stderr)
        sys.exit(1)
    content = args.content
    if not content and not sys.stdin.isatty():
        content = sys.stdin.read()
    append_entry(
        timestamp=args.timestamp,
        role=args.role,
        task=args.task,
        status=args.status,
        content=content,
        max_entries=args.max_entries,
    )
    print(f"Appended entry to {WORK_LOG_PATH}")


if __name__ == "__main__":
    main()
