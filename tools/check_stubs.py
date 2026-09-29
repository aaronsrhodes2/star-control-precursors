"""Enumerate stub / TODO markers across the codebase, grouped by
owner-chat.

Greps src/ + tools/ + references/ for the canonical markers:

- `TODO_AVATAR`  → Image chat
- `TODO_LORE`    → Lore chat
- `TODO_AUDIO`   → Audio chat
- `TODO_DESIGN`  → Design chat (rarely; usually Design picks these
  up from HANDOFF_design_chat.md)
- `TODO`         → bare TODOs (uncategorized; print these last so
  they get noticed but don't dominate the report)

Each marker is printed with file:line and the rest of the line's
content. Output is grouped by owner-chat so you can see at a glance
how much is in-flight per lane.

Run: `python tools/check_stubs.py`
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path


_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent

# Markers in priority order. Each line gets categorized by the first
# matching marker.
MARKERS: tuple[tuple[str, str], ...] = (
    ("TODO_AVATAR", "Image"),
    ("TODO_LORE",   "Lore"),
    ("TODO_AUDIO",  "Audio"),
    ("TODO_DESIGN", "Design"),
    ("TODO_TESTING", "Testing"),
    ("TODO",        "Uncategorized"),
)

# Directories to search
SEARCH_DIRS = (
    "src",
    "tools",
    "references",
)

# File extensions to scan
SCAN_EXTENSIONS = frozenset({
    ".py", ".md", ".csv", ".json",
})


def scan_file(path: Path) -> list[tuple[int, str, str]]:
    """Yield (line_no, marker, line_text) for each marker hit.
    Returns the first marker that matched on each line — so a line
    with `TODO_AVATAR` doesn't also count as `TODO`.
    """
    hits: list[tuple[int, str, str]] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeError):
        return hits
    for line_no, line in enumerate(text.splitlines(), start=1):
        for marker, _owner in MARKERS:
            if marker in line:
                hits.append((line_no, marker, line.strip()))
                break
    return hits


def _ascii_safe(s: str) -> str:
    """Replace non-ASCII chars with '?' so the Windows cp1252 console
    doesn't crash on em-dashes / arrows / etc.
    """
    return s.encode("ascii", errors="replace").decode("ascii")


def main() -> int:
    grouped: dict[str, list[tuple[Path, int, str, str]]] = defaultdict(list)
    file_count = 0
    for sub in SEARCH_DIRS:
        root = _PROJECT_ROOT / sub
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in SCAN_EXTENSIONS:
                continue
            file_count += 1
            hits = scan_file(path)
            for line_no, marker, line in hits:
                owner = next(
                    (o for m, o in MARKERS if m == marker),
                    "Uncategorized",
                )
                grouped[owner].append((path, line_no, marker, line))

    total = sum(len(items) for items in grouped.values())
    print("=" * 70)
    print(f"STUB / TODO marker survey  ·  {file_count} files scanned")
    print("=" * 70)
    print(f"\nTotal markers found: {total}")
    for _marker, owner in MARKERS:
        items = grouped.get(owner, [])
        if not items:
            continue
        print(f"\n[{owner}]  ({len(items)} markers)")
        # Truncate per-owner to avoid wall-of-text; show first 30
        for i, (path, line_no, marker, line) in enumerate(items[:30]):
            rel = path.relative_to(_PROJECT_ROOT)
            # Trim line to terminal width
            trimmed = line if len(line) <= 120 else line[:117] + "..."
            print(_ascii_safe(f"  {rel}:{line_no}  [{marker}]  {trimmed}"))
        if len(items) > 30:
            print(f"  ... and {len(items) - 30} more")
    print()
    print("=" * 70)
    # Brief summary line per owner
    summary = ", ".join(
        f"{o}={len(grouped.get(o, []))}"
        for _m, o in MARKERS
        if grouped.get(o)
    )
    print(f"Summary: {summary}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
