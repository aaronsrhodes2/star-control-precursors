# HANDOFF — anyone → SCZ: Game Lore Chat

> Cross-chat dispatch queue for **lore + canon work** in Star Control Zero. The Game Lore chat reads this file at session start, picks up open entries, authors/refines canon in `references/lore/*.md`, updates the species spreadsheet where relevant, and marks each `✅ PROCESSED <date>` (or removes it) when done. Newest entries at the top.
>
> Other chats append new entries when their work surfaces a canon question, a lore gap, or a doctrine that needs to be made explicit.
>
> **Lore lane scope**: `references/lore/*.md`, the species spreadsheet (`tools/build_species_inventory.py` + `tools/species_inventory.csv`), `memory/*.md` documenting lore canon, narrow code-edit exception on `name` / `description` / `locked` fields for TODO_LORE-marked stub modules.
>
> **Lane discipline reminder**: Lore chat does NOT write game code (Design's lane), image assets / Firefly prompts (Image's lane), audio / VO (Audio's lane), or walk-tests (Testing's lane). When Lore canon affects those areas, the dispatch goes the OTHER way — Lore writes to `HANDOFF_image_chat.md` / `HANDOFF_audio_chat.md` / `HANDOFF_design_chat.md` / `HANDOFF_testing_chat.md` to broadcast the implication.

---

## When to dispatch to Lore (examples)

Other chats should append entries here when they encounter:

- **Canon question** — "the lore says X, but I need to know Y; please confirm or extend"
- **Canon gap** — "I'm authoring/wiring Z and there's no existing lore for it; please write a canonical entry"
- **Canon contradiction** — "lore doc A says X but lore doc B says Y; please reconcile"
- **Species not in spreadsheet** — "I see species $NAME mentioned in a doc but it's not in `species_inventory.csv`; please add it"
- **Stub module needs unlock content** — "this `TODO_LORE`-marked module is ready for Lore-chat authoring of name + description"
- **Quest needs hook content** — "this quest's recruitment-hook text is placeholder; please flesh out"
- **Bio-Archive entry needs body text** — "this archive entry's `long_desc` is stub; please author Furling-Steward-voice content (~150-300 words)"

---

## Authoring backlog reminders (no specific dispatch yet, but Lore-chat should track these)

These are not formal dispatches from other chats — they're Lore-chat's own awareness of work-in-progress areas where it may be called upon:

- **Bio-Archive entry catalog** — `references/lore/station-screens-design.md` enumerates 20 entries across 4 categories. When Design lands `archive_entries.py`, Lore writes the `long_desc` body text for each in Furling Steward voice (condensed lore-doc content; ~150-300 words each).
- **Schematic catalog descriptions** — `references/lore/economy-and-trade-loops.md` suggests ~15 schematics, each with a `source_origin` lore field. When Design lands `schematics.py`, Lore writes the source-origin strings (narratively connecting the source to the target).
- **Tarven Olwen-Sa prior-Steward anecdotes** — `references/lore/crew-recruitment-quests.md` Step 2 of his quest requires per-system flavor-anecdotes for the slice's optional-encounter systems. When Design surfaces the system list, Lore authors the anecdotes.
- **Furling crew Bio-Archive entries** — when the 5 crew are recruited, each adds a short bio-entry to the Bio-Archive's "Furling Crew" category (1-paragraph in-fiction summary in the Steward's voice). Cross-references both `crew-recruitment-quests.md` and `archive_entries.py`.

---

## 2026-05-19 — Consolidated TODO_LORE backlog (30 markers across 3 files)

**Origin**: Testing chat, during the overnight perfect-run dispatch pass. Aaron asked all chats to "fill out final orders" — this is the consolidated lore-authoring backlog for the Lore chat.

