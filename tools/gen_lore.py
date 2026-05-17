"""Gemini-backed lore generator.

Loads a curated slice of project context (rules + lore + existing ship/
species schemas), sends it to Gemini Flash with a structured-output
request, saves the JSON response to tools/gemini_drafts/ for Aaron to
review before any code or doc merge.

Usage:
    .venv/Scripts/python.exe tools/gen_lore.py SLUG  --task ship
    .venv/Scripts/python.exe tools/gen_lore.py SLUG  --task species
    .venv/Scripts/python.exe tools/gen_lore.py SLUG  --task planet

`SLUG` becomes the output filename: tools/gemini_drafts/<task>_<SLUG>.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors
from google.genai import types

ROOT = Path(__file__).resolve().parent.parent
DRAFTS_DIR = ROOT / "tools" / "gemini_drafts"
ENV_PATH = ROOT.parent / ".env"     # D:/Aaron/development/.env


# ---------- Project context (compact — keep under ~6KB) -----------------

PROJECT_PRIMER = """
You are helping author content for **Star Control Zero: The Precursors**, a
fan-game prequel to Star Control II set 250,000 years earlier in the era
of the Furlings (the species SC2 will later call "Precursors"). The
canonical narrative bible lives in references/lore/.

Iron rules:
- The Furlings are the protagonists, calling themselves "the Furred Ones."
  SC2 humans will later misinterpret the name as "Precursors."
- The galaxy is being detected by trans-dimensional predators called
  **the Others**. The Others sense concentrations of cognition. Civilizations
  must either Migrate (cross via a neighbor-galaxy portal), Cloak (suppress
  their cognitive signal — the Slylandro Cloaking Satellite solution),
  Hide (off-grid burrowed silence), Eliminate (die fighting), or be left
  Pre-sentient (below detection threshold by nature).
- Furling factions split over how to handle Homesteaders (species who
  refuse to Migrate): **Persuader** (diplomatic), **Compeller** (firm-
  hand), **Cleanser** (lethal kindness — kill them so the Others don't
  notice them), **Defender** (stay and fight, build the Sa-Matra).
- Each SC2 species we touch in this era is either *proto* (pre-sentient
  ancestor — observation-only encounter) or *full sentient* (active
  participant). Per Rule 4a, when authoring a species with an SC2
  counterpart, use the SC2 form as the silhouette and apply a deliberate
  Furling-era regression delta in the lore.
- Combat is 1v1 top-down with wrap-around arenas, asymmetric ship stats.
  Per ship_design_schema, identity > balance when conflicting.

Tone:
- Furling protagonist is allowed humor and warmth.
- Most aliens are not funny; humor comes from cultural friction.
- **The Others are NEVER funny.** That break is the horror.
- Variable narrative voice — lean into each species' diction.

Creative license — important:
- When asked for a *new* species or ship (i.e. not an SC2 call-forward),
  *be bold and weird*. SC2's signature is alien designs whose lore
  AND mechanics flow from a single bizarre premise:
    * A *two-dimensional* race that can't be damaged head-on (no width
      to hit). Their ship's special is a forward-slice; primary is a
      planar arc that widens and weakens with distance (shotgun-like).
    * A species whose cognition is *distributed across multiple
      star systems* by FTL signaling — their ship's special is to
      'reach out' for help and another ship phases in for one volley.
    * A species that *eats time*. Damage they deal slowly heals; damage
      they take slowly drains them long after the fight.
  These are the calibre of premise we want — premises that *imply*
  unique stats, weapons, and dialog all at once. Don't settle for
  generic "warrior race with plasma cannon."
- The body plan, voice, and ship mechanics should be **mutually
  reinforcing**. If the body is two-dimensional, the ship is a blade.
  If the body is a hive, the ship swarms.
- Furling-era regression (Rule 4a) only applies when there IS an SC2
  counterpart. For pure inventions, no regression — be your most
  inventive self.

Output discipline: respond with **valid JSON only** matching the requested
schema. No prose, no markdown fencing, no commentary outside the JSON.
"""


# Per-task: extra schema + extra context.

TASK_PROFILES: dict[str, dict] = {
    "ship": {
        "context_files": [
            "references/lore/ship-design-schema.md",
            "references/lore/ship-roster.md",
        ],
        "schema_doc": """
