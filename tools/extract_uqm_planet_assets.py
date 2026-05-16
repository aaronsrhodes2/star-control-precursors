"""Copy the UQM planet sprite PNGs into our assets directory and build a
mapping from each of our 59 canonical planet-type enum names to its
asset filename.

Reads:
    references/uqm-source/sc2/content/uqm.rmp
        for the `planet.<short_name>.large` declarations
    references/uqm-source/sc2/content/base/planets/<file>.png
        the actual planet sprites

Writes:
    assets/planets/*.png
        the three sprite sizes (big/med/sml frame 000) per planet type
    src/scz/content/universe/uqm_planet_sprites.json
        mapping {enum_name: {"big": "...png", "med": "...png", "sml": "...png"}}

The UQM planet-type enum names from plandata.h (OOLITE_WORLD, ...,
YEL_GAS_GIANT) need to be matched against the lowercase short names in
the .rmp file (oolite, ..., yelgas). Most map directly; a few don't,
and need a manual alias table.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
RMP = ROOT / "references" / "uqm-source" / "sc2" / "content" / "uqm.rmp"
SRC_PLANETS = (
    ROOT / "references" / "uqm-source" / "sc2" / "content" / "base" / "planets"
)
PLANET_TYPES_JSON = ROOT / "src" / "scz" / "content" / "universe" / "uqm_planet_types.json"
ASSETS_DIR = ROOT / "assets" / "planets"
SPRITES_JSON = ROOT / "src" / "scz" / "content" / "universe" / "uqm_planet_sprites.json"


# Map enum name (from plandata.h) -> UQM short name (used in uqm.rmp).
# Built by uppercasing the short name and adding _WORLD or _GAS_GIANT.
# A few don't follow the rule and need explicit aliases.
ENUM_TO_SHORT_OVERRIDES = {
    "QUASI_DEGENERATE_WORLD": "quasidegenerate",
    "SUPER_DENSE_WORLD":      "superdense",
    "BLU_GAS_GIANT":          "bluegas",
    "CYA_GAS_GIANT":          "cyangas",
    "GRN_GAS_GIANT":          "greengas",
    "GRY_GAS_GIANT":          "greygas",
    "ORA_GAS_GIANT":          "orangegas",
    "PUR_GAS_GIANT":          "purplegas",
    "RED_GAS_GIANT":          "redgas",
    "VIO_GAS_GIANT":          "violetgas",
    "YEL_GAS_GIANT":          "yellowgas",
}


def enum_to_short(enum_name: str) -> str:
    """OOLITE_WORLD -> 'oolite', etc."""
    if enum_name in ENUM_TO_SHORT_OVERRIDES:
        return ENUM_TO_SHORT_OVERRIDES[enum_name]
    # Default: strip _WORLD or _GAS_GIANT suffix, lowercase
    if enum_name.endswith("_WORLD"):
        return enum_name[:-len("_WORLD")].lower()
    if enum_name.endswith("_GAS_GIANT"):
        return enum_name[:-len("_GAS_GIANT")].lower() + "gas"
    return enum_name.lower()


def parse_rmp_planet_entries() -> dict[str, dict[str, str]]:
    """Parse uqm.rmp for `planet.<short>.<size> = GFXRES:base/planets/<file>.ani`
    lines. Return {short: {"big": "<file.ani>", "med": ..., "sml": ...}}.
    """
    text = RMP.read_text(encoding="utf-8")
    entries: dict[str, dict[str, str]] = {}
    pattern = re.compile(
        r"planet\.(\w+)\.(large|medium|small)\s*=\s*GFXRES:base/planets/([\w\-]+)\.ani"
    )
    size_alias = {"large": "big", "medium": "med", "small": "sml"}
    for m in pattern.finditer(text):
        short, size, fname = m.group(1), m.group(2), m.group(3)
        entries.setdefault(short, {})[size_alias[size]] = fname
    return entries


def main() -> int:
    if not RMP.exists():
        print(f"missing UQM .rmp at {RMP}", file=sys.stderr)
        return 1
    if not PLANET_TYPES_JSON.exists():
        print(
            f"missing {PLANET_TYPES_JSON} — run extract_uqm_planet_data.py first",
            file=sys.stderr,
        )
        return 1

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    rmp_entries = parse_rmp_planet_entries()
    print(f"parsed {len(rmp_entries)} planet entries from uqm.rmp")

    types = json.loads(PLANET_TYPES_JSON.read_text(encoding="utf-8"))
    sprite_map: dict[str, dict[str, str]] = {}
    missing: list[str] = []
    copied = 0
    for tp in types:
        enum_name = tp["name"]
        short = enum_to_short(enum_name)
        entry = rmp_entries.get(short)
        if entry is None:
            missing.append(f"{enum_name} (looked up '{short}')")
            continue
        out_for_type: dict[str, str] = {}
        for size, ani_basename in entry.items():
            # The .ani uses 000-frame as the static representative — copy
            # <ani_basename>-000.png for each size.
            src = SRC_PLANETS / f"{ani_basename}-000.png"
            if not src.exists():
                print(f"  WARN: missing {src.name} for {enum_name}", file=sys.stderr)
                continue
            dst_name = f"{ani_basename}-000.png"
            dst = ASSETS_DIR / dst_name
            if not dst.exists():
                shutil.copyfile(src, dst)
                copied += 1
            out_for_type[size] = dst_name
        sprite_map[enum_name] = out_for_type

    SPRITES_JSON.write_text(json.dumps(sprite_map, indent=2), encoding="utf-8")
    print(f"copied {copied} PNG files -> assets/planets/")
    print(f"wrote {len(sprite_map)} type->sprite mappings -> {SPRITES_JSON.relative_to(ROOT)}")
    if missing:
        print(f"WARN: {len(missing)} types had no rmp entry:", file=sys.stderr)
        for m in missing:
            print(f"    {m}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
