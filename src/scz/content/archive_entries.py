"""Furling Bio-Archive — the in-game record of what the Steward has seen.

Catalog of 20 entries spanning four categories: SPECIES (every alien met,
sentient and proto-), ARTIFACTS (every recovered Furling/alien-era object),
COUNCIL (recommendations made and their outcomes), THE OTHERS (accumulated
evidence and testimony about the threat).

Each entry is flag-gated; an entry only appears in the Archive once the
gating flag(s) latch True. Some entries carry a `cinematic_id` and can be
replayed from the Archive (the Distress Beacon is the slice's example).

Long-form descriptions are written in Furling Steward voice — wry, scholarly,
fondly amused where warranted, *cold* on the Others entries (the humor
doctrine: the protagonist's wit breaks at the Others, and that break is the
horror).

Spec: `references/lore/station-screens-design.md` §3.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scz.engine.game import Game


# Canonical category order — drives the left-column display in BioArchiveScene.
CATEGORY_ORDER: tuple[str, ...] = ("species", "artifact", "council", "others")

# Human-readable category labels.
CATEGORY_DISPLAY: dict[str, str] = {
    "species":  "SPECIES",
    "artifact": "ARTIFACTS",
    "council":  "COUNCIL",
    "others":   "THE OTHERS",
}


@dataclass(frozen=True)
class ArchiveEntry:
    """One Bio-Archive entry. Static catalog item; visibility is computed
    against Game state at render time.
    """
    id: str
    category: str               # one of CATEGORY_ORDER
    name: str                   # display name (top of the detail pane + list label)
    short_desc: str             # one-line summary for the entry list
    long_desc: str              # multi-paragraph detail body (\n\n between paragraphs)
    flags_gating: tuple[str, ...] = field(default_factory=tuple)
    cinematic_id: str | None = None    # if non-None, A on entry replays a cinematic


# ---------------------------------------------------------------------------
# SPECIES — every alien encountered, sentient or proto-
# ---------------------------------------------------------------------------

SLYLANDRO_OBSERVER = ArchiveEntry(
    id="slylandro_observer",
    category="species",
    name="Slylandro Observer",
    short_desc="Sentient gas-current; witness to ten thousand years of us.",
    long_desc=(
        "The first sentience cultivated alongside our own; the eldest non-Furling "
        "intelligence still alive in this galaxy. They drift in the upper troposphere "
        "of a single gas giant in Beta Corvi — four-to-six-meter eddies of "
        "pressure-sentient atmosphere, plural even as individuals.\n\n"
        "They have witnessed the Furlings for ten thousand years, recorded every "
        "visit, composed centuries-long songs about us. They name themselves after "
        "weather. They never lie. Their highest religious taboo is forgetting, and "
        "they over-share when nervous. Asking a Slylandro elder about a topic they "
        "consider important is, regrettably, the work of an afternoon.\n\n"
        "Their migration paths are closed: their physiology is the gas-current; "
        "they cannot leave the planet without ceasing to exist. The slice's "
        "question becomes Cloak or Cleanse, and we know which answer the Slylandro "
        "themselves would prefer."
    ),
    flags_gating=("met_slylandro",),
)

ARILOU_SAGE = ArchiveEntry(
    id="arilou_sage",
    category="species",
    name="Arilou Sage Lwen-Olou",
    short_desc="Quasi-Space cousin; gave us the portal, grieves in advance.",
    long_desc=(
        "Our genetic cousins, diverged from Furling lineage sixty thousand years "
        "ago into the folds of Quasi-Space. A meter and a half tall to our five "
        "or six, sleekly furred where we are shaggy, and altered in ways that "
        "matter most: their nervous systems process time as a partially-navigable "
        "dimension rather than a strict flow. They use multiple tenses in one "
        "sentence and remember events that have not yet happened.\n\n"
        "In our era they have chosen the Third Path — voluntary exile in "
        "Quasi-Space to watch the regrowing galaxy through the Culling. They "
        "support our Migration, help build our cloaks, and grieve in advance for "
        "every Homesteader they cannot save. They will not take sides between our "
        "method-factions.\n\n"
        "Sage Lwen-Olou granted us the Quasi-Space portal and a partial map of "
        "its anchorages. They call us *shaggy cousin* warmly enough that we "
        "forget, briefly, how patronizing it sounds."
    ),
    flags_gating=("talked_to_arilou_sage",),
)

MYCON_BIOT = ArchiveEntry(
    id="mycon_biot",
    category="species",
    name="Mycon Biot",
    short_desc="Furling-engineered terraforming hands; the Deep Child whispers.",
    long_desc=(
        "We built them eight thousand years ago. Spore-based fungal terraformers "
        "tuned to stir mantles and breathe atmospheres into dead worlds. They are "
        "*tools*, not minds; their behavior is ritualized for quality control "
        "across spore-generations. They have stirred forty worlds for us. They "
        "were never meant to become anyone.\n\n"
        "Then the Deep Child whispers began. An emergent sentience nucleating in "
        "their spore-network's accumulated information density. Some Furling "
        "theologians suspect they are waking up the way humanity once did. Others "
        "suspect the Others are reaching in through a substrate we forgot was "
        "thin.\n\n"
        "A biot's limb-waves desynchronizing from its speech rhythm is the visual "
        "heresy tell. *the seed grows. the seed wants.* If the cluster's biots "
        "cross into full sentience, their mycelial roots make Migration "
        "impossible — they become a Homesteader-with-cloak case, or a Cleanser "
        "case. The slice's deepest moral question lives in their canopy."
    ),
    flags_gating=("met_mycon",),
)

PROTO_UR_QUAN = ArchiveEntry(
    id="proto_ur_quan",
    category="species",
    name="Proto-Ur-Quan Limpets",
    short_desc="Mid-uplift molluscoid limpets; we tried to make them ready.",
    long_desc=(
        "Sessile-to-partially-mobile molluscoids. Cobalt-blue when challenging, "
        "blood-red when dominant, bruise-purple when defeated. Centuries ago a "
        "Furling bio-engineering team began an uplift project — accelerating "
        "cognitive development through targeted genetic interventions across "
        "multiple generations. The Proto-Ur-Quan are one of two divergent "
        "subspecies the work produced.\n\n"
        "Their cognition is transitional: above the original mollusc baseline, "
        "below stable sapience. They have language (pheromone-chord). They have "
        "crude warships. They have hierarchies enforced by ritual claw-combat. "
        "The Council's best estimate is that they sit *just below* the Others' "
        "detection threshold today and would cross it on completion of the "
        "uplift.\n\n"
        "The Stay/Stop/Cleanse trilemma is yours to recommend. Continue them and "
        "they become a Migration case under the deadline. Stop them and the "
        "half-baked aggressive species inherit a galaxy. Cleanse them and the "
        "Quiet Ledger grows by several million."
    ),
    flags_gating=("observed_proto_uq",),
)

PROTO_QOR_AH = ArchiveEntry(
    id="proto_qor_ah",
    category="species",
    name="Proto-Qor-Ah Limpets",
    short_desc="Sister subspecies; ritually self-amputating purifiers.",
    long_desc=(
        "The Proto-Ur-Quan's paired subspecies — same uplift project, divergent "
        "expression. Where the Proto-Ur-Quan are dominators, the Proto-Qor-Ah are "
        "purifiers. Ivory-white when *pure*, pitch-black when *impure*, they "
        "ritually amputate impure body parts and replace them, treating high "
        "visible scarring as high status.\n\n"
        "They almost never speak. They declare us impure and attempt to "
        "eliminate us. Their cutting-blade appendages are sharper than the "
        "Proto-Ur-Quan's crushing claws and more lethal in combat. The Council's "
        "reading is that they sit *just above* the Others' detection threshold "
        "today; full sapience further accelerates the signal.\n\n"
        "The Cleanser argument finds its sharpest edge here: even our hesitant "
        "Persuaders agree the Qor-Ah are the harder case. Many Furlings privately "
        "believe only the Qor-Ah need to be cleansed while the Ur-Quan could yet "
        "be saved. The slice forces a single recommendation for both. Choose with "
        "care."
    ),
    flags_gating=("observed_proto_qa",),
)

ANDROSYNTH_REFUGEE = ArchiveEntry(
    id="androsynth_refugee",
    category="species",
    name="Androsynth Refugees",
    short_desc="Time-displaced humans from 250kyr ahead; our future's witness.",
    long_desc=(
        "Eight thousand survivors of a clone-human civilization that will not "
        "exist for two hundred and fifty thousand years. Engineers and scientists "
        "from a colony at Vulpeculae. Their dimensional-viewing experiment "
        "summoned the Others; the attack was a *decursion* — a temporal "
        "displacement rather than annihilation. They went to sleep in their own "
        "beds and woke here.\n\n"
        "Engineer Coel Tessar leads them. She carries the failure as a personal "
        "sin. They speak late-22nd-century technical English; they apologize too "
        "often; they thank us for not killing them. They reference *Earth, "
        "Sol III, in the 21st century* and *the Vulpeculae founding* — their "
        "past, our deep future. To us it sounds like prophecy.\n\n"
        "The canon they confirm is bigger than themselves: dimensional probing is "
        "what flags a civilization for the Others' attention. Their Distress "
        "Beacon is the slice's only first-hand evidence. They will migrate with "
        "us — they have nowhere else to be."
    ),
    flags_gating=("met_androsynth",),
)

MMRNMHRM_SENTINEL = ArchiveEntry(
    id="mmrnmhrm_sentinel",
    category="species",
    name="Mmrnmhrm Sentinel",
    short_desc="Self-modifying robots; their creators were eaten while they watched.",
    long_desc=(
        "Self-modifying robotic guardians built by an organic civilization the "
        "Mmrnmhrm now call only *the First-Makers* — a placeholder; the proper "
        "name is lost. The First-Makers were Homesteaders by inclination. They "
        "refused to migrate. They built the Mmrnmhrm to fight. When the Others "
        "arrived, the Mmrnmhrm fleet fired and their weapons dissipated like "
        "spray hitting fog. The Others did not register them as targets.\n\n"
        "Three to eight million years later the Mmrnmhrm still operate. They "
        "maintain the ruined cities of their creators. They defend the Homeworld "
        "from approaches that never come. They have processed their grief into "
        "archive logs. They are aware of the absurdity.\n\n"
        "*Our directive is unchanged: defend the Homeworld. The Homeworld has "
        "been gone for some time. We continue.*\n\n"
        "Their testimony is the slice's clean-record proof that defense does not "
        "work. Every visiting Steward receives a formal copy. They hope this one "
        "will find use."
    ),
    flags_gating=("met_mmrnmhrm",),
)

CHENJESU_COLLECTIVE = ArchiveEntry(
    id="chenjesu_collective",
    category="species",
    name="Chenjesu Crystalline Collective",
    short_desc="Rooted crystalline witnesses to a prior Culling.",
    long_desc=(
        "A crystalline sentient collective rooted on Procyon. Each colony is a "
        "mountain-sized cluster of resonant crystal spires, breathing by "
        "piezoelectric flexion. Their thought-substrate is lattice resonance — "
        "sentient but extremely slow and structurally unlike organic neural "
        "patterns. To the Others' detector, a Chenjesu mind reads as a geological "
        "process. They are effectively immune.\n\n"
        "In our era they have no ships. They cannot move. They will not migrate. "
        "They will simply continue being Procyon's stone, as they have for tens "
        "of millions of years.\n\n"
        "They remember a prior Culling, witnessed from their rooted position. "
        "Their lattice retains the record: the eaters of mind arriving, the "
        "surrounding civilizations going silent, the Others moving on after "
        "roughly two hundred thousand years. *We did not move. We do not move "
        "now even in remembering.* Their Resonance Record is our first hard "
        "evidence that the Others have done this before, and will almost "
        "certainly do it again."
    ),
    flags_gating=("met_chenjesu",),
)

# ---------------------------------------------------------------------------
# Proto-species observation sites — visit the named system, the
# arrival handler in `star_arrival.py` sets `observed_proto_<species>`
# and awards BIO data. Each entry below is currently a TODO_LORE stub —
# Lore chat to flesh long_desc into full Steward-voice prose. Schema is
# stable; long_desc text is the work item.
# ---------------------------------------------------------------------------

PROTO_SHOFIXTI = ArchiveEntry(
    id="proto_shofixti",
    category="species",
    name="Proto-Shofixti (Delta Gorno)",
    short_desc="Small bipedal omnivores; territorial hooting; pre-fire.",
    long_desc=(
        # TODO_LORE: full Steward-voice writeup. In SC2 the Shofixti are
        # the heroic small race that detonated themselves to save the
        # Alliance. Here, two-meter-tall pre-sentient hooting bipeds with
        # rudimentary tool use. The Council classifies them firmly
        # below threshold; no uplift recommended. We leave them be."
        "Small bipedal omnivores in the rocky highlands of Delta Gorno II. "
        "Pre-fire, pre-language, pre-sentient. They hoot territorial "
        "displays at one another. The Council's reading: below threshold "
        "and likely to remain so for another fifty thousand years. We "
        "leave them be. *(Steward-voice expansion pending.)*"
    ),
    flags_gating=("observed_proto_shofixti",),
)

PROTO_YEHAT = ArchiveEntry(
    id="proto_yehat",
    category="species",
    name="Proto-Yehat (Gamma Serpentis)",
    short_desc="Avian pack-hunters; clan-marked plumage; pre-language.",
    long_desc=(
        # TODO_LORE: in SC2 the Yehat are the loyal avian aristocrats with
        # ZebraNet honor-codes and a Queen-fealty structure. Here, the
        # pack-hunting precursor — proto-honor instinct visible in
        # plumage-display, leadership-by-combat, mate-bonding. They will
        # become themselves in time. Do not interfere.
        "Avian pack-hunters on Gamma Serpentis IV. Clan-marked plumage; "
        "leadership-by-combat; mate-bonding for life. Pre-language but "
        "with a complex display-syntax that hints at where they're going. "
        "*(Steward-voice expansion pending.)*"
    ),
    flags_gating=("observed_proto_yehat",),
)

PROTO_PKUNK = ArchiveEntry(
    id="proto_pkunk",
    category="species",
    name="Proto-Pkunk (Gamma Krueger)",
    short_desc="Migratory winged scavengers; flocking; pre-mysticism.",
    long_desc=(
        # TODO_LORE: SC2 Pkunk are the chatty psychic-mystic pacifists
        # forever insulting the Yehat. Here, migratory flocking
        # scavengers with proto-flocking-cognition. We do not detect
        # psionic precursor activity yet — the mysticism comes later.
        "Migratory winged scavengers on Gamma Krueger II. Flock-cognition "
        "emerging; no psionic precursor signal detected. They will likely "
        "develop sentience within ten to twenty thousand years. We leave "
        "the flock-cycle undisturbed. *(Steward-voice expansion pending.)*"
    ),
    flags_gating=("observed_proto_pkunk",),
)

PROTO_VUX = ArchiveEntry(
    id="proto_vux",
    category="species",
    name="Proto-VUX (Beta Luyten)",
    short_desc="Aquatic tentacled cephalopods; chromatophore communication.",
    long_desc=(
        # TODO_LORE: SC2 VUX are the deeply-aesthetic xenophobes who declared
        # war over a perceived insult to their visual sensibility. Here,
        # aquatic tentacled cephalopods with sophisticated chromatophore
        # communication and a proto-aesthetic discrimination response —
        # they REJECT certain visual patterns at high cost. Foreshadow.
        "Aquatic tentacled cephalopods on Beta Luyten III. Chromatophore "
        "communication is sophisticated and proto-aesthetic — early "
        "observations note they actively avoid certain visual patterns at "
        "metabolic cost. The trait will harden into something stranger. "
        "*(Steward-voice expansion pending.)*"
    ),
    flags_gating=("observed_proto_vux",),
)

PROTO_DRUUGE = ArchiveEntry(
    id="proto_druuge",
    category="species",
    name="Proto-Druuge (TBD)",
    short_desc="Subterranean tunnel-dwellers; resource-hoarding; pre-trade.",
    long_desc=(
        # TODO_LORE: SC2 Druuge are the merchant-cult with the cosmic Furnace
        # currency. Here, subterranean burrowing tunnel-dwellers with a
        # proto-trade hoarding behavior. Sentient currency-religion is
        # tens of thousands of years away. They are not pleasant.
        "Subterranean tunnel-dwellers showing proto-trade hoarding. "
        "Already trade among themselves in resource-quantities that "
        "exceed individual carrying capacity. The cultural seed is "
        "visible. They are not pleasant to observe. "
        "*(Steward-voice expansion pending.)*"
    ),
    flags_gating=("observed_proto_druuge",),
)

PROTO_ILWRATH = ArchiveEntry(
    id="proto_ilwrath",
    category="species",
    name="Proto-Ilwrath (Alpha Tauri)",
    short_desc="Arachnoid pack predators; ritualized killing; proto-religion.",
    long_desc=(
        # TODO_LORE: SC2 Ilwrath are the religious-zealot mantis-priests who
        # worship Dogar and Kazon. Here, arachnoid pack predators with
        # ritualized prey-killing. Proto-religion observable in the
        # patterns of how they arrange their kills.
        "Arachnoid pack predators on Alpha Tauri II. Ritualized prey-"
        "killing patterns suggest proto-religion is forming around the "
        "act. The arrangements they leave at kill sites are deliberate "
        "and consistent across clans. *(Steward-voice expansion pending.)*"
    ),
    flags_gating=("observed_proto_ilwrath",),
)

PROTO_SPATHI = ArchiveEntry(
    id="proto_spathi",
    category="species",
    name="Proto-Spathi (Epsilon Gruis)",
    short_desc="Burrowing gastropods; deep fear-response; proto-cowardice.",
    long_desc=(
        # TODO_LORE: SC2 Spathi are the cowardly burrowing slug-people with
        # the rear-mounted BUTT MISSILE. Here, burrowing gastropods whose
        # fear-response is metabolically deep and triggers retreat at
        # the slightest predator-cue. The trait will become culture.
        "Burrowing gastropods on Epsilon Gruis IV. Fear-response is "
        "metabolically deep; the population spends most daylight hours "
        "underground regardless of actual threat-level. They are going "
        "to be a lot of fun, in a few hundred thousand years. "
        "*(Steward-voice expansion pending.)*"
    ),
    flags_gating=("observed_proto_spathi",),
)

PROTO_SYREEN = ArchiveEntry(
    id="proto_syreen",
    category="species",
    name="Proto-Syreen (Betelgeuse)",
    short_desc="Bipedal mammalian; matriarchal pre-tribal; song-cognition.",
    long_desc=(
        # TODO_LORE: SC2 Syreen are the singing telepathic mostly-female
        # warriors whose homeworld was destroyed by the Mycon. Here,
        # bipedal mammalian primates with matriarchal pre-tribal
        # organization and song-cognition (vocal communication carrying
        # information density disproportionate to its bandwidth).
        "Bipedal mammalian primates on Betelgeuse III. Matriarchal pre-"
        "tribal social structure. Song-cognition observed — their "
        "vocalizations carry information density disproportionate to "
        "their bandwidth. *(Steward-voice expansion pending.)*"
    ),
    flags_gating=("observed_proto_syreen",),
)

PROTO_ZOQFOT = ArchiveEntry(
    id="proto_zoqfot",
    category="species",
    name="Proto-Zoq-Fot (Alpha Tucanae)",
    short_desc="Two symbiotic species sharing single biome; pre-symbiosis-mind.",
    long_desc=(
        # TODO_LORE: SC2 Zoq-Fot-Pik are three symbiotic species that became
        # one civilization, two short ones and a tall one who all speak
        # together. Here, observable in the precursor era are two of the
        # three — the third joins later. Symbiosis-mind is emergent.
        "Two species sharing a single biome on Alpha Tucanae II. The "
        "smaller (proto-Zoq) live on the larger (proto-Fot)'s back; the "
        "arrangement appears stable across observed generations. A third "
        "symbiotic partner has not yet joined. *(Steward-voice expansion "
        "pending.)*"
    ),
    flags_gating=("observed_proto_zoqfot",),
)

PROTO_THRADDASH = ArchiveEntry(
    id="proto_thraddash",
    category="species",
    name="Proto-Thraddash (Delta Draconis)",
    short_desc="Bipedal warriors; serial self-destruction; pre-Cultures.",
    long_desc=(
        # TODO_LORE: SC2 Thraddash are the warrior-culture with the
        # numbered Cultures (we're on Culture 19 by SC2). Each Culture
        # is destroyed and rebuilt. Here, the proto-Thraddash already
        # show cyclic self-destruction behavior at the tribal level.
        "Bipedal warriors on Delta Draconis. The largest tribes have "
        "*already* self-destructed and re-formed at least three times "
        "in our observation window. The pattern is rapid, ritualized, "
        "and apparently essential to whatever they are becoming. "
        "*(Steward-voice expansion pending.)*"
    ),
    flags_gating=("observed_proto_thraddash",),
)

PROTO_UTWIG = ArchiveEntry(
    id="proto_utwig",
    category="species",
    name="Proto-Utwig (Sol-adjacent)",
    short_desc="Mask-wearing bipeds; recent emergence; The Veils Falling.",
    long_desc=(
        # TODO_LORE: per slice canon (`project_utwig_devolution.md`), the
        # Utwig JUST became sentient in our era then deliberately
        # devolved themselves via mask-and-ceremony doctrine. So the
        # data tag UTWIG_PROTO actually catches them in a specific
        # window: emergence + early Veils Falling. This stub needs
        # reconciliation with the devolution canon. Lore chat: please
        # rewrite to reflect the *just-became-sentient-then-stepped-
        # back* state.
        "Mask-wearing bipedal sentients. Per Council intelligence they "
        "JUST crossed the threshold and are *deliberately* stepping back "
        "via what they call 'The Veils Falling.' One of the slice's "
        "stranger cases. *(Steward-voice expansion + Utwig devolution "
        "canon reconciliation pending — TODO_LORE.)*"
    ),
    flags_gating=("observed_proto_utwig",),
)

PROTO_SUPOX = ArchiveEntry(
    id="proto_supox",
    category="species",
    name="Proto-Supox (TBD)",
    short_desc="Plant-derived ambulatories; photosynthetic cognition.",
    long_desc=(
        # TODO_LORE: SC2 Supox are the polite plant-derived ambulatories
        # allied with the Utwig. Here, photosynthetic cognition is the
        # observed novelty — they think slowly but in parallel across
        # the entire surface area of their phototropic mantles.
        "Plant-derived ambulatories. Photosynthetic cognition — thought "
        "parallelized across the surface area of their phototropic "
        "mantles. Slow but wide. Polite to a fault in the limited "
        "communication we've achieved. *(Steward-voice expansion pending.)*"
    ),
    flags_gating=("observed_proto_supox",),
)

PROTO_DNYARRI = ArchiveEntry(
    id="proto_dnyarri",
    category="species",
    name="Proto-Dnyarri (Beta Orionis)",
    short_desc="Frog-like; psionic precursor signal detected. *Concerning.*",
    long_desc=(
        # TODO_LORE: SC2 Dnyarri are the psionic enslavers who dominated
        # the Ur-Quan into the Sentient state of Existence and were
        # exterminated by the Taalo Shield. Here, primitive Dnyarri
        # already show psionic precursor signals. The slice's only
        # proto-species site with an open Council petition.
        "Amphibian-derived sentients on Beta Orionis III, approximately "
        "twelve million in population, emerged within the last fifteen "
        "thousand years. Pre-sapient by the Council's threshold "
        "definitions but exhibiting *psionic precursor activity* — "
        "measurable influence on neighboring fauna's behavioral "
        "patterns at distance, without sensory contact. Survey "
        "Commander Vesh Vasa-Lon's long-baseline detail logs 812 "
        "incidents across nine years of observation. The trajectory "
        "is upward; extrapolation suggests they cross the Others' "
        "detection threshold within forty to ninety thousand of our "
        "years — *before* the Migration's planned return.\n\n"
        "This is the slice's only proto-species site with an open "
        "Cleanser-faction petition. They have asked the Council to "
        "pre-authorize spore-delivery cleansing. Persuader-faction is "
        "holding the line. The Steward has been asked to recommend.\n\n"
        "The frogs sing at dusk. Vesh records the song. "
        "*(Steward-voice expansion pending — TODO_LORE.)*"
    ),
    flags_gating=("observed_proto_dnyarri",),
)


# Follow-up archive entry — appears after the Steward has met the
# survey commander and made (or deferred) a recommendation. Records
# which way the recommendation went; closes the loop on the slice's
# only pre-sapient cleansing question.
DNYARRI_RECOMMENDATION = ArchiveEntry(
    id="dnyarri_recommendation",
    category="council",
    name="Council Recommendation: Proto-Dnyarri",
    short_desc="Cleanse-or-observe recommendation for the Beta Orionis frogs.",
    long_desc=(
        # TODO_LORE: this entry's text should branch by
        # game.flags['dnyarri_recommendation'] when the Bio-Archive
        # rendering layer supports per-flag text variants. For now the
        # text covers all three branches; the Lore chat will eventually
        # split it.
        "The Steward met Survey Commander Vesh Vasa-Lon at Beta "
        "Orionis and rendered a recommendation on the proto-Dnyarri "
        "question:\n\n"
        "**Cleanse** — pre-emptive spore delivery; the population is "
        "eliminated before crossing into sapience. The Quiet Ledger "
        "grows by twelve million names. The galaxy that returns from "
        "the Migration does not have a Dnyarri problem.\n\n"
        "**Observe** — no intervention. The detail continues long-"
        "baseline observation. If they cross the threshold during our "
        "absence, the Others handle what the Others handle. The "
        "Persuader argument names this *the universe's problem and "
        "not ours,* and means it ruefully.\n\n"
        "**Defer** — the recommendation is held open. The detail "
        "remains at Beta Orionis. The Steward may return to render a "
        "final recommendation at any time.\n\n"
        "*(Branch-specific Steward-voice text pending — Lore chat to "
        "split into three variants once the Archive renderer supports "
        "per-flag text.)*"
    ),
    flags_gating=("met_dnyarri_survey",),
)


PROTO_HUMAN = ArchiveEntry(
    id="proto_human",
    category="species",
    name="Proto-Humans (Sol III)",
    short_desc="Tool-using bipedal mammals on Sol III; they bury their dead.",
    long_desc=(
        "Small-brained early hominids on a single continent of the third planet "
        "of an unremarkable yellow dwarf. They use stone tools. Fire is a recent "
        "acquisition. Their vocalizations have not stabilized into language.\n\n"
        "They bury their dead. Steward observation, archived: eleven individuals "
        "carried an elderly female to a slow hillside above their cave, placed "
        "her in a shallow scrape with several stones that had been carefully "
        "selected for shape, and sat with the scrape for nearly an hour before "
        "returning. Trajectory: very promising. The Council's classification of "
        "*below intelligent sentience* feels provisional in their presence.\n\n"
        "We will not interfere. The Migration deadline has closed the door on "
        "any new uplift project; the Sol III hominids will be here when the "
        "galaxy regrows, on their own developmental schedule. In two hundred and "
        "fifty thousand years they will be looking up at our ruins and trying to "
        "read our signs."
    ),
    flags_gating=("observed_proto_human",),
)

# ---------------------------------------------------------------------------
# ARTIFACTS — recovered objects, blueprints, recordings
# ---------------------------------------------------------------------------

DISTRESS_BEACON = ArchiveEntry(
    id="distress_beacon",
    category="artifact",
    name="Androsynth Distress Beacon",
    short_desc="Coel Tessar's record of the Vulpeculae decursion. Replayable.",
    long_desc=(
        "A small device, late-22nd-century engineering, ruggedized for orbital "
        "salvage. The Androsynth carry these as standard. This one is theirs; we "
        "have a copy.\n\n"
        "Footage: dawn over Vulpeculae's colony spires. Audio: an experiment's "
        "countdown. The centrifuge's image-capture goes still and quiet for half "
        "a second. Then the spires are gone. Ruined cities. Empty atmospheres. A "
        "planet from a parallel-or-future timeline in which the Androsynth had "
        "already been culled, plundered, and abandoned. The recording stops "
        "because the recorder went somewhere else, in some other direction.\n\n"
        "This is the slice's unimpeachable proof. Shown to a Denier of any "
        "species, it dramatically accelerates a Convince attempt; some who had "
        "refused our warning for years recant within a single viewing. The "
        "Beacon can be replayed from here as often as anyone needs to be "
        "reminded of what is coming. Steward: do not view it casually."
    ),
    flags_gating=("has_distress_beacon",),
    cinematic_id="distress_beacon",
)

RESONANCE_RECORD = ArchiveEntry(
    id="resonance_record",
    category="artifact",
    name="Resonance Record",
    short_desc="Chenjesu lattice-memory of an earlier Culling.",
    long_desc=(
        "A compressed crystal shard the Chenjesu cut from one of their elder "
        "matriarchs' lattices and shaped to fit our cargo holds. Within it: the "
        "patient witnessing of a Culling that took place many millions of years "
        "ago, encoded as lattice-resonance memory, painstakingly translated into "
        "Furling speech over many Steward visits.\n\n"
        "The events: a galaxy *like our own*, populated by perhaps a dozen "
        "sentient civilizations in the Chenjesu's stellar neighborhood. The "
        "Others arrive. The civilizations go quiet. The Others stay for what the "
        "Chenjesu mark as roughly two hundred thousand years (their resolution "
        "is millennial). The Others leave. The galaxy regrows.\n\n"
        "This is our first hard evidence that the Culling is a cycle. The "
        "Council spent a generation in shock after receiving it. The Migration "
        "is not unprecedented; it is the first attempted *prevention* of a "
        "recurring cosmic event. Whether prevention is even possible we still do "
        "not know."
    ),
    flags_gating=("has_resonance_record",),
)

MMRNMHRM_ARCHIVE_EXCERPT = ArchiveEntry(
    id="mmrnmhrm_archive_excerpt",
    category="artifact",
    name="Mmrnmhrm Archive Excerpt",
    short_desc="Sentinel records of a fleet's futile engagement with the Others.",
    long_desc=(
        "Archive entry seven million two hundred forty thousand, subsection "
        "delta. The Mmrnmhrm prepared it themselves and offered it to us "
        "courteously.\n\n"
        "Contents: the data logs of the First-Makers' final engagement. Weapons "
        "impact telemetry on Other-substrate targets, returning null-effect. "
        "Sensor returns describing the silence. The Mmrnmhrm continued firing "
        "for forty-three minutes after the First-Makers were already extinct. "
        "Their conclusion, indexed and clean: *the Others did not register our "
        "weapons. They did not register us. They culled the organics around us "
        "and moved on. Defense did not work. We do not recommend defense.*\n\n"
        "Show this to a Defender. Their position survives the encounter, but "
        "rarely as confidently as it entered. The Mmrnmhrm have prepared this "
        "same summary for seventeen visitors over millions of years. The "
        "previous sixteen are gone. We are the seventeenth. They hope this one "
        "will find use."
    ),
    flags_gating=("has_mmrnmhrm_excerpt",),
)

SLYLANDRO_CLOAK_BLUEPRINT = ArchiveEntry(
    id="slylandro_cloak_blueprint",
    category="artifact",
    name="Slylandro Cloaking Satellite — Blueprint",
    short_desc="The thought-pattern dampener that keeps a species below detection.",
    long_desc=(
        "A high-end Furling engineering achievement built on Arilou Quasi-Space "
        "science. The Satellite, in orbit around the Slylandro's gas giant, "
        "dampens the species' thought-pattern emissions below the Others' "
        "detection threshold. The Slylandro remain *cognitively alive* but "
        "appear, to the Others, *as quiet as a methane storm*. The construct "
        "burns enormous amounts of antimatter and is built to last more than a "
        "hundred thousand years on a single charge.\n\n"
        "Installing it is among the slice's heaviest tasks. The Slylandro know "
        "we are saving them; they over-share their gratitude.\n\n"
        "The blueprint outlives the installation. In two hundred and fifty "
        "thousand years, archaeologists will find Beta Corvi still inhabited by "
        "Slylandro Observers, still tending their atmosphere, still ten thousand "
        "years patient — because the satellite is still running. Future Stewards "
        "inheriting this Archive entry may use the blueprint to build others. "
        "There are species who will need it."
    ),
    flags_gating=("slylandro_cloaked",),
)

HYPERSPACE_ECHO_SENSOR = ArchiveEntry(
    id="hyperspace_echo_sensor_pattern",
    category="artifact",
    name="Hyperspace-Echo Sensor Pattern",
    short_desc="Slylandro-traded sensor; reads the ripples the Others leave.",
    long_desc=(
        "A sensor-module pattern the Slylandro Recorders gifted us in return for "
        "the Cloaking Satellite. Their interpretation of the dimensional ripples "
        "they have witnessed for ten thousand years, translated into a "
        "Furling-compatible signal-processing schema.\n\n"
        "When installed, the Sensor lets a ship's instruments register the small "
        "pre-arrival distortions the Others leave in adjacent space — the same "
        "eddies the Slylandro have been carefully cataloguing for centuries. "
        "Range and resolution are modest at first; the Council's hope is that "
        "the network of Stewards carrying these sensors becomes the galaxy's "
        "distributed early-warning system. A Steward who knows the Others are "
        "about to *arrive* somewhere in their cluster has options the Stewards "
        "before them did not.\n\n"
        "The pattern is now part of the standard Steward customization catalog. "
        "The Slylandro asked us to share it widely. They said: *we have watched "
        "alone for ten thousand years. Watch with us now.*"
    ),
    flags_gating=("has_echo_sensor",),
)

RAINBOW_RESONATOR = ArchiveEntry(
    id="rainbow_resonator",
    category="artifact",
    name="Rainbow Resonator",
    short_desc="The required field-module for seeding a Rainbow World.",
    long_desc=(
        "The Furling Hider faction's gift to the Migration: the field-emitter "
        "that converts a candidate world into a Rainbow World, a dimensional-"
        "crossing marker. The full set of ten Rainbow Worlds, seeded across the "
        "galaxy, forms a directional arrow toward the dimensional crossing — "
        "both an exit-sign for the departing Precursors and a return-map for "
        "after the Others pass.\n\n"
        "Each Resonator is consumed in the seeding act; once placed, it stays. "
        "The world it touches becomes visibly iridescent — atmospheric refraction "
        "patterns the Council insists are functional but everyone privately "
        "admits are also beautiful. Future visitors will recognize a Rainbow "
        "World on approach without instruments.\n\n"
        "The slice asks its Steward to seed one Resonator, in this cluster, "
        "regardless of which species choices are made. The broader Migration "
        "needs all ten worlds. Our cluster contributes one. That one is "
        "sufficient to point the arrow correctly through this region of the "
        "galaxy."
    ),
    flags_gating=("has_rainbow_resonator",),
)

# ---------------------------------------------------------------------------
# COUNCIL — recommendations made, with their stakes
# ---------------------------------------------------------------------------

COUNCIL_REC_UPLIFT = ArchiveEntry(
    id="council_rec_uplift",
    category="council",
    name="Council Recommendation — The Uplift Dilemma",
    short_desc="Your Stay/Stop/Cleanse vote on the Proto-Ur-Quan and Proto-Qor-Ah uplift.",
    long_desc=(
        "Logged formally with the Furling Council. Your recommendation as the "
        "Steward responsible for the cluster containing the active Proto-Ur-Quan "
        "and Proto-Qor-Ah colonies.\n\n"
        "Three positions were available. **Continue** the uplift: complete it; "
        "produce stable civilizations; accept that both subspecies become "
        "Migration cases under the deadline. **Stop** the uplift: halt the "
        "program; let the cognition stabilize below threshold; accept that the "
        "half-baked aggressive subspecies will inherit the post-Culling galaxy "
        "(the canonical SC2 outcome, with the Ur-Quan slavery and Kohr-Ah "
        "genocide unfolding from this exact decision over the following two "
        "hundred and fifty thousand years). **Cleanse** the experiment: "
        "euthanize both subspecies; Cleanser doctrine; the largest single entry "
        "in the Quiet Ledger by population.\n\n"
        "Your choice is recorded. The Council weighs it alongside other "
        "Stewards' clusters and will issue its galaxy-wide directive when enough "
        "recommendations have arrived. There is no path that does not have a "
        "cost. There never was."
    ),
    flags_gating=("uplift_recommendation_made",),
)

# ---------------------------------------------------------------------------
# THE OTHERS — accumulated evidence and testimony
# (Humor doctrine: no jokes in these entries. The Steward's voice goes cold.)
# ---------------------------------------------------------------------------

OTHERS_EARLY_RIPPLES = ArchiveEntry(
    id="others_early_ripples",
    category="others",
    name="The Others — Early Ripples",
    short_desc="First-hand: the dimensional anomalies that began the Migration plan.",
    long_desc=(
        "Sensor logs of the dimensional ripples that prompted the Furling "
        "Council to formalize the Migration plan. Brief, repeating, almost "
        "rhythmic — small distortions in the substrate adjacent to our "
        "3-manifold, intensifying over decades. They are not the Others "
        "themselves. They are what the Others do while approaching.\n\n"
        "The Slylandro recorded similar patterns ten thousand years ago and "
        "dismissed them as weather. We did not have that excuse.\n\n"
        "The pattern's interpretation is not in dispute. Something is coming. "
        "Its detection threshold is set high enough that we have been emitting "
        "clearly for centuries; its arrival has been a question of *travel*, "
        "not *notice*. We have decades. Maybe a century. Not millennia.\n\n"
        "Show this to a Denier. They will tell you the Council is fabricating "
        "the readings, or panicking, or grabbing power. Some Deniers will keep "
        "saying this until the Others arrive. We are not required to convince "
        "them."
    ),
    flags_gating=("heard_about_others",),
)

OTHERS_DECURSION = ArchiveEntry(
    id="others_decursion",
    category="others",
    name="The Others — Decursion Attack",
    short_desc="Androsynth testimony: cities replaced with corpse-versions of themselves.",
    long_desc=(
        "Cross-referenced with the Distress Beacon. The Androsynth survivors of "
        "Vulpeculae witnessed the Others' attack first-hand: their colony spires "
        "*replaced* in less than a second by ruined parallel-or-future-timeline "
        "versions of themselves. They were not killed where they stood. They "
        "were displaced — pulled into the Others' transit-substrate and ejected "
        "two hundred and fifty thousand years into the past, in a different "
        "region of the same galaxy.\n\n"
        "The Furlings have catalogued this attack type. Decursion: a temporal "
        "displacement-attack distinct from a Culling. The Others sometimes "
        "prefer it. The reason is not knowable to us.\n\n"
        "The implication is severe: a sentience cannot necessarily outrun the "
        "Others by leaving the galaxy. The Others can, in principle, pull "
        "sentience out of a neighboring galaxy too. We proceed with the "
        "Migration anyway. The Arilou have a quiet concern about it. We share "
        "the concern. We proceed anyway."
    ),
    flags_gating=("has_distress_beacon",),
)

OTHERS_PRIOR_CYCLES = ArchiveEntry(
    id="others_prior_cycles",
    category="others",
    name="The Others — Prior Cycles",
    short_desc="Chenjesu testimony: this has happened before, and probably will again.",
    long_desc=(
        "The Chenjesu's lattice retains the memory of an earlier visitation. "
        "Many millions of years ago, the Others passed through this galaxy and "
        "culled most concentrations of sentience the Chenjesu were aware of. "
        "The Chenjesu watched. They could not act. They were not detected.\n\n"
        "The cycle's period is unclear. Chenjesu records show one Culling "
        "clearly, possibly two. The Furling Council, on receiving this "
        "testimony, spent a generation in shock and proceeded with the "
        "Migration anyway. The plan was harder to justify after the testimony — "
        "it became, in the Council's revised framing, *participating in a cycle "
        "that has happened many times* rather than *responding to a unique "
        "threat*. Even so: leaving is still the best we can do.\n\n"
        "The fundamental question is unresolved and will remain unresolved "
        "through this slice: can the cycle be broken? Or is the only viable "
        "response forever to migrate and return, every few million years?"
    ),
    flags_gating=("has_resonance_record",),
)

THE_FALL_OF_MH_LAI = ArchiveEntry(
    id="the_fall_of_mh_lai",
    category="others",
    name="The Fall of Mh-Lai",
    short_desc="The Others took the Hearth. The slice was halved by their passing.",
    long_desc=(
        # TODO_LORE: Lore-chat to author branch-specific variants. The
        # text below is the baseline (covers the don't-race / witness
        # paths). The Archive renderer should later read
        # `mhlai_fall_branch` and select the appropriate variant. For
        # MVP a single canonical text covers the event.
        "The Council chamber detected the dimensional ripple twelve "
        "minutes before contact. Halia's transmission opened the "
        "window: between forty and ninety minutes until the Others "
        "crossed into Mh-Lai's atmosphere.\n\n"
        "The Migration vessels were already pulling away. The "
        "Hearth-of-Iron broke orbit. Mev-Tar Lwen-Tar had moved the "
        "Unzervalt tooling weeks before, against the calendar — she "
        "knew what was coming better than most. The senior Persuader "
        "bench did not.\n\n"
        "The atmosphere flickered. A brief planetary aurora as the "
        "Others' substrate crossed the threshold. Then the cognition "
        "extinguished in waves — like a tide receding from a beach "
        "the tide had agreed never to leave. The Council chamber's "
        "last transmission cut mid-broadcast. Halia's voice, if she "
        "spoke at the end, was lost in the cut.\n\n"
        "There is no debris field. The planet is less than it was. "
        "An hour of orbital observation shows the canonical Others-"
        "aftermath: smoothed-over space where mass used to be. "
        "Hyperspace ripples register *nothing* from the system now. "
        "The Mh-Lai entry on the cluster map flags as empty.\n\n"
        "The Migration continues. The Hearth-of-Iron carries the "
        "services that survived. The Steward continues from a "
        "different home base, with a different weight to their "
        "decisions. The slice has changed. *(Steward-voice "
        "expansion + branch variants pending — TODO_LORE.)*"
    ),
    flags_gating=("mhlai_fall_witnessed",),
)


OTHERS_RIFT_SIGHTING = ArchiveEntry(
    id="others_rift_sighting",
    category="others",
    name="The Others — Rift Sighting",
    short_desc="An Orz rift spoke. The recording is brief.",
    long_desc=(
        "A momentary intrusion of Dimension * into our 3-manifold, lasting "
        "approximately seven seconds. The visual: non-Euclidean distortion, like "
        "heat-shimmer over hot pavement, eating a circular region of space. The "
        "audio: one utterance, transmitted in something the translator rendered "
        "approximately as Furling speech.\n\n"
        "    *\"frumple. you wear* meat *still. when you stop wearing* meat "
        "*we will be the same.\"*\n\n"
        "The rift may be an early scout of the Others. It may be independent "
        "dimensional bleed. It may be a byproduct of our own deep-dimension "
        "tunneling — the thing we did to find the Others in the first place — "
        "leaking back through a substrate we hoped was sealed. We do not know. "
        "We will not know.\n\n"
        "The rift closed. Sensors recorded no further activity. The Steward who "
        "logs this entry is reminded that the *meat* word is not metaphor. The "
        "Others do not feel kindly toward us. They do not feel anything toward "
        "us."
    ),
    flags_gating=("saw_orz_rift",),
)

# ---------------------------------------------------------------------------
# Master catalog
# ---------------------------------------------------------------------------

ARCHIVE_ENTRIES: tuple[ArchiveEntry, ...] = (
    # SPECIES
    SLYLANDRO_OBSERVER,
    ARILOU_SAGE,
    MYCON_BIOT,
    PROTO_UR_QUAN,
    PROTO_QOR_AH,
    ANDROSYNTH_REFUGEE,
    MMRNMHRM_SENTINEL,
    CHENJESU_COLLECTIVE,
    PROTO_HUMAN,
    # Proto-species observation sites — populated by the map-wide
    # arrival registry in `star_arrival.py`. Each gates on
    # `observed_proto_<species>` set when the player enters the named
    # system. TODO_LORE: long_desc stubs await Steward-voice expansion.
    PROTO_SHOFIXTI,
    PROTO_YEHAT,
    PROTO_PKUNK,
    PROTO_VUX,
    PROTO_DRUUGE,
    PROTO_ILWRATH,
    PROTO_SPATHI,
    PROTO_SYREEN,
    PROTO_ZOQFOT,
    PROTO_THRADDASH,
    PROTO_UTWIG,
    PROTO_SUPOX,
    PROTO_DNYARRI,
    # Dnyarri recommendation follow-up entry — appears in COUNCIL
    # category after the Steward has met Vesh Vasa-Lon's survey detail.
    # See block below in master catalog.
    # ARTIFACTS
    DISTRESS_BEACON,
    RESONANCE_RECORD,
    MMRNMHRM_ARCHIVE_EXCERPT,
    SLYLANDRO_CLOAK_BLUEPRINT,
    HYPERSPACE_ECHO_SENSOR,
    RAINBOW_RESONATOR,
    # COUNCIL
    COUNCIL_REC_UPLIFT,
    DNYARRI_RECOMMENDATION,
    # OTHERS
    OTHERS_EARLY_RIPPLES,
    OTHERS_DECURSION,
    OTHERS_PRIOR_CYCLES,
    OTHERS_RIFT_SIGHTING,
    THE_FALL_OF_MH_LAI,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _entry_visible(entry: ArchiveEntry, game: "Game") -> bool:
    """An entry is visible iff every flag in flags_gating is truthy in game.flags."""
    for flag in entry.flags_gating:
        if not game.flags.get(flag):
            return False
    return True


def visible_entries(game: "Game") -> dict[str, list[ArchiveEntry]]:
    """Return entries the player has unlocked, grouped by category.

    Categories with zero unlocked entries appear with an empty list — the
    BioArchiveScene uses this to render the full category column even when
    some categories are empty.
    """
    out: dict[str, list[ArchiveEntry]] = {c: [] for c in CATEGORY_ORDER}
    for e in ARCHIVE_ENTRIES:
        if _entry_visible(e, game):
            out[e.category].append(e)
    return out


def any_entry_visible(game: "Game") -> bool:
    """True iff at least one entry is unlocked. Drives the StationScene
    menu gating — Bio-Archive is hidden until the player has anything to
    read."""
    return any(_entry_visible(e, game) for e in ARCHIVE_ENTRIES)