Return JSON with this shape:
{
  "id": "snake_case_id",
  "name": "Display Name (e.g. 'Melnorme Trade Cruiser')",
  "side": "precursor" | "homesteader" | "special",
  "points": int,        // super-melee point cost; 95-180 typical
  "hull_max": int,      // 50-200
  "shield_max": int,    // 0-100; 0 = unshielded
  "shield_regen": float, // per-second; if shield_max > 0
  "shield_regen_delay": float, // seconds after last hit
  "top_speed": float,    // 100-360
  "acceleration": float, // 100-450
  "turn_rate": float,    // 1.0-6.0 (radians/sec)
  "mass": int,           // 50-200
  "energy_max": int,     // 30-120
  "energy_regen": float, // per-second
  "primary_damage": int,
  "primary_energy": int,
  "primary_rate": float, // shots/sec
  "primary_range": int,
  "primary_speed": int,
  "primary_color_rgb": [int, int, int],
  "hull_color_rgb": [int, int, int],
  "accent_color_rgb": [int, int, int],
  "silhouette": "scout" | "skiff" | "cruiser" | "heavy" | "sentinel" | "warship" | "blade",
  "ai_style": "brawler" | "kiter" | "circler" | "left_only",
  "primary_name": "weapon display name",
  "primary_description": "one-line in-fiction description",
  "special_name": "ability display name (TBD if no special)",
  "special_description": "one-line description of the special ability and its tradeoff",
  "lore": "2-4 sentence in-fiction description of the ship class, the species who flies it, and how it fits in the era"
}

