## Star Control Zero — Project Rules (golden mandates)

> Project-specific rules that override everything else when they apply. These are commitments the project has made about itself. They're short and absolute on purpose. When in doubt, read these first.

## Rule 1 — We must improve every asset we stole from SC2

The project ships UQM graphical assets as MVP placeholders so the game has visual coverage while we build it. **Every placeholder is a debt.** Before slice 1.0 release, every entry in `assets/_PLACEHOLDERS.json` with `status == "placeholder"` must be either:

- **Improved** — the original asset enhanced (upscaled, re-colored, animated, AI-touched-up) so the result is meaningfully ours, OR
- **Replaced** — wholly new asset authored or generated for this project, OR
- **Removed** — feature dropped, asset deleted

Updates to the manifest happen *at the same commit* as the asset change. Set `status` to `"improved"` or `"replaced"`, fill `replaced_at` (ISO date) and `improved_with` (short note: "Flask-SD enhance", "hand-painted", "wholly new", etc.).

**Why this rule exists**: UQM is freely-redistributable open-source content under GPL-compatible terms — using it as a placeholder is fine and within the spirit of the OSS lineage. But shipping the slice with vanilla UQM art would mean we never made our own thing. The placeholders are scaffolding; the rule is the commitment to take the scaffolding down.

**How to apply**:
- Audit progress: `.venv/Scripts/python.exe tools/audit_placeholders.py` — prints status counts per category
- Re-run extraction: `.venv/Scripts/python.exe tools/extract_uqm_graphical_assets.py` — safe to re-run; preserves prior status entries
- When committing an improved asset, edit `assets/_PLACEHOLDERS.json` in the same commit
- Do NOT ship a public release while the placeholder count is non-zero

**Tracked categories** (initial extraction, 2026-05): `ships` (4,190 files), `fonts` (2,606), `comm` (1,517), `ui` (439), `lander` (380), `nav` (303), `cutscene` (271), `planets` (171). **Total: 9,877 placeholders.**

The number only goes down. Each improvement gets credited to a real human and dated.

## Rule 2 — Engine before variation, always

Per [variation-architecture.md](lore/variation-architecture.md) and Aaron's design-canon decisions: the static deterministic engine must work end-to-end before any LLM, personality vector, music stem, or visual variation layer touches the code. Variation is a cosmetic layer over a static engine, not woven through gameplay. Build the boring engine first.

This rule exists because we discovered (via Aaron's pivots through the early prototype) that LLM-anticipation code tends to get the design and constraints wrong. Authoring decisions need the static engine to show us where variation actually matters.

## Rule 3 — Tests as repeatable scripts

Every significant gameplay change ships with a test script in `src/scz/testing/scripts.py`. The harness drives the game from MainMenu through whatever the change touches, and asserts the outcome. Aaron watches the live run to confirm visual correctness; the harness covers regression.

This is non-negotiable for combat, hazards, dialog FSMs, the upgrade loop, scene transitions, and any new mechanic with player-visible state. See the existing 14 walk_* scripts for the pattern.

## Rule 4 — SC2 keep/change disposition

The project takes the SC2 source as inspiration and starting material. For each category, the project has a clear disposition: **keep** (mimic the SC2 thing literally), **keep-and-improve** (lift SC2 as a starting point, evolve it), or **change** (the SC2 version is the placeholder; ours will diverge meaningfully).

### KEEP (mimicked literally)

| Item | Source | How |
|---|---|---|
| Hyperspace map backdrop | `assets/maps/sc2-starmap.png` (lifted from `references/maps/`) | Blit as the HyperspaceScene backdrop, scaled to the viewport. Procedural starfield becomes a faint parallax overlay |
| Quasi-Space map backdrop | `assets/maps/quasispace.png` | Same pattern in QuasiSpaceScene |
| UI palette + layout vocabulary | SC2 screenshots + the 600+ frames in `assets/ui/` | Adopt SC2's bright cyan/magenta/yellow-cream on black with characteristic chunky 1-2px borders and shadow-recessed panels. See Phase 3 of the keep/change increment in the plan file |
| Combat feel | `MeleeCombatScene` already wraps; pending features: asteroids, central gravity-well planet (slingshot), 2-controller couch co-op |
| Lore continuity | The narrative bible in `references/lore/*.md` already canonical |

### KEEP-AND-IMPROVE (placeholder → ours, eventually)

Per Rule 1. Tracked in `assets/_PLACEHOLDERS.json`. Currently includes all extracted UQM sprites (ships, comm, lander, cutscene, fonts, nav, planets, ui). Each gets improved or replaced before 1.0.

### CHANGE (will diverge meaningfully)

| Item | Why it changes |
|---|---|
| Music | AI-mutate the UQM tracks as a base; output is not a re-encode but a new arrangement keyed off the originals |
| SFX | Modern treatment — punchier, richer, less 1992 |
| UI sounds | Slight modernization, more pleasant |
| Alien art | Devolve case-by-case (we're 250kya before SC2 — species are typically less evolved; some don't exist yet) |
| Ship art | Less-advanced versions case-by-case (250kya tech regression) |
| Planet visuals | Make them gorgeous; full-resolution, animated, atmosphere effects |
| Planet rotation match | System view (`sml`) and orbit (`big`) must animate from the same .ani frame sequence so a future zoom transition feels continuous |
| Ship crew model | NOT crew-as-HP. Crew are NPC characters installed in module slots (already implemented) and individually talkable. Hull damage is the combat HP |
| Ship upgrade UI | Module bays arranged around the ring nacelle in a top-down ship icon, not a two-column grid |

### Rule 4a — Call-forward respect

When the narrative refers to something SC2 referenced (an artifact, an alien species, a famous planet), the imagery should respect SC2's depiction where one exists. The Furling-era version is typically a *regression* (alien less evolved, artifact under construction, planet pre-apocalypse), but the SC2 form is the silhouette the player will recognize.

**How to apply**: when authoring a new alien/artifact/planet that has an SC2 counterpart:
1. Look up the SC2 version (asset path under `assets/comm/`, `assets/ships/`, `assets/planets/`, `references/uqm-source/sc2/content/base/`)
2. Use it as the starting visual reference
3. Apply a deliberate regression delta (per the species/artifact's lore)
4. Note the SC2 source + the regression rationale in the commit message and the canon doc that introduces it
