"""Single-page project status — aggregates HANDOFFs, test-queue, and
recent git activity across all four chat lanes.

Reads (no writes):
- `references/lore/HANDOFF_design_chat.md`
- `references/lore/HANDOFF_lore_chat.md`
- `references/lore/HANDOFF_image_chat.md`
- `references/lore/HANDOFF_audio_chat.md`
- `references/lore/HANDOFF_testing_chat.md`
- `.claude/test-queue/inbox/`  (pending jobs)
- `.claude/test-queue/done/`   (completed jobs, last N)
- `git log --oneline -n 20`

Prints a one-page summary with:
- Per-chat dispatch counts: open vs processed
- Most-recent top-of-doc entry title per chat
- Pending test-queue jobs
- Recent commits
- Quick triage hints (entries that have been open the longest)

Run anytime: `python tools/status_dashboard.py`
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from collections import Counter


_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent
_LORE_DIR = _PROJECT_ROOT / "references" / "lore"
_TEST_QUEUE_DIR = _PROJECT_ROOT / ".claude" / "test-queue"

HANDOFFS = (
    ("Design",   "HANDOFF_design_chat.md"),
    ("Lore",     "HANDOFF_lore_chat.md"),
    ("Image",    "HANDOFF_image_chat.md"),
    ("Audio",    "HANDOFF_audio_chat.md"),
    ("Testing",  "HANDOFF_testing_chat.md"),
    ("Combat",   "HANDOFF_combat_chat.md"),
)


# Match section headers like "## 2026-05-17 — Some title".
_SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
# Match status lines anywhere in a section.
_STATUS_RE = re.compile(
    r"\*\*Status\*\*\s*:\s*(.+?)(?:\n|$)|^Status\s*:\s*(.+?)(?:\n|$)",
    re.MULTILINE,
)


def _classify_status(text: str) -> str:
    """Heuristic: scan a section's body for the status marker.

    Canonical status enum (richer convention introduced 2026-05-17):
    - ✅ PROCESSED   — work shipped; entry can be pruned next session
    - ⏳ IN-PROGRESS — work partially shipped, more to come (typical of
                       MVP-shipped, follow-ups-deferred entries)
    - 🗄️ BACKLOG     — recognized work, gated on something else first
    - ❌ WONT-DO    — explicitly de-prioritized
    - ☐ OPEN        — not yet started; eligible for pickup

    Falls back to UNKNOWN for sections without a recognizable marker.
    """
    if "✅ PROCESSED" in text:
        return "PROCESSED"
    if "⏳ IN-PROGRESS" in text or "⏳ IN PROGRESS" in text:
        return "IN-PROGRESS"
    if "❌ WONT-DO" in text or "❌ Won't do" in text:
        return "WONT-DO"
    if "🗄️ Backlog" in text or "☐ Backlog" in text or "Status: Backlog" in text:
        return "BACKLOG"
    if "☐ Open" in text or "Status: ☐" in text:
        return "OPEN"
    return "UNKNOWN"


def _parse_handoff(path: Path) -> list[dict]:
    """Return a list of section summaries for a HANDOFF doc.
    Each section: {title, status, lines}.
    """
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    # Split on ## headers — first chunk is preamble, skip it
    parts = re.split(r"^##\s", text, flags=re.MULTILINE)
    sections: list[dict] = []
    for chunk in parts[1:]:
        first_newline = chunk.find("\n")
        if first_newline < 0:
            continue
        title = chunk[:first_newline].strip()
        body = chunk[first_newline + 1:]
        status = _classify_status(body)
        sections.append({
            "title": title,
            "status": status,
            "lines": body.count("\n"),
        })
    return sections


def _recent_commits(n: int = 10) -> list[str]:
    try:
        out = subprocess.run(
            ["git", "log", "--oneline", f"-n{n}"],
            capture_output=True, text=True, cwd=str(_PROJECT_ROOT),
        )
        if out.returncode != 0:
            return []
        return [line.strip() for line in out.stdout.splitlines() if line.strip()]
    except (FileNotFoundError, subprocess.SubprocessError):
        return []


def _list_queue(subdir: str) -> list[str]:
    p = _TEST_QUEUE_DIR / subdir
    if not p.exists():
        return []
    return sorted(f.name for f in p.iterdir() if f.is_file())


def main() -> int:
    print("=" * 70)
    print("STAR CONTROL ZERO — project status dashboard")
    print("=" * 70)

    # Per-lane status counts + most-recent open
    totals = Counter()
    for lane, fname in HANDOFFS:
        sections = _parse_handoff(_LORE_DIR / fname)
        counts = Counter(s["status"] for s in sections)
        for k, v in counts.items():
            totals[k] += v

        # Most-recent open section title (prefer OPEN, then IN-PROGRESS)
        most_recent_open = next(
            (s["title"] for s in sections if s["status"] == "OPEN"),
            None,
        )
        if most_recent_open is None:
            most_recent_open = next(
                (s["title"] for s in sections if s["status"] == "IN-PROGRESS"),
                None,
            )
        print(
            f"\n[{lane:7s}]  "
            f"open={counts.get('OPEN', 0):3d}  "
            f"in-prog={counts.get('IN-PROGRESS', 0):3d}  "
            f"processed={counts.get('PROCESSED', 0):3d}  "
            f"backlog={counts.get('BACKLOG', 0):3d}  "
            f"wont-do={counts.get('WONT-DO', 0):3d}  "
            f"unknown={counts.get('UNKNOWN', 0):3d}"
        )
        if most_recent_open:
            t = most_recent_open
            if len(t) > 65:
                t = t[:62] + "..."
            print(f"           top-open: {t}")

    print()
    print(
        f"[totals]  open={totals.get('OPEN', 0)}  "
        f"in-prog={totals.get('IN-PROGRESS', 0)}  "
        f"processed={totals.get('PROCESSED', 0)}  "
        f"backlog={totals.get('BACKLOG', 0)}  "
        f"wont-do={totals.get('WONT-DO', 0)}"
    )

    # Test queue
    print()
    print("[test-queue]")
    pending = _list_queue("inbox")
    done = _list_queue("done")
    if pending:
        print(f"  pending in inbox ({len(pending)}):")
        for name in pending:
            print(f"    - {name}")
    else:
        print("  inbox empty")
    if done:
        recent_done = done[-5:]
        print(f"  recent done ({len(done)} total, last 5):")
        for name in recent_done:
            print(f"    - {name}")

    # Recent commits
    print()
    print("[recent commits]")
    commits = _recent_commits(10)
    if commits:
        for line in commits:
            print(f"  {line}")
    else:
        print("  (git unavailable)")

    print()
    print("=" * 70)
    total_open = totals.get("OPEN", 0)
    print(
        f"Next move suggestion: "
        f"{'pick up an OPEN dispatch from a lane with capacity' if total_open else 'queue more design work; lanes are caught up'}"
    )
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
