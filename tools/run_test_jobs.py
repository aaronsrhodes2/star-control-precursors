"""Process the .claude/test-queue/ inbox.

Reads JSON request files, runs the requested walks (always with
SDL_VIDEODRIVER=dummy + SDL_AUDIODRIVER=dummy so no window appears),
writes result JSON to done/, full output to logs/, and moves the
inbox file to .processed/ (or .error/ on malformed input).

Usage:
    python tools/run_test_jobs.py --once       # process inbox once and exit (use with /loop)
    python tools/run_test_jobs.py              # loop forever, polling every 60s
    python tools/run_test_jobs.py --list       # list pending inbox files

Protocol spec: .claude/test-queue/README.md
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


# Project root is hard-coded so the script works regardless of which
# worktree it's run from.
PROJECT_ROOT = Path("D:/Aaron/development/star-control-precursors")
QUEUE_DIR    = PROJECT_ROOT / ".claude" / "test-queue"
INBOX        = QUEUE_DIR / "inbox"
DONE         = QUEUE_DIR / "done"
LOGS         = QUEUE_DIR / "logs"
PROCESSED    = INBOX / ".processed"
ERROR_DIR    = INBOX / ".error"

# Always overlay these — every test run is silent, every time.
ENV_OVERLAY = {
    "PYTHONPATH":      "src",
    "SDL_VIDEODRIVER": "dummy",
    "SDL_AUDIODRIVER": "dummy",
}

# Per-walk subprocess timeout. The longest existing walk (walk_tutorial_arc)
# takes ~80s at 3x speed; 600s gives 7x headroom.
PER_TEST_TIMEOUT_S = 600


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _resolve_worktree(worktree: str) -> Path:
    """Map a worktree name to its absolute path. Empty / 'ROOT' / 'main' = project root."""
    if worktree in ("", "ROOT", "root", "main"):
        return PROJECT_ROOT
    wt = PROJECT_ROOT / ".claude" / "worktrees" / worktree
    if not wt.exists():
        raise FileNotFoundError(f"worktree not found: {wt}")
    return wt


def _list_jobs() -> list[Path]:
    if not INBOX.exists():
        return []
    return sorted(
        p for p in INBOX.iterdir()
        if p.is_file() and p.suffix == ".json" and not p.name.startswith(".")
    )


def _discover_tests(worktree_dir: Path) -> list[str]:
    """Run a one-shot Python in the target worktree to list its SCRIPTS keys."""
    env = os.environ.copy()
    env.update(ENV_OVERLAY)
    proc = subprocess.run(
        [sys.executable, "-c",
         "from scz.testing.scripts import SCRIPTS; "
         "print('\\n'.join(sorted(SCRIPTS)))"],
        cwd=worktree_dir,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def _parse_summary(line: str | None) -> tuple[int, int]:
    """Parse 'Test complete: 9 passed, 0 failed.' → (9, 0). Returns (0,0) on failure."""
    if not line:
        return (0, 0)
    tokens = line.replace(",", "").replace(".", "").replace(":", "").split()
    passed = failed = 0
    try:
        passed = int(tokens[tokens.index("passed") - 1])
        failed = int(tokens[tokens.index("failed") - 1])
    except (ValueError, IndexError):
        pass
    return (passed, failed)


def _run_one_test(worktree_dir: Path, test_name: str) -> dict:
    env = os.environ.copy()
    env.update(ENV_OVERLAY)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "scz", "--windowed", "--test", test_name],
            cwd=worktree_dir,
            env=env,
            capture_output=True,
            text=True,
            timeout=PER_TEST_TIMEOUT_S,
        )
        timed_out = False
        exit_code = result.returncode
        output = (result.stdout or "") + (result.stderr or "")
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        exit_code = -1
        output = (exc.stdout or "") + (exc.stderr or "") if isinstance(exc.stdout, str) else ""
        output += f"\n[run_test_jobs] TIMEOUT after {PER_TEST_TIMEOUT_S}s\n"

    summary_line = next(
        (l for l in output.splitlines() if l.startswith("Test complete")),
        None,
    )
    passed, failed = _parse_summary(summary_line)
    ok = (summary_line is not None) and failed == 0 and not timed_out
    return {
        "test": test_name,
        "passed": passed,
        "failed": failed,
        "ok": ok,
        "timed_out": timed_out,
        "exit_code": exit_code,
        "summary_line": summary_line or "(no Test-complete line found)",
        "output": output,
    }


def _process_job(job_path: Path) -> dict:
    """Read job_path, run its tests, write results, move inbox file. Returns the result dict."""
    raw = job_path.read_text(encoding="utf-8")
    try:
        job = json.loads(raw)
    except json.JSONDecodeError as e:
        ERROR_DIR.mkdir(parents=True, exist_ok=True)
        shutil.move(str(job_path), str(ERROR_DIR / job_path.name))
        return {
            "id": job_path.stem,
            "status": "error",
            "summary": f"malformed JSON: {e}",
            "completed_at": _now_iso(),
        }

    job_id        = job.get("id") or job_path.stem
    worktree_name = job.get("worktree", "")
    tests         = job.get("tests", [])

    DONE.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    ERROR_DIR.mkdir(parents=True, exist_ok=True)

    log_path = LOGS / f"{job_id}.log"

    # Resolve worktree
    try:
        worktree_dir = _resolve_worktree(worktree_name)
    except FileNotFoundError as e:
        result = {
            "id": job_id, "status": "error",
            "summary": str(e), "request": job, "completed_at": _now_iso(),
        }
        (DONE / f"{job_id}.json").write_text(json.dumps(result, indent=2))
        shutil.move(str(job_path), str(ERROR_DIR / job_path.name))
        return result

    # Resolve test list — discover available if 'all'
    if tests == ["all"]:
        try:
            tests = _discover_tests(worktree_dir)
        except subprocess.TimeoutExpired:
            tests = []

    if not tests:
        result = {
            "id": job_id, "status": "error",
            "summary": "no tests resolved",
            "request": job, "completed_at": _now_iso(),
        }
        (DONE / f"{job_id}.json").write_text(json.dumps(result, indent=2))
        shutil.move(str(job_path), str(ERROR_DIR / job_path.name))
        return result

    # Run tests sequentially, writing the full log as we go
    details = []
    total_p, total_f = 0, 0
    started_at = _now_iso()
    with log_path.open("w", encoding="utf-8") as logf:
        logf.write(f"# Job {job_id}  ·  worktree {worktree_name!r}  ·  {len(tests)} test(s)\n")
        logf.write(f"# started_at {started_at}\n\n")
        for test_name in tests:
            logf.write(f"\n===== {test_name} =====\n")
            r = _run_one_test(worktree_dir, test_name)
            logf.write(r["output"])
            logf.write(f"\n--- {test_name}: {r['summary_line']}\n")
            total_p += r["passed"]
            total_f += r["failed"]
            # Don't bloat the JSON with raw output — it's in the log file
            r.pop("output", None)
            details.append(r)

    all_ok = all(d["ok"] for d in details)
    status = "passed" if all_ok else "failed"

    result = {
        "id": job_id,
        "status": status,
        "summary": f"{total_p} passed, {total_f} failed across {len(tests)} test(s)",
        "tests_run": [d["test"] for d in details],
        "details": details,
        "log": str(log_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "started_at": started_at,
        "completed_at": _now_iso(),
        "request": job,
    }
    (DONE / f"{job_id}.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    # Move inbox file to .processed/
    shutil.move(str(job_path), str(PROCESSED / job_path.name))
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--once", action="store_true",
                    help="process inbox once then exit (use with /loop)")
    ap.add_argument("--poll-interval", type=int, default=60,
                    help="seconds between polls when not --once (default 60)")
    ap.add_argument("--list", action="store_true",
                    help="just list pending jobs and exit")
    args = ap.parse_args()

    if args.list:
        jobs = _list_jobs()
        if not jobs:
            print("inbox: empty")
            return 0
        print(f"inbox: {len(jobs)} pending job(s)")
        for p in jobs:
            print(f"  {p.name}")
        return 0

    while True:
        jobs = _list_jobs()
        if not jobs:
            if args.once:
                print("inbox: empty")
                return 0
        for job_path in jobs:
            try:
                r = _process_job(job_path)
                print(f"[{r['id']}] {r['status']}: {r['summary']}")
            except Exception as e:
                print(f"[{job_path.name}] UNCAUGHT: {e}", file=sys.stderr)
                # Last-ditch: try to move it to .error so we don't loop on it
                try:
                    ERROR_DIR.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(job_path), str(ERROR_DIR / job_path.name))
                except Exception:
                    pass
        if args.once:
            return 0
        time.sleep(args.poll_interval)


if __name__ == "__main__":
    sys.exit(main())
