"""Wire all status=keep manifest entries into their canonical live paths.

Aaron's directive (2026-05-19): "consider the non-approved as rejected,
and wire in all the new images in the code."

Logic per manifest entry with status=keep:

1. Determine the BASE name (strip trailing _vN, _vN_anything).
   `furling_cleanser_v2` -> base = `furling_cleanser`
   `species_commander_halia_action_v2` -> base = `species_commander_halia_action`

2. Group kept entries by base. For each group, pick the WINNER:
   - If the versionless file (no _vN suffix) is kept, it stays the canonical
     and wins — no copy needed.
   - Otherwise pick the highest-versioned kept variant and COPY its PNG
     onto the versionless filename so the game code (which references
     the versionless path) picks it up.

3. Trigger downstream extraction/animation when needed:
   - tier1_ship_sprites + tier1_ships: re-run extract_sprite_alpha.py
     using the kept variant.
   - tier1_weapons: re-run extract_projectile_alpha.py using the kept
     variant per ship_id.
   - tier1_asteroids: re-run extract_asteroid_alpha.py (handles all
     variants in one pass — picks v1 by default).
   - tier1_planets: copy kept variant to canonical, then re-run
     animate_planet.py --only <planet_id> to refresh sphere frames.
   - tier1_stars: copy kept variant to assets/stars/star_<color>.png.
     Special-case combat_starfield -> assets/combat/starfield.png.

Run with:
    python tools/wire_approved_images.py

Use --dry-run to see what would change without touching anything.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import subprocess
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "assets" / "generated_drafts" / "firefly" / "_manifest.json"

# Pattern for a trailing _vN or _vN_<word> suffix at the end of a stem
VERSION_RE = re.compile(r"_v\d+(?:_[a-z0-9]+)?$")


def strip_version(stem: str) -> str:
    """avatar_commander_halia_v2 → avatar_commander_halia"""
    return VERSION_RE.sub("", stem)


def version_score(stem: str) -> int:
    """Return the numeric version (higher = newer). Versionless = 0."""
    m = re.search(r"_v(\d+)", stem)
    return int(m.group(1)) if m else 0


def find_winners(manifest: dict) -> dict[str, dict]:
    """Return { tier/base: {key, image_path, version} } for each unique
    base name where at least one variant has status=keep. Picks highest
    versionless-or-newest kept variant as the winner.
    """
    groups: dict[str, list[tuple[int, str, str]]] = defaultdict(list)
    for key, entry in manifest.items():
        if entry.get("status") != "keep":
            continue
        if "/" not in key:
            continue
        tier, stem = key.split("/", 1)
        base_stem = strip_version(stem)
        version = version_score(stem)
        groups[f"{tier}/{base_stem}"].append((version, key, entry.get("image_path", "")))

    winners: dict[str, dict] = {}
    for base, items in groups.items():
        # If a versionless entry exists, it wins; else newest version wins.
        versionless = [it for it in items if it[0] == 0]
        if versionless:
            chosen = versionless[0]
        else:
            chosen = max(items, key=lambda it: it[0])
        winners[base] = {"key": chosen[1], "image_path": chosen[2], "version": chosen[0]}
    return winners


def canonical_path_for(base: str) -> pathlib.Path:
    """Given 'tier1_X/foo_bar' return assets/generated_drafts/firefly/tier1_X/foo_bar.png"""
    return ROOT / "assets" / "generated_drafts" / "firefly" / f"{base}.png"


# Tiers where the GAME loads the variant directly (via glob or via
# variant arg to extraction tools) — promoting to a versionless name
# would create a redundant duplicate. Skip the copy step for these.
TIERS_NO_PROMOTE = {
    "tier1_asteroids",      # glob asteroid_*.png; variants ARE the data
    "tier1_ship_sprites",   # extract_sprite_alpha takes --variant; src stays versioned
    "tier1_weapons",        # extract_projectile_alpha takes --variant
}


def copy_to_canonical(winner: dict, base: str, dry_run: bool) -> tuple[bool, str]:
    """Copy the winner's PNG to the canonical (versionless) location.
    Returns (changed, msg).
    """
    src = ROOT / winner["image_path"]
    dst = canonical_path_for(base)
    if not src.exists():
        return False, f"SKIP missing source {src}"
    if src == dst:
        return False, "OK already canonical"
    if dst.exists() and dst.read_bytes() == src.read_bytes():
        return False, "OK matching bytes"
    if dry_run:
        return True, f"WOULD copy {src.name} -> {dst.name}"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    return True, f"COPIED {src.name} -> {dst.name}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would change without touching anything.")
    parser.add_argument("--skip-extraction", action="store_true",
                        help="Skip the heavy alpha-extraction + animate-planet steps.")
    args = parser.parse_args()

    if not MANIFEST.exists():
        print(f"ERROR: manifest not found at {MANIFEST}", file=sys.stderr)
        return 1
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    winners = find_winners(manifest)
    print(f"Found {len(winners)} approved bases across {len(manifest)} manifest entries.")
    print()

    # Step 1: copy each winner to its canonical filename
    promoted = 0
    skipped = 0
    ship_sprite_winners: dict[str, str] = {}      # ship_id -> source variant (v1/v2/...)
    projectile_winners: dict[str, str] = {}       # ship_id -> source variant
    planet_winners: set[str] = set()              # planet_id needs re-animation
    star_winners: dict[str, str] = {}             # color -> source stem
    needs_asteroid_extract = False

    for base, winner in sorted(winners.items()):
        tier, stem = base.split("/", 1)
        if tier in TIERS_NO_PROMOTE:
            # Game loads variants directly — no canonical promote needed.
            changed, msg = False, "(no promote: variant-loaded)"
        else:
            changed, msg = copy_to_canonical(winner, base, args.dry_run)
        marker = "*" if changed else " "
        print(f"  {marker} {tier:24s} {stem:50s} {msg}")
        if changed:
            promoted += 1
        else:
            skipped += 1

        # Collect extraction triggers
        if tier == "tier1_ship_sprites" and stem.startswith("sprite_"):
            # sprite_X_v3 → ship_id=X, variant=v3
            ship_id = stem.removeprefix("sprite_")
            ship_id_base = strip_version(ship_id)
            # Derive variant from the WINNING key
            win_stem = winner["key"].split("/", 1)[1].removeprefix("sprite_")
            m = re.search(r"_v(\d+)", win_stem)
            variant = f"v{m.group(1)}" if m else "v1"
            ship_sprite_winners[ship_id_base] = variant
        elif tier == "tier1_weapons" and stem.startswith("projectile_"):
            ship_id = stem.removeprefix("projectile_")
            ship_id_base = strip_version(ship_id)
            win_stem = winner["key"].split("/", 1)[1].removeprefix("projectile_")
            m = re.search(r"_v(\d+)", win_stem)
            variant = f"v{m.group(1)}" if m else "v1"
            projectile_winners[ship_id_base] = variant
        elif tier == "tier1_planets" and stem.startswith("planet_"):
            planet_id = stem.removeprefix("planet_")
            planet_winners.add(planet_id)
        elif tier == "tier1_asteroids":
            needs_asteroid_extract = True
        elif tier == "tier1_stars":
            if stem.startswith("star_"):
                color = strip_version(stem).removeprefix("star_")
                star_winners[color] = winner["key"]
            elif stem.startswith("combat_starfield"):
                star_winners["__starfield"] = winner["key"]

    print()
    print(f"Promoted {promoted} files. Skipped {skipped} (already canonical).")
    print()

    # Step 2: copy stars + starfield to live paths
    if star_winners:
        print("--- Wiring stars ---")
        stars_dir = ROOT / "assets" / "stars"
        combat_dir = ROOT / "assets" / "combat"
        for color, winner_key in star_winners.items():
            src = canonical_path_for(strip_version(winner_key))
            if color == "__starfield":
                dst = combat_dir / "starfield.png"
            else:
                dst = stars_dir / f"star_{color}.png"
            if not src.exists():
                print(f"  SKIP {color}: {src} missing")
                continue
            if args.dry_run:
                print(f"  WOULD copy {src.name} -> {dst}")
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)
                print(f"  OK   {color:10s} -> {dst.relative_to(ROOT)}")

    if args.skip_extraction:
        print("\n(--skip-extraction set; not re-running extraction tools.)")
        return 0

    # Step 3: alpha-extract ship sprites + projectiles per kept variants
    sd_python = ROOT / "sd-server" / ".venv" / "Scripts" / "python.exe"
    if not sd_python.exists():
        sd_python = pathlib.Path(sys.executable)

    if ship_sprite_winners:
        print("\n--- Extracting ship sprites ---")
        # Group by variant — extract_sprite_alpha.py takes a single variant
        # arg, so we run once per (variant, ship_id) pair via --only.
        for ship_id, variant in sorted(ship_sprite_winners.items()):
            cmd = [
                str(sd_python), "tools/extract_sprite_alpha.py",
                "--variant", variant, "--only", ship_id,
            ]
            if args.dry_run:
                print(f"  WOULD run {' '.join(cmd)}")
                continue
            result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
            tail = (result.stdout or "").strip().split("\n")[-1]
            print(f"  {ship_id:25s} ({variant}) {tail}")

    if projectile_winners:
        print("\n--- Extracting projectile sprites ---")
        for ship_id, variant in sorted(projectile_winners.items()):
            cmd = [
                str(sd_python), "tools/extract_projectile_alpha.py",
                "--variant", variant,
            ]
            if args.dry_run:
                print(f"  WOULD run {' '.join(cmd)} (filtered to {ship_id})")
                continue
            # extract_projectile_alpha.py doesn't have --only; runs all ships
            # that have the requested variant. We'll do one pass per unique
            # variant value to cover everything.
        # Run once per unique variant (deduped)
        for variant in sorted(set(projectile_winners.values())):
            cmd = [str(sd_python), "tools/extract_projectile_alpha.py", "--variant", variant]
            if args.dry_run:
                print(f"  WOULD run {' '.join(cmd)}")
                continue
            result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
            print(f"  ran projectile extract --variant {variant}")

    if needs_asteroid_extract and not args.dry_run:
        print("\n--- Extracting asteroids ---")
        cmd = [str(sd_python), "tools/extract_asteroid_alpha.py"]
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        print(f"  ran asteroid extract")

    if planet_winners:
        print("\n--- Re-animating planets ---")
        py = pathlib.Path(sys.executable)
        # animate_planet.py reads from tier1_planets/planet_<id>.png (the
        # canonical we just promoted above), so simply re-run for the
        # planets whose source changed.
        for planet_id in sorted(planet_winners):
            cmd = [str(py), "tools/animate_planet.py", "--only", planet_id]
            if args.dry_run:
                print(f"  WOULD run {' '.join(cmd)}")
                continue
            result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
            tail = (result.stdout or "").strip().split("\n")[-1]
            print(f"  {planet_id:30s} {tail}")

    print("\nDone. Run `python -m scz --test walk_super_melee` to smoke-test.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
