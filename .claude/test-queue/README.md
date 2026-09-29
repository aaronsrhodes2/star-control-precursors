# Test Queue — dispatch walks to the testing chat

A simple file-based queue so the design chat and image chat can request walk-test runs without opening pygame windows themselves. The testing chat polls this directory and processes jobs.

## Why this exists

Pygame creates a window by default, steals focus, plays audio. When a parallel chat runs a walk-test, the human is disrupted. The dispatch protocol routes test runs through the testing chat, which always invokes pygame with `SDL_VIDEODRIVER=dummy` + `SDL_AUDIODRIVER=dummy` (no window, no audio).

## Layout

```
.claude/test-queue/
├── inbox/                  drop request JSON files here
│   ├── .processed/         successfully run requests get moved here
│   └── .error/             malformed requests get moved here
├── done/                   result JSON files appear here, named to match the request id
└── logs/                   full stdout/stderr per job
```

## Filing a job

Write a JSON file to `inbox/<id>.json` where `<id>` is unique (use an ISO timestamp + short name):

```json
{
  "id": "2026-05-17T0900-bio_archive",
  "tests": ["walk_bio_archive"],
  "worktree": "elegant-bartik-733a37",
  "requester": "design-chat",
  "note": "added a new entry to ARCHIVE_ENTRIES; want to confirm catalog still loads"
}
```

Fields:
- `id` (required) — used as the result filename and log filename. Make it unique.
- `tests` (required) — list of walk names. Use `["all"]` to run every walk in the SCRIPTS registry.
- `worktree` (required) — which worktree's code to test. Examples: `"elegant-bartik-733a37"`, `"distracted-lederberg-56c64c"`. Use `""` or `"ROOT"` to test the project root checkout.
- `requester` (optional) — free-text identifier of who filed it. Helps the testing chat triage.
- `note` (optional) — free-text. Helps the testing chat report meaningfully.

**Absolute path for `Write` from another chat:**
```
D:\Aaron\development\star-control-precursors\.claude\test-queue\inbox\<id>.json
```

## Reading results

After the testing chat processes a job, it writes:

```json
{
  "id": "2026-05-17T0900-bio_archive",
  "status": "passed",
  "summary": "5 passed, 0 failed across 1 test(s)",
  "details": [
    {"test": "walk_bio_archive", "passed": 5, "failed": 0,
     "ok": true, "summary_line": "Test complete: 5 passed, 0 failed.",
     "exit_code": 0}
  ],
  "log": ".claude/test-queue/logs/2026-05-17T0900-bio_archive.log",
  "completed_at": "2026-05-17T09:01:32+00:00",
  "request": {... the original request ...}
}
```

`status` is one of `passed` / `failed` / `error`. Read the full log at `log` if `status` is not `passed`.

## How the testing chat polls

Self-paced `/loop`: every ~15 minutes when idle, immediately if already active. Quiet when inbox is empty. Each tick runs:

```
python tools/run_test_jobs.py --once
```

That script processes every file in `inbox/`, runs the requested tests with `SDL_VIDEODRIVER=dummy` + `SDL_AUDIODRIVER=dummy`, writes results to `done/`, and moves the inbox file to `inbox/.processed/` (success) or `inbox/.error/` (malformed).

## For humans inspecting the queue

- `ls .claude/test-queue/inbox/` — pending jobs
- `ls .claude/test-queue/done/` — finished jobs
- `cat .claude/test-queue/done/<id>.json | jq .summary` — quick result lookup
- `cat .claude/test-queue/logs/<id>.log` — full output of the run

## What NOT to file

- Open-ended manual exploration ("play the game and report bugs") — that's a real chat conversation, not a queueable job.
- Anything that needs human judgement on visual output — the dummy video driver disables rendering, so screenshots/colour checks won't work.
- Long-running performance benchmarks — the runner has a 600s per-test timeout.
