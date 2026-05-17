# Handoff to SCZ Testing chat — please verify the new hyperspace map

(Generated 2026-05-17. Image-generation chat handing off to the testing chat.)

## What landed
Two new interactive layers on the hyperspace map, committed as **`f3ec796`**:

1. **ZoneRenderer** (toggleable species control zones) — `src/scz/hyperspace/zones.py`
2. **SearchOverlay** (text-input star name search) — `src/scz/hyperspace/search.py`

Both are wired into `HyperspaceScene.update()` and `.render()`. New input bindings live in `src/scz/engine/input.py` (`toggle_zones`, `open_search`).

## Please run

```powershell
cd D:\Aaron\development\star-control-precursors
.\.venv\Scripts\python.exe -m scz --test walk_tutorial_path --windowed
.\.venv\Scripts\python.exe -m scz --test walk_arilou_sage --windowed
.\.venv\Scripts\python.exe -m scz --test walk_orbit_and_surface --windowed
.\.venv\Scripts\python.exe -m scz --test walk_super_melee --windowed
```

Expected: **38/38 pass** (9 + 18 + 5 + 6). These were all green at commit time.

## Manual smoke test for the new features (no walk-test coverage yet)

While in **HyperspaceScene** (any scene with the player ship + starmap):

### Zone overlay (Z key)
- Press **Z** — six translucent species-tinted blobs should appear over the map:
  - **Slylandro** (warm peach, single blob at Beta Corvi, bottom-left)
  - **Mycon biot hives** (red, at Epsilon Scorpii)
  - **Mmrnmhrm + Chenjesu** (cool blue, at Procyon)
  - **Melnorme trade routes** (orange, ~9 blobs spread around super-giants)
  - **Rainbow Worlds** (violet, 10 blobs forming an arrow)
  - **Orz rift incursions** (purple, scattered)
- Press **Z** again — blobs disappear. Default state is OFF.

### Star search (/ key)
- Press **/** — modal panel slides in at top with text input.
- Type **"sol"** → preview should show `→ Sol [SOL_PROTO]` in yellow.
- Press **Enter** → camera jumps to Sol; autopilot engages on it.
- Open again, type **"procy"** → preview shows `→ Procyon [CHENJESU_PROTO]`. Enter jumps there.
- **Esc** at any time closes the overlay without moving.
- While search is open, **ship doesn't move** even if you hold arrow keys.

## Known issues to watch for
- Zone overlay uses `BLEND_RGBA_ADD` — overlapping zones brighten rather than mix. If two overlapping species clash visually, that's a tuning issue, not a bug.
- Search consumes ALL keyboard while open via `pygame.key.start_text_input()`. If Escape doesn't close it cleanly, check `stop_text_input()` is being called.
- The Z toggle is bound to `inp.toggle_zones` (key `K_z`). Also bound: `inp.open_search` on `K_SLASH`. No controller bindings yet (intentional — these are mouse-and-keyboard features).

## Likely follow-ups after testing
- Re-tune zone alpha if zones are too loud or too faint
- Refine SearchOverlay typography
- Add controller bindings (Back button for search?)
- Map L1 — clean nebula backdrop via Firefly Reference Image (queued at `tools/firefly_prompts/tier1_nebula/bg_galaxy_nebula.txt`)

## Lore + data notes
Control zones are computed at scene-construction from `Starmap.stars[]` filtered by `defined_name`:
- `SLYLANDRO`, `MYCON_BIOT_HIVE`, `CHENJESU_PROTO`, `MELNORME_PROTO`, `RAINBOW_BEING_SEEDED`, `ORZ_RIFT` are the active tags.
- Proto-species are deliberately SKIPPED (below detection threshold, not active in our era).

If you need to add a new zone (e.g. for Talos, Planar, Mycon awakening sites), edit `build_default_zones()` in `src/scz/hyperspace/zones.py:120`.

Please report back: walk-test counts, any visual weirdness, any input-state weirdness (ship drifting while search is open, etc).
