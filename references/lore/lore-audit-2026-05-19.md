# Lore Audit — 2026-05-19

> Comprehensive audit of canonical-lore-content for canonical-stubs, placeholders, stale-cross-references, and missing-canon. Aaron dispatch: *"Do a full lore audit. Are there any placeholder or stubs left for lore?"*
>
> **TL;DR**: Surprisingly little canonical-prose is canonical-stub. Most "stub" markers in `species_inventory.csv` are canonical-RESOLVED in canonical-newer-canon-docs but the canonical-spreadsheet itself canonical-hasn't-been-updated (Design's job). The canonical-real canonical-Lore-lane canonical-actionable items are: (1) **`species-the-planar.md` needs canonical-rename + canonical-content-refresh to canonical-Thinn-canon** (2) **`species-sheets.md` is canonical-stale by canonical-many-species** (only 8 species canonical-have canonical-§1-§7 sheets; canonical-13+ species canonical-have canonical-rich canonical-canon canonical-elsewhere but canonical-no canonical-formal sheet) (3) **`species-content-backlog.md` finalized-picks table canonical-uses canonical-RENAMED-names** ("The Defiant", "The Curious") instead of canonical-current canonical-Mrokon/Lemmkin. Plus a canonical-few canonical-LOW-severity housekeeping items.

---

## Severity HIGH (canonical-Lore-lane canonical-actionable; canonical-NOT canonical-blocking-MVP but canonical-canon-coherence canonical-suffers)

### HIGH-1 — `species-the-planar.md` is canonical-stale-name + canonical-stale-content

**Status**: Canonical-source-of-truth-doc canonical-still canonical-named `species-the-planar.md` and canonical-content canonical-still canonical-describes them as canonical-"The Planar". Canonical-Aaron canonical-renamed them to canonical-Thinn on 2026-05-17 (canonical *literally Thinn AND they Thought they could stay by facing sideways*). Canonical-12 other lore docs already use canonical-Thinn-canon (HANDOFFs + loop-closing + gemini + cross-awareness + halia + humor + utwig + cleansers + crew-roster). Canonical-no `species-the-thinn.md` file exists.

**Where**: `references/lore/species-the-planar.md` (entire-doc)

**Canon-twist not yet encoded**: Memory says canonical-Thinn canonical-embraced the canonical-Furling-translator-nickname as canonical-their canonical-own — canonical-this canonical-cultural-detail is canonical-NOT in the canonical-Planar-doc (canonical-pre-dates the canonical-twist).

**Action**: Either (a) rename doc to `species-the-thinn.md` + canonical-rewrite-content; (b) leave file in place but canonical-rewrite-content to canonical-Thinn-canon with canonical-margin-note canonical-explaining canonical-the canonical-name canonical-history. **Recommended: (a)**.

---

### HIGH-2 — `species-sheets.md` is canonical-stale by canonical-many-species

**Status**: Doc declares canonical-"the seven slice species" canonical-on canonical-line 7 and canonical-provides canonical-§1-§7 canonical-sheets for canonical-8 entities (Slylandro + Proto-Ur-Quan + Proto-Qor-Ah + Mycon + Arilou + Androsynth + Mmrnmhrm + Chenjesu) + canonical-Others. Canonical-the canonical-slice canonical-now canonical-has canonical-MANY canonical-more canonical-canonical-canonical-species canonical-with canonical-rich canonical-canon canonical-already-authored elsewhere — canonical-but canonical-NO canonical-§1-§7 canonical-sheet:

| Species | Canon-doc | Sheet? |
|---|---|---|
| Lemmkin | `species-the-lemmkin.md` | ❌ missing |
| Utwig | `utwig-quest.md` | ❌ missing |
| Taalo | `loop-closing-content-pass.md §6` | ❌ missing |
| Burvixese | `loop-closing-content-pass.md §7` | ❌ missing |
| Thinn (née Planar) | `species-the-planar.md` + `loop-closing-content-pass.md §8` | ❌ missing |
| Stelloth | `loop-closing-content-pass.md §1` | ❌ missing |
| Selvenne | `loop-closing-content-pass.md §2` | ❌ missing |
| Kovellim | `loop-closing-content-pass.md §3` | ❌ missing |
| Karavem | `loop-closing-content-pass.md §4` | ❌ missing |
| Mrokon | `loop-closing-content-pass.md §5` | ❌ missing |
| Melnorme | `loop-closing-content-pass.md §9` | ❌ missing |
| Dnyarri | `loop-closing-content-pass.md §10` | ❌ missing |
| Orz | `loop-closing-content-pass.md §11` | ❌ missing |
| 5 Furling factions | `factions-and-war.md` + sub-docs | ❌ no canonical-per-faction-sheet |

