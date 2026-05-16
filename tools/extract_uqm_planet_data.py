"""Extract UQM planet-type catalog and per-star-color distributions
from the cloned UQM source. Output is consumed by `scz.system.uqm_procgen`
to mirror SC2's exact procedural generation for unnamed stars.

Inputs:
    references/uqm-source/sc2/src/uqm/plandata.h     (planet type enum)
    references/uqm-source/sc2/src/uqm/plandata.c     (planet_array PlanetFrame definitions)
    references/uqm-source/sc2/src/uqm/planets/orbits.c (six XxxDistribution() tables)

Outputs:
    src/scz/content/universe/uqm_planet_types.json   (per-type Type/Tectonics/Atmo+Density bytes)
    src/scz/content/universe/uqm_star_distributions.json  (per-star-color: which planet types appear)

The JSON shape is deliberately flat; the runtime procgen does the bit-masking.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
UQM = ROOT / "references" / "uqm-source" / "sc2" / "src" / "uqm"
PLANDATA_H = UQM / "planets" / "plandata.h"
PLANDATA_C = UQM / "plandata.c"
ORBITS_C = UQM / "planets" / "orbits.c"
OUT_DIR = ROOT / "src" / "scz" / "content" / "universe"


# Constants from plandata.h / orbits.c (transcribed)
PLANET_RARITIES = {
    "PLANET_NEVER":   0,
    "PLANET_RARE":   15,
    "PLANET_FEW":    63,
    "PLANET_COMMON": 127,
    "PLANET_ALWAYS": 255,
}

# Tectonics constants (from plandata.h — search confirms these numbers)
TECTONICS = {
    "NO_TECTONICS":     0,
    "LOW_TECTONICS":   40,
    "MED_TECTONICS":   80,
    "HIGH_TECTONICS": 140,
    "SUPER_TECTONICS": 200,
}

# Density (bits 0-3 of AtmoAndDensity)
DENSITY = {
    "GAS_DENSITY":    0,
    "LIGHT_DENSITY":  1,
    "LOW_DENSITY":    2,
    "NORMAL_DENSITY": 3,
    "HIGH_DENSITY":   4,
    "SUPER_DENSITY":  5,
}

# Atmosphere (bits 4-7 of AtmoAndDensity)
ATMOSPHERE = {
    "NOTHING":     0,
    "LIGHT":       1,
    "MEDIUM":      2,
    "HEAVY":       3,
    "SUPER_THICK": 4,
}

# Color body codes (HINIBBLE of Type byte)
COLOR_BODIES = {
    "BLUE_BODY":   0,
    "GREEN_BODY":  1,
    "ORANGE_BODY": 2,
    "RED_BODY":    3,
    "WHITE_BODY":  4,
    "GRAY_BODY":   4,   # alias of WHITE_BODY in plandata.h
    "YELLOW_BODY": 5,
    "CYAN_BODY":   6,
    "PURPLE_BODY": 7,
    "VIOLET_BODY": 8,
}

# Size + algo bits in low nibble of Type byte
SIZE_VALUES = {
    "SMALL_ROCKY_WORLD": 0,
    "LARGE_ROCKY_WORLD": 1,
    "GAS_GIANT":         2,
}
ALGO_VALUES = {
    "TOPO_ALGO":      0 << 2,
    "CRATERED_ALGO":  1 << 2,
    "GAS_GIANT_ALGO": 2 << 2,
}


# ---------------------------------------------------------------------------
# Parse plandata.h for the planet-type enum (gives us the canonical order)
# ---------------------------------------------------------------------------

def extract_planet_type_names() -> list[str]:
    """Read plandata.h and return the 59 planet-type names in enum order
    (OOLITE_WORLD .. YEL_GAS_GIANT). Filters out the FIRST_/LAST_/NUMBER_OF
    aliases and the WORLD_TYPE_SPECIAL block."""
    text = PLANDATA_H.read_text(encoding="utf-8")
    # The enum we want spans from FIRST_ROCKY_WORLD through LAST_GAS_GIANT;
    # find the enum block that contains OOLITE_WORLD (the first one) to
    # disambiguate from the size/algo enums earlier in the header.
    enum_matches = list(re.finditer(r"enum\s*\{(.*?)\};", text, re.DOTALL))
    body = None
    for m in enum_matches:
        if "OOLITE_WORLD" in m.group(1):
            body = m.group(1)
            break
    if body is None:
        raise RuntimeError("planet-type enum (containing OOLITE_WORLD) not found")
    # Take only lines that look like a bare identifier followed by , or =
    names: list[str] = []
    seen = set()
    for line in body.splitlines():
        line = re.sub(r"/\*.*?\*/", "", line)  # strip C comments
        line = line.strip().rstrip(",")
        if not line or line.startswith("//"):
            continue
        # Skip alias-only lines (FIRST_xxx = ..., LAST_xxx = ...)
        m = re.match(r"^([A-Z_][A-Z0-9_]*)\s*(?:=\s*.+)?$", line)
        if not m:
            continue
        name = m.group(1)
        # Skip aliases and the special-world block
        if (
            name.startswith("FIRST_")
            or name.startswith("LAST_")
            or name in ("NUMBER_OF_PLANET_TYPES", "WORLD_TYPE_SPECIAL",
                        "PLANET_SHIELDED", "HIERARCHY_STARBASE", "SA_MATRA")
        ):
            continue
        if name in seen:
            continue
        seen.add(name)
        names.append(name)
    if len(names) != 59:
        raise RuntimeError(
            f"expected 59 planet-type names, got {len(names)}: {names!r}"
        )
    return names


# ---------------------------------------------------------------------------
# Parse plandata.c for the PlanetFrame array
# ---------------------------------------------------------------------------

def extract_planet_frames(names: list[str]) -> list[dict]:
    """Walk plandata.c's planet_array[] and pull the 4 numeric fields per
    entry: Type byte, BaseTectonics constant, AtmoAndDensity byte, and the
    four map-gen knobs (num_faults, fault_depth, num_blemishes, base_elevation).
    Skip the resource references (XLAT / CMAP) — they're for rendering.
    """
    text = PLANDATA_C.read_text(encoding="utf-8")
    # Find the planet_array definition
    arr_match = re.search(
        r"const\s+PlanetFrame\s+planet_array\s*\[[^\]]*\]\s*=\s*\{(.*?)\n\}",
        text, re.DOTALL,
    )
    if not arr_match:
        raise RuntimeError("planet_array definition not found")
    body = arr_match.group(1)

    # Each entry is wrapped in { ... }, separated by commas at the top level.
    # The entries contain nested { ... } for UsefulElements. Walk via brace
    # depth tracking.
    entries: list[str] = []
    depth = 0
    start = None
    for i, ch in enumerate(body):
        if ch == "{":
            if depth == 0:
                start = i + 1
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                entries.append(body[start:i])
                start = None
    if len(entries) != 59:
        raise RuntimeError(
            f"expected 59 planet_array entries, got {len(entries)}"
        )

    out: list[dict] = []
    for name, entry in zip(names, entries):
        # Strip the UsefulElements block (we don't need element-by-element
        # data right now; that's for mineral deposits — Phase 2 of the port)
        nested = re.search(r"\{[^{}]*\}", entry, re.DOTALL)
        if nested:
            entry = entry[:nested.start()] + entry[nested.end():]

        # Find the MAKE_BYTE(...) for Type
        type_match = re.search(
            r"MAKE_BYTE\s*\(\s*([A-Z_+\s0-9]+?)\s*,\s*([A-Z_]+_BODY)\s*\)",
            entry,
        )
        if not type_match:
            raise RuntimeError(f"Type MAKE_BYTE not found for {name}")
        size_algo = type_match.group(1)
        color = type_match.group(2)

        # Strip the type_match from the entry, then look for the tectonics
        entry_remainder = entry[type_match.end():]
        # First identifier after that is the Tectonics constant
        tect_match = re.search(r"([A-Z_]+_TECTONICS)", entry_remainder)
        if not tect_match:
            raise RuntimeError(f"Tectonics not found for {name}")
        tectonics = tect_match.group(1)

        # Next MAKE_BYTE for AtmoAndDensity
        ad_match = re.search(
            r"MAKE_BYTE\s*\(\s*([A-Z_]+_DENSITY)\s*,\s*([A-Z_]+)\s*\)",
            entry_remainder[tect_match.end():],
        )
        if not ad_match:
            raise RuntimeError(f"AtmoAndDensity MAKE_BYTE not found for {name}")
        density_const = ad_match.group(1)
        atmo_const = ad_match.group(2)

        # Compute byte values
        # Parse "SMALL_ROCKY_WORLD + CRATERED_ALGO" or similar
        size_algo_clean = size_algo.replace(" ", "")
        parts = size_algo_clean.split("+")
        size_val = 0
        algo_val = 0
        for p in parts:
            p = p.strip()
            if p in SIZE_VALUES:
                size_val = SIZE_VALUES[p]
            elif p in ALGO_VALUES:
                algo_val = ALGO_VALUES[p]
            else:
                raise RuntimeError(
                    f"unknown size/algo component {p!r} in {name}"
                )
        color_val = COLOR_BODIES[color]
        type_byte = (size_val | algo_val) | (color_val << 4)

        atmo_byte = (DENSITY[density_const]) | (ATMOSPHERE[atmo_const] << 4)

        # Find the 4 trailing knobs (num_faults, fault_depth, num_blemishes,
        # base_elevation) — they're the last 4 comma-separated values
        # after the resource references.
        # Just grab all integer tokens after the AtmoAndDensity MAKE_BYTE
        tail = entry_remainder[tect_match.end() + ad_match.end():]
        # Strip comments
        tail = re.sub(r"/\*.*?\*/", "", tail, flags=re.DOTALL)
        tail = re.sub(r"//.*", "", tail)
        # Find the trailing integer sequence: 4 numbers (possibly negative)
        knobs = re.findall(r"-?\d+", tail)
        if len(knobs) < 4:
            raise RuntimeError(
                f"map-gen knobs not found for {name}: tail={tail!r}"
            )
        # The last 4 numbers are the knobs (skip any earlier resource indices)
        nums = knobs[-4:]

        out.append({
            "name": name,
            "type_byte": type_byte,
            "size": size_val,
            "algo": algo_val,
            "color": color,
            "color_idx": color_val,
            "tectonics_const": tectonics,
            "tectonics_val": TECTONICS[tectonics],
            "density_const": density_const,
            "density_val": DENSITY[density_const],
            "atmosphere_const": atmo_const,
            "atmosphere_val": ATMOSPHERE[atmo_const],
            "atmo_and_density_byte": atmo_byte,
            "num_faults": int(nums[0]),
            "fault_depth": int(nums[1]),
            "num_blemishes": int(nums[2]),
            "base_elevation": int(nums[3]),
        })
    return out


# ---------------------------------------------------------------------------
# Parse orbits.c for the six XxxDistribution() rarity tables
# ---------------------------------------------------------------------------

DISTRIBUTION_NAMES = [
    "BlueDistribution",
    "GreenDistribution",
    "OrangeDistribution",
    "RedDistribution",
    "WhiteDistribution",
    "YellowDistribution",
]

DIST_TO_COLOR = {
    "BlueDistribution":   "BLUE_BODY",
    "GreenDistribution":  "GREEN_BODY",
    "OrangeDistribution": "ORANGE_BODY",
    "RedDistribution":    "RED_BODY",
    "WhiteDistribution":  "WHITE_BODY",
    "YellowDistribution": "YELLOW_BODY",
}


def extract_distributions(planet_names: list[str]) -> dict[str, list[int]]:
    """Walk orbits.c, pull each XxxDistribution() table as a 59-entry
    list of rarity values."""
    text = ORBITS_C.read_text(encoding="utf-8")
    out: dict[str, list[int]] = {}
    for dist_name in DISTRIBUTION_NAMES:
        m = re.search(
            r"static\s+BYTE\s+" + dist_name
            + r"\s*\([^)]*\)\s*\{(.*?)return\s*\(PlanetDistribution\[which_world\]\);",
            text, re.DOTALL,
        )
        if not m:
            raise RuntimeError(f"distribution {dist_name} not found in orbits.c")
        body = m.group(1)
        # Find the array initializer
        arr_match = re.search(
            r"const\s+BYTE\s+PlanetDistribution\[[^\]]*\]\s*=\s*\{(.*?)\};",
            body, re.DOTALL,
        )
        if not arr_match:
            raise RuntimeError(f"PlanetDistribution array not found in {dist_name}")
        values: list[int] = []
        for tok in re.finditer(
            r"(PLANET_NEVER|PLANET_RARE|PLANET_FEW|PLANET_COMMON|PLANET_ALWAYS)",
            arr_match.group(1),
        ):
            values.append(PLANET_RARITIES[tok.group(1)])
        if len(values) != 59:
            raise RuntimeError(
                f"distribution {dist_name} has {len(values)} entries, expected 59"
            )
        out[DIST_TO_COLOR[dist_name]] = values
    return out


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def main() -> int:
    if not PLANDATA_C.exists() or not ORBITS_C.exists():
        print(f"missing UQM source files; expected at {UQM}", file=sys.stderr)
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    names = extract_planet_type_names()
    print(f"got {len(names)} planet-type names")

    frames = extract_planet_frames(names)
    types_path = OUT_DIR / "uqm_planet_types.json"
    types_path.write_text(json.dumps(frames, indent=2), encoding="utf-8")
    print(f"wrote {len(frames)} planet types -> {types_path.relative_to(ROOT)}")

    dists = extract_distributions(names)
    # Annotate each entry with which planet types are reachable
    dists_path = OUT_DIR / "uqm_star_distributions.json"
    dists_path.write_text(json.dumps({
        "planet_type_names": names,
        "distributions": dists,
    }, indent=2), encoding="utf-8")
    print(
        f"wrote 6 star-color distributions × {len(names)} types -> "
        f"{dists_path.relative_to(ROOT)}"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
