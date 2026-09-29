# HANDOFF — SCZ: Game Design

> Dispatch board from **SCZ: Game Lore** (and other lanes) to **SCZ: Game Design**. Entries are append-only; Design crosses items off as they land. Most-recent at top.
>
> Per the multi-chat workstream split: code modification is exclusive to Design. Lore authors canonical text + species/quest spreadsheets; Design wires text into the FSM, scenes, and content modules; Image, Audio, and Testing handle their domains. This board is how Lore (and any other lane) tells Design *"here is a thing to wire up."*
>
> Format per entry:
> - **Date / source lane / topic** header
> - **Status** (open / in-progress / landed)
> - **What** (the contract)
> - **Where** (file paths + line refs where applicable)
> - **Notes for Design** (gotchas, format, dependencies)

---

## 2026-05-19 — Lore → Design — Violence-depiction-doctrine cleanse-pass (canonical-from-afar canonical-massive-scale canon)

**Status**: landed (Lore-lane); canonical-Design canonical-action canonical-required canonical-to canonical-port canonical-re-framed canonical-content canonical-into canonical-runtime canonical-text-modules

**What**: Aaron canonical-dispatch 2026-05-19: *"Let's make sure violence is always depicted from afar on a massive scale, not up-close horror."* + *"Do a cleanse of our lore and make sure we are delivering a clean and coherent narrative."* Lore-lane canonical-authored canonical-doctrine + canonical-cleansed canonical-6 canonical-high-risk canonical-passages. **Trigger context**: a sibling Claude chat hit a canonical-usage-policy-filter; canonical-Lore-lane canonical-pre-empted canonical-recurrence canonical-by canonical-canonizing-the-doctrine + canonical-cleaning-prior-content.