**Where**: `references/lore/species-sheets.md` line 7 (canonical-stale-heading) + canonical-missing-§-sections

**Action**: Either (a) author canonical-§1-§7 sheets for all canonical-13+ missing species (canonical-big undertaking but canonical-canon-coherence canonical-job); (b) canonical-update canonical-doc-purpose canonical-to canonical-"baseline slice species only" + canonical-add canonical-pointer-to canonical-canonical-loop-closing-content-pass.md as canonical-canonical-the canonical-extended-species canonical-canon-source. **Recommended: (b)** — canonical-the canonical-loop-closing-doc canonical-already canonical-IS canonical-the canonical-extended canonical-canon and canonical-re-authoring canonical-13 sheets in canonical-§1-§7 format canonical-duplicates canonical-work. Add canonical-redirect-headers in canonical-species-sheets.md.

---

### HIGH-3 — `species-content-backlog.md` finalized-picks table uses canonical-RENAMED-pre-revision names

**Status**: Lines 65-76 list canonical-"finalized" species-slots with canonical-OLD-names that have canonical-since-been-replaced:

| Backlog name (line 71-74) | Current canonical name | Resolved in |
|---|---|---|
| The Taalo (canonical *pacifist crystalline-amphibian pacifists*) | **Taalo** (canonical *Horta-lineage silicon mountain-range*) | `loop-closing-content-pass.md §6` |
| The Defiant | **Mrokon** | `loop-closing-content-pass.md §5` |
| The Curious | **Lemmkin** | `species-the-lemmkin.md` |
| The Burvixese | **Burvixese** (canonical-name-preserved) | `loop-closing-content-pass.md §7` |

Also lines 30-52 canonical-brainstorm-section is canonical-superseded-but-not-marked-as-such; canonical-Long-Memories → canonical-Kovellim, canonical-Bargainers → canonical-Selvenne renames canonical-not canonical-reflected.

**Where**: `references/lore/species-content-backlog.md` lines 29, 30-52, 65-76

**Action**: Add canonical-deprecation-banner at canonical-top + canonical-canonical-update-the-finalized-table with canonical-current-names + canonical-add canonical-rename-history-table.

---

## Severity MEDIUM (canonical-Lore-lane canonical-or canonical-Design-lane canonical-actionable; canonical-housekeeping)

### MED-1 — `ship-roster.md` canonical-TBD canonical-ship-stat-blocks for canonical-invented-species

**Status**: Per Explore-agent canonical-finding: canonical-Precursor + canonical-Homesteader canonical-rosters have canonical-rows `[INVENTED species ship — TBD]` (canonical-lines 17, 27). These map canonical-to canonical-Curious→Lemmkin + canonical-Defiant→Mrokon — canonical-now have canonical-rich-canon in canonical-canon-docs but canonical-canonical-ship-roster canonical-row canonical-still-canonical-blank.

**Where**: `references/lore/ship-roster.md` lines 17, 27

**Action**: Port canonical-Lemmkin + canonical-Mrokon canonical-ship-stat-blocks from canonical-loop-closing-content-pass.md to canonical-ship-roster.md.

---

### MED-2 — `species-precursor-era.md` doesn't include canonical-Taalo / canonical-Burvixese full-entries

**Status**: Per Explore-agent canonical-finding: canonical-doc canonical-covers Slylandro / Proto-Ur-Quan / Proto-Qor-Ah / Mycon / Arilou / Androsynth / Mmrnmhrm / Chenjesu canonical-with canonical-full canonical-precursor-era-entries; canonical-Taalo + canonical-Burvixese canonical-only-covered in canonical-furling-artifacts-and-callforwards.md. Canonical-precursor-era-doc canonical-incomplete.

**Where**: `references/lore/species-precursor-era.md`

