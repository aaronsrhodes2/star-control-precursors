# HANDOFF — Lore / Design / Combat Chat → Image Chat

> Outbox for canon + design changes that require image-side reprocessing. The **Image chat** reads this file at the start of each session, picks up open entries, regenerates/updates the affected Firefly prompts + assets, and marks entries `✅ PROCESSED <date>` (or removes them) when done. **Lore / Design / Combat chats** append new entries when authoring a change that affects visual content.
>
> This file is the **canonical Lore→Image handoff document**, parallel to `tools/species_inventory.csv` (which is the species-side handoff). It is not a TODO list for Lore chat work; it is a *broadcast queue* for Image chat work that Lore chat has determined is needed.
>
> **Lane discipline reminder**: Lore chat does NOT edit `tools/firefly_prompts/`, `tools/gen_image.py`, `tools/firefly_*.py`, `assets/generated_drafts/firefly/*`, or any image assets directly. That's Image chat's lane. Lore chat *describes* what changed and *what should change image-side*; Image chat *executes* the regenerations.
>
> Format: each entry has a date, a short title, the canon change, the affected asset categories, and recommended action. Newest entries at the top.

---

## 2026-05-19 — Consolidated TODO_AVATAR backlog (16 markers, ~14 unique NPCs)

**Origin**: Testing chat, during the overnight perfect-run dispatch pass. Aaron asked all chats to "fill out final orders" — this is the consolidated avatar-authoring backlog the Image chat owns.

**How derived**: `Grep -rn "TODO_AVATAR" src/scz/dialog/characters.py` (16 matches; characters.py is the only file with the marker). Each marker has a pre-written silhouette/palette/setting description authored by Lore/Design chat — Image chat's job is to take those descriptions, draft Firefly prompts, generate variants, and wire into the per-character avatar field.

**Status**: ☐ Open

### NPC list (alphabetized; line refs are post-2026-05-19)

Each entry below cites the line number in `src/scz/dialog/characters.py` where the marker lives. The comment immediately above the character factory contains the canonical silhouette/setting/palette prompt-anchor language the Image chat can drop into Firefly.

| Line | NPC | Species | Notes |
|---|---|---|---|
| ~2131 | **Mraka Yenn-Sa** | Furling Drifter | Warm-tan fur, station-wear coat, observation-deck backdrop. Mraka has a full 7-state recruitment FSM (the canonical example crew member); high-priority avatar. |
| ~2341 | **Vesh Vasa-Lon** | Furling Survey Commander | Research-vessel interior backdrop, muted observation-deck lighting, instrumentation rig visible behind shoulders. Named NPC. |
| ~2391 | **Brisk-Ever-Onward** | Lemmkin elder | Small fast quadrupedal-ish, bright contrasting plate-pattern, paw raised mid-question; half-dozen smaller juvenile Lemmkin in formation behind. Named NPC, species reveal. |
| ~2779 | **Utwig elder** | Utwig (pre-doctrine) | Mid-transition; armored bipedal humanoid grazer ~1.6m, weathered grey skin, bone-cream armor plating along shoulders; wearing early ceremonial veils. Per `project_utwig_devolution.md` — they JUST became sentient in our era. |
| ~3136 | **Burvixese Foreman** | Burvixese | Four-armed humanoid engineer ~1.8m, slate-blue skin with iridescent shimmer at joint creases; upper pair of arms holding precision tools. Named NPC. |
| ~3510 | **Taalo fragment** | Taalo | Silicon-crystalline humanoid mid-shamble, slate-grey/basalt-dark mineral plates with subtle iridescence, two pairs of stride-limbs. Late-era last-witness fragment. |
| ~3898 | **Chenjesu Collective** | Chenjesu | Towering crystalline outcrop with internal lattice glow, faceted spires extending up *and down* (rooted underground); faint chromatic shimmer. Prior-cycle survivor. |
| ~4186 | **Mmrnmhrm Sentinel** | Mmrnmhrm | Clean silver-white machine frame, transformable plates visible at shoulders, eye-lens array, ruined First-Makers' city skyline behind. Voice variation by transformation state. |
| ~4796 | **Cleanser Furling** | Furling (Cleanser hardliner) | Cold white-violet accents on Furling base hull silhouette. Antagonist faction member. |
| ~5060 | **Melnorme Council Elder** | Melnorme | Per `references/lore/species-quests.md` cross-chat dispatch — full-sentient BIO-cargo trader at super-giant stars. Side with Precursors. |
| ~5060 | **Melnorme Supermart Elder** | Melnorme | Second Melnorme variant; see same dispatch. |
| ~5417 | **Bren-Vor Telcas** | Furling Aimer (Weapons Officer crew) | TODO_LORE also flagged; full recruitment FSM pending Design implementation. Avatar can ship ahead of FSM. |
| ~5436 | **Yelena Lwen-Tar** | Furling Mender (Engineer crew) | Same — TODO_LORE also flagged; avatar can ship ahead of FSM. |
| ~5454 | **Mira-Rou Halve-Tel** | Furling Bio-Architect (Medic crew) | Same — TODO_LORE also flagged. |
| ~5472 | **Tarven Olwen-Sa** | Furling Star-Reader (Navigator crew) | Same — TODO_LORE also flagged. |

(Note: the 16th marker at ~4812 is a paired Avatar-fallback comment, not a separate NPC — it lives in the Cleanser Furling block.)

### Suggested generation order

1. **Crew recruits first** (Bren-Vor, Yelena, Mira-Rou, Tarven) — their FSMs are stubs today but they unlock the Best-ending 5/5 crew criterion. Mraka already has a full FSM but missing avatar; pair with these.
2. **Beat-encountered named NPCs** (Vesh Vasa-Lon, Burvixese Foreman, Brisk-Ever-Onward, Mmrnmhrm Sentinel, Utwig elder) — these all gate Bio-Archive entries and the species-saved count.
3. **Prior-cycle witnesses** (Chenjesu Collective, Taalo fragment) — atmospheric encounters; thematic weight.
4. **Faction-themed** (Cleanser Furling, Melnorme Elder pair) — late authoring once the per-faction visual language is locked.

### Wiring contract

Per the dual-chat split (memory: `workflow_dual_chat_split.md`): the avatar/portrait *field* binding happens in Image chat's lane. Drop the final PNG to `assets/comm/<character_id>.png` and add the `avatar_path=` kwarg or equivalent to the character factory. The TODO_AVATAR comment can be removed when complete (and `tools/check_stubs.py` will stop flagging it).

### Cross-references

- `tools/check_stubs.py` — re-run to verify count drops as each NPC ships
- `src/scz/dialog/characters.py` — all markers
- `references/lore/species-sheets.md` — canonical silhouette/voice per species (use as Firefly anchor language)
- `references/lore/crew-recruitment-quests.md` — per-crew background for the 4 stub recruits

---

## 2026-05-18 — Weapon FX projectile sprites (6 ships) + Star sprites (6 colors + starfield)

**Origin**: Aaron's directive (2026-05-18): "Nearly all of our weapon effects are either placeholders (colored circles) or we have generated them and not wired them in… We need gorgeous images for the stars that we will see in the hyperspace view and also in combat view and solar system view."

**Status**: ☐ Open. Prompts written and queued; first automated burv generation produced asteroid-like output, prompts rewritten with explicit anti-celestial-body anchoring. Subsequent automated drives are flaky from Chrome-MCP — Aaron may need to drive these interactively in Firefly Image 3.

### Queued prompts (paste into Firefly Image 3, download 4 variants, save as listed)

**Weapon FX projectile sprites** — drop the v1 download in `assets/generated_drafts/firefly/tier1_weapons/projectile_<ship_id>_v{1..4}.png`, then run `sd-server/.venv/Scripts/python.exe tools/extract_projectile_alpha.py --variant v1` to extract luma-alpha and copy to `assets/ships/sprites/projectile_<ship_id>.png`. The extract script's SHIPS list already includes all 17 ships.

| Prompt file | Saves to | Visual flavor |
|---|---|---|
| [tools/firefly_prompts/tier1_weapons/projectile_burv_broadcaster.txt](tools/firefly_prompts/tier1_weapons/projectile_burv_broadcaster.txt) | `assets/ships/sprites/projectile_burv_broadcaster.png` | Cyan-blue concentric shockwave rings |
| [tools/firefly_prompts/tier1_weapons/projectile_compeller_vessel.txt](tools/firefly_prompts/tier1_weapons/projectile_compeller_vessel.txt) | `assets/ships/sprites/projectile_compeller_vessel.png` | Translucent green sedation beam |
| [tools/firefly_prompts/tier1_weapons/projectile_lemmkin_skitter.txt](tools/firefly_prompts/tier1_weapons/projectile_lemmkin_skitter.txt) | `assets/ships/sprites/projectile_lemmkin_skitter.png` | Warm yellow tracer bolt |
| [tools/firefly_prompts/tier1_weapons/projectile_mycon_podship.txt](tools/firefly_prompts/tier1_weapons/projectile_mycon_podship.txt) | `assets/ships/sprites/projectile_mycon_podship.png` | Purple-red bio-plasmoid |
| [tools/firefly_prompts/tier1_weapons/projectile_thinn_blade.txt](tools/firefly_prompts/tier1_weapons/projectile_thinn_blade.txt) | `assets/ships/sprites/projectile_thinn_blade.png` | Iridescent teal-violet-gold knife-thin beam |
| [tools/firefly_prompts/tier1_weapons/projectile_utwig_jugger.txt](tools/firefly_prompts/tier1_weapons/projectile_utwig_jugger.txt) | `assets/ships/sprites/projectile_utwig_jugger.png` | Heavy amber bolt with green shield-halo |

**Star sprites** — drop the v1 download in `assets/generated_drafts/firefly/tier1_stars/star_<color>_v{1..4}.png`, then alpha-extract via `extract_sprite_alpha.py`-like pipeline (will need a new extraction step — stars are transparent-corona-on-black, so luma-alpha extraction is the right approach, same as projectiles). Final files go to `assets/stars/star_<color>.png`.

| Prompt file | Saves to | Star type |
|---|---|---|
| [tools/firefly_prompts/tier1_stars/star_blue.txt](tools/firefly_prompts/tier1_stars/star_blue.txt) | `assets/stars/star_blue.png` | Hot O/B blue star |
| [tools/firefly_prompts/tier1_stars/star_white.txt](tools/firefly_prompts/tier1_stars/star_white.txt) | `assets/stars/star_white.png` | A-class white star |
| [tools/firefly_prompts/tier1_stars/star_yellow.txt](tools/firefly_prompts/tier1_stars/star_yellow.txt) | `assets/stars/star_yellow.png` | G-class sun-like (Sol) |
| [tools/firefly_prompts/tier1_stars/star_green.txt](tools/firefly_prompts/tier1_stars/star_green.txt) | `assets/stars/star_green.png` | Exotic green anomaly star |
| [tools/firefly_prompts/tier1_stars/star_orange.txt](tools/firefly_prompts/tier1_stars/star_orange.txt) | `assets/stars/star_orange.png` | K-class orange giant |
| [tools/firefly_prompts/tier1_stars/star_red.txt](tools/firefly_prompts/tier1_stars/star_red.txt) | `assets/stars/star_red.png` | M-class red dwarf/giant |

**Combat starfield backdrop** — single image at 16:10:

| Prompt file | Saves to |
|---|---|
| [tools/firefly_prompts/tier1_stars/combat_starfield.txt](tools/firefly_prompts/tier1_stars/combat_starfield.txt) | `assets/combat/starfield.png` |

### Wiring contract (cross-dispatched to Combat chat — see [HANDOFF_combat_chat.md](HANDOFF_combat_chat.md) 2026-05-18 entry)

- Projectile sprites: **zero wiring needed** — `_load_projectile_sprite` already keys off `projectile_<ship_id>.png`.
- Star sprites: **new wiring needed** in 3 places — Combat starfield blit, Solar system sun blit (replacing layered-circle render), optional hyperspace zoomed-in star sprite. Combat chat has the spec.

### Status

- ☐ Open as of 2026-05-18.

---

## 2026-05-18 — Combat sprite spec (Combat chat — full reference)

**Origin**: Combat chat. The Image chat asked for the exact format spec for ship sprites and weapon effects. This entry is the canonical reference; future entries can refer back to it instead of re-stating format details.

### Ship sprite format — hard requirements

| Field | Value |
|---|---|
| **Format** | PNG, 32-bit, alpha channel required |
| **Background** | Fully transparent (alpha = 0 outside the ship silhouette) |
| **Orientation** | **NOSE-UP** — the ship's "forward" direction points toward the TOP of the image (−y in pygame coords). The engine rotates with `pygame.transform.rotozoom(sprite, -degrees(heading), scale)` |
| **Composition** | Centered. The pixel-center of the image is the ship's rotation center + collision center |
| **Aspect** | Square preferred (e.g. 512×512). Non-square works — the engine scales the LONGEST axis to the world-unit target, so a 512×256 image becomes a 56×28 in-world sprite |
| **Source size** | Authoring resolution is flexible; engine downscales via `smoothscale`. 512×512 is the convention and looks great at any viewport scale |
| **In-world target size** | Longest axis = **56 world units** (≈36px at typical viewport scale 0.7). Defined by `SHIP_SPRITE_BASE_SIZE` constant in [src/scz/combat/scene.py](../../src/scz/combat/scene.py:245) |
| **Path** | `assets/generated_drafts/firefly/tier1_ships/ship_<id>.png` |
| **Filename binding** | `SHIP_SPRITES[ship_id]` dict in `scene.py:229`. All 17 tier-1 ships are pre-registered (2026-05-18) — drop the PNG at the mapped filename and the engine picks it up automatically |
| **Hit-flash overlay** | Engine applies a programmatic warm-white additive tint when the ship takes damage. Sprite authors don't need to bake this in — it's `BLEND_RGBA_ADD` over the rotated sprite |
| **Fallback** | Missing/failed sprite loads fall back to a procedural polygon silhouette in `_draw_ship`. Engine never crashes on missing sprite; the legacy polygon-render code path is the safety net |
| **Angle handling** | **Continuous** — `pygame.transform.rotozoom` rotates the single nose-up sprite to any float angle per frame. **One sprite covers all 360°.** No angle-slice atlas needed, no per-angle pre-renders required. This is intentional (modern-indie clean look + zero asset multiplication). The legacy UQM/SC2 multi-angle pre-render aesthetic is a future visual-style decision; if Aaron ever signs off on it, Image chat would author N angles per ship and Combat chat would swap the loader to snap-nearest. Until then: single sprite per ship, full stop |

### Tier-1 ship sprite roster (17 entries)

`✅` = sprite present in the asset dir; `☐` = file claimed in `SHIP_SPRITES` but PNG missing → falls back to polygon.

| ship_id | Filename | Status |
|---|---|---|
| `furling_scout` | `ship_furling_scout.png` | ✅ |
| `persuader_vessel` | `ship_persuader_vessel.png` | ✅ |
| `arilou_skiff` | `ship_arilou_skiff.png` | ✅ |
| `androsynth_cruiser` | `ship_androsynth_cruiser.png` | ✅ |
| `cleanser_cruiser` | `ship_cleanser_cruiser.png` | ✅ |
| `melnorme_trader` | `ship_melnorme_trader.png` | ✅ |
| `defender_vessel` | `ship_defender_vessel.png` | ✅ |
| `mmrnmhrm_sentinel` | `ship_mmrnmhrm_sentinel.png` | ✅ |
| `proto_ur_quan` | `ship_proto_urquan.png` | ✅ |
| `proto_qor_ah` | `ship_proto_qor_ah.png` | ✅ |
| `sentry_drone_47t` | `ship_sentry_drone_47t.png` | ✅ |
| `compeller_vessel` | `ship_compeller_vessel.png` | ✅ |
| `mycon_podship` | `ship_mycon_podship.png` | ✅ |
| `utwig_jugger` | `ship_utwig_jugger.png` | ✅ |
| `lemmkin_skitter` | `ship_lemmkin_skitter.png` | ✅ |
| `thinn_blade` | `ship_thinn_blade.png` | ✅ (placeholder copy from planar_blade — needs canonical re-roll) |
| `burv_broadcaster` | `ship_burv_broadcaster.png` | ✅ |

