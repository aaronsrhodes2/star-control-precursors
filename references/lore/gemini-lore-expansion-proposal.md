# Gemini Free Tier — Lore Expansion Proposal

> Aaron dispatch (2026-05-18): *"Use GEMINI_FREE_API_KEY in the .env for text generation. If there is a way to use Gemini free tier to help us out with expanding our lore, that would be great. Thoughts?"*
>
> Strategic recommendation, prioritized use cases, canonical prompt templates, workflow proposal, risks & mitigations, and quick-wins for tonight. Lore-chat opinion on how Gemini Free tier can multiply our lore-volume without diluting canonical-voice.

---

## 1. Strategic recommendation — yes, with constraints

**TL;DR**: Yes, use Gemini Free for lore expansion — but as a **draft-generator that Lore reviews**, not as a **canon-author**. Free tier is well-suited for **high-volume, low-stakes lore content** (combat banter pools; awareness event backups; Bio-Archive entry expansions). It is **NOT well-suited for canonical-doctrine-sensitive content** (4th-wall breaks; Disastrous-ending narrator; Halia's canonical-key-passages; Mh-Lai Fall last transmission). Those remain hand-authored.

The slice now has ~42 lore docs + ~50k lines of canon + canonical-voice-registers for 23 species/factions + canonical-humor-doctrine + canonical-callback-economy + canonical-no-Earth-religion-terms for the Utwig + canonical-3-fourth-wall-break-scarcity. **The canonical-prompt-templates can encode all of this into Gemini's context.** With careful prompt engineering, Gemini Flash output will hit canonical-voice ~70-85% of the time; Lore reviews the rest.

Net effect: **10x lore-volume-per-Lore-hour** for the high-volume tasks. Quality stays canonical-Lore-controlled.

---

## 2. Existing tooling state

The project already has Gemini-Flash integration scaffolding:

- **`tools/gen_lore_gemini.py`** — canonical script with Anthropic fallback; reads `GEMINI_API_KEY`; supports canonical *species_description* + *voice_profile* + *quest_dialog* prompt templates
- **`tools/gemini_drafts/`** — output directory with existing canonical drafts (canonical *ship_melnorme_trader.json*, *species_mmrnmhrm.json*, *species_mycon_biot.json*)

**Env vars available**:
- `GEMINI_API_KEY` (canonical-existing, used by current script)
- `GEMINI_FREE_API_KEY` (canonical-Aaron-just-mentioned)

**Canonical Design-dispatch needed**: the existing script reads `GEMINI_API_KEY`; canonical-Aaron specified `GEMINI_FREE_API_KEY`. Recommend: Design canonical-updates the script to prefer `GEMINI_FREE_API_KEY` for Lore-batch tasks while preserving `GEMINI_API_KEY` for canonical-higher-stakes generation. Or treat as canonical aliases. (Aaron's call; flagged in §8 dispatch.)

---

## 3. Prioritized use cases — effort vs. value analysis

Ranked by canonical *value-per-Lore-review-hour*. Highest ROI first.

### Tier 1 — High volume × Low canonical risk (recommended immediate)

| Use case | Volume | Canonical risk | Notes |
|---|---|---|---|
| **Combat banter pool expansion** | High (~70 base × 5x = ~350 lines) | Low | Banter is canonical-flavor; canonical-voice-register-driven; Gemini handles per-species register well |
| **Awareness event backup pool** | Medium (~70 base + canonical-3-per-species-already-authored; could expand to canonical-5-per-species backup) | Low | Awareness events follow canonical-pattern; canonical-canonical-flag-trigger + canonical-greeting-prefix-line |
| **Bio-Archive entry expansion** | Medium (~26 existing + canonical-room-for-more-canonical-detail) | Low | Steward-voice canon; canonical existing template; canonical Bio-Archive Entry 14,4XX format |
| **Common Room ambient banter** | High (canonical-existing-canon could expand with canonical-50+ more idle moments) | Low | Crew register canonical-stable; canonical-cross-crew dynamics canonical-canonical |

### Tier 2 — Medium volume × Medium canonical risk

| Use case | Volume | Canonical risk | Notes |
|---|---|---|---|
| **Quest dialog branch expansion** | Medium (each canonical-quest could grow 2-3 optional canonical-side-branches) | Medium | Risk: branches may invent canonical-conflicts with existing canon; canonical-Lore-review-mandatory |
| **NPC name generation for [PLACEHOLDER]** | Low (canonical ~5-10 placeholders flagged) | Medium | Risk: canonical-naming-conventions must canonical-be-encoded carefully per-species |
| **Lemmkin canonical *Things We Have Tried* archive entries** | High (canonical-104k entries; canonical-could-author canonical-50-100 highlights) | Low-Medium | Canonical-Lemmkin-cheerful-recklessness register canonical-easy-to-encode; canonical-comedic-content easy-to-batch |
| **Furling Humor Archive entries** | Medium (canonical-7,400 entries; canonical-could-author canonical-30-50 highlights) | Low | Canonical-Furling-humor-doctrine canonical-encodable |

### Tier 3 — Low volume × High canonical risk (NOT recommended for Gemini)

| Use case | Why hand-authored only |
|---|---|
| **The 3 canonical 4th-wall breaks** | Canonical scarcity-is-the-canon; canonical-fixed dialog passages; Gemini risks generating *more* breaks |
| **Halia's canonical key passages** | Canonical-priority-production-passages; canonical-emotional-weight; Lore hand-authors |
| **Mh-Lai Fall last transmission** | Canonical *"I love you, Steward..."* is canonical; Gemini would generate variants that dilute the canonical-original |
| **Coel Tessar's *from-afar* theory articulation** | Canonical-most-vulnerable-Coel moment; canonical-priority-production; hand-authored |
| **Cleanser-supervised Halia whisper** | Canonical *"I'm sorry, Steward"*; the slice's most painful single line; hand-authored |
| **Disastrous ending narrator + *We told you the Others were never funny*** | Canonical-priority-production; canonical-Furling-humor-doctrine canonical-final-word |
| **Sevra's Andromeda 4th-wall-break-#2** | Canonical-fixed dialog; canonical-priority-production |
| **Vael-Souren mourning lines** | Canonical-priority-production per `cross-species-awareness-and-progress-meter.md` |

The canonical-rule: **if it's canonical-priority-production for Audio, it should be hand-authored**. Gemini is for **canonical-flavor-volume**, not canonical-emotional-peaks.

---

## 4. Canonical prompt templates — for Tier 1 use cases

These are Lore-authored canonical-prompt-templates that encode the canonical-canon-context into Gemini's prompt. Design wires them into `gen_lore_gemini.py` (or successor script). The canonical-Gemini-output is canonical-draft-only; canonical-Lore-reviews + canonical-edits + canonical-files-to-`gemini_drafts/`.

### 4.1 Combat banter pool expansion

```yaml
template_id: combat_banter_expansion
canonical_inputs:
  - species_name (e.g. "Lemmkin")
  - canonical_voice_register (e.g. "no fear, only curiosity; cheerful through every damage bracket")
  - canonical_existing_lines (3-5 from existing canon, as anchors)
  - damage_bracket ("opening" / "75%" / "50%" / "25%" / "5%")
  - quantity_requested (default: 5)

prompt:
  You are extending the canonical combat banter pool for {species_name} in
  the Star Control Zero (SCZ) vertical slice. The canonical voice register
  for this species is:

  {canonical_voice_register}

  Canonical existing lines (as voice anchors — match this tone, do not
  duplicate):
  {canonical_existing_lines}

  Generate {quantity_requested} NEW canonical-banter lines for the {damage_bracket}
  damage bracket. Each line should:
  - Match the canonical voice register exactly
  - Be 1-3 sentences
  - NOT reference Earth religions, idioms, or cultural references
  - NOT break the 4th wall (those are canonical-reserved scarce)
  - NOT introduce species-canon-conflicts (no new lore facts; only voice/flavor)
  - Treat the Furling Steward as the canonical-opponent
  - Vary in tone and content — avoid canonical-repetition

  Output as a JSON array of strings. No preamble, no markdown.
```

### 4.2 Awareness event backup pool

```yaml
template_id: awareness_event_backup
canonical_inputs:
  - species_name
  - canonical_voice_register
  - canonical_awareness_channel (e.g. "Furling Council relay; broadcaster network")
  - canonical_existing_3_events (the canonical-Aaron-canon-3)
  - new_event_trigger_flag (e.g. "flag:karavem_song_received_by_other_species")
  - canonical_event_description (1 sentence: what happened in the galaxy)

prompt:
  You are authoring a canonical awareness-event greeting-prefix for
  {species_name} in the Star Control Zero (SCZ) vertical slice. The
  canonical voice register for this species is:

  {canonical_voice_register}

  Canonical awareness channel (how they would have heard about distant
  events):
  {canonical_awareness_channel}

  Canonical existing awareness events (as voice anchors — match the tone):
  {canonical_existing_3_events}

  NEW event the species has learned about: {canonical_event_description}.
  This event is triggered by the flag: {new_event_trigger_flag}.

  Generate ONE canonical awareness greeting-prefix line that:
  - The species delivers when the Steward visits AFTER the flag is set
  - References the event in the species' canonical voice
  - Is 1-3 sentences (brief; not quest-blocking)
  - Does NOT introduce species-canon-conflicts
  - Does NOT reference Earth religions
  - Does NOT break the 4th wall
  - Acknowledges the Steward's role (if the Steward triggered the event)
  - Maintains canonical voice register without exception

  Output the line ONLY as plain text. No JSON, no preamble, no quotes,
  no markdown.
```

### 4.3 Bio-Archive entry expansion

```yaml
template_id: bio_archive_entry
canonical_inputs:
  - subject (e.g. "the Karavem Resonance Module")
  - canonical_category ("species" / "artifact" / "council" / "others")
  - canonical_flag_gating (e.g. "has_karavem_resonance_module")
  - canonical_steward_voice_register (Furling Steward; canonical observation register)
  - canonical_existing_entry_examples (1-2 from bio-archive-entries.md)
  - canonical_entry_number (e.g. 14,485)

prompt:
  You are authoring a canonical Bio-Archive entry for the Star Control
  Zero (SCZ) vertical slice. The Bio-Archive is the Steward's in-game
  observation log; canonical voice is the Furling Steward's
  observation register — quiet, factual, occasionally warm or wry.

  Canonical existing entries (as voice anchors):
  {canonical_existing_entry_examples}

  Subject: {subject}
  Category: {canonical_category}
  Flag-gating: {canonical_flag_gating}
  Entry number: {canonical_entry_number}

  Generate the entry. Format:

    Bio-Archive Entry {canonical_entry_number}. Subject: <one-line subject>.

    <100-250 words of canonical-Steward-voice observation. Reference
    canonical-existing-canon where appropriate. Maintain Steward's
    observation register. SC2-references canonically backdated 250kya.>

  Constraints:
  - Steward voice (first person, observational, occasionally wry)
  - No Earth-religion vocabulary
  - No 4th-wall breaks
  - No invention of species-canon-facts beyond the subject's existing canon
  - Italic-blockquoted style implied (single-paragraph; the rendering layer
    handles italics)

  Output the entry as plain text. No preamble.
```

### 4.4 Common Room ambient banter

```yaml
template_id: common_room_ambient
canonical_inputs:
  - scene_context (e.g. "post-Fall, 3 days after Halia's death-branch")
  - canonical_crew_present (list of crew with canonical voice registers)
  - canonical_recent_event (1 sentence: what just happened in slice)
  - canonical_recurring_phrases (from callback economy: *"Drink the tea"*, *"by my standards"*, etc.)
  - quantity_requested (default: 3 beats)

prompt:
  You are authoring canonical Common Room ambient banter for the Star
  Control Zero (SCZ) vertical slice. The Common Room is the canonical
  ship's social hub; canonical 7 crew members + Forty-Seven AI.

  Scene context: {scene_context}
  Crew present: {canonical_crew_present}
  Recent slice event: {canonical_recent_event}
  Canonical recurring phrases (use sparingly; canonical-callback economy):
  {canonical_recurring_phrases}

  Canonical crew voice registers:
  - Mraka (Furling Compeller, Pilot; fast, sharp, Drifter-pragmatic, "tools alphabetized" running joke)
  - Tarven (Furling Persuader, Navigator; measured, archive-keeper-precise, dry)
  - Forward (Thinn, Weapons Officer; perpendicular-geometry, sincere-not-funny)
  - Renn Halvor (Androsynth, Engineer; late-22nd-century slang slips, survivor's guilt)
  - Vresh (Taalo in silicon tank, Medic; "we-all" plural, hum-pattern emotional valence)
  - Sevra (Utwig atheist; bare-faced, future-tense reclaimed, unguarded curiosity)
  - Forty-Seven (Ship AI; factual-observation deadpan, "by my standards", distributed-presence)

  Generate {quantity_requested} canonical Common Room banter beats. Each
  beat:
  - Is 3-5 exchanges between 2-4 crew members
  - Matches each crew member's voice register exactly
  - References the scene context
  - May use canonical recurring phrases sparingly
  - Does NOT break the 4th wall
  - Does NOT introduce species-canon-conflicts
  - Maintains canonical Furling-humor-doctrine (Furling Steward great; aliens
    not directly funny; canonical Others NEVER funny)

  Output as JSON: [{ "beat_id": "...", "exchanges": [{ "speaker": "...",
  "line": "..." }] }]. No preamble.
```

### 4.5 Lemmkin *Things We Have Tried That Did Not Work* archive entries

```yaml
template_id: lemmkin_archive_entry
canonical_inputs:
  - quantity_requested (default: 10)

prompt:
  You are authoring canonical entries for the Lemmkin "Things We Have
  Tried That Did Not Work" archive — a canonical 104,000-entry public
  Lemmkin cultural treasure of canonical engineering disasters
  cheerfully archived.

  Canonical Lemmkin voice: no fear only curiosity; cheerful through any
  outcome including their own demise; canonical anthropomorphic-squirrel
  energy; canonical breeding-fast-to-replace-losses; canonical "we will
  try again with mittens" register.

  Canonical existing sample entries:
  - "Eating the comet that was on fire (singed all four of us; would do
    again with mittens)"
  - "Politely informing the Cleanser that they were holding the
    spore-canister upside-down (the Cleanser was patient; the Lemmkin was
    incinerated; the Lemmkin's last words were 'Thank you for the
    lesson')"

  Generate {quantity_requested} NEW canonical archive entries. Each
  entry:
  - 1-2 sentences
  - Canonical Lemmkin cheerful-recklessness voice
  - Describes a canonical engineering experiment / investigation / decision
    that went canonically wrong
  - Often ends with canonical resolution-or-lesson-learned despite the
    canonical-disaster
  - Treats the canonical-investigator's-fate cheerfully
  - May reference canonical other species / canonical-slice-events from a
    Lemmkin perspective (canonical curiosity-not-fear)
  - No Earth-religion references
  - Variety of canonical engineering domains (explosives, sensors, propulsion,
    biology, kitchen appliances, civics)

  Output as JSON array of strings. No preamble.
```

### 4.6 Furling Humor Archive entries (canonical jokes by/about species)

```yaml
template_id: furling_humor_archive
canonical_inputs:
  - subject_species (e.g. "Slylandro")
  - subject_species_register (e.g. "over-share comedy; weather-name absurdity")
  - quantity_requested (default: 5)

prompt:
  You are authoring canonical entries for the Furling Humor Archive — a
  canonical 7,400-entry archive of Furling jokes about other species.
  Canonical: these are jokes Furlings tell each other about the subject
  species. They mostly DO NOT LAND with the subject species (canonical:
  Furling humor doesn't always translate). The canonical comedy is the
  Steward attempting one and watching it fall flat.

  Subject species: {subject_species}
  Subject species voice register: {subject_species_register}

  Canonical sample entries:
  - Archive entry 4,182: "Why did the Slylandro cross the troposphere?
    To get to the — they have not yet decided why. They will tell us
    when they have. The joke is the waiting."
  - Archive entry 7,389: "Why is the Utwig High Veil still thinking? —
    Because the doctrine canonically forbids it, and he has agreed to
    disobey only the parts of the doctrine that concern him."

  Generate {quantity_requested} canonical Furling Humor Archive entries
  about {subject_species}. Each:
  - 1-3 sentences
  - Canonical Furling-told-among-Furlings register (NOT the subject species'
    register)
  - References the subject species' canonical traits humorously but never
    cruelly (canonical-humor-doctrine: gentle-mocking never cruel)
  - Canonical-Earth-humor-categories permitted but no Earth-religion references
  - Most entries should "not land" with the subject species — canonical
    cultural-friction is the canon
  - Format: "Archive entry <NNN>: <joke text>"

  Output as JSON array of strings. No preamble.
```

### 4.7 Quest dialog optional branch expansion

```yaml
template_id: quest_dialog_branch
canonical_inputs:
  - quest_id (e.g. "stelloth_artifact_trade")
  - canonical_species_voice_register
  - canonical_existing_FSM_states (the canonical-existing canon dialog states)
  - branch_position (e.g. "between about_trade and trade_complete")
  - branch_purpose (e.g. "Steward expresses doubt about the trade value")

prompt:
  You are authoring an OPTIONAL canonical dialog branch for the SCZ
  quest "{quest_id}". The branch is added at position
  {branch_position} and serves purpose: {branch_purpose}.

  Canonical existing FSM states (as voice + canon anchors):
  {canonical_existing_FSM_states}

  Canonical species voice register: {canonical_species_voice_register}

  Generate the new branch. Format:

    state_name:
      npc_speaker: <character>
      npc_text: |
        <2-4 sentences in canonical species voice>
      choices:
        - text: "<player option 1>"
          next: <existing-state-or-new-state>
          category: <ASK_LORE | NEGOTIATE | AGREE | REFUSE | BACK | FAREWELL>
        - text: "<player option 2>"
          next: ...

  Constraints:
  - Must integrate with existing FSM states (use canonical-existing state-names
    in `next:` references)
  - Must NOT introduce new species-canon-facts
  - Must NOT introduce new modules/rewards (the existing FSM controls those)
  - Must match canonical voice register exactly
  - Must NOT break the 4th wall
  - 2-4 choices per state

  Output the new branch state(s) only. No preamble, no markdown wrapper.
```

---

## 5. Workflow proposal

### 5.1 The canonical pipeline

```
1. Lore authors canonical-prompt-template (this doc §4)
   ↓
2. Design wires the template into gen_lore_gemini.py
   ↓
3. Lore (or Aaron) runs the script with canonical-inputs per use case
   ↓
4. Gemini Flash generates draft → saved to tools/gemini_drafts/<canonical-name>.json
   ↓
5. Lore reviews the draft:
   - Voice register canonical-accurate? ✓
   - Canonical-doctrine respected? ✓ (no Earth religions; no 4th-wall breaks; etc.)
   - Canonical-fact-consistent? ✓
   - Edits as needed
   ↓
6. Lore-approved drafts ported into canonical-source-docs (references/lore/*.md)
   OR canonical-spreadsheet rows (tools/build_quest_inventory.py / etc.)
   ↓
7. Design ports to runtime content (src/scz/dialog/characters.py / etc.)
```

### 5.2 The canonical Lore review checklist

For every Gemini-generated draft, Lore canonical-verifies:

- [ ] Canonical voice register matches the species/character
- [ ] No Earth-religion vocabulary (especially for Utwig: no *heresy*, *holy*, *Father*, *Brother*, *Sister*)
- [ ] No 4th-wall breaks (the canonical 3 are canonical-fixed)
- [ ] No species-canon-fact-conflicts (no new traits, no new history-facts)
- [ ] No canonical-callback-phrase mis-attributions (canonical *"Drink the tea"* is Halia's; migrates only per canonical-doc-canon)
- [ ] Canonical-humor-doctrine respected (Furling Steward funny; aliens via cultural-friction; Others NEVER funny)
- [ ] No invention of new NPCs (use only canonical-existing NPCs)
- [ ] No SC2-canon-violations (canonical SC2 species fates respected)

### 5.3 Canonical-batching strategy

Per Gemini Free tier limits (canonical ~20 RPD on Flash per existing script's note; canonical Aaron's `GEMINI_FREE_API_KEY` may have separate quota):
- **Batch by use case** — generate canonical-50-banter-lines in one session, not canonical-1-at-a-time
- **Save all drafts to `gemini_drafts/`** — easy review; easy regeneration if needed
- **Generate during slow Lore-hours** — Gemini processing while Lore reviews previous batch
- **Plan canonical-7-day-rolling-batches** — spread quota across canonical-week

---

## 6. Risks & mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| **Voice register drift** (Gemini outputs sound off-canon) | High | Anchor lines in every prompt; canonical Lore review mandatory; reject + regenerate if off |
| **Canonical-fact invention** (Gemini adds new species traits/history) | Medium | Strict canonical-no-new-facts constraint in prompt; Lore reviews for canon-conflicts |
| **Earth-religion vocabulary slips** (especially in Utwig content) | Medium | Explicit canonical-no-Earth-religion constraint; canonical Utwig glossary referenced; Lore reviews carefully |
| **4th-wall break inflation** (Gemini generates more breaks) | Low-Medium | Explicit canonical-no-4th-wall constraint; canonical-3-canonical-breaks documented in prompt |
| **Free-tier quota exhaustion** | Medium | Existing script has Anthropic fallback; batch strategically; canonical 7-day rolling batches |
| **Generated content feels canonical-AI-generic** (lacks canonical-character) | Medium | Robust voice anchors in every prompt; canonical-Lore-edits-add-character; canonical-prompt-iteration over multiple sessions |
| **Cleanser/Other content gets accidentally funny** (humor-doctrine violation) | Low | Explicit constraint; Lore review enforces |
| **Pricing surprise** (free tier quota lower than expected) | Low | Existing script has fallback; Aaron can canonical-budget paid-tier for canonical-key-passages if free tier exhausted |

---

## 7. Quick wins doable tonight

If approved, the canonical fastest-volume-multiplier work for tonight (Lore can author the canonical-prompts; Design wires; Lore reviews):

1. **Author canonical 5 banter lines per species per damage bracket** for the 11 species in `loop-closing-content-pass.md` — currently 2-3 lines per bracket; expand to 5. Net: ~110 new banter lines (~22 currently × 5).
2. **Author canonical 2 additional awareness events per species** for the 23 species in `cross-species-awareness-and-progress-meter.md` — currently canonical-3 per Aaron canon (canonical hard-cap); but a canonical-backup pool of canonical-2-extra-events per species (canonical-not-Aaron-canon; canonical-Design-can-substitute if specific events feel off) gives canonical-resilience. Net: ~46 backup events.
3. **Author canonical 5 Lemmkin archive entries** — pure canonical-cheerful-disaster comedy; canonical *Things We Have Tried* pool. Net: 5 entries (canonical-many-more easily generated in follow-up batches).
4. **Author canonical 3 Common Room post-Fall ambient beats** — canonical-quieter-post-Fall variant; canonical-3-3-day-pause + canonical-3-week-later quieter-resumption + canonical-month-later return-to-near-baseline. Net: 3 beats.

**Total tonight-yield (if executed)**: ~165 new canonical-content-items + canonical-prompt-templates documented for future runs.

**Tonight workflow if Aaron approves**:
- Lore (this chat) finalizes prompt templates (canonical-already-authored in §4)
- Dispatches to Design to wire `gen_lore_gemini.py` for `GEMINI_FREE_API_KEY` + new templates
- Design runs canonical-quick-batches with the templates
- Outputs saved to `tools/gemini_drafts/`
- Lore-chat in NEXT session reviews + ports to canonical-source-docs
- Loop continues across canonical-7-day-window

**Tonight workflow if Aaron wants Lore-only-no-code**:
- Lore (this chat) hand-authors a canonical-sample-batch — canonical-5-Lemmkin-archive-entries + canonical-3-Common-Room-post-Fall-beats — as canonical *proof-of-concept what Gemini would generate*. Aaron can canonical-compare quality + canonical-decide whether to wire Gemini for canonical-batch-production.

---

## 8. Cross-chat dispatches

### To Design (`HANDOFF_design_chat.md`)

**Net new work**:
- **Update `gen_lore_gemini.py`** to prefer `GEMINI_FREE_API_KEY` over `GEMINI_API_KEY` for Lore-batch tasks (canonical: Aaron specified `GEMINI_FREE_API_KEY`). Recommend env-var-precedence: prefer `GEMINI_FREE_API_KEY`; fallback to `GEMINI_API_KEY`; fallback to Anthropic.
- **Wire 7 new canonical-prompt-templates** into the script per `§4`: combat_banter_expansion / awareness_event_backup / bio_archive_entry / common_room_ambient / lemmkin_archive_entry / furling_humor_archive / quest_dialog_branch
- Each template canonical-takes canonical-inputs; canonical-output to `tools/gemini_drafts/<canonical-name>.json`
- Recommend a canonical *batch-runner* sub-script that takes a canonical-CSV of (template_id + inputs) and runs all in sequence with canonical-rate-limit-respecting delays
- **No canonical-direct-integration with runtime** — outputs are canonical-drafts; canonical-Lore-reviews-and-ports manually to source-docs

### To Image (`HANDOFF_image_chat.md`)
- No work required by this dispatch (canonical text-generation only)

### To Audio (`HANDOFF_audio_chat.md`)
- No work required immediately
- **Future**: as Gemini-generated banter lines flow through Lore-review into canonical-spreadsheets, Audio will pick them up via the canonical-existing-banter-line-recording pipeline. No special handling needed.

### To Testing (canonical-implicit)
- After Gemini-generated content lands in canonical-source-docs, Testing canonical-walks-cover-the-new-content via canonical-baseline walks (no new walk-types needed)

---

## 9. Open Aaron-calls

- **Approval to proceed with the canonical pipeline?** Yes/No.
- **Tonight's first batch — which use cases?** Recommend: combat banter expansion + Lemmkin archive entries (canonical-highest-value-per-hour).
- **Quota budgeting**: should canonical-Lore burn canonical-free-tier-quota aggressively tonight, or canonical-stagger across canonical-week?
- **Canonical-prompt-template ownership**: do canonical-prompts live in this doc (Lore canonical-canon) or in the script (Design canonical-code)? Recommend: canonical-templates documented in this doc (canonical-Lore-source-of-truth); canonical-script-versions canonical-import-from-here.
- **Canonical-Anthropic-fallback**: existing script has fallback to Anthropic when Gemini quota exhausted. Aaron may want to canonical-keep this canonical-fallback or canonical-disable it (canonical-disabling-it forces canonical-quota-discipline; canonical-keeping-it preserves canonical-availability).

---

## Cross-references

- `tools/gen_lore_gemini.py` — canonical-existing Gemini-Flash script with Anthropic fallback
- `tools/gemini_drafts/` — canonical-existing drafts directory
- [`loop-closing-content-pass.md`](loop-closing-content-pass.md) — canonical 11-species canon; canonical-Gemini-could-expand combat banter + Bio-Archive entries
- [`cross-species-awareness-and-progress-meter.md`](cross-species-awareness-and-progress-meter.md) — canonical 69 awareness events; canonical-Gemini-could-author canonical-backup-pool
- [`humor-pass.md`](humor-pass.md) — canonical 8-style humor canon; canonical-Gemini-encodes via canonical-voice-registers
- [`callbacks-and-callforwards.md`](callbacks-and-callforwards.md) — canonical 4th-wall-break scarcity canon; canonical Gemini-must-respect-the-3-canon
- [`halia-profile.md`](halia-profile.md) — canonical Halia canonical-key-passages canonical-NOT-Gemini-eligible (hand-authored)
- [`utwig-quest.md`](utwig-quest.md) — canonical Utwig glossary (no Earth religion); canonical Gemini-prompts must canonical-embed this constraint
