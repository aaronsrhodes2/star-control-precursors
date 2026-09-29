"""Update _manifest.json after second 2026-05-17 burst.

Adds Lemmkin trio + 3 lander animations as NEW.
Moves Halia + 5 furling reference characters from reroll/reject → pending.
"""

import json
import pathlib
from datetime import datetime

MANIFEST_PATH = pathlib.Path("assets/generated_drafts/firefly/_manifest.json")
NOW = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

NEW_ENTRIES = [
    ("tier1_portraits/species_lemmkin_portrait", "1:1", "lemmkin curator portrait"),
    ("tier1_avatars/avatar_lemmkin_curator", "1:1", "lemmkin curator avatar"),
    ("tier1_ships/ship_lemmkin_skitter", "1:1", "lemmkin glass-cannon scout ship"),
    ("tier1_lander/lander_furling_descending", "1:1", "lander descending animation"),
    ("tier1_lander/lander_furling_ascending", "1:1", "lander ascending animation"),
    ("tier1_lander/lander_furling_destroyed", "1:1", "lander destroyed animation"),
]

REROLLED_TO_PENDING = [
    "tier1_portraits/species_commander_halia_portrait",
    "tier1_avatars/avatar_commander_halia",
    "tier1_furling_reference/furling_persuader",
    "tier1_furling_reference/furling_compeller",
    "tier1_furling_reference/furling_defender",
    "tier1_furling_reference/furling_hider",
    "tier1_furling_reference/furling_denier",
]


def main():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    for key, aspect, desc in NEW_ENTRIES:
        category, slug = key.split("/", 1)
        manifest[key] = {
            "prompt_path": f"tools/firefly_prompts/{category}/{slug}.txt",
            "image_path": f"assets/generated_drafts/firefly/{key}.png",
            "aspect": aspect,
            "model": "Firefly Image 3",
            "generated_at": NOW,
            "status": "pending",
            "tags": [slug.split("_")[0], desc],
            "notes": (
                "NEW 2026-05-17 second burst: Lemmkin + lander animations. "
                "Awaiting Aaron review."
            ),
        }

    for key in REROLLED_TO_PENDING:
        if key not in manifest:
            print(f"  WARN: {key} not in manifest, skipping")
            continue
        entry = manifest[key]
        prior_notes = entry.get("notes", "")
        entry["status"] = "pending"
        entry["generated_at"] = NOW
        entry["model"] = "Firefly Image 3"
        entry["notes"] = (
            f"REROLLED 2026-05-17 second burst via Firefly Image 3. "
            f"Prior notes: {prior_notes}"
        )

    out = dict(sorted(manifest.items()))
    MANIFEST_PATH.write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(f"Manifest updated: {len(out)} entries total")
    print(f"  NEW: {len(NEW_ENTRIES)}")
    print(f"  Rerolled: {len(REROLLED_TO_PENDING)}")


if __name__ == "__main__":
    main()