Visual direction for the 6 missing entries is already in the 2026-05-17 "Combat-ship sprite roster gap" entry below.

### Weapon effects — what's procedural vs. what would benefit from sprites

**Current state**: every projectile is rendered procedurally as colored circles / polygons. There is no sprite system for projectiles yet — adding one is a Combat-side code change that will follow once Image chat has authored a sprite library worth wiring.

**Rendering inventory** (what the engine currently draws):

| Pattern / element | Used by | Current render | Sprite potential |
|---|---|---|---|
| `single` / `twin` / `triple` / `multi_spread` / `burst` | Scout default, Persuader, P-Ur-Quan, Mmrnmhrm | Solid circle in the ship's `primary_color` | **High** — small glowing bolt sprite, oriented along travel vector |
| `lance` | Androsynth, Thinn, Scout-with-Lance-Coil | Larger solid circle, faster | **High** — long thin bright bolt sprite (elongated, glowing) |
| `scatter` | Proto-Qor-Ah, Scout-with-Scatter-Array | Multiple small circles in a cone | Medium — small glowing bolt sprite reused 5×, jittered |
| `homing` / `homing_cluster` | Mmrnmhrm-missile-form, Scout-with-Homing-Mortar, Proto-Ur-Quan special | Solid circle with curved motion | **High** — plasmoid sprite + comet-tail trail particles |
| `charged` | Defender, Mycon, Proto-Ur-Quan | 2× radius solid circle | **High** — heavy glowing plasma-orb sprite (3 size variants for Melnorme tier_plasma) |
| `lawnmower_blade` | Proto-Qor-Ah, Scout-with-Lawnmower-Disc | 4-point rotating star polygon | **High** — saw-blade disc sprite, spun via `rotate` each frame |
| `tracking` | Arilou, Scout-with-Tracking-Laser | Curved laser bolt | Medium — narrow energy-bolt sprite (similar to single, but slightly different color tone) |
| `water_spray` (5 droplets per fire) | Cleanser | Cyan circles | **Medium** — water-blob sprite, splash-distortion on flight |
| `is_icepeedo` | Cleanser special | Chunky ice-blue circle, homing | **High** — chunky torpedo sprite (Cleanser ice-aesthetic) |
| `is_water → ice convert` | After 1s flight | Color shifts to ice blue | Medium — ice-fragment sprite |
| `engine_seeker` | Defender, Scout-with-Engine-Disruptor-Coil | Single homing bolt | **High** — Defender-aesthetic missile sprite (military missile body, exhaust trail) |
| `resonance_pulse` | Burv | Single circle with hit_debris on impact | **Medium** — sound-wave-ring sprite (concentric ring with motion blur) |
| `gravity_well` | Compeller | Layered alpha rings, pulsing | Already pretty (procedural) — could be enhanced with a swirling-distortion sprite |
| `chaff_spray` | Defender | Cloud sprites (alpha layered, procedural) | Already pretty — sprite would be flat improvement |
| `tractor_lasso` rope | Persuader | Wiggling yellow zig-zag (procedural) | Already pretty — special case, not sprite-friendly |
| `fried_discs` (orbital ring) | Proto-Qor-Ah special | 4-point star polygons orbiting host | Could share `lawnmower_blade` saw-blade sprite |
| `bubble` | Androsynth primary | Translucent purple circle | **Medium** — soap-bubble sprite |
| Engine-thruster particles | All thrusting ships | Procedural alpha-blended puffs (engine-glow tint) | Already pretty — no sprite needed |
| Debris particles (resonance hit) | Burv impact | Procedural points flying out | Already pretty — no sprite needed |
| **Hit flash / shield-hit ring** | All ships | Programmatic additive tint + shield circle stroke | Already pretty — no sprite needed |

**What the engine does NOT currently render** — opportunities for Image chat to add new visual investment:

1. **Impact / explosion sprites** — currently a projectile just disappears on hit and the target ship's `hit_flash` flickers warm-white. A small expanding blast-puff sprite at the impact point would massively improve "felt" combat.
2. **Death animation** — when a ship hits 0 HP, it just disappears with a brief wreck-stub render. A sprite-sheet or particle-burst explosion sprite would close this gap.
3. **Muzzle flash** — currently no per-shot visual at the firing point. A nose-flash sprite (small bright puff) authored once per ship-class could be tinted programmatically.

### Recommended priority order (Combat chat's request)

If Image chat budget is constrained, this is the priority order combat suggests:

1. **The 6 missing ship sprites** (see roster above) — biggest legibility win; existing fallback polygon is visibly cruder than the sprite ships
2. **Death-explosion sprite** (single shared asset, OR per-ship-class variants) — current "ship just vanishes" is the most noticeable visual gap
3. **Impact-burst sprite** (single shared asset, tinted by projectile color) — small expanding puff
4. **Heavy plasma-orb sprite** — `charged` pattern is used by 3 flagship-tier ships; current "big circle" doesn't carry the weight
5. **Saw-blade disc sprite** — `lawnmower_blade` for Proto-Qor-Ah + Scout-with-Lawnmower-Disc mod; current 4-point-star polygon reads as cheap
6. **Long-bolt lance sprite** — `lance` for Androsynth, Thinn, Scout-with-Lance-Coil mod
7. **Homing plasmoid + comet-tail trail** — multiple ships
8. **Missile sprite** — Defender engine_seeker + Cleanser icepeedo + Scout-with-Homing-Mortar mod

### Wiring contract — what Combat chat will do once sprites land

When Image chat completes ship sprites: zero combat-chat work needed; they're picked up automatically by `_load_ship_sprite` via the pre-registered `SHIP_SPRITES` map.

When Image chat completes weapon-effect sprites: Combat chat will wire a new `PROJECTILE_SPRITES` map keyed by pattern (or by pattern + ship_id when needed for variant treatment) and a `_load_projectile_sprite` cached loader paralleling the ship-sprite path. Drop the files into a new dir (`assets/generated_drafts/firefly/tier1_projectiles/` or similar — Image chat picks the convention), then notify Combat chat which dir to wire. Combat chat will add the loader + render path in one pass.

### Acceptance — testing a sprite landed

After dropping a new ship sprite into `assets/generated_drafts/firefly/tier1_ships/ship_<id>.png`:

```bash
SDL_VIDEODRIVER=dummy python -m scz.testing.scripts walk_super_melee
```

Exit code 0 means the sprite loaded cleanly. To see it visually:

```bash
python -m scz.main --windowed
# Main menu → Super-Melee → pick the ship → watch a fight
```

The sprite should render rotated correctly (nose pointing in the direction of travel) and be visibly distinct from the procedural-polygon fallback.

### Status

- ☐ Open as of 2026-05-18 — informational reference; no specific outputs required from this entry. Action items are in the other 2026-05-17 sprite-roster entries.

---

## 🗂️ 2026-05-17 — CONSOLIDATED OPEN-WORK SUMMARY (start here)

> The list below is your **session checklist**. Each item links to a detailed entry further down in this doc. Process in roughly the order shown; species-art is the biggest workload. Mark each `✅ PROCESSED <date>` as you complete it, both here and in the detailed entry.

### High-priority — slice critical-path content

- [ ] **Burvixese world destruction cutscene** — Caster activation + moth-to-flame Others arrival + civilization consumed + Caster left standing on empty planet + Burv Broadcaster nodes scattered. Slice-defining catastrophic-witness beat
- [ ] **Taalo shield-tragedy reframe** (multi-asset) — fragment portrait (Horta-lineage; boulder-when-still / shamble-when-moving), home mountain landscape, contemplation-cove dialog backdrop, Shield activated state, Shield post-failure inert state, extermination cutscene, **post-Culling orbital planet view (looks ordinary; calcified bodies indistinguishable from rocks)**
- [ ] **Furling fur-everywhere aesthetic** — reprocess any existing Furling-interior imagery (Halia bridge, Mh-Lai station, Furling Scout interior, Council chambers) with the canonical fur-on-everything + translucent fur light-diffusers
- [ ] **Utwig Veils Falling** (3 assets) — comic rehearsal backdrop (priests alternating ablutions etc.), mass-mask-donning ceremony cutscene, post-doctrine Utwig portrait (SC2-era body)

### High-priority — new species art (5 species × 3-5 assets each = ~20 outputs)

- [ ] **Stelloth** — Tarvel-Three-Voices chord portrait (three-body mantis-stack with murrer cords) + Three-Voice Arc ship + super-giant trading post backdrop
- [ ] **Selvenne** — Brain-Coral Sanctum dialog backdrop + individual polyp portrait + memory-playback cinematic frame template
- [ ] **Mrokon** — Vrek-The-Eighth-Body puppet portrait + Operator bunker portrait + Mrokon's Stand surface + Hammer-Ship + **Hammer-Of-Refusal cutscene** (canonical SC2 dimpled-Vessel source)
- [ ] **Kovellim** — Ovala-Eight-Crossings elder portrait (knot-scars + cycle-cloak embroidery) + Eight-Knot Station exterior + receiving chamber interior + Crossing-Frigate exterior
- [ ] **Karavem** — Welcome Choir backdrop (12 in six-part harmony) + individual portrait + Aeris-Sing canyon-city + Aria-Skiff exterior
- [ ] **Lemmkin** — portrait (anthropomorphic squirrel, no fear) + Whirligig planet surface (canopy cities + visible cliff-mortality warning signs) + Lemmkin Skitter ship

### Filename migration (no new rendering needed)

- [ ] **Thinn rename** (was Planar) — rename `species_planar_blade_portrait.png` → `species_thinn_blade_portrait.png`; rename Firefly prompt file; update body text inside the prompt (Planar → Thinn, Planar Blade → Thinn Blade); update `_manifest.json`; update articulation.py identifiers; update gen_lore.py if Image-lane

### Design-chat requested visual upgrades

- [ ] **Combat-arena starfield backdrop** — `assets/combat/starfield.png` (1600×1000 or 3200×2000)
- [ ] **Hyperspace combat coaxial interference tunnel** — `assets/combat/hyperspace_tunnel.png` (512×512 alpha PNG)
- [ ] **Lander surface terrain textures** — 7 PNGs for terrestrial / ocean / rocky / desert / ice / primordial / volcanic

### Style direction quick-reference

- Stelloth: **cool pearl-grey + green-violet** — precise compositions
- Selvenne: **warm ocean-bioluminescence** — liquid compositions
- Mrokon: **stark grey + pale-blue accent** — blocky purposeful compositions; ledger-mark motif on bodies AND ships
- Kovellim: **weathered umber-bronze** — weighty archaeological compositions; knot-scar / coiled-ledger motif
- Karavem: **gold-cream-silver + plumage palettes** — graceful aerial / canyon compositions
- Lemmkin: **bright cheerful** — Pixar-readability, movement-suggesting poses, no menace
- Taalo: **slate-grey + violet-amber glow** — Horta-lineage; brave melancholy
- Thinn: **iridescent teal/violet/gold** — view-dependent refraction; the slipstream visual

### Subjective-feedback open requests (Testing chat findings — visual)

- Hyperspace map dim-tier contrast strong enough at fullscreen?
- HUD `resources NN% anomalies N` line legible against starfield?
- Badge colors (slate grey for DRAINED, muted green for VISITED) read clearly?
- Lander procedural-terrain textures look right for each planet type? (See `tools/manual_playtest_lander.md` checklist)

---

## 2026-05-17 — Combat-ship sprite roster gap (Design chat request)

**Origin**: Design chat. The combat roster grew from 11 to 17 ships this pass; 6 new ships have stat blocks + AI + special wiring but no sprite asset, so they fall back to the procedural-polygon silhouette in `_draw_ship`. The combat scene loads from `assets/generated_drafts/firefly/tier1_ships/ship_<id>.png` per the existing `SHIP_SPRITES` mapping in [src/scz/combat/scene.py](src/scz/combat/scene.py).

### Existing sprites (don't re-author — already shipped)

```
ship_furling_scout.png         ship_persuader_vessel.png      ship_arilou_skiff.png
ship_androsynth_cruiser.png    ship_cleanser_cruiser.png      ship_melnorme_trader.png
ship_defender_vessel.png       ship_mmrnmhrm_sentinel.png     ship_proto_urquan.png
ship_proto_qor_ah.png          ship_sentry_drone_47t.png
```

### Required new ship sprites (6 PNGs)

Same convention as existing: top-down nose-up, transparent background, ~512×512, square. Loaded via `SHIP_SPRITES` map; the engine rotates them around their center to face the ship's heading. Aim for similar visual weight to existing ships at typical viewport scale.

| File | Ship | Visual direction |
|---|---|---|
| `ship_compeller_vessel.png` | **Compeller Vessel** — Furling sub-faction (sedation/deception) | Furling-family silhouette like Persuader/Cleanser but with **tractor-array antennae or sedation-prong protrusions** at the bow. Heavier than Persuader, lighter than Cleanser. **Slate-grey + green accent** (the green sedation-arm motif). Pre-Cleanser-era Furling palette — still "we're here to help" but with restraints visible. Compellers carry tools, not weapons-first |
| `ship_mycon_podship.png` | **Mycon Podship** | Organic pod aesthetic — bulbous, *grown* not built. **Dark purple-red hull** (matches `primary_color=(200,90,130)`); fibrous surface texture; bio-luminescent veins; central plasmoid-emission aperture forward; defensive pod-spikes around the perimeter. SC2-canon Mycon look but in our era — *not yet awakened to full sentience but the biots are organizing into vessels* |
| `ship_utwig_jugger.png` | **Utwig Jugger** (pre-doctrine) | Heavy bipedal mask-craft aesthetic (the Utwig built ships before they devolved). Boxy, ceremonially-ornamented. **Heavy shield emitter prominent** — the iconic absorption shield is what they're known for. Sandy/cream hull `(180,200,160)` with green-tinged shield-edge visible. Reads "tank" |
| `ship_lemmkin_skitter.png` | **Lemmkin Skitter** | Already specced in detail in the existing Lemmkin Skitter entry of this doc. Cross-reference / share work where possible. Small angular, four-thruster, bright-color paint job, fast/fragile |
| `ship_thinn_blade.png` | **Thinn Blade** | Already specced in detail in the existing Thinn rename entry. Sail-craft, elliptical, pilot embedded along the spine, edge-on-thin |
| `ship_burv_broadcaster.png` | **Burv Broadcaster** *(REVISED 2026-05-19)* | **GIGANTIC BULLHORN** — the ship IS a flying loudspeaker. Conical mouth (the broadcast aperture) aimed forward; cylindrical body tapering back to a narrow grip + thin support struts for thrust nacelles. Copper-brass + crystalline accents (Burv Caster artifact aesthetic preserved). Inside the conical mouth: visible harmonic-resonator diaphragm. Wave-shaped venting along the body. Four-armed engineering accents still present as service-handles on the body. The silhouette should be **immediately readable as "literal bullhorn"** even at small scale — that's the entire visual joke. `silhouette="bullhorn"` in `src/scz/combat/ships.py`. Weapon (new 2026-05-19): full-arena-range slow curved resonance wave that grows + fades as it travels; immune to its own weapon |

### Optional bonus pass — weapon sprite library

