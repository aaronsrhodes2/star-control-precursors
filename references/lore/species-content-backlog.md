# Species Content Backlog — Invented Species to Fill Out the Galaxy

> Workspace for additional sentient species whose lore does NOT directly link to a future SC2 race. These exist for galaxy variety, ship-roster filling, and to give the Stay/Go conflict richer color. Aaron has covered all the SC2-linkable species; this doc tracks the species we invent fresh.

## Why we need these

SC2 has ~25 named races. Most of them are pre-sentient in the Furling era (the proto-*-Yehat, proto-Pkunk, proto-Spathi, etc. that appear as `*_PROTO` in our extracted star data). Those proto-species are *below the detection threshold* and the Furling answer is generally to leave them alone.

But the Furling era also has its own sentient civilizations — species that *will not survive* the Culling to be in SC2, and species whose lore is invented fresh for our game. These give us:

- **Real combat opponents** (other than Cleansers and rogue biots) for combat variety
- **Real diplomatic encounters** with the full Convince/Intimidate/Dominate methods
- **Ship roster variety** for super-melee
- **Lore color** — the galaxy was *full* of life before the Culling; we should show some of it

## Targets

We need **at least 2 more invented Precursor (Go) species** and **at least 2 more invented Homesteader (Stay) species** to round out the slice + super-melee roster. Each needs:

- A name (Furling-named or self-named — the Furlings can call them by translated nicknames)
- A homeworld coordinate (from the extracted starmap; pick an unclaimed system)
- A reason for Stay or Go (varied — not the same reasons we already have)
- A ship design (hull / weapon / mechanic — see [ship-roster.md](ship-roster.md))
- A voice profile (LLM prompt)
- A faction alignment with one of the existing Furling method-factions if applicable

## Brainstormed Stay reasons (each could be its own species)

Pick a couple that don't overlap with existing canon:

- **The Reincarnators** — believe death is a transition; the Culling is just a particularly aggressive birth-cycle; they will be reborn after; *they actually look forward to it*. Religious-philosophical. Peaceful. Stay because *crossing dimensions corrupts the cycle of rebirth*.
- **The Sworn-to-Place** — a species whose biology bonds them to a single planetary feature (a specific mountain range, a deep-ocean current, a fixed coordinate). Removing them is the worst form of pain. They cannot migrate without intolerable suffering.
- **The Long-Memories** — a species whose civilization is defined by maintained physical archives (libraries of stone, etc.). The archive is too heavy to move. They stay with their library.
- **The Bargainers** — believe the Others can be negotiated with. They've worked out a complex theory of inter-dimensional trade. They are wrong. They will die confidently.
- **The Defiant** — small, militaristic, proud. They CHOOSE to fight even knowing they will lose. They will not be moved by argument, threat, or pity.
- **The Quiet Voluntary** — a species that has *just* become sentient (during the Furling era) and asks to be *demoted* back below threshold via Furling intervention. They prefer to "go back to sleep."

## Brainstormed Go reasons (each could be its own species)

- **The Curious** — they want to see the new galaxy; pure exploratory motivation; the most willing migrators.
- **The Hunted** — they were already being hunted in our galaxy (by another species, or by some local cataclysm); the Migration is a gift.
- **The Engineered** — Furling-created species (like the Mycon biots but later, more advanced); their original purpose was to assist the Migration itself; loyal.
- **The Refugees of the Pre-Mobilization Trembling** — survivors of whatever event the Chenjesu remember as the *pre-Mobilization Trembling* (possibly a prior Culling); they have institutional memory of being almost-extinct and will leave at any cost.
- **The Calculators** — a hyper-rational species who ran the math and concluded Migration has the highest expected utility. They are insufferable about it.
- **The Younglings** — a young sentient species that has not yet built up emotional attachment to their homeworld; emigration feels natural, like all youth feels natural.

## Brainstormed unaligned / weird species

- **The Tide-Sleepers** — a species whose civilization cycles in/out of awareness; awake for ~10,000 years, dormant for ~100,000. They might *miss* the Culling entirely by being asleep through it. The Furlings cannot wake them in time to ask.
- **The Splinters** — a species that fractured millennia ago into sub-cultures with mutually-exclusive Stay-vs-Go convictions; civil war is *already* underway when the Furlings arrive.
- **The Listeners** — a species who only communicates by listening (no expressive language at all). The Furlings cannot Convince them in the normal sense; they can only *demonstrate*.

## Authoring Workflow

For each species we add:

1. Pick a name. The Furlings tend toward short, evocative translations (one or two syllables).
2. Pick a homeworld star from the extracted `stars.json` (avoid stars already assigned to canon species).
3. Write the Stay/Go reason in one paragraph. Pick a reason that doesn't duplicate an existing species' reason.
4. Sketch the ship: hull class (light/medium/heavy), one signature weapon, one signature mechanic. Personality-vector baseline.
5. Write a voice profile (1-paragraph LLM system prompt).
6. Add a full entry to [species-precursor-era.md](species-precursor-era.md) following the existing format (Backstory, Cultural Attitudes, Quirks, Postures, Individual Diversity Vectors).
7. Add the ship to [ship-roster.md](ship-roster.md) with combat AI baseline.

## Initial Picks (finalized)

Two of the four invented-species slots are now filled by **canonical SC2 species we get to flesh out** (because they're extinct in SC2 with sparse canon — see [furling-artifacts-and-callforwards.md](furling-artifacts-and-callforwards.md)). The remaining two slots are still genuinely invented.

| Slot | Side | Species | Source |
|---|---|---|---|
| Stay #1 | Homesteader | **The Taalo** | SC2-canonical, extinct by SC2 era. Peaceful crystalline-amphibian pacifists. Make the **Protector** psionic-shield (which outlives them). Die in the Culling. **Cannot be saved** — the slice's most poignant beat. |
| Stay #2 | Homesteader | **The Defiant** (invented) | Combat-coded; aggressive ship with low caution; war-band matchup distinct from the proto-Ur-Quan; voice is proud-doomed |
| Go #1 | Precursor | **The Burvixese** | SC2-canonical, extinct by SC2 era. Industrious humanoid engineers. Make the **Burv Broadcasters** (galaxy-wide hyperwave memorial network — "we were here. If you find this, you are not alone."). Migrate with the Furlings; their broadcasters survive them in our galaxy. Slice's most cheerful Precursor encounter. |
| Go #2 | Precursor | **The Curious** (invented) | Light-fast exploration ship; weak in combat but evasive; voice is wide-eyed and overwhelming-everything-with-questions |

This gives us **two fanservice species** (Taalo, Burvixese) tied directly to SC2 lore items players will recognize, and **two invented species** (Defiant, Curious) that exist purely for the Furling-era story. Good balance.

## Naming Conventions

When inventing species names, the Furlings tend to translate alien self-designators into one of these patterns:

- Two-syllable, soft-consonant: *Velish*, *Maron*, *Tylar*, *Olin*
- Three-syllable, ending in a vowel: *Asterya*, *Korine*, *Mellava*
- Hard-consonant, single-syllable: *Vorn*, *Krak*, *Sshk* (the LLM should make the harsh ones harsh)
- Compound-descriptive: *the Listeners*, *the Reincarnators*, *the Sworn-to-Place* (literal-translation form)

Aaron should approve any final names; this doc just suggests forms.
