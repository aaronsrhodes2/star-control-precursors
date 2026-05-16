"""Bulk-copy UQM graphical assets into our `assets/` tree as MVP
placeholders, and write a manifest tracking every copied file's
replacement status (per the project's `we-must-improve` golden rule —
see references/project-rules.md).

Categories copied:
    ships/         per-species combat sprites (all 3 sizes + .ani)
    comm/          alien dialog portraits + .ani
    nav/           hyperspace/system ambient backgrounds
    lander/        lander + lifeforms + hazards
    cutscene/      intro/ending/credits/spins story art
    ui/            menus, blueprints, activity spinners
    fonts/         per-species glyph fonts

Skipped (per the survey):
    addons/        3DO video/music — too big
    planets/       already extracted (separate tool)
    battle/        small, decorative — defer

Manifest format (assets/_PLACEHOLDERS.json):
    {
      "ships/androsynth/blazer-big-000.png": {
        "source": "base/ships/androsynth/blazer-big-000.png",
        "category": "ships",
        "context": "androsynth",
        "status": "placeholder",
        "replaced_at": null,
        "improved_with": null
      },
      ...
    }

`status` starts "placeholder" for everything. When we hand-author or
SD-generate a replacement, we update the entry in-place. The repo's
visible debt is the count of "placeholder" entries.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SRC_BASE = ROOT / "references" / "uqm-source" / "sc2" / "content" / "base"
ASSETS = ROOT / "assets"
MANIFEST_PATH = ASSETS / "_PLACEHOLDERS.json"


# What to copy, by category. Each entry is (subdir, list of glob patterns
# RELATIVE to base/subdir). The category name becomes the assets/<cat>/
# destination root.
EXTRACTION_PLAN: list[tuple[str, list[str]]] = [
    ("ships",    ["**/*.png", "**/*.ani"]),
    ("comm",     ["**/*.png", "**/*.ani"]),
    ("nav",      ["*.png", "*.ani"]),
    ("lander",   ["**/*.png", "**/*.ani", "**/*.ct"]),
    ("cutscene", ["**/*.png", "**/*.ani"]),
    ("ui",       ["*.png", "*.ani", "*.ct"]),
    ("fonts",    ["**/*.png", "**/*.ani"]),
]


def context_from_path(category: str, rel_path: Path) -> str:
    """Best-effort 'what is this for' tag — first directory under the
    category root if any, else 'misc'. e.g. 'ships/androsynth/...' →
    'androsynth'; 'nav/ambient-000.png' → 'misc'."""
    parts = rel_path.parts
    if len(parts) > 1:
        return parts[0]
    return "misc"


def main() -> int:
    if not SRC_BASE.exists():
        print(f"missing UQM base content at {SRC_BASE}", file=sys.stderr)
        return 1

    # Load existing manifest (preserve any "replaced"/"improved" entries
    # so re-running the extraction doesn't clobber upgrade tracking).
    existing: dict[str, dict] = {}
    if MANIFEST_PATH.exists():
        existing = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    manifest: dict[str, dict] = {}
    total_copied = 0
    total_skipped_existing = 0

    for category, patterns in EXTRACTION_PLAN:
        src_root = SRC_BASE / category
        if not src_root.exists():
            print(f"  WARN: source category {category} not found at {src_root}",
                  file=sys.stderr)
            continue
        dst_root = ASSETS / category
        dst_root.mkdir(parents=True, exist_ok=True)

        cat_count = 0
        for pattern in patterns:
            for src in src_root.glob(pattern):
                if not src.is_file():
                    continue
                rel = src.relative_to(src_root)
                dst = dst_root / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                key = f"{category}/{rel.as_posix()}"
                if dst.exists():
                    total_skipped_existing += 1
                else:
                    shutil.copyfile(src, dst)
                    total_copied += 1
                    cat_count += 1
                # Manifest entry — preserve prior status if it was
                # already marked improved/replaced
                prior = existing.get(key, {})
                manifest[key] = {
                    "source": f"base/{category}/{rel.as_posix()}",
                    "category": category,
                    "context": context_from_path(category, rel),
                    "status": prior.get("status", "placeholder"),
                    "replaced_at": prior.get("replaced_at"),
                    "improved_with": prior.get("improved_with"),
                }
        print(f"  {category}: copied {cat_count} new files")

    # Final pass — scan EVERY file under assets/ (e.g. the earlier
    # planet extraction at assets/planets/) and ensure each has a
    # manifest entry. Treat unmanifested files as placeholders.
    for path in ASSETS.rglob("*"):
        if not path.is_file():
            continue
        if path.name.startswith("_"):
            continue   # skip the manifest itself and other _-prefixed metadata
        rel = path.relative_to(ASSETS)
        key = rel.as_posix()
        if key in manifest:
            continue
        # Inferred category = first path part
        category = rel.parts[0] if len(rel.parts) > 0 else "misc"
        # Context = second path part if present, else "misc"
        context = rel.parts[1] if len(rel.parts) > 1 else "misc"
        # Try to infer the UQM source path. Most assets came from
        # base/<category>/<relative>; planets follow that pattern too.
        prior = existing.get(key, {})
        manifest[key] = {
            "source": f"base/{rel.as_posix()}",
            "category": category,
            "context": context if context != path.name else "misc",
            "status": prior.get("status", "placeholder"),
            "replaced_at": prior.get("replaced_at"),
            "improved_with": prior.get("improved_with"),
        }

    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )
    placeholders = sum(1 for v in manifest.values() if v["status"] == "placeholder")
    print(f"\nTotal: {total_copied} new + {total_skipped_existing} already-present "
          f"= {len(manifest)} tracked files")
    print(f"Placeholders awaiting improvement: {placeholders}")
    # Per-category breakdown
    by_cat: dict[str, int] = {}
    for v in manifest.values():
        if v["status"] == "placeholder":
            by_cat[v["category"]] = by_cat.get(v["category"], 0) + 1
    print("By category:")
    for cat, n in sorted(by_cat.items(), key=lambda kv: -kv[1]):
        print(f"  {cat:12s} {n}")
    print(f"\nManifest: {MANIFEST_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
