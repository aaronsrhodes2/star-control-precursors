"""
Extract the SC2 universe data from the cloned UQM source and derive a
precursor-era (250,000 years before SC2) version of the galaxy.

Inputs (relative to project root):
    references/uqm-source/sc2/src/uqm/plandata.c       (star coordinates / types)
    references/uqm-source/sc2/src/uqm/gendef.h         (DEFINED enum -> lore index)
    references/uqm-source/sc2/content/base/gamestrings.txt (constellation + Greek letter names)

Outputs:
    references/sc2-universe/stars.json       (canonical SC2-era star data)
    src/scz/content/universe/stars.json      (precursor-era derived star data)
    src/scz/content/universe/derivation.md   (notes on what transforms were applied)

The precursor-era derivation applies (in order):
    1. Galactic rotation: rotate around (5000, 5000) by 0.4 degrees retrograde
       (Sun's galactic year ~250 Myr, so 250 kyr is ~0.36 deg of rotation).
    2. Stellar proper motion: deterministic per-star Gaussian shift,
       scaled by approximate UQM unit -> light-year conversion.
    3. Star-type rejuvenation: a small fraction of SC2 SUPER_GIANT stars
       were less evolved 250 kyr ago. We probabilistically demote some
       to GIANT.
    4. Lore stripping: SC2 lore artifacts that don't exist yet
       (e.g. SAMATRA, RAINBOW, URQUAN_WRECK, ANDROSYNTH ruins) are
       cleared from the Index field. Pre-existing race homeworlds
       are kept but tagged "proto_" if the race is pre-sentient in
       our era.
"""

from __future__ import annotations

import json
import math
import random
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# UQM constants
# ---------------------------------------------------------------------------

# Star types in MAKE_STAR(type, color, owner)
STAR_TYPES = ["DWARF_STAR", "GIANT_STAR", "SUPER_GIANT_STAR"]

# Star colors. UQM names — BLUE is hottest, RED is coolest.
# GREEN is artistic license (real stars don't appear green).
STAR_COLORS = [
    "BLUE_BODY", "GREEN_BODY", "ORANGE_BODY",
    "RED_BODY", "WHITE_BODY", "YELLOW_BODY",
]

# DEFINED enum from gendef.h. SOL_DEFINED = 1.
DEFINED_NAMES = [
    None,  # 0 = no lore index
    "SOL", "SHOFIXTI", "MAIDENS", "START_COLONY", "SPATHI", "ZOQFOT",
    "MELNORME0", "MELNORME1", "MELNORME2", "MELNORME3", "MELNORME4",
    "MELNORME5", "MELNORME6", "MELNORME7", "MELNORME8",
    "TALKING_PET", "CHMMR", "SYREEN", "BURVIXESE", "SLYLANDRO", "DRUUGE",
    "BOMB", "AQUA_HELIX", "SUN_DEVICE", "TAALO_PROTECTOR", "SHIP_VAULT",
    "URQUAN_WRECK", "VUX_BEAST", "SAMATRA", "ZOQ_SCOUT", "MYCON",
    "EGG_CASE0", "EGG_CASE1", "EGG_CASE2",
    "PKUNK", "UTWIG", "SUPOX", "YEHAT", "VUX", "ORZ", "THRADD",
    "RAINBOW", "ILWRATH", "ANDROSYNTH", "MYCON_TRAP",
]
# UMGAH_DEFINED is an alias for TALKING_PET_DEFINED.
DEFINED_NAMES_TO_ALIAS = {"TALKING_PET": "UMGAH_OR_TALKING_PET"}

# Greek letter prefix. Prefix=0 means no prefix in the C source.
# Prefix=1 -> Alpha, Prefix=2 -> Beta, etc. (1-indexed in plandata.c).
GREEK_LETTERS = [
    "Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta",
    "Theta", "Iota", "Kappa", "Lambda", "Mu", "Nu", "Xi",
]

# UQM universe coordinate range. The C macros MAX_X_UNIVERSE / MAX_Y_UNIVERSE
# correspond to 9999. We treat (0,0) as bottom-left.
MAX_COORD = 10000
GALACTIC_CENTER = (5000, 5000)  # arbitrary, just a rotation pivot

# Approximate physical scale: the SC2 map covers ~1000 ly across, so
# 1 UQM unit ~ 0.1 ly. Used to apply realistic proper motion.
UNIT_TO_LY = 0.1
KMS_TO_LY_PER_KYR = 1.0227e-3  # 1 km/s ≈ 0.001 ly per million years
TIMESPAN_KYR = 250.0           # 250,000 years


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