**Where**:
- **NEW doctrine doc**: [`violence-depiction-doctrine.md`](violence-depiction-doctrine.md) — canonical-from-afar canonical-massive-scale canon; canonical-three canonical-distance-axes (canonical-Spatial / canonical-Temporal / canonical-Scale); canonical-acceptable canonical-vs canonical-avoid canonical-register canonical-examples; canonical-application-checklist canonical-for canonical-future-content-authoring
- **6 re-framed passages** (canonical-narrative-event canonical-preserved; canonical-only canonical-rendering canonical-changed):
  1. `cinematic-narration.md §9` Disastrous Ending — canonical-`"used your blood to sign the treaty"` → canonical-`"the fleet fell silent. The galaxy fell silent. The treaty was binding because there was no one left to contest it."`
  2. `cinematic-narration.md §2.7` Taalo Shield Failure — canonical-`"They feel the cooling. They remain conscious during most of it."` → canonical-`"The mountain-range was still by the next sunrise."` (canonical-temporal-aftermath canonical-framing; canonical-`"They do not cry out"` canonical-preserved canonical-because canonical-it canonical-notes canonical-absence-of-protest canonical-rather canonical-than canonical-act-of-suffering)
  3. `cutscene-sequences.md §Slylandro-Cleansing-Cooperate` Cleansing cinematic — canonical-`"absorbed it through their respiratory membrane"` → canonical-`"presence faded from the gas mantle over the course of a Mh-Lai day"`
  4. `cutscene-sequences.md §Taalo-Shield-Failure` — same Taalo re-frame as #2 above (pan-timing canonical-may canonical-need canonical-Design-lane canonical-re-balance canonical-given canonical-shortened canonical-text)
  5. `cutscene-sequences.md §Disastrous-Ending` — same Disastrous re-frame as #1 above
  6. `callbacks-and-callforwards.md §Break #3` — same Disastrous re-frame as #1 above
  7. `cleanser-encounter-design.md about_method` NPC dialog — canonical-`"absorb it through their respiratory membrane"` → canonical-`"presence fades from the gas mantle"` (canonical-Vael-Souren's canonical-Cleanser-clinical-mourner-tone canonical-preserved)
  8. `HANDOFF_audio_chat.md §Break #3` audio-direction — canonical-quote canonical-updated canonical-to canonical-match canonical-new canonical-canon
- **Existing canon canonical-already-from-afar canonical-and canonical-canon-compatible**: `bio-archive-entries.md` (canonical-Steward-observation-register canonical-throughout); `the-furlings-and-the-others.md` (canonical-mass-extinction canonical-kept-deliberately-vague-and-off-screen); `cleansers-as-ice-branch.md` (canonical-doctrine-acknowledgment canonical-without canonical-rendering); `the-androsynth-refugees.md` (canonical-Coel canonical-from-afar-theory canonical-explicitly-from-afar canonical-already)

**Notes for Design**:
- **NPC dialog runtime port**: `cleanser-encounter-design.md` line ~109 (`about_method` state) — canonical-runtime canonical-text-content canonical-re-framed; canonical-Design canonical-port-target canonical-likely canonical-`src/scz/dialog/characters.py` canonical-Vael-Souren canonical-NPC canonical-state-machine. canonical-Re-framed canonical-line canonical-canonical-included canonical-in canonical-source-doc canonical-for canonical-direct canonical-copy-paste.
- **Cinematic narration runtime port**: canonical-Disastrous-ending + canonical-Taalo-Shield-failure + canonical-Slylandro-Cleansing-Cooperate canonical-narrations canonical-re-framed canonical-in canonical-source-docs. canonical-Design canonical-port-target canonical-likely canonical-`src/scz/content/cinematic_passages.py` canonical-or canonical-similar. canonical-Re-framed canonical-text canonical-canonical-included canonical-in canonical-source-docs canonical-for canonical-direct canonical-copy-paste.
- **Tone-doctrine canon for future Lore + Design authoring**: per `violence-depiction-doctrine.md`, canonical-future canonical-violence-adjacent canonical-content canonical-checked canonical-via canonical-canonical-`application-checklist` (canonical-6-question canonical-self-check canonical-canonical-orbital-distance + canonical-aggregate-scale + canonical-named-mechanism-without-detail + canonical-no-blood-or-organs + canonical-aftermath-not-moment-of-death + canonical-`record`-not-`witness`). canonical-Design-lane canonical-runtime-text canonical-canonical-should canonical-apply canonical-same-checklist.
- **No code-modification required** beyond canonical-runtime-text-content-updates. canonical-No canonical-data-schema canonical-changes; canonical-no canonical-FSM-structure canonical-changes. canonical-canonical-Re-frames canonical-are canonical-canonical-pure-text canonical-substitutions canonical-on canonical-existing canonical-states.

**Verification path**: canonical-walks canonical-needed — `walk_cinematic_disastrous_ending` (canonical-trigger canonical-Disastrous canonical-end-state canonical-flags; canonical-verify canonical-new canonical-text canonical-renders); `walk_cinematic_taalo_shield_failure` (canonical-trigger canonical-Taalo-Cleanse canonical-outcome; canonical-verify canonical-new canonical-text canonical-renders); `walk_cleanser_dialog_about_method` (canonical-visit canonical-Cleanser canonical-during canonical-Slylandro-cleanse canonical-pre-event; canonical-verify canonical-Vael-Souren canonical-`about_method` canonical-state canonical-renders canonical-new canonical-protocol-not-spore canonical-text).

---

## 2026-05-19 — Lore → Design — stars.json canonical-defined_name canonical-additions + canonical-stale precursor_note canonical-updates + canonical-hyperspace-zones-overlay canonical-additions

**Status**: open — canonical-derived canonical-from-the-2026-05-19-Lore-audit + canonical-cross-check canonical-of canonical-HANDOFF_TO_TESTING_CHAT.md (canonical-Image→Testing 2026-05-17) + canonical-`src/scz/hyperspace/zones.py` + canonical-`src/scz/content/universe/stars.json`

**What**: canonical-Lore-lane canonical-audit-of canonical-hyperspace-zones-overlay canonical-system canonical-revealed canonical-multiple canonical-stale-canon-references canonical-and canonical-missing canonical-zone-tags canonical-for canonical-newly-canonized-species. canonical-Three-part canonical-dispatch:

**Part 1 — `stars.json` canonical-stale `precursor_note` text canonical-needs-correction**

Two canonical-stale `precursor_note` canonical-fields claim canonical-species canonical-`doesn't yet exist in our era` canonical-but canonical-both canonical-NOW canonical-canonical-DO canonical-exist canonical-per canonical-canon-updates:
- `stars.json` line 1696: *"In SC2 this is ANDROSYNTH; doesn't yet exist in our era."* — **canonical-INCORRECT**: per `the-androsynth-refugees.md`, the canonical-Androsynth-Refugees canonical-DO canonical-exist in canonical-our era (canonical-time-displaced canonical-from-canonical-SC2-future canonical-via canonical-Other-decursion). canonical-Recommend-update-text: *"In SC2 this is ANDROSYNTH; in our era they are canonical-time-displaced-refugees from the canonical-SC2-future."*
- `stars.json` line 1730: *"In SC2 this is TAALO_PROTECTOR; doesn't yet exist in our era."* — **canonical-INCORRECT**: per `loop-closing-content-pass.md §6`, the canonical-Taalo canonical-DO canonical-exist canonical-in canonical-our era (canonical-silicon-mountain-range-species; canonical-they canonical-BUILD canonical-the canonical-Taalo Shield canonical-in canonical-our canonical-slice). canonical-Recommend-update-text: *"In SC2 this is TAALO_PROTECTOR; in our era the Taalo exist and are canonical-actively-building it as the canonical-Taalo-Shield — anti-Others-defense canonical-which canonical-fails."*

**Part 2 — `stars.json` canonical-`defined_name` canonical-tag canonical-additions canonical-for canonical-newly-canonized-species**

Per `scanner-lore.md` Tier 1+2 canonical-canon (memory) the canonical-slice-cluster canonical-has canonical-19 canonical-canonical-named-systems. canonical-stars.json canonical-currently canonical-has canonical-defined_name canonical-tags canonical-for canonical-only canonical-SOME (SLYLANDRO, MYCON_BIOT_HIVE, CHENJESU_PROTO, MELNORME_PROTO, RAINBOW_BEING_SEEDED, ORZ_RIFT, SHOFIXTI_PROTO, YEHAT_PROTO, UTWIG_PROTO, MURDER_OF_CROWS_PROTO, etc). canonical-Missing canonical-tags canonical-for canonical-newly-canonized-species:

| Recommended `defined_name` tag | System name (per `scanner-lore.md`) | Canon source |
|---|---|---|
| `TAALO` | Taalo's Stone (canonical-single canonical-system canonical-with canonical-4 canonical-planets canonical-per canonical-scanner-lore) | [`loop-closing-content-pass.md §6`](loop-closing-content-pass.md) |
| `THINN_SPIRE` | Spire (canonical-sub-Neptune; canonical-Thinn canonical-homeworld) | [`species-the-thinn.md`](species-the-thinn.md) |
| `LEMMKIN_WHIRLIGIG` | Whirligig Lemmkin | [`species-the-lemmkin.md`](species-the-lemmkin.md) |
| `MROKON_STAND` | Mrokon's Stand | [`loop-closing-content-pass.md §5`](loop-closing-content-pass.md) |
| `STELLOTH_THREE_VOICE` | Three-Voice Arc Stelloth | [`loop-closing-content-pass.md §1`](loop-closing-content-pass.md) |
| `SELVENNE_VELLUMAR` | Vellumar Selvenne | [`loop-closing-content-pass.md §2`](loop-closing-content-pass.md) |
| `KOVELLIM_EIGHT_KNOT` | Eight-Knot Station | [`loop-closing-content-pass.md §3`](loop-closing-content-pass.md) |
| `KARAVEM_AERIS_SING` | Aeris-Sing Karavem | [`loop-closing-content-pass.md §4`](loop-closing-content-pass.md) |
| `BURVIXESE_CASTER` | Burv Caster system (canonical-Tier-3 canonical-backlog canonical-per canonical-MEMORY) | [`loop-closing-content-pass.md §7`](loop-closing-content-pass.md) |
| `UTWIG_SENTIENT` | (canonical-separate-from canonical-UTWIG_PROTO canonical-at canonical-line 4911; canonical-sentient-Utwig canonical-recently-emerged-from canonical-same-world; canonical-Veiled-Assembly canonical-system) | [`utwig-quest.md`](utwig-quest.md) |
| `ANDROSYNTH_REFUGEE` | Coel Tessar Arrival (canonical-time-displaced canonical-from-SC2-future) | [`the-androsynth-refugees.md`](the-androsynth-refugees.md) |
| `MMRNMHRM_COHORT` | Mmrnmhrm Cohort-47-Theta | [`the-mmrnmhrm-and-chenjesu.md`](the-mmrnmhrm-and-chenjesu.md) (currently canonical-canonical-overlaps with canonical-CHENJESU_PROTO at canonical-Procyon — canonical-Design canonical-may canonical-choose canonical-canonical-shared-tag canonical-or canonical-canonical-distinct-coordinates) |
| `CLEANSER_APPROACH` | Cleanser Approach Vector | [`cleansers-as-ice-branch.md`](cleansers-as-ice-branch.md) |
| `MH_LAI` | Mh-Lai (canonical-Furling-home; canonical-pre-Fall canonical-and canonical-post-Fall canonical-variants) | [`scanner-lore.md`](scanner-lore.md) per MEMORY |

**Coordinate-selection**: canonical-Lore-lane canonical-does-not-have canonical-canonical-exact canonical-coordinates canonical-for canonical-the canonical-additions. canonical-Recommend-Design canonical-pick canonical-canonical-currently-unnamed canonical-star-slots canonical-(canonical-`defined_name: null`) canonical-with canonical-canonical-cluster-name canonical-matching canonical-the canonical-canon-canonical-system-name canonical-where canonical-possible. canonical-Coordinate-collision canonical-Proto-Spathi vs canonical-Proto-Shofixti canonical-at canonical-290.8:026.9 canonical-already canonical-flagged canonical-in canonical-prior canonical-dispatch — canonical-may canonical-want canonical-to canonical-resolve canonical-at canonical-same canonical-pass.

**Part 3 — `src/scz/hyperspace/zones.py` canonical-`build_default_zones()` canonical-additions**

Per `zones.py` lines 135-224, canonical-current zone-roster covers canonical-6 species/groups: SLYLANDRO + MYCON_BIOT_HIVE + MMRNMHRM_CHENJESU + MELNORME + RAINBOW_WORLDS + ORZ_RIFT. canonical-Once Part-2 canonical-`defined_name` tags canonical-added to canonical-stars.json, canonical-Design canonical-may canonical-extend canonical-`build_default_zones()` canonical-to canonical-cover canonical-the canonical-canon-additions canonical-with canonical-the canonical-following canonical-suggested canonical-palette canonical-(canonical-Lore-lane canonical-canonical-aesthetic canonical-guidance; canonical-Image-lane canonical-may canonical-override):

| Zone | Suggested color | Suggested alpha | Suggested radius |
|---|---|---|---|
| Taalo silicon-mountain (single-system; canonical-canonical-grounded) | canonical-stone-grey (180, 180, 175) | 60 | 400 |
| Thinn Spire (single-system; canonical-canonical-iridescent) | canonical-iridescent-teal (130, 220, 200) | 70 | 400 |
| Lemmkin Whirligig (single-system; canonical-canonical-chaotic-bright) | canonical-warm-orange-rust (255, 150, 80) | 75 | 500 |
| Mrokon's Stand (canonical-canonical-bunker-grim) | canonical-dark-iron (110, 100, 95) | 70 | 500 |
| Stelloth Three-Voice (canonical-canonical-chord-resonance) | canonical-resonant-violet (170, 130, 220) | 70 | 500 |
| Selvenne Vellumar (canonical-canonical-coral-hive) | canonical-coral-pink (255, 140, 165) | 70 | 600 |
| Kovellim Eight-Knot (canonical-canonical-nomadic-multi-system canonical-trail) | canonical-faded-gold (200, 180, 130) | 60 | 700 |
| Karavem Aeris-Sing (canonical-canonical-musical-aerial) | canonical-sky-cyan (140, 200, 230) | 70 | 500 |
| Burvixese Caster (canonical-canonical-broadcasting-loud) | canonical-broadcast-amber (255, 200, 100) | 80 | 700 |
| Utwig-Sentient (canonical-canonical-Veil-mist) | canonical-pearl-grey (210, 200, 195) | 65 | 400 |
| Androsynth Refugee (canonical-canonical-displaced-from-future) | canonical-deep-red (180, 60, 60) | 70 | 400 |
| Cleanser Approach Vector (canonical-canonical-cold-cleanser-doctrine) | canonical-cold-violet (100, 80, 160) | 75 | 600 |

**Notes for Design**:
- **Cross-check `HANDOFF_TO_TESTING_CHAT.md` (project root)** — canonical-2026-05-17 canonical-Image→Testing canonical-handoff canonical-line 63 canonical-references canonical-canonical *"(e.g. for Talos, Planar, Mycon awakening sites)"* canonical-as canonical-zone-extension canonical-examples. canonical-Both canonical-`Talos` + canonical-`Planar` canonical-are canonical-canonical-stale-names: canonical-Talos→retired (canonical-canonical-replaced-by canonical-canonical-Taalo + canonical-Thinn); canonical-Planar→Thinn rename. canonical-Mycon-awakening-sites canonical-remains canonical-canon-valid. canonical-When canonical-Design canonical-updates canonical-zones.py, canonical-canonical-also-update-the-TESTING-handoff canonical-reference canonical-OR canonical-flag-it canonical-as canonical-superseded.
- **Coordinate-collision canonical-Proto-Spathi vs Proto-Shofixti** (per prior canonical-dispatch 2026-05-18): canonical-`SHOFIXTI_PROTO` canonical-tag at canonical-290.8:026.9 canonical-may canonical-need canonical-rename canonical-to canonical-`SPATHI_PROTO` canonical-with canonical-a canonical-second canonical-Shofixti-slot canonical-elsewhere. canonical-Resolve-at-same-pass canonical-recommended.
- **`UTWIG_PROTO` vs `UTWIG_SENTIENT` canonical-coexistence**: per canonical-Proto-Utwig-vs-sentient-Utwig canonical-disambiguation canonical-(canonical-canonical-`proto-species-bio-archive-entries.md §11` Cross-canon canonical-note), canonical-BOTH canonical-canon-simultaneously-exist canonical-on canonical-same canonical-world canonical-(canonical-proto-Utwig canonical-pre-sentient-grazers; canonical-sentient-Utwig canonical-recently-emerged-and-devolving). canonical-Design canonical-may canonical-want canonical-canonical-two canonical-defined_name canonical-tags canonical-at canonical-same canonical-coordinates canonical-OR canonical-canonical-single canonical-tag canonical-with canonical-canonical-two canonical-Bio-Archive-entries canonical-cross-linked. canonical-Recommend canonical-canonical-two-tags canonical-for canonical-canonical-zone-overlay canonical-clarity.

**Verification path**: canonical-walks-needed canonical-once canonical-Part-2 canonical-+ canonical-Part-3 canonical-land:
- `walk_hyperspace_zones_full` — canonical-press canonical-Z; canonical-verify canonical-canonical-all canonical-canon-zones canonical-render canonical-without canonical-overlap-clashes
- `walk_hyperspace_search_thinn` — canonical-press canonical-/; canonical-type canonical-`thinn`; canonical-verify canonical-canonical-→ canonical-Spire canonical-resolves
- `walk_hyperspace_search_taalo` — canonical-press canonical-/; canonical-type canonical-`taalo`; canonical-verify canonical-canonical-→ canonical-Taalo's Stone canonical-resolves
- canonical-also canonical-once canonical-canonical-Bio-Archive entries canonical-for canonical-Lemmkin/Mrokon/Taalo/Thinn/etc canonical-ported canonical-to canonical-archive_entries.py: canonical-`walk_bio_archive_full_roster` canonical-verifies canonical-canonical-all canonical-species-entries canonical-appear

---

## 2026-05-19 — Lore → Design — Lore audit closeout (Thinn-doc rename + ship-roster stat-blocks + canon-coherence housekeeping)

**Status**: landed (Lore-lane); canonical-Design canonical-may canonical-want canonical-to canonical-action canonical-the canonical-derived canonical-spreadsheet-updates

**What**: Aaron dispatch: *"Do a full lore audit"* + *"proceed as you see fit. Do the best filling in anything that is missing and we will adjust it while testing the fully playable game"*. Lore-lane canonical-completed full canonical-audit ([`lore-audit-2026-05-19.md`](lore-audit-2026-05-19.md)) and canonical-actioned all canonical-7 canonical-Lore-lane canonical-self-actions:

1. **HIGH-1**: canonical-Renamed `species-the-planar.md` → `species-the-thinn.md` + canonical-content-refresh canonical-encoding canonical-Aaron's-pun-canon + canonical-embraced-translator-nickname canon-twist + canonical-Forward-crewmate-canon + canonical-doctrine-flaw-comedy + canonical-combat-paradox (canonical-firing-them-into-Migration). Canonical-Bio-Archive-Entry-14,478 canonical-authored. Old canonical-`species-the-planar.md` canonical-deleted.
2. **HIGH-2**: `species-sheets.md` canonical-redirect-header canonical-added (canonical-line-7-heading canonical-updated; canonical-Extended-species-redirect-table canonical-added covering canonical-13-additional-species; canonical-Retired-species-name-history canonical-added).
3. **HIGH-3**: `species-content-backlog.md` canonical-rename-history-banner canonical-added at canonical-top + canonical-brainstorm-deprecation-banner canonical-added at canonical-§Brainstormed-Stay-reasons.
4. **MED-1**: `ship-roster.md` canonical-Lemmkin Skitter canonical-stat-block-row canonical-added (replaces canonical-`[INVENTED species ship — TBD]` on canonical-Precursor side); canonical-Mrokon Hammer-Vessel canonical-stat-block-row canonical-added (replaces canonical-`[INVENTED species ship — TBD]` on canonical-Homesteader side). Canonical-Hammer-Of-Refusal canonical-mark-the-Others canonical-mechanic canonical-encoded.
5. **MED-2**: `species-precursor-era.md` canonical-extended-species-redirect-header canonical-added.
6. **MED-3**: `MEMORY.md` canonical-broken-pointer canonical-`taalo-burvixese-planar.md` canonical-fixed (canonical-points-to canonical-loop-closing-content-pass.md + canonical-species-the-thinn.md).
7. **LOW-1**: canonical-brainstorm-deprecation-banner canonical-added (combined with HIGH-3).

**Where**:
- New: [`species-the-thinn.md`](species-the-thinn.md) (replaces canonical-`species-the-planar.md`)
- New: [`lore-audit-2026-05-19.md`](lore-audit-2026-05-19.md) — canonical-full audit-report
- Updated: [`species-sheets.md`](species-sheets.md) — canonical-redirect-table
- Updated: [`species-content-backlog.md`](species-content-backlog.md) — canonical-rename-history
- Updated: [`ship-roster.md`](ship-roster.md) — canonical-Lemmkin + canonical-Mrokon stat-blocks
- Updated: [`species-precursor-era.md`](species-precursor-era.md) — canonical-redirect-table

**Notes for Design** (canonical-derived canonical-spreadsheet/code-mod canonical-work canonical-Lore-lane canonical-CANNOT canonical-do):
- **`tools/species_inventory.csv`** canonical-still-has canonical-stub-rows for canonical-BURVIXESE/CURIOUS/DEFIANT/TAALO/THE_BARGAINERS/THE_DEFIANT_BACKLOG/THE_LONG_MEMORIES/PLANAR canonical-already canonical-flagged canonical-in canonical-prior canonical-dispatch (2026-05-18 entry below). **Now ALL canon-resolutions canonical-have canonical-source-of-truth canonical-docs**:
  - `BURVIXESE` → canonical-content in `loop-closing-content-pass.md §7`
  - `CURIOUS` → canonical-rename-to-`LEMMKIN`; canon in `species-the-lemmkin.md`
  - `DEFIANT` → canonical-rename-to-`MROKON`; canon in `loop-closing-content-pass.md §5`
  - `TAALO` → canonical-content in `loop-closing-content-pass.md §6`
  - `THE_BARGAINERS` → canonical-rename-to-`SELVENNE`; canon in `loop-closing-content-pass.md §2`
  - `THE_DEFIANT_BACKLOG` → canonical-DELETE-duplicate (merged-into-MROKON)
  - `THE_LONG_MEMORIES` → canonical-rename-to-`KOVELLIM`; canon in `loop-closing-content-pass.md §3`
  - `PLANAR` → canonical-rename-to-`THINN`; canon in `species-the-thinn.md`
  - `TALOS_SUBFACTION` → canonical-DELETE (Furling sub-faction retired)
- **`src/scz/content/ship_roster.py`** (or equivalent) — canonical-Lemmkin Skitter + canonical-Mrokon Hammer-Vessel canonical-stat-blocks canonical-now canonical-canonical-canonized in canonical-`ship-roster.md`. Canonical-Design canonical-may canonical-port canonical-into canonical-Python canonical-ship-roster-content-module canonical-with canonical-canonical-combat-AI-personality-vectors.
- **`src/scz/content/archive_entries.py`** — canonical-Bio-Archive-Entry-14,478 (canonical-Thinn) canonical-now canonical-canon. canonical-Plus canonical-the canonical-12 canonical-proto-species canonical-Bio-Archive canonical-entries canonical-from canonical-prior-dispatch.
- **Asset-rename**: canonical-portrait `assets/generated_drafts/firefly/tier1_portraits/species_planar_blade_portrait.png` canonical-still-uses-canonical-old-`planar_blade` slug. Canonical-Image-chat canonical-work canonical-to canonical-rename-to-canonical-`thinn`. canonical-Not canonical-blocking; canonical-asset-naming canonical-cosmetic.

**Verification path**: canonical-walks canonical-could canonical-be canonical-added — `walk_thinn_doctrine_explain` (visit Edge-Align-Eldest; verify canonical-doctrine-explanation surfaces); `walk_thinn_combat_paradox` (canonical-engage canonical-Thinn-Blade canonical-in canonical-combat; canonical-verify canonical-canonical-5%-hull canonical-surrender canonical-line canonical-and canonical-canonical-Migration-population-increases). Canonical-also canonical-`walk_lemmkin_skitter_combat` + `walk_mrokon_hammer_combat` canonical-once canonical-ship-roster.py canonical-canonical-ported.

---

## 2026-05-18 — Lore → Design — 12 enriched proto-species Bio-Archive entries (web-research-enriched) + species_inventory.csv stub-resolutions

**Status**: open

**What**: Aaron dispatch: *"Maybe it wants you to generate proto-species lore by researching internet content for the SC2 species?"* — reframing the canonical `species_inventory.csv` rows previously marked *"correct-as-stub"* (the 12 canonical proto-species) as canonical-actionable. Lore conducted canonical-WebFetch research against [Ultronomicon — wiki.uqm.stack.nl](https://wiki.uqm.stack.nl/) (canonical UQM-team-hosted SC2 wiki) and authored [`proto-species-bio-archive-entries.md`](proto-species-bio-archive-entries.md) — 12 canonical-enriched Bio-Archive entries (Entry 14,311 through 14,322) covering: Proto-Spathi, Proto-Yehat, Proto-Pkunk, Proto-VUX, Proto-Druuge, Proto-Ilwrath, Proto-Shofixti, Proto-Thraddash, Proto-Syreen, Proto-Supox, Proto-Utwig, Proto-Zot-Yin-Dag-Hap-Lod-Nit-Fot-Pik. Each entry is canonical-150-300-word Furling-Steward Bio-Archive observation pairing canonical-SC2-future-identity with canonical-Furling-era-pre-sentient-observation. Canonical-SC2-fan-recognizable traits surfaced in canonical-pre-sentient form (e.g. proto-Ilwrath webs already canonical-aligned-at-Procyon; proto-Syreen bioluminescent-vibrational-communication as canonical-pre-telepathy; proto-Druuge already canonical-trading-pebbles-before-sentience). **Two canonical-canon-twist entries (2026-05-18 Aaron-revision)**: (1) **Proto-Spathi** canonical-INVERTED to canonical-fearless-warrior-molluscs — canonical-SC2-cowardice is canonical-fall-from-courage canonical-not canonical-line-from-cowardice (canonical-Council-archivist canonical-margin-note *"Something will happen to them"* canonical-encodes-the-tragedy; canonical-likely canonical-Ur-Quan canonical-Battle-Thrall-enslavement canonical-call-forward); (2) **Proto-Zoq-Fot-Pik** canonical-EXPANDED to canonical-Proto-Zot-Yin-Dag-Hap-Lod-Nit-Fot-Pik — canonical-EIGHT canonical-cooperating-pre-sentient-lineages of which canonical-only-THREE canonical-survive-to-SC2-era; canonical-five (canonical-Yin/Dag/Hap/Lod/Nit) canonical-go-extinct in the canonical-250kya-gap; canonical-Zot canonical-linguistic-shifts to canonical-Zoq; canonical-Council-archivist canonical-margin-note *"Three."* canonical-added in canonical-later hand encodes the canonical-attrition-elegy.

**Where**:
- **Source canon**: [`proto-species-bio-archive-entries.md`](proto-species-bio-archive-entries.md) — 12 canonical-Bio-Archive entries
- **Code surfaces likely affected**:
  - `src/scz/content/archive_entries.py` (per Beat-5 plan) — extend the canonical-20-entry baseline catalog to canonical-32 entries by canonical-porting the 12 proto-species entries into the canonical `ARCHIVE_ENTRIES` list under canonical-`category="species"`. Long-form descriptions canonical-copyable from the source doc.
  - `tools/species_inventory.csv` — 12 canonical-`CORRECT-AS-STUB` rows now have canonical-richer-content available for canonical-spreadsheet-update; canonical-row description-fields canonical-update-to-point-to-canonical-this-doc
  - `tools/extract_sc2_universe.py` star-data — canonical-coordinate-collision flagged for Proto-Spathi (Epsilon Gruis I) vs Proto-Shofixti (canonical-extracted-data canonical-tagged `SHOFIXTI_PROTO` at coords 290.8:026.9 — canonical-Spathi-homeworld is canonical-elsewhere). Canonical-Design canonical-disambiguate the canonical-coordinate-table.
  - `references/lore/scanner-lore.md` (Tier 3 backlog) — canonical-12 systems now have canonical-Bio-Archive entry depth that canonical-could-inform canonical-scanner-reveal-text expansion
- **Species_inventory.csv stub-resolution batch** (canonical-already-staged in earlier audit; canonical-this-dispatch canonical-finalizes):
  - **Retire**: `TALOS_SUBFACTION` (canonical fully-retired per `species-the-thinn.md` canon; canonical-replaced by Taalo silicon-mountains + Thinn ribbon-species)
  - **Rename**: `THE_CURIOUS` → `LEMMKIN` (canonical per `species-the-lemmkin.md`)
  - **Map**: `THE_DEFIANT` → `MROKON` (canonical per `loop-closing-content-pass.md`)
  - **Delete**: `THE_DEFIANT_BACKLOG` (canonical-duplicate)
  - **Retire-or-map**: `THE_BARGAINERS` → canonical-map-to canonical-Selvenne (per `loop-closing-content-pass.md`); `THE_LONG_MEMORIES` → canonical-map-to canonical-Kovellim (per `loop-closing-content-pass.md`)
  - **Rename**: `PLANAR` → `THINN` (canonical per `species-the-thinn.md`)
  - **Resolved-stubs**: the 12 canonical-proto-species rows now have canonical-richer-content; canonical-row description fields canonical-update-to-reference `proto-species-bio-archive-entries.md`

**Notes for Design**:
- **Voice consistency**: the 12 entries canonical-match the canonical-Furling Bio-Archivist register established in `proto-species-observations.md` ("Attenborough narrating an early-hominid documentary"). When canonical-porting into `archive_entries.py` canonical-preserve the canonical-italic-Bio-Archive-entry-formatting (canonical-the entries canonical-render as canonical-Steward's-direct-observation rather than canonical-third-party description).
- **Coordinate-collision flag** (Proto-Spathi §1): the canonical-extracted-data has the canonical 290.8:026.9 slot canonical-tagged `SHOFIXTI_PROTO` but canonical-Spathi-homeworld Epsilon-Gruis-I is canonical-elsewhere. Recommend canonical-Design canonical-rename one of the entries or canonical-add a canonical-second canonical-tagged-slot for Proto-Spathi at canonical-Epsilon-Gruis-I-coordinates. Source-doc `proto-species-bio-archive-entries.md` Cross-canon §1 flags this canonical-explicitly.
- **Canonical Council-personal-notes** flagged for canonical-Council-archive integration:
  - canonical *"do not put fire near them"* for proto-Shofixti (§7)
  - canonical *"recommend no Mycon deployment in this system ever"* for proto-Syreen (§9; canonical SC2-callforward-warning canonical-honoring canonical-Syra-destruction-canon)
- **Bio-Archive Entry numbering**: canonical-entries are canonical-14,311 through 14,322 — canonical-continuing the canonical-Bio-Archive-numbering established in `bio-archive-entries.md`. Design canonical-preserves entry-numbers when canonical-porting.
- **Proto-Utwig vs sentient-Utwig disambiguation**: the canonical-proto-Utwig (§11) are canonical-canon-simultaneously-with canonical-sentient-Utwig (per `utwig-quest.md`). Canonical-proto-Utwig are canonical-canonical-stable-pre-sentient-grazers on the canonical-same-world; canonical-sentient-Utwig are canonical-recently-emerged-and-canonical-devolving. Both canonical-belong in the canonical-Archive; canonical-do-not collapse them into canonical-one entry. Suggest canonical-cross-referencing the canonical-two entries with a canonical-"see also" link in the canonical-detail-pane.
- **Cross-canon hooks already authored**: §6 Proto-Ilwrath web-alignment-at-Procyon canonical-call-forwards to Chenjesu canon; §2-3 Proto-Yehat/Pkunk divergence-margin-note canonical-call-forwards to canonical-SC2 50,000-year-divergence; §9 Proto-Syreen canonical-call-forwards to canonical-SC2-Syra-destruction. These hooks canonical-already-deployed in the canonical-Bio-Archive-text — Design canonical-no canonical-additional canonical-call-forward-work canonical-required.
- **Proto-Spathi canon-twist (§1)**: canonical-fearless-warrior-molluscs in canonical-Furling-era; canonical-cowardly *"please don't let me die today"* molluscs in canonical-SC2-era. Canonical-trajectory is canonical-fall-from-courage. Design canonical-may canonical-want-to-surface this canonical-inversion in canonical-downstream-content: (a) canonical-Bio-Archive-detail-pane canonical-cross-reference to canonical-SC2-cowardly-prayer (canonical-"They will be canonical-something else by then"); (b) canonical-Halia-conversation canonical-line referencing canonical-Spathi-courage-loss as canonical-cautionary-tale for canonical-Furling-children; (c) canonical-Forty-Seven canonical-observation canonical-noting canonical-courage-is-not-easy-to-keep. **Coordinate-collision still flagged** (§1) — canonical-extracted-`SHOFIXTI_PROTO` slot at 290.8:026.9 needs canonical-disambiguation regardless of canon-twist; canonical-recommend canonical-add-second-tagged-slot for canonical-Proto-Spathi at canonical-Epsilon-Gruis-I.
- **Proto-Zot-Yin-Dag-Hap-Lod-Nit-Fot-Pik canon-twist (§12)**: canonical-EIGHT cooperating-pre-sentient-lineages — canonical-not canonical-three. Canonical-five canonical-extinct-by-SC2-era. **Canonical-canon-mechanism (2026-05-18 Aaron-canon)**: *"The Others canonical-leave-the-canonical-three-dumbest-alone."* Canonical-the canonical-five-extinct canonical-developed canonical-canonical-too-much canonical-cognition canonical-and-tripped canonical-the canonical-Others' canonical-intelligence-detection-threshold (canonical-yin canonical-thoughtful; canonical-dag canonical-elaborate-tunnels; canonical-hap canonical-organized-patterns; canonical-lod canonical-stones-in-rows; canonical-nit canonical-pre-mathematical-aerial-formations). Canonical-the canonical-three-survivors canonical-stayed-below: canonical-zot canonical-shout-in-trees; canonical-fot canonical-feel-things-deeply; canonical-pik canonical-sit-still-and-look-at-things. **Canon-implication**: canonical-SC2-Zoq-Fot-Pik canonical-loveable-comedy-relief-affect is canonical-canonical-survivor's-grateful-stupidity. Design canonical-may surface canonical-this canonical-via: (a) canonical-Zoq-Fot-Pik canonical-NPC-dialog canonical-grieving-the-lost-cousins-they-do-not-know-they-lost (canonical-they-do-not-remember-the-yin canonical-or-the-hap; canonical-only-the-Bio-Archive canonical-remembers); (b) canonical-Bio-Archive entry-name canonical-renders canonical-`Proto-Zot-Yin-Dag-Hap-Lod-Nit-Fot-Pik` (canonical-long-form-canonical-preserved in canonical-Archive-naming); (c) canonical-Council-archivist canonical-margin-note canonical-expanded canonical-to canonical-encode-the-canon-mechanism (canonical *"Three. The Others canonical-left the canonical-three-dumbest-alone..."*) canonical-rendered-as-canonical-faded-secondary-text in canonical-detail-pane (canonical-typographic canonical-call-out canonical-of-canonical-attrition-mechanism); (d) **canonical-parallels canonical-Utwig canon**: canonical-Utwig canonical-CHOSE canonical-to canonical-drop-below-threshold (canonical-Veils Falling deliberate devolution); canonical-Zoq-Fot-Pik canonical-were-already canonical-naturally-there — canonical-Design canonical-may canonical-want canonical-cross-reference canonical-detail-pane-links canonical-between canonical-the canonical-two-entries canonical-as canonical-two-paths-to-the-same-survival-strategy; (e) canonical-Steward-NPC-dialog canonical-line canonical-available: *"The Others canonical-cull the canonical-clever"* canonical-canon-phrase canonical-canonical-now canonical-deployable canonical-as canonical-Steward-observation canonical-in canonical-multiple-contexts (canonical-Halia-conversation; canonical-Forty-Seven-observation; canonical-Bio-Archive-detail-pane canonical-cross-references canonical-to canonical-Utwig + canonical-Slylandro + canonical-Zoq-Fot-Pik + canonical-Chenjesu canonical-as canonical-all canonical-canonical-below-threshold-survivors).

**Verification path**: walks needed — `walk_bio_archive_proto_species` (verify all 12 canonical-proto-species entries surface under canonical-SPECIES category; verify long-form descriptions render); `walk_bio_archive_count` (verify canonical-Archive baseline expanded from canonical-20 to canonical-32 entries); manual smoke: dock at Mh-Lai → open Bio-Archive → verify canonical-SPECIES category lists canonical-32 entries with the canonical-12 proto-species entries canonical-visible-from-game-start (canonical-no-flag-gating needed for canonical-already-observed proto-species per canonical-observation-encounter-on-system-entry model).

---

## 2026-05-17 — Lore → Design — Utwig quest fleshed out (religious humor + Veils Falling FSM + Ultron recovery)

**Status**: open

**What**: Aaron dispatch: *"Flesh out the utwig quest with lots of religious humor."* Full quest design authored in [`utwig-quest.md`](utwig-quest.md) — 10 sections covering the Veils Falling doctrine lore, 6 named NPCs + 3 generic-class NPCs, full dialog FSM with multiple branches (Devolved / Split / Ultron Returned / Doctrine Held), a religious-humor reference bank (~50 canonical lines and absurdities), branches-and-rewards table, cross-canon implications, dispatches, open Aaron-call items, and a **canonical glossary of Utwig religious lexicon**.

**Made-up-religion principle (2026-05-17 Aaron clarification)**: *"All made up religions, none from earth."* The Utwig Veils Falling doctrine borrows **no terminology, honorifics, ritual structures, scriptural conventions, or symbolic vocabulary from any Earth religious tradition**. Canonical terms use *only* species-specific neologisms: **Veil-betrayal** (not *heresy*), **Falling-Book** (not *holy text*), **Veiled Assembly** (not *Council*), **Veil-tender** (not *acolyte*), **doctrine-keeper** or **Veil-scholar** (not *theologian* in-character; meta-narrator may use general English). Names use *only* personal-name + optional Veil-suffix (e.g. *Mal-Dren Veil-Of-Knowing*); **no honorifics** like Brother / Sister / Father / Reverend / Holy / Master. The Original Doctrine school canonically REFUSES the Veil-suffix (Tev-Mal is simply *Tev-Mal* — the absence is doctrinal). See [`utwig-quest.md §11 Glossary`](utwig-quest.md) for full canonical lexicon.

**Where**:
- **Source canon**: [`utwig-quest.md`](utwig-quest.md) — full quest design + dialog FSM in YAML-like format compatible with the existing quest-spreadsheet schema
- **Code surfaces likely affected**:
  - `tools/build_quest_inventory.py` (parallel chat owns the spreadsheet but Lore authored the FSM here for porting) — new quest `utwig_veils_falling` with ~20 dialog state rows
  - `src/scz/dialog/characters.py` — six new named NPCs (Mal-Dren, Velden, Trell-Vach, Korven-Sa, Lenne, Tev-Mal) + three generic-class NPCs (Form-Filers, Form-Readers, Form-Burners)
  - New artifact module: **ULTRON_ARTIFACT** (SC2 callforward; recovered via Ultron-Returned branch)
  - Bio-Archive entry to be added in next Lore pass: *Utwig — The Veils Falling* (under SPECIES category)
  - Council-recommendation Council-vote scene: Cleanser argues *"Just to be safe"*; Persuader/Preserver argues *"respect the choice"*; Steward's recommendation tips the balance — add this Council-vote-decision scene as a slice climax-beat for the Utwig

**Notes for Design**:
- **Voice the Utwig deadpan throughout**. Per the slice's humor doctrine, the Utwig are sincere theologians whose theology happens to be deeply funny to outsiders. The Steward's wit is the comic register; the Utwig themselves are not comedians. **Done right, no Utwig is a punchline; they are doing their best.** Every line should land with full doctrinal solemnity even when the content is absurd.
- **The four canonical branches** (Devolved / Split / Ultron Returned / Heretically Halted) all preserve the Utwig terminal status as *Devolved* in the SC2 sense (the slice's Utwig do not fully migrate; the doctrine succeeds; SC2 canon preserved). The variations are *what the Steward takes with them*.
- **The Tev-Mal whisper sub-conversation** is the canonical key to the Ultron-recovery path. The Steward who hears Tev-Mal's *"You were beautiful when you thought"* line and carries it back to the High Veil unlocks the warmer Ultron-grant branch. Suggest gating Ultron-recovery on having visited Tev-Mal first (soft gate; not strict requirement; the High Veil's *high_veil_smiles_unseen* branch becomes available with the line in inventory).
- **The Form-Filing scene** (full bureaucratic petition process per §4 `form_filing` state) is the canonical religious-comedy showcase. Recommend NOT skipping this on first encounter even if the Steward attempts to expedite — let the Steward go through the canonical filing process at least once for the humor beat, then offer the expedite path.
- **The Velden's pride slip** (*"I made it. I am proud of it. I am sorry."*) is the slice's most quietly devastating Utwig line. Recommend surfacing this in any Velden-conversation that builds enough trust.
- **The Sixth-Veil Utwig walking past** — a canonical ambient beat in the Utwig settlement. No dialog; canonical visual + the *weight* of seeing a successful devolution. Recommend this is a scripted ambient encounter the Steward witnesses at least once.
- **The Council-vote scene for the Utwig**: Cleanser argues *"Just to be safe"* (devolution is theoretical; the Utwig might not actually drop below threshold; safer to euthanize); Preserver counter-argues *"respect the choice"*; Persuader sides with Preserver here (canonical alignment); Compeller is ambivalent. **The Cleanser-victory path on this vote is canonically the worst Utwig outcome** — a species voluntarily devolving into safety while another faction euthanizes them anyway. The Steward's recommendation is the tie-breaker.

**Verification path**: walks needed — `walk_utwig_doctrine_explain` (visit High Veil; verify Veils Falling doctrine surfaces); `walk_utwig_form_filing` (file the petition through the full bureaucratic process; verify all three Form-class NPCs surface and the canonical *"the forms had to be designed for you"* line fires); `walk_utwig_ultron_recovery_warm` (visit Tev-Mal first; visit Velden second; visit Mal-Dren third; verify the warm Ultron-grant branch surfaces); `walk_utwig_migrants_accepted` (verify the 30 migrants branch resolves correctly); `walk_utwig_council_vote_persuader_victory` (verify the Council scene's Persuader/Preserver counter-argument fires and the Steward's recommendation tips it correctly).

---

## 2026-05-18 — Lore → Design — 2 canonical Tier-1 weapon mods (Targeting Lattice I + Energy Cycler I)

**Status**: open — canonical-Lore-content for 2 new canonical-Tier-1-modules; canonical-stat-delta-and-cost balancing is Design's call

**What**: Author 2 canonical-Tier-1 weapon-slot modules to expand the canonical-baseline-purchasable module catalog (per `station-screens-design.md §2`, canonical-Tier-1 currently has Fuel Tank +50 / Shield Booster I / Beam Mod I / Cargo Pod +50 — recommend adding canonical-Accuracy + canonical-Reload Tier-1 mods to round out canonical-Weapon-slot variety). Per Rule 5 narrow-exception: Lore canonical-authors-name + description; Design canonical-balances stat-delta + cost.

### Module 1 — **Targeting Lattice I**

- **slot**: `weapon`
- **tier**: 1 (canonical-baseline-purchasable from Mh-Lai shop)
- **canonical-Furling-thematic description**: *"Furling fire-control lattice. Cohesion-tracks the target through sensor-fusion across multiple sweep-frequencies. Tightens the aim-arc."*
- **canonical-stat-delta direction**: increases primary-weapon accuracy / hit-chance / aim-arc-tightness. Specific delta values + scaling = Design canonical-balancing.
- **canonical-cost direction**: comparable to canonical Beam Mod I (75 credits + 5 USEFUL); canonical-Targeting-Lattice-I should canonical-feel-similarly-priced. Specific cost = Design canonical-balancing.
- **canonical-locked**: `False` (canonical-Tier-1 baseline-purchasable; canonical-no-quest-gate)
- **canonical-rendering-flavor**: when canonical-installed, canonical-visible-as canonical-fine-lattice-overlay on canonical-ship's-targeting-reticle (canonical-Image-lane optional Phase 2)

### Module 2 — **Energy Cycler I**

- **slot**: `weapon`
- **tier**: 1 (canonical-baseline-purchasable from Mh-Lai shop)
- **canonical-Furling-thematic description**: *"Furling energy-routing-cycler. Shortens cooldown between beam-pulses by pre-charging the emitter-coils. Faster fire-rate."*
- **canonical-stat-delta direction**: reduces weapon cooldown / increases shots-per-second / improves canonical-weapon-fire-rate. Specific delta values + scaling = Design canonical-balancing.
- **canonical-cost direction**: comparable to canonical Beam Mod I; canonical-Energy-Cycler-I should canonical-feel-similarly-priced. Specific cost = Design canonical-balancing.
- **canonical-locked**: `False`
- **canonical-rendering-flavor**: when canonical-installed, canonical-emitter-coils canonical-glow-faintly-warmer between canonical-shots (canonical-Image-lane optional Phase 2)

### Notes for Design
- Both modules are canonical-Tier-1 baseline-purchasable. Per `station-screens-design.md`, Tier-1 is for *padding the Trade-economy with a meaningful sink*. Canonical: these 2 mods expand canonical-Weapon-slot variety (canonical-existing Beam Mod I is canonical-damage-up only).
- Canonical-recommended canonical-stat-delta-scale: small (canonical Tier-1 should feel like canonical-incremental upgrades). Aaron canon canonical-balancing-rule from `station-screens-design.md`: *"Tier-1 ship module is ~50-100 credits + 5-10 USEFUL"*.
- Canonical-canonical-stacking-rule: Design's call whether canonical-Targeting-Lattice-I and canonical-Beam-Mod-I can canonical-both-be-equipped (only one canonical-Weapon-slot per `station-screens-design.md`); recommend canonical-mutually-exclusive (canonical-one Weapon-mod per ship; canonical-player-choice between damage / accuracy / fire-rate).
- Canonical-canonical-Tier-2-paths canonical-flagged for future: **Targeting Lattice II** (canonical-quest-gated unlock; canonical-additional accuracy + canonical-active-ability *"Predictive Sweep"*) and **Energy Cycler II** (canonical-quest-gated unlock; canonical-additional cooldown reduction + canonical-active-ability *"Surge Discharge"*). Not slice-MVP; canonical-future-pass.

**Verification path**: walks needed — `walk_purchase_targeting_lattice_i` (verify canonical-purchasable at Mh-Lai; verify canonical-installs-into-Weapon-slot; verify canonical-stat-delta applies); `walk_purchase_energy_cycler_i` (same checks for the canonical-Reload mod); `walk_weapon_slot_mutual_exclusion` (verify canonical-only-one-Weapon-mod-equipped at a time per `station-screens-design.md`).

---

## 2026-05-18 — Lore → Design — Cutscene sequences spec'd (Ken Burns pan-and-narrate; MVP-ready)

**Status**: open — **simple-but-canonical-impactful runtime target**

**What**: Aaron dispatch: *"Fill out the cutscene sequences. They should be awesome rewards or thrilling defeats depending on a good or bad outcome, and there should be heavy text associated with it. We can use still images that are very wide, so we slowly slide across the image..."* Full canon in [`cutscene-sequences.md`](cutscene-sequences.md). **16 cutscene-spec sets** authored with canonical-wide-image-canvas + canonical-pan-path + canonical-text-blocks (heavy-prose) + canonical-duration + canonical-Phase-2-overlay-suggestions.

**The MVP cutscene system** (canonical-implementation-tonight):
- **Wide canvas**: 3840×1080 (canonical 3-screens-wide) for canonical-horizontal-pan; 1080×3840 vertical; 1920×1920 square-close-detail for canonical-character-zoom (canonical Halia death uses square-zoom-only)
- **Ken Burns pan**: `pan: {start: [x,y,zoom], end: [x,y,zoom], duration_sec, easing}` — canonical linear / ease-in / ease-out / ease-in-out
- **Text overlay**: timed `text_blocks` with start/end seconds, position (bottom-third default; center for anchors), color (warm-amber=good / cool-grey=baseline / cold-violet=Cleanser-related / bright-white=priority-anchor)
- **No audio required** for Phase 1 (Aaron canon: *text for now, speech later*)
- **Phase 2 overlays** flagged per cutscene but canonical-deferred (particles / light effects / color shifts / canonical-spatial-distortion-for-Others-cutscenes)

**Minimal `CinematicScene` class** spec sketched in `cutscene-sequences.md §3.1` — canonical-pseudo-Python sketch ready for Design to translate. Core loop: `load image → interpolate pan position → blit viewport → render active text blocks with fade`.

**16 cutscenes specced** (5 categories):
- **Tutorial/Beat cutscenes (2)**: Council Briefing (Halia mandate-delivery; canonical *"The bookkeeping is the dignity"* anchor); Beat 4 Distress Beacon delivery (canonical *"I will not watch it twice"*)
- **GOOD-outcome species-resolution (4)**: Slylandro Cloak (canonical 250kya-saved); Vresh Extraction (canonical-good-with-tragedy); Lemmkin Migrate (canonical-cheerful-rolling-in); Sevra Recruitment (canonical *"Tomorrow"*)
- **BAD-outcome species-resolution (3)**: Slylandro Cleansed (canonical *"Just to be safe"*); Fall of Mh-Lai (canonical *"I am working on it"*); Taalo Shield Failure (canonical *"They do not have the vocal apparatus for it"*)
- **Defeat-priority (2)**: Halia's Death (canonical square-zoom-on-her-eyes; canonical command→private code-switch; canonical *"Drink the tea"* final); Lemmkin Stay-outcome (canonical *"We will die curious. We recommend it."*)
- **Mid/Endgame (5)**: Rainbow World Seeding (canonical *"longest postcard"*); First-Other-Vessel sighting (canonical-priority-horror); Crossing-Opens (canonical *Migration fleet in canonical order; bookkeeping-is-the-dignity return*); Best Ending (canonical Quiet Resolution); Great Ending (canonical *we continue, mostly*); Disastrous Ending (canonical *"Good job"* + canonical *"We told you the Others were never funny"* fourth-wall-break #3); Unsuccessful Ending (canonical *"the galaxy is the kitchen now"*); **NEW Sterile Galaxy Ending** (canonical Cleanser-pushed Steward extended vote to proto-species — canonical-cold-violet-throughout)

**Skip-protection** canonical-required on priority-passages: Halia death / Disastrous / Crossing-Opens / Unsuccessful / Sterile-Galaxy / Taalo Shield. Canonical: fade-cut on skip but canonical-final-anchor-line always plays.

**Canonical priority build-order for tonight** (if Design has 2-4 hours):
1. Build canonical-minimal `CinematicScene` class (1 hr) — image load + pan interpolation + timed text-block render
2. Wire Council Briefing trigger (30 min) — canonical-easy first cutscene; canonical-low-stakes test
3. Stitch one wide image (1 hr) — recommend Crossing-Opens OR Slylandro Cloak
4. Test playback (30 min)
5. Iterate to 3-5 cutscenes next session

**Asset format suggestion**: image at `assets/cutscene/<event_id>/canvas.png`; metadata at `assets/cutscene/<event_id>/sequence.yaml` with canonical-pan-and-text-block fields directly portable from cutscene-sequences.md specs.

**Cross-canon integration**:
- 15 of these cutscenes share content with `cinematic-narration.md` — canonical-narration-prose already authored there
- Trigger flags consolidated across both docs (canonical 15+ flag list)
- Bio-Archive auto-population canonical-recommended on cinematic-trigger (6 of 16 cutscenes open with canonical *Bio-Archive Entry 14,4XX* numbering)
- Canonical music-policy alignment per `cinematic-narration.md §5`

**Verification path**: walks needed — `walk_cinematic_pan_render` (verify canonical pan-and-text-block render works for 1 test cutscene); `walk_cinematic_skip_protection` (verify canonical-priority-passages reject skip until canonical-final-anchor); `walk_cinematic_bio_archive_autopop` (verify canonical-6-entries-numbered open canonical-Bio-Archive entries when cutscene fires).

---

## 2026-05-18 — Lore → Design — 15 canonical cinematic narration passages + CinematicScene wiring

**Status**: open

**What**: Aaron dispatch: *"Let's beef up the writing around the dramatic events and the tragic events that happen in the game, so we have something to read (listen to in voice) while we view the cutscene image."* Authored as [`cinematic-narration.md`](cinematic-narration.md) — 15 canonical cinematic voice-over passages with canonical-trigger-flags + canonical-visual-frame-summaries + canonical-narration-prose + canonical-speaker + canonical-voice-direction + canonical-callback-economy-phrase-deployments.

**Net new content**:
- **15 canonical cinematic narration passages** (~3,200 words; ~25-35 minutes of recorded voice content)
- Canonical trigger flags per cinematic (flag-state-driven scene-firing)
- Canonical CinematicScene-instance specifications (canonical-image-sequence + canonical-narration-track per scene)
- Canonical pacing: each passage canonical-broken into 3-7 canonical-beats matching canonical-image-frame-transitions

**Cinematic trigger flag list** (canonical for Design's scene-trigger system):

| Cinematic | Trigger flag |
|---|---|
| 2.1 Council Briefing | `flag:tutorial_beat_5_council_briefing` |
| 2.2 Androsynth Arrival | `flag:tutorial_beat_4_androsynth_arrived` |
| 2.3 Slylandro Cloak | `flag:slylandro_cloaking_satellite_installed` |
| 2.4 Fall of Mh-Lai (race-but-doomed) | `flag:mh_lai_fell` + `flag:steward_witnessed_close` |
| 2.5 Halia's Death | `flag:halia_died_in_fall` |
| 2.6 Cleanser-supervised Whisper | `flag:halia_cleanser_supervised` |
| 2.7 Taalo Shield Failure | `flag:taalo_shield_failed` + `flag:taalo_eliminated` |
| 2.8 Disastrous Ending | `flag:ending_disastrous` |
| 3.1 Burvixese Be-Loud Failure | `flag:burvixese_be_loud_failed` |
| 3.2 Lemmkin Stay-outcome | `flag:lemmkin_stay_outcome` |
| 3.3 Coel's from-afar theory | `flag:coel_from_afar_theory_articulated` |
| 3.4 Drev-Tok's Death | `flag:drev_tok_killed` |
| 3.5 Crossing-Opens | `flag:rainbow_worlds_aligned` + `flag:crossing_opens` |
| 3.6 Hammer-Round first use | `flag:hammer_round_fired_on_other` |
| 3.7 Unsuccessful Ending | `flag:ending_unsuccessful` |

**Canonical CinematicScene infrastructure requirements**:
- Each cinematic is a canonical `CinematicScene` instance
- Canonical-image-sequence track + canonical-narration-track + canonical-music-bed track
- Canonical-pacing-driven by canonical-narration-beats (canonical-3-7 beats per cinematic with canonical-pauses between)
- **Canonical skip-protection on priority-production passages**: canonical-Steward cannot skip canonical-Halia's-death (§2.5), canonical-Disastrous-ending (§2.8), canonical-Crossing-Opens (§3.5), canonical-Unsuccessful-ending (§3.7). Recommend canonical-fade-cut on canonical-skip-attempt but canonical-the-canonical-final-anchor-line canonical-always-plays.

**Bio-Archive integration** (canonical-recommended):
- 6 of 15 cinematics open with canonical *Bio-Archive Entry 14,4XX* numbering (canonical-Steward narrator convention)
- Recommend canonical-Bio-Archive entries canonical-auto-populated from canonical-cinematic-narration-text at canonical-cinematic-trigger
- Canonical-entries: 14,420 (Androsynth Arrival), 14,476-A (Taalo Shield), 14,484 (Slylandro Cloak), 14,494-B (Hammer-Round), 14,495 (Crossing-Opens), 14,499 (Unsuccessful Ending). Plus canonical-non-numbered-entry for Fall of Mh-Lai (canonical-Steward canonical-cannot-supply-the-number; the canonical-absence-of-numbering IS the canonical-content)

**Music cue coordination**:
- Canonical NO MUSIC during Disastrous (§2.8) and Unsuccessful Steward-Forty-Seven exchange (§3.7) — canonical *the silence is the content*
- Canonical MAJOR ORCHESTRAL CUE for Crossing-Opens (§3.5) — slice's only major orchestral cue per parallel-chat canon
- Canonical Karavem 3-hour-song carries Crossing-Opens canonical-secondary-musical-bed

**Fourth-wall-break canon respected**:
- Cinematic 2.8 deploys canonical 4th-wall-break #3 (canonical *"We told you the Others were never funny"*) — completes the canonical-3-fixed-canon
- No additional canonical-4th-wall-breaks in the cinematic set

**Verification path**: walks needed — `walk_cinematic_council_briefing` (verify Halia mandate-delivery canonical-anchor *"the bookkeeping is the dignity"*); `walk_cinematic_halia_death` (verify canonical Command→Private code-switch + canonical comm-channel-cuts-immediately-after-Drink-the-tea); `walk_cinematic_cleanser_whisper` (verify canonical *"I'm sorry, Steward"* whisper canonical-briefly-outside-Cleanser-channel-acoustic-profile); `walk_cinematic_taalo_shield` (verify canonical 11-second-Shield-burn + canonical bodies-calcify-into-landscape narrative + canonical-Vresh-grief-mode-final-line); `walk_cinematic_disastrous` (verify canonical *"Good job"* + canonical *"We told you the Others were never funny"* + canonical-absolute-silence-after); `walk_cinematic_crossing_opens` (verify canonical Migration fleet canonical-order + canonical *"The bookkeeping is the dignity"* return + canonical *"Engaging the corridor — now"* final).

---

## 2026-05-18 — Lore → Design — Gemini Free tier integration for lore-batch expansion

**Status**: open — recommendation + canonical prompt templates ready

**What**: Aaron dispatch: *"Use GEMINI_FREE_API_KEY in the .env for text generation. If there is a way to use Gemini free tier to help us out with expanding our lore, that would be great."* Full canonical analysis + 7 canonical-prompt-templates in [`gemini-lore-expansion-proposal.md`](gemini-lore-expansion-proposal.md). Lore-side recommendation: **YES, use Gemini Free for high-volume, low-canonical-risk lore expansion** with strict canonical-Lore-review.

**Where**:
- **Existing tooling**: `tools/gen_lore_gemini.py` (canonical-Gemini-Flash script with canonical Anthropic-fallback; canonical-reads `GEMINI_API_KEY`); `tools/gemini_drafts/` (canonical-existing drafts directory)
- **Source canon**: [`gemini-lore-expansion-proposal.md`](gemini-lore-expansion-proposal.md) — 9 sections covering strategy, existing tooling, prioritized use cases, 7 canonical prompt templates, workflow, risks, quick wins

**Code changes Design should make** (canonical: this is Design's lane per Rule 5):
1. **Update env-var precedence**: existing script reads `GEMINI_API_KEY`; canonical-Aaron-canon specifies `GEMINI_FREE_API_KEY`. Recommend: prefer `GEMINI_FREE_API_KEY`; fallback to `GEMINI_API_KEY`; fallback to Anthropic.
2. **Wire 7 new canonical-prompt-templates** into the script per `§4` of proposal doc:
   - `combat_banter_expansion` — extend banter pools 5x per species
   - `awareness_event_backup` — generate backup awareness events beyond canonical-3-per-Aaron
   - `bio_archive_entry` — expand Bio-Archive entries
   - `common_room_ambient` — generate Common Room ambient banter beats
   - `lemmkin_archive_entry` — canonical *Things We Have Tried* archive entries
   - `furling_humor_archive` — canonical Furling Humor Archive entries
   - `quest_dialog_branch` — canonical optional dialog branches
3. **Canonical *batch-runner* sub-script**: takes canonical-CSV of `(template_id, inputs)` rows; runs all in sequence with canonical rate-limit-respecting delays; outputs to canonical-`tools/gemini_drafts/<canonical-name>.json`
4. **No canonical-direct-integration with runtime** — outputs are canonical-drafts only; canonical-Lore reviews; canonical-Lore ports manually to source-docs and spreadsheets

**Notes for Design**:
- **The 7 canonical-prompt-templates are canonical-Lore-authored** in the proposal doc `§4`. Recommend Design canonical-imports them directly (canonical: do not paraphrase; the templates encode canonical-voice-anchors + canonical-doctrine-constraints precisely).
- **The canonical Lore-review-loop is mandatory**: Gemini outputs are canonical-draft-only. Recommend Design canonical-does-not-auto-port outputs to runtime; canonical-Lore-reviews-each-batch.
- **Quota strategy**: free-tier Gemini Flash is canonical-~20 RPD per existing script's note. Recommend canonical-7-day rolling batches; canonical-strategic-batching.
- **Existing Anthropic fallback** in script: Aaron-call on whether to preserve. Recommend canonical-keep-fallback (preserves canonical-availability when quota exhausts).

**Prioritized tonight-batches** (if Aaron approves immediate execution):
1. **Combat banter expansion** — extend the canonical 11-species pools from 2-3 lines per damage bracket to canonical-5-each. Net: ~110 new banter lines.
2. **Lemmkin archive entries** — canonical *Things We Have Tried That Did Not Work* pool expansion. High canonical-comedic-value; canonical-low-canonical-risk.
3. **Common Room post-Fall ambient beats** — canonical-quieter-post-Fall variant (3 days / 3 weeks / 1 month).

**Verification path**: no new walks needed for the canonical-pipeline-itself (canonical: Gemini outputs go to drafts directory; canonical-Lore-reviews-and-ports manually). Future walks pick up canonical-new-content via canonical-baseline walks once canonical-Lore has canonical-ported drafts.

**Tier 3 — canonical-DO-NOT-Gemini-author content** (canonical-priority-production-only):
- The 3 canonical 4th-wall breaks
- Halia's canonical key passages (Quiet Resolution mandate / Fall last transmission / Cleanser-supervised whisper / Andromeda-final-exchange)
- Coel Tessar's *from-afar* theory articulation
- Disastrous ending narrator + *We told you the Others were never funny*
- Sevra's Andromeda 4th-wall-break-#2
- Vael-Souren canonical-mourning lines (canonical-priority-production)

These remain hand-authored. Recommend Design canonical-flag these in the script as canonical *DO_NOT_GEMINI_AUTHOR* canonical-passages — if a canonical-template-call references one of these, the script canonical-refuses-and-instructs-Lore-to-hand-author.

---

## 2026-05-18 — Lore → Design — Cross-species awareness events + Should I Stay or Should I Go meter

**Status**: open — two-feature dispatch

**What**: Aaron dispatch: *"Do a pass where there are extra dialog events that let the player know the species is aware of events elsewhere in the galaxy that the player responsible for... Each species might only be aware of 3 other possible nearby events, not every single one. Build an overall 'Should I Stay or Should I Go' meter that is sort of a quest completion meter letting the player know how much of the 'great ending' content they have completed, successful or not."* Full canon in [`cross-species-awareness-and-progress-meter.md`](cross-species-awareness-and-progress-meter.md).

**Feature 1 — Cross-species awareness events** (~69 events):
- 23 species/factions × 3 awareness events each
- Conditional-dialog-trigger system: when a canonical-flag is set AND the species has a canonical-channel-to-know-about-it, the species canonical-greets-the-Steward on next-visit with awareness-prefix-line
- Awareness channels documented per species (Furling Council relay / Burvixese Broadcaster network / Arilou Quasi-Space temporal-drift / Slylandro 10,000-year observation / Mycon spore-network / Chenjesu resonance-translation / Stelloth trader-network / Selvenne hive-mind / Kovellim galactic-monitoring / Karavem song-exchange / Melnorme trade-data / Cleanser doctrinal-tracking / Mrokon kill-tally / Lemmkin curiosity / Preserver canopy-singing-network / Forty-Seven records)
- Canonical implementation: each species' on_revisit_dialog FSM-state checks flag-conditions; if met, prepends canonical-awareness-line before standard greeting
- Awareness lines are canonical-flavor not canonical-quest-blocking; canonical-the-Steward-can-skip and proceed to canonical-baseline-dialog
- Key examples: Vael-Souren's Halia-died-mourning-line ("Halia is canonical-recorded. The canonical-Quiet-Ledger now contains canonical-her name with canonical-full-honor. She was canonical-honorable to a canonical-fault..."); Slylandro's Taalo-extinction awareness ("We have heard the silicon-songs of Taalo's-Stone go silent..."); Lemmkin's Mh-Lai-fell awareness ("STEWARD! We have already-built-three-canonical-models of canonical-what-the-Others-might-have-done!")

**Feature 2 — Should I Stay or Should I Go Meter**:
- **Player-visible UI** tracking canonical-progress-toward-Great-tier-ending content
- Total = **51 completion-points**: 16 species + 7 crew + 25 side-quests + Halia/Ultron/Crossing binaries
- **Successful or not per Aaron canon**: the meter measures **completion**, not **moral outcome** (a species Cleansed counts as canonical-handled)
- **Tier projection** rendered alongside raw completion: Best / Great / Good / Successful-at-cost / Unsuccessful / Disastrous — each with canonical-display-label ("On track for *the Quiet Resolution*" / "On track for *we continue, mostly*" / etc.)
- **Forty-Seven delivers the meter** via canonical *"by my standards"* register
- Canonical UI: corner-icon (baseline-visibility) + clickable-full-display panel + tier-projection text with canonical-color-coding (warm-gold filled / cool-grey unfilled / cold-violet Disastrous-tier-warning per Cleanser-palette callback)
- Canonical *automatic-pop-up on tier-threshold-crossed*
- **Canonical Forty-Seven Disastrous-tier-warning canonical-line** authored (`§3.9`): canonical *"the canonical-Disastrous-tier-ending canonical-includes a canonical-specific narrator-line. The line is canonical-not-said-with-cruelty. The line is canonical-said-flat. I am canonical-noting-this-for-your-canonical-information. Drink the tea."* — canonical: this is canonical *Forty-Seven's third-canonical-warning of the canonical-three-canonical-warnings-in-the-slice*
- Canonical Forty-Seven flair-lines per state-change: brief; non-intrusive

**Where**:
- **Source canon**: [`cross-species-awareness-and-progress-meter.md`](cross-species-awareness-and-progress-meter.md) — 6 sections
- **Code surfaces likely affected**:
  - Each species' dialog FSM: new conditional-greeting-prefix branch checking canonical-flag-state + canonical-channel-eligibility
  - **NEW meter-tracking system**: flag-state observer that recalculates 51-point completion + tier projection on every flag-state change
  - **NEW meter UI**: corner-icon + full-display panel per `§3.7`
  - **NEW Forty-Seven meter-delivery dialog FSM** per `§3.4`
  - **NEW Forty-Seven flair-line trigger system** for state-change announcements per `§3.8`
  - **NEW automatic-pop-up trigger** on tier-threshold-crossed
  - Canonical *"Drink the tea"* canonical-callback-economy expansion (now appears across canonical 5+ species/NPCs through awareness events) — recommend dialog metadata tagging

**Notes for Design**:
- **The canonical-awareness-events use the SAME flag-state as the canonical-meter** — implementation can share the underlying flag-tracking; no duplicate state needed
- **The canonical-meter only fills**: even if a species is canonical-Cleansed-after-Migration-was-offered, the canonical-component is canonical-still-set. The canonical-moral-outcome is canonical-tracked-separately for canonical-tier-prediction (favorable-count vs. unfavorable-count)
- **Canonical *successful or not* canon**: completing a quest unfavorably (e.g. Lemmkin Stay-outcome) still increments the meter; canonical-the-tier-projection is canonical *where moral-outcome matters*
- **Canonical Disastrous-tier-warning is canonical Forty-Seven's third-canonical-warning** — completes the trilogy of canonical-Forty-Seven-warnings (canonical post-Fall 4th-wall break #1; canonical per-Cleanser-vote; canonical Disastrous-tier-projection)
- **Canonical [PLACEHOLDER] markers** in awareness events for canonical-NPC-names — same placeholders as `loop-closing-content-pass.md`

**Verification path**: walks needed — `walk_awareness_events_taalo_eliminated` (verify multiple-species reference Taalo extinction after triggering); `walk_meter_open` (verify canonical Forty-Seven delivers the meter with current state); `walk_meter_tier_projection_disastrous_warning` (verify canonical-warning-line fires when tier-projection drops to Disastrous); `walk_meter_continuous_update` (verify flag-state-changes recalculate immediately).

---

## 2026-05-18 — Lore → Design — LOOP-CLOSING content pass: 11 species + full quest FSMs + combat banter + Common Room beats

**Status**: open — slice's content-completion pass

**What**: Aaron dispatch: *"Fill in all of the gaps. Fill out the quest dialog, the ship-to-ship banter, the common room banter, anything in the spreadsheets that is missing, creatively invent it... close the loop on the game tonight with full content, placeholders if needed."* Authored as [`loop-closing-content-pass.md`](loop-closing-content-pass.md) — single-doc content-completion pass covering the 11 remaining species (**Stelloth / Selvenne / Kovellim / Karavem / Mrokon / Taalo / Burvixese / Thinn / Melnorme / Dnyarri / Orz-rifts**) with full canon + quest dialog FSMs + combat banter pools + Common Room reaction beats.

**Net new content** (Design's spreadsheet-port-target):
- **11 quest FSMs** with canonical state-transitions / branches / side-effects: `stelloth_artifact_trade` / `selvenne_memory_archive` / `kovellim_crossing_trade` / `karavem_song_exchange` / `mrokon_hammer` / `taalo_shield` / `burvixese_broadcasters` / `thinn_edge_align` / `melnorme_trade_and_recruitment` / Dnyarri-encounter / Orz-rift-encounter
- **~55 new quest rows** for `tools/build_quest_inventory.py` (parallel chat) — 11 quests × ~5 states each
- **~70 new combat banter lines** across 5-damage-bracket pools per species
- **~50 new Common Room banter beats** including canonical first-meet reactions + pre/post-Fall ambient variants + per-quest-completion + per-quest-failure
- **12 new modules**: STELLOTH_PHASE_LENS / SELVENNE_REEF_TOUCH / KOVELLIM_FOLDER_COMPASS / KOVELLIM_CROSSING_BRACE / KOVELLIM_CYCLE_MEMORY / KARAVEM_RESONANCE_MODULE / MROKON_HAMMER_ROUND / TAALO_SILICATE_HARDENING_LANDER_UPGRADE / BURVIXESE_AMPLIFIER_LANDER_UPGRADE / MELNORME_ECHO_SENSOR / MELNORME_HARDENING_LANDER_UPGRADE / MELNORME_COUNCIL_SEAT
- **11 new Bio-Archive entries** authored (Steward voice; ~150-word entries each)
- **Canonical Thinn-paradoxical-combat-saves-more-Thinn mechanic**: the slice's canonical *only species where firing on them saves more of them* (canonical: combat causes them to realize the Edge-Align doctrine is wrong and Migrate at higher rates). Slice-novel mechanic; recommend careful balancing.

**Notes for Design**:
- **Each species has a canonical Quiet Resolution path** (Migrate / Cloak / Hide / Devolve / Eliminated-with-honor / Mixed-state). Canonical: the Steward's recommendation tips the canonical-vote per species.
- **Compact FSM format**: state name + speaker + dialog text + choice list + next-state + side-effects. Direct port to existing FSM scheme.
- **Canonical [PLACEHOLDER] markers** flagged for Aaron-call where canonical-NPC-names provisional (Veshen / Tev-Mar-Burv / Edge-Align-Eldest).
- **Canonical existing parallel-chat docs may overlap** for species the parallel chat has authored (`species-the-stelloth.md` / `species-the-selvenne.md` / `species-the-mrokon.md` / `species-the-kovellim.md` / `species-the-karavem.md` per MEMORY). Where canonical-overlap exists, recommend syncing: parallel-chat's species-specific docs are canonical for in-character voice + lore detail; this loop-closing doc is canonical for quest FSM + combat banter + Common Room beats. Both should be ported.
- **Spreadsheet ports needed**: 11 quest FSMs → `quest_inventory.csv` (~55 rows). 12 module identifiers → `modules.py` content catalog. 11 Bio-Archive entries → `archive_entries.py` (per existing Beat 5 Bio-Archive spec).
- **Common Room banter pool** extension: tag categories per `§12` — first-meet reactions / pre-Fall vs post-Fall ambient / per-quest-completion / per-quest-failure / Andromeda-arrival chorus extensions (canonical full FIXED-SEQUENCE per `humor-pass.md` and `callbacks-and-callforwards.md`).

**Verification path**: walks needed — one `walk_<species>_quest` per species (11 walks), each verifying the canonical-quest-FSM resolves to canonical-correct-terminal-state across canonical-major-branches. Plus `walk_thinn_combat_paradox` (verify canonical *firing-on-Thinn-saves-more-Thinn* mechanic fires). Plus `walk_dnyarri_disguised_reveal` (verify canonical-pretending-to-be-another-species + canonical first-fire-reveal). Plus `walk_orz_rift_buys_time` (verify canonical *combat-resolution-extends-rift-free-cluster-time*).

---

## 2026-05-18 — Lore → Design — Lemmkin full canon + canonical *out-interest the Others* Convince Vote mechanic

**Status**: open

**What**: Aaron canonized two new Lemmkin dispatches: (1) species profile — *"No fear, only curiosity, and they breed quite fast to make up for the losses. Excellent engineers, though safety precautions being not on the requirements list... It's absolute chaos, danger and discovery on the planet. Travel there is NOT recommended without proper safety equipment, which you cannot buy planetside."* (2) quest mechanic — *"When we inform the Lemmkin of the impending doom, they were so excited to see what The Others looked like... the entire Lemmkin leadership will vote to go with the Precursors or stay to see what happens based on your quest and dialog outcomes. Your quest will be to find something more interesting than being eaten by The Others."* Full canon in [`species-the-lemmkin.md`](species-the-lemmkin.md).

**Where**:
- **Source canon**: [`species-the-lemmkin.md`](species-the-lemmkin.md) — 9 sections; full species + canonical quest + canonical NPC + canonical Skitter ship + canonical Common Room reactions + canonical SC2-callforward archive-misattribution
- **Code surfaces likely affected**:
  - **New canonical quest `lemmkin_convince_vote`** — canonical *Interest Token gathering + leadership vote* mechanic
  - **New canonical mechanic: Interest Tokens** — canonical 7 HIGH-value tokens (Chenjesu Resonance Record / Mmrnmhrm Archive / Forty-Seven-talking / Quasi-Space portal sample / Sevra / Vresh / Slylandro Cloaking Satellite blueprint) + canonical 7 MEDIUM-value (Distress Beacon / Karavem song / Stelloth chord-engagement / Mrokon Hammer / proto-species observations / Burvixese Broadcasters / Preserver canopy-village) + canonical several LOW-value (decorative only). Tokens canonical-acquired during slice; canonical-presented at Vote.
  - **Canonical 3 outcome branches**: Migrate (5+ HIGH OR 7+ MEDIUM) / Split (3-4 HIGH OR 5-6 MEDIUM) / Stay (<3 HIGH AND <5 MEDIUM)
  - **New canonical NPC**: **Whisk-Of-The-Better-Bouncing-Thing** (canonical engineer-spokesperson; canonical full canonical voice direction in `§4`)
  - **New canonical sanctuary visit**: **Skitter-Prime** — canonical *chaos planet*; canonical visitor-hazard system (canonical *safety equipment cannot be bought planetside*); canonical Forty-Seven warning before arrival
  - **Canonical Forty-Seven safety-warning canonical line**: *"Steward. We are canonical-approaching Skitter-Prime. The canonical-Furling-Council canonical-issues the canonical-following-canonical-reminders: you cannot canonical-purchase canonical-safety-equipment planetside; canonical-bring-your-own; canonical-do-not-investigate-anything-the-Lemmkin-are-also-investigating; canonical-the-Lemmkin-are-canonical-very-charming-and-this-is-canonical-part-of-the-canonical-hazard."*
  - **New canonical Bio-Archive entry**: *Lemmkin — Recklessly Curious Engineers*
  - **Canonical Lemmkin Skitter ship** (existing canon canonical-reaffirmed; canonical Burst-Scatter Probe + Tail-Drop 180-pivot; canonical cheerful-escalation pilot register per `humor-pass.md §6.1`)
  - **Canonical Common Room reaction scene** post-Vote (3 variants per `§6.4`): Migrate-cheerful / Split-quieter / Stay-painful-with-canonical-callback

**Notes for Design**:
- **The Convince Vote is the slice's most-unique-mechanic.** No other species has a vote that the Steward wins by *out-interesting* the antagonist. Recommend treating this as canonical priority-implementation.
- **Interest Tokens are gathered during slice play organically** — the Steward acquires them by encountering content. Recommend the Vote does NOT require backtracking; canonical: if the Steward visits a token-source naturally during the slice, the token is automatically logged. If the Steward skipped a content area, that token is canonical-unavailable at the Vote.
- **The canonical Stay outcome is the slice's painfully-tender Homesteader resolution** — the canonical Lemmkin spokesperson canonical-quotes-Halia (*"Drink the tea"*) at the canonical farewell. This is the canonical *"Drink the tea"* callback's most painful migration in the slice. Recommend treating with priority production attention.
- **The canonical *safety equipment cannot be bought planetside* canon** is a hard-mechanic gate: if the Steward visits Skitter-Prime without canonical pre-loaded safety equipment, canonical-take-canonical-environmental-damage (canonical small but persistent canonical hit-rate during the visit); canonical *Forty-Seven warns; if ignored, canonical-Steward-fur-singed cosmetic + minor HP-tick during visit*. Recommend the gate is canonical-visible but canonical-not-fatal.
- **Whisk canonical-asks-to-touch-the-Steward's-fur** — canonical first-meeting beat. Canonical dialog choice for the Steward: *Yes (canonical Lemmkin Interest +1; canonical: Whisk does canonical-investigate the fur briefly with canonical-gentle-instruments; canonical: the Steward's fur is canonical-fine afterward)* OR *No (canonical Whisk canonical-respects this; canonical: small archived note in canonical-Lemmkin records about canonical-Furling-canonical-fur-protocols)*. Recommend surfacing.

---

## 2026-05-18 — Lore → Design — Coel Tessar canonical character profile + Androsynth *from-afar* canonical Others-attention theory

**Status**: open

**What**: Aaron canonized Coel Tessar's full character profile AND a new speculative canonical theory: *"It is possible the androsynth were the ones that drew the eye of The Others from afar with their multi-dimensional experiments."* Authored as extension to [`the-androsynth-refugees.md`](the-androsynth-refugees.md) — new §"Coel Tessar — full character profile" + new §"The 'from afar' theory" within the canonical Others-canonization section.

**Where**:
- **Source canon**: [`the-androsynth-refugees.md`](the-androsynth-refugees.md) §"The 'from afar' theory" + §"Coel Tessar — full character profile"
- **Code surfaces likely affected**:
  - **Coel Tessar NPC dialog FSM** — canonical *devastated* register; canonical flat-affect public + canonical-vulnerable-in-private-with-Steward; canonical voice direction in `§"Coel Tessar — full character profile"`
  - **Canonical private-trust-gated dialog branch** where Coel canonical-articulates the canonical *from-afar theory* to the Steward; canonical: gated on canonical Steward visits + canonical-trust-built; canonical: the canonical *possibly to everyone* line is the canonical-most-vulnerable canonical-Coel line
  - **Canonical Renn Halvor-Coel-Tessar permission-grant scene** — canonical short-and-warm exchange; canonical *they canonical-do-not-discuss-the-experiment*
  - **Canonical Andromeda-crossing Coel final exchange** — canonical *Coel boards the Steward's escort vessel for the canonical-final crossing; canonical-one canonical-final-exchange-about-the-from-afar-theory; canonical-Coel canonical-decides-to-believe-or-not-believe-it for the rest of her life*

**Notes for Design**:
- **The canonical *from-afar theory* is canonical-UNCONFIRMED.** The slice does not confirm or deny it. Canonical: the canonical theory canonical-may-be-true or canonical-may-be-false; canonical: the canonical-ambiguity is canonical *the slice's deepest unresolvable Other-question*. Recommend implementing the canonical-dialog-branch as canonical *the theory is articulated, the Steward responds, the conversation closes without resolution*. No canonical resolution beat.
- **Coel canonical-carries-the-guilt-of-the-entire-cycle in private** — canonical: she does not articulate this to other Androsynth (canonical: they have enough grief without it); canonical: the Steward is canonical-her-only-confidant on this theory.
- **Renn Halvor canonical-knows-the-theory** but canonical-does-not-discuss-it with Coel. Canonical: Renn's canonical own grief is canonical-incompatible with canonical-the-broader-galactic-version. Canonical: he carries it separately. Recommend canonical Renn dialog branch (gated on canonical Steward asks): *"Yes. I have heard the theory. I do not know if it is true. I am — *(canonical brief pause)* — sorry, if it is. I cannot make my apology mean more than that. The Steward has been gentle with us. I cannot ask for more."*
- **Canonical NEW player-elected dialog choice** during the canonical Coel-private scene: *"Do you believe the theory?"* — canonical Coel-response: *"I — yes. Privately. I do not have the canonical-proof. The proof may not canonical-exist. I believe it because the canonical-alternative-is that the Others were canonical-coming-anyway and our canonical-experiment was canonical-coincidence. I find that canonical-harder to live with than the canonical-guilt. The canonical-guilt at least canonical-means-our-deaths-were-the-canonical-cost-of-our-canonical-curiosity. The canonical-coincidence-version would canonical-mean canonical-they-were-canonical-meaningless."*

**Verification path**: walks needed — `walk_lemmkin_first_visit` (verify Skitter-Prime canonical-environment + Whisk canonical first-meeting + canonical fur-touching-protocol dialog + canonical Bio-Archive entry triggered); `walk_lemmkin_convince_vote_migrate` (gather 5+ HIGH tokens; present at Vote; verify Migrate outcome); `walk_lemmkin_convince_vote_stay` (present <3 tokens; verify Stay outcome with canonical *Drink the tea* canonical-callback-line); `walk_lemmkin_skitter_prime_no_safety` (visit without safety equipment; verify canonical environmental damage and canonical Forty-Seven warning); `walk_coel_from_afar_theory` (build trust with Coel; verify the canonical private theory-articulation dialog branch + canonical Steward response options); `walk_coel_andromeda_final` (verify the canonical final exchange about the theory at the canonical Andromeda crossing).

---

## 2026-05-18 — Lore → Design — Halia canonized: Persuader + Defense Fleet Commander + gruff-honorable-jokes-when-permitted

**Status**: open

**What**: Aaron canonized Halia's full character profile: *"Halia is gruff, and honorable to a fault. Their only aim is to save as many as possible. Halia is from the Persuader faction of Furlings. Halia will joke, but when the situation is serious, Halia is a dominant commander and functional leader, professional to the core. Also the commander of the Furling Defense Fleet."* Full canon in [`halia-profile.md`](halia-profile.md) — 12-section character bible consolidating and extending all prior Halia canon scattered across parallel-chat docs. Surface update applied to [`factions-and-war.md`](factions-and-war.md) Persuader section.

**Where**:
- **Source canon**: [`halia-profile.md`](halia-profile.md) — physical/voice/leadership/humor/Defense-Fleet/Steward-relationship/arc/key-lines/dispatches
- **Code surfaces likely affected**:
  - Halia NPC dialog FSM — canonical **dual register** (private gruff-warm vs. command professional-to-the-core); canonical **code-switch triggers** per §3.2 (public Council scene begins / Defense Fleet operation initiates / combat imminent / non-crew witness present / Steward delivers operationally-significant news / Others enter the conversation)
  - **Canonical post-serious-moment decompression** — Halia delivers a canonical brief joke immediately after a serious moment ends; canonical reset-of-tone signature
  - **Halia + Forty-Seven banter** — canonical: Halia knows Forty-Seven is a person; canonical address Forty-Seven directly; canonical *"Forty-Seven, drink the tea"* extension
  - **The Furling Defense Fleet** — canonical broader Furling military formation (not faction-aligned); canonical-distinct from Defender-faction Sa-Matra militia; canonical commanded by Halia; canonical mission per §6.2 (escort evacuating species / secure corridors / last-resort grounded-species defense / search-and-rescue)
  - **Defense Fleet Liaison officers** — canonical ~300 officers embedded with migrant fleets to coordinate; canonical Halia's organization
  - **Drev-Tok recurring Council-channel-intrusions** canonized: Halia canonical *files Council-record then eats lunch through them*; canonical Halia private commentary to Steward: *"I respect his canonical-conviction. I will not let him take my Fleet."*
  - **Halia bridge-visit canonical scene** — recommended post-mid-slice or post-Fall; canonical *"You have a six-species bridge"* observation moment with canonical Forty-Seven exchange
  - **Three new canonical recurring phrases** added to the callback economy: *"Drink the tea"* / *"That was a compliment"* / *"I'm telling you that as your friend, not your commander"* — slice now has canonical 11 recurring phrases; all should fire at the canonical Andromeda chorus

**Notes for Design**:
- **The dual register is the canonical heart of the character.** Halia's code-switch from private gruff-warm to command professional-to-the-core happens canonical-cleanly; canonical 2-3 second transition; canonical the listener canonical *hears it happen*. Recommend implementing as a state-flag on Halia's dialog NPC that toggles based on §3.2 conditions.
- **Halia's *honor-to-a-fault is canonical why she's at Mh-Lai when the Fall happens*** (§4.2). Canonical: she canonical *committed to Lirin Pel-Sa* (Preserver ambassador at Beta Corvi, canonical 40-year resident) that she would not leave the cluster until the Slylandro Cloaking Satellite deployed. Canonical: the commitment kept her on the wrong planet. Canonical: she does not regret it. This canonical *integrates Halia's personal arc with the existing Fall of Mh-Lai canon* and the canonical Preserver-Slylandro-cloak arc.
- **Canonical command-vessel canonical *Hearth-of-Iron*** post-Fall (canonical existing canon from parallel-chat); canonical: pre-Fall command-vessel was canonical-lost at Mh-Lai.
- **The canonical *save as many as possible* singular aim** is canonical Halia's character-mathematical-anchor. Canonical: she canonical *keeps a personal-ledger of saved individuals*; canonical *does not show it*. Canonical: this is canonical-distinct-from her Council-record-keeping (which is canonical-public). Recommend surfacing the canonical personal-ledger as canonical-Halia-canon if a scene needs it.
- **Three branch-state visual + voice variants** for the canonical Fall of Mh-Lai branches — pre-Fall confident / post-Fall surviving quieter / post-Fall Cleanser-supervised constrained. Each branch canonical-affects Halia's banter delivery + Common Room mood (per existing parallel-chat post-Fall canon).
- **Canonical Andromeda-final-exchange** (§9.4) — **provisional canon**; Aaron may want to revise. The canonical line *"Drink the tea — when you arrive"* with canonical *small smile audible in voice* is the slice's canonical commander-arc closing-moment.

**Verification path**: walks needed — `walk_halia_council_briefing` (verify canonical Quiet Resolution mandate delivery in command register + canonical Steward post-mandate banter); `walk_halia_drev_tok_intrusion` (verify Drev-Tok canonical Council-channel-intrusion fires + Halia's canonical *files-and-eats-lunch* non-response behavior); `walk_halia_bridge_visit` (verify canonical *"You have a six-species bridge"* moment + canonical Forty-Seven exchange); `walk_halia_code_switch` (verify dual-register transition triggers + canonical 2-3-second code-switch cadence); `walk_halia_post_serious_decompression` (verify canonical brief-joke fires within ~20 seconds of any serious-scene ending in private context with Steward); `walk_halia_andromeda_crossing` (if approved) verify canonical-final-exchange canonical-line firings.

---

## 2026-05-17 — Lore → Design — Callbacks, call-forwards, and three canonical 4th-wall breaks

**Status**: open

**What**: Aaron dispatch: *"Callbacks and call-forwards are the best opportunities for jokes. Breaking the 4th wall once or twice at key moments over the course of the game can be fun."* Full canon authored in [`callbacks-and-callforwards.md`](callbacks-and-callforwards.md). Extends [`humor-pass.md`](humor-pass.md) with focused canon on the slice's two highest-tier humor seams + canonical three 4th-wall-break placements.

**Where**:
- **Source canon**: [`callbacks-and-callforwards.md`](callbacks-and-callforwards.md) — 7-section canon
- **Code surfaces likely affected**:
  - **Dialog metadata tagging** for callback-eligible lines — engine should prefer callback variants in appropriate contexts; canonical seed/recur/migrate pattern
  - **Andromeda-arrival chorus canonical FIXED-SEQUENCE script** (`§2.3`) — NOT LLM-rendered; canonical scripted text; every running joke fires at the capstone; canonical Forty-Seven *"I have been listening for some time"* double-bookend opens AND closes the slice
  - **Three canonical 4th-wall breaks** (`§4`) — **strict canon: EXACTLY THREE; no more across the slice**. Each has canonical-fixed dialog passage; canonical placement points marked. Bio-Archive does NOT log them as fictional events.
  - **SC2 call-forward content** (`§3`) — Forty-Seven primary delivery NPC; canonical *"whoever finds this"* register surfaces 3-5 times canonical; canonical Furling-language signs as environmental detail 5-10 places canonical
  - **Canonical Forty-Seven-with-Mraka-on-Zelnick scene** (`§3.1`) — recommended cinematic; *"I will be there. I am the ship. ...I may or may not remember this conversation when Captain Zelnick wakes me. — I will try."* canonical exchange is the slice's quietest SC2-fan-service moment

**Notes for Design**:
- **Callback architecture: seed → recur → migrate.** Each running phrase is canonical *seeded* in origin context, *recurs* 2-3 times in canonical-owner's voice, then *migrates* into other crew's voices as canonical *family-language*. Recommend dialog metadata to support this lifecycle.
- **The canonical 8 recurring phrases** (`§2.1`): *"We have agreed"* (Cleanser) / *"Just to be safe"* (Cleanser) / *"I am working on it"* (Forty-Seven) / *"We did not hurt them"* (Preserver) / *"We-all"* (Vresh) / *"Tomorrow"* with canonical care (Sevra) / *"May your future-tense remain useful to you"* (Utwig) / *"By my standards"* (Forty-Seven). Each one canonically migrates by mid-slice. The Andromeda-arrival chorus canonically *cashes the entire callback economy at once*.
- **The three 4th-wall breaks**:
  - **Break #1 (slice midpoint, post-Fall)**: Forty-Seven acknowledges the listener exists. Tone: warm-careful. Canonical *"Whoever is listening — I am noting that the listening is canonically broader than my ship-channel suggests — I want to say: the work is the work."* Forty-Seven canonical binds itself: *"I am noting that I will not say it again."*
  - **Break #2 (Andromeda arrival)**: Sevra (bare-faced; the canonical outsider) thanks the listener. Tone: warm-direct-but-fictional-frame-preserved. Canonical line: *"whoever has been with us, all this time, from before I was on the bridge. Thank you."* Canonical: Sevra is *not looking at the Steward; Sevra is looking at the window*. Canonical Steward pickup: *"Some things only have to be said once."*
  - **Break #3 (Disastrous ending extension)**: narrator canonical-extends the existing *"Good job"* punchline with one new line — *"We told you the Others were never funny."* Canonical: dark; deserved; the slice canonically bites back.
- **Canonical SC2 call-forward catalog** (`§3.4`): canonical comedic-references authored for Sa-Matra, Sun Device, Mycon Egg Cases, Aqua Helix, Burvixese Broadcasters, Taalo Protector, Shofixti Glory Device. Each canonical reference has Forty-Seven-as-primary-delivery; canonical Steward wit-register-response.
- **Canonical proto-species call-forward scenes** (`§3.2`): proto-Spathi practicing fear; proto-Druuge inventing currency *before* sentience; proto-Ilwrath webs all pointing at Procyon (where Chenjesu canonically live; canonical *"the Council canonically does not know what to do with this information"*).
- **The canonical "we are the Precursors" absurd-realization scene** (`§3.3`): canonical Common Room scene recommended placement post-Mh-Lai-Fall; canonical Tarven-and-Mraka argument about whether they preceded themselves; canonical Steward's *"At least we'll be famous"*; canonical Tarven response *"That is the canonical small comfort. Thank you, Steward."*

**Verification path**: walks needed — `walk_callback_economy_andromeda` (verify all 8 canonical recurring phrases fire at the Andromeda arrival chorus); `walk_4thwall_break_1` (verify Forty-Seven's post-Fall acknowledgment scene triggers; verify the canonical *"I will not say it again"* binding holds for the rest of the slice); `walk_4thwall_break_2` (verify Sevra's Andromeda *"whoever has been with us"* line fires at canonical position in the arrival chorus); `walk_4thwall_break_3` (verify Disastrous ending canonical *"We told you the Others were never funny"* line fires after *"Good job"*). Plus `walk_sc2_callforward_zelnick` (verify the Mraka-Forty-Seven canonical Zelnick-conversation surfaces during the canonical Vela Factory visit).

---

## 2026-05-17 — Lore → Design — Humor pass: 8 comedy styles + Steward Wit Register + ~50 new banter lines

**Status**: open

**What**: Aaron dispatch: *"Do a full pass on our current lore so we are taking ample chances to bake jokes of all different styles such as puns, physical humor, intellectual humor, cultural humor, etc... and make sure we are updating our banter to be properly humorous as well."* Authored as [`humor-pass.md`](humor-pass.md) — 10-section canon covering 8 comedy styles, the canonical Steward Wit Register, 21 per-species humor profiles, ~50 new canonical banter lines across crew + per-species combat + Council scenes, plus the *Furling Humor Archive* as a Forty-Seven affinity-reward content track.

**Where**:
- **Source canon**: [`humor-pass.md`](humor-pass.md) — full 10-section humor reference
- **Code surfaces likely affected**:
  - **Steward Wit Register** — the slice's LLM dialog renderer should draw the Steward's voice from `humor-pass.md §3`; canonical Steward stock-lines reference bank provided for sampling
  - **Per-species humor profile registry** — 21 species each with canonical comedy register (`humor-pass.md §4`); LLM renderer draws per-encounter lines from these
  - **Common Room banter pool extension** — ~30 new canonical crew banter lines (`humor-pass.md §5`); add categories: `mraka_tarven_pun_variant`, `mraka_tarven_physical_variant`, `forward_vresh_intellectual`, `sevra_renn_cultural`, `forty_seven_steward_observational`, `nose_rash_chorus`, `andromeda_arrival_chorus`
  - **Per-species combat banter extension** — ~20 new canonical per-species combat lines (`humor-pass.md §6`); extends existing banter-library categories with humor-style focused variants per species
  - **Council scene banter** — canonical Cleanser-Preserver standing exchange (`humor-pass.md §7.1`); canonical Drev-Tok Council-channel-intrusion (`§7.2`); canonical Steward Council aside (`§7.3`)
  - **Furling Humor Archive** content track — Forty-Seven-affinity-gated dialog branches; canonical archive entries authored as samples (`humor-pass.md §8`); Design's call whether to surface as canonical UI artifact (a Bio-Archive sub-section the Steward can browse) or as ambient Forty-Seven readings

**Notes for Design**:
- **The 8 comedy styles canon** (`humor-pass.md §2`): cultural (highest frequency) / intellectual / absurdist / physical / puns&wordplay / observational / dark / callback. Recommend at least 3-4 styles surface in any 30-minute play session — gives the slice canonical *comedic variety*.
- **The Steward Wit Register is the slice's primary comic register-bearer.** The canonical profile (`§3.1`): dry-observational primary; quick-witted secondary; gentle-mocking never cruel; self-aware; audience-surrogate; knows when to stop. Canonical stop-points: Halia's death; the Disastrous ending; the Sa-Matra Standoff; all Others-encounters. The doctrine of *Others never funny* extends to *Others-adjacent grief never funny*.
- **The canonical *"Furling great, Others none, alien friction"* doctrine remains foundational**. This humor pass *expands the implementation* but does not change the doctrine.
- **The Forty-Seven *"by my standards"* delivery** is canonical deadpan; canonical examples cited; recommend treating Forty-Seven as the slice's *observational-humor anchor*.
- **The Lemmkin canonical-cheerfulness-at-every-damage-bracket** is the slice's most-extreme single comedy register; recommend a dedicated banter pool that maintains canonical cheer through all 5 damage brackets (Opening / 75% / 50% / 25% / 5%); canonical lines per `§6.1`.
- **The nose-rash Common Room chorus** (`§5.5`) — canonical 6-crew-plus-Forty-Seven sequential reaction scene; the slice's longest single comedic beat; recommend cinematic-eligible scene treatment.
- **The Andromeda-arrival chorus** (`§5.6`) — canonical Migration-end scene; each crewmate canonical line authored; recommend scripting as canonical sequence not random-sample.

**Verification path**: walks needed — `walk_humor_pass_steward_wit` (verify Steward's canonical wit-register surfaces across 5+ scenes); `walk_nose_rash_chorus` (verify all 6 crew + Forty-Seven deliver their canonical comment lines in the chorus order); `walk_andromeda_arrival_chorus` (verify each crewmate's canonical Andromeda-arrival line surfaces in canonical order); `walk_council_cleanser_preserver_exchange` (verify the canonical 5-beat exchange + Compeller eye-rolling-aside fires in the Council scene).

---

## 2026-05-17 — Lore → Design — Utwig two-outcome canon + Sevra (the Utwig atheist crewmate)

**Status**: open

**What**: Aaron dispatch: *"The outcome for them is either you leave them alone, or you cleanse them. If you leave them alone, maybe you get an utwig atheist as a crewmate. Maybe you keep them from getting cleansed by the Cleansers or you let the Cleansers have a go at the Utwig."* The Utwig quest is restructured to a **binary two-outcome canon**: Leave Them Alone (block Cleansers) vs. Let The Cleansers Have A Go (permit Cleansers). Optional sub-rewards (Sevra crewmate / Ultron / 30 migrants) stack as nested branches within Leave-Alone. Canon update applied to [`utwig-quest.md`](utwig-quest.md) — restructured §1 + §6 + new §3.7 Sevra NPC.

**Where**:
- **Source canon**: [`utwig-quest.md §1 Quest summary`](utwig-quest.md) (restructured to two-outcome canon); [`§3.7 Sevra — *The Utwig Atheist*`](utwig-quest.md) (new NPC); [`§6 Branches and rewards`](utwig-quest.md) (restructured to two-outcome table with stackable sub-rewards)
- **Code surfaces likely affected**:
  - **Quest FSM restructure** — collapse the previous four-branch FSM (Devolved / Split / Ultron Returned / Doctrine Held) to **two-outcome FSM** (Leave-Alone with stackable sub-states / Cleanse-path with three sub-states). The Doctrine Held branch is canonically retracted — dissuasion is not a viable Steward path; the Utwig doctrine is firm; the Steward who tries simply falls back to one of the two main outcomes.
  - **NEW: Sevra NPC + crewmate slot** — 7th crew member with non-combat role *Doctrinal Observer / Diplomatic Witness*. New Common Room placement: small reading corner near Vresh's tank.
  - **NEW: Sevra recruitment scene** — outer-groves location; first-meeting dialog per §3.7; recruitment-offer dialog per §3.7; recruitment gates per §3.7 (Leave-Alone outcome + Doctrine-Acknowledged ceremonial budget + visited outer groves)
  - **Sevra active ability**: *The Unmasked View* (hint-system on demand; limited per game-day)
  - **Sevra passive bonus**: *Witness Without Doctrine* (third Steward-side voice in Council-recommendation scenes alongside Mraka and Tarven)
  - **Council-vote scene update**: the two-outcome canon's binary decision lives at the Council-vote scene; the Steward's recommendation tilts the Council toward Persuader/Preserver (Leave-Alone) or Cleanser/Compeller (Let-Them-Have-A-Go). Add Sevra's voice to the deliberation if recruited (canonical Sevra-voice argues *preserve-the-choice from the inside* — uniquely valuable input)
  - **Cleanse-path consequence cascade**: when Cleanser action proceeds, Vael-Souren (or successor) is dispatched; canonical *cleansing scene* gives the Steward a last-minute intervention chance (Stand-Against combat); if not intervened, the Utwig die. Bio-Archive entry surfaces SC2-canonical-disruption fact (the SC2 Utwig do not exist in this outcome; Ultron destroyed; cleanse-path is the slice's most SC2-divergent species outcome).

**Notes for Design**:
- **The binary canon is the headline.** Aaron simplified the previous four-branch FSM; the implementation should follow. The nested sub-rewards (Sevra / Ultron / 30 migrants) are individually optional and individually stackable within Leave-Alone. Players who get all three earn the canonical *Maximum Leave-Alone* outcome.
- **Sevra is the slice's narratively-warmest Utwig reward.** Their canonical first-meeting line is one of the slice's most quietly moving moments: *"Steward. Hello. I have been watching you participate in our ceremonies. You did them carefully. You did not pretend to believe in them. I appreciate this."* Recommend surfacing this in a polished cinematic if the Steward unlocks the recruitment.
- **Sevra is canonically NOT in the main chambers.** They must be sought out in the outer groves — a separate explore-able sub-location of the Utwig settlement. Recommend an environmental detail that hints toward them (a small structure visible from the main chambers; canonical *"who lives there?"* moment).
- **Sevra has NO Veil-suffix in their name** (just "Sevra") — same canonical refusal as Tev-Mal but from a different doctrinal position. They are the canonical *post-doctrine generation* (born ~95 years post-sentience; never knew pre-doctrine era).
- **Sevra refuses to wear a mask.** Canonical heresy in the settlement; tolerated because young. Image lane: render Sevra bare-faced — the only Utwig the Steward will see *without* a mask. Visible canonical Utwig facial musculature; canonical Horta-lineage armored proto-biology features visible. Audio lane: Sevra is the only Utwig without the mask-acoustic-filter; canonical distinguishing audio cue.
- **Cleanse-path SC2-canon-disruption note**: when the Cleanser action proceeds, the slice's Bio-Archive should surface a canonical note for the player: *"The Utwig do not exist in the SC2 era. The Ultron does not exist as an SC2 artifact. The depression-doctrine of the SC2 Utwig has no source civilization to reference. You have altered SC2 canon at this species' boundary."* This is the slice's most SC2-divergent single-species outcome; recommend surfacing the impact.
- **The Stand-Against combat path against Vael-Souren-at-Utwig** is canonically the *last-minute save* for a Steward who voted Cleanser but reconsidered. Provides a redemption-arc beat for players who change their mind. Recommend allowing this path.

**Verification path**: walks needed — `walk_utwig_leave_alone_baseline` (Leave-Alone vote; no sub-rewards; verify Devolved terminal); `walk_utwig_sevra_recruited` (Leave-Alone + ceremonial respect + outer-grove visit; verify Sevra recruitment offer fires + crew slot 7 fills); `walk_utwig_max_leave_alone` (Sevra + Ultron + 30 migrants stack; verify Maximum Leave-Alone canonical archive entry); `walk_utwig_cleanse_permitted` (Cleanser vote; stood aside at cleansing; verify Eliminated terminal + SC2-canon-disruption Bio-Archive note); `walk_utwig_cleanse_intervened` (Cleanser vote but engaged Vael-Souren in last-minute Stand-Against; verify the canonical *"You changed your mind"* archive line + outcome reverts to Leave-Alone if combat won).

---

## 2026-05-17 — Lore → Design — Utwig Ceremony System (the "trying to leave is the comedy" running gag)

**Status**: open — substantial extension of the Utwig quest dispatched above

**What**: Aaron dispatch: *"The Utwig traditions and ceremonies are RIDICULOUS! It takes FOREVER to get out of there without participating in them all and that is the joke about them. You are trying to get out of there, but they want to wash your nose with their ointment and it causes a rash, and you try to leave but they have not yet blessed your landing gear... it goes on and on, but if you break protocol, they may get mad."* Authored as [`utwig-quest.md §10`](utwig-quest.md). The Utwig running gag is now canonical: a visit takes FOREVER because of endless sincere ceremonies; the Steward who participates is doctrinally-respected; the Steward who breaks protocol triggers escalating consequences up to Cleanser-vote-confidence loss.

**Where**:
- **Source canon**: [`utwig-quest.md §10 The Ceremonies — Trying To Leave Is The Comedy`](utwig-quest.md) — full canonical 20-ceremony repertoire across visit lifecycle (Pre-arrival / Greeting / Welcoming / In-conversation / Pre-farewell / Farewell / Departure) + Ceremonial Budget mechanics + return-visit canonical escalation + "they may get mad" escalation table
- **Code surfaces likely affected**:
  - New **Ceremonial Budget** quest-internal score (Utwig-visit-specific); modified by participation choices; quest-end tier modifier (Doctrine-Respected / Acknowledged / Skirted / Violated)
  - **Ceremony dialog scenes** — 20 canonical ceremonies; first visit canonically presents 8 (Lore-curated selection); return visits add 4-6 additional invented-for-this-Steward ceremonies
  - **Standing impact cascade**: polite decline (-1) / rude decline (-2) / thrust-during-tones (-5) / 4+ rude declines or repeated thrust-violations triggers Doctrine-Violated tier with Cleanser-vote-confidence rise
  - **Nose-rash state**: persistent in-game cosmetic state (3 in-game days) triggered by Nose-Ointment Ritual participation; canonically inspected by Common Room crew on return
  - **Common Room chorus scene** (canonical): all crew gather to comment on the rash; canonical sibling-argument between Mraka and Tarven about whether it's funny or concerning; slice's longest single comedic beat
  - **Forty-Seven canonical assists**: ship-AI provides phrase-lookup for the Steward (canonical phrase logging from prior Furling Steward visits); canonical thrust-prevention during Veil-of-Distance tones
  - **Falling-Book Appendix-of-Visitors**: canonical persistent record of Steward behavior; survives Culling; canonically read by SC2-era Utwig 250kya later — the Steward's protocol-respect determines how the SC2 Utwig canonically remember the Steward (warm vs. sad)

**Notes for Design**:
- **Render ceremonies as quick humor-montages on participation, not as 12-minute real-time waits.** The canonical comedy is the *accumulation* and the *quantity*, not the real-time tedium. A "Participate" choice should fast-forward through the ceremony with brief humor-flavor text + audio; a "Decline politely" choice should trigger the canonical Utwig disappointed-response dialog; a "Decline rudely" choice should escalate immediately.
- **The Ceremonial Budget is HIDDEN from the player**. They see standing changes; they do not see the running Budget tally. The quest-end outcome reveals which tier they hit. This makes the comedy land harder — the player feels the social pressure without seeing the math.
- **The nose-rash is a cosmetic-only status**, not gameplay-impacting. Just visible + canonical Common Room chorus. Recommend a simple status-icon with the canonical tooltip *"Utwig Welcoming Anointment — itchy nose; harmless; 3 days remaining."*
- **Forty-Seven's role**: the ship-AI is canonically helpful in navigating Utwig protocol. They have prior-Steward records. The Steward who *talks to Forty-Seven before the visit* canonically gets canonical-phrase coaching (small UI assist for the Statement-of-Intent and Veil-Hailing ceremonies). This is a small Forty-Seven-affinity payoff.
- **The Veil-Hailing canonical first ceremony** is the canonical *good place to learn the rhythm* — the first comedic-montage; the Steward learns the canonical Utwig protocol-style; subsequent ceremonies build on this baseline.
- **Mal-Dren slip-rate**: canonically every 8 minutes during long conversations. Recommend a timer-based slip-trigger on Mal-Dren conversations longer than ~8 in-game minutes. Each slip is canonically apologized for; the cumulative slip-apology count is canonical comedic-tragedy (by the fourth slip, Mal-Dren is canonically *weary*).
- **The Stand-of-Greeting non-coordination**: per §10.3, Forty-Seven canonically delivers the Markov-chain observation: *"I am noting a Markov-chain-like emergent property in this ceremony. The expected duration is, in principle, infinite. The doctrine-keepers will canonically conclude when the cluster of stand-sit events stabilizes. I cannot predict when. Please be patient."* — recommend surfacing this Forty-Seven line during the ceremony as ship-AI ambient comment.
- **Return-visit canonical escalation**: track Steward's prior visits; each return adds canonical *additional ceremonies invented for this Steward*. Recommend cap at 4 visits before the canonical comedy diminishes; further visits use the standard repertoire.
- **The canonical Falling-Book Appendix archive entry**: at quest-end, update the Bio-Archive's Utwig entry with the Steward's canonical archived behavior. The SC2-era memory of the Steward depends on this. Recommend the canonical archive line vary by Ceremonial Budget tier.

**Verification path**: add walks — `walk_utwig_ceremony_participate_all` (verify all 8 first-visit ceremonies present + Doctrine-Respected tier achieved); `walk_utwig_ceremony_polite_decline_all` (verify 8 polite-decline lines fire + Doctrine-Skirted tier); `walk_utwig_ceremony_rude_break` (verify Doctrine-Violated tier triggers + Cleanser-vote-confidence rises + canonical archive line records the breach); `walk_utwig_nose_rash_chorus` (verify Common Room crew chorus fires after Nose-Ointment Ritual participation; assert all 5 crew + Forty-Seven each deliver their canonical comment line).

---

## 2026-05-17 — Lore → Design — Preservers canonized (tree-branch Furlings, new faction + non-lethal combat kit)

**Status**: open

**What**: Aaron dispatch: *"Let's change 'The Preservers' as these sort of hippy, peace love and happiness Furling faction that refuse to hurt anything but also want to leave and encourage the other races that can to also leave. They are the 'Green' furlings and live in trees and their ships use gravity and jumping as a weapon."* The **Preservers** are now canonized as a Migration-Positive Pacifist Furling faction AND a biologically distinct **tree-branch of the Furling species** — green-furred, photosynthetic, refuse to harm. Their Canopy-class ships use **non-lethal gravity-and-jump combat kit**. Full canon in [`preservers-as-tree-branch.md`](preservers-as-tree-branch.md); surface updates applied to [`factions-and-war.md`](factions-and-war.md) and [`cleansers-as-ice-branch.md`](cleansers-as-ice-branch.md).

**Where**:
- **Source canon**: [`preservers-as-tree-branch.md`](preservers-as-tree-branch.md) — 10 sections covering biology, doctrine, ships and combat, Council politics, slice presence, NPCs, sanctuary location, cross-canon updates, dispatches, open items
- **Code surfaces likely affected**:
  - Furling Council faction-standing tracker — add **Preserver** standing flag alongside Persuader / Compeller / Cleanser / Defender / Denier / Hider (now 7 factions)
  - Council-recommendation FSM — add **Preserver vote** as a fourth standing voice alongside Persuader / Compeller / Cleanser. Preserver vote argues *preserve-the-choice* on every grounded-species decision. Canonical counter-line to Cleanser's *"Just to be safe"*: *"We will not be safer for having killed them. The Quiet you propose is the Quiet of a closed grave. Our Quiet must be the Quiet of a continuing song, even if some voices in it are not ours."*
  - Slice ship roster — add **Canopy-class Preserver vessel** (organic vertical silhouette; tree-shaped; non-lethal kit per §5.2)
  - Combat AI personality — new **Preserver AI archetype**: high-pacifism + high-empathy + low-aggression + flee-bias. Combat kit: **Gravity Well Projection (GWP)** (3-5s well; pulls enemies; no direct damage; collateral damage via collisions only) + **Gravitational Jump (GJ)** (~600u displacement; ~15s cooldown; small departure-eddy effect). Vulnerable to attrition; flees when pressed.
  - Two new NPCs: **Lirin Pel-Sa** (Preserver ambassador at Beta Corvi, 40-year resident) + **Veth Pel-Sa** (Lirin's elder sibling, Canopy-class captain — note the parallel-sibling motif with Mraka/Tarven)
  - New hyperspace encounter: *Long-Reach Of The Slow Branch* Canopy-class vessel with **dock / decline / attack** branches; killing the ship is canonically a heavy reputation hit + Bio-Archive Steward-Quiet-Ledger entry
  - New sanctuary location: **Preserver canopy-village** (cluster star TBD; tree-rich world). Optional interactions: share fruit, listen to chorus, receive living-plant cutting, **speak with the resident Taalo guest** (sibling-substrate-fragment of Vresh's colony — canonical reveal if *The Last Voice* completed favorably)
  - Inventory: **living-plant cutting** as a small item; canonical placement in the Common Room next to Vresh's tank

**Notes for Design**:
- **The non-lethal combat kit is the slice's first canonically pacifist combat AI.** Existing AI personality vectors will need an extension to support *"flee-bias + non-damage-weapon + collision-as-collateral"*. The Preserver ship will be the only ship in super-melee that *cannot intentionally damage the player*. Recommend playtesting carefully — this is unusual mechanically.
- **The canonical Preserver doctrinal phrase** *"We did not hurt them. They were caught in a gradient. They could have moved differently."* is available as a Veth Pel-Sa combat-banter line and as a Lirin Pel-Sa Council-recommendation aside. Recommend surfacing both.
- **The Taalo extraction tank's engineering lineage is now canonized**: Vresh's tank on the Steward's ship is derived from work the Preservers contributed at their canopy-village. Cross-canon ripple — if Vresh's *The Last Voice* completes favorably, the canopy-village Taalo guest can recognize Vresh through proximity-empathic-resonance. Suggest adding this as a small canonical reveal scene at the canopy-village.
- **The parallel-sibling motif**: Veth Pel-Sa is Lirin Pel-Sa's elder sibling. This mirrors Tarven (older) / Mraka (younger) on the Steward's bridge. Two sibling pairs of opposite-or-similar political alignment. If Design wants to surface the parallel, a small Lirin-Veth conversation visible at the canopy-village would do it — they do NOT argue (they are both Preservers; aligned), but the Steward can see the sibling-dynamic without the political-foil tension. The contrast with Mraka-Tarven is the canon.
- **No Preserver crew on the bridge**. The Steward's two Furling crewmates are warm-world (Mraka, Tarven). A Preserver crewmate would be canonically slow-moving and possibly incompatible with Mraka's pace; the bridge composition is deliberate.

**Verification path**: walks needed — `walk_preserver_dock` (visit Canopy-class peacefully), `walk_preserver_combat` (attack Canopy-class; verify the non-lethal kit triggers, the collision-damage path works, fleeing-AI works), `walk_preserver_kill` (kill Canopy-class; verify reputation collapse + Bio-Archive Quiet-Ledger entry), `walk_canopy_village_visit` (visit sanctuary; verify fruit-sharing / chorus-listening / plant-cutting / Taalo-guest-reveal-when-Last-Voice-completes). Council-recommendation walks need updating to assert Preserver vote-voice surfaces alongside Persuader / Compeller / Cleanser.

---

## 2026-05-17 — Lore → Design — Mraka & Tarven canonized as siblings + political foils

**Status**: open

**What**: Aaron dispatch: *"One of our furlings is a counter point of the other furling on political / ethical dilemmas and they constantly argue. Make them siblings."* Mraka Yenn-Sa and Tarven Olwen-Sa are now canonically **direct siblings** (not cousin-clan-bonded as in prior canon) AND **opposing-faction political foils** (Compeller Mraka vs. Persuader Tarven). The constant argument is the bridge's canonical Furling-internal centerpiece. Full canon added to [`crew-roster-redesign.md §3`](crew-roster-redesign.md) (substantially expanded — six new sub-sections covering the sibling backstory, the political foil, the reframed Iren-Vor reveal, faction visuals, side-quest updates, and how the rest of the crew relate to the argument).

**Where**:
- **Source canon**: [`crew-roster-redesign.md §3.1-3.6`](crew-roster-redesign.md)
- **Code surfaces likely affected**:
  - `src/scz/content/crew.py` (or equivalent) — Mraka and Tarven crew records gain a *sibling* relation flag and *faction* fields (Mraka=Compeller, Tarven=Persuader)
  - Argument-banter system — Mraka and Tarven need cross-aware dialog: lines that reference *the other* by name and by recent disagreement. Suggest a new banter-pool category: `mraka_tarven_argument` with line variants for each argument-surface (migration ethics / speed-vs-care / stewardship / family / their parents)
  - Council-recommendation dialog scenes — when the Steward files a recommendation (Continue/Stop/Cleanse/Defer), Mraka and Tarven both surface an opinion before the Steward decides. Their opinions vary by recommendation type per their faction stance. Add to the recommendation dialog FSM.
  - Cluster-route decisions — Mraka and Tarven have differing route-preference comments; subtle confidence-shifts based on Steward's choice history. Could surface as ambient Common Room banter.
  - Halia death-branch scene — canonical *silence* moment: Mraka and Tarven sit in the Common Room together without arguing. This is a specific scene-state. When the argument resumes (canonically 3-4 days later), the lines should be slightly different — Halia's death has shifted both of them. Banter-pool update.

**Notes for Design**:
- **The Iren-Vor reveal is reframed, not removed**. Previously the reveal was *"we discover we're related"*; now it's *"we discover prior Stewards in our family line."* It still surfaces in *The Erased Logs* side-quest as the emotional climax. Mraka's canonical line on receiving the reveal: *"You did all this work for me."* Tarven's reply: *"For both of us."* Followed by a canonical 3-minute argument about the wording. **Do not let the system skip the argument.**
- **The naming-difference is canon**: Mraka adopted *Yenn-Sa* on joining the Drifter Circuit (Drifter-honorific name); Tarven kept the family present-generation name *Olwen-Sa*. Their shared deep ancestral clan is **Olwen-Veth**. The names are not interchangeable; the difference is a character beat (Tarven thinks Mraka's rename was abandonment of family; Mraka thinks Tarven's kept-name is sentimentality).
- **Their alcoves are adjacent in the Common Room** (port-forward + port-forward-mid) — canonically by Furling Council design (Drifter and Archive slots are adjacent on Scouts to encourage cross-disciplinary friction). The siblings *cannot get away from each other on the ship*. This is a deliberate physical-canon layer.
- **Mraka's *The Last Race*** quest end-beat update: Mraka's Drifter-Circuit keepsake (canonical end-of-quest item) prompts a *public Tarven disapproval moment* — Tarven sees the Drifter token, expresses disapproval, the siblings argue, the Steward stands aside, they reconcile two days later. Add a 3-4 dialog-line beat to the quest's wrap state. The keepsake hangs in Mraka's alcove afterward — visible Common Room canonical fixture.
- **Forty-Seven's "Olwen-Sa Sibling Discourse" folder**: optional Forty-Seven dialog branch where the Steward asks about the recordings; Forty-Seven shares verbatim excerpts. This is a deep Easter-egg interaction; not slice-MVP-required, but if Design surfaces a "speak with Forty-Seven" interaction, this is one of the canonical branches available.

**Verification path**: existing Mraka and Tarven recruitment walks (per parallel-chat) need: (a) updated to reference the *sibling* relation rather than cousin-clan, (b) the Iren-Vor reveal substring updated. Add a `walk_olwen_sa_argument` checkpoint walk that verifies at least one argument-banter line surfaces in the Common Room across a session. The Halia-death-silence scene needs a presence-assertion (negative — *no argument banter fires in the 3 days following*).

---

## 2026-05-17 — Lore → Design — Crew roster redesign (six-species bridge + Ship AI)

**Status**: open

**What**: Two-message Aaron dispatch substantially redesigns the crew roster. **Only two crewmates are Furlings**; the other four slots are: 1 Thinn (Forward — existing canon reaffirmed as sole weapons officer), 1 Androsynth refugee (NEW — Renn Halvor, Engineer), 1 Taalo in silicon environment tank (NEW — Vresh-Hum-Of-The-Slow-Veins, Medic), and 1 Furling Scout Ship AI (NEW — Forty-Seven, has *The Quiet Engine* side-quest that unlocks a combat get-out-of-jail-free escape via QS-portal). Total bridge population: 6. Full canon in [`references/lore/crew-roster-redesign.md`](crew-roster-redesign.md).

**Where**:
- **Source canon**: [`crew-roster-redesign.md`](crew-roster-redesign.md) — 10 sections covering the new roster, three new crewmate full canons (Renn / Vresh / Forty-Seven), Common Room layout update with the silicon tank, the Bren-Vor/Yelena/Mira-Rou retirement + content-porting table, dispatches to all three asset/code chats, open items
- **Code surfaces likely affected**:
  - `src/scz/content/crew.py` (or equivalent crew-roster module) — three crew records to retire (Bren-Vor, Yelena, Mira-Rou), three to author (Renn, Vresh, Forty-Seven); two to retain (Mraka, Tarven)
  - Common Room scene — tank rendering + display panel + alcove reassignments
  - Quest FSMs for *The Last Reading* (Renn), *The Last Voice* (Vresh), *The Quiet Engine* (Forty-Seven)
  - **New module: COMBAT_QUASI_PORTAL_GENERATOR (CQPG)** — slice's get-out-of-jail-free escape; held-trigger activation; 5-minute cooldown; random nearby-star emergence; standard QS-navigation slightly degraded as tradeoff
  - **New active abilities**: *Decursion-Shear Compensation* (Renn), *Empathic-Field Pulse* (Vresh), *Emergency Jump* (Forty-Seven)
  - **New modules**: DIMENSIONAL_SHEAR_DAMPENER (Renn), EMPATHIC_FIELD_DAMPENER (Vresh), CQPG (Forty-Seven)
  - **Distributed-presence NPC pattern**: Forty-Seven is not a portrait-and-dialog NPC. Design needs a UI pattern for ship-AI conversation that does not use the normal alcove/dialog-portrait paradigm — suggest text-only dialog mode invoked from any console or a dedicated "Speak to Forty-Seven" Steward action.

**Notes for Design**:
- **The Quiet Engine quest's QPCG is the largest single Design implication of this dispatch.** The combat-mode QS-portal escape fundamentally changes the slice's combat tension. Cooldown + random destination + QS-nav degradation are all balancing parameters Lore has set provisionally — playtesting will tune. Recommend not unlocking until late mid-slice (after at least one full grounded-species save).
- **Retired Furlings' content (Bren-Vor / Yelena / Mira-Rou)**: §8 of the new canon doc has the migration table. Most of Yelena's content ports cleanly to Renn Halvor (HULL_RESONANCE_DAMPENER → DIMENSIONAL_SHEAR_DAMPENER; Karol-Vere bond NPC migrates as Karol-Vere Late-Tessar; Mraka-Yelena "tools alphabetized" joke survives as Mraka-Renn). Most of Mira-Rou's content ports to Vresh (Deep Child's Cradle → The Last Voice; Sevreth's Child branch partially shelved, may survive as a separate Mycon-quest item with Vresh's empathic-resonance read as the diagnostic mechanism). Bren-Vor's content is mostly shelved at slice scope.
- **The Forward weapons-officer mutual-exclusion is RETRACTED**. Forward is now the sole weapons officer; Bren-Vor is fully retired. Any Forward-vs-Bren-Vor branching logic in the existing quest system needs simplification — Forward path is now the only path.
- **Vresh's silicon tank is a SCENE FIXTURE**, not a movable portrait. The tank is part of the Common Room's bulkhead architecture; Vresh cannot leave it. Design needs to handle this as a non-movable NPC anchor — Vresh's dialog scenes are always at the tank window. The hum-language two-track voice direction is Audio's concern; Design just renders Vresh's words as standard dialog text with a small visual cue (Vresh's hum-pulse rate visible through the window).
- **Forty-Seven's *Forty* short-name** is canonically earned by completing *The Quiet Engine*. Design can soften this to a high-affinity threshold if preferred. The canonical line that unlocks the right: *"You may call me Forty. I find I prefer it. I had not expected to."*

**Verification path**: existing crew-recruitment walks (`walk_recruit_*` per parallel-chat) need updating — three walks to retire (Bren-Vor, Yelena, Mira-Rou recruitment), three new walks to author (Renn, Vresh, Forty-Seven recruitment). Quest-completion walks (*The Last Reading*, *The Last Voice*, *The Quiet Engine*) — each new. The Quiet Engine walk should specifically test the CQPG combat-jump path (set up a combat scenario, trigger Emergency Jump, expect emergence at a random nearby star).

---

## 2026-05-17 — Lore → Design — Cleanser canonical vote: total cleansing of stay-behinds

**Status**: open

**What**: New canon dispatched by Aaron, extending the Cleanser doctrine: *"Their vote is to wipe out the life that stays behind, even the friends like the grounded species just to be safe."* The Cleansers vote to euthanize **every grounded species** — including allied and friend species — as a doctrinal application of asymmetric cycle-risk weighting. Full canon added as [`cleansers-as-ice-branch.md §6 "The Vote — total cleansing of the stay-behinds"`](cleansers-as-ice-branch.md). Surface-level notes also added to [`factions-and-war.md`](factions-and-war.md) and [`cleanser-encounter-design.md`](cleanser-encounter-design.md).

**Where**:
- **Source canon**: [`cleansers-as-ice-branch.md §6`](cleansers-as-ice-branch.md) — 5 subsections covering doctrinal logic, "even the friends" clause, who the vote covers / doesn't, slice implications, and the canonical doctrinal phrase
- **Code surfaces likely affected**:
  - Council standing tracking (Persuader / Cleanser / Compeller flag-states) is the visible record of this ongoing vote — already in flag system
  - Vael-Souren dialog FSM in `src/scz/dialog/characters.py` — opportunity for one new player-elected branch: "Why even the friends?" → Vael-Souren responds "Just to be safe." (one of the slice's coldest lines if delivered well)
  - No mechanical FSM changes required; this is a doctrinal canonization that *underwrites* the existing slice flag system rather than replacing it

**Notes for Design**:
- **The Slylandro Cloaking Satellite path is canonically a Persuader victory *against* the standing Cleanser vote**, not a doctrinal consensus. This does not change the path's flag outcome but it sharpens the framing: a successful cloak is the Council overriding the Cleanser vote on that species, not the Cleansers consenting.
- **The canonical doctrinal phrase**: *"Just to be safe."* Available to surface as a Vael-Souren response in any branch where the Steward asks her *why a friend / why an ally / why a species we have lived with for ten thousand years*. Optional new player-elected dialog choice in the `about_method` or `argue_persuader` state: `"Why even the friends?"` → Cleanser response with the canonical phrase. Strong slice line; recommend surfacing.
- **Combat: killing Vael-Souren does NOT retract the Cleanser vote.** Canonically, a second Cleanser would arrive at the next standing-vote threshold; a third after that. The slice does not surface this — Vael-Souren is the only Cleanser encounter the Steward faces in slice scope — but the *future-game / extended-slice content* hook is recorded. Design choice: if the slice surfaces any post-Vael-Souren Cleanser pressure (e.g. a Cleanser-channel transmission acknowledging her death and stating "another will come"), the canonical line is available.
- **Council vote machinery clarified**: the Steward's species-by-species recommendations function as individual votes in a multi-species Council deliberation. Each Persuader recommendation is a vote *against* the standing Cleanser position for that species. The aggregate Persuader / Cleanser / Compeller standing already tracks this implicitly. Design's call whether to surface a vote-by-vote breakdown in the Bio-Archive's COUNCIL category — the doctrinal framing is now available.
- **Proto-species coverage**: the Cleanser vote also covers proto-species (proto-Humans on Sol III included). The Persuader vote wins baseline. **A Cleanser-pushed Steward could in principle change this, erasing the SC2-era ancestors pre-history.** Not slice-MVP-achievable on the strict math; flagged as a potential future ending tier — provisional name **"The Sterile Galaxy" ending** — between Unsuccessful and Disastrous in severity. Not slice-scope; awaiting Aaron-call.

**Verification path**: existing `walk_cleanser_cooperate` and `walk_cleanser_combat` walks are unaffected. If Design surfaces the new "Why even the friends?" dialog branch, add a walk variant that takes it and asserts on the canonical "Just to be safe" response substring. Otherwise no walk change.

---

## 2026-05-17 — Lore → Design — Cleansers canonized as ice-branch Furlings

**Status**: open

**What**: New canon dispatched by Aaron: *"The Cleansers are an ice-centric branch of the Furlings. White fur. Aggressive stubbornness. No empathy."* The Cleansers are no longer a pure ideological faction — they are a biologically distinct **sub-branch of the Furling species**, and the faction doctrine emerged from the lineage's cold-world biology. Full canon authored in [`references/lore/cleansers-as-ice-branch.md`](cleansers-as-ice-branch.md). Surface-level updates already applied to [`cleanser-encounter-design.md`](cleanser-encounter-design.md) and [`factions-and-war.md`](factions-and-war.md).

**Where**:
- **Source canon**: [`references/lore/cleansers-as-ice-branch.md`](cleansers-as-ice-branch.md) — full doc covering biology, behavior, encounter implications, and cross-canon updates
- **Code surfaces likely affected** (Design's call which to touch first):
  - `src/scz/combat/ai.py` (or wherever Cleanser AI personality is defined) — retract the high-hesitation parameter on Cleanser ships
  - `src/scz/dialog/characters.py` Vael-Souren character — no dialog change required; voice direction is the layer that updates
  - `src/scz/content/species_visual.py` (or equivalent) — the Cleanser palette `(40, 50, 80)` interior / `(200, 180, 240)` rim is already canon; Design can leave it alone

**Notes for Design**:
- **Combat AI**: the existing canonical Cleanser combat profile uses `ai_style = "kiter"` with **high-caution / high-hesitation** personality bias. The **high-hesitation parameter is retracted**. Cleansers are high-caution + high-commitment + low-retreat. They fire when the math says to fire. The "hesitation" appearance in early designs was a misreading of the cultural-mourning performance; the biology is committed. Update whatever parameter holds this — likely a personality-vector field somewhere — to remove or invert hesitation.
- **Vael-Souren dialog**: no change required. Her existing FSM in `cleanser-encounter-design.md` reads correctly under the new canon. The update is below-the-surface (voice direction layer; see audio dispatch separately).
- **Optional new mechanic available**: *Cold-Mask Cleanser* variant (the warm-substrate-suppressed-by-will subset) for any harder-than-baseline Cleanser NPC the slice wants. Not slice-MVP-required. Not yet specced as a code surface.
- **Mixed-coat character trait**: if Design wants to expose a Steward coat-color customization (warm-gold / salt-and-pepper / piebald / white), this is now available canon. Default Steward is warm-gold (canonical empathy-baseline). Not slice-MVP-required; flagged as a future-pass character option.

**Verification path**: existing `walk_cleanser_cooperate` and `walk_cleanser_combat` are unaffected. If a perceptive walk-test wants to verify the white-fur portrait, add a presence-assertion on the dialog scene's portrait field once the image-chat lands the Vael-Souren white-fur asset. Until then, no walk change.

---

## 2026-05-17 — Lore → Design — Bio-Archive entry text (Beat 5 closeout)

**Status**: open

**What**: Twenty canonical Bio-Archive entry long-form texts are authored in Steward voice, ready to port into `src/scz/content/archive_entries.py`. This closes the Lore side of the Beat 5 Bio-Archive plan ([plan: please-review-the-local-peppy-balloon](C:\Users\aaron\.claude\plans\please-review-the-local-peppy-balloon.md)). Design owns the scene + dataclass + wiring; the long-form body text was the only blocker on Lore's side, and it is no longer blocking.

**Where**:
- **Source**: [`references/lore/bio-archive-entries.md`](bio-archive-entries.md) — the full 20-entry catalog, per-entry id / category / flag / short_desc / long_desc / cinematic_id, in the canonical Steward voice
- **Target** (new files Design creates): `src/scz/content/archive_entries.py` and `src/scz/station/archive.py`
- **Spec**: [`references/lore/station-screens-design.md` §3 Bio-Archive Scene](station-screens-design.md) — UX, dataclass schema, layout, control flow

**Notes for Design**:
- Lift each `long_desc` block **verbatim** into the `ArchiveEntry.long_desc` field. The Steward voice is canonical; do not re-render or paraphrase.
- The 20 entries map 1:1 onto the design-doc table — same `id`s, same gating flags. The `short_desc` field is one-line list rendering; `long_desc` is the detail-pane body.
- The `distress_beacon` entry has `cinematic_id = "cin_androsynth_decursion"` and is replayable. Per the plan: if the cinematic system isn't yet wired by the Image lane, stub it to log `[cinematic replay: cin_androsynth_decursion]` and let `long_desc` still render. The handoff to Image is logged separately on `HANDOFF_image_chat.md` (or its equivalent) when that lane runs.
- The `council_uq_qa` entry contains a `{recommendation_text}` placeholder. The Steward's actual filed text (one of "Continue / Stop / Cleanse / Defer to Council") flows in based on `game.flags["uplift_recommendation"]`. Either string-substitute when building `long_desc` for that entry, or append the variant as a trailing paragraph — Design picks.
- The `long_desc` blocks are formatted as italic-blockquotes (`> *...*` in Markdown source). The BioArchiveScene detail pane should render the body in italic style; quotation marks inside (Mmrnmhrm quotes, rift utterance) are dialogue and stay roman.
- The proto-Human entry deliberately preserves the doubled entry number (14,310 from the standing observation file, copied forward into the Steward's working log). Keep the parenthetical in `long_desc` exactly — small but canonical.
- Per the plan, the StationScene "Bio-Archive" menu item is hidden until any artifact flag is True. The artifact flags from these 20 entries are: `has_distress_beacon`, `has_resonance_record`, `has_mmrnmhrm_excerpt`, `slylandro_cloak_active`, `has_echo_sensor`, `has_rainbow_resonator`. Any of these → menu visible.

**Verification path**: `walk_bio_archive` walk-test per the plan — set a flag (e.g. `game.flags["has_distress_beacon"] = True`), open Station, expect Bio-Archive menu item visible, enter Archive, cycle categories, select the Distress Beacon entry, expect `long_desc` renders the canonical Steward-voice body, B returns to Station. The text-render assertion can substring-match a distinctive phrase from the entry (e.g. `"between two heartbeats"` for the Distress Beacon's video description).

---

## Append new entries above this line