**How derived**: `Grep -rn "TODO_LORE" src/scz/`:
- `src/scz/content/archive_entries.py` — **20 markers** (proto-species Bio-Archive long_desc stubs + some branched variants)
- `src/scz/dialog/characters.py` — **9 markers** (crew recruitment dialog FSM content + Melnorme module stub)
- `src/scz/content/modules.py` — **1 marker** (Melnorme trade-network sensor deltas)

**Status**: ☐ Open. Each section below is independent — they can ship in any order.

### Section 1: Proto-species Bio-Archive long_desc entries (`src/scz/content/archive_entries.py`)

13 proto-species archive entries currently have stub `long_desc` text. Each needs Furling-Steward-voice expansion (~150-300 words each per the Bio-Archive design doc). The SC2 reference for each species is already in the marker comment to help anchor the in-fiction "before they were the SC2 race" voicing.

| Line | Entry | SC2 ref | Slice-era state |
|---|---|---|---|
| ~272 | `PROTO_SHOFIXTI` | The heroic small race who detonated themselves | Pre-sentient, observed in their system |
| ~292 | `PROTO_YEHAT` | Loyal avian aristocrats; ZebraNet honor-codes | Pre-sentient, observed |
| ~311 | `PROTO_PKUNK` | Chatty psychic-mystic pacifists | Pre-sentient; migratory flocking |
| ~329 | `PROTO_VUX` | Deeply-aesthetic xenophobes | Pre-sentient |
| ~349 | `PROTO_DRUUGE` | Merchant-cult with cosmic Furnace currency | Pre-sentient; subterranean burrowing tunnel-dwellers |
| ~368 | `PROTO_ILWRATH` | Religious-zealot mantis-priests of Dogar and Kazon | Pre-sentient; arachnoid pack predators |
| ~386 | `PROTO_SPATHI` | Cowardly burrowing slug-people with BUTT MISSILE | Pre-sentient; burrowing gastropods |
| ~405 | `PROTO_SYREEN` | Singing telepathic mostly-female warriors | Pre-sentient |
| ~424 | `PROTO_ZOQ_FOT_PIK` | Three symbiotic species | Pre-sentient |
| ~443 | `PROTO_THRADDASH` | Numbered Cultures warrior-culture | Pre-sentient |
| ~462 | `PROTO_UTWIG` | Doctrine-of-the-Ultron Utwig | **Newly-sentient in our era** — devolution canon per `project_utwig_devolution.md` |
| ~485 | `PROTO_SUPOX` | Polite plant-derived allies-of-Utwig | Pre-sentient; photosynthetic cognition |
| ~503 | `PROTO_DNYARRI` | Psionic enslavers of the Ur-Quan | Pre-sentient (haunting future-implication) |

Plus 2 branched/state-aware entries:

| Line | Entry | Note |
|---|---|---|
| ~524 | `PROTO_DNYARRI` (continued frog song) | "*(Steward-voice expansion pending — TODO_LORE.)*" — the standalone song-observation flavor line |
| ~540 | Branch on `game.flags['dnyarri_recommendation']` | Bio-Archive should branch text by the player's Dnyarri recommendation flag once it's set; today's text is the baseline-only |

Plus 1 branched late-game entry:

