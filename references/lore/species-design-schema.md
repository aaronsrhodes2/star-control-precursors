## Species Design Schema (canonical template)

> The structural template every species in the game conforms to. Lore docs ([species-precursor-era.md](species-precursor-era.md), [the-androsynth-refugees.md](the-androsynth-refugees.md), etc.) hold the *narrative* for each species; this document is the *form* they all fit into. When inventing or editing a species, fill in every section here. Empty sections are explicit decisions (e.g. *"no ship — they are rooted"*), never oversights.

LLM variation is deferred to a later phase per the engine-first commitment in [variation-architecture.md](variation-architecture.md). All schema fields below are authored as static deterministic content for now. The schema is shaped so a future LLM-rendering layer can read these fields verbatim as prompt material.

## §1 — Physical Attributes

The base for visual generation (Flask-SD prompts in Phase 4) and animation (Phase 5+). The text here must be enough that a text-to-image model produces a recognizable archetype on first prompt.

- **Body archetype**: one sentence, concrete and image-able. *"Floating gas-bag drifter, 4-meter diameter, semi-transparent membrane with internal pulse patterns."*
- **Scale next to a Furling**: Furling = 5–8 m tall reference. State whether the species is much smaller, comparable, or much larger.
- **Distinctive features**: 3–5 specific visual hooks. Color regions, limbs/appendages, eye/sensor configuration, surface texture. These are what makes the SD prompt produce *this species and not another*.
- **Color palette**: 3–4 dominant colors + 1 accent color (RGB or named). Used for warp-pod color, dialog portrait fill, and SD prompt color words.
- **Motion / pose** *(animation-future)*: how they hold themselves, how they move. Drift / hover / amble / sessile / etc.
- **Visual progression budget** *(per the three-pillar variation principle)*:
  - **Phase 4 base**: one static SD-generated portrait per species
  - **Phase 4.5**: per-individual deterministic variation knobs (hue shift, age band, accessory variation) — same archetype, no two individuals identical
  - **Phase 5+**: subtle idle animation (a breath, a drift, a pulse) on the portrait
  - **Phase 6+**: LLM-variation overlay (a few words of per-encounter visual modulation fed back into the SD prompt) — deferred

## §2 — Speech Pattern

Translator imperfection is canon: the Furling translator passes most semantics through, but it lets each species' quirks bleed through on purpose. This is what makes alien dialog feel alien even when rendered in English.

- **Translator quirk**: one to three idiosyncrasies that distinguish this species' translated speech from neutral English. Examples:
  - *Slylandro*: run-on awed sentences, 3+ commas minimum, plural "we" because wind-currents speak as one
  - *Arilou*: multiple tenses in one sentence ("we were-are-will-be relieved"), refer to un-happened events as memories
  - *Mycon*: CAPITALS for invocations, lowercase for status; third-person self-reference; fragmented ritual phrases
- **Vocabulary anchors**: 5–10 words/concepts they over-use; words/concepts they cannot translate
- **Sample lines**: 2–3 short authored examples in the target voice. These seed both the canned fallback bank and (future) the LLM voice prompt
- **Non-verbal species**: if dialog is sensory description rather than speech (e.g. proto-Ur-Quan pheromone-cloud colors), state how it's rendered to the player (italicized prose, color tokens, etc.)

## §3 — Cultural Posture

A single dominant posture + 1–2 secondary notes. The posture biases the dialog FSM's default choice presentation and (later) the combat-AI personality preset. **Canon postures** — pick one as dominant:

| Posture | Meaning |
|---|---|
| Aggressive | Initiates conflict; reads contact as threat |
| Peaceful | Avoids conflict; reads contact as opportunity |
| Curious | Engages first; asks more than it answers |
| Indifferent | Engagement is transactional; no investment |
| Scared | Defensive; assumes contact is hostile until proven otherwise |
| Brave | Will face threat without flinching; not the same as aggressive |
| Reverent | Treats contact as significant or sacred |
| Patient | Long timescale; not in a hurry to resolve anything |
| Fragmented | No coherent posture — internal factions or possessed individuals |