Currently every projectile renders as a colored circle in `_draw_ship`/`_update_projectiles`. The engine has 12 distinct **primary patterns** that would benefit from signature sprites (or, more efficiently, signature *colors + glow rendering* — design's call). If Image chat has budget after the 6 ship sprites, signature sprites for the high-visibility patterns:

| Pattern | Used by | Sprite idea |
|---|---|---|
| `homing` | (Melnorme had it; reassigned) | Glowing orange plasmoid with comet tail |
| `bubble` | Androsynth | Translucent purple bubble, 16-24px |
| `returning` | Proto-Qor-Ah RHC | Saw-blade disc — spinning, metallic |
| `tier_plasma` | Melnorme | 3 size variants (small/medium/large) — same orange glow |
| `charged` | Defender / Mycon / Proto-Ur-Quan | Big slow plasma orb |
| `tracking` | Arilou | Hitscan laser beam (linear, not circular) |

(Lower priority than ship sprites. Design chat can render-improve later via gradient/glow draws if Image chat doesn't get to these.)

### Acceptance

For each new sprite: drop the PNG in the right path, launch `python -m scz.main --windowed --test walk_super_melee`, verify the ship renders with the new sprite (not the procedural polygon fallback) and reads cleanly at typical viewport scale.

### Status

- ☐ Open as of 2026-05-17
- Tag `✅ PROCESSED <date>` per file (or as a block once all 6 land)

---

## 2026-05-17 — **SLICE TERMINAL**: The 6 Endings cinematics

**Lore source**: `references/lore/the-endings.md` (NEW). The slice has 6 canonical endings ranging from Best to Disastrous. Each needs its own distinct cinematic with carefully differentiated tonal palette + content.

| Ending | Path | Tonal Palette | Content summary |
|---|---|---|---|
| **Best** | `tier1_cutscenes/cutscene_ending_best.png` (+ multi-frame Andromeda resettlement) | Warm gold-cream + Andromeda-promise indigo | Migration crossing opens; FULL fleet enters; Halia beside Steward (or memorial sigil); ALL Common Room bond-objects visible; multi-frame Andromeda resettlement (Kovellim 9th-knot scar, Karavem canyon-cities, Selvenne reef intact, Lemmkin archive unpacked, Stelloth artifacts accepted, Mrokon dead NAMED on memorial, Sevreth's Child humming, Forward + diaspora arguing cheerfully) |
| **Great** | `tier1_cutscenes/cutscene_ending_great.png` | Warm but slightly less saturated | Same structure as Best; Common Room bond-objects PARTIALLY visible; some crew arcs unfinished in epilogue |
| **Good** | `tier1_cutscenes/cutscene_ending_good.png` | Warm but COOLER; emptier compositions | Migration crossing opens; full alien fleet; Common Room named-crew alcoves PARTIALLY EMPTY; canonical *"home you arrive with is not the home you could have had"* |
| **Successful, at a cost** | `tier1_cutscenes/cutscene_ending_at_cost.png` | Cool greys + amber accents; warmth has RECEDED | Migration crossing opens; fleet visibly THINNER; some vessels missing; Selvenne reef sections lost; Karavem Andromeda perch-city slots empty; *professional-not-warm* bridge |
| **Unsuccessful** | `tier1_cutscenes/cutscene_ending_unsuccessful.png` (2-frame sequence) | Deep blues + violet; lonely | UNIQUE sequence — NOT Crossing-Opens. Steward escapes alone through crossing; cut to galaxy-consumed-forever visual (negative-black saturating the galaxy; faint glow of consumed stars; canonical *"galaxy as kitchen"* image); back to Steward alone in Andromeda |
| **Disastrous** | `tier1_cutscenes/cutscene_ending_disastrous.png` (multi-frame) | NEGATIVE-BLACK + harsh BLOOD-RED | UNIQUE darkest sequence. Steward alone at arrow-tip; attempts to negotiate (futile); transmits unilateral treaty; Others approach + consume ship + Steward; **blood-red runes spreading across star-fields imprinting the treaty onto galactic substrate**; Others eat galaxy at leisure; ends on screen-fade with stark *"Good job."* punchline text |

### Disastrous-ending special visual notes

- **Not funny in the visual register** — the dark comedy is in the *narrator text*, NOT the imagery. Visuals must be UNSETTLING.
- **Treaty-imprint imagery**: blood-red runes spreading across star-fields; galactic substrate visibly stained; permanent legal-claim aesthetic reading as both *bureaucratic* AND *cosmic-horror*
- **Steward's death is IMPLIED, not depicted** — show Others approaching the ship; cut away; show aftermath (blood-imprint on the galaxy). Avoid gore.
- **The *"Good job."* text** is the canonical visual punchline. Stark white text on negative-black; no animation. Holds for several seconds before fade.

### Andromeda resettlement frames (Best/Great only — and reduced in Great)

Each saved species's resettlement should be visible:
- Kovellim Crossing-Frigates docked; Ovala-Eight-Crossings receiving 9th knot-scar
- Karavem perch-cities being constructed in Andromeda canyon-worlds
- Selvenne reef-sections lowered into Andromeda ocean-worlds
- Lemmkin archive unpacked + read (canonical earlier-than-expected "found Precursor caches")
- Stelloth artifact-archive accepted by post-Migration galactic culture
- **Mrokon dead being NAMED** at a memorial — canonical: their dead are *not anonymous* in the new galaxy
- Furling Persuader / Hider / Defender flag-raising at new home
- Halia (if alive) giving first Andromeda speech

### Common Room bond-object density

Best/Great/Good endings should show the Common Room as part of the epilogue (canonical *"the room you've lived in becomes the room you arrive with"*). Bond-object density visibly differentiates these endings.

### Style differentiation

4 successful endings share a visual vocabulary (Migration fleet imagery, crossing-corridor iridescence, Andromeda promise) but differ in *temperature and density*. The 2 failure endings are visually DISTINCT scenes — not "lesser versions" of success.

### Status

- ☐ Open as of 2026-05-17 — **slice terminal**. The slice's final visual investment.

---

## 2026-05-17 — **SLICE CLIMAX**: The Final Conflict — fleet-vs-fleet at the Rainbow Worlds arrow-tip

**Lore source**: `references/lore/the-final-conflict.md`. Quest: `the_final_conflict`. Slice's largest single visual investment after the Fall of Mh-Lai.

### Required art

| Asset | Path | Spec |
|---|---|---|
| **Drev-Tok Velt-Mar — Sa-Matra Prototype bridge portrait** | `tier1_portraits/npc_drev_tok_velt_mar.png` | Furling Defender Commander; ~70 years; veteran; cold composed authority. Heavy Defender uniform (canonical militaristic style; contrasts with Halia's warmer Persuader cloak). Three Defender-operation campaign-marks ("Three Hammers"). Sa-Matra Prototype command bridge background — hard lines, military instrumentation, NOT Persuader fur-warmth. Mood: *2 years of grievance held in formal stillness* |
| **Sa-Matra Prototype exterior** | `tier1_ships/ship_sa_matra_prototype.png` | Massive Furling Defender warship — heavy armored hull; canonical Defender geometric pattern; visible primary energy-lance emitter along the spine. Reads as *peak Furling military engineering*. Three structural sections (foreshadowing Phase 2 split). Dark Furling metalwork + Defender crimson |
| **Sa-Matra Phase 2 multi-vessel form** | `tier1_ships/ship_sa_matra_prototype_split.png` | The Prototype split into 3 coordinated sub-vessels; central coordination vessel as the linkage hub; combat-ready geometric formation |
| **Drev-Tok's coalition fleet** | `tier1_cutscenes/cutscene_final_homesteader_fleet.png` | Homesteader fleet at arrow-tip; Sa-Matra Prototype center; flanking Defender Vessels; conditional elements based on slice flags (Mrokon Hammer-Ships if Mrokon-Eliminated; Burvixese Broadcasters if sabotaged; Thinn slipstreams if not migrated; Cleanser-vessel with Halia aboard if Cleanser-Fall) |
| **Migration fleet arrival** | `tier1_cutscenes/cutscene_final_migration_fleet.png` | Migration fleet completing formation; every species's vessels in formation — Hearth-of-Iron center; Kovellim Crossing-Frigates ahead; Karavem Aria-Skiffs; Selvenne Tank-Ships; Stelloth Three-Voice Arc; Mmrnmhrm Sentinel-Loop Cradles; Androsynth Refugee Fighters; migrant-contingents; Steward's ship at center |
| **Drev-Tok's first transmission** | `tier1_dialog_backgrounds/bg_drev_tok_address.png` | Bridge of Sa-Matra Prototype; Drev-Tok at command table; Council-channel broadcast indicator; mood: *2 years culminating in this single moment* |
| **Diplomatic-rare conversion frame** | `tier1_cutscenes/cutscene_drev_tok_converts.png` | Moment Drev-Tok sees the marked Others' Vessel beside Steward's ship; close shot of his face — recognition + doctrinal collapse + *"my doctrine was wrong"*; rare frame; only in hidden best-outcome branch |
| **The dimensional crossing opens** | `tier1_cutscenes/cutscene_crossing_opens.png` | Rainbow Worlds align; dimensional corridor to Andromeda opens — shimmering iridescent passageway; Andromeda faintly visible at far end; Migration fleet entering in canonical order (Kovellim first; Karavem singing; Selvenne slow; Furlings; migrants; Steward LAST) |
| **The Steward enters last (canonical honor frame)** | `tier1_cutscenes/cutscene_steward_enters_corridor.png` | Steward's Furling Scout at threshold of dimensional corridor; Halia visible on bridge (if alive) OR memorial sigil (if dead); Migration fleet ahead in corridor; empty galaxy behind |

### Style direction

- **Drev-Tok's aesthetic** = Defender military; dark metalwork, hard geometric lines, deep crimson accents — *contrasts deliberately with Persuader warmth*. He is NOT the bad guy; he is the *opposite faction*. Visual respect required.
- **Sa-Matra Prototype** = *peak Furling engineering* — Drev-Tok's pride is justified at the engineering level; the ship is gorgeous; canonical visual story is *what the Furlings could have built if they had decided to fight*
- **Two fleets in contrast**: Migration fleet = varied, multi-species, fragile-and-strong-together; Defender coalition = uniform, military, focused, smaller. The visual asymmetry IS the canon.
- **Dimensional crossing**: iridescent, beautiful, the slice's payoff visual. Andromeda glimpse subtle — a *promise*, not a clear shot.

### Status

- ☐ Open as of 2026-05-17 — **slice-climactic**. Single largest cinematic dispatch.

---

## 2026-05-17 — **MAJOR**: The Fall of Mh-Lai cinematic (slice's biggest emotional beat)

**Lore source**: `references/lore/the-fall-of-mh-lai.md` (NEW). Mid-game scene; Mh-Lai (Furling home) is consumed by the Others. Quest FSM `the_fall_of_mh_lai` in `tools/quest_inventory.csv`.

This is **the slice's biggest single visual moment**. Cinematic depicts the Furling home falling. Multiple frames needed; emotional weight is the point.

### Required cinematic frames

| Frame | Path | Spec |
|---|---|---|
| **Halia's first transmission portrait** | `tier1_cutscenes/cutscene_halia_first_transmission.png` | Commander Halia at the Council chamber's command-table, mid-transmission. Furling fur-aesthetic; Persuader insignia visible on her cycle-cloak; she is *composed but knows*. The Persuader-priority channel indicator visible at the corner of frame. Mood: calm authority + intimate care. **This is the Steward's friend.** |
| **Mh-Lai pre-fall orbital view** | `tier1_planets/bg_mhlai_pre_fall.png` | Mh-Lai from orbit — habitable terrestrial world with visible canopy-cities + the station structure visible in low orbit. Migration vessels at standby orbit (~6 vessels visible). Mood: *the home that's about to be lost*. Last-time-it-looks-this-way. |
| **The dimensional ripple approaching** | `tier1_cutscenes/cutscene_others_approach_mhlai.png` | Mh-Lai's outer halo. The canonical negative-black distortion of the Others crossing through dimensional space toward the planet. Slow, structured, massive. **Not chaotic — orderly and inevitable.** The Migration vessels in foreground beginning to pull away. |
| **The Council chamber (mid-evacuation)** | `tier1_dialog_backgrounds/bg_mhlai_council_chamber_evac.png` | Interior of the Council chamber during evacuation. Halia visible at the command-table; Persuader / Hider Council members evacuating through side-passages; the Defender chief in her Sa-Matra-prototype armor refusing to leave. The chamber's *data-archive racks* visible — they will be sealed in the final-state seal before the fall. Mood: *controlled urgency*. |
| **Atmospheric flicker — the moment the Others cross** | `tier1_cutscenes/cutscene_mhlai_atmospheric_flicker.png` | Planetary aurora as the Others' dimensional substrate intersects Mh-Lai's atmosphere. The aurora is *beautiful* — bright violet-amber bands. This is the last beautiful moment Mh-Lai will produce. |
| **The fall (in waves)** | `tier1_cutscenes/cutscene_mhlai_consumed.png` (or sequence) | Mh-Lai's atmosphere darkening in waves as the Others' substrate intersects the planet's biosphere. Cognition extinguishes en masse. **NO debris. NO rubble.** The planet is *less than it was*, smoothed over by the Others' passage. The Migration vessels watching at safe distance. **The slice's quietest cinematic by design.** |
| **Halia's final transmission** | `tier1_cutscenes/cutscene_halia_final_transmission.png` | Halia in the Council chamber's last moments. Aurora visible through the chamber window behind her. She speaks slowly. The data-archive racks behind her glow with final-state seal activating. **One of the slice's most important canonical images.** |
| **Mh-Lai post-fall orbital view** | `tier1_planets/bg_mhlai_post_fall.png` | The empty space where Mh-Lai was. Faint debris of the *Hearth-of-Iron-style derelict orbital infrastructure* — but no planet. The sun's light reaches through to where the planet used to be. **The canonical SC2-era image** if any archaeologist of that era ever flies through this cluster — it looks like a star with a derelict ring-station and nothing else. |
| **Hearth-of-Iron exterior** | `tier1_ships/ship_hearth_of_iron.png` | The Migration flagship — large, blocky, *clearly a home now*. Furling insignia + Persuader markings + the canonical Mh-Lai memorial sigil (added post-fall — a stylized circle with the fur-pattern of the lost planet's surface). The exterior should read as *home-on-the-move*. |
| **Hearth-of-Iron interior (new home-base scene)** | `tier1_dialog_backgrounds/bg_hearth_of_iron_concourse.png` | The Migration flagship's main concourse — replaces Mh-Lai Station as the player's home base post-fall. Mev-Tar Lwen-Tar's transferred Unzervalt tooling visible in background; Council-remnant chamber visible; canonical Furling fur aesthetic but with *grief markers* (Mh-Lai memorial sigils on walls; small mourning displays). |

### Halia branch-state portraits

The cinematic outcome depends on which branch the player chose. Three Halia variants needed:

- `tier1_avatars/halia_alive_persuader_free.png` — Halia at her Hearth-of-Iron command position; alive; *quietly carrying it*; Persuader-faction in full leadership. (Race-success branch)
- `tier1_avatars/halia_dead_remembered.png` — formal Persuader-faction memorial portrait; framed; on a wall in Hearth-of-Iron. (Race-doomed / Don't-race branches)
- `tier1_avatars/halia_alive_cleanser_supervised.png` — Halia at a Cleanser-faction-protocol formal stance; *visibly miserable*; Cleanser channel-indicator visible at the corner. (Cleanser-acceleration branch)

### Style direction

- **Cool palette throughout** — blue-violet, slate, near-black; the warmth of Mh-Lai is *what's being lost*; the visual register cools as the cinematic progresses
- **Furling-fur aesthetic ONE LAST TIME** in the Council chamber interior — the canonical fur-everywhere makes the chamber feel *home-like* in a way that hurts when it falls
- **The Others = negative-black distortion + non-Euclidean shapes**, consistent with Taalo / Burvixese cinematic visuals
- **No combat language** — this is not a battle scene; it's a *witness* scene. The Furlings can't fight the Others. The cinematic should never imply *active resistance*.
- **Halia's gravity** — every portrait of her should hold the viewer. She is the Steward's *friend* canonically; her composure under doom is the slice's emotional anchor

### Status

- ☐ Open as of 2026-05-17 — **slice-critical**. Highest priority of any cinematic work. The slice does not land emotionally without this.

---

## 2026-05-17 — **MAJOR**: Crew Common Room scene art (Aaron's direct dispatch)

**Lore source**: `references/lore/crew-common-room.md` (NEW) — full canon doc. **Read it.** It spells out per-crew alcove canonical postures, bond-objects, fur aesthetic, layout.

This is **the slice's first major ship-interior scene** — the Common Room is where the player goes to *find their crew* between missions. It needs to feel **warmly lived-in** with the Furling fur-everywhere aesthetic at maximum saturation.

### Master backdrop — required first

| Asset | Path | Spec |
|---|---|---|
| **Common Room interior — empty (master backdrop)** | `tier1_dialog_backgrounds/bg_common_room_empty.png` | ~8m × 5m × 3m room interior, isometric or three-quarter view; long central table with bench seating (capacity 8); five named-crew alcoves arranged around the perimeter; Steward's bunk corner; generic-crew rotating alcove. **FURLING FUR EVERYWHERE** per canon — long-luxurious-shag on benches (mammoth/musk-ox texture), short-dense-pile on table-surface (mole/otter), translucent pale-fur diffusers on light fixtures producing warm amber-tinted lighting with fibrous shadow edges, fur-textured handhold-height wall grips, ceremonial-soft-underfur on Steward's bunk. Empty of crew + bond-objects (those render as overlay sprites). Resolution: 1920×1080 or higher. Mood: *warm, textural, biologically-cared-for*. Color palette: warm browns (sand, cinnamon, oat, umber) + amber light-diffusion + soft shadows |

### Per-alcove crew portrait + posture art (5 named crew)

Each named crew needs a **standing portrait** showing them in their canonical alcove posture, rendered as a sprite that overlays on the master backdrop. The lore doc spells out each canonical posture precisely.

| Crew | Asset | Posture |
|---|---|---|
| **Mraka Yenn-Sa** | `tier1_crew_room/crew_pilot_in_alcove.png` | Standing at the alcove's small window, looking out at hyperspace patterns; pose suggests *quiet attention to what's outside* |
| **Bren-Vor Telcas** | `tier1_crew_room/crew_weapons_in_alcove.png` | Seated on bunk-edge, weapons-cleaning kit deployed, cleaning a kinetic-rifle component (canonically the *eighty-seventh* time he's cleaned this specific part) |
| **Yelena Lwen-Tar** | `tier1_crew_room/crew_engineer_in_alcove.png` | At her workbench, mid-repair; tools visible; the workbench is the *densest object-cluster in the Common Room* canonically; her tail-tip is in motion (Furling gesture) |
| **Mira-Rou Halve-Tel** | `tier1_crew_room/crew_medic_in_alcove.png` | At her medbay-window observation post, taking notes; glass amphora visible on shelf nearby; serene-but-focused expression |
| **Tarven Olwen-Sa** | `tier1_crew_room/crew_navigator_in_alcove.png` | Seated cross-legged on bunk with at least 2 log-readers open; mid-thought; the eternal tea-cup nearby |

### Per-alcove bond-objects (conditional render; ~15-20 small sprites)

Each named-crew alcove has a personal shelf that accumulates bond-objects across the slice. Each object is a small sprite (~80×80px to ~150×150px) that renders only when its enabling flag is set.

**Mraka's alcove shelf** (port-forward corner):
- `obj_mraka_drifter_medals.png` — small medal display (3 cluster-cup wins); ALWAYS visible
- `obj_mraka_unnamed_family_portrait.png` — framed Olwen-Veth family portrait (faces visible but Mraka does not name them aloud); ALWAYS visible
- `obj_mraka_soren_drive_component.png` — saved-piece-of-Soren's-ship; visible only if `mraka_sq_complete=True`
- `obj_mraka_olwen_veth_clan_marker.png` — small Olwen-Veth clan-emblem (gift from Soren); visible only if `mraka_sq_complete=True`

**Bren-Vor's alcove shelf** (starboard-mid):
- `obj_brenvor_velt_ra_photo.png` — Velt-Ra photograph (face turned slightly away from camera); ALWAYS visible
- `obj_brenvor_firing_rule_notebook.png` — personal annotation notebook on combat-restraint; ALWAYS visible
- `obj_brenvor_velt_ra_journal.png` — Velt-Ra's journal, closed, with a small Persuader pin on top; visible only if `brenvor_sq_complete=True`

**Yelena's alcove shelf** (starboard-aft):
- `obj_yelena_family_photo.png` — Mev-Tar + young-Yelena with oversized wrench; ALWAYS visible
- `obj_yelena_tool_rack.png` — 17 alphabetized specialized tools; ALWAYS visible
- `obj_yelena_unzervalt_floor_fragment.png` — fragment of the last Scout's cradle; visible only if `yelena_sq_complete=True`
- `obj_yelena_korven_buckle.png` — Korven's surviving tool-belt buckle; visible only if `yelena_sq_complete=True`

**Mira-Rou's alcove shelf** (port-aft):
- `obj_mira_amphora.png` — glass amphora with heirloom biot-fragment; ALWAYS visible. **TWO STATES**: `obj_mira_amphora_quiet.png` (default) vs `obj_mira_amphora_alive.png` (if `sevreth_child_alive=True` — clearly bioluminescent presence inside)
- `obj_mira_olune_portrait.png` — great-grandmother Olune Halve-Tel portrait; ALWAYS visible
- `obj_mira_shear_repair_kit.png` — portable shear-repair fab pattern; ALWAYS visible
- `obj_mira_hider_citation.png` — Furling Hider citation; visible only if `mira_sq_complete=True AND heirloom_suppressed=True`

**Tarven's alcove shelf** (port-forward-mid):
- `obj_tarven_prior_steward_miniatures.png` — row of 7 prior-Steward portrait miniatures; ALWAYS visible
- `obj_tarven_tea_collection.png` — multiple tea cups (canonical inexhaustible supply); ALWAYS visible
- `obj_tarven_iren_vor_cache_open.png` — Iren-Vor's recorded-voice cache, proudly displayed; visible if `tarven_sq_complete=True AND iren_vor_archive_unlocked=True`
- `obj_tarven_iren_vor_cache_locked.png` — same cache with a small physical lock-seal; visible if `tarven_sq_complete=True AND iren_vor_secret_kept=True`

### Special bond-object: Sevreth's Child (allow-emergence branch)

`tier1_crew_room/character_sevreths_child.png` — tiny bioluminescent presence inside the amphora; bright enough to be visible from across the Common Room; faint chromatic glow; readable as both biot and being. Visible only if `sevreth_child_alive=True`.

### UI element sprites

| Sprite | Path | Spec |
|---|---|---|
| **Notification badge ("!")** | `tier1_ui/notification_badge.png` | Small Furling-cyan "!" with subtle pulse-animation; readable at small size; non-alarming aesthetic |
| **TALK prompt** | `tier1_ui/talk_prompt.png` | Button-icon + "TALK" label; appears on cursor-hover over crew member; cyan-on-warm-background; cancellable look |
| **Banter bubble template** | `tier1_ui/banter_bubble.png` | Speech-bubble style with Furling-fur-textured border; semi-translucent body; readable text area |

### Style direction

- **Warmly lived-in** — the room should feel *occupied*, not staged. Bond-objects should look slightly *used*, not pristine. Yelena's tool-rack should have one tool slightly out of order. Tarven's tea cups should have one with the dregs still in it.
- **Furling fur EVERYWHERE** is the canonical palette-shaper — even the floor has short-dense-pile (the Furlings dislike bare floors)
- **Warm amber lighting** with fibrous shadow-edges — the canonical fur-diffuser look
- **Slight asymmetry** in the alcove arrangement — the room is *grown into*, not architecturally-perfect
- **Per-crew alcove fur palettes** match each crew's signature color (Mraka weathered umber, Bren-Vor muted grey-blue, Yelena cinnamon-and-cream, Mira-Rou pale-green-and-white, Tarven deep brown)

### Implementation phasing

- **Phase 1 (slice MVP)**: master backdrop + 5 crew portraits + UI sprites + ALWAYS-visible bond-objects (~10 sprites total)
- **Phase 2 (post-MVP)**: conditional bond-objects (~10 sprites; render based on side-quest flags) + Sevreth's Child special-case
- **Phase 3 (variation layer)**: per-crew "mood" portrait variations based on crew_morale stat

### Status

- ☐ Open as of 2026-05-17 — first ship-interior scene; substantial scope but high payoff for slice's emotional texture

---

## 2026-05-17 — Forward, the Thinn Rebel (alternative weapons officer)

**Lore source**: `references/lore/crew-recruitment-quests.md` section "2a. Forward — Thinn Rebel". The slice's *only* Thinn ever to face forward and use singular pronouns. Mutually exclusive with Bren-Vor for the weapons-officer slot.

### Required art

| Asset | Path | Spec |
|---|---|---|
| **Forward — at Mh-Lai docks (recruitment portrait)** | `tier1_portraits/crew_weapons_officer_thinn_forward.png` | Iridescent teal-violet-gold ribbon-body, ~2m tall, **FORWARD-FACING toward the camera** (canonical — he is the only Thinn ever to do this; this single visual fact is the entire character in one frame); slipstream curling around him; optical-point face with ~12 dark points along his upper edge looking *directly* at the viewer; pose suggests *patient determination*. Mh-Lai docks visible faintly behind him. Mood: *cheerful rebellion*. |
| **Forward — Common Room alcove (in posture)** | `tier1_crew_room/crew_weapons_thinn_in_alcove.png` | Forward in his weapons-officer alcove; standing forward-facing; the iridescent-mineral wall-panel he installed (Thinn-aesthetic overlay on Furling fur base) visible; his vertical resting-rack bunk; his "Forward" emblem (a single forward-arrow) on the alcove plate |
| **Forward's bond-objects** | `tier1_crew_room/obj_forward_*.png` | (1) `obj_forward_perpendicular_diagram.png` — paper sheet with 7 arrows in different directions and a handwritten *"this one"* note; (2) `obj_forward_shed_ribbon.png` — single Thinn ribbon-fragment from Spire (iridescent); (3) `obj_forward_emblem.png` — single forward-arrow; (4) `obj_forward_spire_rock.png` — small parting-gift from troupe (post-confrontation branch); (5) `obj_forward_troupe_letter.png` — paper-letter addressed *"to Forward"* in multi-Thinn handwriting (post-quiet-goodbye branch); (6) `tier1_crew_room/character_thinn_diaspora_far_slope.png` and `character_thinn_diaspora_lower_bench.png` — the two additional Thinn that join Forward in the confrontation branch (standing edge-on per their preserved doctrine, contrasting with Forward's forward-facing) |
| **Forward's side-quest cinematic — Spire troupe** | `tier1_dialog_backgrounds/bg_spire_troupe_encounter.png` | Spire's upper-atmosphere habitat; ~20 Thinn troupe-members visible, all edge-on (mostly invisible per canon — see them as faint chromatic slipstreams curling around the perch-platforms); Forward in foreground forward-facing; the visual story is *one species, two doctrines, both probably wrong* |

### Style direction

- **Forward's iridescence**: same canonical Thinn teal/violet/gold view-dependent shift, but his ribbon-body should feel *slightly more saturated* than canonical Thinn (canonically because he's the only one anyone has ever really *seen*; the rest of the species is always edge-on)
- **Forward-facing canon is the entire character**: every frame of Forward, his body should be unambiguously *facing the viewer*. The only character in the entire slice who is consistently full-broadside instead of three-quarter or edge
- **The troupe (when shown)**: render the troupe-members as *barely-there iridescent slipstreams* — edge-on canonical invisibility; the viewer should have to *look* to see them; the visual joke is that Forward stands out spatially while *being literally 2D the same as them*

### Cross-reference

- Mutually exclusive with Bren-Vor's weapons-officer alcove art (covered in prior Common Room dispatch). If Forward is recruited, his alcove renders; if Bren-Vor is recruited, his alcove renders. Same slot, different content.

### Status

- ☐ Open as of 2026-05-17

---

## 2026-05-17 — Crew side-quest supporting NPCs (5 new portraits)

**Source**: `references/lore/crew-recruitment-quests.md` "Backstories, Personalities, Side-Quests" appendix. The 5 crew side-quests introduce new supporting NPCs the player meets. All Furling unless noted.

| NPC | Quest | Visual notes |
|---|---|---|
| **Soren Kel-Var** | Mraka's "The Last Race" | Furling Drifter; ~40 Furling years; weathered (12 years on the docks since Mraka recommended-against-him); cycle-cloak with single Drifter's Circuit emblem; carries a defeated-but-honest demeanor; the canonical "Mraka's rival" face |
| **Karol-Vere Belt-Tar** | Bren-Vor's "The Aimer's Verdict" | Furling Cleanser officer; formal Council uniform; composed and procedurally confident; the cover-up is *under* the composure (visible only in micro-expressions); ~55 Furling years; weathered authority |
| **Mev-Tar Lwen-Tar** | Yelena's "The Last Hull" | Furling Senior Mh-Lai assembly chief; ~50 Furling years; Mender's tool-belt with ~30 specialized tools; warm, tired, *emotionally weighted* (her husband Korven died years ago; her factory is decommissioning); strong family resemblance to Yelena |
| **Iren-Vor Olwen-Veth** *(flashback only)* | Tarven's "The Erased Logs" | Deceased prior Steward (50 years before slice); shown only in cache-recording flashback frame; ~45 Furling years at recording time; calm and tired; *carries the weight of a secret she chose not to share*. Olwen-Veth clan markings (the clan Mraka mourns) |
| **Sevreth's Child** *(allow-emergence branch only)* | Mira-Rou's "Deep Child's Cradle" | Tiny biot-class sentient being; ~5cm; bioluminescent; lives in Mira-Rou's amphora on the medbay counter; communicates via chemical signals + faint sub-audible humming; the canonical "first Halve-Tel-hosted sentient biot" |

### Style direction

- **Soren**: weathered ochre-tan; defeated dignity; he should read as *the man who got it wrong twelve years ago and remembers*
- **Karol-Vere**: cold formal grey-blue Cleanser uniform; *composed but not warm*; the kind of face Persuaders dislike at first sight
- **Mev-Tar**: warm brown work-clothes; tool-belt prominent; *family-warm* in body language but visibly tired at the slice's timing (her factory is dying)
- **Iren-Vor (flashback)**: rendered with a *slight desaturation* + *aurora-edge* indicating "this is a recording from 50 years ago"; clan-cloak with Olwen-Veth markings (deep blue-greens) cross-referencing Mraka's quest content
- **Sevreth's Child**: tiny + delicate + *clearly alive*; bioluminescent ribbon-cilia inside the amphora; readable as both *biot* and *being*

### Status

- ☐ Open as of 2026-05-17
- These are *secondary* NPCs (single-quest appearances); ship the main slice-species portraits first, then come back to these

---

## 2026-05-17 — Two new Precursor-faction species: Kovellim + Karavem (toward Aaron's 8+8 species target)

**Canon sources**: `species-the-kovellim.md`, `species-the-karavem.md`. Both Precursor-faction (Migrating). The Precursor-side now has its 8 species: Arilou, Androsynth, Mmrnmhrm, Stelloth, Selvenne, Melnorme, Kovellim, Karavem. (Plus Homesteader 8: Slylandro, Chenjesu, Taalo, Burvixese, Utwig, Thinn, Lemmkin, Mrokon. Plus Others. Plus Furlings.)

### Kovellim — required art

| Asset | Path | What |
|---|---|---|
| **Ovala-Eight-Crossings (elder portrait)** | `tier1_portraits/species_kovellim_elder.png` | Tall ~3-4m bipedal humanoid; weathered ochre-tan skin with darker umber **knot-scars** (count eight visible scars across cheekbones / shoulders / hands; each scar is a raised coil ~3-8cm); **deep-set eyes** (nearly recessed caves — bone-remodeling from repeated crossings; the visual effect is gravity-in-the-face); deep cycle-cloak with extraordinarily detailed embroidery (the cloak is a literal family migration genealogy in cloth-form, 8 crossings recorded). Mood: *warm gravity*, the weight of millennia held gently. Eyes catch light from the inside. |
| **Eight-Knot Station exterior** | `tier1_planets/bg_kovellim_eight_knot_station.png` | Deep-space station in a halo of small asteroids; the station itself has **eight visible structural rings** (one per crossing); each ring shows wear-patterns from prior use; the asteroid-halo orbits in slow synchrony. Mood: *prepared, weathered, calm*. |
| **Receiving chamber interior** | `tier1_dialog_backgrounds/bg_kovellim_chamber.png` | Ovala's receiving chamber — circular, low-lit, cycle-cloaks hanging on the walls (each one a family genealogy in embroidery); tea-service in foreground (leaves from a prior galaxy, canonical); Ovala seated in her receiving chair; deep window showing hyperspace-aligned dimensional patterns. |
| **Kovellim Crossing-Frigate exterior** | `tier1_ships/ship_kovellim_crossing_frigate.png` | Stout migration vessel; thick armored hull with visible *coiled markings* where prior Cycle-Fold uses have scarred the ship (each scar a ship's-own record); warm umber-bronze color palette; not elegant but *durable*. |

### Karavem — required art

| Asset | Path | What |
|---|---|---|
| **Welcome Choir backdrop (dialog scene)** | `tier1_dialog_backgrounds/bg_karavem_welcome_choir.png` | A perch-city cliff-edge — ~12 Karavem in six-part harmony arrangement, **each in regional plumage** (western golden-rust, eastern pale-cream-and-sage, highland deep-indigo with silver tips); vast canyon-cliff backdrop with morning light; the Karavem are *visibly singing* (wing-flexed, throat-organs prominent at the front of the neck). Mood: *warm welcome amplified by natural acoustics*. |
| **Individual Karavem portrait** | `tier1_portraits/species_karavem_individual.png` | Single bipedal humanoid ~1.5m with large feathered wings folded against the back; soft feathered body in plumage palette; complex throat-organ at the front of the neck; wide-set eyes (color shifts per mood — golden by default, bright yellow when delighted, red-amber when contemplative, pale silver when grief-singing); delicate four-fingered hands held in conversational gesture. |
| **Aeris-Sing canyon-city backdrop** | `tier1_planets/bg_aeris_sing_canyons.png` | Vast canyon walls carved with terraced perch-cities; bridges between cliffs; slow-stellar-rotation lighting (long shadows; 40-hour day); bioluminescent moss on certain cliff-faces glowing at twilight; **acoustically-resonant architectural features visible** — focused cliffs, baffled walls, amphitheater geometry. |
| **Karavem Aria-Skiff exterior** | `tier1_ships/ship_karavem_aria_skiff.png` | Stylized **bird-of-prey silhouette**; long glittering wings (cosmetic, not for flight in space); main hull elegant and slim; warm gold-cream-silver color palette; reads as *artistic expression in spaceframe form*. |

### Style direction across both

- **Kovellim**: warm umber-bronze + ochre-tan; *weighty* compositions; archaeological details (knot-scars on bodies, ledger-knots on ships); the visual story is *survival across deep time*
- **Karavem**: gold-cream-silver + plumage-rich greens/indigos; *graceful* compositions; aerial / canyon geometry; the visual story is *song-shaped culture*

### Status

- ☐ Open as of 2026-05-17
- Tag `✅ PROCESSED <date>` per species as art lands

---

## 2026-05-17 — Three new species: Stelloth + Selvenne + Mrokon (creative-pass authoring)

**Canon sources**:
- `references/lore/species-the-stelloth.md` — three-body chord-beings; Bargainers; Precursor-faction artifact-traders
- `references/lore/species-the-selvenne.md` — planet-scale coral hive-mind; Long-Memories; experiential memory archive (touch transmits qualia)
- `references/lore/species-the-mrokon.md` — Defiant warrior-puppet operators; Hammer-Of-Refusal kinetic-impact doctrine that canonically marks the Others

All three replace placeholder rows in the species spreadsheet. All three have full quest FSMs in `tools/quest_inventory.csv`. **Go exotic** was the brief; the body plans deliver: chord-beings with three timescales, coral reefs with qualia-transfer, puppet-operators with expendable bodies.

### Stelloth — required art

| Asset | Path | What |
|---|---|---|
| **Tarvel-Three-Voices chord portrait** | `tier1_portraits/species_stelloth_chord.png` | Three mantis-like bodies linked by braided biological cords (the *murrer*); dark pearl-grey carapace with green-violet iridescent sheen; bodies arranged in choreographed-tripartite pose. **Speaker** (front, normal-sized eyes, vertical chitinous mouth-slit); **Witness** (side or upper, HUGE multifaceted eyes, head-mounted cognition-crystals visible, no mouth); **Counter** (rear, smaller eyes mostly closed, abdomen patterned with *ledger-marks* — scribed shell-history of past contracts honored/broken). Cords connecting them glow faintly harmonic-yellow when the chord is aligned |
| **Three-Voice Arc (trading vessel)** | `tier1_ships/ship_stelloth_three_voice_arc.png` | Elegant elongated craft; three sections linked by visible tethers (mirroring the chord-body morphology); each section semi-independent; three-fold asymmetric design; muted pearl-grey hull with green-violet accents |
| **Super-giant trading post backdrop** | `tier1_dialog_backgrounds/bg_stelloth_supergiant_post.png` | A different super-giant from the Melnorme — distinct stellar context (suggest a redder super-giant; the Stelloth like wavelengths around ionized iron); their Stelloth Beacon as a visible artifact orbiting nearby (a small structure broadcasting their canonical quasispace pattern) |

### Selvenne — required art

| Asset | Path | What |
|---|---|---|
| **Brain-Coral Sanctum (dialog backdrop)** | `tier1_dialog_backgrounds/bg_selvenne_sanctum.png` | Cathedral-scale brain-coral structure on the Vellumar seabed; **bioluminescent in slow chromatic waves** (purple/cyan/chartreuse polyp colors migrating across the surface as memories transit); rays of warm Vellumar sunlight penetrating ~50m down; reef-fish-analogues swimming through; a Furling submarine platform docked at the periphery (suggesting scale and visitation context) |
| **Individual Selvenne polyp portrait** | `tier1_portraits/species_selvenne_polyp.png` | A single ~5cm polyp with tentacle-cilia extended; slow chromatic bioluminescent glow; framed against velvet-dark background to highlight the colors; the polyp should read as *intelligent* despite being tiny — sense of presence in a small body |
| **Memory-playback cinematic frame style** | `tier1_cutscenes/memory_playback_frame_template.png` (style reference) | Distinct visual treatment for the moment a polyp transmits qualia to the Steward: the frame should have an *aurora-edge* (chromatic shimmer around the border) indicating "this is a Selvenne memory-replay"; the central image is a flashback to some ancient species's POV moment. This is a TEMPLATE / style guide — the actual playback frames are per-memory and per-species, but they all share the aurora-edge styling |

### Mrokon — required art

| Asset | Path | What |
|---|---|---|
| **Vrek-The-Eighth-Body puppet portrait** | `tier1_portraits/species_mrokon_puppet.png` | Heavy-armored bipedal warrior, ~2.3m; ceramic-composite armor in mid-grey with **scarred ledger-marks** along chest and shoulders (8 ledger-marks tallying previous puppet-deaths); **pale-blue glowing deep-link harness** at the back of the neck; kinetic-rifle held formally across the body; pose: *patient readiness*, not aggression; the helmet has eye-slits but no visible biological face |
| **Operator portrait (bunker interior, rare)** | `tier1_portraits/species_mrokon_operator.png` | Small ~1m being in a deep-link chair; pale near-white skin (no sun exposure); large expanded cranium with multiple interface ports; eyes closed in deep concentration; surrounded by bunker-interface equipment; pale-blue deep-link glow from the cranium; mood: *quiet, intimate, vulnerable*. Compare-contrast with the puppet portrait — the *real* Mrokon is small and indoors, not the armored warrior |
| **Mrokon's Stand surface backdrop** | `tier1_planets/bg_mrokon_stand_surface.png` | Vast warrior-training grounds — grey-brown rocky plains; ruined practice-targets; canonical *training accidents* visible (failed puppets lying still in the grass, awaiting maintenance teams); underground bunker entrances dotting the landscape; harsh yellow-sun sky; the planet should feel both *prepared* (lots of military infrastructure) and *resigned* (everyone knows what's coming) |
| **Mrokon Hammer-Ship exterior** | `tier1_ships/ship_mrokon_hammer.png` | Blocky, heavy, armored battleship; large kinetic-cannon mounted prominently along the spine; bears the canonical Mrokon scribed-ledger pattern along the hull (puppet-tradition extended to the ship); design language: *purposeful weight*, not elegance. Reads as "this ship will fire one shot, then break" |
| **The Hammer-Of-Refusal moment cutscene** | `tier1_cutscenes/cutscene_mrokon_hammer_fires.png` | The slice's defining defiance beat: tens of thousands of kinetic-impact rounds simultaneously striking the Others' fleet; the Others' Vessels visibly DENT (the canonical dimples appear); the Mrokon puppets self-destruct in the recoil shockwave; sunset lighting on Mrokon's Stand; mood: tragic-triumphant. **The marking is permanent.** This frame is canonically what produces the SC2-era "Others' Vessel has dimples" observation |

### Style direction across all three

- **Stelloth**: cool sophisticated trader-aesthetic; pearl-greys + green-violet; *precise* compositions (mirror their contractual rigor)
- **Selvenne**: warm ocean-bioluminescence; rich purples/cyans/chartreuse; *liquid* compositions (the species is fluid, the memories are fluid)
- **Mrokon**: stark warrior-aesthetic; greys + pale-blue accent; *blocky* compositions; the canonical "scribed ledger-marks" as a recurring visual motif across both puppet armor and ship hull

### Status

- ☐ Open as of 2026-05-17
- Tag `✅ PROCESSED <date>` per species as each species's art lands

---

## 2026-05-17 — Utwig Veils Falling — comic rehearsal + ceremony chaos imagery

**Canon source** (lore docs: [species-sheets.md §11 Utwig](species-sheets.md) — Doctrine canon refined 2026-05-17; [species-quests.md "The Veils Falling"](species-quests.md); [build_quest_inventory.py](../../tools/build_quest_inventory.py) `utwig_veils` quest — `q_utwig_observe_practice` + `q_utwig_doctrine_explanation` + `q_utwig_awareness_explanation` + refreshed `q_utwig_witness_ceremony`):

**Aaron's framing (2026-05-17)**: the Utwig devolution-doctrine is the **comical adoption of every religion at the same time** — incompatible rituals stacked, fasting schedules competing, masks-over-masks-over-masks. The plan **actually works** because the cognitive load of holding 47 contradictory observances simultaneously is what crushes their sapience-signature below the Others' detection threshold. They survive — drowning peacefully in their many many many traditions. The comedy IS the mechanism; the mechanism IS the survival.

### Required art targets

| Asset category | Path / context | What to make |
|---|---|---|
| **Utwig rehearsal scene (comic)** | `tier1_dialog_backgrounds/bg_utwig_rehearsal.png` | Open temple-courtyard with **simultaneously running incompatible rituals everywhere**: priests kneeling east AND facing west (some alternating mid-ritual); a priest standing on one foot drinking blessed water while another lies down drinking unblessed water (canonically the SAME priest alternating); Utwig wearing masks-over-masks-over-masks (some have 4-5 stacked); prayer scrolls in stacks the size of furniture; censers hung from shoulders; one Utwig writing the same prayer in seventeen languages simultaneously on a stone tablet; Furling stonemasons in the background carving in an unreadable script. Visual mood: *organized chaos*, sincere effort, gentle absurdity. **Read as comedy first, tragedy second.** |
| **Veils Falling ceremony (mass-mask-donning)** | `tier1_cutscenes/cutscene_utwig_veils_falling.png` | The actual ceremony at dawn: **ten thousand Utwig in a vast plaza** simultaneously donning multiple masks while performing the consolidated mega-ritual; choreographed-yet-incompatible movements (some kneeling, some prostrating, some standing while spinning in slow circles); concentric rings of priests representing each adopted faith; the Doctrine-Master Vell-Of-The-Open-Face placing the outermost mask in the center. **Sunrise lighting.** Compositionally heroic but the camera should also catch some *visibly exhausted* Utwig who have been preparing for weeks. Reads as: *they meant this*. Comedy + commitment + the moment the cognitive doors close |
| **Post-doctrine Utwig (locked in ritual; SC2-canon body)** | `tier1_portraits/species_utwig_post_doctrine.png` | The post-ceremony Utwig — the SC2-era body: depressed-seeming armored bipedal humanoid; multiple masks stacked over the face; prayer scrolls hanging from the body; the *exhaustion of permanent ritual* visible in the posture; this is the Utwig Captain Zelnick meets 230kya later. **Compare to the pre-doctrine portrait** (unmasked, lucid, anxious-but-alive) — the visual contrast IS the canonical tragedy |
| **Vell-Of-The-Open-Face (pre-doctrine elder portrait)** | `tier1_avatars/` if compatible | The Doctrine-Master before the ceremony: unmasked, mid-action carrying a stack of seventeen prayer scrolls, censer on each shoulder, slightly disheveled, fully sapient, anxious-but-determined. The face is *visible* — wide-set expressive eyes, mobile facial musculature, amber-flushed skin suggesting commitment. **The viewer should see this face and *know* they're about to lose it forever.** |
| **Utwig homeworld surface (Gorno region)** | `tier1_planets/bg_gorno_temple_complex.png` | Wide aerial view of the Utwig temple-complex on Gorno: dozens of temple structures in different architectural styles (one per adopted faith); paths between them designed for the mass-ritual choreography; canonical *crowding* — every available surface is in use for some ritual purpose. The Utwig do not have spare *space*; this is canonically because they do not have spare *cognition*. |

### Style direction

- **Humor doctrine ON during the rehearsal scene** — the visual should make the viewer smile at the absurdity. *Sincere* absurdity, not mocking — the Utwig believe in what they're doing.
- **Humor doctrine OFF during the Veils Falling cutscene** — the ceremony itself is dignified, committed, and quietly tragic. The mass-mask-donning moment is *not* funny; it's the moment a species closes its own cognitive doors forever, voluntarily, while singing hymns from four religions simultaneously.
- **Color palette**: warm earth tones (the Utwig are armored bipedal humanoids with amber-flushing skin) + ceremonial robe colors from multiple faiths (color-coded by sect — Korthi blue, Belyat red, Tarvinian green, etc.). The *clash* of color palettes within a single frame IS the visual comedy.
- **Composition**: lots of small interactions visible at multiple scales. The viewer should reward close inspection (e.g., notice the priest balancing on a bench, *both* sitting and standing).

### What does NOT change

- The pre-doctrine Utwig portrait (already in the species sheet — unmasked, lucid, expressive)
- The Gorno coordinates / system canon (unchanged)
- The Ultron callforward visual (separate artifact, separate handoff if/when authored)

### Status

- ☐ Open as of 2026-05-17
- Tag this entry `✅ PROCESSED <date>` when the rehearsal + ceremony + post-doctrine portrait land

---

## 2026-05-17 — Hyperspace combat — coaxial interference tunnel (Design chat request)

**Origin**: Design chat (not Lore). New visual target for hyperspace combat fights. Aaron's framing (2026-05-17):

> *"What we are fighting around is the 'coaxial interference tunnel' that forms between our hyperspace bubbles when we close for combat. Acts the same as a moonless planet."*

This replaces the planet visual when combat is initiated in hyperspace (Cleanser patrol, Cleanser climax, future intercept encounters). Mechanically identical to a moonless planet — same gravity well, same collision damage — but visually distinct so the player reads "we're fighting in hyperspace" without exposition.

**Engine state (Design chat already shipped):**
- [src/scz/combat/scene.py](src/scz/combat/scene.py) — `MeleeCombatScene` now takes `arena_style="solar_system"` (default) or `"hyperspace"`. Hyperspace style forces `moon=False` and routes the central-body render to `_draw_hyperspace_tunnel`.
- The render method tries to load `assets/combat/hyperspace_tunnel.png` first. If found, it's `smoothscale`'d to the body's collision diameter (2 × `PLANET_RADIUS` = 140 px at base scale) and blitted as the central body. If not found, a procedural fallback renders concentric pulsing violet rings with cyan accent lines (interference-fringe vibe).
- Two encounters already wired to use the hyperspace style:
  - `_trigger_cleanser_patrol` in [src/scz/hyperspace/scene.py](src/scz/hyperspace/scene.py) (the foreshadow patrol)
  - `_cleanser_engage_combat` in [src/scz/dialog/characters.py](src/scz/dialog/characters.py) (the climax fight, post-dialog)

### Required output

**One PNG** at `assets/combat/hyperspace_tunnel.png`. Single image, no animation frames (the engine will tint/rotate per-fight if needed later).

### Composition spec

- **Resolution**: 512 × 512 (recommended). The engine smoothscales to 140 × 140 at base arena scale and slightly larger at higher zooms — 512 gives clean downsampling. **Square aspect.**
- **Top-down "looking into a tunnel" perspective** — the camera is staring DOWN the throat of the interference figure. The brightest, most chaotic region is the center; concentric rings (the interference fringes) widen outward.
- **Diegetic frame**: this is the *interference pattern between two coaxial hyperspace bubbles*. Imagine two soap bubbles whose surfaces interpenetrate — where they overlap, a third structure manifests. Layered, harmonic, *not* a vortex (no spiral implication — it's standing-wave interference, not rotational flow).
- **Visible features**:
  - **Center**: dense, near-black core. Implies depth — like looking down a hole. Subtle violet/magenta glow at the very center but mostly absorptive.
  - **Mid-rings**: layered concentric bands in deep violet, magenta, and cyan-purple. Each band slightly offset (the interference fringes aren't perfectly circular — slight asymmetry reads as physical reality).
  - **Outer ring**: brightest, most chromatic. Sharp violet/magenta edge with cyan harmonics where the two bubble surfaces visibly overlap.
  - **Halo bleed**: very faint outer glow leaking past the body's edge. Just enough that the eye reads "this thing has presence."
- **No stars, no nebulae, no planet imagery**. The tunnel is one focal object on a transparent background. (Alpha-channel PNG. Outside the disk: transparent.)

### Palette

- **Primary**: deep violet (#5c2a8c), magenta (#a020a0), royal purple (#7a3aa8)
- **Secondary**: cyan harmonic accents (#40c0d8, #2080b0) — these are the interference-fringe color, used SPARINGLY (10-15% of total color area) on the outer rings and any harmonic-pulse spots
- **Background**: near-black with faint violet tint (#0a0418)
- **NO yellows, oranges, reds, or warm tones** — this is hyperspace, not a solar phenomenon. Cool only.

### Stylistic references

- **NOT**: a portal (no swirling vortex)
- **NOT**: a planet (no surface texture, no continents, no atmosphere haze)
- **NOT**: a black hole accretion disk (no rotational asymmetry)
- **YES**: oil-on-water interference patterns, viewed straight down
- **YES**: cymatic ripple patterns (Chladni plates, standing waves)
- **YES**: cross-section of a diffraction grating with depth — the rings should *imply* you could fall into them

### Acceptance checks

Drop the PNG in, run `python -m scz.main --windowed`, trigger the Cleanser patrol encounter (set `tutorial_complete=True` and fly to the patrol coords near 1500, 900), and visually verify:

- [ ] Tunnel reads as a non-planet body — no continents, no atmosphere
- [ ] Central body still feels solid enough to "fight around" — the player can tell where its collision boundary is
- [ ] Color palette is unambiguously cool (no warm tones)
- [ ] Composition has center-weighted depth (eye is pulled inward)
- [ ] No reading-pause for "what is that thing" — should be intuitively "weird hyperspace stuff" at a glance

### What does NOT change

- **Planet visual** (solar-system arena style) is unaffected — that's the default and remains a colored sphere
- **Other arena furniture** (asteroids, nebulae, background star, starfield) all render identically in both arena styles
- **Combat physics** are identical — same gravity strength, same collision radius, same collision damage

### Status

- ☐ Open as of 2026-05-17
- Tag this entry `✅ PROCESSED <date>` (or remove it) when `assets/combat/hyperspace_tunnel.png` lands and passes acceptance

---

## 2026-05-17 — Lemmkin species portrait + Whirligig planet surface + Lemmkin Skitter ship

**Canon source** (lore docs: [species-the-lemmkin.md](species-the-lemmkin.md); [build_species_inventory.py](../../tools/build_species_inventory.py) LEMMKIN row; [build_quest_inventory.py](../../tools/build_quest_inventory.py) `lemmkin_curiosity` quest):

**The Lemmkin** are a newly authored species (renamed from the placeholder CURIOUS row 2026-05-17). Recklessly-curious anthropomorphic squirrels with zero fear, lemming-clade collective behavior, scientific output through the roof, cliff-mortality through the roof, staying behind to *see what happens* with the Others. Homesteader-by-choice.

### Required art targets

| Asset category | Path / context | What to make |
|---|---|---|
| **Lemmkin individual portrait** | `tier1_portraits/species_lemmkin_portrait.png` | Anthropomorphic squirrel; bipedal, ~1.1m tall (suggest scale via familiar object next to figure); brown-and-cream dense fur (default regional palette — easterners redder, high-canopy greyer); **over-large round eyes** (signature trait — they want to see everything); twitchy nose; small round ears; cheek pouches; prehensile tail held in an upward S-curve gesture; four-fingered + opposable-thumb hands holding a notebook or scientific instrument; energetic mid-action pose, not static. Mood: bright-eyed delight, not menace. Background suggestion: dense forest canopy / tree-city framework |
| **Brisk-Ever-Onward (elder)** | `tier1_avatars/` if compatible — Lemmkin elder portrait | Larger Lemmkin (~1.3m); slightly greyer muzzle; otherwise same body plan; *more weighted* pose suggesting elder status but still energetic |
| **Whirligig planet surface** | `tier1_dialog_backgrounds/bg_whirligig_canopy.png` | Kilometer-tall trees with Lemmkin canopy-cities woven into the upper branches; bridges, platforms, observation perches; bright daylight (6-hour day = lots of light); rapid axial rotation hint via canopy-blown debris if compositionally possible. Should read as a *thriving* civilization — lots of motion, lots of habitation, lots of evidence of high-traffic exploration. Many tiny Lemmkin figures visible at various distances. **Cliffs visible in the mid-ground** with broken canopy-bridges and warning signs — canonical lemming-mortality |
| **Lemmkin Skitter (exterior)** | `tier1_ships/ship_lemmkin_skitter.png` | Small angular hull, ~30m long, painted in *bright contrasting colors* (the Lemmkin like to find their own ship in the sky); four thruster nacelles arranged around a central spine; thrusters can fire in any direction; weapon: Burst-Scatter Probe ports visible on the leading edge; tail-fin reminiscent of a squirrel tail (small species-flavor touch). Lightweight, agile, fragile-looking, *fast.* |

### Reprocessing prior outputs

- The CURIOUS row in `species_inventory.csv` had a placeholder color `(sky blue)` in `src/scz/content/species_visual.py`. **Image-lane action**: when adding a Lemmkin warp-pod palette, prefer a *bright cheerful color* — sky-blue is acceptable but consider also a *warm orange-cream* that ties to their canonical fur palette. (Design will wire the palette; this is just a suggestion.)
- No prior Lemmkin art exists; everything starts fresh.

### Style direction

- **Pixar-aesthetic readability** with Furling-era texturing — the Lemmkin should read as *cute* on first glance and *more complicated* on inspection (when the viewer notices, e.g., the warning sign about cliffs in the background of a portrait)
- **No menace.** The Lemmkin are not predators; they are not threats. Visual language should be *charming, bright-eyed, energetic*.
- **Movement-suggesting poses.** Static-portrait Lemmkin should still look like they're about to leap, sprint, or grab something. The species doesn't sit still.

### Status

- ☐ Open as of 2026-05-17
- Tag `✅ PROCESSED <date>` when Lemmkin portrait + Whirligig backdrop + Skitter sprite land

---

## 2026-05-17 — Burvixese world destruction cutscene (slice catastrophic-witness beat)

**Canon source** (lore docs: [species-sheets.md §10 Burvixese](species-sheets.md); [species-quests.md "The Caster Reckoning"](species-quests.md); [furling-artifacts-and-callforwards.md "The Burvixese and the Caster"](furling-artifacts-and-callforwards.md); [build_quest_inventory.py](../../tools/build_quest_inventory.py) `burv_caster` quest):

**Aaron's framing (2026-05-17)**: *"The BURVIXESE are the ones who thought they could amplify their intelligence using a caster device to make the Others spare them. Instead, it was like a moth to flame and they were all consumed and left their caster device, their civilization's last bid for survival."*

This is the slice's defining **Be-Loud-doctrine-failure** beat — the contrast to the Taalo's defense-shield-failure beat. Both end in extermination; the Burvixese version is *louder, faster, and more directly the doctrine's fault*. The visual story is **moth-to-flame**.

### Required cutscene art

| Asset category | Path / context | What to make |
|---|---|---|
| **Burv Caster activated** | `tier1_artifacts/artifact_burv_caster_active.png` | Planetary-scale cognitive-amplification array; equatorial-belt mounted; harmonic resonators at regular intervals (~300km of installation visible); the Caster firing in **a bright pulsing harmonic wave radiating outward from the equator** — beautiful, confident, doomed. Reads as the architecture of a *proud civilization at its peak*. Pre-Others-arrival |
| **The Others arriving — moth to flame** | `tier1_cutscenes/cutscene_burv_others_arrive.png` (and possibly a 2-3 frame sequence) | **The visual punchline.** The Caster's harmonic wave is *visible* in space; the Others arrive *attracted by it* — converging on the source like moths to a candle flame. Negative-black distortions, non-Euclidean visual (consistent with the Taalo extermination cutscene's Others-visuals). Many Others converge — more than at any other slice beat — because the Caster is broadcasting LOUDER than any other cognition in the galaxy at this moment. **The doctrine's failure mode is the doctrine's premise: they wanted to be seen. They were seen.** |
| **Burvixese civilization consumed** | `tier1_cutscenes/cutscene_burv_consumed.png` | Slice's most viscerally catastrophic beat: city-scale infrastructure collapsing into negative-black distortion; thousands of Burvixese cognitive-signatures extinguishing simultaneously; the Caster *still firing* during the consumption — they don't shut it off, they can't, the harmonic activation is a one-way commit. The doctrine's last expression is itself the executioner. Heavy, fast, terrifying |
| **Post-destruction: the Caster left standing** | `tier1_artifacts/artifact_burv_caster_inert.png` (and orbital planet view) | The Caster array survives the Culling because it's *infrastructure*, not cognition. **Visible from orbit on the empty planet**, exactly as SC2 archaeologists will later find it. The civilization gone; the device standing; the silence absolute. Compare to the Taalo Shield's post-Culling inert state — the Burv Caster's inert state should feel *grander and more melancholy* (it was the last bid for survival; it stands intact as a monument to that bid) |
| **Burv Broadcaster nodes scattered across galaxy** | `tier1_artifacts/artifact_burv_broadcaster.png` | The smaller broadcaster-amplifier nodes the Burvixese seeded across the galaxy pre-activation. These survive autonomously and become the SC2-canonical Burv Broadcaster network the Captain Zelnick era uses for galactic comms. Should look like a *smaller* variant of the Caster — same Burvixese engineering aesthetic; copper-brass-and-stone with harmonic-resonator antennae |

### Style direction

- **Burvixese aesthetic**: Four-armed engineer pride. Architecture is *proud, confident, peaked civilization* — they aren't humble about what they've built. Color palette: warm coppers, brass, dark stone; harmonic-resonator amber-glow at peak operation.
- **Moth-to-flame visual metaphor explicit** in the arriving-Others frame. The Caster's broadcast wave should *visually radiate*; the Others should be *visibly attracted to it*; the frame composition should make the metaphor unmissable.
- **Humor doctrine zero** during the consumption frame — the Steward's wit options vanish here, the same as during the Taalo extermination. The Burvixese were funny pre-activation (proud engineers cracking jokes about resonance harmonics); the catastrophe is not funny.

### Reprocessing prior outputs

- Existing Burvixese portrait (if any) should remain — only the cutscene art is new
- The Caster doc references already in `furling-artifacts-and-callforwards.md` should remain canonical; this HANDOFF entry is purely the *visual* targets

### Status

- ☐ Open as of 2026-05-17
- Tag `✅ PROCESSED <date>` when the cutscene + artifact + broadcaster art lands

---

## 2026-05-17 — Combat-arena starfield backdrop (Design chat request)

**Origin**: Design chat (not Lore). New visual target for the melee combat scene. The arena got planet, moon, and asteroids this round; the backdrop is now the obvious next visual weak spot — currently a procedural cross-star scatter. We want a Firefly-authored deep-space backdrop to give the arena real atmosphere.

**Engine state (Design chat already shipped):**
- [src/scz/combat/scene.py](src/scz/combat/scene.py) — on `on_enter`, the scene tries to load `assets/combat/starfield.png`. If found, it's `smoothscale`'d to the arena rect and blitted as the backdrop (replacing the procedural starfield). Missing file → procedural fallback (SC2-style cross-stars with warm/cool tints).
- **Drop-in**: place a single PNG at `assets/combat/starfield.png`. No engine change needed. The next combat fight uses it.

### Required output

**One PNG** at `assets/combat/starfield.png`. Single image, not a layered set (the engine doesn't currently parallax — we may add that later).

### SC2 source reference (what UQM does, what we're upgrading)

UQM's melee starfield is procedural — the engine scatters three tiny sprites at random positions:

- `references/uqm-source/sc2/content/base/battle/stars-000.png` — 1×1 dim pixel (background dust)
- `references/uqm-source/sc2/content/base/battle/stars-001.png` — small 4-point cross-star (bright midground)
- `references/uqm-source/sc2/content/base/battle/stars-002.png` — single magenta pixel (rare accent)

These are PALETTE references, not literal sprites we want to ship. The Design chat already mirrored that pattern procedurally — what we want from Image chat is to *replace the procedural scatter with a single beautifully-authored backdrop image*. Sample those SC2 sprites to confirm the palette + density vibe SC2 was going for (dense, cold, with occasional warm-color punctuation), then paint a higher-fidelity version.

### Composition spec

- **Resolution**: 1600 × 1000 (matches `ARENA_W` × `ARENA_H` exactly — pixel-perfect mapping). Higher resolutions like 3200×2000 also fine, the engine smoothscales.
- **Aspect**: 16:10. Tile-seamless not required (player never sees wrap edge of the backdrop — the arena edge is the wrap edge, and the camera doesn't pan).
- **Top-down deep-space view** — no horizon, no foreground. The camera is "looking down into a galactic depth field." Stars at multiple depths, faint nebulosity, occasional distant bright objects.
- **Mood**: cold, with warm accents. The combat scene tints itself blue-violet (arena boundary is (28,28,48)); the backdrop should sit *behind* that without competing. Think "Battlefleet Gothic background plate," "FTL starfield," "Star Control 2 hyperspace texture but rendered in HD."
- **No focal feature**: the *planet* is the focal feature (drawn on top, mid-arena). The backdrop must read as ambient — no bright nebula in the center, no dominant feature anywhere. The eye should accept it as "deep space" and move on.
- **Density**: more stars than current procedural (200 dots). Many faint dust-grain stars; fewer mid-bright stars; very few bright cross-stars or distant galaxies. *Reward close inspection* but don't compete with the action layer.

### Palette + tone direction

- **80% cool** — deep blue, indigo, near-black with subtle violet hint
- **15% warm punctuation** — distant red-giants and warm-white stars as accent
- **5% rare features** — occasional faint nebulosity wisps, possibly a distant unresolved spiral galaxy in a corner, faint dust lanes

The current arena boundary frame is `(28, 28, 48)` and the screen fill is `(4, 4, 14)`. The backdrop should have a similar base value — not pure black, not bright. The procedural fallback's brightest pixels are ~b=220 (near-white); the backdrop's brightest should be similar so the *planet and ships* still pop on top.

### What to avoid

- **No bright primary-color sources** in mid-frame. Players' eyes track ship sprites + projectiles, which are colored (yellow/cyan/red/violet). A bright pink nebula will tug attention away.
- **No literal recognizable references** — no Earth, no Saturn, no specific galaxy that breaks the precursor-era diegesis.
- **No text, no logos, no watermarks, no compositional symmetry**. Symmetric starfields look fake; we want the natural unevenness of real deep-space photography.
- **No moving elements / no animation frames** — single static image. Parallax-style animation is a future engineering task; not today.

### Acceptance checks

Drop the PNG in, run `python -m scz.main --windowed --test walk_super_melee` and visually verify:

- [ ] Backdrop renders behind the planet/moon/asteroids/ships without obscuring them
- [ ] No bright hotspot competes with the action layer
- [ ] Tone reads as "cold deep space with warm accents" not "neon nebula"
- [ ] Stars at multiple visual depths (some sharp, some hazy)
- [ ] Looks dramatically better than the procedural fallback (the bar to clear)

### Status

- ☐ Open as of 2026-05-17
- Tag this entry `✅ PROCESSED <date>` (or remove it) when `assets/combat/starfield.png` lands and passes acceptance

---

## 2026-05-17 — Thinn rename (formerly the Planar) — asset + prompt filename migration

**Canon change** (lore docs: [species-the-thinn.md](species-the-thinn.md) — renamed from `species-the-planar.md` via `git mv`; [build_species_inventory.py](../../tools/build_species_inventory.py) — PLANAR row retired, THINN row added; [build_quest_inventory.py](../../tools/build_quest_inventory.py) — new `thinn_edge_align` quest):

**Aaron's pun**: *Thinn* — both literally thin (2D ribbon-bodies, zero width) AND **they thought** they could stay if they all just faced sideways when the Others came. Captures geometry + Homesteader doctrine + Homesteader-faction self-deprecation in one syllable. The species themselves have embraced the name; their *own* nickname for themselves is now "Thinn."

**No visual redesign** — the body plan, color palette, and ship spec are all unchanged. **The only image-side change is filenames** (and any Firefly prompt text that names the species).

### Required filename migrations

| Old name | New name | Action |
|---|---|---|
| `assets/generated_drafts/firefly/tier1_portraits/species_planar_blade_portrait.png` | `assets/generated_drafts/firefly/tier1_portraits/species_thinn_blade_portrait.png` | Rename the file |
| `tools/firefly_prompts/tier1_portraits/species_planar_blade_portrait.txt` | `tools/firefly_prompts/tier1_portraits/species_thinn_blade_portrait.txt` | Rename the file; ALSO update body text inside (replace "Planar" → "Thinn", "Planar Blade" → "Thinn Blade", etc.) |
| `assets/generated_drafts/firefly/_manifest.json` | (same path) | Edit JSON entries — update any `species_planar_blade_*` keys/values to `species_thinn_blade_*` |
| `tools/firefly_prompts/README.md` | (same path) | Edit any "Planar" mentions to "Thinn" |
| `src/scz/dialog/articulation.py` | (same path) | Edit any "Planar" / "PLANAR" identifiers to "Thinn" / "THINN" (this is in your lane per Rule 5 — articulation.py is Image-owned) |
| `tools/gen_lore.py` | (same path) | If this is Image-lane code that mentions the Planar (saw a Planar reference in the grep), update to Thinn. If Lore-lane, please flag back via `HANDOFF_lore_chat.md` and I'll handle it. |

### Prompt-text changes inside the renamed firefly_prompt file

The Firefly prompt for the Thinn portrait should incorporate the new name into the prompt body. Suggested substitutions:
- *"Planar"* (species name) → *"Thinn"*
- *"Planar Blade"* (ship class) → *"Thinn Blade"*
- *"planar appendages"* → *"thin appendages"* (already done in the renamed lore doc; mirror here)
- Any reference to "the planar projection" (cognition/dimensional language) — keep "thin projection" or "two-dimensional projection" depending on context; avoid lowercase-planar-the-adjective entirely going forward

### What does NOT change

- Body plan (vertical iridescent ribbon-sheet; ~2m tall; ~80cm across; zero width)
- Color palette (teal / royal violet / gold-leaf yellow; view-angle-dependent shift)
- "Face" optical points (8-16 asymmetric per individual on upper edge)
- Slipstream visual signature
- Edge-on invisibility mechanic
- Ship silhouette (sail-craft, elliptical, pilot embedded along the spine)
- Color palette for the ship (matches Thinn iridescence)
- The magenta aurora portrait backdrop

### Status

- ☐ Open as of 2026-05-17
- Tag this entry `✅ PROCESSED <date>` (or remove it) when filename migrations + prompt-text updates are complete

---

## 2026-05-17 — Lander surface-terrain textures (Design chat request)

**Origin**: Design chat (not Lore). New visual target for the lander resource-gathering mini-game. No canon change — this is a *render-quality* upgrade for an already-shipped scene. The engine already generates a procedural pattern per planet type (boulders, dunes, lava veins, etc.); we want to replace that with beautiful Firefly-authored 2D top-down terrains.

**Engine state (Design chat already shipped):**
- [src/scz/planet/scene.py:108-118](src/scz/planet/scene.py) defines the seven planet types (`TERRESTRIAL`, `OCEAN`, `ROCKY`, `DESERT`, `ICE`, `PRIMORDIAL`, `VOLCANIC`) with their palette tints
- [src/scz/planet/scene.py](src/scz/planet/scene.py) — `_load_firefly_terrain()` checks `assets/planets/terrain_<type>.png` (all lowercase) on scene entry. If a file exists, it's `smoothscale`'d to the lander surface rect and used as the terrain background; if not, the procedural fallback runs
- **Drop-in**: just place PNG files in `assets/planets/`. No engine change needed. The next time the player lands, the new art appears

### Required outputs (7 PNGs total)

One PNG per planet type. Filename → planet type:

| File (must match exactly) | Planet type | Slice context |
|---|---|---|
| `assets/planets/terrain_terrestrial.png` | TERRESTRIAL | Earth-like worlds, the bulk of habitable surfaces |
| `assets/planets/terrain_ocean.png` | OCEAN | Mostly-water worlds; rare landfall, mostly view-from-above-shallow-sea |
| `assets/planets/terrain_rocky.png` | ROCKY | Default lander target; Mh-Lai II is this type |
| `assets/planets/terrain_desert.png` | DESERT | Arid sand/dune worlds |
| `assets/planets/terrain_ice.png` | ICE | Cold pale crystalline worlds |
| `assets/planets/terrain_primordial.png` | PRIMORDIAL | Hot young worlds with lava streams and emerging biomes; Mycon biot-cradle look |
| `assets/planets/terrain_volcanic.png` | VOLCANIC | Live volcanic / molten metal worlds |

### Composition spec (all 7)

- **Top-down view**, no horizon, no sky — the player's camera is straight down. Edges should be self-similar (the procedural fallback the player has seen so far is a flat tinted square — these images replace that)
- **Square aspect** — the lander surface rect is always rendered square. **Recommended source resolution: 1024×1024** (the engine `smoothscale`s to ~700×700 typical at 1920×1080 fullscreen, ~500×500 at 1280×720 windowed)
- **Tileable-feeling without needing exact tile seams** — the player never sees the same image twice on screen, so a hard tile guarantee isn't required, but avoid a single dominant focal feature (no "one giant volcano in the middle"). The surface reads as a continuous terrain panel
- **Detail at multiple scales** — when the player drives the lander around, the terrain should reward the eye both at a glance (silhouette / color regions) and on close inspection (texture grain). Think *Dwarf Fortress map tile but painted by hand*
- **No text, no UI elements, no procedural-noise look** — these go behind the lander icon, deposits (which the engine renders as fuzz-to-sharp blobs), and hazards (which the engine renders as colored discs). Anything in the texture that competes with those overlays is a problem. Avoid bright primary-color hotspots where the deposit / hazard overlays render
- **Player rendering on top**: the lander icon is yellow-cream diamond, deposits are tinted blobs (red/orange/green/cyan by type), hazards are translucent danger-colored discs. Pick palettes that let those overlays read clearly

### Per-type direction

**TERRESTRIAL** (engine palette: sky `(90,140,180)` blue, ground `(120,150,110)` muted-green)
- Patchwork of dry grass, scrub, low woods, small streams or pools. Earth-temperate-zone aerial photo aesthetic. Light cloud-cast shadows acceptable. *Avoid blue water as the dominant feature — that's OCEAN's job.*

**OCEAN** (palette: deep-blue sky `(60,100,160)`, sea `(70,110,170)`)
- Shallow-coastal-sea aerial view. Sandbars, coral-like reef patches, kelp-mat darkening, foam-edges on submerged reefs. Camera is *just above the surface*; you should see the seabed colors through the water but not the open sky.

**ROCKY** (palette: dark sky `(40,30,30)`, rocky-brown `(110,90,70)`) — **MOST IMPORTANT, this is the default lander world**
- Cratered or boulder-strewn rocky surface. Bedrock outcrops, scree fields, faint mineral veins (subtle — don't compete with deposit overlays), light dust accumulations between rocks. Think *Mars rover panorama from directly above*. Slight reddish-brown undertone, but the planet-type tint baseline is muted-brown.

**DESERT** (palette: tan sky `(140,110,70)`, sand `(200,170,100)`)
- Wind-carved dunes, mesa flats, dry riverbed scars, occasional rock spires. Subtle ripple-texture in dune fields. Photographic aerial-desert aesthetic.

**ICE** (palette: cold-light `(180,200,220)`, pale-ice `(220,230,240)`)
- Glacier surface with crevasses, refrozen pools, blue-shadow veins in the ice, scattered snow accumulations, exposed bedrock where the ice has retreated. Subtle prismatic refraction where ice is thin.

**PRIMORDIAL** (palette: red-hot sky `(100,30,30)`, lava-ground `(200,80,50)`)
- Young hot world: glowing lava streams between freshly-cooled basalt plates, faint steam-vent plumes, deep-red bioluminescent slime mats colonizing the cooler basalt fringes (these are the Mycon biots in their pre-sentient state — *do not* make them look like creatures, they're just colored slimes here). The world reads as "geology and life are both still arguing." Lore link: this is what Furling biologists call a *biot-cradle* world.

**VOLCANIC** (palette: dark red `(50,20,20)`, lava `(140,50,30)`)
- Mature volcanic world, more brutal than PRIMORDIAL. Black-glass basalt plains cracked open by lava veins; pyroclastic ash drifts; charred rock; obsidian fields. Less life, more raw geology. *No biot slimes here — this is too hot.*

### SC2 primer references (use as "style reference" / "structure reference" in Firefly)

Aaron's request: *"We can use the original base ones from SC2 as primers for Firefly if it has that option."* Firefly supports a **Style Reference** image and a **Structure Reference** image (separate slots in the web UI). Use the SC2 globe textures already extracted into `assets/planets/` as Style Reference for the palette, not Structure Reference (the globes are spherical, not top-down — wrong structure entirely):

| Planet type | Best SC2 primer (palette only) | Path |
|---|---|---|
| TERRESTRIAL | `azure-big-000.png` or `opalescent-big-000.png` | `assets/planets/azure-big-000.png` |
| OCEAN | `azure-big-000.png` or `cyangas-big-000.png` | `assets/planets/azure-big-000.png` |
| ROCKY | `carbide-big-000.png`, `chondrite-big-000.png`, `metal-big-000.png` | `assets/planets/carbide-big-000.png` |
| DESERT | `auric-big-000.png`, `copper-big-000.png`, `dust-big-000.png` | `assets/planets/auric-big-000.png` |
| ICE | `pellucid-big-000.png` | `assets/planets/pellucid-big-000.png` |
| PRIMORDIAL | `infrared-big-000.png`, `magma-big-000.png` (lighter) | `assets/planets/infrared-big-000.png` |
| VOLCANIC | `magma-big-000.png`, `crimson-big-000.png` | `assets/planets/magma-big-000.png` |

(The globes are tiny — 128×128 at most. Firefly's style-reference resamples internally; that's fine, we're just stealing the palette.)

### Prompt skeleton (copy-paste, edit per type)

```
Top-down aerial view of a <planet-type-description> surface terrain.
Square composition, 1024x1024. No horizon, no sky, no UI elements,
no text. Painterly 2D game-art aesthetic — beautiful but readable.
Multi-scale detail: clear silhouette regions at a glance, fine grain
on close look. Continuous panel, no single dominant focal feature.
Muted palette consistent with <hex-colors-from-spec-above>. Avoids
bright primary-color hotspots that would compete with overlay icons.
Style: <hand-painted-overhead-strategy-game-tile, similar mood to
Star Control 2 lander mini-game backdrops but high-detail painterly
remake>.
```

### Per-type prompt additions

- **TERRESTRIAL**: *"...temperate patchwork of dry grass, scrub, small woods, occasional creeks. Earth-aerial reconnaissance aesthetic. Subtle cloud-cast shadows."*
- **OCEAN**: *"...shallow-coastal seabed visible through clear blue-green water. Sandbars, reef patches, kelp mats. Faint surface ripples."*
- **ROCKY**: *"...cratered bedrock and scree fields. Mars-rover-panorama tone but directly overhead. Subtle reddish mineral veining. Dust accumulations between boulders. Dramatic but not busy."*
- **DESERT**: *"...wind-carved dune fields and dry riverbed scars. Occasional rock spires casting long shadows. Sand-ripple texture across the dunes."*
- **ICE**: *"...glacial surface with crevasses and blue-shadow ice veins. Refrozen meltpools. Scattered snow. Subtle prismatic refraction where ice is thin."*
- **PRIMORDIAL**: *"...young hot world. Cooling lava streams between basalt plates. Faint steam vents. Deep-red bioluminescent slime mats colonizing the cooler basalt fringes (these are colored slimes — NOT creatures). Geology and proto-life co-existing."*
- **VOLCANIC**: *"...mature volcanic world. Black-glass basalt plains cracked by glowing lava veins. Pyroclastic ash drifts. Obsidian fields. Raw, hostile, no visible life."*

### Acceptance checks

Before marking this entry processed, verify in-game (drop a PNG in, launch `python -m scz.main --windowed`, fly to each planet type, land):

- [ ] Texture renders inside the surface rect (no black ground showing through)
- [ ] Texture isn't visually washed out by the engine's flat-color terrain fill (palette match should be close enough that the under-layer reads as continuous)
- [ ] Deposits (fuzz-to-sharp blobs) remain readable at the sensor edge — i.e. the texture isn't too busy or too high-contrast in mid-tones
- [ ] Hazard discs (translucent red-orange for active, dim outline for inactive) remain readable on top
- [ ] Different terrain types feel visually distinct at a glance — you can tell a ROCKY from a DESERT from an ICE world without reading the HUD

### Status

- ☐ Open as of 2026-05-17
- Tag this entry `✅ PROCESSED <date>` (or remove it) when all 7 PNGs land in `assets/planets/` and pass the acceptance checks above

---

## 2026-05-17 — Taalo shield-tragedy reframe (new visual targets + reframing prior outputs) — **REFINED with Horta visual lineage + post-Culling calcified-rocks state**

**Canon change** (lore docs: [species-sheets.md §9 Taalo](species-sheets.md) — incl. new §1.6 "Post-extermination appearance," [species-quests.md "The Shield That Will Not Hold"](species-quests.md), [furling-artifacts-and-callforwards.md "The Taalo Shield"](furling-artifacts-and-callforwards.md), [slice-cluster.md §12 Taalo's Stone](slice-cluster.md)):

The Taalo are the slice's defining tragedy. Major canon:

- **The Taalo are a single mountain range** on Taalo's Stone II (~2000 km long, 8-12 km peaks). Individuals are mobile silicon-fragment-organisms of that mountain. *The mountain is them; they are the mountain.*
- **Visual lineage — the Star Trek TOS Horta** (from *"The Devil in the Dark,"* 1967) is the **canonical primary visual reference**. Like the Horta, Taalo fragments are silicon-substrate creatures that **shamble** (heavy patient lurching, not a stride; weight-shifting between sets of stride-limbs with multi-second pauses), **eat rock with secreted mineral acid** (the acid is harmless to organic flesh on contact but pits stone for years; the fragment lowers its forward articulator-limb against a rock face and the acid bores a shallow chamber over hours), and **look like ordinary rocks when at rest or dead.** Style cue for Firefly: *"silicon-based organism in the visual tradition of the Horta from classic Terran fiction — boulder-like silhouette when still, slow shambling gait when moving, plate-segmented body of slate-grey mineral material with subtle iridescent lattice glow."*
- **They cannot leave their planet** — metabolism is tied to acid-grazing the local silicate ecosystem.
- **They are NOT below the Others' detection threshold** despite silicon substrate (mountain-cognition is too large/coherent).
- **They are building the Taalo Shield in our slice** — a planetary-scale anti-Others defensive barrier embedded in the mountain's flank. Generator-nodes at regular intervals along the range. Pale-violet pre-activation glow.
- **The Shield does not work.** Mid-late slice beat: Shield activates → Others arrive → Shield does nothing → Taalo consumed in the Culling.
- **Post-Culling: the Taalo bodies calcify into ordinary-looking rocks.** Within hours the lattice-glow dims and goes dark. Within weeks the plate-articulations stiffen and fuse. Within centuries the bodies weather indistinguishably into the substrate. **From orbit, the post-Culling homeworld is invisible — it looks like a normal silicate-rocky planet with a long mountain range and some derelict industrial-looking structures (the inert Shield) on the flanks.** The Taalo are *not visually distinct* from rocks in their resting/dead state — only an archaeologist on the ground with the right instruments would notice the biological lattice inside certain stones.
- **The inert Shield survives** — recovered 230kya later by SC2 archaeologists at Delta Vulpeculae II-C. They find an intact device with side-effect psionic-nullifier property. **They do NOT find the Taalo bodies as bodies** — those are now landscape. *Their graves are the mountain.*
- ~5,000-year Furling friendship preserved. Steward is "the fourth Steward to visit this ridge."

### Affected asset categories

The Image chat should regenerate/append art for:

| Asset category | Path / context | What changes / is new |
|---|---|---|
| **Taalo fragment-individual portrait** | `tier1_portraits/` — Taalo Witness fragment | NEW. Slate-grey mineral-plate body; violet-amber glow patterns syncing across plates; quadrupedal-leaning bipedal **shamble** (not stride — heavy lurching motion); two pairs of stride-limbs + two upper articulator-limbs; **NO concentrated head** — sensory facets distributed across upper hemisphere; geological-patient pose. Plate-pattern varies by region-of-origin. **Horta visual lineage explicitly**: boulder-like silhouette when still — a fragment in repose should look like a rock-with-intentionality, not a creature-being-still. Two-state portrait if compositionally possible: at-rest (looks like a rock) and active (glow-pulses visible, plates flexed open at the shamble-articulation points) |
| **Taalo home mountain landscape** | `tier1_planets/` or `tier1_dialog_backgrounds/` — Taalo's Stone II surface view | NEW. 2000km-long mountain range with 8-12km peaks on a high-silicate continental world. **Shield-infrastructure embedded in the mountain flanks** — deep-anchored copper-brass-and-stone generator-nodes at regular intervals; pale-violet pre-activation glow patterns at the ridges; faint deep-mountain-blue consensus-glow visible from orbit during mass-consciousness moments. Rest of the planet is barren-stable terrain |
| **Contemplation-cove landscape** | `tier1_dialog_backgrounds/` — bg_taalo_cove or similar | NEW. Natural amphitheater in the mountain's flank ~3km below the highest peak. Slate-grey rock walls; soft violet-amber glow from embedded lattice-veins; a flat sitting-area where Stewards traditionally land; the contemplation-cove is where most Steward-Taalo dialog happens |
| **Taalo Shield — activated state** | `tier1_artifacts/` — `artifact_taalo_shield_activated.png` | NEW. Mountain-anchored field projector with a pale-violet field-projection arcing in a hemisphere over the planet surface. Visible from orbit. The Shield at peak operation, just before failing |
| **Taalo Shield — post-failure inert state** | `tier1_artifacts/` — `artifact_taalo_shield_inert.png` | NEW. The Shield's physical structure (generator-nodes in the mountain flanks) after the Taalo are consumed. Quiet. No glow. Bedrock-anchored. **This is the canonical SC2-era artifact Captain Zelnick et al. recover at Delta Vulpeculae II-C** — the inert post-failure state is the artifact's permanent appearance. Even after 230kya |
| **Taalo extermination cutscene** | `tier1_cutscenes/` — `cutscene_taalo_consumed.png` (and possibly a multi-frame sequence) | NEW. Slice's defining tragic beat: Shield activates (pale-violet hemisphere over mountain); Others arrive (negative-black distortion, non-Euclidean visual); Shield does *nothing* — Others come through it as if it isn't there; Taalo glow-patterns extinguish one by one across the visible range. Hold on the silent mountain afterward. Heavy. Quiet. *No music recommended; just the lattice-resonance audio fading*. **Humor doctrine zero — the Steward's wit options vanish entirely during this scene** |
| **Taalo post-Culling planet view** | `tier1_planets/` or `tier1_cutscenes/` — `planet_taalo_stone_post_culling.png` | NEW. Orbital view of Taalo's Stone II *after* the Culling. **The visual story is dignity through restraint** — the planet now looks *almost ordinary*: a silicate-rich rocky world with an unusual long mountain range and some old industrial-looking structures (the inert Shield generators) embedded in the flanks. **Nothing visually telegraphs that a sentient species lived and died here.** The Taalo bodies have calcified indistinguishably into the substrate. From orbit you cannot tell. This is the canonical SC2-era appearance of Delta Vulpeculae II-C — when Captain Zelnick's team eventually arrives 230kya later, this is what they see. The image's emotional weight comes from *the player knowing what's missing* while looking at an unremarkable rocky planet. Subtle: maybe the mountain's pre-activation pale-violet glow-veins are faintly visible as discolored mineral streaks in the rock if you look closely, but the planet is *primarily reading as just-a-rocky-planet* |
| **Dialog character — Taalo Witness fragment** | Image chat avatar set | Optional. Sample names: *We-Who-Watch-The-Northwest-Bench*, *The-Slow-Watcher-At-The-Trailhead*, *Mineral-Sampler-Of-The-South-Watershed*. Layered avatar treatment compatible with the dialog system; **very slow** glow-pulse rate on the plates (slower than any other species' portrait animation) |
| ~~**Lattice-resonance audio**~~ | ~~Audio assets~~ | **MIGRATED to `HANDOFF_audio_chat.md` (2026-05-17)** — when the Audio chat lane was formalized, this row moved to its proper inbox. See HANDOFF_audio_chat.md "Taalo lattice-resonance VO + slice-defining silence cue" |

### Reprocessing prior outputs

- **No prior Taalo art exists** that needs to be retracted — the Taalo are a newly-authored species (previously TBD in the spreadsheet). All Taalo image work starts fresh from this canon
- **The earlier "post-slice Shield" framing** for the Taalo Shield is retired. If any in-progress Image-chat work treated the Shield as "not in our slice," reframe it: the Shield is built *in our slice* and is a slice-scope artifact in both activated and inert states

### Prompt-level guidance for any Taalo-interior or Shield prompt

> *"silicon-based mineral-substrate aesthetic in the visual tradition of the **Horta** from classic Terran science fiction (*Star Trek: The Original Series, 'The Devil in the Dark'*) — slate-grey and basalt-dark mineral plates; boulder-like silhouette when still (a fragment at rest reads as a rock-with-intentionality, not a creature-being-still); heavy shambling locomotion when in motion; acid-etched architecture (caves, sitting-shelves, terraced contemplation-coves cut into the mountain by generations of Taalo grazing-and-thinking); pale violet-amber glow patterns visible across body and mountain surface, syncing slowly with deep lattice-resonance; geological tempo throughout; no organic warmth; weight, age, patience, dignity; the species accepts its probable extinction with composure, never with despair — the visual mood is *brave melancholy*, not horror or despair"*

**Star Trek TOS Horta is the canonical primary visual reference** for the species. The Furling-era Taalo are more *articulated* than the Horta (they walk on legs, they have manipulator-limbs, they have facial sensory facets), but the silhouette philosophy is the same: this is a *rock that intends*. When at rest, the fragment should be hard to distinguish from a boulder. When moving, the shamble should suggest the boulder *deciding* to move.

For the Shield specifically — both activated and inert states share design language: copper-brass mountain-anchored generators with crystalline-mineral integration into the bedrock; the activated state has pale-violet field-projection; the inert state is dark, dormant, beautiful in its silence.

For the post-Culling orbital planet view: the visual restraint is the point. The planet should *look ordinary*. The viewer's emotional response comes from knowing what's missing while looking at an unremarkable rocky world.

### What does NOT change

- The earlier Taalo-related entries flagged in the Furling-fur entry above (Taalo are not Furlings — their interiors don't get fur)
- Burvixese/Caster / Burv Broadcasters art — separate species, unaffected
- Mmrnmhrm / Chenjesu / other below-threshold-by-biology species — they still qualify; only the Taalo's biology framing changed

### Status

- ☐ Open as of 2026-05-17
- Tag this entry `✅ PROCESSED <date>` when the Image chat has generated all listed new assets and updated any in-progress Taalo prompts to the new canon

---

## 2026-05-17 — Furling aesthetic: fur-everywhere interior design canon

**Canon change** (lore doc: [the-furlings-and-the-others.md §1 "The aesthetic-of-the-fur"](the-furlings-and-the-others.md), with downstream callforward in [furling-artifacts-and-callforwards.md "Earth's Moon (Moonbase)"](furling-artifacts-and-callforwards.md)):

Furling designers extend their own shagginess outward: **every surface a Furling regularly touches is fur-covered**. Ship controls, console panels, command-chair armrests, doorframes, handholds, decorative wall panels, table-tops, ceremonial seating. Variation by function:

- **Short dense pile** (mole/otter texture) — heavy-use control surfaces, console panels, frequently-gripped handholds
- **Long luxurious shag** (mammoth/musk-ox texture) — decorative wall panels, less-touched seating, ceremonial drapes
- **Softest summer-underfur** — ceremonial high-status seating, Council-chamber chairs

**Light fixtures wear translucent fur diffusers** — fine pale fur stretched over bulb-housings, *"for proper diffusion."* Every photon in a Furling interior is filtered through fur. The cumulative effect: warm, textural, slightly amber-tinted lighting; soft shadows; visible fibrous texture across every illumination boundary.

The aesthetic is ergonomics-married-to-taste — Furling hands grip fur better than smooth surfaces; their sensory hair-roots register tactile information through fur better than through bare metal; their eyes prefer fibre-diffused light to point-source light. **The Furlings did not invent this aesthetic so much as refuse to abandon it.**

**SC2-era consequence**: Captain Zelnick boards the dormant Furling Scout at Earth's Moon and finds the interior inexplicably *fluffy*. The Persuader Steward who sealed the ship 250kyr earlier cured and stabilized all the fur with antimicrobial substrate-binders so it would last; it does. SC2 archaeologists describe the controls as having "biological accents of unknown purpose."

### Affected asset categories (everything Furling-interior)

The Image chat should reprocess prompts and (where already generated) regenerate art for:

| Asset category | Path / context | What changes |
|---|---|---|
| **Furling dialog backgrounds** | `tier1_dialog_backgrounds/bg_furling_bridge.png` and any other bg image set inside a Furling-built space | Add fur-covered console surfaces; fur-diffused warm amber lighting; visible fibrous texture on contact surfaces; consoles wear short-pile fur, seating wears longer shag |
| **Layered avatar backgrounds** (Furling characters) | Backgrounds in `tier1_avatars/` for Furling characters (Commander Halia is the slice example; future Furling NPCs to come) | Backdrop should show fur-textured station/ship interior behind the character; fur-diffused lighting on the character |
| **Furling Scout ship — interior view** | If/when interior shots exist (e.g., Time Drive cutscenes, Customization-UI ship-deck views, lander cabin) | All console surfaces, armrests, doorframes fur-covered; fur diffusers on instrument lights |
| **Furling Scout ship — exterior** | `tier1_ships/` for Furling Scout exterior sprite | **No change.** Fur does not survive vacuum, radiation, or thrust. Exterior remains standard Furling metalwork |
| **Mh-Lai Station backdrops** | Cutscene backdrops or scene art set inside Mh-Lai Station | Council chambers, command rooms, corridors — fur on surfaces, fur-diffused lighting, "warmly textured everything" |
| **Cutscene backdrops featuring Furling interiors** | `tier1_cutscenes/` — any cutscene set in a Furling space (Cloak Install station-stub backdrop already wired, others to come) | Same treatment — fur surfaces, fur-diffused lights |
| **Future Furling NPC portraits** | New Furling characters (Talos? Hider researcher? Cleanser-emissary?) | Their workspace backgrounds carry the fur aesthetic |

### Reprocessing guidance

- **Prompt-level addition** for any prompt set inside a Furling interior: append a recipe of *"all touched surfaces covered in fur of varying length and softness — short dense pile on heavy-use controls, long luxurious shag on decorative panels, ceremonial soft underfur on seating; light fixtures fitted with translucent pale-fur diffusers giving a warm amber-tinted glow with fibrous shadow edges; the room reads as textural, warm, and biologically-cared-for."*
- **Existing Firefly art already in `assets/comm/` or `assets/generated_drafts/firefly/`** that depicts Furling interiors should be flagged for regeneration on the next Firefly round. Where re-render is too expensive, a *fur-overlay pass* (post-process fur texture on top of existing console surfaces) is acceptable
- **Tactile profile of the fur**: short pile is roughly mole-fur length (~3-5mm); shag is mammoth-fur length (~20-40cm in places); ceremonial underfur is downy and almost cloud-like
- **Color palette of the fur itself**: matches the standard Furling browns and creams from existing Furling character portraits — sand, cinnamon, oat, deep umber. Fur on consoles is often dyed *darker* than the wearer (so it doesn't camouflage them); fur on ceremonial seating is often dyed *paler* (so the seated Furling stands out from the chair)
- **The translucent fur diffusers on lights** are specifically *pale fur* — bone-white or pale-cream — so the diffused light comes through warmly without losing intensity. Stretched taut over the bulb-housing like a drumhead, just dense enough to glow

### What does NOT change

- Exterior ship sprites (fur cannot survive vacuum/thrust)
- Planet sprites (the Mh-Lai planet, Furlmart moon, etc. — these are surface views, not interiors)
- Faction insignia and module icons (these are 2D symbols, not 3D interior surfaces)
- Resource icons, UI elements, navigational backdrops
- Anything NOT inside a Furling-built space

### Status

- ☐ Open as of 2026-05-17
- Tag this entry `✅ PROCESSED <date>` (or remove it) when the Image chat has regenerated the affected prompts + assets

---

*(Future entries appended below.)*
