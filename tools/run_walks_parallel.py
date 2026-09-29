"""Parallel walk-test runner — fan out all walks across worker
processes; aggregate results.

Replaces the sequential `for t in walks; python -m scz.main --test $t`
loop. On a 27-walk regression, the sequential runner takes ~5 minutes
wall-clock (long combat walks are the long pole). Running 8 walks in
parallel cuts that to ~1.5 minutes — the slowest walk is the bound.

Usage:
    python tools/run_walks_parallel.py                # all walks
    python tools/run_walks_parallel.py walk_a walk_b  # subset
    python tools/run_walks_parallel.py --workers 4    # tune parallelism
    python tools/run_walks_parallel.py --verbose      # stream stdout per walk

Output: one line per walk with pass/fail counts, plus a final summary.
Exit code: 0 if all walks pass, 1 if any failed, 2 if any errored.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import os
import subprocess
import sys
import time
from pathlib import Path


# Project paths — script works regardless of which worktree you launch
# it from (auto-detects via parent walk).
_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent
_SRC_DIR = _PROJECT_ROOT / "src"


def list_all_walks() -> list[str]:
    """Discover every walk in SCRIPTS by importing the registry."""
    env = os.environ.copy()
    env["SDL_VIDEODRIVER"] = "dummy"
    env["SDL_AUDIODRIVER"] = "dummy"
    env["PYTHONPATH"] = str(_SRC_DIR)
    result = subprocess.run(
        [
            sys.executable, "-c",
            "from scz.testing.scripts import SCRIPTS; "
            "print('\\n'.join(sorted(SCRIPTS)))",
        ],
        capture_output=True, text=True, env=env, cwd=str(_SRC_DIR),
    )
    if result.returncode != 0:
        print(f"[parallel] failed to enumerate walks: {result.stderr}",
              file=sys.stderr)
        sys.exit(2)
    return [w.strip() for w in result.stdout.splitlines() if w.strip()]


def run_one_walk(walk: str, verbose: bool = False) -> dict:
    """Run a single walk in a subprocess. Returns a result dict with
    name, exit_code, passed, failed, duration_s, summary_line.
    """
    env = os.environ.copy()
    env["SDL_VIDEODRIVER"] = "dummy"
    env["SDL_AUDIODRIVER"] = "dummy"
    env["PYTHONPATH"] = str(_SRC_DIR)
    start = time.monotonic()
    proc = subprocess.run(
        [sys.executable, "-m", "scz.main", "--test", walk],
        capture_output=True, text=True, env=env, cwd=str(_SRC_DIR),
        timeout=600,
    )
    duration = time.monotonic() - start
    # Parse "Test complete: X passed, Y failed." line
    passed = 0
    failed = 0
    summary_line = ""
    for line in proc.stdout.splitlines():
        if "Test complete:" in line:
            summary_line = line.strip()
            # Format: "Test complete: 5 passed, 0 failed."
            try:
                rest = line.split("Test complete:")[1].strip().rstrip(".")
                parts = [p.strip() for p in rest.split(",")]
                for part in parts:
                    if "passed" in part:
                        passed = int(part.split()[0])
                    elif "failed" in part:
                        failed = int(part.split()[0])
            except (IndexError, ValueError):
                pass
            break
    if verbose:
        print(f"\n===== {walk} =====")
        print(proc.stdout)
        if proc.stderr:
            print("[stderr]", proc.stderr, file=sys.stderr)
    return {
        "name": walk,
        "exit_code": proc.returncode,
        "passed": passed,
        "failed": failed,
        "duration_s": duration,
        "summary_line": summary_line or "(no Test complete line)",
        "stderr_tail": proc.stderr[-400:] if proc.stderr else "",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Parallel walk-test runner.",
    )
    parser.add_argument(
        "walks", nargs="*",
        help="Specific walks to run (default: all walks in SCRIPTS).",
    )
    parser.add_argument(
        "--workers", type=int, default=8,
        help="Max parallel walks (default: 8).",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Stream each walk's full stdout to console.",
    )
    args = parser.parse_args()

    walks = args.walks or list_all_walks()
    print(
        f"[parallel] running {len(walks)} walks "
        f"with up to {args.workers} workers ..."
    )

    overall_start = time.monotonic()
    results: list[dict] = []
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=args.workers,
    ) as ex:
        futures = {
            ex.submit(run_one_walk, w, args.verbose): w
            for w in walks
        }
        for fut in concurrent.futures.as_completed(futures):
            r = fut.result()
            results.append(r)
            badge = (
                "OK  " if r["failed"] == 0 and r["exit_code"] == 0
                else "FAIL"
            )
            print(
                f"  [{badge}] {r['name']:42s}  "
                f"{r['passed']:3d} passed, "
                f"{r['failed']:3d} failed  "
                f"({r['duration_s']:5.1f}s)"
            )
    overall_duration = time.monotonic() - overall_start

    # Sort results by name for the summary
    results.sort(key=lambda r: r["name"])

    total_passed = sum(r["passed"] for r in results)
    total_failed = sum(r["failed"] for r in results)
    erroring = [r for r in results if r["exit_code"] != 0]
    failing = [r for r in results if r["failed"] > 0]

    print()
    print("=" * 62)
    print(
        f"[parallel] {len(walks)} walks  ·  "
        f"{total_passed} assertions passed, "
        f"{total_failed} failed  ·  "
        f"{overall_duration:.1f}s wall-clock"
    )
    print("=" * 62)

    if failing:
        print(f"\nFailing walks ({len(failing)}):")
        for r in failing:
            print(f"  - {r['name']}  ({r['failed']} failed)")
    if erroring:
        print(f"\nErroring walks ({len(erroring)}):")
        for r in erroring:
            print(f"  - {r['name']}  (exit {r['exit_code']})")
            if r["stderr_tail"]:
                for line in r["stderr_tail"].splitlines()[-4:]:
                    print(f"      {line}")

    if erroring:
        return 2
    if failing:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