Then: 1–2 secondary notes — *e.g. "Pacifist by physiology AND religion. Cannot defend if attacked."* — that color the dominant posture.

## §4 — Humor Doctrine (cross-cutting)

**The Furling protagonist (the player) has a GREAT sense of humor.** Wry, observational, occasionally bone-dry. The player's dialog choices should include witty options wherever tonally appropriate. This is canon for *the player's voice*; other Furlings vary — Persuader Halia is warm-weary, the Sage is cryptic, Cleansers are humorless, Defenders are grim.

**Most alien species do not have humor**, by their own lights. The humor in alien-Furling dialog comes from **cultural friction** — the player's witty inner reading of:
- **Cultural differences**: a Mycon biot solemnly reports a status the player finds absurd → the player's choice phrasing can be deadpan or mock-formal
- **Physical differences**: the Slylandro's "shaggy giants" of the player → the player can play it back at them
- **Unexpected similarities**: the Mmrnmhrm say "Archive entry seven million two hundred forty thousand" with no awareness this is funny → the player can deadpan-reciprocate

The humor doctrine is a **one-way street**: the player is funny, the aliens aren't (with rare exceptions — a few Arilou *might* be drily aware they sound condescending; a few Slylandro *might* notice they over-share). The friction creates the laugh, not the alien.

**The Others are NEVER funny.** Not in their speech, not in the player's choices around them, not in flavor text. The Others are pure dread. If a Furling cracks a joke around an Other-rift sighting, the joke lands wrong on purpose — it's the player coping, and the world is too cold for the joke to land.

This doctrine affects every layer of dialog content: canned fallback text, dialog choice phrasing, (later) LLM prompt system messages, combat banter, descriptions of encounters. The protagonist's humor is *the* tonal signature distinguishing this game from straight-faced space opera.

## §5 — Ship (or "no ship" — state the reason)

If the species has spacecraft in the slice era, fill in [ship-design-schema.md](ship-design-schema.md) for each ship class. If not, this section is just the reason: *"Slylandro are rooted gas-giant physiology, no ships."*

## §6 — Quest (one per species, bidirectional)

Each slice species has **one canonical quest** that fits the structure:

- **They want from us**: a concrete thing only the Furling Steward can deliver
- **We want from them**: a concrete reward (ship module, lore unlock, faction standing, special ability, irrefutable evidence)
- **Bridge**: the in-fiction reason these two are bundled in one transaction

The quest is the species' narrative center of mass. Branching outcomes (succeed cleanly, succeed with cost, fail gracefully, refuse) connect to the win-condition terminal-status framework in [win-condition-and-methods.md](win-condition-and-methods.md).

Full per-species quest sheets in [species-quests.md](species-quests.md).

## §7 — Win-Condition Terminal Status

How this species ends up at the moment the door closes — referenced for completeness, designed in detail in [win-condition-and-methods.md](win-condition-and-methods.md):

| Terminal status | Meaning |
|---|---|
| Migrated | They cross into the neighboring galaxy |
| Cloaked | They stay but go silent (Slylandro Cloaking Satellite) |
| Hidden | They retreat to Quasi-Space (Arilou path) |
| Eliminated | Cleansed before the door closes |
| Pre-sentient | They never crossed the detection threshold — left alone |

## Authoring Checklist

A species sheet is complete when:
- [ ] §1 has enough text that an SD prompt produces a recognizable archetype
- [ ] §2 has a quirk distinct from every other species' quirk + 2 sample lines
- [ ] §3 picks one canonical posture and adds 1–2 secondary notes
- [ ] §4 has been considered — does the player get one or two witty dialog options against this species? What kind of friction is the laugh on?
- [ ] §5 either fills the ship schema or states the reason no ship exists
- [ ] §6 has a bidirectional quest sketch
- [ ] §7 declares the canonical terminal status(es) reachable from the quest

A species sheet that fails the checklist is not slice-ready.