**Action**: Author canonical-precursor-era-section entries for canonical-Taalo + canonical-Burvixese + canonical-Thinn + canonical-Lemmkin + canonical-Utwig + canonical-Stelloth/Selvenne/Kovellim/Karavem/Mrokon — canonical-OR canonical-add canonical-redirect-header canonical-pointing-to canonical-loop-closing-content-pass.md as canonical-extended-canon-source (same recommendation as canonical-HIGH-2).

---

### MED-3 — Memory-references canonical-`taalo-burvixese-planar.md` canonical-but canonical-no-such-file-exists

**Status**: MEMORY.md says canonical-`references/lore/species-the-taalo-burvixese-planar.md` exists as canonical-"three Homesteader-by-different-strategy alien species" canonical-canon-doc. Canonical-file canonical-doesn't-exist. Canonical-canon canonical-lives-distributed in canonical-loop-closing-content-pass.md §6-§8 and canonical-species-the-planar.md.

**Where**: nonexistent `references/lore/species-the-taalo-burvixese-planar.md`

**Action**: Either (a) author canonical-consolidated-doc to match canonical-memory-reference; (b) update canonical-MEMORY.md canonical-pointers to canonical-actual canonical-doc-locations (canonical-loop-closing-content-pass.md §6-§8). **Recommended: (b)** — canonical-loop-closing-content-pass.md already canonical-IS canonical-the canonical-source-of-truth.

---

## Severity LOW (canonical-housekeeping; canonical-non-blocking)

### LOW-1 — `species-content-backlog.md` canonical-brainstorm-section canonical-needs canonical-deprecation-note

**Status**: Lines 30-52 list canonical-brainstormed-species-options canonical-superseded by canonical-line 65-76 canonical-finalized-picks. canonical-No canonical-deprecation-marker.

**Action**: Add canonical-banner at canonical-line 29 — *"Brainstorm section below archived; active species slots canonical-finalized at §Initial Picks."*

---

### LOW-2 — `ship-roster.md` line 45-46 Others' Hijack canonical-TBD

**Status**: Canonical-Phase-2-deferred per `furling-tech-mechanics.md` canonical-canon. canonical-Marked-TBD canonical-correctly.

**Action**: None canonical-required. canonical-Confirm canonical-Phase-2-scope-tag when canonical-actually canonical-developed.

---

### LOW-3 — `notes.md` canonical-housekeeping-only

**Status**: Canonical-no canonical-open-TODOs canonical-found.

**Action**: None canonical-required.

---

## NOT canonical-stubs (canonical-Lore-lane canonical-confirmed canonical-canon-coherent)

For completeness, these were checked and are canonical-canon-coherent:

- ✅ `bio-archive-entries.md` — all canonical-20 baseline entries have canonical-long-form-prose (canonical-Index + 4 categories: 9 SPECIES + 6 ARTIFACTS + 1 COUNCIL + 4 OTHERS)
- ✅ `proto-species-bio-archive-entries.md` — all canonical-12 enriched entries canonical-have canonical-150-300-word canonical-prose (canonical-2026-05-18 + canonical-2026-05-19 canon-twists applied)
- ✅ `cinematic-narration.md` — 15 canonical-priority-passages canonical-fully canonical-authored
- ✅ `cutscene-sequences.md` — 16 canonical-cutscene-specs canonical-fully canonical-detailed (canonical-Phase-1 MVP canonical-text-on-screen format)
- ✅ `callbacks-and-callforwards.md` — 8 canonical-recurring phrases + canonical-3 canonical-fourth-wall-breaks canonical-fully canonical-authored
- ✅ `humor-pass.md` — 8 styles + 21 species humor profiles canonical-fully canonical-authored
- ✅ `halia-profile.md` — canonical-dual-register canon canonical-fully canonical-authored
- ✅ `crew-roster-redesign.md` — canonical-7-crew canonical-bridge canonical-fully canonical-canonized
- ✅ `cleansers-as-ice-branch.md` + `preservers-as-tree-branch.md` — canonical-three-pole canonical-Furling canonical-biology canonical-fully canonical-canonized
- ✅ `utwig-quest.md` — canonical-Veils-Falling canonical-doctrine + canonical-FSM canonical-fully canonical-authored
- ✅ `cross-species-awareness-and-progress-meter.md` — 69 awareness events + 51-point meter canonical-fully canonical-authored
- ✅ `the-endings.md` (per MEMORY) — 6-tier canonical-ending-system canonical-canonized
- ✅ `economy-and-trade-loops.md` (per MEMORY) — canonical-3-vendor-niches canonical-canonized
- ✅ `the-precursors-and-homesteaders.md` — canonical-central-faction-canon canonical-coherent
- ✅ `the-furlings-and-the-others.md` — canonical-central-narrative canonical-coherent
- ✅ `factions-and-war.md` — canonical-Persuader + Cleanser + Preserver canonical-coherent
- ✅ `the-androsynth-refugees.md` — canonical-Coel-Tessar + canonical-from-afar-theory canonical-coherent

