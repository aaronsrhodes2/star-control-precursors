"""Validate every context dir under assets/music/.

Wraps tools/audio_inspect_stems.py and reports per-context summary +
totals. Exit code is non-zero if ANY stem flagged.

Usage:
    .venv/Scripts/python.exe tools/audio_inspect_all.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MUSIC_ROOT = ROOT / "assets" / "music"
INSPECT = ROOT / "tools" / "audio_inspect_stems.py"
PY = sys.executable


def main() -> int:
    if not MUSIC_ROOT.is_dir():
        print(f"no music dir at {MUSIC_ROOT}", file=sys.stderr)
        return 2
    dirs = sorted(p for p in MUSIC_ROOT.iterdir() if p.is_dir())
    if not dirs:
        print("no contexts to inspect", file=sys.stderr)
        return 1
    any_fail = False
    print(f"\nInspecting {len(dirs)} contexts under {MUSIC_ROOT}\n")
    for d in dirs:
        print("=" * 70)
        print(f"CONTEXT: {d.name}")
        print("=" * 70)
        r = subprocess.run(
            [PY, str(INSPECT), str(d)],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        sys.stdout.write(r.stdout)
        if r.stderr:
            sys.stderr.write(r.stderr)
        if r.returncode != 0:
            any_fail = True
    print("\n" + "=" * 70)
    print("OVERALL:", "FAIL (flags present)" if any_fail else "OK")
    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main())
