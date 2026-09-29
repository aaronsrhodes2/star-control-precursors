# Roadmap to a Full Play Field

> Authored 2026-05-17 from the Design lane. This doc tallies every open gap between the current vertical-slice and a *full play field* — defined as: the player can drop into hyperspace, encounter every queued species along their domain patrols, run each species' decision-tree quest to a terminal status, and reach one of the canon endings. Asset polish (final portraits / music) lives in the Image + Audio lanes and is out-of-scope for this Design-lane plan.

## Method

This roadmap is partitioned into **six phases** of ~3-4 Design-chat sessions each. Phases are mostly orderable rather than strictly ordered — Phase N has dependencies but can interleave with Phase N+1 work that those dependencies don't block. Each phase ends with a measurable "milestone walk test" that, when green, proves that band of functionality.

Estimated total: **15-20 Design-chat sessions** to close all gaps. The Combat / Image / Audio chats run autonomously alongside and are not on this critical path; their lanes are tracked in their own HANDOFF docs.

## Phase 1 — Hyperspace Domain Population *(this session)*

The hyperspace map currently shows stars + ambient ripples + 4 scripted encounters (Cleanser patrol + climax, Coel Tessar, salvage wrecks ×4). What it does NOT show: *the rest of the galaxy is occupied by somebody*. Today the player can fly from Mh-Lai to Beta Corvi unmolested by anything that isn't story-flag-gated.

**Goal**: every region of the 10000×10000 starmap belongs to *somebody* whose ships patrol it. Crossing into another faction's territory carries real possibility of a contested encounter.

**Deliverables**:
- `src/scz/content/species_domains.py` — `SpeciesDomain(name, center, radius, color, ship_class_id, encounter_density)` dataclass + a 6-domain initial registry (Furling Hearth, Cleanser Approach, Slylandro Stations, Mycon Whisper, Melnorme Network, Wild)
- Hyperspace render: faint colored boundary rings rendered before stars
- Per-domain patrol spawning in `_maybe_spawn_encounters`: 1-2 EncounterPoints per domain on scene entry, retiring via `met_<species>_patrol_<n>` flags
- `walk_species_domain_patrol` walk test
- HUD readout: "you are in [Cleanser Approach]" / "you are in unclaimed space"

**Milestone walk**: `walk_species_domain_patrol` — enter hyperspace, teleport into Cleanser Approach domain, expect domain readout in HUD, expect at least one Cleanser patrol EncounterPoint within trigger radius.

## Phase 2 — Queued Species Implementations *(5-7 sessions)*

Eleven species have authored lore docs and zero engine code. Each session ships one or two species: dialog FSM in `src/scz/dialog/characters.py`, content registries (any per-species artifacts in Bio-Archive, any per-species station-screen modules), system content (homeworld star content module), walk-test, archive-entry. Combat-side ship classes come from the Combat Mechanics chat in parallel.

Priority order (by load-bearing-ness in the canon):
1. **Mmrnmhrm** — `references/lore/the-mmrnmhrm-and-chenjesu.md` — prior-cycle robot survivors; canonizes Others-come-in-cycles. *High*
2. **Chenjesu** — same doc — rooted prior-cycle witnesses below threshold; replayable Resonance Record. *High*
3. **Taalo** — `references/lore/species-precursor-era.md` + memory — silicon range-species; their tragedy; Taalo Shield construction fails. *High* (slice-defining)
4. **Burvixese** — same doc — Be-Loud doctrine; Burv Caster fails catastrophically; small contingent migrates. *Medium*
5. **Utwig** — same doc — chose-devolution; Veils Falling; Ultron retcon. *Medium*
6. **Lemmkin** — `references/lore/species-the-lemmkin.md` — fast-breeding archivists; Stay by archive-weight. *Low*
7. **Stelloth** — `references/lore/species-the-stelloth.md` — *Low*
8. **Selvenne** — `references/lore/species-the-selvenne.md` — *Low*
9. **Mrokon** — `references/lore/species-the-mrokon.md` — *Low*
10. **Kovellim** — `references/lore/species-the-kovellim.md` — *Low*
11. **Karavem** — `references/lore/species-the-karavem.md` — *Low*
12. **Thinn** — `references/lore/species-the-thinn.md` — *Low*

Each one terminates the species in Cluster Status Board with one of: Migrated / Cloaked / Hidden / Eliminated / Pre-sentient. The Council Mission system gets one mission per species (already partially wired).

**Milestone walk per species**: `walk_species_<name>_quest` — visit homeworld, run terminal-status branch, expect cluster-status update.

## Phase 3 — Plot-Beat Mechanics *(3-4 sessions)*

The slice's plot arc has five mechanics still missing engine support:

1. **Rainbow Worlds chain** — 10 Rainbow-tagged stars in `stars.json`. Player needs to visit *some-or-all* of them and read the arrow they point to. Mechanic: visiting each grants a `rainbow_<n>_observed` flag; an in-Bio-Archive entry assembles the constellation diagram once N ≥ 3 are observed; the **Andromeda Crossing** finale becomes available after the threshold. *(canonical doc: `references/lore/rainbow-worlds-arc.md`)*

2. **Others' Vessel Hijack quest** — multi-beat quest to acquire a wrecked Others' Vessel and bring it under Furling control. Per `references/lore/ship-roster.md`, the Vessel is *not* in super-melee normally; this quest is the only way to unlock it. Likely structure: receive intel → fly to specific deep-space coords → puzzle-encounter → cinematic → vessel unlocked in shipyard.