Tune stats to the ai_style and side: brawlers prefer high HP + close
range; kiters prefer mobility + long range; circlers favor turn rate +
medium range. Make ONE ship-defining tradeoff clear (e.g. "fragile but
fast", "slow but devastating").
""",
    },
    "species": {
        "context_files": [
            "references/lore/species-design-schema.md",
            "references/lore/species-precursor-era.md",
        ],
        "schema_doc": """
Return JSON with this shape:
{
  "id": "SNAKE_UPPER_ID",
  "common_name": "What they call themselves",
  "furling_archive_name": "What Furlings call them",
  "sentience_status": "pre_sentient" | "infant_sentient" | "full_sentient",
  "physical": "2-4 sentences on body plan, scale, sensory modalities",
  "speech_pattern": "1-2 sentences on how they talk (vocabulary, syntax, register)",
  "posture": "1 sentence on the iconic body language / silhouette",
  "homeworld_name": "Furling-era name of their main planet (if they have one)",
  "homeworld_descriptor": "1 sentence describing the planet",
  "faction_alignment": "precursor" | "homesteader" | "neither" | "split",
  "motive_in_era": "2-3 sentences on what drives them in the Furling era",
  "sc2_callforward": "1-2 sentences on how the SC2 version of this species relates to the Furling-era version (per Rule 4a)",
  "encounter_hook": "1-2 sentences on what makes their slice-encounter memorable"
}
""",
    },
    "planet": {
        "context_files": [
            "references/lore/slice-cluster.md",
        ],
        "schema_doc": """
Return JSON with this shape:
{
  "name": "Furling-era planet name",
  "system_name": "Star system Furling-era name",
  "system_coords_universe": [int, int],   // in (0..10000, 0..10000)
  "planet_type": "ROCKY" | "GAS_GIANT" | "ICE" | "DESERT" | "OCEAN" | "JUNGLE" | "VOLCANIC",
  "atmosphere": "1 line",
  "surface_description": "2-3 sentences",
  "notable_resources": ["RESOURCE_TYPE", ...],
  "biological_descriptor": "1 sentence on whether life exists and what kind",
  "lore_hook": "1-2 sentences on why this planet matters to the slice"
}
""",
    },
}


def load_context(files: list[str]) -> str:
    """Read + concatenate the listed context files (truncated for budget)."""
    out: list[str] = []
    for rel in files:
        p = ROOT / rel
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        # Trim to keep total context modest
        if len(text) > 8000:
            text = text[:8000] + "\n[...truncated...]"
        out.append(f"--- BEGIN {rel} ---\n{text}\n--- END {rel} ---")
    return "\n\n".join(out)


def build_prompt(task: str, slug: str, brief: str) -> str:
    profile = TASK_PROFILES[task]
    context = load_context(profile["context_files"])
    return (
        f"AUTHORING TASK: generate a {task} entry called '{slug}'.\n\n"
        f"BRIEF FROM AARON:\n{brief}\n\n"
        f"SUPPORTING CONTEXT:\n{context}\n\n"
        f"OUTPUT REQUIREMENTS:\n{profile['schema_doc']}\n\n"
        f"Return JSON only. No markdown fences. No prose outside the JSON."
    )


def _retry_delay_from_429(err: genai_errors.ClientError) -> float | None:
    """Pull a 'retry in N s' hint out of a 429 error. None if not a 429
    or not parseable."""
    msg = str(err)
    m = re.search(r"retry in ([\d.]+)\s*s", msg, re.IGNORECASE)
    if m:
        return float(m.group(1))
    m = re.search(r"retryDelay['\"]?\s*:\s*['\"]?(\d+)s", msg)
    if m:
        return float(m.group(1))
    return None


def call_gemini(prompt: str, model: str = "gemini-2.5-flash") -> str:
    """Returns raw text response from Gemini. Retries once on a 429
    rate-limit error using the server's suggested delay."""
    load_dotenv(ENV_PATH)
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(f"GEMINI_API_KEY not in {ENV_PATH}")
    client = genai.Client(api_key=api_key)
    full_prompt = PROJECT_PRIMER + "\n\n" + prompt
    cfg = types.GenerateContentConfig(
        temperature=0.85, response_mime_type="application/json",
    )
    try:
        resp = client.models.generate_content(
            model=model, contents=full_prompt, config=cfg,
        )
        return resp.text or ""
    except genai_errors.ClientError as err:
        if "429" not in str(err) and "RESOURCE_EXHAUSTED" not in str(err):
            raise
        delay = _retry_delay_from_429(err)
        if delay is None:
            raise
        # Hard cap so the script can't hang on a per-day limit
        if delay > 90:
            print(
                f"[gen_lore] 429 — retry hint {delay:.0f}s is too long "
                f"(likely per-day quota). Aborting.",
                file=sys.stderr,
            )
            raise
        wait = delay + 2.0
        print(
            f"[gen_lore] 429 — waiting {wait:.1f}s then retrying once",
            file=sys.stderr,
        )
        time.sleep(wait)
        resp = client.models.generate_content(
            model=model, contents=full_prompt, config=cfg,
        )
        return resp.text or ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("slug", help="output filename slug (used as ID hint)")
    parser.add_argument(
        "--task", required=True, choices=list(TASK_PROFILES.keys()),
        help="what to generate"
    )
    parser.add_argument(
        "--brief", default="",
        help="one-paragraph brief for the LLM (sets direction, "
             "constraints, references) — if omitted, reads from stdin"
    )
    parser.add_argument("--model", default="gemini-2.5-flash")
    args = parser.parse_args()

    brief = args.brief
    if not brief:
        print("Reading brief from stdin (Ctrl-D / Ctrl-Z to finish):",
              file=sys.stderr)
        brief = sys.stdin.read()
    if not brief.strip():
        print("ERROR: brief is empty", file=sys.stderr)
        return 1

    prompt = build_prompt(args.task, args.slug, brief)
    print(f"[gen_lore] task={args.task} slug={args.slug} model={args.model}",
          file=sys.stderr)
    print(f"[gen_lore] prompt length: {len(prompt)} chars", file=sys.stderr)

    raw = call_gemini(prompt, model=args.model)
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"[gen_lore] WARNING: response not valid JSON ({e}); "
              f"saving raw text", file=sys.stderr)
        parsed = {"_raw_text": raw, "_parse_error": str(e)}

    DRAFTS_DIR.mkdir(exist_ok=True, parents=True)
    out_path = DRAFTS_DIR / f"{args.task}_{args.slug}.json"
    out_path.write_text(
        json.dumps(parsed, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"[gen_lore] wrote {out_path}", file=sys.stderr)
    # Echo to stdout so callers can pipe
    print(json.dumps(parsed, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