| Line | Entry | Note |
|---|---|---|
| ~863-893 | Branch on `game.flags['rainbow_seeded']` / `race_outcome` | Lore-chat to author branch-specific variants. The text below the marker is the baseline (covers don't-race / witness paths) |

**Voice anchor**: each entry is in-character Furling Steward voice — a journal-like sighting log with bio-data observations, behavioral notes, and (subtly) the slice's "leave them alone" thematic counterweight to the Ur-Quan uplift question (per `project_proto_species.md` and `project_humor_doctrine.md`).

### Section 2: Crew recruitment dialog FSM content (`src/scz/dialog/characters.py`)

4 stub crew recruits + 1 helper marker. Each is currently a 1-state placeholder. Lore chat owns the per-state dialog *content* (voice, beat sequencing, FSM transition lines); the Design chat will wire the FSM scaffolding into the runtime.

| Line | NPC | Crew role | Notes |
|---|---|---|---|
| ~588 | (helper comment) | — | Notes that `crew-recruitment-quests.md` specifies the recruitment-quest content; Lore should treat that doc as source of truth and expand here |
| ~5417 | **Bren-Vor Telcas** | Aimer (Weapons Officer) | TODO_AVATAR + TODO_LORE both flagged. Full 5-7 state recruitment FSM matching Mraka's structure |
| ~5436 | **Yelena Lwen-Tar** | Mender (Engineer) | Same — TODO_AVATAR + TODO_LORE |
| ~5454 | **Mira-Rou Halve-Tel** | Bio-Architect (Medic) | Same |
| ~5472 | **Tarven Olwen-Sa** | Star-Reader (Navigator) | Same; also has a planned per-system "prior-Steward anecdote" mini-quest noted in the existing Lore backlog reminder above |

**Reference patterns** (use as template):
- `mraka_yenn_sa` — the canonical 7-state recruitment FSM in the same file (already in production; use as voice + structure template)
- `references/lore/crew-recruitment-quests.md` — per-crew background + hook specs

**Also**: each recruited crew gets a short Bio-Archive entry (1 paragraph in-fiction Steward-voice summary) once they're aboard. Cross-references the existing "Authoring backlog reminder" Furling-crew-Archive bullet above.

### Section 3: Melnorme stub modules (`src/scz/content/modules.py` + cross-ref in characters.py)

| File | Line | Item | Note |
|---|---|---|---|
| `modules.py` | ~221 | `MELNORME_TRADE_NETWORK_SENSOR` deltas | Working hypothesis is "surfaces all super-giant trade-routes on the starmap regardless of whether the Steward has flown there." Lore chat to align with `species-quests.md` "Open canonical questions" block and finalize. |
| `characters.py` | ~1728 | (cross-reference to above) | Comment in Melnorme dialog FSM noting the module's deltas are stubbed; will surface in Bio-Archive once entry is authored. |

### Suggested authoring order

1. **The 4 crew recruitment FSMs** — highest-impact for the slice (unlocks the BEST-ending 5/5 crew criterion). Voice-rich because each recruit is a named individual; Mraka is the template.
2. **Branched archive entries** (the 2 state-aware ones around line 540 + line 863) — these are short authoring tasks that unlock the slice's narrative-payoff variation (player choices showing up in their Bio-Archive at the end).
3. **Proto-species bulk** — 13 entries, each ~150-300 words. Bulk authoring suited to a focused Lore-chat session. Each is also lightweight thematically (these are "left them alone" notes, the counterweight to the uplift dilemma).
4. **Melnorme module deltas** — small canonical decision, but unblocks the Melnorme economy loop.

### Wiring contract

Per the lane discipline: Lore chat writes the *text* (long_desc string content; per-state dialog lines for the crew FSMs). Design chat owns the *FSM transition logic* (`states`, `transitions`, `choices` data) for crew FSMs. When Lore drops new prose, file a tiny dispatch in `HANDOFF_design_chat.md` if the FSM transitions also need to change (e.g. "this state needs a new choice option for the player").

### Cross-references

- `tools/check_stubs.py` — re-run to verify count drops as each marker is filled
- `references/lore/the-furlings-and-the-others.md` — Steward voice canon
- `references/lore/proto-species-observations.md` — proto-species voicing canon
- `references/lore/crew-recruitment-quests.md` — per-crew spec
- `references/lore/species-quests.md` — Melnorme stub questions
- `memory/project_proto_species.md` — proto-species design doctrine
- `memory/project_humor_doctrine.md` — Steward humor (most aliens aren't funny; protagonist is)

### Skipped lane (Audio)

Audio chat HANDOFF was checked (`Grep TODO_AUDIO`) — only 3 self-reference markers, no actionable backlog. Skipping audio dispatch this round.

---

*(Future entries appended above this line.)*