3. **Dnyarri Disguised Encounter** — fog-of-war over the ship roster: a Dnyarri-controlled ship looks like any other species' ship until it fires. The species has no fleet of its own (they're mind-control passengers on hijacked hosts) so no domain — instead, 2-3 disguised encounters scatter across hyperspace each scene-entry, biased to spawn inside the cover species' matching domain. *(canonical doc: `references/lore/dnyarri-disguised-encounter.md`)*

4. **Migration finale** — the player either calls Migration (good ending), enters Andromeda Crossing (very-good ending), or fails to handle a critical-mass of species and triggers the Bad End (Others arrive). End-state evaluation against Cluster Status Board.

5. **Multiple endings** — at least four endings: Migration (default-good), Andromeda (best), Cleanser-aligned (dark-grey), Fall-Without-Migration (bad). Each has a closing cinematic; cinematic framework comes from Phase 5.

**Milestone walks**: `walk_endings` parametrized over the 4 endings + `walk_dnyarri_disguised_first_encounter`.

## Phase 4 — Crew Side-Quests *(5 sessions)*

Five named Furling crew quests stubbed in `references/lore/crew-recruitment-quests.md`:

1. **Mraka Yenn-Sa** (Pilot) — MVP shipped; needs 2-4 beat polish + dialog branches
2. **Bren-Vor Telcas** (Weapons Officer) — `_stub_crew_dialog` placeholder; full quest TBD
3. **Yelena Lwen-Tar** (Engineer) — same
4. **Mira-Rou Halve-Tel** (Medic / Bio-Architect) — same
5. **Tarven Olwen-Sa** (Navigator / Star-Reader) — same

Each adds a promoted crew module (active ability) to the ship customization screen. Mh-Lai shipyard tolerance rule applies (Furling shipyard only).

Per-quest deliverables: full dialog FSM, recruit gate flag, common-room alcove unlocked, promoted-module mechanic, walk-test.

**Milestone walk**: `walk_crew_full_complement` — recruit all 5, expect each module installable.

## Phase 5 — Polish *(2-3 sessions)*

Carry-over mechanics that exist as scaffolds but need closure:

- **Cinematic framework** — the Distress Beacon, Fall of Mh-Lai, and the 4 endings all want a real cinematic player. Today they're scenes with text + colored shapes; we want a uniform `CinematicScene(beats=[…])` shell that takes a list of beat-dicts (image_id, caption, duration, music_cue) and runs them.
- **Time Drive ↔ combat integration** — Furling Time Drive is canonical (saves at any point, rewind to any save). Today it's hyperspace-only. Needs hook in combat scene + lander scene.
- **Halia branch variants** — Commander Halia's dialog FSM currently has 3 states; the canon supports 6 branch variants per `references/lore/halia-steward-banter.md`. Author the remaining 3 branches.
- **Common Room banter** — generic crew banter cycle on visit (random selection from per-crew banter pool, gated by recent quest progress).

## Phase 6 — Asset Catch-up *(autonomous; out-of-Design-lane)*

Tracked here only for visibility. These run autonomously in their own chats:

- **Image chat**: avatar / portrait / ship-sprite / cutscene-frame generation for every TODO_AVATAR marker. Unlimited Firefly generator running.
- **Audio chat**: SFX / ambient bed / music-cue / voice-profile generation for every TODO_AUDIO marker. Local sound/music model running.

Design lane keeps TODO_AVATAR and TODO_AUDIO markers liberally seeded; the asset producers pick them up on their own schedule. Final integration is automatic — when the asset lands at the canonical path the marker checks for, the in-game render switches from placeholder to final.

## Cross-Phase Tooling

Tools that the Testing chat owns / maintains, called out so the Design lane doesn't duplicate effort:

- `tools/run_walks_parallel.py` — full regression in ~46s
- `tools/dialog_coverage.py` — BFS FSM auditor
- `tools/module_stat_audit.py` — per-module install+verify
- `tools/status_dashboard.py` — cross-lane HANDOFF view
- `tools/check_stubs.py` — TODO_* marker survey, owner-grouped

Anything that needs new test infrastructure: file via `HANDOFF_testing_chat.md`.

## What's NOT on this roadmap

Out-of-scope, by design:
- **Procgen of unvisited star systems** — explicitly we are *not* generating contents for the 470+ unscripted stars. The 13 slice systems remain hand-authored; everything else stays empty-procgen.
- **Super-melee ladder / arcade modes** — Combat Mechanics chat owns this; ask them.
- **Save / load file polish** — exists at MVP level; deferred.
- **Localization** — English-only for the slice.

## Definition of "Full Play Field" (success criteria)

When all six phases complete:

1. ✅ Player can fly from Mh-Lai to any of the 13 slice systems
2. ✅ Hyperspace patrols populate territory between systems
3. ✅ Every queued species has a homeworld scene + decision dialog → terminal status
4. ✅ Cluster Status Board reflects all 23 species accurately
5. ✅ Rainbow Worlds chain can be observed → Andromeda Crossing unlocks
6. ✅ Hijack quest can be run → Others' Vessel becomes super-melee-available
7. ✅ All 5 crew recruited → all 5 active abilities installable
8. ✅ Each of the 4 endings reachable from the Migration finale
9. ✅ Fall of Mh-Lai fires mid-game; post-fall flow lands cleanly
10. ✅ Full regression walk (`tools/run_walks_parallel.py`) green
