"""
Project structure tree for Phase 2 (Project Structure Panel).
Builds directory tree with configurable depth, lazy loading, and ignore list.
"""

from pathlib import Path
from typing import Any

# Configurable ignore list: dir/file names to exclude from tree
# Can be extended via TREE_IGNORE env (comma-separated) or overridden in code
_DEFAULT_IGNORE = frozenset({
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    ".env",
    ".env.local",
    ".env.*.local",
    ".DS_Store",
    ".cursor",
    "dist",
    "build",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
    "*.pyc",
})


def _get_ignore_set() -> frozenset[str]:
    """Return ignore set: default + optional env override."""
    ignore = set(_DEFAULT_IGNORE)
    env_ignore = __import__("os").environ.get("TREE_IGNORE", "").strip()
    if env_ignore:
        for name in env_ignore.split(","):
            n = name.strip()
            if n:
                ignore.add(n)
    return frozenset(ignore)


def _should_ignore(name: str, ignore: frozenset[str]) -> bool:
    """True if name should be ignored (exact or prefix match for patterns)."""
    if name in ignore:
        return True
    for pat in ignore:
        if pat.startswith("*") and name.endswith(pat[1:]):
            return True
    return False


def resolve_path_under_root(root: Path, path: str | None) -> Path | None:
    """
    Resolve path under workspace root. Rejects path traversal (..).
    Returns resolved Path if valid and exists, else None.
    For path=None or empty, returns root.
    """
    if not path or not path.strip():
        return root
    return validate_path_under_root(root, path, must_exist=True)


def validate_path_under_root(
    root: Path, path: str | None, must_exist: bool = False
) -> Path | None:
    """
    Validate path is under workspace root. Rejects path traversal (..).
    Returns resolved Path if valid, else None.
    For file read: use must_exist=True. For file write: use must_exist=False.
    """
    root = root.resolve()
    if not path or not path.strip():
        return None
    # Reject explicit path traversal
    if ".." in path or path.startswith("/"):
        return None
    # Normalize: remove leading slashes/dots
    clean = path.strip().lstrip("/.")
    if not clean:
        return None
    resolved = (root / clean).resolve()
    # Must be under root
    try:
        resolved.relative_to(root)
    except ValueError:
        return None
    if must_exist and not resolved.exists():
        return None
    return resolved


def resolve_file_for_read(root: Path, path: str | None) -> tuple[Path | None, str | None]:
    """
    Resolve file path for reading. Rejects path traversal.
    Returns (resolved_path, error_code). error_code is None on success.
    error_code: "400" = invalid path/traversal, "404" = not found or not a file.
    """
    root = root.resolve()
    if not path or not path.strip():
        return None, "400"
    if ".." in path or path.startswith("/"):
        return None, "400"
    clean = path.strip().lstrip("/.")
    if not clean:
        return None, "400"
    resolved = (root / clean).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        return None, "400"
    if not resolved.exists():
        return None, "404"
    if resolved.is_dir():
        return None, "404"
    return resolved, None


def resolve_file_for_write(root: Path, path: str | None) -> Path | None:
    """
    Resolve file path for writing. Rejects path traversal.
    Returns resolved Path if valid (under root; if exists, must not be dir), else None.
    """
    resolved = validate_path_under_root(root, path, must_exist=False)
    if resolved is None:
        return None
    if resolved.exists() and resolved.is_dir():
        return None
    return resolved


def build_tree(
    root: Path,
    target: Path,
    depth: int,
    lazy: bool,
    ignore: frozenset[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Build directory tree as list of nodes.
    Each node: { name, path, type: "file"|"dir", children?: [...] }
    - path: relative to root (or absolute string for API)
    - For lazy=True, dirs have no children until expanded via GET /api/tree?path=...
    """
    if ignore is None:
        ignore = _get_ignore_set()
    root = root.resolve()
    target = target.resolve()
    nodes: list[dict[str, Any]] = []

    if not target.is_dir():
        return nodes

    try:
        entries = sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except OSError:
        return nodes

    for entry in entries:
        if _should_ignore(entry.name, ignore):
            continue
        try:
            rel = entry.relative_to(root)
            path_str = str(rel).replace("\\", "/")
        except ValueError:
            continue

        node: dict[str, Any] = {
            "name": entry.name,
            "path": path_str or ".",
            "type": "dir" if entry.is_dir() else "file",
        }

        if entry.is_dir():
            if lazy:
                # Omit children; client fetches via GET /api/tree?path=...
                node["has_children"] = True
            elif depth > 0:
                child_nodes = build_tree(root, entry, depth - 1, lazy, ignore)
                node["children"] = child_nodes
        nodes.append(node)

    return nodes
