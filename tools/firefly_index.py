"""Firefly image-pipeline manifest CRUD.

Reads/writes assets/generated_drafts/firefly/_manifest.json — the single
source of truth for what's been generated, what status each image is
in, and where each one will land if accepted.

Schema per entry (keyed by "<category>/<slug>"):
{
  "prompt_path":   "tools/firefly_prompts/<category>/<slug>.txt",
  "image_path":    "assets/generated_drafts/firefly/<category>/<slug>.png",
  "aspect":        "1:1",
  "generated_at":  "2026-05-16T22:14:00Z",
  "status":        "queued" | "pending" | "keep" | "reject" | "wired",
  "tags":          ["melnorme", "ship", "combat-sprite"],
  "destination":   "assets/ships/melnorme/trader-big-000.png",
  "manifest_entry_to_update": "ships/melnorme/trader-big-000.png",
  "notes":         "optional Aaron notes"
}

CLI:
    python tools/firefly_index.py list                   # all entries
    python tools/firefly_index.py list --status pending  # filter
    python tools/firefly_index.py list --category tier1_ships
    python tools/firefly_index.py add  <key> --prompt PATH --image PATH ...
    python tools/firefly_index.py mark <key> keep|reject|pending|wired --notes "..."
    python tools/firefly_index.py show <key>
    python tools/firefly_index.py scan                   # discover prompts, add queued entries
    python tools/firefly_index.py stats                  # status counts per category
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = ROOT / "tools" / "firefly_prompts"
CACHE_DIR = ROOT / "assets" / "generated_drafts" / "firefly"
MANIFEST_PATH = CACHE_DIR / "_manifest.json"

VALID_STATUSES = {"queued", "pending", "keep", "reject", "wired"}


def load() -> dict[str, dict[str, Any]]:
    if not MANIFEST_PATH.exists():
        return {}
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def save(data: dict[str, dict[str, Any]]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    ordered = {k: data[k] for k in sorted(data)}
    MANIFEST_PATH.write_text(
        json.dumps(ordered, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _key_from_paths(prompt_path: Path) -> str:
    rel = prompt_path.relative_to(PROMPTS_DIR)
    return rel.with_suffix("").as_posix()


def _parse_aspect_from_prompt(prompt_path: Path) -> str:
    """Read the '# aspect: X:Y' header from a prompt file. Default 1:1."""
    if not prompt_path.exists():
        return "1:1"
    for line in prompt_path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith("# aspect:"):
            return s.split(":", 1)[1].strip().lower().replace("aspect", "").strip()
        if s.startswith("# aspect"):
            return s.split(":", 1)[-1].strip()
        if not s.startswith("#"):
            break
    return "1:1"


def scan_prompts(data: dict[str, dict[str, Any]]) -> int:
    """Walk tools/firefly_prompts/tier*_*/*.txt and add any missing
    entries as status=queued. Returns count of newly-added entries."""
    added = 0
    for prompt_file in PROMPTS_DIR.glob("tier*_*/*.txt"):
        key = _key_from_paths(prompt_file)
        if key in data:
            continue
        category = prompt_file.parent.name
        slug = prompt_file.stem
        image_path = CACHE_DIR / category / f"{slug}.png"
        data[key] = {
            "prompt_path": prompt_file.relative_to(ROOT).as_posix(),
            "image_path": image_path.relative_to(ROOT).as_posix(),
            "aspect": _parse_aspect_from_prompt(prompt_file),
            "generated_at": None,
            "status": "queued",
            "tags": [category.replace("tier1_", "").replace("tier2_", "").replace("tier3_", "")],
            "destination": None,
            "manifest_entry_to_update": None,
            "notes": "",
        }
        added += 1
    return added


def cmd_list(args: argparse.Namespace) -> int:
    data = load()
    rows = []
    for k, v in data.items():
        if args.status and v["status"] != args.status:
            continue
        if args.category and not k.startswith(args.category + "/"):
            continue
        rows.append((k, v["status"], v.get("aspect", "?"),
                     "img" if v.get("generated_at") else "-"))
    print(f"{'key':60s} {'status':10s} {'aspect':6s} {'img':4s}")
    for r in rows:
        print(f"{r[0]:60s} {r[1]:10s} {r[2]:6s} {r[3]:4s}")
    print(f"\n{len(rows)} entries")
    return 0


def cmd_scan(args: argparse.Namespace) -> int:
    data = load()
    n = scan_prompts(data)
    save(data)
    print(f"scanned; added {n} new entries; total {len(data)}")
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    data = load()
    by_cat: dict[str, dict[str, int]] = {}
    for k, v in data.items():
        cat = k.split("/", 1)[0]
        st = v["status"]
        by_cat.setdefault(cat, {}).setdefault(st, 0)
        by_cat[cat][st] += 1
    print(f"{'category':25s} {'queued':>7} {'pending':>8} {'keep':>5} {'reject':>7} {'wired':>6}")
    for cat in sorted(by_cat):
        s = by_cat[cat]
        print(
            f"{cat:25s} {s.get('queued', 0):>7} {s.get('pending', 0):>8} "
            f"{s.get('keep', 0):>5} {s.get('reject', 0):>7} {s.get('wired', 0):>6}"
        )
    total = sum(sum(s.values()) for s in by_cat.values())
    print(f"\ntotal: {total} entries across {len(by_cat)} categories")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    data = load()
    entry = data.get(args.key)
    if entry is None:
        print(f"no entry for {args.key}", file=sys.stderr)
        return 1
    print(json.dumps(entry, indent=2))
    return 0


def cmd_mark(args: argparse.Namespace) -> int:
    if args.status not in VALID_STATUSES:
        print(f"status must be one of {sorted(VALID_STATUSES)}", file=sys.stderr)
        return 1
    data = load()
    if args.key not in data:
        print(f"no entry for {args.key}", file=sys.stderr)
        return 1
    data[args.key]["status"] = args.status
    if args.notes:
        data[args.key]["notes"] = args.notes
    if args.destination:
        data[args.key]["destination"] = args.destination
    save(data)
    print(f"marked {args.key} -> {args.status}")
    return 0


def cmd_record_generated(args: argparse.Namespace) -> int:
    """Mark an entry as pending (file just written by firefly drive)."""
    data = load()
    if args.key not in data:
        # Auto-add if scan hasn't picked it up
        scan_prompts(data)
        if args.key not in data:
            print(f"no prompt file for {args.key}", file=sys.stderr)
            return 1
    entry = data[args.key]
    entry["status"] = "pending"
    entry["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if args.image_path:
        entry["image_path"] = args.image_path
    save(data)
    print(f"recorded generation for {args.key}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list")
    p_list.add_argument("--status", default=None)
    p_list.add_argument("--category", default=None)
    p_list.set_defaults(func=cmd_list)

    p_scan = sub.add_parser("scan")
    p_scan.set_defaults(func=cmd_scan)

    p_stats = sub.add_parser("stats")
    p_stats.set_defaults(func=cmd_stats)

    p_show = sub.add_parser("show")
    p_show.add_argument("key")
    p_show.set_defaults(func=cmd_show)

    p_mark = sub.add_parser("mark")
    p_mark.add_argument("key")
    p_mark.add_argument("status")
    p_mark.add_argument("--notes", default=None)
    p_mark.add_argument("--destination", default=None)
    p_mark.set_defaults(func=cmd_mark)

    p_rec = sub.add_parser("record-generated")
    p_rec.add_argument("key")
    p_rec.add_argument("--image-path", default=None)
    p_rec.set_defaults(func=cmd_record_generated)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
