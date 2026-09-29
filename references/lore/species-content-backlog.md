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

The slot table below tracks invented + fanservice species for the slice. **Canon reconciliation note (revised 2026-05-17, second pass)**: the "Be Loud" doctrine — broadcast cognition so loudly the Others recognize you as a peer and pass you over — is **exclusively a Burvixese (alien-species) project** in canon. Two earlier drafts mis-assigned it to (a) a separate alien species called "Taalo" and (b) a Furling sub-faction called "Talos." Both retracted. The Taalo are now correctly framed as the **SC2-canonical silicon-based alien species** (Homesteader-by-biology; below the Others' detection threshold) who later build the **Taalo Shield** ~230kya from now. The Burvixese build the **Burv Caster** as their failed Be-Loud project in our slice; the SC2-canonical scattered Burv Broadcasters are amplifier nodes of that project.

| Slot | Side | Species | Status | Source |
|---|---|---|---|---|
| Stay #1 | Homesteader | **The Utwig** | ✅ **Authored** (2026-05-17) | SC2-canonical, ceremonial-locked depressed mask-wearers by SC2 era. In our era: newly-sentient species who *chose* devolution-via-mask-and-ceremony as their survival doctrine. The Veils Falling is the mid-game witnessing event. They survive the Culling locked into ritual. SC3's "Precursors devolved into animals" is canonically a misreading: it was the Utwig. |
| Stay #2 | Homesteader | **The Taalo** | ✅ **Authored** (2026-05-17, third pass — shield-tragedy reframe) | SC2-canonical silicon-based "rock-like" sentients; the species *is* a mountain range on a single planet; they cannot leave (metabolism tied to local ecosystem). Cognitive signature too large/coherent to slip below the Others' threshold despite silicon substrate. **They build the Taalo Shield *in our slice*** as a planetary anti-Others defense; the Shield does not work; the Taalo are **Eliminated** by the Others regardless of player intervention. The inert Shield survives them and is recovered 230kya later by SC2 archaeologists, who use its side-effect psionic-nullifier property against the Dnyarri. **Side-quest: help with the Shield (better SC2-artifact recovery) or don't (worse) — outcome for the Taalo is the same.** The slice's defining tragedy. |
| Stay #3 | Homesteader | **The Defiant** (invented) | ⏳ Pending | Combat-coded; aggressive ship with low caution; war-band matchup distinct from the proto-Ur-Quan; voice is proud-doomed |
| Go #1 | Precursor (mostly Eliminated) | **The Burvixese** | ✅ **Authored** (2026-05-17, second pass) | SC2-canonical alien engineers from Burvix Caster. In our era they have committed to the **Be-Loud doctrine** — build the **Burv Caster** to broadcast cognition loudly enough that the Others will recognize them as peers and pass them over. The Furling Council advised against it. The doctrine fails catastrophically — Others arrive faster, eat the loud first. Most Burvixese die at the Caster site; a small contingent migrates to Andromeda. SC2-canonical "Burvixese are extinct, broadcasters scattered" traces to this loss. |
| Go #2 | Precursor | **The Curious** (invented) | ⏳ Pending | Light-fast exploration ship; weak in combat but evasive; voice is wide-eyed and overwhelming-everything-with-questions |

**Net effect (second pass)**: the slice now has **three fanservice alien species** (Burvixese, Taalo, Utwig — all SC2-canonical) and **two invented alien species** (Defiant + Curious). The Be-Loud doctrine is fully on the Burvixese; the Talos Furling sub-faction is retracted; the Taalo are the SC2-canonical silicon-based aliens (no Be-Loud, no Resonator — they are below-threshold by biology). Homesteader-side ship roster: Defender (Furling) + Mmrnmhrm + Proto-Ur-Quan + Proto-Qor-Ah + Defiant (pending) = 5. Precursor-side ship roster: Furling Scout + Persuader + Arilou + Androsynth + [OPEN slot, was Burvixese Memorialist, now needs a new candidate — possibly Curious] = 4 + 1-pending.

### Where each authored species lives

**Taalo** (Authored 2026-05-17, *third pass — shield-tragedy reframe*):
- Species sheet: [species-sheets.md §9](species-sheets.md) — silicon-based aliens, mountain-range substrate, cannot leave home planet, **building the Shield in our slice; the Shield fails; they die**
- Quest: [species-quests.md "The Shield That Will Not Hold"](species-quests.md) — side-quest; help-or-not, outcome same
- Ship: NONE — the species is a mountain range; cannot leave the planet (metabolism ecosystem-dependent). See [ship-roster.md "Species without ships"](ship-roster.md)
- Artifact callforward: [furling-artifacts-and-callforwards.md "The Taalo Shield"](furling-artifacts-and-callforwards.md) — the Shield is built *in our slice* (not post-slice as in earlier drafts); fails against the Others; inert remains survive as the SC2 anti-Dnyarri artifact via side-effect psionic-nullifier property
- Homeworld: **Taalo's Stone II** in the Taalo's Stone system (synthetic at (700, 4800) — see [slice-cluster.md §12](slice-cluster.md))

**Burvixese** (Authored 2026-05-17, *second pass* — Be-Loud doctrine, mostly Eliminated):
- Species sheet: [species-sheets.md §10](species-sheets.md)
- Quest: [species-quests.md "The Caster Reckoning"](species-quests.md)
- Ship: NONE in combat — Be-Loud doctrine consumes all engineering capacity. See [ship-roster.md "Species without ships"](ship-roster.md)
- Artifact callforward: [furling-artifacts-and-callforwards.md "The Burv Caster"](furling-artifacts-and-callforwards.md) — the failed Be-Loud device; the canonical SC2 Burv Broadcasters are network amplifier nodes
- Homeworld: **Burvix Caster** (already in stars.json at line 238)

**Utwig** (Authored 2026-05-17):
- Species sheet: [species-sheets.md §11](species-sheets.md)
- Quest: [species-quests.md "The Veils Falling"](species-quests.md)
- Ship: NONE — they declare technology profane during the doctrine. The SC2-era *Jugger* ship is a post-Culling Druuge-traded rebuild, not slice-relevant. See [ship-roster.md "Species without ships"](ship-roster.md)
- Narrative + SC3-misinterpretation hook: [furling-artifacts-and-callforwards.md "The Utwig and the Ultron"](furling-artifacts-and-callforwards.md)
- Homeworld: the **Utwig** system (already in stars.json at line 79 as `UTWIG`, tagged `UTWIG_PROTO` in the precursor-era starmap)
- **Reclassification note**: the Utwig were previously listed in [proto-species-observations.md](proto-species-observations.md) as pre-sentient grazers. They have *just* become sentient in our era (which is what triggers the devolution doctrine). The proto-observation is now historical context, not a current observation

### Pending — what the Defiant and Curious still need

For each remaining slot, the authoring workflow at the top of this doc applies. Required artifacts per remaining species:
- Homeworld coordinate assigned from `stars.json`
- §1–§7 species sheet in [species-sheets.md](species-sheets.md)
- Quest entry in [species-quests.md](species-quests.md)
- Ship stat block in [ship-roster.md](ship-roster.md) §"Stat Blocks"
- Row in the Slice-Scope Roster table replacing the current `[INVENTED species ship — TBD]` placeholder

Authoring the Defiant first is recommended — they fill the last Homesteader-side combat slot, which is the highest-leverage gap for super-melee variety. The Curious are nice-to-have but lower priority. The Stay #3 open slot is the lowest priority and may simply be left vacant if the alien-Homesteader-side roster of 4 (Mmrnmhrm + Proto-Ur-Quan + Proto-Qor-Ah + Defiant when authored) feels sufficient against the 4 alien-Precursor-side species (Arilou + Androsynth + Burvixese + Curious when authored).

## Naming Conventions

When inventing species names, the Furlings tend to translate alien self-designators into one of these patterns:

- Two-syllable, soft-consonant: *Velish*, *Maron*, *Tylar*, *Olin*
- Three-syllable, ending in a vowel: *Asterya*, *Korine*, *Mellava*
- Hard-consonant, single-syllable: *Vorn*, *Krak*, *Sshk* (the LLM should make the harsh ones harsh)
- Compound-descriptive: *the Listeners*, *the Reincarnators*, *the Sworn-to-Place* (literal-translation form)

Aaron should approve any final names; this doc just suggests forms.
