"""Third burst manifest update — Aaron's specific reroll notes."""

import json
import pathlib
from datetime import datetime

MANIFEST_PATH = pathlib.Path("assets/generated_drafts/firefly/_manifest.json")
NOW = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

REROLLED = [
    ("tier1_portraits/species_mycon_biot_portrait",
     "Prior was wrong species (bone planet). Now: canonical SC2 Mycon "
     "biot — fungal humanoid with mushroom-cap head and mycelial neck-fronds."),
    ("tier1_avatars/avatar_planar_witness",
     "Prior had a humanoid figure inside the glass. Per Aaron: 'No body, "
     "just a sheet of transparency.' Now: pure iridescent rectangular sheet "
     "of pearlescent glass, no figure inside, just the geometric flat shape."),
    ("tier1_portraits/species_mmrnmhrm_portrait",
     "Prior was rejected as 'fine androsynth, if not menacing enough'. "
     "Now: hulking armored ancient mechanical guardian with single bright "
     "cyan central optical sensor, brutalist industrial styling, menacing."),
    ("tier1_dialog_backgrounds/bg_planet_surface",
     "Prior was landscape view. Per Aaron: 'need top-down terrain for our "
     "resource gathering minigame.' Now: bird's-eye-view satellite shot, "
     "rocky desert tile with umber sand + pale-cream outcrops."),
    ("tier1_avatars/avatar_chenjesu_witness",
     "Prior had arms. Per Aaron: 'remove the arms.' Now: rooted crystal-"
     "spire being, no arms, immobile ancient mineral consciousness."),
]


def main():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    for key, why in REROLLED:
        if key not in manifest:
            print(f"  WARN: {key} not in manifest, skipping")
            continue
        entry = manifest[key]
        prior_notes = entry.get("notes", "")
        entry["status"] = "pending"
        entry["generated_at"] = NOW
        entry["model"] = "Firefly Image 3"
        entry["notes"] = (
            f"REROLLED 2026-05-17 burst 3. {why} Prior: {prior_notes[:120]}"
        )
    out = dict(sorted(manifest.items()))
    MANIFEST_PATH.write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Manifest updated: {len(out)} entries total ({len(REROLLED)} rerolled)")


if __name__ == "__main__":
    main()