STAR_LINE_RE = re.compile(
    r"\{\{\s*(-?\d+),\s*(-?\d+)\s*\},\s*"
    r"MAKE_STAR\s*\(\s*(\w+),\s*(\w+),\s*-1\s*\)\s*,\s*"
    r"(\w+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\}"
)


def parse_plandata(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace")
    stars: list[dict] = []
    for m in STAR_LINE_RE.finditer(text):
        x = int(m.group(1))
        y = int(m.group(2))
        # Skip the QuasiSpace vortex sentinel sweeping past the universe
        # bounds, and skip the trailing terminator at (MAX*2, MAX*2).
        if x > MAX_COORD or y > MAX_COORD:
            continue
        star_type = m.group(3)
        color = m.group(4)
        defined = m.group(5)
        prefix = int(m.group(6))
        postfix = int(m.group(7))

        defined_int: int
        if defined.isdigit():
            defined_int = int(defined)
        else:
            try:
                defined_int = DEFINED_NAMES.index(defined.replace("_DEFINED", ""))
            except ValueError:
                # UMGAH_DEFINED -> TALKING_PET_DEFINED alias
                if defined == "UMGAH_DEFINED":
                    defined_int = DEFINED_NAMES.index("TALKING_PET")
                else:
                    defined_int = 0
        stars.append({
            "x": x, "y": y,
            "type": star_type,
            "color": color,
            "defined_index": defined_int,
            "defined_name": DEFINED_NAMES[defined_int] if 0 < defined_int < len(DEFINED_NAMES) else None,
            "prefix_index": prefix,   # 0 = no Greek letter, 1 = Alpha, ...
            "postfix_index": postfix, # 0 = Vega, 1 = Antliae, ...
        })
    return stars


def parse_constellation_names(path: Path) -> list[str]:
    """Read the postfix name table from gamestrings.txt.

    The table starts at STAR_STRING_BASE (the first `#(Vega)` line) and
    runs until STAR_NUMBER_BASE (the `#(Alpha)` line).
    Each entry is four lines: `#(name)`, `name`, blank, blank.
    """
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    names: list[str] = []
    i = 0
    in_table = False
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#(") and "STAR_STRING_BASE" in line:
            in_table = True
            # The name is the value of this line's parenthesized text.
            names.append(line[2:line.index(")")])
            i += 4  # skip name line + 2 blanks
            continue
        if in_table:
            if line.startswith("#(") and "STAR_NUMBER_BASE" in line:
                break
            if line.startswith("#(") and ")" in line:
                names.append(line[2:line.index(")")])
                i += 4
                continue
        i += 1
    return names


def cluster_name(prefix_index: int, postfix_index: int, names: list[str]) -> str:
    postfix = names[postfix_index] if 0 <= postfix_index < len(names) else f"<unknown:{postfix_index}>"
    if prefix_index == 0:
        return postfix
    if 1 <= prefix_index <= len(GREEK_LETTERS):
        return f"{GREEK_LETTERS[prefix_index - 1]} {postfix}"
    return f"<bad-prefix:{prefix_index}> {postfix}"


# ---------------------------------------------------------------------------
# Precursor-era derivation
# ---------------------------------------------------------------------------

# Lore artifacts that don't exist yet in the Precursor era (250 kyr earlier).
PRECURSOR_ERA_REMOVED = {
    "SAMATRA",          # Built later/being built — not yet placed
    "URQUAN_WRECK",     # The Dnyarri era hasn't happened yet
    "ANDROSYNTH",       # Human synthetic offshoot — doesn't exist yet
    "SHIP_VAULT",       # Syreen ship vault is post-Mycon catastrophe
    "VUX_BEAST",        # VUX civilization isn't established
    "EGG_CASE0", "EGG_CASE1", "EGG_CASE2",   # Mycon Deep Children
    "MYCON_TRAP",       # Pursuit-of-Mycon plot doesn't apply
    "TAALO_PROTECTOR",  # Taalo had perished by SC2; in our era, still alive?
    "AQUA_HELIX",       # Chenjesu/Mmrnmhrm artifacts not yet placed
    "SUN_DEVICE",
    "BOMB",             # Utwig Bomb — Utwig civ pre-dates this
    "BURVIXESE",        # Lost civilization in SC2; in our era, alive (renamed BURVIXESE_LIVING)
    "MAIDENS",          # Shofixti Maidens vault is post-Ur-Quan war
    "START_COLONY",     # The Earth Starbase isn't built yet
    "ZOQ_SCOUT",        # Zoq-Fot-Pik scout ship encounter
}

# Lore artifacts that EXIST but in different form / get renamed.
PRECURSOR_ERA_RENAME = {
    "RAINBOW": "RAINBOW_BEING_SEEDED",   # central plot — they're being placed during gameplay
    "SOL": "SOL_PROTO",                  # no humans yet
    "SHOFIXTI": "SHOFIXTI_PROTO",        # Shofixti pre-sentient
    "YEHAT": "YEHAT_PROTO",              # Yehat pre-sentient
    "VUX": "VUX_PROTO",                  # VUX "in their infancy" per worldbuilding doc
    "PKUNK": "PKUNK_PROTO",
    "THRADD": "THRADD_PROTO",
    "UTWIG": "UTWIG_PROTO",
    "SUPOX": "SUPOX_PROTO",
    "DRUUGE": "DRUUGE_PROTO",
    "ILWRATH": "ILWRATH_PROTO",
    "SPATHI": "SPATHI_PROTO",
    "SYREEN": "SYREEN_PROTO",
    "CHMMR": "CHENJESU_PROTO",           # Chmmr is post-merging; their precursor is Chenjesu
    "ORZ": "ORZ_RIFT",                   # Orz are dimensional incursions, not residents
    "MYCON": "MYCON_BIOT_HIVE",          # Active Precursor terraformers
    "SLYLANDRO": "SLYLANDRO",            # Already sentient observers per lore
    "TALKING_PET": "DNYARRI_PRIMITIVE",  # Dnyarri ancestors
    "ZOQFOT": "ZOQFOT_PROTO",
    "MELNORME0": "MELNORME_PROTO", "MELNORME1": "MELNORME_PROTO",
    "MELNORME2": "MELNORME_PROTO", "MELNORME3": "MELNORME_PROTO",
    "MELNORME4": "MELNORME_PROTO", "MELNORME5": "MELNORME_PROTO",
    "MELNORME6": "MELNORME_PROTO", "MELNORME7": "MELNORME_PROTO",
    "MELNORME8": "MELNORME_PROTO",
}


def rotate_about(x: float, y: float, cx: float, cy: float, theta_rad: float) -> tuple[float, float]:
    dx, dy = x - cx, y - cy
    cos_t = math.cos(theta_rad)
    sin_t = math.sin(theta_rad)
    return cx + dx * cos_t - dy * sin_t, cy + dx * sin_t + dy * cos_t


def precursor_era_star(star: dict, rng: random.Random) -> dict | None:
    """Transform one SC2-era star into its 250kya version.

    Returns None if the star should not exist (rare for transformations
    that 'erase' a star from the precursor era — currently never happens;
    we always keep the star and merely clear its lore tag).
    """
    new = dict(star)

    # 1. Galactic rotation: retrograde 0.36 deg ~ Sun's orbital motion in 250 kyr.
    # This is so small at the UQM map scale (~10 pixels of shift across the
    # 10000-wide map) that we make it slightly visible by using 0.5 deg.
    theta = math.radians(-0.5)
    rx, ry = rotate_about(new["x"], new["y"], *GALACTIC_CENTER, theta)
    new["x"] = round(rx)
    new["y"] = round(ry)

    # 2. Stellar proper motion. Different star classes have different
    # typical space velocities; we just approximate with a normal distribution.
    # Hot blue stars: young, low dispersion (~10 km/s).
    # Yellow/orange: thick disk, ~30 km/s.
    # Red dwarfs: oldest, highest dispersion (~50 km/s).
    color_sigma_kms = {
        "BLUE_BODY": 8.0,
        "WHITE_BODY": 15.0,
        "GREEN_BODY": 20.0,   # treat as a peculiar/lore color
        "YELLOW_BODY": 25.0,
        "ORANGE_BODY": 35.0,
        "RED_BODY": 50.0,
    }
    sigma_kms = color_sigma_kms.get(new["color"], 30.0)
    # ly drifted in 250 kyr = sigma_kms * KMS_TO_LY_PER_KYR * 250
    drift_ly = sigma_kms * KMS_TO_LY_PER_KYR * TIMESPAN_KYR
    drift_units = drift_ly / UNIT_TO_LY
    # Apply 2D Gaussian shift deterministically per star.
    dx = rng.gauss(0, drift_units)
    dy = rng.gauss(0, drift_units)
    new["x"] = int(round(new["x"] + dx))
    new["y"] = int(round(new["y"] + dy))
    # Clamp to map.
    new["x"] = max(0, min(MAX_COORD - 1, new["x"]))
    new["y"] = max(0, min(MAX_COORD - 1, new["y"]))

    # 3. Star-type rejuvenation: about 10% of SUPER_GIANTs were merely
    # GIANTs 250 kyr ago. (Very rough — SC2 has only a handful of supergiants.)
    if new["type"] == "SUPER_GIANT_STAR" and rng.random() < 0.10:
        new["type"] = "GIANT_STAR"
        new["primordial_note"] = "Was a giant 250kya; not yet a supergiant."

    # 4. Lore stripping / rename.
    name = new.get("defined_name")
    if name in PRECURSOR_ERA_REMOVED:
        new["defined_index"] = 0
        new["defined_name"] = None
        new["precursor_note"] = f"In SC2 this is {name}; doesn't yet exist in our era."
    elif name in PRECURSOR_ERA_RENAME:
        new["defined_name"] = PRECURSOR_ERA_RENAME[name]
        # We don't update defined_index — it stays as the SC2 reference,
        # but defined_name is what the game UI should display.

    # 5. Primordial tagging — about 3% of dwarf systems are still forming.
    if new["type"] == "DWARF_STAR" and rng.random() < 0.03:
        new["primordial"] = True

    return new


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    root = Path(__file__).resolve().parent.parent
    plandata = root / "references" / "uqm-source" / "sc2" / "src" / "uqm" / "plandata.c"
    gamestrings = root / "references" / "uqm-source" / "sc2" / "content" / "base" / "gamestrings.txt"

    if not plandata.exists():
        print(f"plandata.c not found at {plandata}", file=sys.stderr)
        return 1
    if not gamestrings.exists():
        print(f"gamestrings.txt not found at {gamestrings}", file=sys.stderr)
        return 1

    stars = parse_plandata(plandata)
    names = parse_constellation_names(gamestrings)

    # Attach cluster name
    for s in stars:
        s["cluster_name"] = cluster_name(s["prefix_index"], s["postfix_index"], names)

    # Drop QuasiSpace vortices (recognized by postfix index pointing past the
    # actual table) and the sentinel. We've already filtered by coord above.
    stars = [s for s in stars if s["postfix_index"] < len(names)]

    # ---- Save canonical SC2 universe ----
    sc2_out = root / "references" / "sc2-universe"
    sc2_out.mkdir(parents=True, exist_ok=True)
    sc2_payload = {
        "metadata": {
            "source": "uqm-source/sc2/src/uqm/plandata.c",
            "star_count": len(stars),
            "constellation_count": len(names),
            "coord_range": [0, MAX_COORD],
            "era_kyr_before_present": 0,
            "note": "Verbatim SC2 universe — canonical reference, do not edit.",
        },
        "star_types": STAR_TYPES,
        "star_colors": STAR_COLORS,
        "greek_letters": GREEK_LETTERS,
        "defined_names": DEFINED_NAMES,
        "constellation_names": names,
        "stars": stars,
    }
    (sc2_out / "stars.json").write_text(json.dumps(sc2_payload, indent=2))
    print(f"Wrote canonical SC2 universe to {sc2_out / 'stars.json'} ({len(stars)} stars)")

    # ---- Derive and save precursor-era universe ----
    # Seed by (x,y) so the derivation is reproducible.
    precursor_stars: list[dict] = []
    for s in stars:
        rng = random.Random(s["x"] * (MAX_COORD + 1) + s["y"])
        new = precursor_era_star(s, rng)
        if new is not None:
            # Recompute cluster name after position changes (name doesn't move with the star,
            # but constellations are just naming conventions, so keep the SC2 label).
            new["cluster_name"] = s["cluster_name"]
            precursor_stars.append(new)

    sczu = root / "src" / "scz" / "content" / "universe"
    sczu.mkdir(parents=True, exist_ok=True)
    precursor_payload = {
        "metadata": {
            "derived_from": "references/sc2-universe/stars.json",
            "star_count": len(precursor_stars),
            "era_kyr_before_present": 250,
            "transforms": [
                "Galactic rotation: -0.5 deg around (5000, 5000)",
                "Stellar proper motion: per-color Gaussian drift over 250 kyr",
                "Star type rejuvenation: 10% of supergiants demoted to giants",
                "Lore stripping: artifacts that don't yet exist removed/renamed",
                "Primordial tag: 3% of dwarfs marked as still-forming",
            ],
        },
        "stars": precursor_stars,
    }
    (sczu / "stars.json").write_text(json.dumps(precursor_payload, indent=2))
    print(f"Wrote precursor-era universe to {sczu / 'stars.json'} ({len(precursor_stars)} stars)")

    # Quick summary stats
    from collections import Counter
    type_counts = Counter(s["type"] for s in precursor_stars)
    color_counts = Counter(s["color"] for s in precursor_stars)
    lore_count = sum(1 for s in precursor_stars if s.get("defined_name"))
    primordial_count = sum(1 for s in precursor_stars if s.get("primordial"))
    print(f"  Star types:    {dict(type_counts)}")
    print(f"  Star colors:   {dict(color_counts)}")
    print(f"  Lore-tagged:   {lore_count}")
    print(f"  Primordial:    {primordial_count}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
