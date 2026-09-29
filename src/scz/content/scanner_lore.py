"""Scanner Lore — per-star and per-planet canonical reveal text.

Canon source: `references/lore/scanner-lore.md`.

The Furling Scout's onboard scanner surfaces lore-text passages when
the Steward arrives in a system or enters orbit around a planet. The
reveals are the slice's primary *exploration reward* — every system
the player visits canonically becomes more meaningful.

**Voice**: Furling Steward observation register — quiet, factual,
occasionally warm or wry. SC2 references are backdated by the
canonical 250kya gap (cities haven't been built yet; species that
arise later don't exist yet; geographic features are deep-past forms
of their SC2-era counterparts).

**Reveal flow**:
1. Player arrives in a system → `_star_key(star)` lookup → if matching
   `STAR_LORE` entry exists, the scanner displays the passage in the
   HUD's SCANNER READOUT panel; first-time view sets
   `flag:lore_revealed_<key>=True` and (Phase 5) auto-adds a
   Bio-Archive entry.
2. Player enters orbit around a planet → per-planet key
   `(star_key, planet_index)` lookup → if matching planet_lore entry
   exists, the same panel displays the orbital scan.
3. Subsequent visits to the same star/planet show an abbreviated
   "Scanned ✓" indicator instead of the full passage.

**Post-Fall divergence**: for `MH_LAI_HOME`, the Mh-Lai planet lore
differs based on `flag:mhlai_destroyed=True`. The handler picks the
appropriate variant.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scz.engine.game import Game


@dataclass(frozen=True)
class SystemLore:
    """Lore content for one stellar system.

    - `star_lore`: 1-3 sentence reveal shown on system entry. None to
      skip the star-level reveal (e.g. for unremarkable systems).
    - `planet_lore`: planet index → lore-text dict. Only includes
      planets that have something interesting to scan; mundane planets
      (most gas giants, generic ROCKY) are omitted and produce no
      reveal on orbit.
    - `mhlai_post_fall_override`: for MH_LAI_HOME only — alternate
      `planet_lore[1]` text used when `flag:mhlai_destroyed=True`.
    """
    star_lore: str | None = None
    planet_lore: dict[int, str] = field(default_factory=dict)
    mhlai_post_fall_override: str | None = None


# Per-star lore. Keys are the `defined_name` from stars.json (or
# `home_system` synthetics like MH_LAI_HOME / TAALOS_STONE / etc).
STAR_LORE: dict[str, SystemLore] = {

    "MH_LAI_HOME": SystemLore(
        star_lore=(
            "The Furlings' Hearth. Stable yellow-orange dwarf. "
            "Sustained habitability across four billion years. "
            "Three confirmed Furling-era colonization waves; the "
            "fourth is your own. The star has a faint canonical "
            "name in Furling — Mh-Layi-Olen, 'the patient one' — "
            "though the Furlings rarely speak it; they save the "
            "name for the moments that matter."
        ),
        planet_lore={
            # Mh-Lai homeworld sits at planet index 2 (see
            # home_system.home_planets — index 0 = Mh-Lai I, index 1 =
            # Mh-Lai II, index 2 = Mh-Lai itself, index 3 = the gas
            # giant, index 4 = Furlmart). Indices match the canonical
            # hand-built planet list, not the SC2-ish "Mh-Lai I/II/III"
            # naming on display.
            2: (
                "Mh-Lai. Capital of the Furling Persuader Council. "
                "Furred-everywhere interior architecture; canopy "
                "cities woven into the planet's mountain ridges; "
                "Mh-Lai Station orbits at L1 with the Hearth. "
                "Population: approximately 2.3 billion Furlings. "
                "Warm-temperate climate; long autumn-and-spring; "
                "brief sharp summers. The Council chambers are in "
                "the Persuader Council Hall on the third continent."
            ),
            4: (
                "Furlmart. Mh-Lai's third moon. Mineral-rich cargo-"
                "handling depot; Furlmart Cooperative runs the docks. "
                "Your shakedown run delivers here. The senior cargo "
                "handler, Borek-Sa-Selvenne, has been at this post "
                "for sixty of his eighty Furling years and is "
                "canonically *unimpressed* with you."
            ),
        },
        mhlai_post_fall_override=(
            "Mh-Lai. Consumed. The Council chambers are gone. "
            "Hearth-of-Iron docks at L1 carries the survivors. "
            "Sensor returns indicate no surface activity. The Mh-Lai "
            "Station debris remains in orbit, untouchable for "
            "salvage by Migration protocol."
        ),
    ),

    "ARILOU_OUTPOST": SystemLore(
        star_lore=(
            "The Sage's Threshold. F-class star, canonically anchored "
            "to the slice's primary Quasi-Space portal network. The "
            "Arilou chose this star because its gravity well "
            "stabilizes their dimensional crossings. They will not "
            "say why specifically; the canonical Arilou register: "
            "'the chosen-one knows; the others may discover later.'"
        ),
        planet_lore={
            1: (
                "Arilou Sanctuary. Single outpost; approximately two "
                "hundred Arilou Sages permanently in residence. The "
                "atmosphere shimmers with dimensional-substrate "
                "refraction — the Quasi-Space proximity makes the "
                "air *taste different* per canonical Furling reports. "
                "Sage Lwen-Olou's tower is visible from orbit. The "
                "Sage will see you before you land. This is "
                "canonical, and unsettling."
            ),
        },
    ),

    "SOL_PROTO": SystemLore(
        star_lore=(
            "Sol. G-class yellow dwarf. Stable, unremarkable, "
            "well-aged. The third planet hosts proto-Human "
            "populations in their mid-Neolithic period — perhaps "
            "twenty million pre-sentient hominids. Below the "
            "Others' threshold by a comfortable margin. The "
            "Furling Council's standing instruction: observe, log, "
            "do not interfere."
        ),
        planet_lore={
            2: (
                "Earth, as the proto-Humans will call it later. "
                "Pre-Neolithic surface; canonical mid-Pleistocene "
                "Earth — large mammals, expansive grasslands, "
                "early human technology limited to flint-knapping "
                "and seasonal migration. The proto-Humans here will "
                "become Captain Zelnick's people in approximately "
                "250,000 years. Do not interfere."
            ),
        },
    ),

    "SLYLANDRO": SystemLore(
        star_lore=(
            "Beta Corvi. Yellow-orange dwarf with an unusual "
            "heavy-element gas-giant — canonically the gas-giant "
            "*Source Mass* that hosts the Slylandro civilization. "
            "SC2 archaeologists 250,000 years from now will catalog "
            "this system as the Slylandro Probe origin; in our era, "
            "it is the living Slylandro civilization."
        ),
        planet_lore={
            # Slylandro homeworld is the gas-giant (per beta_corvi content);
            # planet index typically 2 in the procgen layout but the
            # Slylandro hand-built planets put their world at index 2.
            # If the player orbits a different planet here the reveal
            # is just the star lore from system entry.
            2: (
                "Source Mass. Gas-giant; Slylandro Observer "
                "civilization in the upper troposphere. Drift-think "
                "layer concentrates at ~0.4 bar pressure; the "
                "Slylandro literally *float* on cognition-pattern "
                "thermodynamics. Population estimation is a category "
                "error — canonically the species is *cognitively "
                "continuous*. SC2 archaeologists will later "
                "misclassify them as 'gas-bag autonomous probes' — "
                "they are people, not robots."
            ),
        },
    ),

    "CHENJESU_PROTO": SystemLore(
        star_lore=(
            "Procyon. Bright F-class binary. The Chenjesu Crystalline "
            "Collective grows on the rocky inner planet — silicon-"
            "lattice sentients with thought-substrate so foreign to "
            "the Others' detection apparatus that they read as "
            "*geological process*, not mind. Below threshold by "
            "biology. They have watched at least one prior Culling "
            "from this stone."
        ),
        planet_lore={
            1: (
                "Chenjesu lattice-spires. Continental crystalline "
                "outcrop covering most of the planet's largest "
                "landmass. The Collective's matriarch-elders have "
                "been adding lattice for tens of millions of years. "
                "Communication is by audible tone resonance, slow "
                "enough that a single Chenjesu sentence takes 10-20 "
                "seconds. Sit. They will speak when they speak."
            ),
        },
    ),

    "MMRNMHRM_OSSUARY": SystemLore(
        star_lore=(
            "Gamma Trianguli. Red dwarf, ancient and cool, far from "
            "any major Furling staging route. Mmrnmhrm Sentinel-"
            "Loop home. Their First-Makers' civilization died "
            "approximately seven million years ago in a prior "
            "Culling; the Sentinels have maintained the empty "
            "Homeworld since. They will see you before you cross "
            "the heliopause. The canonical Mmrnmhrm courtesy: "
            "they hail incoming vessels with the formal phrase "
            "'defense did not work; we attempt anyway.'"
        ),
        planet_lore={
            1: (
                "Ossuary. The First-Makers' homeworld. Iron-rich "
                "rocky world; visible from orbit as a continent of "
                "silent imposing ruins. Empty cities. Prepared "
                "meal-tables. Open doors. The Sentinels maintain "
                "the cities exactly as they were left, on schedules "
                "they have followed for three to eight million "
                "years. Walking the empty streets is the slice's "
                "most canonically quiet surface experience."
            ),
        },
    ),

    "TAALOS_STONE": SystemLore(
        star_lore=(
            "Red dwarf. Warm, silicate-rich, geothermally active — "
            "the canonical environment for the silicon-based Taalo "
            "Mountain-Range Sentience. SC2 archaeologists 250,000 "
            "years from now will catalog this system as the Taalo "
            "Shield recovery site at Delta Vulpeculae II-C. What "
            "they find then is what we are building *now*."
        ),
        planet_lore={
            1: (
                "Taalo's Stone II. The home mountain-range. "
                "Two thousand kilometers long; eight to twelve "
                "kilometer peaks; the species *is* the range. "
                "Individual Taalo are mobile silicon-organism "
                "fragments — they shamble across rock substrate at "
                "geological tempo. Shield-construction infrastructure "
                "is visible from orbit: copper-brass generator nodes "
                "embedded in the mountain flanks; pale-violet "
                "pre-activation glow patterns. The Steward is "
                "canonically the fourth Steward to visit this ridge."
            ),
        },
    ),

    "BURVIX_CASTER": SystemLore(
        star_lore=(
            "Delta Cassiopeiae. Yellow dwarf; mid-cluster. The Burvix "
            "Caster system. Yellow dwarfs are the canonical thermal "
            "environment for industrial-civilization four-armed "
            "engineering; the Burvixese chose this world for the "
            "Caster's planetary-scale broadcaster install. Smaller "
            "broadcaster nodes pre-deployed across the galaxy "
            "amplify the carrier-band from here."
        ),
        planet_lore={
            1: (
                "Burvix Caster (the world, named after the device). "
                "Industrial heavy-built; the Caster's primary array "
                "is embedded in the equatorial crust. Visible from "
                "orbit as concentric construction rings around the "
                "cognitive-amplifier core. Pre-activation: pale "
                "violet glow patterns calibrating against the "
                "stellar background. Activation: pending the next "
                "moon's twelfth cycle. The Foreman is canonically "
                "Vesh-Kar Twel-Pin."
            ),
        },
    ),

    "LEMMKIN_WHIRLIGIG": SystemLore(
        star_lore=(
            "Beta Crucis. Green dwarf, mid-southern slice. The "
            "Whirligig system. The star is named by the Lemmkin "
            "for their planet's rapid axial rotation — visible "
            "from interstellar distances as a planet that "
            "*flickers* in light-curve readings. The Lemmkin are "
            "fast-breeding, eclectic-research-temperament "
            "archivists; they will find you delightful and ask "
            "many questions."
        ),
        planet_lore={
            1: (
                "Whirligig. Densely forested terrestrial; six-hour "
                "day; canopy cities woven into kilometer-tall "
                "trees. Population: difficult to estimate (the "
                "Lemmkin do not stand still long enough for an "
                "accurate census; canonical Furling Council "
                "estimate ~120 million but with wide bounds). "
                "Cliff-mortality warning signs visible on Surface "
                "scan — canonical Lemmkin trait."
            ),
        },
    ),

    "UTWIG_PROTO": SystemLore(
        star_lore=(
            "Beta Aquarii. Yellow dwarf. The Utwig homeworld system. "
            "The Utwig have just become sentient and are entering "
            "their canonical Veils Falling — the formal mass-"
            "adoption of mask-and-ceremony culture as cognitive-"
            "dampening doctrine. The transition is in three days; "
            "elders are already in early ceremonial veils."
        ),
        planet_lore={
            2: (
                "Beta Aquarii III. The Utwig homeworld. Temperate; "
                "armored bipedal grazers in mid-cultural-transition. "
                "Cities are reorganizing around mask-craftworks and "
                "ritual-temple courtyards; orbital shuttles are "
                "being ritually dismantled; foundries cold. "
                "Veiled-In-Three-Days is the canonical Council "
                "speaker. The Quieting is in twelve days."
            ),
        },
    ),

    "DNYARRI_PRIMITIVE": SystemLore(
        star_lore=(
            "Beta Orionis. Yellow dwarf. The Dnyarri are pre-"
            "sapient amphibian-derived sentients on the third "
            "planet — approximately twelve million individuals "
            "exhibiting psionic precursor activity. Survey "
            "Commander Vesh Vasa-Lon's observation detail "
            "is permanently stationed in-system. The Cleanser "
            "bench has filed a petition; the Council is waiting "
            "on a Steward's recommendation."
        ),
        planet_lore={
            2: (
                "Beta Orionis III. Pre-sapient amphibian-derived "
                "population concentrated in subtropical "
                "freshwater systems. Psionic precursor activity "
                "measured at +14× the long-baseline trend over "
                "the last observation millennium. Extrapolation "
                "suggests threshold-crossing within 40-90 "
                "thousand years. Survey-camera arrays log "
                "everything. The Dnyarri-here do not yet know "
                "they are being watched."
            ),
        },
    ),

    "MYCON_BIOT_HIVE": SystemLore(
        star_lore=(
            "K-class orange dwarf. Mycon biot operations "
            "concentrated on the third planet — Furling-managed "
            "terraforming infrastructure, canonically the central "
            "node of the slice's biot-terraforming program. The "
            "Mycon collective here has been operational for "
            "approximately three thousand eight hundred Furling "
            "years."
        ),
        planet_lore={
            2: (
                "The Mycon Hive Cradle. Active biot installation. "
                "Surface: lava-glow plus biot-slime mats covering "
                "approximately twelve percent of the cooled-basalt "
                "regions. The biots are working. The biosphere is "
                "being engineered into Furling-specified "
                "terraforming conditions. **Listen for "
                "FIRST_WHISPER patterns** — your Bio-Architect crew "
                "will notice if the biot-mass is developing "
                "sentience."
            ),
        },
    ),

    "ORZ_RIFT": SystemLore(
        star_lore=(
            "Gamma Vulpeculae. Blue-white giant. Canonical Furling "
            "Rift research station orbits the third planet. "
            "Anomalous dimensional-substrate readings: the Furling "
            "Hider faction's longest-running anomaly study lives "
            "here. **Caution: ambient dimensional-stress mid-"
            "system; minor Time Drive interference reported.**"
        ),
        planet_lore={
            2: (
                "The Rift. Furling Rift research station. Half-built "
                "dimensional-substrate observatory; Hider faction "
                "operates here on a permanent rotation. The Rift "
                "itself — the dimensional anomaly the station "
                "studies — is canonically *visible from orbit* as "
                "a faint chromatic shimmer when conditions align. "
                "Canonical Hider rule: *we measure; we do not "
                "enter.*"
            ),
        },
    ),
}


def star_key(star: dict) -> str:
    """Return the canonical scanner-lore key for a star.

    Synthetic stars carry their own `defined_name` (MH_LAI_HOME for
    Mh-Lai, ARILOU_OUTPOST for the Sage's seat, TAALOS_STONE for the
    Taalo system, etc); SC2-canonical stars use their `defined_name`
    from `stars.json` (SLYLANDRO, CHENJESU_PROTO, MMRNMHRM_OSSUARY,
    etc). Stars without a defined_name fall through to the
    `cluster_name` so future content can light them up.
    """
    dn = star.get("defined_name")
    if dn:
        return dn
    return star.get("cluster_name", "UNKNOWN")


def star_lore_for(star: dict, game: "Game | None" = None) -> str | None:
    """Return the star-level scanner reveal text, or None if the star
    has no registered lore.

    Note: this is NOT idempotent with the reveal-flag — the caller
    decides whether to set `lore_revealed_<key>` after displaying.
    """
    entry = STAR_LORE.get(star_key(star))
    if entry is None:
        return None
    return entry.star_lore


def planet_lore_for(
    star: dict, planet_index: int, game: "Game | None" = None,
) -> str | None:
    """Return the orbital-scan reveal text for a planet, or None if
    the planet has no registered lore.

    Handles the Mh-Lai post-Fall override: when `flag:mhlai_destroyed`
    is True and the planet is Mh-Lai itself (planet_index 1 at
    MH_LAI_HOME), the post-Fall variant is returned.
    """
    entry = STAR_LORE.get(star_key(star))
    if entry is None:
        return None
    # Mh-Lai post-Fall override — homeworld is at planet index 2
    if (
        star_key(star) == "MH_LAI_HOME"
        and planet_index == 2
        and entry.mhlai_post_fall_override is not None
        and game is not None
        and game.flags.get("mhlai_destroyed")
    ):
        return entry.mhlai_post_fall_override
    return entry.planet_lore.get(planet_index)


def reveal_star_lore(game: "Game", star: dict) -> tuple[str | None, bool]:
    """Mark the star's lore as revealed (idempotent) and return
    `(lore_text, is_first_reveal)`.

    `is_first_reveal` is True only on the first call for this star —
    used by the scanner UI to play the canonical first-reveal cue
    and (Phase 5) auto-add a Bio-Archive entry.
    """
    text = star_lore_for(star, game)
    if text is None:
        return None, False
    key = star_key(star)
    flag = f"lore_revealed_star_{key}"
    is_first = not game.flags.get(flag)
    game.flags[flag] = True
    return text, is_first


def reveal_planet_lore(
    game: "Game", star: dict, planet_index: int,
) -> tuple[str | None, bool]:
    """Mark the planet's lore as revealed (idempotent) and return
    `(lore_text, is_first_reveal)`.
    """
    text = planet_lore_for(star, planet_index, game)
    if text is None:
        return None, False
    key = star_key(star)
    flag = f"lore_revealed_planet_{key}_{planet_index}"
    is_first = not game.flags.get(flag)
    game.flags[flag] = True
    return text, is_first