---

## Cross-chat dispatches

### To Design (`HANDOFF_design_chat.md`)
- Confirms previously-dispatched `species_inventory.csv` stub-resolution batch (TALOS retire / CURIOUS→LEMMKIN / DEFIANT→MROKON / THE_DEFIANT_BACKLOG delete / THE_BARGAINERS→Selvenne / THE_LONG_MEMORIES→Kovellim / PLANAR→THINN) — canonical-still canonical-open canonical-on-Design-board.
- New canonical-finding: `ship-roster.md` lines 17, 27 canonical-TBD canonical-ship-stat-blocks canonical-now have canonical-canon-content available — port Lemmkin + Mrokon stat-blocks from `loop-closing-content-pass.md`.

### To Image (`HANDOFF_image_chat.md`)
- No new canonical-Image-actionable items from this audit. Canonical-existing canonical-image-dispatches canonical-cover canonical-the canonical-species canonical-with canonical-canonical-rich canonical-canon.

### To Audio (`HANDOFF_audio_chat.md`)
- No new canonical-Audio-actionable items from this audit.

### Lore-lane self-actions queued
1. **HIGH-1**: Rename `species-the-planar.md` → `species-the-thinn.md` + canonical-content-refresh to canonical-Thinn-canon (canonical-embraced-translator-nickname canon-twist)
2. **HIGH-2**: Add canonical-redirect-header to `species-sheets.md` + canonical-update canonical-line-7-heading to clarify canonical-baseline-slice-species-only scope
3. **HIGH-3**: Add canonical-rename-history-banner + canonical-update-finalized-picks-table in `species-content-backlog.md`
4. **MED-1**: Port canonical-Lemmkin + canonical-Mrokon canonical-ship-stat-blocks from canonical-loop-closing-content-pass.md to canonical-ship-roster.md
5. **MED-2**: Add canonical-redirect-header to `species-precursor-era.md` pointing to canonical-loop-closing-content-pass.md as canonical-extended-canon-source
6. **MED-3**: Update canonical-MEMORY.md canonical-`taalo-burvixese-planar.md` canonical-pointer to canonical-actual-doc-location
7. **LOW-1**: Add canonical-brainstorm-deprecation-banner to `species-content-backlog.md`

**Estimated Lore-lane work**: 3-4 hours for HIGH-1 (Thinn-doc canonical-rewrite); 30min each for HIGH-2/HIGH-3/MED-1/MED-2/MED-3/LOW-1.

---

## Audit methodology

- Ran `tools/audit_placeholders.py` — canonical-asset-only (Image-lane); canonical-no canonical-lore-stub-detection
- Grepped `references/lore/*.md` for: `TODO_LORE|TODO_AVATAR|TODO_DESIGN|TODO_AUDIO|TODO_IMAGE|TODO_TEST|STUB|PLACEHOLDER|TBD|FIXME|XXX|WIP|placeholder|stub-only|TBC|to-be-written` (case-insensitive)
- Checked canonical-renamed-species canonical-stale-references: PLANAR, Zoq-Fot-Pik, THE_BARGAINERS, THE_LONG_MEMORIES, THE_CURIOUS, ^DEFIANT, ^CURIOUS, TALOS_SUBFACTION
- Verified canonical-source-of-truth-doc existence for canonical-Thinn (canonical-fail) + canonical-Taalo-Burvixese-Planar (canonical-fail)
- Dispatched Explore-agent for cross-doc consistency audit (canonical-confirmed canonical-HIGH-1 + canonical-HIGH-2 + canonical-MED-1 + canonical-MED-2 findings)
- Read canonical-suspect-docs canonical-directly: species-content-backlog.md, species-sheets.md headings, bio-archive-entries.md headings, loop-closing-content-pass.md headings, species-the-planar.md
