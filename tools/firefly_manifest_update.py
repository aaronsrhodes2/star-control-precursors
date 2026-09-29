"""Update _manifest.json after 2026-05-17 burst session.

Marks Phase 1 NEW prompts as 'pending' and updates reroll items
(reroll_requested → pending after a fresh image is in place).
"""

import json
import pathlib
from datetime import datetime

MANIFEST_PATH = pathlib.Path("assets/generated_drafts/firefly/_manifest.json")
NOW = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

# 18 NEW Phase 1 prompts saved this session (added as new manifest entries)
NEW_PHASE1 = [
    ("tier1_portraits/species_stelloth_chord", "1:1", "stelloth chord-being portrait"),
    ("tier1_ships/ship_stelloth_three_voice_arc", "1:1", "stelloth triple-hull ship"),
    ("tier1_dialog_backgrounds/bg_stelloth_trading_post", "1:1", "stelloth station interior"),
    ("tier1_portraits/species_selvenne_polyp", "1:1", "selvenne bioluminescent polyp"),
    ("tier1_dialog_backgrounds/bg_selvenne_brain_coral_sanctum", "1:1", "selvenne coral sanctum"),
    ("tier1_cutscenes/cutscene_selvenne_memory_playback", "16:9", "selvenne qualia memory frame"),
    ("tier1_portraits/species_mrokon_vrek_puppet", "1:1", "mrokon vrek puppet"),
    ("tier1_portraits/species_mrokon_operator_bunker", "1:1", "mrokon operator bunker-dweller"),
    ("tier1_planets/planet_mrokons_stand_surface", "1:1", "mrokon homeworld surface"),
    ("tier1_ships/ship_mrokon_hammer_ship", "1:1", "mrokon hammer warship"),
    ("tier1_portraits/species_kovellim_ovala_elder", "1:1", "kovellim elder with knot-scars"),
    ("tier1_planets/bg_kovellim_eight_knot_station", "1:1", "kovellim eight-knot orbital station"),
    ("tier1_dialog_backgrounds/bg_kovellim_receiving_chamber", "1:1", "kovellim octagonal chamber"),
    ("tier1_ships/ship_kovellim_crossing_frigate", "1:1", "kovellim crossing frigate"),
    ("tier1_dialog_backgrounds/bg_karavem_welcome_choir", "1:1", "karavem 12-voice welcome choir"),
    ("tier1_portraits/species_karavem_veled_elder", "1:1", "karavem elder conductor"),
    ("tier1_planets/bg_aeris_sing_canyons", "1:1", "karavem homeworld canyon-cities"),
    ("tier1_ships/ship_karavem_aria_skiff", "1:1", "karavem bird-of-prey combat skiff"),
]

# Reroll items that got a fresh save this session (reroll_requested → pending)
REROLLED_TO_PENDING = [
    "tier1_ships/ship_furling_scout",
    "tier1_ships/ship_arilou_skiff",
    "tier1_ships/ship_mmrnmhrm_sentinel",
    "tier1_ships/ship_androsynth_cruiser",
    "tier1_portraits/species_slylandro_witness_portrait",
    "tier1_portraits/species_taalo_portrait",
    "tier1_portraits/species_melnorme_portrait",
    "tier1_artifacts/artifact_distress_beacon_device",
    "tier1_avatars/avatar_planar_witness",
    "tier1_avatars/avatar_utwig_elder",
    "tier1_avatars/avatar_taalo",
    "tier1_avatars/avatar_mmrnmhrm_sentinel",
    "tier1_avatars/avatar_vael_souren_cleanser",
    "tier1_cutscenes/cutscene_migration_portal",
]


def main():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    # Insert NEW Phase 1 entries
    for key, aspect, desc in NEW_PHASE1:
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
                "NEW 2026-05-17 Phase 1 new-species batch. "
                "Per HANDOFF_image_chat.md from Lore-chat worktree. "
                "Simplified prompt (~800-900 chars) to avoid Firefly content "
                "filter. Awaiting Aaron review."
            ),
        }

    # Move rerolled items to pending and bump generated_at
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
            f"REROLLED 2026-05-17 via Firefly Image 3 (free unlimited tier). "
            f"Prior notes: {prior_notes}"
        )

    # Reorder by key alpha
    out = dict(sorted(manifest.items()))
    MANIFEST_PATH.write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(f"Manifest updated: {len(out)} entries total")
    print(f"  NEW Phase 1 entries: {len(NEW_PHASE1)}")
    print(f"  Rerolled entries: {len(REROLLED_TO_PENDING)}")


if __name__ == "__main__":
    main()
