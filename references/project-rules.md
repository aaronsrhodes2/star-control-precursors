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
