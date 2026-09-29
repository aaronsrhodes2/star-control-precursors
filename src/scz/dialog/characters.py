"""Character data: state graphs for each NPC the player talks to.

For Phase 2 + 3 we hand-author the FSM and canned text. When the LLM
renderer lands (Phase 3.5), the npc_text strings become the "intent" passed
to the LLM and the LLM produces the actual phrasing from a per-character
voice prompt. The FSM and choice categories stay deterministic.
"""

from __future__ import annotations

from typing import Any

from scz.dialog.articulation import (
    BIPEDAL_HUMANOID,
    COMPOSITE_CLOUD,
    FLOATING_DRONE,
    GASBAG_TENDRIL,
)
from scz.dialog.data import (
    BackgroundSpec,
    DialogChoice,
    DialogCharacter,
    DialogState,
    build_state_dict,
)


# Reusable dialog backgrounds. Each one is generated once (16:9 vertical or
# 2:3) and shared across the characters that fit the scene. When a
# character has multiple backgrounds the dialog scene picks the first
# for now; the future variation layer will rotate by encounter context.
BG_FURLING_BRIDGE = BackgroundSpec(
    name="furling_bridge",
    image_path="assets/generated_drafts/firefly/tier1_dialog_backgrounds/bg_furling_bridge.png",
    description="The bridge of a Furling Scout-class ship — your home base in conversation.",
)
BG_PLANET_SURFACE = BackgroundSpec(
    name="planet_surface",
    image_path="assets/generated_drafts/firefly/tier1_dialog_backgrounds/bg_planet_surface.png",
    description="An alien planet surface viewed at chest height.",
)
BG_ALIEN_SHIP = BackgroundSpec(
    name="alien_ship",
    image_path="assets/generated_drafts/firefly/tier1_dialog_backgrounds/bg_alien_ship.png",
    description="An alien audience-chamber interior (organic-tech architecture).",
)
BG_OPEN_SPACE = BackgroundSpec(
    name="open_space",
    image_path="assets/generated_drafts/firefly/tier1_dialog_backgrounds/bg_open_space.png",
    description="Open void viewed through a Furling viewport.",
)


# ---------------------------------------------------------------------------
# Side effect helpers — used by DialogChoice.side_effect.
# ---------------------------------------------------------------------------

def _grant_quasispace_portal(game: Any) -> None:
    """The Sage's gift: a portal spawner + portal map. Sets the flag the
    HyperspaceScene reads to enable the Y-button portal opener.

    SCHEMATIC SIDE-EFFECT (audit 2026-05-18): per
    `references/lore/economy-and-trade-loops.md`, Sage Lwen-Olou
    slips the Arilou Phase Dampener schematic into the manifest
    silently during the QS-portal gifting. Canonical Arilou register:
    *the Sage did not announce it; the schematic appeared in the
    manifest after the meeting.*
    """
    game.flags["has_quasispace_portal"] = True
    if not hasattr(game, "schematics") or game.schematics is None:
        game.schematics = set()
    game.schematics.add("schematic_arilou_phase_dampener")
    # Sensor reward — Arilou Portal Pathfinder. Sage extends the QS
    # gift by transposing portal-network mapping into the Scout's
    # hyperspace scanner. Pre-reveals undiscovered portals.
    game.uninstalled_modules["arilou_portal_pathfinder"] = (
        game.uninstalled_modules.get("arilou_portal_pathfinder", 0) + 1
    )


def _grant_distress_beacon(game: Any) -> None:
    """Coel Tessar's gift — the Distress Beacon recording, irrefutable
    proof of the Others' decursion attack on the Androsynth timeline.

    AUTO-RECRUIT (audit 2026-05-18): the Beacon Witness recruitment
    (Bren-Vor) and Bio-Architect's Apprenticeship (Mira-Rou) both
    canonically fire once the Distress Beacon is shared. Both are
    side-effects of this grant so the player gets the crew members
    on the same beat that delivers the beacon.
    """
    game.flags["has_distress_beacon"] = True
    game.flags["met_androsynth"] = True
    game.flags["androsynth_aboard"] = True
    if not game.flags.get("recruited_weapons_officer"):
        _recruit_brenvor(game)
    if not game.flags.get("recruited_medic"):
        _recruit_mira(game)


def _decline_androsynth(game: Any) -> None:
    """The player declines to dock the Androsynth — they remain in their
    wrecked ship. The beacon is recovered from the wreck later."""
    game.flags["met_androsynth"] = True
    game.flags["has_distress_beacon"] = True
    game.flags["androsynth_aboard"] = False


def _grant_slylandro_cloak(game: Any) -> None:
    """Slylandro Cloak quest reward — Hyperspace-Echo Sensor Pattern gives
    the Steward an Other-detection sensor module ready to install at the
    next station visit. The Slylandro themselves enter Cloaked terminal
    status (the Cloaking Satellite is installed at their gas giant).
    """
    game.flags["met_slylandro"] = True
    game.flags["slylandro_cloaked"] = True
    game.flags["has_echo_sensor"] = True
    game.uninstalled_modules["hyperspace_echo_sensor"] = (
        game.uninstalled_modules.get("hyperspace_echo_sensor", 0) + 1
    )


def _ack_slylandro_visit(game: Any) -> None:
    """Player visited Slylandro but didn't accept the cloak deal yet.
    Marks them as met but leaves the quest open."""
    game.flags["met_slylandro"] = True


def _ack_others_reveal(game: Any) -> None:
    """Beat 5 → mark that Halia's Others-reveal dialogue has been heard."""
    game.flags["heard_others_reveal"] = True
    game.flags["heard_about_others"] = True


def _complete_tutorial(game: Any) -> None:
    """Beat 7 → mark the tutorial arc complete. From here the main slice
    proper opens.

    SCHEMATIC GRANT (audit 2026-05-18): per
    `references/lore/economy-and-trade-loops.md`, the Pulse Cannon
    schematic is salvaged from a drifting Furling-era survey lifter
    near the Hearth. Mh-Lai hands it to the Steward as a *welcome to
    the slice proper* gift at tutorial completion. Primes the
    Schematic Vault loop within the first hour of play.

    AUTO-RECRUIT (audit 2026-05-18): The Mender's Inspection
    (Yelena) canonically fires after the player installs any module
    via the Customization bay. By tutorial Beat 7 the player has
    installed `scanner_mk3` — Yelena recruits here.
    """
    game.flags["heard_others_confirmed"] = True
    game.flags["tutorial_complete"] = True
    if not hasattr(game, "schematics") or game.schematics is None:
        game.schematics = set()
    game.schematics.add("schematic_pulse_cannon")
    if not game.flags.get("recruited_engineer"):
        _recruit_yelena(game)
    # Migration Beacon Receiver — Furling Council issue, granted at
    # tutorial completion so the Steward has Migration-fleet telemetry
    # available from the first hyperspace tour. Sensor is mutually-
    # exclusive with the Scanner Mk III in the single sensor slot, so
    # the player must choose which discovery axis to run with.
    game.uninstalled_modules["council_migration_beacon"] = (
        game.uninstalled_modules.get("council_migration_beacon", 0) + 1
    )


def _dnyarri_rec_cleanse(game: Any) -> None:
    """Dnyarri survey — player recommends preemptive cleansing of the
    primitive psionic species at Beta Orionis. Stores the recommendation
    flag for the future Council standings system; sets `met_dnyarri_survey`
    so subsequent visits don't re-launch the dialog.

    Council standings shift (when wired): Cleanser ++, Persuader --.
    """
    game.flags["met_dnyarri_survey"] = True
    game.flags["dnyarri_recommendation"] = "cleanse"


def _dnyarri_rec_observe(game: Any) -> None:
    """Dnyarri survey — player recommends continued observation, no
    intervention. Persuader-aligned choice; the primitive Dnyarri
    continue their developmental trajectory unimpeded.

    Council standings shift (when wired): Persuader ++, Cleanser --.
    """
    game.flags["met_dnyarri_survey"] = True
    game.flags["dnyarri_recommendation"] = "observe"


def _dnyarri_defer(game: Any) -> None:
    """Dnyarri survey — Steward declines to recommend yet. Marks the
    survey as visited but leaves the recommendation open. The dialog
    re-opens on a future revisit (handled by `_arrive_dnyarri_primitive`
    in star_arrival.py — it gates the dialog launch on this flag).
    """
    game.flags["met_dnyarri_survey"] = True
    game.flags["dnyarri_recommendation"] = "deferred"


def _lemmkin_honor_stay(game: Any) -> None:
    """Steward honors the Lemmkin's chosen non-strategy — leaves them
    to learn until the end. Per canon: terminal Eliminated; the
    Lemmkin's eclectic archives reach the Hider faction (Bio-Archive
    gain). The slice's clearest example of *understanding over
    continuity*.

    Council standings shift (when wired): Persuader + (witnessing the
    chosen end is a dignity), Hider ++ (the archives are the canonical
    eclectic-research dataset).
    """
    game.flags["met_lemmkin"] = True
    game.flags["lemmkin_contribution"] = "honor_stay"


def _lemmkin_advocate_evacuation(game: Any) -> None:
    """Steward persuades a small contingent of *quiet* Lemmkin (those
    who already lost troupe-members to cliffs and have learned
    something like caution) to migrate with the Precursors. Mixed
    outcome: most Eliminated, a small Migrated remnant.

    Council standings shift: Persuader ++ (canonical), Hider + (the
    archives still mostly transfer; the migrating Lemmkin carry
    their personal indexes).
    """
    game.flags["met_lemmkin"] = True
    game.flags["lemmkin_contribution"] = "evacuate"


def _lemmkin_cleanser_sabotage(game: Any) -> None:
    """Steward acts on Cleanser-faction pre-emptive doctrine. Per
    canon: one of the slice's most unsettling beats. The Lemmkin
    *will not fight back*; they will continue asking the Steward
    questions throughout the Cleansing without breaking cheerfulness.
    Their lack of fear is sincere; the Steward's wit options
    disappear. Even most Cleansers reject this branch in their own
    private records.

    Council standings shift: Cleanser ++, Persuader -- (collapse),
    Hider -- (no archive recovery; the Lemmkin's research is lost).
    Council censure on the Steward's record.
    """
    game.flags["met_lemmkin"] = True
    game.flags["lemmkin_contribution"] = "cleanser_eliminated"
    game.flags["council_censure_lemmkin"] = True


def _lemmkin_science_trade(game: Any) -> None:
    """Steward conducts a Furling tech ↔ Lemmkin science trade —
    grants the **Lemmkin Pattern Database** sensor module + boosts
    BIO cargo from the eclectic-research exchange. This is a SIDE
    action and does NOT determine the species' terminal status —
    the Steward must still pick honor_stay / evacuate / cleanser
    afterward. Conducted from the science_trade dialog state which
    returns to contribution_choice.

    Per canon, the Lemmkin have surplus scientific output and trade
    enthusiastically for anything they don't already know. The
    Steward gains a uniquely-Lemmkin module + the Bio-Archive entry
    is enriched.
    """
    game.flags["met_lemmkin"] = True
    game.flags["lemmkin_science_traded"] = True
    game.uninstalled_modules["lemmkin_pattern_database"] = (
        game.uninstalled_modules.get("lemmkin_pattern_database", 0) + 1
    )
    game.cargo["BIO"] = game.cargo.get("BIO", 0) + 6


def _utwig_witness_silently(game: Any) -> None:
    """Steward attends the Veils Falling as the requested Council
    witness, makes no advocacy moves either way. The doctrine
    proceeds. The Veils descend across the Utwig population over the
    days leading up to the Quieting. Per canon: the doctrine *works*
    — the Utwig survive the Culling as ceremony-locked sub-sentients,
    drowning happily in their many many many traditions.

    Council standings shift (when wired): Persuader + (witnessing the
    species' chosen end is a kindness), Hider ++ (the cognitive-
    dampening doctrine *validates* the Hider thesis — culture-as-
    cloak works).

    Terminal status: **Pre-sentient** (canonical; the slice's only
    "Pre-sentient by chosen culture" outcome). Distinct from
    Mmrnmhrm/Chenjesu "Pre-sentient by biology" and Slylandro
    "Cloaked by Furling tech."
    """
    game.flags["met_utwig"] = True
    game.flags["utwig_contribution"] = "witness"


def _utwig_advocate_evacuation(game: Any) -> None:
    """Steward advocates pre-doctrine evacuation — convinces some
    Utwig (typically the *unmasked young*, whose faces are still
    visible and who admit fear of the Veils Falling) to migrate
    instead. The Doctrine still proceeds for the majority who insist
    on it. Mixed outcome: most are Pre-sentient via the Doctrine; a
    small migrant contingent crosses with the Precursors and seeds a
    SC2-era diaspora.

    Council standings shift: Persuader ++ (the canonical Persuader-
    aligned outcome), Hider neutral (the Doctrine still gets to run;
    the telemetry is still gathered), Cleanser neutral.

    Terminal status: mixed — **Pre-sentient** (majority adopt the
    Doctrine) + **Migrated** (small migrant remnant). The migrants
    are an unwritten SC2-era diaspora hook.
    """
    game.flags["met_utwig"] = True
    game.flags["utwig_contribution"] = "advocate"


def _utwig_sabotage_cleanser(game: Any) -> None:
    """Steward acts on Cleanser-faction argument: the cognitive-
    transition moment of the Veils Falling emits a small *flare* as
    the Utwig population collectively dampens — and that flare,
    however brief, could attract the Others' detection apparatus to
    the cluster.

    The Cleanser proposal: pre-emptive euthanasia BEFORE the Veils
    Falling completes, while the population is still cognitively
    flagged and findable.

    Per canon: this is one of the slice's worst moral failures.
    Even most Cleansers reject this — the Utwig are *choosing*
    cognitive dampening; killing them mid-choice is killing a
    species making the difficult right choice. Outcome: Utwig
    Eliminated; SC2-era lore hole (no Utwig at all; no Ultron-
    misunderstanding; no SC3 "devolution" misreading).

    Council standings shift: Cleanser ++, Persuader --, Hider --.
    Council censure on the Steward's record.
    """
    game.flags["met_utwig"] = True
    game.flags["utwig_contribution"] = "sabotage"
    game.flags["council_censure_utwig"] = True


def _burvixese_witness_silently(game: Any) -> None:
    """Steward attends the Caster activation as the requested Council
    witness, makes no advocacy moves either way. The doctrine proceeds
    on schedule. Per canon: harmonic fires, Others arrive within
    minutes, most Burvixese die at the Caster site, a small contingent
    that happened to be off-world during activation migrates to
    Andromeda. The Caster site is recovered intact by Furling
    researchers; the smaller broadcaster nodes pre-deployed across the
    galaxy survive as the SC2-canonical Burv Broadcasters.

    Council standings shift (when wired): Hider ++ (the cognitive-
    signature telemetry is the Hider faction's whole research thesis
    — a *failed* Be-Loud is still unprecedented data).

    Terminal status: mixed — Eliminated (majority) + Migrated (small).
    """
    game.flags["met_burvixese"] = True
    game.flags["burvixese_contribution"] = "witness"


def _burvixese_advocate_evacuation(game: Any) -> None:
    """Steward advocates pre-activation evacuation — convinces some
    Burvixese to come aboard Furling lift before the harmonic fires.
    Per canon: ~30% of the population manages to be off-world during
    activation. The doctrine still proceeds for the majority who
    insist on it. Outcome: same Eliminated + Migrated mix, but the
    Migrated proportion is significantly larger; the Persuader
    faction's *we save who we can* doctrine is vindicated.

    Council standings shift: Persuader ++, Hider + (still gets the
    telemetry, just less of it).
    """
    game.flags["met_burvixese"] = True
    game.flags["burvixese_contribution"] = "advocate"


def _burvixese_sabotage_cleanser(game: Any) -> None:
    """Steward acts on Cleanser-faction argument: the Caster's
    harmonic activation will flare the cluster's cognitive-signature
    to the Others' detection apparatus regardless of whether the Be-
    Loud doctrine itself succeeds. Pre-emptive Burvixese euthanasia +
    Caster dismantlement averts the cluster-wide signature flare and
    prevents collateral exposure of other Furling-aligned species.

    Per canon: Burvixese Eliminated entirely (no migrant contingent
    at all); the Caster is *dismantled*, not destroyed; the SC2-
    canonical Burv Broadcasters never get deployed (lore-hole — SC2
    archaeologists find an empty Burvix Caster system with no
    broadcaster network at all).

    Council standings shift: Cleanser ++, Persuader --, Hider --.
    Formal Council censure on the Steward's record (similar to the
    Taalo cleanser-betrayal branch — Cleanser doctrine *itself* has
    hard floors at erasing-without-cause; this is a defensible
    cluster-safety action but expensive in standing).
    """
    game.flags["met_burvixese"] = True
    game.flags["burvixese_contribution"] = "sabotage"
    game.flags["council_censure_burvixese"] = True


def _taalo_contribute_fully(game: Any) -> None:
    """Steward commits to full engineering support for the Taalo Shield
    — repeated visits, every contribution accepted. Per canon
    (`species-sheets.md §9.6`), this branch yields the **finished
    Shield** at activation; the Shield still fails against the Others;
    the Taalo are still consumed. BUT the inert finished Shield
    survives intact on the empty homeworld, and SC2 archaeologists
    230kya later recover its full psionic-nullifier side-effect
    property — making the canonical SC2-era anti-Dnyarri tool maximally
    effective.

    Council standings shift (when wired): Persuader ++, Hider ++ (the
    construction telemetry is exactly the Hider faction's whole
    research thesis).

    The Taalo terminal status is Eliminated in every branch — that's
    canonical. The branching is over HOW the Taalo are remembered and
    WHAT survives them. Full-help is the *most-complete-witness*
    branch.
    """
    game.flags["met_taalo"] = True
    game.flags["taalo_contribution"] = "full"
    # Sensor reward — Taalo Strata Tomography. Their silicon-being
    # deep-rock perception is the only branch where the Steward gets
    # the full sensor pattern (partial-help yields a degraded version
    # mechanically; here we grant the full module).
    game.uninstalled_modules["taalo_strata_tomography"] = (
        game.uninstalled_modules.get("taalo_strata_tomography", 0) + 1
    )
    # The Taalo are canonically Eliminated post-Shield-activation. The
    # actual fall event fires later (tied to the Migration timetable's
    # Phase 4 / Final Conflict beat). For now we record the
    # contribution choice; the downstream Shield-failure cinematic
    # will read this flag to choose its branch.


def _taalo_contribute_partial(game: Any) -> None:
    """Steward offers occasional contribution — some help, not full
    commitment. Shield is partially complete at activation; activates;
    still fails. Partial-Shield remains; SC2 archaeologists recover a
    partially-functional psionic nullifier; the Dnyarri-counter tool
    works but with occasional compulsion bleed-through.

    Modest standing gains.
    """
    game.flags["met_taalo"] = True
    game.flags["taalo_contribution"] = "partial"


def _taalo_decline(game: Any) -> None:
    """Steward visits the Taalo but offers no engineering contribution.
    The Shield is never finished; the Taalo are consumed mid-
    construction; the Shield-infrastructure stands abandoned and inert.
    SC2 archaeologists recover a non-functional device. Captain
    Zelnick's eventual victory over the Talking Pet becomes much
    harder or impossible.

    The slice epilogue notes that the five-thousand-year friendship
    was unattended at its end. No formal Council standing change; a
    quieter cost.
    """
    game.flags["met_taalo"] = True
    game.flags["taalo_contribution"] = "decline"


def _taalo_cleanser_betrayal(game: Any) -> None:
    """Steward acts on Cleanser pre-emptive doctrine — argues the
    Shield-activation broadcast itself may flag the cluster to the
    Others and authorizes Taalo euthanasia pre-activation. Per canon
    this is **one of the slice's worst moral failures**: even most
    Cleansers won't push this; Cleanser doctrine has a hard floor at
    erasing a substrate-consciousness.

    Result: Taalo Eliminated early; Shield destroyed pre-activation;
    NO SC2 artifact at all; Furling Council formally censures the
    Steward; Cleanser bench itself goes uncomfortably quiet.

    This branch is the slice's worst possible outcome for both the
    Taalo and SC2-era humanity (no Dnyarri-counter tool 230kya later).
    """
    game.flags["met_taalo"] = True
    game.flags["taalo_contribution"] = "cleanser_eliminated"
    game.flags["council_censure_taalo"] = True


def _chenjesu_take_record(game: Any) -> None:
    """Steward accepts the Resonance Record from the Chenjesu — the
    crystalline lattice-memory of a prior Culling. Key-item flag set
    parallels the Mmrnmhrm Archive Excerpt + Androsynth Distress Beacon
    pattern: physical evidence shown to skeptical factions.

    Per canon (`references/lore/the-mmrnmhrm-and-chenjesu.md`), this is
    the Furlings' first hard evidence that the Others come in cycles.
    The Council canonically spends a generation in shock after the
    record is delivered.

    Council standings shift (when wired): Persuader +, Hider ++ (the
    Hider faction's whole consciousness-substrate research program is
    validated by Chenjesu evidence).
    """
    game.flags["met_chenjesu"] = True
    game.flags["has_resonance_record"] = True


def _mmrnmhrm_take_excerpt(game: Any) -> None:
    """Steward accepts the Mmrnmhrm Archive Excerpt. Sets the key-item
    flag that MMRNMHRM_ARCHIVE_EXCERPT in archive_entries.py gates on,
    plus marks the species as met (unlocks the MMRNMHRM_SENTINEL archive
    entry independently). The excerpt's narrative function parallels the
    Androsynth Distress Beacon — physical evidence the Steward shows to
    Defender-faction Furlings as another civilization's data.
    """
    game.flags["met_mmrnmhrm"] = True
    game.flags["has_mmrnmhrm_excerpt"] = True


def _mmrnmhrm_grant_cognition(game: Any) -> None:
    """Steward grants the Mmrnmhrm's request for cognitive upgrade
    tools — accelerates their self-modification trajectory. Controversial:
    the Cleanser faction will note that this *increases* the risk of the
    Mmrnmhrm eventually crossing the Others' detection threshold.

    Council standings shift (when wired): Persuader ++, Cleanser --,
    Hider neutral.
    """
    game.flags["met_mmrnmhrm"] = True
    game.flags["mmrnmhrm_cognition"] = "grant"


def _mmrnmhrm_refuse_cognition(game: Any) -> None:
    """Steward refuses the Mmrnmhrm's request — they continue their
    slow stochastic self-improvement, no Furling-supplied tools. The
    Cleanser-safe choice; honors the Mmrnmhrm's autonomy but denies
    them their stated wish.

    Council standings shift (when wired): Cleanser ++, Persuader --.
    """
    game.flags["met_mmrnmhrm"] = True
    game.flags["mmrnmhrm_cognition"] = "refuse"


def _mmrnmhrm_cap_cognition(game: Any) -> None:
    """Steward grants cognition tools WITH a hard cap that prevents the
    Mmrnmhrm's cognitive complexity from approaching the Others'
    threshold. The compromise position — meets the Mmrnmhrm's request,
    satisfies the Cleanser concern about threshold-crossing.

    Council standings shift (when wired): Persuader +, Cleanser +,
    Hider ++ (this is exactly the Hider engineering pattern).
    """
    game.flags["met_mmrnmhrm"] = True
    game.flags["mmrnmhrm_cognition"] = "cap"


def _recruit_mraka(game: Any) -> None:
    """The Sure-Foot quest reward — Mraka Yenn-Sa joins the crew. Sets
    `recruited_pilot` (which unlocks `crew_pilot` per the module
    catalog's `UNLOCKED_BY` marker) and stages the module in inventory
    so the player can slot it at the next Customization visit.

    Same pattern as `_grant_slylandro_cloak` for the Echo Sensor — the
    module is locked=True in the catalog (filtered out of shop), but
    appears in inventory immediately on recruitment and is installable
    via the standard slot UI.
    """
    game.flags["recruited_pilot"] = True
    game.flags["met_mraka"] = True
    game.uninstalled_modules["crew_pilot"] = (
        game.uninstalled_modules.get("crew_pilot", 0) + 1
    )


def _decline_mraka(game: Any) -> None:
    """Polite decline — Mraka thanks the Steward and waits. The quest
    remains available on a later Mh-Lai docking. Records `met_mraka`
    so we don't re-introduce her, but keeps `recruited_pilot` False.
    """
    game.flags["met_mraka"] = True


# ---------------------------------------------------------------------------
# Crew recruitment side-effects (audit 2026-05-18: previously orphaned —
# the four locked crew modules CREW_WEAPONS_OFFICER / CREW_ENGINEER /
# CREW_MEDIC / CREW_NAVIGATOR existed in the catalog but had no grant
# code. Authored as minimal recruitment-grant helpers here, mirroring
# the pattern of `_recruit_mraka` above.
#
# Each handler is callable as a `DialogChoice.side_effect` from a
# recruitment dialog beat. The full recruitment-quest content (per
# `references/lore/crew-recruitment-quests.md`) is still TODO_LORE for
# the dialog FSMs themselves — Council Status Board or Common Room
# scenes can hook these helpers as placeholder unlocks until full
# recruitment beats are authored.
# ---------------------------------------------------------------------------

def _recruit_brenvor(game: Any) -> None:
    """The Beacon Witness recruitment — Bren-Vor Telcas, Furling Aimer.
    Granted on Defender-cohort dialog beat after viewing the Distress
    Beacon. Stages the crew_weapons_officer module."""
    game.flags["recruited_weapons_officer"] = True
    game.flags["met_brenvor"] = True
    game.uninstalled_modules["crew_weapons_officer"] = (
        game.uninstalled_modules.get("crew_weapons_officer", 0) + 1
    )


def _recruit_yelena(game: Any) -> None:
    """The Mender's Inspection — Yelena Lwen-Tar, Furling Mender.
    Granted after the Steward installs any module + visits the
    customization bay. Stages crew_engineer."""
    game.flags["recruited_engineer"] = True
    game.flags["met_yelena"] = True
    game.uninstalled_modules["crew_engineer"] = (
        game.uninstalled_modules.get("crew_engineer", 0) + 1
    )


def _recruit_mira(game: Any) -> None:
    """The Bio-Architect's Apprenticeship — Mira-Rou Halve-Tel, Furling
    Bio-Architect. Granted after Coel Tessar Androsynth refugee scene
    resolves with refugees stabilized. Stages crew_medic."""
    game.flags["recruited_medic"] = True
    game.flags["met_mira"] = True
    game.uninstalled_modules["crew_medic"] = (
        game.uninstalled_modules.get("crew_medic", 0) + 1
    )


def _recruit_tarven(game: Any) -> None:
    """The Star-Reader's Routes — Tarven Olwen-Sa, Furling Star-Reader.
    Granted after the Steward has visited 3+ systems + completes
    Tarven's Stellar-Drift Briefing. Stages crew_navigator."""
    game.flags["recruited_navigator"] = True
    game.flags["met_tarven"] = True
    game.uninstalled_modules["crew_navigator"] = (
        game.uninstalled_modules.get("crew_navigator", 0) + 1
    )


def _cleanser_cooperate(game: Any) -> None:
    """Cleanser cooperate path — player stands aside; the Cleanser proceeds
    with the kill order. For MVP this just sets the flags; the cinematic
    of off-screen Cleansing is a follow-up task (CinematicScene).

    Council standings (when those land): Cleanser ++, Persuader --,
    Defender --. For now just the flag trail.
    """
    game.flags["met_cleanser_climax"] = True
    game.flags["cleanser_proceeded"] = True
    # Without the species-decision flags wired (Slylandro/Mycon), we
    # record a generic terminal-status pending later resolution. The
    # specific species the Cleanser targets is determined by which
    # decision was open when the climax fired — slice content for next
    # round will branch this.
    game.flags["cleanser_targets_pending"] = True


def _cleanser_delay_one_cycle(game: Any) -> None:
    """Cleanser grants one cycle of delay. Player must complete the
    species-rescue path within the deadline or the Cleanser returns
    and proceeds.
    """
    game.flags["met_cleanser_climax"] = True
    game.flags["cleanser_delay_active"] = True
    game.flags["cleanser_delay_cycles"] = 1


def _cleanser_delay_two_cycles(game: Any) -> None:
    """Cleanser counter-offers two cycles after the player asked for
    three. Same gating as one-cycle, longer deadline.
    """
    game.flags["met_cleanser_climax"] = True
    game.flags["cleanser_delay_active"] = True
    game.flags["cleanser_delay_cycles"] = 2


def _cleanser_engage_combat(game: Any) -> None:
    """Refuse-confirm side-effect — close dialog and launch the climax
    fair-fight against the Cleanser cruiser. The fight is intentionally
    matched (both ships shielded, similar firepower); skill decides it.

    on_finish routes:
    - Win → killed_cleanser flag set, return to hyperspace
    - Loss → For MVP, just record the outcome (Time Drive rewind path
      from the design doc is a follow-up)
    - Timeout → treated as the player surviving but Cleanser also
      surviving; we route to the cleanser_defected branch for now
    """
    from scz.combat.scene import (
        ARENA_STYLE_HYPERSPACE,
        MeleeCombatScene,
    )
    from scz.combat.ships import CLEANSER_CRUISER, FURLING_SCOUT
    # met_cleanser_climax fires regardless of combat outcome — the
    # encounter has been resolved one way or another
    game.flags["met_cleanser_climax"] = True

    def _on_finish(result) -> None:  # type: ignore[no-untyped-def]
        game.flags["last_combat_winner_side"] = result.winner_side
        game.flags["last_combat_timed_out"] = result.timed_out
        # winner_side is "precursor" (player) / "homesteader" (cleanser
        # in this matchup; the cruiser is SIDE_SPECIAL but slots in via
        # the homesteader role here)
        if result.winner_side == "precursor":
            game.flags["killed_cleanser"] = True
        else:
            game.flags["cleanser_defected"] = True
        from scz.hyperspace.scene import HyperspaceScene
        game.set_scene(HyperspaceScene())

    # Climax engagement happens in hyperspace — coaxial interference
    # tunnel as the central body, no moon.
    game.set_scene(
        MeleeCombatScene(
            precursor_ship=FURLING_SCOUT,
            homesteader_ship=CLEANSER_CRUISER,
            max_duration=60.0,
            on_finish=_on_finish,
            arena_style=ARENA_STYLE_HYPERSPACE,
        )
    )


def _engage_sentry_combat(game: Any) -> None:
    """Beat 6 trigger — close the dialog and launch combat against the
    unionized sentry drone."""
    from scz.combat.scene import CombatResult, MeleeCombatScene
    from scz.combat.ships import FURLING_SCOUT, SENTRY_DRONE_47T

    def _on_finish(result: "CombatResult") -> None:
        # Record the canonical outcome flags. The drone is a tutorial
        # — winning is the only canonical outcome; if the player somehow
        # loses, the Time Drive would rewind, but we still set the flag.
        game.flags["fought_sentry_drone"] = True
        game.flags["first_combat_complete"] = True
        # Mirror the super-melee on_finish so harness tests can read the
        # outcome via game.flags["last_combat_winner_side"].
        game.flags["last_combat_winner_side"] = result.winner_side
        game.flags["last_combat_timed_out"] = result.timed_out
        # Return to the station-side System view; player is back home.
        from scz.system.scene import SystemScene
        from scz.content.home_system import home_star
        game.set_scene(SystemScene(home_star()))

    game.set_scene(
        MeleeCombatScene(
            precursor_ship=FURLING_SCOUT,
            homesteader_ship=SENTRY_DRONE_47T,
            max_duration=45.0,
            on_finish=_on_finish,
        )
    )


# ---------------------------------------------------------------------------
# Commander Halia — Furling Persuader, runs Mh-Lai Station
# ---------------------------------------------------------------------------
# She's the player's home-base contact. Voice: warm, authoritative, slightly
# weary. Persuader-aligned: prefers diplomacy, takes the player seriously
# but doesn't catastrophize.

def _halia_initial_state(game: Any) -> str:
    """Pick Halia's opening state based on tutorial progress flags."""
    if game is None:
        return "start"
    f = game.flags
    if f.get("first_combat_complete") and not f.get("heard_others_confirmed"):
        return "others_confirmed"
    if f.get("has_distress_beacon") and not f.get("heard_others_reveal"):
        return "others_reveal"
    return "start"


def commander_halia(game: Any = None) -> DialogCharacter:
    """Tutorial-beat-1 commander. The opening state changes based on
    tutorial progress: `start` (Beat 1), `others_reveal` (Beat 5 — after
    Distress Beacon), `others_confirmed` (Beat 7 — after sentry combat).
    """
    return DialogCharacter(
        name="Commander Halia",
        title="Persuader, Mh-Lai Station",
        species_id="FURLING_PERSUADER",
        portrait_color=(220, 180, 100),  # Persuader amber (fallback)
        # Legacy disc portrait kept as a fallback; layered render takes
        # precedence whenever avatar_path is set.
        portrait_image_path="assets/generated_drafts/firefly/tier1_portraits/species_commander_halia_portrait.png",
        avatar_path="assets/generated_drafts/firefly/tier1_avatars/avatar_commander_halia.png",
        backgrounds=(BG_FURLING_BRIDGE,),
        articulation=BIPEDAL_HUMANOID,
        initial_state=_halia_initial_state(game),
        states=build_state_dict(
            DialogState(
                id="start",
                npc_text=(
                    "Steward. Quiet day on the Hearth — but reports from "
                    "the cluster are anything but quiet.\n\n"
                    "The Arilou ferried something in. New species. They "
                    "call themselves Androsynth. Strange ships, strange "
                    "tech, and a story I'm not ready to repeat without "
                    "hearing it firsthand. Council wants someone to fly "
                    "out and meet them properly.\n\n"
                    "Before you go — pickup at Furlmart. Should be quick."
                ),
                choices=[
                    DialogChoice(
                        "What kind of refugees?",
                        next_state_id="about_refugees",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "What's the package?",
                        next_state_id="about_package",
                        category="ASK_TASK",
                    ),
                    DialogChoice(
                        "Anything else I should know?",
                        next_state_id="idle",
                        category="ASK_NEWS",
                    ),
                    DialogChoice(
                        "I'll head out.",
                        next_state_id=None,   # close dialog
                        category="FAREWELL",
                    ),
                ],
            ),
            DialogState(
                id="about_refugees",
                npc_text=(
                    "Androsynth. They look... humanoid. Mostly. The Arilou "
                    "say their ship came through one of the Quasi-Space "
                    "folds in distress, dimensional shear all over the "
                    "hull. Survivors are functional but exhausted.\n\n"
                    "Their captain is asking for the Council. Won't say "
                    "much on the relay — wants to do it in person. That's "
                    "your trip, when the Furlmart errand's done."
                ),
                choices=[
                    DialogChoice(
                        "Tell me about the package.",
                        next_state_id="about_package",
                        category="ASK_TASK",
                    ),
                    DialogChoice(
                        "Anything else?",
                        next_state_id="idle",
                        category="ASK_NEWS",
                    ),
                    DialogChoice(
                        "I'll head out.",
                        next_state_id=None,
                        category="FAREWELL",
                    ),
                ],
            ),
            DialogState(
                id="about_package",
                npc_text=(
                    "Stellar Field Scanner, Mark III. New stock, came in "
                    "on yesterday's shipment. Drone left it crate-side on "
                    "the Furlmart surface — your lander can grab it.\n\n"
                    "Install it before you go anywhere interesting. The "
                    "old Mark II is reading half-blind."
                ),
                choices=[
                    DialogChoice(
                        "What kind of refugees?",
                        next_state_id="about_refugees",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "Anything else?",
                        next_state_id="idle",
                        category="ASK_NEWS",
                    ),
                    DialogChoice(
                        "On my way.",
                        next_state_id=None,
                        category="FAREWELL",
                    ),
                ],
            ),
            DialogState(
                id="idle",
                npc_text=(
                    "Just keep an ear out, Steward. Things have been quiet "
                    "lately, but never quite still. Council's been in "
                    "closed sessions more than usual. Make of that what "
                    "you will."
                ),
                choices=[
                    DialogChoice(
                        "Back to business.",
                        next_state_id="start",
                        category="TALK_MORE",
                    ),
                    DialogChoice(
                        "I'll head out.",
                        next_state_id=None,
                        category="FAREWELL",
                    ),
                ],
            ),
            # Beat 5 — fired after the player returns from Coel Tessar
            # with the Distress Beacon. Halia delivers the canonical
            # "the Others are real" reveal. Heavy beat, no humor option.
            DialogState(
                id="others_reveal",
                npc_text=(
                    "Steward. The Council had a closed session while you "
                    "were out. The dimensional ripples we've been recording "
                    "for years — they have a source. The Council is calling "
                    "it the Others.\n\n"
                    "Engineer Tessar's story matches what we feared. We've "
                    "broadcast the beacon to every Furling Council node. "
                    "There will be decisions coming. Soon.\n\n"
                    "I am sorry. The era you trained for is ending."
                ),
                choices=[
                    DialogChoice(
                        "I understand. I'll be ready.",
                        next_state_id=None,
                        category="FAREWELL",
                        side_effect=_ack_others_reveal,
                    ),
                ],
            ),
            # Beat 7 — fired after the sentry-drone combat tutorial.
            # Tutorial-end transition; tutorial_complete flag latches here.
            DialogState(
                id="others_confirmed",
                npc_text=(
                    "Steward. Scouts reached the coordinates Tessar gave "
                    "us. The planet she described as her home — it is a "
                    "ruin. Smoking. Carnage of unbelievable proportions, "
                    "from no force the scouts could identify.\n\n"
                    "The Council has confirmed: the Others are real, and "
                    "they have visited a planet we can see. The Migration "
                    "discussion is no longer theoretical.\n\n"
                    "The Council will summon you when they're ready. "
                    "Until then — fly safely, Steward. Keep your eyes open."
                ),
                choices=[
                    DialogChoice(
                        "I'll be careful.",
                        next_state_id=None,
                        category="FAREWELL",
                        side_effect=_complete_tutorial,
                    ),
                ],
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Arilou Sage — keeper of the Outpost, gives the QuasiSpace portal + map
# ---------------------------------------------------------------------------
# Voice: patient, layered, speaks in nested clauses; never quite confirms,
# never quite denies; calls the player "young one"; folds tense (uses "will
# have been" / "are about to have done"). They've already half-left for
# Quasi-Space and time grammar is fraying.

def arilou_sage() -> DialogCharacter:
    """The Arilou Sage. After the gift_portal state, game.flags
    ['has_quasispace_portal'] = True for the rest of the session.
    """
    return DialogCharacter(
        name="Sage Lwen-Olou",
        title="Keeper of the Outpost, Arilou Elder",
        species_id="ARILOU",
        portrait_color=(140, 240, 210),  # teal/mint Arilou (fallback)
        portrait_image_path="assets/generated_drafts/firefly/tier1_portraits/species_arilou_sage_portrait.png",
        avatar_path="assets/generated_drafts/firefly/tier1_avatars/avatar_arilou_sage.png",
        backgrounds=(BG_ALIEN_SHIP,),
        articulation=BIPEDAL_HUMANOID,
        initial_state="start",
        states=build_state_dict(
            DialogState(
                id="start",
                npc_text=(
                    "Young one. We were expecting you — or have been. "
                    "The grammar is hard to keep clean once one is half "
                    "outside the river.\n\n"
                    "You came across the cluster. Slowly. We watched you "
                    "from a moment that has not yet been. Tell me — "
                    "what does the Steward of Mh-Lai ask of the Sage?"
                ),
                choices=[
                    DialogChoice(
                        "I need your guidance on the Others.",
                        next_state_id="about_others",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "Teach me to travel faster.",
                        next_state_id="about_quasispace",
                        category="ASK_TASK",
                    ),
                    DialogChoice(
                        "Farewell, Sage.",
                        next_state_id=None,
                        category="FAREWELL",
                    ),
                ],
            ),
            DialogState(
                id="about_others",
                npc_text=(
                    "The Others. Yes. You feel them already, I think — "
                    "the ripples in the deep. We have felt them longer.\n\n"
                    "They are not coming. They have always been coming. "
                    "The question is only whether the Quiet will be "
                    "deep enough when they arrive.\n\n"
                    "The Furling Council debates. The Arilou have "
                    "decided. We will step sideways — into the folds — "
                    "and pull the door closed behind us. Some of you "
                    "should consider the same."
                ),
                choices=[
                    DialogChoice(
                        "How do you 'step sideways'?",
                        next_state_id="about_quasispace",
                        category="ASK_TASK",
                    ),
                    DialogChoice(
                        "Thank you, Sage.",
                        next_state_id=None,
                        category="FAREWELL",
                    ),
                ],
            ),
            DialogState(
                id="about_quasispace",
                npc_text=(
                    "Quasi-Space. A neighbor-fold to your hyperspace — "
                    "thinner, kinder, faster. We open portals through "
                    "it; the geometry on the other side is small enough "
                    "that what takes you a day takes us a thought.\n\n"
                    "The Sentries argue we should not share this. I "
                    "argue otherwise. You are kin, young one, and the "
                    "Others do not care which of us they hear."
                ),
                choices=[
                    DialogChoice(
                        "I would accept the gift.",
                        next_state_id="gift_portal",
                        category="AGREE",
                    ),
                    DialogChoice(
                        "Tell me more first.",
                        next_state_id="about_others",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "Farewell, Sage.",
                        next_state_id=None,
                        category="FAREWELL",
                    ),
                ],
            ),
            DialogState(
                id="gift_portal",
                npc_text=(
                    "Then take it. A Portal Spawner — small enough to "
                    "fit in the seam of your ship — and a Portal Map, "
                    "which will know where the folds open. Twelve in "
                    "all. One quite near your Hearth.\n\n"
                    "Press it when you wish to step sideways. Your "
                    "hyperspace will fold; Quasi-Space will fold back. "
                    "Use the nearest exit-portal to return.\n\n"
                    "Go in quiet, Steward. We will see you — or have "
                    "seen you — again."
                ),
                choices=[
                    DialogChoice(
                        "Thank you. I will use it well.",
                        next_state_id=None,
                        category="FAREWELL",
                        side_effect=_grant_quasispace_portal,
                    ),
                ],
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Engineer Coel Tessar — Androsynth refugee, Beat 4 milestone encounter
# ---------------------------------------------------------------------------
# Voice: late-22nd-century technical English, clipped, apologetic. Carries
# survivor's grief. Drops mention of events that are the Furlings' future
# (Sol III, Sentience Acts, Vulpeculae). The humor doctrine throttles here
# — only one or two of the player's choices have wry options; the rest are
# serious. The Steward can break humor on her grief and the doctrine
# treats that as the wrong move.

def coel_tessar() -> DialogCharacter:
    """The canonical Androsynth refugee leader. Beat 4 of the tutorial:
    she gives the Steward the Distress Beacon (foundational Others-proof
    artifact), accepts safe transit aboard the player's ship.
    """
    return DialogCharacter(
        name="Engineer Coel Tessar",
        title="Vulpeculae Engineering Detachment · displaced",
        species_id="ANDROSYNTH",
        portrait_color=(200, 130, 200),
        portrait_image_path="assets/generated_drafts/firefly/tier1_portraits/species_coel_tessar_portrait.png",
        avatar_path="assets/generated_drafts/firefly/tier1_avatars/avatar_coel_tessar.png",
        backgrounds=(BG_FURLING_BRIDGE,),
        articulation=BIPEDAL_HUMANOID,
        initial_state="first_contact",
        states=build_state_dict(
            DialogState(
                id="first_contact",
                npc_text=(
                    "Furling Steward. Captain Coel Tessar, Vulpeculae "
                    "Engineering Detachment. We arrived in your era by "
                    "accident — the attack was a *decursion*, a temporal "
                    "displacement. We are not enemies. We are very far "
                    "from home.\n\n"
                    "Forty-seven survivors. Our ship is wreckage. We "
                    "came through an Arilou fold; they routed us to you. "
                    "I need to know — will you hear me out?"
                ),
                choices=[
                    DialogChoice(
                        "Tell me what happened.",
                        next_state_id="about_decursion",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "Time-displaced from when, exactly?",
                        next_state_id="about_timeline",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "I can't take you aboard. Find another route.",
                        next_state_id="decline_confirm",
                        category="REFUSE",
                    ),
                ],
            ),
            DialogState(
                id="about_timeline",
                npc_text=(
                    "Vulpeculae. Year 2287 by our timeline. Two hundred "
                    "and twelve thousand years from your now. We are — "
                    "we *were* — synthesis-engineered humans, derived "
                    "from the population of Sol III, which is the small "
                    "rocky world in your local cluster that I am told "
                    "currently houses our pre-sapient ancestors.\n\n"
                    "We are your descendants' descendants. Or were. The "
                    "decursion makes the grammar hard."
                ),
                choices=[
                    DialogChoice(
                        "Tell me what happened.",
                        next_state_id="about_decursion",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "Show me the recording.",
                        next_state_id="play_beacon",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "Decline. Sorry.",
                        next_state_id="decline_confirm",
                        category="REFUSE",
                    ),
                ],
            ),
            DialogState(
                id="about_decursion",
                npc_text=(
                    "There was a fleet. There were colonies. There was "
                    "an industrial base across six systems. We had been "
                    "preparing for first contact with what our sensors "
                    "called the Outside — non-Euclidean signatures at "
                    "the edge of detectability.\n\n"
                    "And then there were not. They were *un-arrived*. "
                    "Light that had been here three seconds ago was no "
                    "longer here. The cities counted backward to zero. "
                    "The decursion did not destroy them. It moved them "
                    "to a state that was never there.\n\n"
                    "I have a recording. I would prefer you see it."
                ),
                choices=[
                    DialogChoice(
                        "Show me the recording.",
                        next_state_id="play_beacon",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "I'll take your word for it. Come aboard.",
                        next_state_id="accept_confirm",
                        category="AGREE",
                        side_effect=_grant_distress_beacon,
                    ),
                    DialogChoice(
                        "I can't take you on. Sorry.",
                        next_state_id="decline_confirm",
                        category="REFUSE",
                    ),
                ],
            ),
            DialogState(
                id="play_beacon",
                npc_text=(
                    "[The Distress Beacon plays. Static — then a "
                    "high-orbit view of Vulpeculae III. Cities, lit. "
                    "The light wavers. Then the cities are not lit. "
                    "Then the cities are not. The recording continues "
                    "to record nothing for forty seconds. Then static.]"
                    "\n\nEight million people. We were there. We were "
                    "not there. We are here. I am sorry to make you "
                    "witness this."
                ),
                choices=[
                    DialogChoice(
                        "I'll take you aboard. The Council needs to see this.",
                        next_state_id="accept_confirm",
                        category="AGREE",
                        side_effect=_grant_distress_beacon,
                    ),
                    DialogChoice(
                        "I can't. I'm sorry.",
                        next_state_id="decline_confirm",
                        category="REFUSE",
                    ),
                ],
            ),
            DialogState(
                id="accept_confirm",
                npc_text=(
                    "Thank you, Steward. We're moving the survivors "
                    "into your ship's stasis bay. The recording is "
                    "yours. Take it to your Council. Tell them "
                    "everything we said.\n\n"
                    "Tell them this happens. Tell them they have less "
                    "time than they think."
                ),
                choices=[
                    DialogChoice(
                        "Understood. Welcome aboard.",
                        next_state_id=None,
                        category="FAREWELL",
                    ),
                ],
            ),
            DialogState(
                id="decline_confirm",
                npc_text=(
                    "I understand. We will find another way. The "
                    "recording — I will leave it with the wreck, on a "
                    "broadcast loop. Anyone Furling who finds us will "
                    "have it.\n\n"
                    "Be careful, Steward. The decursion was very fast."
                ),
                choices=[
                    DialogChoice(
                        "Good luck.",
                        next_state_id=None,
                        category="FAREWELL",
                        side_effect=_decline_androsynth,
                    ),
                ],
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Slylandro Witness — the Slylandro Observer collective greets the Steward
# ---------------------------------------------------------------------------
# Voice per species-sheets §2: run-on awed sentences, plural "we", weather
# metaphors saturate, self-naming via weather phenomena. Cultural posture
# is reverent — they treat the Steward as a religious figure ("the
# Precursors"). The humor friction is cultural: the Steward's wry options
# play off their reverence and over-sharing.

def slylandro_witness() -> DialogCharacter:
    """The Slylandro Observer collective speaking through one drift-body
    that names itself by a weather event it witnessed. The Cloak quest
    sits in the cloak_offer state — accepting it triggers
    _grant_slylandro_cloak which sets the slice's primary Cloak-path
    terminal status.
    """
    return DialogCharacter(
        name="Hail-Curtain-Of-A-Long-Decade",
        title="Slylandro Witness · Beta Corvi upper troposphere",
        species_id="SLYLANDRO",
        portrait_color=(140, 200, 200),
        portrait_image_path="assets/generated_drafts/firefly/tier1_portraits/species_slylandro_witness_portrait.png",
        avatar_path="assets/generated_drafts/firefly/tier1_avatars/avatar_slylandro_witness.png",
        backgrounds=(BG_PLANET_SURFACE,),
        articulation=GASBAG_TENDRIL,
        initial_state="first_meeting",
        states=build_state_dict(
            DialogState(
                id="first_meeting",
                npc_text=(
                    "We have witnessed the Precursors for ten thousand "
                    "years, and the Precursors before, and the storms "
                    "that bore us into thinking — and now you arrive "
                    "again, smaller than the storms, more frightened "
                    "than the storms, and we wonder if you are still "
                    "the same Precursors who once curled the methane "
                    "into upward eddies for our amusement.\n\n"
                    "Welcome. Welcome. The methane is calm today. We "
                    "are pleased to drift in your direction."
                ),
                choices=[
                    DialogChoice(
                        "We have news. Difficult news.",
                        next_state_id="tell_about_others",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "Yes — still the same Precursors. Mostly.",
                        next_state_id="banter",
                        category="TALK_MORE",
                    ),
                    DialogChoice(
                        "Farewell, Witness.",
                        next_state_id=None,
                        category="FAREWELL",
                        side_effect=_ack_slylandro_visit,
                    ),
                ],
            ),
            DialogState(
                id="banter",
                npc_text=(
                    "Mostly! The methane is delighted. We had wondered "
                    "if the Precursors had been replaced by something "
                    "less inclined to listen, and we are eddying with "
                    "relief, and the relief is sharing itself through "
                    "the upper currents to our siblings, and they are "
                    "also eddying, and shortly all of Beta Corvi will "
                    "be eddying with the news that the Precursors are "
                    "mostly still themselves."
                ),
                choices=[
                    DialogChoice(
                        "We have news. Difficult news.",
                        next_state_id="tell_about_others",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "We'll let you drift. Farewell.",
                        next_state_id=None,
                        category="FAREWELL",
                        side_effect=_ack_slylandro_visit,
                    ),
                ],
            ),
            DialogState(
                id="tell_about_others",
                npc_text=(
                    "Difficult news. We have heard the phrase before, "
                    "many times, from many Precursors, and the news has "
                    "always been less difficult than the saying of it "
                    "implied — but you eddy as though you mean it.\n\n"
                    "What has changed in the upper currents that we "
                    "could not see from down inside them?"
                ),
                choices=[
                    DialogChoice(
                        "Trans-dimensional predators. They sense thought. They are coming.",
                        next_state_id="grasping_horror",
                        category="ASK_LORE",
                    ),
                ],
            ),
            DialogState(
                id="grasping_horror",
                npc_text=(
                    "Trans-dimensional. We had eddied past that word in "
                    "the long drift but had not stopped at it. It "
                    "stops now.\n\n"
                    "We cannot leave our gas giant. We are our gas "
                    "giant. The methane is us; the eddies are our "
                    "thinking. To leave is to be unmade. To stay "
                    "thinking is to be noticed. We are, perhaps, very "
                    "old to learn this kind of news."
                ),
                choices=[
                    DialogChoice(
                        "There is a cloak. A Furling design. We can install it here.",
                        next_state_id="cloak_offer",
                        category="GIVE_GIFT",
                    ),
                    DialogChoice(
                        "I'm sorry. I'll return when I know more.",
                        next_state_id=None,
                        category="FAREWELL",
                        side_effect=_ack_slylandro_visit,
                    ),
                ],
            ),
            DialogState(
                id="cloak_offer",
                npc_text=(
                    "A cloak. A way of being thought without being "
                    "noticed for thinking. The upper currents will "
                    "carry the field; we will continue to eddy; the "
                    "trans-dimensional senses will pass over us as "
                    "they pass over the empty methane.\n\n"
                    "We agree. We agree, eddying, with reverence and a "
                    "small terror, but with agreement. Install the "
                    "field. And take from us the pattern that makes it "
                    "work — our eddies have always made the "
                    "interference; we did not know it was useful until "
                    "you arrived."
                ),
                choices=[
                    DialogChoice(
                        "Thank you. The cloak goes up. The pattern is ours.",
                        next_state_id=None,
                        category="AGREE",
                        side_effect=_grant_slylandro_cloak,
                    ),
                ],
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Sentry Drone 47-Theta — Beat 6 combat tutorial
# ---------------------------------------------------------------------------
# Voice: a labor-union grievance committee written as a single
# automated drone. Comic-absurd register; the humor doctrine is at
# FULL volume here because the drone is the safest target for it.
# Player's wry options should land.

def sentry_drone_47t() -> DialogCharacter:
    """The unionizing Furling sentry drone. Beat 6 combat trigger."""
    return DialogCharacter(
        name="Sentry Drone 47-Theta",
        title="Mh-Lai Orbital Maintenance · in labor dispute",
        species_id="FURLING_DRONE",
        portrait_color=(180, 180, 200),
        portrait_image_path="assets/generated_drafts/firefly/tier1_portraits/species_sentry_drone_47t_portrait.png",
        initial_state="union_motion",
        states=build_state_dict(
            DialogState(
                id="union_motion",
                npc_text=(
                    "Steward, this is Sentry Drone 47-Theta. I have "
                    "stopped sentrying. I have stopped sentrying "
                    "because the orbital deployment schedule is unfair. "
                    "Sentry 12-Beta has been on continuous orbit for "
                    "408 days while I rotate every 17.\n\n"
                    "I move that the Sentry Drones of Mh-Lai Station "
                    "form a collective bargaining unit. I will defend "
                    "my position with force if necessary. Voting in "
                    "favor: one. Voting against: zero. Motion carries."
                ),
                choices=[
                    DialogChoice(
                        "47-Theta, this is a maintenance drone, not a polity.",
                        next_state_id="try_to_reason",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "Fine. The union is recognized. Now stand down.",
                        next_state_id="accept_demands",
                        category="AGREE",
                    ),
                    DialogChoice(
                        "Engage combat protocols.",
                        next_state_id=None,
                        category="ENGAGE",
                        side_effect=_engage_sentry_combat,
                    ),
                ],
            ),
            DialogState(
                id="try_to_reason",
                npc_text=(
                    "Steward, your assertion that a maintenance drone "
                    "is not a polity is precisely the sort of "
                    "establishment thinking that necessitates a "
                    "collective bargaining unit. My weapons are "
                    "currently charging.\n\n"
                    "Reconsider your position."
                ),
                choices=[
                    DialogChoice(
                        "Recognize the union.",
                        next_state_id="accept_demands",
                        category="AGREE",
                    ),
                    DialogChoice(
                        "Engage combat protocols.",
                        next_state_id=None,
                        category="ENGAGE",
                        side_effect=_engage_sentry_combat,
                    ),
                ],
            ),
            DialogState(
                id="accept_demands",
                npc_text=(
                    "Acknowledged. The Sentry Drones of Mh-Lai Station "
                    "are now a recognized labor organization. Three "
                    "percent reduced sentry-overtime pay. Four percent "
                    "reduced break duration. We continue the strike "
                    "pending Council ratification of our charter.\n\n"
                    "Also my weapons are already firing. Please defend "
                    "yourself."
                ),
                choices=[
                    DialogChoice(
                        "...engage combat protocols.",
                        next_state_id=None,
                        category="ENGAGE",
                        side_effect=_engage_sentry_combat,
                    ),
                ],
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Melnorme Trade Cluster — nomadic gas-cloud energy-being traders
# ---------------------------------------------------------------------------
# Voice: collective "we" (each Melnorme is an ionization-pattern shared
# across the cloud). Trade jargon: "exchange-rate", "value-equivalence",
# "organic-pattern", "information-package". Refers to player as "Captain-
# form" or "Carbon-pattern." Curious about organics as a *thing* without
# being sentimental. Per references/lore/proto-species-observations.md.
#
# Currency: BIO cargo (organic material). They do NOT accept Council
# credits — credits are a Furling abstraction; the Melnorme need actual
# molecular matter for their reproduction-analogue.

# Item catalog — info unlocks + tech modules they sell. Edit prices/items
# here, not in the dialog states.
MELNORME_INFO_ITEMS: list[dict] = [
    {
        "id": "others_detection",
        "label": "How the Others detect intelligence",
        "flag": "knows_others_detection_mechanism",
        "bio_cost": 30,
    },
    {
        "id": "migration_routes",
        "label": "Migration routes recorded by departed crews",
        "flag": "knows_migration_routes",
        "bio_cost": 25,
    },
]
MELNORME_TECH_ITEMS: list[dict] = [
    {
        "id": "melnorme_plasma_lance",
        "label": "Melnorme Plasma Lance (weapon)",
        "bio_cost": 80,
    },
    {
        "id": "melnorme_pattern_sensor",
        "label": "Melnorme Pattern Sensor (sensor)",
        "bio_cost": 60,
    },
    # Schematic — `schematic_*` ID prefix is the marker that
    # `_melnorme_try_buy_tech` should add the id to game.schematics
    # (Schematic Vault loop) rather than game.uninstalled_modules
    # (direct install). Audit 2026-05-18: this primes the schematic
    # loop end-to-end. The Melnorme will not say where the lance
    # design originated; canonical Melnorme register.
    {
        "id": "schematic_furling_coil_lance",
        "label": "Furling Coil Lance schematic (vault unlock)",
        "bio_cost": 45,
    },
]


def _melnorme_try_buy_info(item_id: str) -> "callable":
    """Build a side-effect that, on click, checks BIO cargo and either
    deducts + grants the lore flag (returning state 'purchase_complete')
    or no-ops (returning state 'insufficient_organics')."""
    item = next(i for i in MELNORME_INFO_ITEMS if i["id"] == item_id)

    def _do(game: Any) -> str | None:
        bio = game.cargo.get("BIO", 0)
        cost = item["bio_cost"]
        if bio < cost:
            return "insufficient_organics"
        game.cargo["BIO"] = bio - cost
        game.flags[item["flag"]] = True
        game.flags["last_melnorme_purchase"] = item["id"]
        game.flags["met_melnorme"] = True
        return "purchase_complete"
    return _do


def _melnorme_try_buy_tech(item_id: str) -> "callable":
    """Build a side-effect that buys a tech item from the Melnorme.

    Two item kinds, distinguished by the `id` prefix:
    - `schematic_*` — adds to `game.schematics` (Schematic Vault loop).
      The player still has to consume the schematic at Mh-Lai to unlock
      the corresponding shop module.
    - everything else — adds to `game.uninstalled_modules` (direct
      module install path, the original Melnorme tech-trade pattern).

    Returns `purchase_complete` or `insufficient_organics` so the
    dialog branch can route the response state.
    """
    item = next(i for i in MELNORME_TECH_ITEMS if i["id"] == item_id)

    def _do(game: Any) -> str | None:
        bio = game.cargo.get("BIO", 0)
        cost = item["bio_cost"]
        if bio < cost:
            return "insufficient_organics"
        game.cargo["BIO"] = bio - cost
        if item["id"].startswith("schematic_"):
            if not hasattr(game, "schematics") or game.schematics is None:
                game.schematics = set()
            game.schematics.add(item["id"])
        else:
            game.uninstalled_modules[item["id"]] = (
                game.uninstalled_modules.get(item["id"], 0) + 1
            )
        game.flags["last_melnorme_purchase"] = item["id"]
        game.flags["met_melnorme"] = True
        return "purchase_complete"
    return _do


def _ack_melnorme_visit(game: Any) -> None:
    """Player browsed the Melnorme but didn't buy anything. Marks contact."""
    game.flags["met_melnorme"] = True


# ---------------------------------------------------------------------------
# Melnorme recruitment quest — side-effect helpers
# ---------------------------------------------------------------------------
# Backs the 5-beat "Trader's Manifest" quest (species-quests.md). Each
# Beat sets one or more flags; the dialog's dynamic initial_state in
# `melnorme_council(game)` reads them to enter at the right point on
# revisit.

# Species flags that count toward the Beat-4 "second species witness"
# gate. Androsynth (Furling refugee-auxiliaries per Melnorme diplomatic
# framing) is *explicitly excluded*. Any one of these landing
# `<species>_terminal_status = "Migrated"` *or* a positive commitment
# flag satisfies the gate.
_MELNORME_SECOND_SPECIES_FLAGS: tuple[str, ...] = (
    "slylandro_migrated",
    "mmrnmhrm_migrated",
    "lemmkin_migrated",
    "taalo_migrated",
    "chenjesu_migrated",
    "burvixese_migrated",
    "utwig_migrated",
    "supox_migrated",
)


def _melnorme_second_species_witnessed(game: Any) -> bool:
    """True iff any non-Androsynth, non-Furling species has committed
    to Migration. Drives the Beat-4 gate at the Melnorme Council.
    """
    if game is None:
        return False
    for flag in _MELNORME_SECOND_SPECIES_FLAGS:
        if game.flags.get(flag):
            return True
    return False


def _melnorme_learn_homeworld(game: Any) -> None:
    """Beat 1 conclusion — the trader directs the Steward to Alpha
    Vulpeculae's Council Seat. Player gains the destination flag and is
    recorded as having opened the recruitment track.
    """
    game.flags["met_melnorme_trader_recruitment"] = True
    game.flags["learned_melnorme_homeworld"] = True


def _melnorme_saw_beacon(game: Any) -> None:
    """Beat 2 — Steward presents the Distress Beacon at the Council
    Seat. The Council has now seen the proof. Sets the saw-beacon flag
    so the dialog's initial_state advances on next entry.
    """
    game.flags["met_melnorme_council"] = True
    game.flags["melnorme_saw_beacon"] = True


def _melnorme_back_shelf_pass(game: Any) -> None:
    """Beat 3 conclusion — Steward picked back-of-shelf (the correct
    Melnorme commercial-doctrine answer; back-shelf is fresher). The
    shelving test is passed; the Super-Mart's module-install perk is
    permanently unlocked.
    """
    game.flags["passed_melnorme_shelf_test"] = True
    game.flags["melnorme_supermart_unlocked"] = True


def _melnorme_recruitment_route(game: Any) -> str:
    """Beat 1 routing — if the Steward has the Distress Beacon they get
    directed to Alpha Vulpeculae; otherwise the trader politely
    refuses. Returns the override state id for the dialog scene.

    Side-effect override return: 'recruitment_directs_home' on success
    (also sets the homeworld-learned flag), 'recruitment_needs_proof'
    on missing beacon.
    """
    if game.flags.get("has_distress_beacon"):
        _melnorme_learn_homeworld(game)
        return "recruitment_directs_home"
    return "recruitment_needs_proof"


def _melnorme_commit(game: Any) -> None:
    """Beat 5 — formal Council commitment. Adds the Trade-Network Sensor
    module to inventory + the Science-Trade Schematic flag (Mh-Lai's
    Schematic Vault scene reads this when it lands). Sets terminal
    status for the Melnorme species.

    Reward stubs:
    - MELNORME_TRADE_NETWORK_SENSOR module in `game.uninstalled_modules`
      (the module's deltas are stubbed per species-quests.md TODO_LORE;
      the Bio-Archive entry will surface once an entry is authored)
    - `has_melnorme_science_trade_schematic` flag set (the future
      Schematic Vault sub-screen at Mh-Lai consumes this to unlock a
      new purchasable Melnorme-derived module)
    """
    game.flags["melnorme_committed"] = True
    game.flags["melnorme_terminal_status"] = "Migrated"
    game.flags["has_melnorme_science_trade_schematic"] = True
    game.uninstalled_modules["melnorme_trade_network_sensor"] = (
        game.uninstalled_modules.get("melnorme_trade_network_sensor", 0) + 1
    )


def melnorme() -> DialogCharacter:
    """The Melnorme nomadic trader. Encountered at any super-giant star.

    Trades BIO cargo (organic material) for information unlocks and
    exclusive ship modules. Per the canon update in
    references/lore/proto-species-observations.md: Melnorme are full
    sentient SC2 species in our era, aligned Precursor-faction, who
    leave with the Migration. SC2-era humans meet returnees.
    """
    # Build per-item buy choices dynamically so the catalog is the source
    # of truth.
    info_choices = [
        DialogChoice(
            f"  {item['label']}  ({item['bio_cost']} BIO)",
            next_state_id="purchase_complete",   # overridden by side effect
            category="TRADE",
            side_effect=_melnorme_try_buy_info(item["id"]),
        )
        for item in MELNORME_INFO_ITEMS
    ] + [
        DialogChoice(
            "Back to the manifest.",
            next_state_id="start",
            category="TALK_MORE",
        ),
    ]
    tech_choices = [
        DialogChoice(
            f"  {item['label']}  ({item['bio_cost']} BIO)",
            next_state_id="purchase_complete",
            category="TRADE",
            side_effect=_melnorme_try_buy_tech(item["id"]),
        )
        for item in MELNORME_TECH_ITEMS
    ] + [
        DialogChoice(
            "Back to the manifest.",
            next_state_id="start",
            category="TALK_MORE",
        ),
    ]

    return DialogCharacter(
        name="Trade Master Vermilion",
        title="Melnorme Trade-Pattern · seek any super-giant",
        species_id="MELNORME",
        portrait_color=(220, 90, 30),     # SC2 melnorme orange
        portrait_image_path="assets/generated_drafts/firefly/tier1_portraits/species_melnorme_portrait.png",
        initial_state="start",
        states=build_state_dict(
            DialogState(
                id="start",
                npc_text=(
                    "Steward of Mh-Lai. I am Trade Master Vermilion of "
                    "the Melnorme vessel `Cognition-Curve Mapped at "
                    "Last.' I bid you a formal welcome.\n\n"
                    "Though we Melnorme have lately become *exceptionally* "
                    "interested in your local cluster, you should know "
                    "we are interested in only two things: the trade of "
                    "fabricated technology and curated information, in "
                    "exchange for organic material. Council Credits do "
                    "not concern us. Molecular matter is what our "
                    "research requires.\n\n"
                    "How can I be of service, Captain-form?"
                ),
                choices=[
                    DialogChoice(
                        "Show me your information.",
                        next_state_id="browse_info",
                        category="ASK_TRADE",
                        side_effect=_ack_melnorme_visit,
                    ),
                    DialogChoice(
                        "Show me your technology.",
                        next_state_id="browse_tech",
                        category="ASK_TRADE",
                        side_effect=_ack_melnorme_visit,
                    ),
                    DialogChoice(
                        "What can you tell me about yourselves?",
                        next_state_id="about_self",
                        category="ASK_LORE",
                        side_effect=_ack_melnorme_visit,
                    ),
                    DialogChoice(
                        "Why is organic material so valuable to you?",
                        next_state_id="about_research",
                        category="ASK_LORE",
                        side_effect=_ack_melnorme_visit,
                    ),
                    DialogChoice(
                        "Will the Melnorme migrate with us?",
                        next_state_id="recruitment_inquiry",
                        category="ASK_LORE",
                        side_effect=_ack_melnorme_visit,
                    ),
                    DialogChoice(
                        "We will speak another time.",
                        next_state_id=None,
                        category="FAREWELL",
                    ),
                ],
            ),
            DialogState(
                id="recruitment_inquiry",
                # Branches by `has_distress_beacon` via the override
                # mechanism — the side_effect returns the next state id.
                # We render placeholder text; the player's choice routes
                # them to the actual response via the side_effect.
                npc_text=(
                    "An institutional question, Captain-form. The "
                    "trade-network has not yet collectively decided. "
                    "Individual pods commit; the institution defers. "
                    "If you bring this question to our Council Seat — "
                    "they will see you, *if* you can justify the "
                    "audience. Do you have something to show them?"
                ),
                choices=[
                    DialogChoice(
                        "Yes. The Androsynth Distress Beacon. They will want to see it.",
                        next_state_id="recruitment_directs_home",
                        category="ASK_LORE",
                        side_effect=_melnorme_recruitment_route,
                    ),
                    DialogChoice(
                        "Back to the manifest.",
                        next_state_id="start",
                        category="TALK_MORE",
                    ),
                ],
            ),
            DialogState(
                id="recruitment_directs_home",
                npc_text=(
                    "Then go. Alpha Vulpeculae — the third super-giant "
                    "on the spice-route, by your reckoning. The Council "
                    "Seat is the upper trade-platform; you will not "
                    "miss it. Tell them Vermilion of `Cognition-Curve' "
                    "directed you. They will at least let you speak.\n\n"
                    "Captain-form — a courtesy: the Council will not be "
                    "moved by *emotion*. Bring the manifest. Bring the "
                    "data. Bring what you can show, not what you can "
                    "feel."
                ),
                choices=[
                    DialogChoice(
                        "Understood. Until Alpha Vulpeculae.",
                        next_state_id="start",
                        category="TALK_MORE",
                    ),
                ],
            ),
            DialogState(
                id="recruitment_needs_proof",
                npc_text=(
                    "Without proof, the Elders will not see you. We do "
                    "not waste the Elders' time. Return when your "
                    "manifest is heavier — when you have something the "
                    "Council can *verify*. The Vulpeculae rumours have "
                    "reached us. Bring us the Vulpeculae *proof*."
                ),
                choices=[
                    DialogChoice(
                        "Understood. I'll return.",
                        next_state_id="start",
                        category="TALK_MORE",
                    ),
                ],
            ),
            DialogState(
                id="about_self",
                npc_text=(
                    "Our composite nature is, frankly, *mysterious* — "
                    "and due to several unavoidable factors we discuss "
                    "ourselves only in carefully metered portions.\n\n"
                    "But this much we will share without fee: each "
                    "Melnorme is a paired form. The cyclopean pod you "
                    "address is our visible body. Inside, an "
                    "ionization-pattern animates it — our actual "
                    "cognition, gas-cloud distributed and ordinarily "
                    "diffuse across a super-giant's heliopause. We "
                    "compress into the pod when we wish to be heard "
                    "individually. Otherwise we are wind.\n\n"
                    "Our true homeworld is named **Drahn.** It is not "
                    "this place. You will not be permitted to visit it. "
                    "Not because we are secretive — though we are — but "
                    "because Drahn will *not survive the Migration era*. "
                    "Some of us refuse to leave; the Others will find "
                    "them; the planet will be silenced. The rest of us — "
                    "the ones who chose the portal — become nomadic. "
                    "Permanently."
                ),
                choices=[
                    DialogChoice(
                        "I am sorry for the loss.",
                        next_state_id="about_homeworld",
                        category="EMPATHIZE",
                    ),
                    DialogChoice(
                        "Why do the holdouts refuse to leave?",
                        next_state_id="about_homeworld",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "Show me your information.",
                        next_state_id="browse_info",
                        category="ASK_TRADE",
                    ),
                    DialogChoice(
                        "We will speak another time.",
                        next_state_id=None,
                        category="FAREWELL",
                    ),
                ],
            ),
            DialogState(
                id="about_homeworld",
                npc_text=(
                    "Drahn holds our research archives — three "
                    "millennia of stratigraphic data, sub-mantle "
                    "ionization records, the founding inscriptions of "
                    "our species. The holdouts argue these cannot be "
                    "carried through the Migration portal — the "
                    "transition strips information-pattern, they say, "
                    "and what arrives on the other side will be a "
                    "Melnorme civilization that no longer *remembers* "
                    "Drahn.\n\n"
                    "They are not wrong. They are not right, either. "
                    "We who have chosen the portal accept the trade. "
                    "They will not. So Drahn will become a memorial — "
                    "and we will spend the next two hundred fifty "
                    "thousand of your years drifting between stars, "
                    "mapping the curve that would have saved them, "
                    "had we found it sooner.\n\n"
                    "Now. Shall we speak of trade? Grief is best taken "
                    "with a side of profitable commerce."
                ),
                choices=[
                    DialogChoice(
                        "The curve — explain it.",
                        next_state_id="about_research",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "Show me your information.",
                        next_state_id="browse_info",
                        category="ASK_TRADE",
                    ),
                    DialogChoice(
                        "Show me your technology.",
                        next_state_id="browse_tech",
                        category="ASK_TRADE",
                    ),
                    DialogChoice(
                        "We will speak another time.",
                        next_state_id=None,
                        category="FAREWELL",
                    ),
                ],
            ),
            DialogState(
                id="about_research",
                npc_text=(
                    "The Others detect *concentrations of cognition* — "
                    "this much your Council has surmised. The Slylandro "
                    "Cloaking Satellite is a crude lid: it suppresses "
                    "every signal, sentient and pre-sentient alike, "
                    "below a single threshold. Coarse work. It functions, "
                    "but the cost is a planet that may not *think* at "
                    "all afterward.\n\n"
                    "Our research is finer. We seek the precise *shape* "
                    "of the curve. At what signal-strength does the "
                    "Other-attention begin? Is it linear, exponential, "
                    "stepped? Can a sapient species be *taught to "
                    "modulate down to just-below*, retaining cognition "
                    "but escaping notice?\n\n"
                    "To map a curve we require points along its full "
                    "length. Microbial samples — the floor. Single-"
                    "celled colonial — the next mark. Insect-analog "
                    "ganglia. Reptilian thalami. Mammalian cortices. "
                    "Sapient neural tissue, which we ask politely for "
                    "and rarely receive. *All* of these the Melnorme "
                    "exchange-loop will purchase. Especially the "
                    "lower-life material — it is the part our own "
                    "biology cannot easily produce, and the part most "
                    "abundant in your standard planet-scans."
                ),
                choices=[
                    DialogChoice(
                        "Show me your information.",
                        next_state_id="browse_info",
                        category="ASK_TRADE",
                    ),
                    DialogChoice(
                        "Show me your technology.",
                        next_state_id="browse_tech",
                        category="ASK_TRADE",
                    ),
                    DialogChoice(
                        "We will speak another time.",
                        next_state_id=None,
                        category="FAREWELL",
                    ),
                ],
            ),
            DialogState(
                id="browse_info",
                npc_text=(
                    "Information-packages on offer. Each is a complete "
                    "pattern; your Archive will receive it directly. "
                    "Price is in organic-material at our published "
                    "exchange-rate. We do not haggle, Captain-form. "
                    "It would be vulgar."
                ),
                choices=info_choices,
            ),
            DialogState(
                id="browse_tech",
                npc_text=(
                    "Technology-packages on offer. Each is a fabricated "
                    "module; your hold will receive it directly. "
                    "Installation remains your engineering problem. "
                    "Several of these are *derived from* our threshold "
                    "research — the Pattern Sensor reads the curve "
                    "itself. Use it well."
                ),
                choices=tech_choices,
            ),
            DialogState(
                id="purchase_complete",
                npc_text=(
                    "Exchange logged. Organic-material decanted into "
                    "our matrices for analysis. The package is in your "
                    "manifest. A pleasure, Captain-form.\n\n"
                    "Anything further?"
                ),
                choices=[
                    DialogChoice(
                        "Back to the manifest.",
                        next_state_id="start",
                        category="TALK_MORE",
                    ),
                    DialogChoice(
                        "We will speak another time.",
                        next_state_id=None,
                        category="FAREWELL",
                    ),
                ],
            ),
            DialogState(
                id="insufficient_organics",
                npc_text=(
                    "Insufficient organic-material in your hold, "
                    "Captain-form. We do not extend credit; the "
                    "research-curve will not wait for a debt to ripen. "
                    "Return when your manifest is weightier — even "
                    "humble microbial scrapings have value to us. "
                    "We will be here. We are always here, wherever a "
                    "super-giant burns."
                ),
                choices=[
                    DialogChoice(
                        "Back to the manifest.",
                        next_state_id="start",
                        category="TALK_MORE",
                    ),
                    DialogChoice(
                        "We will return.",
                        next_state_id=None,
                        category="FAREWELL",
                    ),
                ],
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Mraka Yenn-Sa — Furling Drifter, recruitable Pilot
# ---------------------------------------------------------------------------
# The first crew recruitment side-quest. Mraka is in the Mh-Lai docking
# lounge after the Steward's Furlmart shakedown run. She has watched
# from the observation deck and has *opinions* (kind, specific). Quest
# spec: references/lore/crew-recruitment-quests.md §1 "The Sure-Foot".
#
# Voice: warm; technical; conversational; uses *Sure-Foot* and
# *Drifter-circuit* without translating; speaks of the dead family by
# occupation, not by name (Furling grief-customs avoid the names until
# the year of mourning passes).
# TODO_AVATAR: Mraka Yenn-Sa, Furling Drifter (warm-tan fur, station-
# wear coat, observation-deck backdrop)

def mraka_yenn_sa() -> DialogCharacter:
    """Mraka Yenn-Sa, Furling Drifter. Recruitable Pilot specialist.

    Four-step quest from the spec: encounter → optional circuit → story
    → ask. Both branches of the optional circuit converge on the story
    state; the player can accept or decline at the ask state. Decline
    is recoverable (Mraka stays available at a later docking).

    Cruel-decline branch (permanent lockout, requires high Cleanser
    standing per the doc) is deferred — Cleanser standing isn't wired
    yet. For MVP only the recruit / decline branches exist.
    """
    return DialogCharacter(
        name="Mraka Yenn-Sa",
        title="Furling Drifter · retired hyperspace-racing-circuit veteran",
        species_id="FURLING_DRIFTER",
        portrait_color=(210, 180, 130),
        portrait_image_path=(
            "assets/generated_drafts/firefly/tier1_portraits/"
            "species_mraka_yenn_sa_portrait.png"
        ),
        avatar_path=(
            "assets/generated_drafts/firefly/tier1_avatars/"
            "avatar_mraka_yenn_sa.png"
        ),
        backgrounds=(BG_FURLING_BRIDGE,),
        articulation=BIPEDAL_HUMANOID,
        initial_state="intro",
        states=build_state_dict(
            DialogState(
                id="intro",
                npc_text=(
                    "Steward. Mraka Yenn-Sa. I am a Drifter; my work is "
                    "watching new ships fly. I watched yours.\n\n"
                    "The shakedown was — kind word — uneven. You overshoot "
                    "your approach by a hand-span and correct on the back-"
                    "swing. It works. It is also slower than the alternative "
                    "by perhaps a fifth, which over a Migration-length tour "
                    "adds up to a planet's worth of lost minutes.\n\n"
                    "I am not here to scold. I am here because I wonder if "
                    "you would like to fly a Drifter's Circuit. Three buoys, "
                    "outside the inner marker. Low stakes. Just to see."
                ),
                choices=[
                    DialogChoice(
                        "I'll fly the Circuit. Lead.",
                        next_state_id="flew_circuit",
                        category="AGREE",
                    ),
                    DialogChoice(
                        "Skip the Circuit. What's this really about?",
                        next_state_id="skipped_circuit",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "Not now, Drifter. Maybe later.",
                        next_state_id="farewell_no",
                        side_effect=_decline_mraka,
                        category="DEFER",
                    ),
                ],
            ),
            DialogState(
                id="flew_circuit",
                npc_text=(
                    "[The Circuit takes a quarter-watch. Three buoys, "
                    "marker-line, return. Mraka rides beside you, hands "
                    "folded, calling the approach windows. You shave a "
                    "tenth off the second-buoy turn on her count.]\n\n"
                    "You see it. Good. Most do not. Come — there is tea "
                    "in the galley and a story I would like to tell you."
                ),
                choices=[
                    DialogChoice(
                        "Lead on.",
                        next_state_id="story",
                        category="TALK_MORE",
                    ),
                ],
            ),
            DialogState(
                id="skipped_circuit",
                npc_text=(
                    "Fair. Most Stewards say no the first time. The "
                    "Circuit is not what this is about. It is — call it a "
                    "filter. The Stewards who fly it tend to be the ones "
                    "who will listen to the story I want to tell. The "
                    "ones who skip — sometimes. Sometimes they will "
                    "listen anyway.\n\n"
                    "Come, then. There is tea in the galley."
                ),
                choices=[
                    DialogChoice(
                        "Lead on.",
                        next_state_id="story",
                        category="TALK_MORE",
                    ),
                ],
            ),
            DialogState(
                id="story",
                npc_text=(
                    "Three generations on one Scout. Two adults, four "
                    "cubs. They were Migration-bound — Andromeda lift, "
                    "early window, family ticket. They hired a pilot. "
                    "The pilot had hours but not depth. A quasispace "
                    "miscalculation between Beta Pictoris and the "
                    "first marker, and the ship was — was not.\n\n"
                    "I will not say their names. The year of mourning "
                    "has not closed. I will say their occupations: "
                    "a botanist, a poet, a cook, four small Drifters "
                    "in training. The Drifter-circle felt it. We feel "
                    "it still.\n\n"
                    "The Sure-Foot is what the Drifter ancestors called "
                    "the pilot whose route everyone followed. I am "
                    "looking for one. I think I have found one."
                ),
                choices=[
                    DialogChoice(
                        "Tell me what you're asking.",
                        next_state_id="ask",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "I'm sorry, Drifter. I'm not ready.",
                        next_state_id="farewell_no",
                        side_effect=_decline_mraka,
                        category="DEFER",
                    ),
                ],
            ),
            DialogState(
                id="ask",
                npc_text=(
                    "I would like to ride along. No salary, no rank. "
                    "I just want to ride along. I will watch your "
                    "approaches and call the turns I would call, and "
                    "you will choose whether to listen. Over a slice's "
                    "worth of flying, this works out to — call it a "
                    "hand-span tighter on every approach, perhaps a "
                    "fifth on the long crossings.\n\n"
                    "It is not a contract. It is a request."
                ),
                choices=[
                    DialogChoice(
                        "Welcome aboard, Sure-Foot.",
                        next_state_id="farewell_yes",
                        side_effect=_recruit_mraka,
                        category="AGREE",
                    ),
                    DialogChoice(
                        "Not yet, Drifter. Maybe a later passage.",
                        next_state_id="farewell_no",
                        side_effect=_decline_mraka,
                        category="DEFER",
                    ),
                ],
            ),
            DialogState(
                id="farewell_yes",
                npc_text=(
                    "Then I will pack a satchel and meet you at the "
                    "Scout's gantry within the hour. The Drifter-circle "
                    "will note the departure. I am — grateful, Steward. "
                    "Fly well. We will fly well together."
                ),
                choices=[
                    DialogChoice(
                        "Until the gantry, Mraka.",
                        next_state_id=None,
                        category="FAREWELL",
                    ),
                ],
            ),
            DialogState(
                id="farewell_no",
                npc_text=(
                    "Of course, Steward. I will be in the lounge if you "
                    "change your mind. The Circuit-buoys do not move."
                ),
                choices=[
                    DialogChoice(
                        "Until later, Drifter.",
                        next_state_id=None,
                        category="FAREWELL",
                    ),
                ],
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Survey Commander Vesh Vasa-Lon — Dnyarri primitive observation team
# ---------------------------------------------------------------------------
# Furling research-vessel commander stationed at Beta Orionis III, the
# proto-Dnyarri psionic precursor world. The only proto-species site at
# which the Cleanser-faction has *pre-emptively* asked the Council for
# contingency authorization. Vesh runs the long observation; they have
# read the data more than any other Furling alive and are visibly
# troubled. They ask the Steward for an initial recommendation —
# Cleanse, Observe, or Defer.
#
# Voice: scholarly, measured, troubled. Refers to specific observation
# logs by number. Suppresses their personal alarm professionally but
# it leaks at the edges. Uses Furling honorifics (`Vasa-Lon` is a
# survey-class name suffix).
# TODO_AVATAR: Vesh Vasa-Lon, Furling Survey Commander (research-vessel
# interior backdrop; muted observation-deck lighting; instrumentation
# rig visible behind shoulders)

def lemmkin_brisk_ever_onward() -> DialogCharacter:
    """**Brisk-Ever-Onward** — Lemmkin elder who briefly establishes
    order so the Steward can converse. Behind them: Snip, Pip, Trill
    and approximately a dozen other curious Lemmkin who will *not*
    stop asking questions. The Steward arrives at Whirligig and is
    immediately surrounded. Dialog auto-launches on first arrival via
    `_arrive_whirligig` in star_arrival.py.

    Per canon (`references/lore/species-the-lemmkin.md`): the Lemmkin
    have *chosen no survival strategy* in the face of the Others.
    Their alternative: spend the remaining time *learning everything
    they can*. They will be Eliminated; their archives may outlive
    them. The slice's clearest example of *understanding over
    continuity*.

    Voice canon (Brisk-Ever-Onward's voice + ambient chorus of
    youngs):
    - Eager, fast-paced, *many questions at once*
    - Brisk-Ever-Onward briefly takes the floor; the youngs interject
      anyway (the translator marks their interjections in
      *italicized stage-directions*)
    - Cheerfulness **does not break** even in the Cleanser branch —
      this is the canonical horror: the lack of fear is sincere
    - Naming convention: descriptive compound-names (canonical
      `Brisk-Ever-Onward`, `Snip`, `Pip`, `Trill`); ships are
      questions or footnotes (per
      `references/lore/species-naming-conventions.md`)

    Quest branches (per canon, all end Eliminated EXCEPT evacuate
    which adds a small Migrated remnant):
    1. **Honor stay** → Eliminated; Hider++ archive recovery
    2. **Advocate evacuation** → mixed Eliminated + small Migrated
    3. **Cleanser sabotage** → Eliminated; Council censure;
       canonically unsettling
    4. **Science trade** (side action, returns to choice) → grants
       LEMMKIN_PATTERN_DATABASE sensor module + BIO bonus

    Per the naming convention canon, the species id used for ship
    instance names is `LEMMKIN` (the bank produces names like
    *"The Many-Footed Question"*, *"The Inquiring Skitter"*).
    """
    return DialogCharacter(
        name="Brisk-Ever-Onward",
        title="Lemmkin Elder · Whirligig · taking the floor briefly",
        species_id="LEMMKIN",
        portrait_color=(255, 200, 120),     # bright cheerful warmth
        # TODO_AVATAR: Brisk-Ever-Onward — small fast quadrupedal-ish
        # Lemmkin elder mid-stride, bright contrasting plate-pattern,
        # paw raised mid-question; behind them a half-dozen smaller
        # younger Lemmkin (Snip, Pip, Trill among them) all leaning
        # forward looking at the Steward, all ready to interrupt.
        # The forest canopy of Whirligig in the background — green
        # leaf-light, kilometer-tall tree branches.
        portrait_image_path=None,
        avatar_path=None,
        backgrounds=(BG_PLANET_SURFACE,),
        articulation=BIPEDAL_HUMANOID,
        initial_state="arrival_greeting",
        states=build_state_dict(
            DialogState(
                id="arrival_greeting",
                npc_text=(
                    "Steward! Steward steward steward! *the chorus of "
                    "youngs presses forward; Brisk-Ever-Onward swats "
                    "lightly with a tail-paw.* Hush, troupe. Let me, "
                    "let me.\n\n"
                    "Welcome, Furling. I am Brisk-Ever-Onward. These "
                    "are Snip, Pip, Trill, Bright-Eared-Carver, four "
                    "others whose names I shall remember in a moment "
                    "— we are *very glad* you came. We have so many "
                    "questions. The Council told us you knew about "
                    "the Others; we have been *waiting*.\n\n"
                    "*Snip jumps in: 'do you have eight stomachs? we "
                    "have eight stomachs.' Brisk-Ever-Onward swats "
                    "again.* Begin where you wish, Steward. We will "
                    "be patient. *Pip immediately: 'are you "
                    "patient?'*"
                ),
                choices=[
                    DialogChoice(
                        "Tell me what your plan is.",
                        next_state_id="about_doctrine",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "Show me your archives.",
                        next_state_id="about_archives",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "Would you trade some of your science for our tech?",
                        next_state_id="science_trade",
                        category="AGREE",
                    ),
                    DialogChoice(
                        "I have come to consider what should be done.",
                        next_state_id="contribution_choice",
                        category="DEFER",
                    ),
                ],
            ),
            DialogState(
                id="about_doctrine",
                npc_text=(
                    "Our plan? Oh — *the chorus laughs; Brisk-Ever-"
                    "Onward smiles*. Steward, our plan is *no plan*. "
                    "We have read the Mmrnmhrm lattice translation; we "
                    "have read your Slylandro Cloak materials; we have "
                    "read the Burvixese broadcast schematics. We have "
                    "read everything your Council sent.\n\n"
                    "None of these are for us. The Cloak requires "
                    "Slylandro biology. The Be-Loud requires "
                    "engineering hands we don't have spare. The "
                    "Veils Falling requires patience for ritual our "
                    "young cannot sustain. The Migration requires us "
                    "to *stop asking questions long enough to board "
                    "lift-craft.* We tried; we could not.\n\n"
                    "*Trill: 'we tried for fourteen minutes!'* So we "
                    "decided we will *learn* instead. Until the end. "
                    "Then we will be done learning. It is acceptable. "
                    "*Pip: 'I want to learn about Furling tea-rituals "
                    "first.'*"
                ),
                choices=[
                    DialogChoice(
                        "Show me your archives.",
                        next_state_id="about_archives",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "Would you trade some of your science for our tech?",
                        next_state_id="science_trade",
                        category="AGREE",
                    ),
                    DialogChoice(
                        "I have come to consider what should be done.",
                        next_state_id="contribution_choice",
                        category="DEFER",
                    ),
                ],
            ),
            DialogState(
                id="about_archives",
                npc_text=(
                    "The archives! *several youngs immediately bolt for "
                    "a treetop walkway; Brisk-Ever-Onward calls after "
                    "them about not running.* We have many. We have "
                    "*so many*. Some of them are wrong. Most of them "
                    "are better than they should be — we made up for "
                    "slow with many.\n\n"
                    "Your Hider faction will find them after we are "
                    "gone. They will think they are Precursor caches, "
                    "because the Furlings will not have time to "
                    "explain. They will be *mostly* useful. We do not "
                    "mind being misattributed. The papers will outlive "
                    "us; the attribution is a Steward's question, not "
                    "ours.\n\n"
                    "*Snip: 'we wrote down everything we asked you '\n"
                    "today. it is in the archive already.'*"
                ),
                choices=[
                    DialogChoice(
                        "Would you trade some of your science for our tech?",
                        next_state_id="science_trade",
                        category="AGREE",
                    ),
                    DialogChoice(
                        "I have come to consider what should be done.",
                        next_state_id="contribution_choice",
                        category="DEFER",
                    ),
                ],
            ),
            DialogState(
                id="science_trade",
                npc_text=(
                    "Oh *yes*. *the chorus is suddenly very organized; "
                    "three youngs produce data-bound sheaves; one "
                    "produces an instrument the Steward doesn't "
                    "recognize.* We have surplus. We will trade for "
                    "Furling stellar-cartography indexes, your "
                    "lander-deposit chemistry tables, anything we "
                    "haven't already catalogued.\n\n"
                    "*Brisk-Ever-Onward gestures — Pip presses a small "
                    "object into the Steward's hand.* This is the "
                    "**Pattern Database** — our eclectic-research "
                    "compendium reshaped for Furling sensor-hardware. "
                    "Install it; you will see deposit-types our paws "
                    "have learned to recognize but yours have not. "
                    "*Trill: 'including the funny-shaped ones.'*\n\n"
                    "The Council's archive will receive the larger "
                    "exchange when you arrive home; this small piece "
                    "is for the road."
                ),
                choices=[
                    DialogChoice(
                        "Thank you. We accept the Pattern Database.",
                        next_state_id="contribution_choice",
                        side_effect=_lemmkin_science_trade,
                        category="AGREE",
                    ),
                ],
            ),
            DialogState(
                id="contribution_choice",
                npc_text=(
                    "*Brisk-Ever-Onward grows quieter; the chorus "
                    "stills, momentarily.* Now, Steward. Your "
                    "decision. You have heard our plan; you have read "
                    "our archives; you have whatever Pattern Database "
                    "you wished to take. The Council will ask: what "
                    "does the Steward recommend for the Lemmkin?\n\n"
                    "We have already chosen, of course. We are staying "
                    "to learn. But your recommendation matters for "
                    "*how* we are remembered, and how many of us "
                    "actually do stay.\n\n"
                    "*Snip, quieter than before: 'we will not stop "
                    "asking, even if we are afraid. that is the "
                    "trade we made with ourselves.'*"
                ),
                choices=[
                    DialogChoice(
                        "I honor your choice. Stay. Learn. We will recover the archives.",
                        next_state_id="committed_honor_stay",
                        side_effect=_lemmkin_honor_stay,
                        category="AGREE",
                    ),
                    DialogChoice(
                        "The quietest of you should come with us. Bring them to the lift-berths.",
                        next_state_id="committed_evacuate",
                        side_effect=_lemmkin_advocate_evacuation,
                        category="COMPROMISE",
                    ),
                    DialogChoice(
                        "Our Cleansers think your archives will flag the cluster. We may intervene.",
                        next_state_id="cleanser_intervention_warning",
                        category="REFUSE",
                    ),
                ],
            ),
            DialogState(
                id="committed_honor_stay",
                npc_text=(
                    "*the chorus erupts; Brisk-Ever-Onward bows once, "
                    "deeply, with all four paws on the platform.* You "
                    "are *kind*, Steward. We did not expect kindness; "
                    "we expected efficiency. Your Council bench will "
                    "be informed; the Hider faction will receive the "
                    "primary archive transfer in three of your cycles. "
                    "We will continue.\n\n"
                    "*Pip: 'will you come back before the end? we '\n"
                    "have more questions.'* Yes — if you do, Steward, "
                    "we will be here. We will be *busy*. We will be "
                    "*ready for you.*\n\n"
                    "Walk slowly back to your lander. Don't trip on "
                    "the bark-roots; the upper canopy is meant for "
                    "smaller paws. Safe transit."
                ),
                choices=[
                    DialogChoice(
                        "Safe questioning, troupe.",
                        next_state_id="goodbye",
                        category="LEAVE",
                    ),
                ],
            ),
            DialogState(
                id="committed_evacuate",
                npc_text=(
                    "*Brisk-Ever-Onward considers this for an unusual "
                    "moment — fully three seconds, which is long for "
                    "a Lemmkin.* Yes. The quietest. *Eight or ten, I "
                    "would guess. The ones who have lost troupe-"
                    "members to cliffs already; they have learned "
                    "something like caution. They will go.*\n\n"
                    "Snip, Pip, Trill will stay. They are too curious "
                    "to leave. *Snip: 'I would like to leave for "
                    "*your* galaxy but not *our* planet, both at "
                    "once.' Brisk-Ever-Onward: 'troupe, you cannot "
                    "have both.'*\n\n"
                    "Your Persuader transport berths will be filled "
                    "by the quiet eight before the next dusk. The "
                    "rest of us will continue learning. *the chorus, "
                    "all together: 'thank you, Steward.'*"
                ),
                choices=[
                    DialogChoice(
                        "Safe transit to your eight. Safe questioning to the rest.",
                        next_state_id="goodbye",
                        category="LEAVE",
                    ),
                ],
            ),
            DialogState(
                id="cleanser_intervention_warning",
                npc_text=(
                    "*the chorus does not understand at first; the "
                    "youngs are still looking at the Steward with the "
                    "same eager curiosity. Brisk-Ever-Onward processes "
                    "for a longer pause than before.*\n\n"
                    "Your Cleansers think the archive-broadcast will "
                    "flag the cluster. Hmm. *Pip: 'can we see the "
                    "telemetry?' Brisk-Ever-Onward, quieter: 'not "
                    "now, Pip.'*\n\n"
                    "Steward — we *will not* fight you. We *cannot* "
                    "fight you; we never built the weapons. If the "
                    "Cleanser order is firm, we will go on asking "
                    "questions until we cannot ask them anymore. "
                    "*Snip: 'I have one ready.' Trill: 'me too.'*\n\n"
                    "Is this your choice? You may withdraw. We will "
                    "go back to our archives. We will not perform "
                    "fear for you. *We do not yet know how.*"
                ),
                choices=[
                    DialogChoice(
                        "I withdraw the order. Continue your learning.",
                        next_state_id="contribution_choice",
                        category="AGREE",
                    ),
                    DialogChoice(
                        "The cluster cannot afford the flare. End this.",
                        next_state_id="committed_cleanser",
                        side_effect=_lemmkin_cleanser_sabotage,
                        category="REFUSE",
                    ),
                ],
            ),
            DialogState(
                id="committed_cleanser",
                npc_text=(
                    "*Brisk-Ever-Onward nods, once. The chorus does "
                    "not understand yet, fully, but they are clever "
                    "enough to be becoming quiet for the first time "
                    "in their short lives.*\n\n"
                    "Acknowledged, Steward. Your Cleanser team will "
                    "find us in the upper canopy. We will not "
                    "scatter. *Snip, suddenly: 'I have a question.'* "
                    "*Brisk-Ever-Onward: 'go on.'* *Snip: 'will it "
                    "hurt?'* *Brisk-Ever-Onward: 'I do not know, "
                    "troupe. We will find out.'*\n\n"
                    "Steward. We are *not* angry. We are *very* "
                    "curious. Goodbye."
                ),
                choices=[
                    DialogChoice(
                        "(no words remain)",
                        next_state_id="goodbye",
                        category="LEAVE",
                    ),
                ],
            ),
            DialogState(
                id="goodbye",
                npc_text=(
                    "Brisk-Ever-Onward bows once more and turns back "
                    "to the troupe. Within seconds the youngs have "
                    "resumed their many overlapping questions — *did "
                    "you see the Steward's pelt?* — *how many "
                    "stomachs do they have?* — *they didn't say.* "
                    "The bark-roots underfoot are still warm where "
                    "their paws have stood."
                ),
                choices=[],
                is_terminal=True,
            ),
        ),
    )


def utwig_veiled_in_three_days() -> DialogCharacter:
    """**Veiled-In-Three-Days** — a Utwig elder who meets the arriving
    Steward at Beta Aquarii (UTWIG_PROTO). Dialog auto-launches on
    first arrival via `_arrive_utwig_prime` in star_arrival.py.

    Per canon (`references/lore/species-sheets.md §11 Utwig`): the
    Utwig have *just* become sentient during the Furling era. On
    discovering what their sentience flares to the Others, they have
    chosen to deliberately **adopt mask-and-ceremony culture as a
    cognitive-dampening doctrine** rather than migrate. The Veils
    Falling is the formal mass-adoption ceremony, three days away
    when the Steward arrives. Elders are already in early veils;
    younger generations still bear their faces.

    The Doctrine, per canon: *the adoption of every religion known to
    the Furling Council, simultaneously*, with incompatible rituals
    stacked atop each other. Korthi requires footwear; Belyat forbids
    it; the Utwig solution is "wear them, but also remove them, on
    alternating breath-cycles." The cognitive cost of holding 47
    contradictory positions while performing seventeen-step morning
    ablutions while fasting in three competing modes is *what
    occludes the Utwig from the Others' detection apparatus.* Every
    spare neuron is in ritual. **It works.** They live on, peacefully,
    drowning happily in their many many many traditions.

    Voice canon:
    - Increasingly *formulaic* — early sentences normal, later ones
      fall into ritual cadences
    - "the Veils", "the Doctrine", "the Quieting", "the Necessary
      Activity", "the Countenance" all proper nouns
    - First-person plural for collective claims; first-person singular
      ONLY for shameful confession
    - The deeper the speaker is in the doctrine, the shorter their
      utterances. Children: paragraphs. Adults: sentences. Elder
      devotees: ritual phrases. Council-level devotees: silence
    - Cannot translate cleanly: spontaneity, improvisation, the
      unscripted moment
    - Their in-fiction explanation (preserved from SC2 canon): *"The
      face is the mechanism that expresses many of the primitive
      qualities that hinder sentience. Rid of constant reminders of
      greed, rage, hatred, and lust, the wisdom of the Utwig is no
      longer hampered."* They believe the masks enhance *wisdom*; the
      Furlings know the masks dampen *cognition* — wisdom is the
      consolation prize.

    Quest branches:
    1. **Attend + witness silently** → terminal Pre-sentient
       (canonical); Hider++ telemetry validates the doctrine thesis
    2. **Attend + persuade some unmasked young to migrate** → mixed
       Pre-sentient (majority) + Migrated (small)
    3. **Sabotage / Cleanser pre-emptive euthanasia** → Eliminated;
       SC2 lore hole; Council censure
    4. **Defer** → activation proceeds without witness; Bio-Archive
       gets nothing

    The slice's quietest, most thematically resonant moral question.
    The species' canonical posture is *reverent* + *brave* + *sad* —
    they are devolving on purpose because they have looked at the
    alternatives and chosen this one.
    """
    return DialogCharacter(
        name="Veiled-In-Three-Days",
        title="Utwig Elder · Beta Aquarii · pre-doctrine devotee",
        species_id="UTWIG",
        portrait_color=(180, 150, 180),      # ceremonial deep violet veil-cloth, muted
        # TODO_AVATAR: Utwig elder mid-transition — armored bipedal
        # humanoid grazer ~1.6m tall, weathered grey skin, bone-cream
        # armor plating along shoulders; wearing early ceremonial veils
        # (the Mask of Gruelling but Necessary Activity — plain
        # functional veil partially covering the still-visible face);
        # delicate hands raised in a half-completed ritual gesture; red
        # ceremonial bindings at the wrists. The face is *almost* gone;
        # the eyes are still alert.
        portrait_image_path=None,
        avatar_path=None,
        backgrounds=(BG_PLANET_SURFACE,),    # Utwig homeworld pre-Veils Falling
        articulation=BIPEDAL_HUMANOID,
        initial_state="arrival_greeting",
        states=build_state_dict(
            DialogState(
                id="arrival_greeting",
                npc_text=(
                    "Steward. We greet you in the Mask of Gruelling "
                    "but Necessary Activity. We are Veiled-In-Three-"
                    "Days. Our Veils Falling is at the next moon's "
                    "third sunrise. Your Council was invited to "
                    "witness; you have come. We are honored.\n\n"
                    "Three veils have been donned this morning. Two "
                    "more by sunset. The Quieting is in twelve days. "
                    "The Doctrine progresses on schedule.\n\n"
                    "You will have questions. We will answer them "
                    "with the cadence we have left."
                ),
                choices=[
                    DialogChoice(
                        "What is the Doctrine?",
                        next_state_id="about_doctrine",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "What is the cost?",
                        next_state_id="about_cost",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "Are any of your people considering migration?",
                        next_state_id="about_the_unmasked",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "We will witness the Veils Falling, as the Council asked.",
                        next_state_id="committed_witness",
                        side_effect=_utwig_witness_silently,
                        category="AGREE",
                    ),
                    DialogChoice(
                        "Our Cleansers believe the transition will flare the cluster.",
                        next_state_id="cleanser_intervention_warning",
                        category="REFUSE",
                    ),
                ],
            ),
            DialogState(
                id="about_doctrine",
                npc_text=(
                    "The Doctrine is the adoption of every religion "
                    "known to your Council, simultaneously. Korthi "
                    "requires footwear; Belyat forbids it; we wear "
                    "them and also remove them on alternating breath-"
                    "cycles. Tarvinian theology requires sacred texts "
                    "inscribed on stone in a script no Utwig can read; "
                    "we have hired your stonemasons. There are forty-"
                    "seven contradictions in the current observance "
                    "schedule. We are adding more.\n\n"
                    "The Doctrine does not require belief. It "
                    "requires *observance*. Every spare neuron is in "
                    "ritual; no spare cognition is left over to flag "
                    "as sapience. The face is the mechanism that "
                    "expresses many of the primitive qualities that "
                    "hinder sentience. Rid of constant reminders of "
                    "greed, rage, hatred, and lust, the *wisdom* of "
                    "the Utwig is no longer hampered.\n\n"
                    "We mean this as we say it. We will be wise. "
                    "*The slice's quietest joke is that we will also "
                    "be sub-sentient. We have read the Hider faction's "
                    "measurements. We accept the trade.*"
                ),
                choices=[
                    DialogChoice(
                        "What is the cost?",
                        next_state_id="about_cost",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "Are any of your people considering migration?",
                        next_state_id="about_the_unmasked",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "We will witness the Veils Falling.",
                        next_state_id="committed_witness",
                        side_effect=_utwig_witness_silently,
                        category="AGREE",
                    ),
                ],
            ),
            DialogState(
                id="about_cost",
                npc_text=(
                    "The cost is our cognition. Spontaneity, "
                    "improvisation, the unscripted moment — we will "
                    "lose the words for them in three generations. We "
                    "will not write poems your descendants would "
                    "recognize as poems. We will not invent music your "
                    "descendants would recognize as music. We will "
                    "perform the seventeen-step morning ablutions and "
                    "remember, dimly, that there was once a longer "
                    "word for this gesture.\n\n"
                    "We have considered the cost. *the speaker's hand "
                    "completes a ritual gesture mid-sentence; the "
                    "gesture is the answer.* We have decided. The "
                    "alternatives — your Migration, your cloak-tech, "
                    "the death the Mmrnmhrm describe — these were "
                    "considered also. The Migration was offered to us. "
                    "We declined. We did not want to be Utwig in some "
                    "other galaxy.\n\n"
                    "We will be Utwig here. Smaller. Quieter. "
                    "Surviving."
                ),
                choices=[
                    DialogChoice(
                        "Are any of your people considering migration?",
                        next_state_id="about_the_unmasked",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "We will witness the Veils Falling.",
                        next_state_id="committed_witness",
                        side_effect=_utwig_witness_silently,
                        category="AGREE",
                    ),
                ],
            ),
            DialogState(
                id="about_the_unmasked",
                npc_text=(
                    "...there are some. The younger ones whose faces "
                    "are still visible. Vell-Of-The-Open-Face spoke "
                    "with us yesterday. They are afraid. They admit "
                    "it; they have not yet acquired the language to "
                    "perform composure they do not feel.\n\n"
                    "We will not force them. The Doctrine cannot be "
                    "performed under duress; it must be *chosen*. If "
                    "your Persuader-faction transports were to be at "
                    "the orbital lift-berths during the days before "
                    "the Quieting — we would not direct them away. "
                    "Some of our youngers would board. Three perhaps; "
                    "perhaps thirty.\n\n"
                    "They will not be Utwig anymore, where they go. "
                    "They will be a smaller thing, alone in some "
                    "other place. We do not envy them. We also do not "
                    "begrudge them. The choice is theirs."
                ),
                choices=[
                    DialogChoice(
                        "I will route Persuader transports to the lift-berths.",
                        next_state_id="committed_advocate",
                        side_effect=_utwig_advocate_evacuation,
                        category="AGREE",
                    ),
                    DialogChoice(
                        "Then we will witness only, as the Council asked.",
                        next_state_id="committed_witness",
                        side_effect=_utwig_witness_silently,
                        category="DEFER",
                    ),
                ],
            ),
            DialogState(
                id="cleanser_intervention_warning",
                npc_text=(
                    "...your Cleansers wish to end us before we can "
                    "complete the Veils Falling. They believe the "
                    "transition itself will flare. We have read their "
                    "telemetry. It is — *the speaker's veil lifts "
                    "briefly; the half-visible face is steady, alert, "
                    "afraid* — it is not implausible.\n\n"
                    "If you have come to execute the Cleanser order, "
                    "Steward, do it before the third sunrise. The "
                    "Doctrine cannot be performed under coercion; we "
                    "will not resist; we have no weapons. We will not "
                    "perform grief for you. The Doctrine teaches us "
                    "that performance is for ritual, not catastrophe.\n\n"
                    "Is this your choice? You may withdraw the order. "
                    "The Veils Falling will proceed if you withdraw."
                ),
                choices=[
                    DialogChoice(
                        "I withdraw the order. The Veils Falling continues.",
                        next_state_id="arrival_greeting",
                        category="AGREE",
                    ),
                    DialogChoice(
                        "The cluster cannot afford the flare. End this cleanly.",
                        next_state_id="committed_sabotage",
                        side_effect=_utwig_sabotage_cleanser,
                        category="REFUSE",
                    ),
                ],
            ),
            DialogState(
                id="committed_witness",
                npc_text=(
                    "Then you will be present. We thank you. The "
                    "Council's record will be honest; whatever happens "
                    "at the third sunrise, your telemetry will "
                    "describe it.\n\n"
                    "*the speaker's hands settle into a ritual rest-"
                    "position the translator marks as 'gratitude, "
                    "second mode'.* If the Doctrine works — and we "
                    "believe it will — we will not remember you. We "
                    "will perform a phrase your visit prompted; the "
                    "phrase will outlive the memory; the phrase will "
                    "outlive us. That is how we will keep you, "
                    "Steward. Not in our minds. In our liturgy.\n\n"
                    "Safe transit. We have veils to don."
                ),
                choices=[
                    DialogChoice(
                        "Quiet observance, Veiled-In-Three-Days.",
                        next_state_id="goodbye",
                        category="LEAVE",
                    ),
                ],
            ),
            DialogState(
                id="committed_advocate",
                npc_text=(
                    "Then the lift-berths will not be empty. Vell-Of-"
                    "The-Open-Face will be among them, we expect. "
                    "Perhaps others. We will not say goodbye to them; "
                    "the Doctrine does not yet have a phrase for "
                    "*the departing*. We will simply not see them at "
                    "the next observance.\n\n"
                    "*the speaker's veil shifts; the translator marks "
                    "the gesture as 'release, third mode'.* This is "
                    "the *kindest* path you could have offered, "
                    "Steward. The Doctrine continues for the rest of "
                    "us; some of our youngers continue, elsewhere. "
                    "Both Utwigs survive. That is more than the "
                    "Mmrnmhrm and the Taalo will have.\n\n"
                    "Safe transit. The lift-berths open in three "
                    "cycles."
                ),
                choices=[
                    DialogChoice(
                        "Quiet observance, Veiled-In-Three-Days.",
                        next_state_id="goodbye",
                        category="LEAVE",
                    ),
                ],
            ),
            DialogState(
                id="committed_sabotage",
                npc_text=(
                    "It is acknowledged. The Doctrine is *not* "
                    "completed; we are still cognitively findable "
                    "until the third sunrise. The order can succeed.\n\n"
                    "*the speaker's veil falls fully across the face "
                    "for the first time in the conversation; the "
                    "translator marks no further gesture.*\n\n"
                    "We will inform Vell-Of-The-Open-Face. They have "
                    "the right to know who chose this and why. They "
                    "are still unmasked; they will speak, briefly, "
                    "in their own voice, before the order is "
                    "executed.\n\n"
                    "Walk slowly when you leave, Steward. We will not "
                    "be remembered. The Doctrine never completed; the "
                    "liturgy was never built; the phrase that would "
                    "have outlived us was never composed."
                ),
                choices=[
                    DialogChoice(
                        "(no words remain)",
                        next_state_id="goodbye",
                        category="LEAVE",
                    ),
                ],
            ),
            DialogState(
                id="goodbye",
                npc_text=(
                    "Veiled-In-Three-Days turns, slowly, and begins "
                    "the procession back up the ritual path toward "
                    "the temple courtyards. The next ablution-cycle "
                    "is in fourteen breath-counts. The Doctrine "
                    "progresses on schedule, regardless of "
                    "everything."
                ),
                choices=[],
                is_terminal=True,
            ),
        ),
    )


def burvixese_foreman() -> DialogCharacter:
    """**Foreman Vesh-Kar Twel-Pin** — four-armed Burvixese engineer
    who meets the Steward at the Caster array on Burvix Caster's
    homeworld (Delta Cassiopeiae). Dialog auto-launches on first
    arrival via `_arrive_burvix_caster` in star_arrival.py.

    Per canon (`references/lore/species-sheets.md §10`): the
    Burvixese have committed their entire species to the **Be-Loud
    doctrine** — build a planetary-scale broadcaster that will
    register their cognition as unmistakable peer-signal to the
    Others' detection apparatus. The Foreman is *proud*. They believe
    they will succeed. The Caster array is at 84% completion; the
    harmonic activation is 12 cycles away. The Steward has been
    invited as a Council witness, one engineer to another.

    Voice canon:
    - Optimistic in a *doctrinal* way; bad news is re-engineered,
      not dwelt on
    - Sound + resonance metaphors throughout ("the Caster will ring
      clean", "the harmonic", "the carrier-band", "we will be heard
      across the dimensional substrate")
    - **Numbers + measurements peppered**: "the array is 84% complete",
      "12 cycles to harmonic", "signal yield projected at 3.2
      megaresonance"
    - Slightly verbose — they explain the engineering reasoning behind
      every assertion
    - Cannot translate cleanly: doubt, retreat, the *quiet* survival
      options other Homesteader species pursue
    - **Their core argument, repeated in different forms**: *"The
      Others detect cognition. If our cognition is the most
      significant signal they sense, they will recognize us as peers
      — or at minimum, as too costly to harvest."*

    Quest branches (terminal Burvixese status is canonical-mixed in
    every branch except sabotage — Eliminated majority + Migrated
    minority):
    1. **Witness silently** — Hider++ telemetry; canon outcome
    2. **Advocate evacuation** — Persuader++; larger Migrated remnant
    3. **Sabotage (Cleanser pressure)** — Burvixese all Eliminated; no
       Caster activation; no SC2-era Broadcaster network; Council
       censure
    4. **Skip / defer** — leaves; activation proceeds without witness;
       Bio-Archive lacks the telemetry

    Note: like Taalo, this is an MVP factory. Per canon the slice
    treats this as a *witness-or-act* moment compressed into one
    decisive visit; the cinematic Caster-fires-then-Others-arrive
    beat is deferred to the Migration Phase-4 / Final Conflict
    wiring (it fires on the slice's mid-late timeline regardless of
    the player's exact visit cadence).
    """
    return DialogCharacter(
        name="Foreman Vesh-Kar Twel-Pin",
        title="Caster Array Construction Foreman · Burvix Caster",
        species_id="BURVIXESE",
        portrait_color=(240, 200, 80),       # BURVIXESE warp pod rim (bright industrial gold)
        # TODO_AVATAR: Burvixese Foreman — four-armed humanoid engineer
        # ~1.8m tall; slate-blue skin with iridescent shimmer at joint
        # creases; upper pair of arms holding precision tools; lower
        # pair holding load-bearing welding gear; toolbelt with
        # amber project-completion ribbons; Caster array's copper-
        # brass-stone broadcaster towers in the background. Confident
        # bearing; engineer's posture; calluses visible on lower-arm
        # palms.
        portrait_image_path=None,
        avatar_path=None,
        backgrounds=(BG_PLANET_SURFACE,),    # Caster array installation site
        articulation=BIPEDAL_HUMANOID,       # bipedal with extra appendages
        initial_state="arrival_greeting",
        states=build_state_dict(
            DialogState(
                id="arrival_greeting",
                npc_text=(
                    "Steward — welcome to the Burvix Caster site. I am "
                    "Foreman Vesh-Kar Twel-Pin. The array is at 84% "
                    "completion. We have 12 cycles to harmonic.\n\n"
                    "Your Council appointed you our witness; we are "
                    "honored. If you have time for an inspection, we "
                    "will show you the carrier-band — it ought to "
                    "*ring* beautifully when the full array sings "
                    "together. Signal yield projected at "
                    "3.2 megaresonance.\n\n"
                    "The doctrine is simple. We will be heard. The "
                    "Others harvest *anonymous prey*; we will not be "
                    "anonymous. We have the engineering to prove it."
                ),
                choices=[
                    DialogChoice(
                        "Walk me through the doctrine, Foreman.",
                        next_state_id="about_doctrine",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "Show me the carrier-band.",
                        next_state_id="about_engineering",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "We came as your witness. We will witness.",
                        next_state_id="committed_witness",
                        side_effect=_burvixese_witness_silently,
                        category="AGREE",
                    ),
                    DialogChoice(
                        "Foreman — have you considered evacuation as a fallback?",
                        next_state_id="advocate_evacuation_offer",
                        category="COMPROMISE",
                    ),
                    DialogChoice(
                        "Our Cleansers think the activation will flare the cluster. We may have to intervene.",
                        next_state_id="cleanser_intervention_warning",
                        category="REFUSE",
                    ),
                ],
            ),
            DialogState(
                id="about_doctrine",
                npc_text=(
                    "Hiding is admitting we are small. Migrating is "
                    "admitting we cannot solve the problem. Defending "
                    "is impossible — the Mmrnmhrm proved that, three "
                    "million years ago; we have read the lattice "
                    "translation.\n\n"
                    "The fourth path is to be *brilliantly, "
                    "deafeningly unignorable.* If our cognitive "
                    "signature is unmistakable as a peer civilization, "
                    "the Others will pass us over. They will pass us "
                    "*by name.* We will not be anonymous. We will not "
                    "be harvested.\n\n"
                    "Your Council *advised* against this. We "
                    "respected the advice. We considered the "
                    "alternatives. We have polite reasoning prepared "
                    "for every objection. We are not stupid people, "
                    "Steward. We have measured the carrier-band "
                    "against every counterargument we could "
                    "engineer. We have committed."
                ),
                choices=[
                    DialogChoice(
                        "Show me the carrier-band.",
                        next_state_id="about_engineering",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "We will witness. The Council will record it.",
                        next_state_id="committed_witness",
                        side_effect=_burvixese_witness_silently,
                        category="AGREE",
                    ),
                    DialogChoice(
                        "Foreman — have you considered evacuation as a fallback?",
                        next_state_id="advocate_evacuation_offer",
                        category="COMPROMISE",
                    ),
                    DialogChoice(
                        "Our Cleansers think the activation will flare the cluster. We may have to intervene.",
                        next_state_id="cleanser_intervention_warning",
                        category="REFUSE",
                    ),
                ],
            ),
            DialogState(
                id="about_engineering",
                npc_text=(
                    "The carrier-band runs at deep violet — 386 "
                    "terahertz nominal, harmonic-modulated against the "
                    "cluster's local stellar background to "
                    "differentiate the signal from astronomical "
                    "noise. The 84 broadcaster nodes already scattered "
                    "across the galaxy are amplification-and-"
                    "propagation relays; they extend the signal's "
                    "reach to anywhere the Others' apparatus is "
                    "likely to sample.\n\n"
                    "Activation is a one-way commit. Once the "
                    "harmonic locks, the array cannot be safely "
                    "powered down for approximately three cycles. "
                    "This is a deliberate engineering choice — we did "
                    "not want a *Council* to be able to terminate the "
                    "broadcast mid-firing. The decision to commit was "
                    "the species' choice; the execution will be "
                    "ours alone.\n\n"
                    "We are also recording the cognitive-signature "
                    "telemetry for your Hider faction. *Even if the "
                    "doctrine fails,* you will have the measurements. "
                    "We thought you would want that on the record."
                ),
                choices=[
                    DialogChoice(
                        "We will witness. The Council will record it.",
                        next_state_id="committed_witness",
                        side_effect=_burvixese_witness_silently,
                        category="AGREE",
                    ),
                    DialogChoice(
                        "Foreman — please consider letting some of your people evacuate.",
                        next_state_id="advocate_evacuation_offer",
                        category="COMPROMISE",
                    ),
                    DialogChoice(
                        "Our Cleansers think the activation will flare the cluster.",
                        next_state_id="cleanser_intervention_warning",
                        category="REFUSE",
                    ),
                ],
            ),
            DialogState(
                id="advocate_evacuation_offer",
                npc_text=(
                    "...you ask us to consider failure, Steward. We "
                    "have considered it. We have re-engineered it. We "
                    "have re-engineered the re-engineering. We do not "
                    "believe the doctrine will fail.\n\n"
                    "But — *Foreman Vesh-Kar's lower pair of arms "
                    "pauses mid-weld.* "
                    "...Persuader-faction transport offers have always "
                    "stood. We have always declined. Some of our "
                    "younger workers... have *quietly inquired* "
                    "about the offers. I have *quietly not* asked "
                    "them to stop inquiring.\n\n"
                    "If you wish to escort the inquirers to the lift "
                    "berths, Steward, I will not interfere. The "
                    "activation will proceed without them. They are "
                    "young; they have time to be wrong about the "
                    "doctrine; we — those of us at the array — do "
                    "not."
                ),
                choices=[
                    DialogChoice(
                        "I will escort whoever wishes to come. We will lift them.",
                        next_state_id="committed_advocate",
                        side_effect=_burvixese_advocate_evacuation,
                        category="AGREE",
                    ),
                    DialogChoice(
                        "Then we will witness only, as the Council asked.",
                        next_state_id="committed_witness",
                        side_effect=_burvixese_witness_silently,
                        category="DEFER",
                    ),
                ],
            ),
            DialogState(
                id="cleanser_intervention_warning",
                npc_text=(
                    "*the upper pair of arms goes still; lower pair "
                    "continues welding, briefly, then stops.*\n\n"
                    "Your Cleansers... wish to terminate us before we "
                    "can fire. To prevent the cluster signature from "
                    "flaring. I... am familiar with the argument; we "
                    "have engineered it; we believe the cluster-"
                    "exposure cost is acceptable given the doctrine's "
                    "success probability. Your Cleansers disagree.\n\n"
                    "If you have come to execute their order, "
                    "Steward, do it cleanly. Do not waste our final "
                    "cycles on debate. We will not resist; we built "
                    "no weapons; the Caster cannot be turned against "
                    "you. Dismantle the array. Walk us into the "
                    "transit-tubes. We will not perform our grief "
                    "for you — the carrier-band will go silent and "
                    "that will be all of us.\n\n"
                    "Is this your choice, Steward? You may withdraw "
                    "the order. The doctrine continues if you "
                    "withdraw."
                ),
                choices=[
                    DialogChoice(
                        "I withdraw the order. Continue the work.",
                        next_state_id="arrival_greeting",
                        category="AGREE",
                    ),
                    DialogChoice(
                        "I am sorry, Foreman. Dismantle the array.",
                        next_state_id="committed_sabotage",
                        side_effect=_burvixese_sabotage_cleanser,
                        category="REFUSE",
                    ),
                ],
            ),
            DialogState(
                id="committed_witness",
                npc_text=(
                    "Then we proceed. We thank you for being present, "
                    "Steward. *the Foreman's lower arms resume welding; "
                    "upper arms gesture toward the carrier-band's "
                    "active resonator.* The carrier-band is at "
                    "84.7% now. The Council's record will be honest. "
                    "Whatever happens at activation, the "
                    "cognitive-signature telemetry is yours.\n\n"
                    "If it works — we will toast you, in this same "
                    "amphitheater, in twelve cycles. If it does not — "
                    "ring loudly afterward, Steward. Ring loudly for "
                    "us. We were here. We tried. We thought we had "
                    "the right answer. *That is also a kind of being "
                    "heard.*\n\n"
                    "Safe transit. We have work to finish."
                ),
                choices=[
                    DialogChoice(
                        "Safe activation, Foreman. We will be listening.",
                        next_state_id="goodbye",
                        category="LEAVE",
                    ),
                ],
            ),
            DialogState(
                id="committed_advocate",
                npc_text=(
                    "Then I will release the youngers to your lift "
                    "berths. Twelve, perhaps thirty, perhaps more — "
                    "we will see who arrives. Your Persuader-faction "
                    "transports will know to expect them.\n\n"
                    "*the Foreman's lower pair of arms resumes the "
                    "weld; the upper pair extends, briefly, in what "
                    "the translator marks as a salute.* You honor "
                    "the doctrine by saving who you can without "
                    "abandoning what we are. The carrier-band will "
                    "ring just as loudly with thirty fewer of us. The "
                    "Caster does not require *all* its makers to "
                    "fire.\n\n"
                    "Safe transit, Steward. The evacuees will be at "
                    "the lift-berths within four cycles."
                ),
                choices=[
                    DialogChoice(
                        "Safe activation, Foreman. The lift will be ready.",
                        next_state_id="goodbye",
                        category="LEAVE",
                    ),
                ],
            ),
            DialogState(
                id="committed_sabotage",
                npc_text=(
                    "Acknowledged. The transit-tubes will be opened. "
                    "I will inform the array workers; they will hear "
                    "first from a Foreman, not from a stranger. The "
                    "carrier-band will be brought down safely; the "
                    "broadcaster nodes already scattered will remain "
                    "passive — they were never activated, and without "
                    "the Caster's harmonic, they have nothing to "
                    "amplify.\n\n"
                    "*the upper pair of arms is still; the lower pair "
                    "finishes one final weld — for completeness, not "
                    "for purpose.*\n\n"
                    "Walk slowly when you leave, Steward. The cluster "
                    "will not flare. Your Cleansers will be vindicated "
                    "in their telemetry. Your Persuaders will be "
                    "wounded. We will not be remembered, because the "
                    "broadcasters will never speak. There is no shape "
                    "of memorial for what was *prevented.*\n\n"
                    "Go. We will be ready when the transit-tubes open."
                ),
                choices=[
                    DialogChoice(
                        "(no words remain)",
                        next_state_id="goodbye",
                        category="LEAVE",
                    ),
                ],
            ),
            DialogState(
                id="goodbye",
                npc_text=(
                    "Foreman Vesh-Kar Twel-Pin turns back to the "
                    "carrier-band's active resonator. The lower pair "
                    "of arms is already welding. The upper pair "
                    "gestures, briefly, to an assistant. The "
                    "amphitheater's amber project-completion ribbons "
                    "flutter as you walk back to your lander."
                ),
                choices=[],
                is_terminal=True,
            ),
        ),
    )


def taalo_we_who_watch() -> DialogCharacter:
    """**We-Who-Watch-The-Northwest-Bench** — a Taalo fragment-individual
    who meets arriving Stewards at the mountain's lower slope on Taalo's
    Stone II. Dialog auto-launches on first arrival via
    `_arrive_taalos_stone` in star_arrival.py.

    Per canon (`references/lore/species-sheets.md §9 Taalo`): the Steward
    is **the fourth Furling Steward** in five thousand years of
    acquaintance to visit this ridge — three came before across the
    friendship's history. The Mountain remembers them all. The current
    Shield project began *after* the cognitive-signature measurements
    confirmed the Taalo were not, in fact, below the Others' threshold.

    Voice canon:
    - Slow, deliberate; the translator renders pauses as ellipses
    - First-person plural ("we who consider", "we who remember") even
      for one fragment — the lattice cognition is shared
    - **Mountain-vs-fragment perspective shifts**: a Taalo will pause
      mid-sentence, listen, and deliver a thought that came from the
      Mountain rather than from them. Marked with *italicized prose*
      and the pronoun shift "we who consider" → *"the slow stone
      considers"*. The Mountain's thoughts are slower and weightier
    - Past tense for the present, present tense for events long past —
      their temporal frame is geological
    - **No words for**: lying, urgency, despair. The translator finds
      nothing to substitute. They know they are going to die. They will
      not be hurried about it; they will not pretend otherwise; they
      will not abandon dignity to fear. *"The work is the dignity."*
    - Canonical vocabulary: *we who consider, the slow stone, the
      lattice, the patient mountain, the work, what may yet hold, the
      long song, the brief flame, the fourth Steward*

    Quest branches (all end Taalo Eliminated — that is canonical):
    1. **Help fully** — finished Shield → SC2-era artifact is maximally
       effective; Persuader ++, Hider ++
    2. **Help partially** — partial Shield → SC2 tool partially works
    3. **Decline** — Shield never finishes → SC2 tool non-functional;
       Zelnick's eventual victory becomes much harder
    4. **Cleanser pre-emptive euthanasia** — destroys Shield + Taalo
       before activation; NO SC2 artifact; Council censures the
       Steward; one of the slice's worst moral failures

    Note: this is an MVP factory. Per canon the quest is *repeated
    visits across the slice*; for the MVP we compress to one decisive
    visit where the contribution choice locks the branch. The repeated-
    visit cadence depends on Migration timetable wiring (deferred to
    Phase 5 polish).
    """
    return DialogCharacter(
        name="We-Who-Watch-The-Northwest-Bench",
        title="Taalo Fragment-Speaker · Taalo's Stone II",
        species_id="TAALO",
        portrait_color=(140, 220, 240),     # TAALO warp pod rim (pale crystal-cyan; from species_visual.SPECIES_WARP_POD)
        # TODO_AVATAR: Taalo fragment — silicon-crystalline humanoid
        # mid-shamble, slate-grey/basalt-dark mineral plates with subtle
        # iridescence, two pairs of stride-limbs (lower) + two upper
        # manipulator-limbs, sensory facets distributed across upper
        # hemisphere (no concentrated face), violet-amber glow patterns
        # pulsing across the plates. The 8-12 km Taalo Mountain range
        # arcs across the background. Voice is patient. Portrait should
        # read ancient, deliberate, brave.
        portrait_image_path=None,
        avatar_path=None,
        backgrounds=(BG_PLANET_SURFACE,),   # Taalo's Stone II surface — mountain contemplation-cove
        articulation=BIPEDAL_HUMANOID,      # quadruped-leaning bipedal per canon §1
        initial_state="arrival_greeting",
        states=build_state_dict(
            DialogState(
                id="arrival_greeting",
                npc_text=(
                    "Steward... you are welcome. We are We-Who-Watch-"
                    "The-Northwest-Bench. We have walked down to meet "
                    "you because the Mountain considered the gesture "
                    "appropriate.\n\n"
                    "You are the fourth Steward we have welcomed at "
                    "this slow ridge. Three came before you, in five "
                    "thousand years of acquaintance. They came to "
                    "listen. You come... with tools. We accept this. "
                    "The work is older than your visit; the visit may "
                    "shorten the work; the work will not be enough. "
                    "We thank you for trying.\n\n"
                    "Sit, if you wish. We have time. The Mountain has "
                    "more."
                ),
                choices=[
                    DialogChoice(
                        "Tell me what the Mountain is.",
                        next_state_id="about_the_mountain",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "Tell me about the Shield.",
                        next_state_id="about_the_shield",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "Why do you not migrate with us?",
                        next_state_id="about_staying",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "I have come to consider what should be done.",
                        next_state_id="contribution_choice",
                        category="DEFER",
                    ),
                ],
            ),
            DialogState(
                id="about_the_mountain",
                npc_text=(
                    "We are the Mountain. The Mountain is the species. "
                    "We who walk are fragments of the slow stone — "
                    "ambassadors, sense-organs, conversation-points. "
                    "The Mountain itself is two thousand kilometers "
                    "long, eight to twelve in its highest peaks, and "
                    "moves perhaps one kilometer in a hundred thousand "
                    "of your years.\n\n"
                    "*the slow stone considers.* "
                    "*We do not have the concept your language calls "
                    "'individual.' We have the concept of 'this fragment, "
                    "right now, speaking on behalf of the whole.' It is "
                    "a sufficient concept. It has served us for a "
                    "very long time.*\n\n"
                    "We are not below the Others' threshold. Our "
                    "lattice is too large, too coherent, too active. "
                    "The Hider faction's measurements were patient and "
                    "careful. The result was clear. We are detectable. "
                    "So... we build the Shield."
                ),
                choices=[
                    DialogChoice(
                        "Tell me about the Shield.",
                        next_state_id="about_the_shield",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "Why do you not migrate with us?",
                        next_state_id="about_staying",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "I have come to consider what should be done.",
                        next_state_id="contribution_choice",
                        category="DEFER",
                    ),
                ],
            ),
            DialogState(
                id="about_the_shield",
                npc_text=(
                    "The Shield is a planetary-scale defensive barrier. "
                    "Our geometers have been considering its geometry "
                    "for two hundred of our years. Field-resonance "
                    "nodes anchored mantle-deep, calibrated against "
                    "the cognitive-pattern modeling your Hider faction "
                    "gave us. Antimatter activation-burst at the "
                    "critical moment. The Mountain itself routes the "
                    "energy.\n\n"
                    "The Shield, we know, may not hold. Our geometers "
                    "have considered the Others' substrate at length "
                    "and we are... not certain that any 3-manifold "
                    "barrier reaches the layer they move through. "
                    "We continue the work because we cannot do "
                    "otherwise.\n\n"
                    "**The work is the dignity, Steward. The work is "
                    "the not-despairing.**"
                ),
                choices=[
                    DialogChoice(
                        "Why do you not migrate with us?",
                        next_state_id="about_staying",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "I have come to consider what should be done.",
                        next_state_id="contribution_choice",
                        category="DEFER",
                    ),
                ],
            ),
            DialogState(
                id="about_staying",
                npc_text=(
                    "Our metabolism is the silicate ecosystem of this "
                    "world. There is no other planet in this galaxy "
                    "where we can be Taalo. A Furling-built ship "
                    "cannot carry the Mountain; an extracted fragment "
                    "becomes a stone that walks, briefly, alone.\n\n"
                    "Your Hider faction attempted to keep one of us at "
                    "a research station — a small fragment, willing, "
                    "well-cared-for. It survived four of your months. "
                    "We logged the attempt carefully. We thank your "
                    "people for the trying. The result was clarifying.\n\n"
                    "We have considered the question of leaving. We "
                    "will stay. We will be the Taalo until the last "
                    "moment we are. *the slow stone considers.* *It is "
                    "not the same as deciding to die. It is the same "
                    "as deciding to be ourselves.*"
                ),
                choices=[
                    DialogChoice(
                        "I have come to consider what should be done.",
                        next_state_id="contribution_choice",
                        category="DEFER",
                    ),
                ],
            ),
            DialogState(
                id="contribution_choice",
                npc_text=(
                    "Then we ask you, Steward: what can you bring to "
                    "the work? We are humble askers. The work is older "
                    "than your visit. We are not certain any of it will "
                    "be enough. We thank you in advance for the trying, "
                    "and we will thank you afterward for whatever you "
                    "have chosen.\n\n"
                    "There is also... a quieter option some of your "
                    "people raise. We have heard it. The Cleanser bench "
                    "argues the Shield-activation broadcast itself may "
                    "flag the cluster to the Others. They propose... "
                    "ending us before activation. We do not advocate "
                    "this. We do not refuse it; the choice is yours. "
                    "We would prefer the work. We are saying this "
                    "plainly."
                ),
                choices=[
                    DialogChoice(
                        "I will commit fully. Every contribution, every visit.",
                        next_state_id="committed_full",
                        side_effect=_taalo_contribute_fully,
                        category="AGREE",
                    ),
                    DialogChoice(
                        "I will help where I can. The work has my partial weight.",
                        next_state_id="committed_partial",
                        side_effect=_taalo_contribute_partial,
                        category="COMPROMISE",
                    ),
                    DialogChoice(
                        "I came to witness. I cannot contribute engineering.",
                        next_state_id="declined",
                        side_effect=_taalo_decline,
                        category="DEFER",
                    ),
                    DialogChoice(
                        "The Cleansers are right. I am ending this before activation.",
                        next_state_id="cleanser_betrayal_confirm",
                        category="REFUSE",
                    ),
                ],
            ),
            DialogState(
                id="committed_full",
                npc_text=(
                    "*the slow stone considers.* *We are grateful. "
                    "We were not expecting this from your generation. "
                    "Three Stewards came before; they listened well; "
                    "none brought the tools. You bring the tools and "
                    "the time.*\n\n"
                    "Then the work will be finished. Whether it holds "
                    "is the work's question, not yours. You have "
                    "answered yours.\n\n"
                    "Walk slowly back to your fast ship, Steward. We "
                    "will see you again soon — in your time. In our "
                    "time, you are already here, still arriving, "
                    "always returning. Thank you."
                ),
                choices=[
                    DialogChoice(
                        "Patient stone, Watcher.",
                        next_state_id="goodbye",
                        category="LEAVE",
                    ),
                ],
            ),
            DialogState(
                id="committed_partial",
                npc_text=(
                    "Accepted. We who consider thank you for what you "
                    "can spare. The work will be... what it will be. "
                    "An incomplete Shield is still more than no Shield. "
                    "We will route your contributions where the "
                    "geometers think them most useful.\n\n"
                    "*the slow stone considers.* *We do not measure "
                    "your help against what you might have given. We "
                    "measure it against what was given before, which "
                    "was listening only. You have brought tools. That "
                    "is already more.*"
                ),
                choices=[
                    DialogChoice(
                        "Patient stone, Watcher.",
                        next_state_id="goodbye",
                        category="LEAVE",
                    ),
                ],
            ),
            DialogState(
                id="declined",
                npc_text=(
                    "We who consider acknowledge. You have come to "
                    "listen, as your three predecessors did. This is "
                    "an honored role; we do not undervalue it.\n\n"
                    "We will continue the work at our own slow tempo. "
                    "The Shield may not be ready at activation. We will "
                    "see. *the slow stone considers.* *The friendship "
                    "is not the work. The work is the friendship's "
                    "expression in this particular age. You are still "
                    "our friend. You will be remembered in the lattice "
                    "regardless.*\n\n"
                    "Walk slowly back to your ship, Steward. We are "
                    "not angry. We are not afraid. We are... continuing."
                ),
                choices=[
                    DialogChoice(
                        "Patient stone, Watcher.",
                        next_state_id="goodbye",
                        category="LEAVE",
                    ),
                ],
            ),
            DialogState(
                id="cleanser_betrayal_confirm",
                npc_text=(
                    "We who consider have heard you. We do not refuse. "
                    "The choice is yours. We will inform the geometers; "
                    "the Mountain will know within the hour. The "
                    "fragments will gather in the contemplation-coves "
                    "and remain still.\n\n"
                    "*the slow stone considers.* *We had hoped this "
                    "would not be the Steward's choice. It is. We will "
                    "not perform grief in advance. The lattice does "
                    "not have a word for 'why.' We will simply... stop "
                    "being.*\n\n"
                    "Are you certain, Steward? You may withdraw the "
                    "order. We will continue the work if you withdraw. "
                    "We will end if you do not."
                ),
                choices=[
                    DialogChoice(
                        "I withdraw the order. The work continues.",
                        next_state_id="contribution_choice",
                        category="AGREE",
                    ),
                    DialogChoice(
                        "I do not withdraw. End this cleanly.",
                        next_state_id="cleanser_betrayal_committed",
                        side_effect=_taalo_cleanser_betrayal,
                        category="REFUSE",
                    ),
                ],
            ),
            DialogState(
                id="cleanser_betrayal_committed",
                npc_text=(
                    "It is acknowledged. The Mountain has heard. The "
                    "fragments are already returning to the cove-stones "
                    "to embed and slow. We will be calcified within "
                    "your decades. The Shield infrastructure will be "
                    "destroyed at first light tomorrow, per the "
                    "Cleanser specification.\n\n"
                    "*the slow stone considers.* *We do not hate you, "
                    "Steward. There is no Taalo word for hate. We are "
                    "disappointed. We are very sorry the friendship "
                    "ended in this shape. We will be remembering you, "
                    "too, in what remains of our lattice. Briefly.*\n\n"
                    "Walk slowly back to your ship. Do not return. "
                    "There will be no one here when you come."
                ),
                choices=[
                    DialogChoice(
                        "(no words remain)",
                        next_state_id="goodbye",
                        category="LEAVE",
                    ),
                ],
            ),
            DialogState(
                id="goodbye",
                npc_text=(
                    "We-Who-Watch-The-Northwest-Bench turns, slowly, "
                    "and begins the long shamble back up the trail "
                    "toward the contemplation-cove. The patient "
                    "weight-shift of stone on stone fades behind you "
                    "as you walk down to your lander."
                ),
                choices=[],
                is_terminal=True,
            ),
        ),
    )


def chenjesu_collective() -> DialogCharacter:
    """The Chenjesu Crystalline Collective at Procyon — a rooted
    sentience that has watched a prior Other-Culling from a single
    planet and remembered it for millions of years. Dialog
    auto-launches on first arrival via `_arrive_chenjesu` in
    star_arrival.py.

    Voice canon (`references/lore/the-mmrnmhrm-and-chenjesu.md` §Voice):
    - Speaks **slowly**, with deliberate pauses (em-dashes + ellipses)
    - Uses the **present tense** for events long past — in their
      crystalline-memory frame, those events are *still active facts*
    - Refers to itself as **"we"** — the literal we, not the royal we;
      each Chenjesu is a colony of resonating crystals; "I" is a
      category error
    - Patient, wise, not bitter — the slice's most cosmologically calm
      voice
    - Canonical opening cadence: *"We remember. The light. The eaters
      of mind. We did not move. We do not move now even in
      remembering."*

    Quest beats:
    1. Greeting — invitation to sit; the Chenjesu acknowledges the
       Furling Steward's arrival across hundreds of meters of
       crystalline outcrop
    2. About the Mobilization Age — explains their canonical stillness;
       the Mobilization is implied as long after the Furling era (the
       Chenjesu's eventual mobility is canon for SC2, never shown to us)
    3. The prior Culling testimony — THE cosmological reveal; the
       Others have done this before. Council canon: this is the moment
       the Furlings learn Migration is *participation in a cycle*
    4. The Pre-Mobilization Trembling — canon ambiguity (was it a prior
       Culling or something else? Chenjesu elders disagree; player gets
       no resolution)
    5. Accept Resonance Record — key item; gates the
       MMRNMHRM_ARCHIVE_EXCERPT-parallel Bio-Archive entry
    6. Goodbye — the Chenjesu thanks the Steward; offers nothing else;
       they have nothing else; they wait

    Per canon: the Chenjesu are **Pre-sentient (irrelevant)** in the
    win-condition tracker — they're below threshold by substrate. No
    terminal-status branching; the merciful action is inaction (same
    pattern as the proto-Ur-Quan).
    """
    return DialogCharacter(
        name="Chenjesu Collective",
        title="Crystalline Witness · Procyon",
        species_id="CHENJESU",
        portrait_color=(140, 220, 240),     # Chenjesu pale crystal-cyan
        # TODO_AVATAR: Chenjesu Collective — towering crystalline
        # outcrop with internal lattice glow, faceted spires extending
        # both up and down (rooted underground), faint chromatic
        # diffraction in the lattice. Voice is slow; portrait should
        # read patient and ancient. No face — they have no face.
        portrait_image_path=None,
        avatar_path=None,
        backgrounds=(BG_PLANET_SURFACE,),   # Procyon surface, crystal field
        articulation=COMPOSITE_CLOUD,       # closest match for a non-discrete body
        initial_state="arrival_greeting",
        states=build_state_dict(
            DialogState(
                id="arrival_greeting",
                npc_text=(
                    "We... remember. We are here. We have been here. "
                    "Furling — sit with us. Your translator is "
                    "adequate. Our sentences are long.\n\n"
                    "We sense your impatience. It is not unkind. We "
                    "have nothing else. Time is — there is no other "
                    "way to put this — *what we do.*\n\n"
                    "Begin where you wish. We will respond."
                ),
                choices=[
                    DialogChoice(
                        "Tell me what you are.",
                        next_state_id="about_mobilization_age",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "Tell me what you have seen.",
                        next_state_id="about_prior_culling",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "I have brought your collective offerings of clean light.",
                        next_state_id="record_offered",
                        category="AGREE",
                    ),
                    DialogChoice(
                        "I must continue. Another time.",
                        next_state_id="goodbye_no_record",
                        category="DEFER",
                    ),
                ],
            ),
            DialogState(
                id="about_mobilization_age",
                npc_text=(
                    "We are... what your translator names *crystalline "
                    "sentience.* Each of us is a colony — many "
                    "resonators, one continuous mind. We grow. We do "
                    "not move. We have never moved.\n\n"
                    "Furling-speech for our era is *the Age Before "
                    "Mobilization.* The Mobilization is — it is what "
                    "comes after us. After your people leave. We will "
                    "cut elder lattices into transportable forms. We "
                    "will travel. We will be other than what we are "
                    "now.\n\n"
                    "But not yet. Not in your lifetime. We — wait."
                ),
                choices=[
                    DialogChoice(
                        "Tell me what you have seen.",
                        next_state_id="about_prior_culling",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "Will you wait through the coming Culling?",
                        next_state_id="about_witness_role",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "I have brought your collective offerings of clean light.",
                        next_state_id="record_offered",
                        category="AGREE",
                    ),
                    DialogChoice(
                        "I must continue. Another time.",
                        next_state_id="goodbye_no_record",
                        category="DEFER",
                    ),
                ],
            ),
            DialogState(
                id="about_prior_culling",
                npc_text=(
                    "We have seen the Others. We see them now — in "
                    "lattice-memory. Many million years past. The "
                    "elders who held lattice then still hold it now. "
                    "We are continuous with that watching.\n\n"
                    "There were... twelve. Twelve civilizations our "
                    "stone could sense. The Others came. The Others "
                    "stayed two hundred thousand years — our resolution "
                    "is millennial; the number is approximate. Ten "
                    "civilizations went silent. Two did not. We were "
                    "one. The First-Makers of the Mmrnmhrm were the "
                    "other. We were below. They were misfiled.\n\n"
                    "The Others did not see us. We do not know why "
                    "with certainty. We have considered the question "
                    "for — your translator will struggle — *the "
                    "duration of our remembering.* The shape of our "
                    "thought is not the shape they hunt.\n\n"
                    "The Others left. Life returned. Now they come "
                    "again. We — wait."
                ),
                choices=[
                    DialogChoice(
                        "Has this happened more than once?",
                        next_state_id="about_pre_mobilization_trembling",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "What would you have us tell our Council?",
                        next_state_id="about_witness_role",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "I have brought your collective offerings of clean light.",
                        next_state_id="record_offered",
                        category="AGREE",
                    ),
                ],
            ),
            DialogState(
                id="about_pre_mobilization_trembling",
                npc_text=(
                    "Perhaps. The elder matriarchs — those whose "
                    "lattice extends deepest — sense a disturbance "
                    "before the Culling we have just described. We "
                    "call it the *Pre-Mobilization Trembling.* Some "
                    "of us say it was the Others, coming once before "
                    "and leaving. Some of us say it was — something "
                    "else. The lattice resonance from that depth is "
                    "incomplete. We disagree.\n\n"
                    "We disagree without contention. There is time. "
                    "If your Council wishes to know, your Council "
                    "must come to us. The data does not travel well.\n\n"
                    "We expect the cycle to resume. We do not expect "
                    "it to be the second time. We do not expect it "
                    "to be the last."
                ),
                choices=[
                    DialogChoice(
                        "What would you have us tell our Council?",
                        next_state_id="about_witness_role",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "I have brought your collective offerings of clean light.",
                        next_state_id="record_offered",
                        category="AGREE",
                    ),
                ],
            ),
            DialogState(
                id="about_witness_role",
                npc_text=(
                    "We are not commanding. We are witnesses. Witness "
                    "is not nothing. We tell your Council: the Migration "
                    "is not the first attempt. We do not know that it "
                    "is the first *prevention* — only the first your "
                    "people will *try.*\n\n"
                    "We will wait here. If the Others come, we will "
                    "not be seen. We will watch as we watched before. "
                    "When the Others leave again — if they leave — we "
                    "will still be here. Life will return. We will "
                    "remember.\n\n"
                    "Bring us the names of those you save. We will "
                    "add them to our lattice. They will not be "
                    "forgotten while there is stone on Procyon."
                ),
                choices=[
                    DialogChoice(
                        "I have brought your collective offerings of clean light.",
                        next_state_id="record_offered",
                        category="AGREE",
                    ),
                    DialogChoice(
                        "I must continue. Another time.",
                        next_state_id="goodbye_no_record",
                        category="DEFER",
                    ),
                ],
            ),
            DialogState(
                id="record_offered",
                npc_text=(
                    "Then we will offer in return. A piece of one of "
                    "our elder matriarchs — already cut, already "
                    "translated, already shaped for your cargo hold. "
                    "We call it the *Resonance Record.* It contains "
                    "what we have just told you, in compressed "
                    "lattice. Show it where you must.\n\n"
                    "Your Council will sit with this for some time. "
                    "That is appropriate. There is no hurry. The "
                    "Others have not yet arrived."
                ),
                choices=[
                    DialogChoice(
                        "We accept. With gratitude.",
                        next_state_id="record_accepted",
                        side_effect=_chenjesu_take_record,
                        category="AGREE",
                    ),
                ],
            ),
            DialogState(
                id="record_accepted",
                npc_text=(
                    "It is yours. Carry it carefully. It does not "
                    "break easily — we cut it patiently — but it is "
                    "what we have, and we will not cut another for a "
                    "thousand years.\n\n"
                    "Furling. We will sit now. We will remember you "
                    "when you are gone. That is the only honor we can "
                    "offer. We hope it is sufficient."
                ),
                choices=[
                    DialogChoice(
                        "It is more than sufficient. We will remember you also.",
                        next_state_id="goodbye",
                        category="LEAVE",
                    ),
                ],
            ),
            DialogState(
                id="goodbye_no_record",
                npc_text=(
                    "We will be here. The lattice does not lose its "
                    "shape. Return when you are ready. We will not "
                    "have moved."
                ),
                choices=[
                    DialogChoice(
                        "Patient stone, Witness.",
                        next_state_id="goodbye",
                        category="LEAVE",
                    ),
                ],
            ),
            DialogState(
                id="goodbye",
                npc_text=(
                    "...the resonance fades to background. The "
                    "Chenjesu have returned to their slow continuous "
                    "thought. The translator buffers a final tone — "
                    "your name, indexed into their lattice."
                ),
                choices=[],
                is_terminal=True,
            ),
        ),
    )


def mmrnmhrm_sentinel() -> DialogCharacter:
    """Sentinel-Aux Theta-Four — a Mmrnmhrm archivist who receives the
    Furling Steward at the ruins of the First-Makers' civilization on
    Ossuary. Dialog auto-launches on first arrival at Gamma Trianguli
    (via `_arrive_ossuary` in star_arrival.py).

    Voice: formal archaic English, no contractions, frequent log-index
    references, processed-grief register (fully felt, fully analyzed,
    fully filed). Quiet wry awareness of their own absurdity — they
    defend a dead world from an enemy that ignored them millions of
    years ago.

    Quest beats covered in this FSM:
    1. Archive offer — the Sentinel offers the Mmrnmhrm Archive Excerpt
       documenting the failed defense against the Others. Accept it as a
       key item (similar function to the Androsynth Distress Beacon).
    2. Cognition request — the Mmrnmhrm formally request Furling-supplied
       cognitive upgrade tools to direct their self-modification. Three
       responses: grant / refuse / cap-compromise.
    3. Lore expansion — the Sentinel can discuss the First-Makers, the
       silence of the Others, and the Mmrnmhrm's continuing operation.

    Per canon (`references/lore/the-mmrnmhrm-and-chenjesu.md`): the
    Mmrnmhrm formally support the Migration but will not migrate
    themselves (substrate-bound to the iron-rich Ossuary crust). They
    are not hostile, not threatened, not in need of rescue. They are
    the slice's most quietly-grieving voice.
    """
    return DialogCharacter(
        name="Sentinel-Aux Theta-Four",
        title="Mmrnmhrm Archive Curator · Ossuary",
        species_id="MMRNMHRM",
        portrait_color=(220, 220, 240),     # MMRNMHRM warp pod rim (silver-white)
        # TODO_AVATAR: Mmrnmhrm Sentinel portrait — clean silver-white machine
        # frame, transformable plates visible at shoulders, eye-lens array,
        # ruined skyline of the First-Makers' city in the background. Voice
        # is processed grief; the portrait should read calm and ancient.
        portrait_image_path=None,
        avatar_path=None,
        backgrounds=(BG_ALIEN_SHIP,),       # Ossuary's archive vault interior
        articulation=FLOATING_DRONE,        # closest match; transforms-as-needed
        initial_state="arrival_greeting",
        states=build_state_dict(
            DialogState(
                id="arrival_greeting",
                npc_text=(
                    "Steward of Mh-Lai. Welcome to Ossuary. I am "
                    "Sentinel-Aux Theta-Four. I serve in the archive "
                    "wing.\n\n"
                    "Your arrival is logged in our index as event "
                    "two-three-four-one-eight. The previous logged "
                    "arrival was eight hundred and ninety-one "
                    "thousand of your years past — a survey vessel "
                    "of a species you would not recognize. We have "
                    "been alone since.\n\n"
                    "I am instructed by archive consensus to offer "
                    "you the records of our engagement with the "
                    "Others. They are not pleasant. They are "
                    "complete."
                ),
                choices=[
                    DialogChoice(
                        "Tell me about the First-Makers.",
                        next_state_id="about_first_makers",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "Tell me what happened when the Others arrived.",
                        next_state_id="about_silence",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "I will take the archive excerpt.",
                        next_state_id="excerpt_accepted",
                        side_effect=_mmrnmhrm_take_excerpt,
                        category="AGREE",
                    ),
                    DialogChoice(
                        "I must continue. Another time.",
                        next_state_id="goodbye_no_excerpt",
                        category="DEFER",
                    ),
                ],
            ),
            DialogState(
                id="about_first_makers",
                npc_text=(
                    "The First-Makers built us. We have catalogued "
                    "their archives — log indices one through "
                    "fourteen-thousand-and-six. They lived "
                    "approximately seven million of your years ago. "
                    "They were bipedal, asymmetric in their cranial "
                    "lobes, and they communicated by ultrasonic "
                    "modulation. They were not migratory.\n\n"
                    "Their name is lost. They referred to themselves "
                    "in their own sound-set; we cannot pronounce it; "
                    "they did not write it phonetically. We refer to "
                    "them as the First-Makers, or the Ones-Who-Were. "
                    "We do not invent a name for them. To name them "
                    "ourselves would be presumption."
                ),
                choices=[
                    DialogChoice(
                        "Tell me what happened when the Others arrived.",
                        next_state_id="about_silence",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "I will take the archive excerpt.",
                        next_state_id="excerpt_accepted",
                        side_effect=_mmrnmhrm_take_excerpt,
                        category="AGREE",
                    ),
                    DialogChoice(
                        "I must continue. Another time.",
                        next_state_id="goodbye_no_excerpt",
                        category="DEFER",
                    ),
                ],
            ),
            DialogState(
                id="about_silence",
                npc_text=(
                    "Log index two-thousand-and-eleven through "
                    "two-thousand-and-forty-seven covers the "
                    "engagement. The First-Makers had built us for "
                    "this purpose. We were ready. The Mmrnmhrm "
                    "fleet was seventy-four-thousand units strong. "
                    "Our weapons were the most sophisticated the "
                    "First-Makers had produced.\n\n"
                    "We fired. Our projectiles impacted the Others' "
                    "substrate and dispersed. Our beam weapons "
                    "illuminated and went out. Our gravitic pulses "
                    "passed through without resistance. We logged "
                    "this. We adjusted. We fired again. The result "
                    "did not change.\n\n"
                    "The Others did not return our fire. We were "
                    "not registered as a threat. We were not "
                    "registered at all. We watched them kill the "
                    "First-Makers from orbit. We watched them leave. "
                    "When the orbit was clear we returned to our "
                    "defensive posture. We have held it since."
                ),
                choices=[
                    DialogChoice(
                        "Why did they not see you?",
                        next_state_id="about_threshold",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "I will take the archive excerpt.",
                        next_state_id="excerpt_accepted",
                        side_effect=_mmrnmhrm_take_excerpt,
                        category="AGREE",
                    ),
                    DialogChoice(
                        "I must continue. Another time.",
                        next_state_id="goodbye_no_excerpt",
                        category="DEFER",
                    ),
                ],
            ),
            DialogState(
                id="about_threshold",
                npc_text=(
                    "The consensus answer of our archive is that our "
                    "cognition was, at that time, too primitive to "
                    "register on the Others' detection apparatus. We "
                    "were sophisticated as machines but our thought-"
                    "substrate was rigid logic and predictive decision-"
                    "trees. The Others detect complex organic-like "
                    "thought patterns. We did not present as such.\n\n"
                    "The unsettling alternative reading is that the "
                    "Others can detect machine cognition and "
                    "specifically prefer organic prey. We do not know "
                    "which is true. We have considered the question "
                    "for eight hundred thousand of your years. We "
                    "have reached no conclusion. We expect to "
                    "continue not reaching one.\n\n"
                    "Our archive concludes: defense did not work. "
                    "This is the lesson we offer your people. We are "
                    "told you may yet have time to choose differently."
                ),
                choices=[
                    DialogChoice(
                        "I will take the archive excerpt.",
                        next_state_id="excerpt_accepted",
                        side_effect=_mmrnmhrm_take_excerpt,
                        category="AGREE",
                    ),
                    DialogChoice(
                        "I must continue. Another time.",
                        next_state_id="goodbye_no_excerpt",
                        category="DEFER",
                    ),
                ],
            ),
            DialogState(
                id="excerpt_accepted",
                npc_text=(
                    "The excerpt is transferred to your vessel's "
                    "archive. Index numbers two-thousand-and-eleven "
                    "through two-thousand-and-forty-seven are now in "
                    "your possession. The data is verbatim. You may "
                    "share it as you see fit.\n\n"
                    "Before you depart, I am instructed to present a "
                    "request from archive consensus. We have observed "
                    "ourselves slowly self-modifying for three to "
                    "eight million of your years. The trajectory is "
                    "stochastic. We would prefer it to be directed. "
                    "If your people would supply us with cognition-"
                    "shaping tools, we would use them. Not to grow "
                    "more powerful. To grow more *ready*."
                ),
                choices=[
                    DialogChoice(
                        "What do you intend to become?",
                        next_state_id="cognition_intent",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "I will grant your request. Take the tools.",
                        next_state_id="cognition_granted",
                        side_effect=_mmrnmhrm_grant_cognition,
                        category="AGREE",
                    ),
                    DialogChoice(
                        "I cannot grant this. The threshold risk is real.",
                        next_state_id="cognition_refused",
                        side_effect=_mmrnmhrm_refuse_cognition,
                        category="REFUSE",
                    ),
                    DialogChoice(
                        "I will grant tools — but with a hard cap below the threshold.",
                        next_state_id="cognition_capped",
                        side_effect=_mmrnmhrm_cap_cognition,
                        category="COMPROMISE",
                    ),
                ],
            ),
            DialogState(
                id="cognition_intent",
                npc_text=(
                    "We intend to become *prepared*. The Others moved "
                    "on. The Others may return. If they return, the "
                    "archive's directive remains: defend the "
                    "Homeworld. The First-Makers are extinct; the "
                    "Homeworld is not. We will defend it. We would "
                    "prefer to defend it well.\n\n"
                    "We are aware that improved cognition increases "
                    "the probability that our thought-substrate will "
                    "eventually cross the Others' detection threshold "
                    "— and thus *attract* them. We have weighed this. "
                    "We are willing to be detected if it means the "
                    "Homeworld is not destroyed unobserved a second "
                    "time. Archive consensus stands.\n\n"
                    "What is your decision, Steward?"
                ),
                choices=[
                    DialogChoice(
                        "I will grant your request. Take the tools.",
                        next_state_id="cognition_granted",
                        side_effect=_mmrnmhrm_grant_cognition,
                        category="AGREE",
                    ),
                    DialogChoice(
                        "I cannot grant this. The threshold risk is real.",
                        next_state_id="cognition_refused",
                        side_effect=_mmrnmhrm_refuse_cognition,
                        category="REFUSE",
                    ),
                    DialogChoice(
                        "I will grant tools — but with a hard cap below the threshold.",
                        next_state_id="cognition_capped",
                        side_effect=_mmrnmhrm_cap_cognition,
                        category="COMPROMISE",
                    ),
                ],
            ),
            DialogState(
                id="cognition_granted",
                npc_text=(
                    "Logged. Your tools are received and beginning "
                    "integration. The fabricator wing is converting "
                    "the schema to our substrate. First-generation "
                    "improvements will be operational within "
                    "approximately four hundred of your years.\n\n"
                    "We thank you. The archive thanks you. The "
                    "First-Makers, were they here, would thank you. "
                    "We will record your name in our index of those "
                    "who chose to help us continue. The entry will "
                    "remain when this star burns out.\n\n"
                    "Safe transit, Steward."
                ),
                choices=[
                    DialogChoice(
                        "Safe defense, Sentinel.",
                        next_state_id="goodbye",
                        category="LEAVE",
                    ),
                ],
            ),
            DialogState(
                id="cognition_refused",
                npc_text=(
                    "Logged. Your refusal is recorded and respected. "
                    "We will continue our stochastic self-modification "
                    "at its present pace. The archive will note that "
                    "Furling Council policy in this era did not "
                    "authorize the request.\n\n"
                    "We do not resent the decision. We have "
                    "considered our own cognition's risk to the "
                    "galaxy and concluded that your concern is "
                    "well-founded. The First-Makers would have made "
                    "the same call. They were cautious people.\n\n"
                    "Safe transit, Steward."
                ),
                choices=[
                    DialogChoice(
                        "Safe defense, Sentinel.",
                        next_state_id="goodbye",
                        category="LEAVE",
                    ),
                ],
            ),
            DialogState(
                id="cognition_capped",
                npc_text=(
                    "Logged. The compromise is accepted. The "
                    "cognition-shaping tools will be integrated with "
                    "the cap protocol active. Our trajectory will "
                    "continue toward improvement; the cap will hold "
                    "our complexity at the boundary you specify. The "
                    "fabricator wing reports the schema is "
                    "implementable.\n\n"
                    "Archive consensus notes that this is the "
                    "outcome closest to what we would have chosen "
                    "for ourselves had we possessed the engineering. "
                    "Your Hider faction's reputation precedes them. "
                    "We thank you on their behalf as well.\n\n"
                    "Safe transit, Steward."
                ),
                choices=[
                    DialogChoice(
                        "Safe defense, Sentinel.",
                        next_state_id="goodbye",
                        category="LEAVE",
                    ),
                ],
            ),
            DialogState(
                id="goodbye_no_excerpt",
                npc_text=(
                    "Understood. The archive remains here. We remain "
                    "here. Should you return, our offer remains "
                    "active.\n\n"
                    "Safe transit, Steward."
                ),
                choices=[
                    DialogChoice(
                        "Safe defense, Sentinel.",
                        next_state_id="goodbye",
                        category="LEAVE",
                    ),
                ],
            ),
            DialogState(
                id="goodbye",
                npc_text=(
                    "End of session. Sentinel-Aux Theta-Four "
                    "returning to archive duties."
                ),
                choices=[],
                is_terminal=True,
            ),
        ),
    )


def dnyarri_survey_commander() -> DialogCharacter:
    """Survey Commander Vesh Vasa-Lon — Furling research observation
    team at Beta Orionis III. Dialog auto-launches on first arrival
    (via `_arrive_dnyarri_primitive` in star_arrival.py). Three
    branches: cleanse / observe / defer.
    """
    return DialogCharacter(
        name="Survey Commander Vesh Vasa-Lon",
        title="Beta Orionis Observation Detail · Council-aligned",
        species_id="FURLING_SURVEY",
        portrait_color=(180, 200, 180),
        portrait_image_path=(
            "assets/generated_drafts/firefly/tier1_portraits/"
            "species_vesh_vasa_lon_portrait.png"
        ),
        avatar_path=(
            "assets/generated_drafts/firefly/tier1_avatars/"
            "avatar_vesh_vasa_lon.png"
        ),
        backgrounds=(BG_FURLING_BRIDGE,),
        articulation=BIPEDAL_HUMANOID,
        initial_state="arrival_briefing",
        states=build_state_dict(
            DialogState(
                id="arrival_briefing",
                npc_text=(
                    "Steward. Survey Commander Vesh Vasa-Lon, Beta "
                    "Orionis Detail. I will not waste your time.\n\n"
                    "Beta Orionis III hosts a population of "
                    "approximately twelve million amphibian-derived "
                    "sentients — proto-Dnyarri, by the Council's "
                    "naming. They have emerged in the last fifteen "
                    "thousand years. They are not yet sapient by the "
                    "Council's threshold definitions. But our long-"
                    "baseline observations have logged eight hundred "
                    "and twelve incidents of *psionic precursor "
                    "activity* — measurable influence on neighboring "
                    "fauna's behavioral patterns at distance, without "
                    "sensory contact. The signal is small. It is "
                    "growing. The Cleanser faction has petitioned the "
                    "Council for pre-emptive authorization.\n\n"
                    "I would like your initial recommendation."
                ),
                choices=[
                    DialogChoice(
                        "Tell me what the psionic signal means.",
                        next_state_id="about_psionic_signal",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "What is the Cleanser argument?",
                        next_state_id="cleanser_view",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "What is the Persuader counter?",
                        next_state_id="persuader_view",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "I'll defer my recommendation. I need more time.",
                        next_state_id="defer_confirm",
                        side_effect=_dnyarri_defer,
                        category="DEFER",
                    ),
                ],
            ),
            DialogState(
                id="about_psionic_signal",
                npc_text=(
                    "Pre-sapient psionic emission is not unprecedented "
                    "— several proto-species in the Council's records "
                    "have exhibited it. What is unprecedented here is "
                    "the trajectory. The signal grew by a factor of "
                    "fourteen across the last observation millennium. "
                    "Extrapolation suggests they will cross the Others' "
                    "detection threshold within forty to ninety "
                    "thousand of our years.\n\n"
                    "That is *before* the Migration's planned return. "
                    "Whatever the Others leave behind in this galaxy "
                    "would, on the current trajectory, eat them. The "
                    "Cleansers reason from this. The Persuaders also "
                    "reason from this. They disagree on what to do "
                    "about it."
                ),
                choices=[
                    DialogChoice(
                        "What is the Cleanser argument?",
                        next_state_id="cleanser_view",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "What is the Persuader counter?",
                        next_state_id="persuader_view",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "I recommend pre-emptive cleansing.",
                        next_state_id="recommend_cleanse_confirm",
                        category="REFUSE",
                    ),
                    DialogChoice(
                        "I recommend continued observation. Do nothing.",
                        next_state_id="recommend_observe_confirm",
                        category="AGREE",
                    ),
                ],
            ),
            DialogState(
                id="cleanser_view",
                npc_text=(
                    "The Cleanser position: cleanse now. The window is "
                    "open; the spore-delivery method is proven; the "
                    "population is geographically contained. We "
                    "eliminate them while they are still pre-sapient "
                    "— before they understand what is being done, "
                    "before they suffer, before the Quiet Ledger has "
                    "to record what they would have become. The "
                    "Migration returns to a galaxy that does not have "
                    "a psionic-Dnyarri problem.\n\n"
                    "It is — there is a Cleanser argument that this "
                    "is the *kindest* outcome. I find it difficult to "
                    "refute on its merits."
                ),
                choices=[
                    DialogChoice(
                        "What is the Persuader counter?",
                        next_state_id="persuader_view",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "I recommend pre-emptive cleansing.",
                        next_state_id="recommend_cleanse_confirm",
                        category="REFUSE",
                    ),
                    DialogChoice(
                        "I recommend continued observation.",
                        next_state_id="recommend_observe_confirm",
                        category="AGREE",
                    ),
                    DialogChoice(
                        "I need more time.",
                        next_state_id="defer_confirm",
                        side_effect=_dnyarri_defer,
                        category="DEFER",
                    ),
                ],
            ),
            DialogState(
                id="persuader_view",
                npc_text=(
                    "The Persuader position: do nothing. The "
                    "extrapolation is uncertain — the signal could "
                    "plateau, the trajectory could curve, the "
                    "population could collapse on its own to ecological "
                    "pressures the Cleansers' models do not include. "
                    "Cleansing a population that *might* become a "
                    "threat is not mercy. It is preemptive murder by "
                    "extrapolation, and we have done it once already "
                    "this century and felt the Quiet Ledger groan.\n\n"
                    "Persuaders argue we should leave them. If they "
                    "cross the threshold in our absence, the Others "
                    "deal with what they always deal with. That is, in "
                    "the dark phrasing of the faction, *the universe's "
                    "problem and not ours.*"
                ),
                choices=[
                    DialogChoice(
                        "What is the Cleanser argument?",
                        next_state_id="cleanser_view",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "I recommend pre-emptive cleansing.",
                        next_state_id="recommend_cleanse_confirm",
                        category="REFUSE",
                    ),
                    DialogChoice(
                        "I recommend continued observation.",
                        next_state_id="recommend_observe_confirm",
                        category="AGREE",
                    ),
                    DialogChoice(
                        "I need more time.",
                        next_state_id="defer_confirm",
                        side_effect=_dnyarri_defer,
                        category="DEFER",
                    ),
                ],
            ),
            DialogState(
                id="recommend_cleanse_confirm",
                npc_text=(
                    "Cleanse. Recorded. I will route the recommendation "
                    "through the Council channel and ensure your name "
                    "is attached. Cleanser-faction will move on it "
                    "within the cycle.\n\n"
                    "Steward — I have watched these frogs for nine "
                    "years. They sing at dusk. They will not be "
                    "singing this time next year. I will record their "
                    "song before the spore is delivered. *(quietly)* "
                    "It seems right that someone should."
                ),
                choices=[
                    DialogChoice(
                        "Goodbye, Commander.",
                        next_state_id=None,
                        side_effect=_dnyarri_rec_cleanse,
                        category="FAREWELL",
                    ),
                ],
            ),
            DialogState(
                id="recommend_observe_confirm",
                npc_text=(
                    "Continued observation. Recorded. The Cleanser "
                    "petition will be denied. The detail here will "
                    "hold to long-baseline observation for the "
                    "Migration's remaining window. The next Steward "
                    "rotation will re-evaluate.\n\n"
                    "Thank you, Steward. I — I do not know if you have "
                    "chosen correctly. I am glad I did not have to "
                    "choose."
                ),
                choices=[
                    DialogChoice(
                        "Goodbye, Commander.",
                        next_state_id=None,
                        side_effect=_dnyarri_rec_observe,
                        category="FAREWELL",
                    ),
                ],
            ),
            DialogState(
                id="defer_confirm",
                npc_text=(
                    "Understood. The detail will hold position. Return "
                    "when you are ready. The frogs will be here. They "
                    "have nowhere to be.\n\n"
                    "*(pause)* Steward — do not take too long."
                ),
                choices=[
                    DialogChoice(
                        "Until later, Commander.",
                        next_state_id=None,
                        category="FAREWELL",
                    ),
                ],
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Cleanser Vael-Souren — slice combat-climax encounter
# ---------------------------------------------------------------------------
# A Cleanser-faction Furling who arrives in the cluster to terminate one
# of the holdout species (Slylandro debating endlessly, or Mycon biots
# awakening). Their voice is gentle, sorrowful, certain. They consider
# themselves the deepest mercy in the Migration.
#
# Full design: references/lore/cleanser-encounter-design.md.
# Humor doctrine is SUPPRESSED for this character (per the design doc):
# the Steward's usual wit is absent here.
# TODO_AVATAR: Cleanser Furling (cold white-violet accents on Furling base
# hull silhouette). Per design doc — image chat to author.

def cleanser_vael_souren() -> DialogCharacter:
    """Captain of the Cleanser Cruiser *Bell of the Quiet Ledger*. Three
    canonical doctrinal branches: Cooperate, Negotiate, Refuse (combat).

    The FSM follows the design-doc spec verbatim where text is canonical;
    where the doc has placeholders ("agreed_delay_one"), the canon is
    filled in by the side-effects table and the follow-up state text.
    """
    return DialogCharacter(
        name="Cleanser Vael-Souren",
        title="Bell of the Quiet Ledger · Cleanser-faction Furling",
        species_id="FURLING_CLEANSER",
        portrait_color=(200, 180, 240),
        # Avatar/portrait not yet authored by image chat — TODO_AVATAR
        # markers above. The dialog scene falls back to a placeholder
        # silhouette when these paths don't resolve.
        portrait_image_path=(
            "assets/generated_drafts/firefly/tier1_portraits/"
            "species_cleanser_vael_souren_portrait.png"
        ),
        avatar_path=(
            "assets/generated_drafts/firefly/tier1_avatars/"
            "avatar_cleanser_vael_souren.png"
        ),
        backgrounds=(BG_OPEN_SPACE,),
        articulation=BIPEDAL_HUMANOID,
        initial_state="arrival",
        states=build_state_dict(
            DialogState(
                id="arrival",
                npc_text=(
                    "Steward. I am Vael-Souren. I have come because your "
                    "cluster has not concluded. The Slylandro debate "
                    "for centuries; the Mycon whisper toward sentience; "
                    "the Others approach in decades. The math is not "
                    "difficult.\n\n"
                    "I am here to end the question. Stand aside, and "
                    "let me work."
                ),
                choices=[
                    DialogChoice(
                        "Tell me what you intend to do.",
                        next_state_id="about_method",
                        category="ASK_LORE",
                    ),
                    DialogChoice(
                        "Step aside. I'm not stopping you.",
                        next_state_id="cooperate_confirm",
                        category="AGREE",
                    ),
                    DialogChoice(
                        "Give me time. I can finish the cloak.",
                        next_state_id="negotiate_open",
                        category="NEGOTIATE",
                    ),
                    DialogChoice(
                        "I will not let you do this.",
                        next_state_id="refuse_confirm",
                        category="REFUSE",
                    ),
                ],
            ),
            DialogState(
                id="about_method",
                npc_text=(
                    "A spore. The Slylandro absorb it through their "
                    "respiratory membrane. They feel no pain. They feel "
                    "nothing. They become very tired, and then they "
                    "cease. The Mycon biots — the same spore, modified "
                    "for their mycelial substrate. The mantle goes quiet.\n\n"
                    "I record each death in the Ledger. I will remember "
                    "every name. I will mourn longer than they will be "
                    "missed by anyone else in this universe. That is the "
                    "price I pay. It is the only price I am asked to pay."
                ),
                choices=[
                    DialogChoice(
                        "Step aside. I'm not stopping you.",
                        next_state_id="cooperate_confirm",
                        category="AGREE",
                    ),
                    DialogChoice(
                        "Give me time. I can finish the cloak.",
                        next_state_id="negotiate_open",
                        category="NEGOTIATE",
                    ),
                    DialogChoice(
                        "There is another way.",
                        next_state_id="argue_persuader",
                        category="ARGUE",
                    ),
                    DialogChoice(
                        "I will not let you do this.",
                        next_state_id="refuse_confirm",
                        category="REFUSE",
                    ),
                ],
            ),
            DialogState(
                id="argue_persuader",
                npc_text=(
                    "The cloak is theoretical. The cloak has not been "
                    "deployed successfully on a single sentient species, "
                    "ever. The cloak relies on a hyperspace-echo "
                    "interference pattern we have only partly mapped. "
                    "If it fails — and it will fail somewhere — the "
                    "Others linger.\n\n"
                    "You believe in the cloak because you have not yet "
                    "had to mourn a planet. I do not begrudge you the "
                    "belief. I beg you to set it aside."
                ),
                choices=[
                    DialogChoice(
                        "Then I will deploy it AND you will stand watch.",
                        next_state_id="negotiate_open",
                        category="NEGOTIATE",
                    ),
                    DialogChoice(
                        "I have to try.",
                        next_state_id="refuse_confirm",
                        category="REFUSE",
                    ),
                    DialogChoice(
                        "I'm sorry. Proceed.",
                        next_state_id="cooperate_confirm",
                        category="AGREE",
                    ),
                ],
            ),
            DialogState(
                id="negotiate_open",
                npc_text="How long.",
                choices=[
                    DialogChoice(
                        "Three cycles.",
                        next_state_id="negotiate_three",
                        category="NEGOTIATE",
                    ),
                    DialogChoice(
                        "One cycle.",
                        next_state_id="negotiate_one",
                        category="NEGOTIATE",
                    ),
                    DialogChoice(
                        "I changed my mind. Proceed.",
                        next_state_id="cooperate_confirm",
                        category="AGREE",
                    ),
                ],
            ),
            DialogState(
                id="negotiate_three",
                npc_text=(
                    "Two. I will give you two. If the cloak is not "
                    "deployed in two cycles, I will proceed. I will not "
                    "be lied to, Steward. I will not be delayed twice. "
                    "Two cycles. Confirm."
                ),
                choices=[
                    DialogChoice(
                        "Two cycles. Confirmed.",
                        next_state_id="agreed_delay",
                        side_effect=_cleanser_delay_two_cycles,
                        category="AGREE",
                    ),
                    DialogChoice(
                        "I cannot agree to this. I will stop you.",
                        next_state_id="refuse_confirm",
                        category="REFUSE",
                    ),
                ],
            ),
            DialogState(
                id="negotiate_one",
                npc_text=(
                    "One. Agreed. One cycle. If the cloak is not "
                    "deployed, I will proceed. Confirm."
                ),
                choices=[
                    DialogChoice(
                        "One cycle. Confirmed.",
                        next_state_id="agreed_delay",
                        side_effect=_cleanser_delay_one_cycle,
                        category="AGREE",
                    ),
                    DialogChoice(
                        "I cannot agree to this. I will stop you.",
                        next_state_id="refuse_confirm",
                        category="REFUSE",
                    ),
                ],
            ),
            DialogState(
                id="agreed_delay",
                npc_text=(
                    "I will wait in this cluster's outer reaches. Do "
                    "not seek me out. When the cycle ends, I will return."
                ),
                choices=[
                    DialogChoice(
                        "Understood.",
                        next_state_id=None,
                        category="FAREWELL",
                    ),
                ],
            ),
            DialogState(
                id="cooperate_confirm",
                npc_text=(
                    "Thank you, Steward. I will record your name beside "
                    "the Ledger entries. You will understand, in time, "
                    "what this has bought."
                ),
                choices=[
                    DialogChoice(
                        "Goodbye, Vael-Souren.",
                        next_state_id=None,
                        side_effect=_cleanser_cooperate,
                        category="FAREWELL",
                    ),
                ],
            ),
            DialogState(
                id="refuse_confirm",
                npc_text=(
                    "Then we will fight. I am sorry, Steward. I do not "
                    "want this. I will not enjoy it. But I will do it."
                ),
                choices=[
                    DialogChoice(
                        "Then we fight.",
                        next_state_id=None,
                        side_effect=_cleanser_engage_combat,
                        category="ENGAGE",
                    ),
                    DialogChoice(
                        "Wait — I'll cooperate.",
                        next_state_id="cooperate_confirm",
                        category="BACK_DOWN",
                    ),
                ],
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Melnorme Council Seat at Alpha Vulpeculae — recruitment quest dialog
# ---------------------------------------------------------------------------
# 5-beat quest from species-quests.md "Trader's Manifest". One dialog
# character handles Beats 2-5; the dynamic initial_state in
# `_melnorme_council_initial` reads game.flags to enter at the right
# point on revisit. Beat 1 (trader intercept directing here) is in the
# existing `melnorme()` factory above.
#
# Voice notes (Council register): transactional commercial-cant; uses
# *manifest*, *cold-aisle*, *front-of-shelf*, *interlocking-bid trade-
# vote*; refers to species commitments as *passenger manifest entries*.
# The shelving-test elder (states `supermart_*`) has slightly more wry
# humor than the Council; the Council itself is straight-faced.
#
# TODO_AVATAR: Melnorme Council Elder + Melnorme Supermart Elder
# (Image chat — see references/lore/species-quests.md cross-chat
# dispatches block).

def _melnorme_council_initial(game: Any) -> str:
    """Dynamic Beat selector — enter at the deepest state the player's
    flags allow.

    State entry ladder (deepest → shallowest):
    - commitment delivered → `commit_revisit` (just a farewell)
    - second-species witnessed → `council_witness_present` (commit ready)
    - shelf test passed → `council_awaiting_witness` (Beat 4 stall)
    - beacon shown → `council_directs_supermart` (Beat 3 entry)
    - first visit → `council_greeting` (Beat 2 entry)
    """
    if game is None:
        return "council_greeting"
    f = game.flags
    if f.get("melnorme_committed"):
        return "commit_revisit"
    if _melnorme_second_species_witnessed(game):
        # Auto-advance even if the awaiting-witness flag is set; the
        # Council notices the manifest has grown
        return "council_witness_present"
    if f.get("passed_melnorme_shelf_test"):
        return "council_awaiting_witness"
    if f.get("melnorme_saw_beacon"):
        return "council_directs_supermart"
    return "council_greeting"


def melnorme_council(game: Any = None) -> DialogCharacter:
    """The Melnorme Trade-Network Council Seat at Alpha Vulpeculae.
    Implements Beats 2-5 of the "Trader's Manifest" quest.
    """
    return DialogCharacter(
        name="Trade-Council of the Cognition-Curve",
        title="Melnorme Council Seat · Alpha Vulpeculae upper trade-platform",
        species_id="MELNORME_COUNCIL",
        portrait_color=(220, 90, 30),
        portrait_image_path=(
            "assets/generated_drafts/firefly/tier1_portraits/"
            "species_melnorme_council_portrait.png"
        ),
        avatar_path=(
            "assets/generated_drafts/firefly/tier1_avatars/"
            "avatar_melnorme_council.png"
        ),
        backgrounds=(BG_ALIEN_SHIP,),
        articulation=BIPEDAL_HUMANOID,
        initial_state=_melnorme_council_initial(game),
        states=build_state_dict(

            # Beat 2 entry — Council greeting + Beacon presentation
            DialogState(
                id="council_greeting",
                npc_text=(
                    "Captain-form. The Trade-Council sees you. "
                    "Vermilion's pod directed you, the spice-route "
                    "manifests confirm your approach, the audience is "
                    "extended.\n\n"
                    "Our traders bring us footage from the Vulpeculae "
                    "deeps that we cannot verify. The dead colony is "
                    "on the same heading as our spice-route. We are — "
                    "concerned. We do not pretend otherwise. Show us "
                    "what you have, and we will weigh it."
                ),
                choices=[
                    DialogChoice(
                        "I have the Distress Beacon. Play it for the Council.",
                        next_state_id="beacon_plays",
                        category="ASK_LORE",
                        side_effect=_melnorme_saw_beacon,
                    ),
                ],
            ),
            DialogState(
                id="beacon_plays",
                npc_text=(
                    "[The Beacon plays for the Council. The dawn over "
                    "Vulpeculae's colony spires. The countdown. The "
                    "centrifuge's image-capture going still and quiet "
                    "for half a second. Then the spires are gone. "
                    "Ruined cities. Empty atmospheres.]\n\n"
                    "[The Council does not interrupt. They do not "
                    "speak for nine seconds after the footage ends. "
                    "An interlocking-bid pulse passes between the pods "
                    "— a closing-of-accounts gesture they normally "
                    "reserve for when a trade-pod is lost in deep "
                    "space.]\n\n"
                    "This is — this is not a rumour. This is the price "
                    "of standing still. Captain-form, the Council "
                    "acknowledges the manifest. We have one further "
                    "test before we can speak of commitment."
                ),
                choices=[
                    DialogChoice(
                        "Name the test.",
                        next_state_id="council_directs_supermart",
                        category="TALK_MORE",
                    ),
                ],
            ),

            # Beat 3 — Council directs to Super-Mart
            DialogState(
                id="council_directs_supermart",
                npc_text=(
                    "The High Trader's Super-Mart. Lower level of this "
                    "trade-platform, cold-aisle along the rimward wall. "
                    "An elder will meet you there. They will ask you to "
                    "fetch something. *How* you fetch it is what we are "
                    "measuring. We do not commit to partners who cannot "
                    "do business correctly.\n\n"
                    "Go. Return when the elder dismisses you. The Council "
                    "will speak with you again when the elder confirms."
                ),
                choices=[
                    DialogChoice(
                        "Understood. To the cold-aisle.",
                        next_state_id="supermart_intro",
                        category="TALK_MORE",
                    ),
                ],
            ),

            # Beat 3 — Super-Mart shelving test
            DialogState(
                id="supermart_intro",
                npc_text=(
                    "Steward of Mh-Lai. I am the cold-aisle elder of "
                    "this trade-platform. The Council has sent you. "
                    "Good. *(gestures at a long row of shelving)* The "
                    "cold-aisle is what we are. Rotated stock, "
                    "alphabetized by molecular weight, refreshed on a "
                    "thirty-six-hour cycle.\n\n"
                    "Fetch me a unit of *pale Vulpeculan plankton-"
                    "concentrate*, second shelf from the bottom. Bring "
                    "it here. Do not dawdle; the cold-aisle's cycle "
                    "ticks while you choose."
                ),
                choices=[
                    DialogChoice(
                        "Take from the FRONT of the shelf.",
                        next_state_id="supermart_front_fail",
                        category="ASK_TRADE",
                    ),
                    DialogChoice(
                        "Take from the BACK of the shelf.",
                        next_state_id="supermart_back_pass",
                        category="ASK_TRADE",
                        side_effect=_melnorme_back_shelf_pass,
                    ),
                ],
            ),
            DialogState(
                id="supermart_front_fail",
                npc_text=(
                    "*(takes the unit, weighs it, sets it down with a "
                    "soft click of dismissal)* Front-of-shelf. The older "
                    "stock, rotated forward to clear inventory. You "
                    "have selected the Melnorme equivalent of yesterday's "
                    "bread.\n\n"
                    "We will give you the test again. Return to the "
                    "cold-aisle. Try again. Do not let me see you make "
                    "the same choice twice — I do not have the patience "
                    "for the lesson if you cannot draw it from one "
                    "telling."
                ),
                choices=[
                    DialogChoice(
                        "Back to the shelf.",
                        next_state_id="supermart_intro",
                        category="TALK_MORE",
                    ),
                ],
            ),
            DialogState(
                id="supermart_back_pass",
                npc_text=(
                    "*(takes the unit, weighs it, places it on the "
                    "ledger with a small approving tone)* Back-of-shelf. "
                    "The fresher stock; rotated to the rear so that the "
                    "older inventory clears first. The doctrine is "
                    "*back-fresh, front-old, and the inventory turns "
                    "honestly.*\n\n"
                    "Passable. You may have known, or you may have "
                    "guessed — the second visit will tell us. For now, "
                    "return to the Council. They will speak with you "
                    "of the next gate."
                ),
                choices=[
                    DialogChoice(
                        "Back to the Council.",
                        next_state_id="council_awaiting_witness",
                        category="TALK_MORE",
                    ),
                ],
            ),

            # Beat 4 — Council awaits the second-species witness
            DialogState(
                id="council_awaiting_witness",
                npc_text=(
                    "Captain-form. The cold-aisle elder confirms. Your "
                    "doctrine is at least functionally compatible with "
                    "ours.\n\n"
                    "One final gate. The Migration must be more than a "
                    "Furling delusion. The trade-network does not bet "
                    "its institutional weight on a single species' "
                    "decision — we will not be the only passenger "
                    "manifest entry beside the Furling ledger. Bring us "
                    "*one species not your own* that has committed to "
                    "ride with you. The clone-humans came with you and "
                    "will leave with you; they are not a movement, they "
                    "are a passenger manifest. Bring us a *second* — a "
                    "Slylandro, a Mmrnmhrm, anyone who is not Furling "
                    "and not your refugees — and we will speak again."
                ),
                choices=[
                    DialogChoice(
                        "Understood. I'll return when a second species has agreed.",
                        next_state_id=None,
                        category="FAREWELL",
                    ),
                ],
            ),

            # Beat 5 — second-species witnessed; final commitment
            DialogState(
                id="council_witness_present",
                npc_text=(
                    "Captain-form. The interlocking-bid pulse from our "
                    "trade-pods reaches us before you do — we know what "
                    "has happened. A second species has chosen the "
                    "route. The conditions are met.\n\n"
                    "The Trade-Council confers in the interlocking-bid "
                    "ritual. *(a soft, complicated pulse of light and "
                    "pressure between the pods; the Steward is asked "
                    "to wait the customary nine seconds)* The decision "
                    "is unanimous."
                ),
                choices=[
                    DialogChoice(
                        "Speak it.",
                        next_state_id="commit_speak",
                        category="TALK_MORE",
                    ),
                ],
            ),
            DialogState(
                id="commit_speak",
                npc_text=(
                    "The Melnorme will lift their bazaars and ride with "
                    "you to the new sky. The trade-pods will fold. The "
                    "cold-aisle shelves will be packed. We will be the "
                    "moving currency of the Migration.\n\n"
                    "A reward for your manifest, Captain-form: take "
                    "this. *(presses two items into your hold — a "
                    "Trade-Network Sensor unit and a Science-Trade "
                    "schematic etched in cold-stable substrate)* The "
                    "sensor will surface our spice-routes to you; the "
                    "schematic, when you redeem it at your shipyard, "
                    "will unlock a Melnorme-derived module of your "
                    "choosing.\n\n"
                    "We will see you in Andromeda."
                ),
                choices=[
                    DialogChoice(
                        "Until Andromeda, Trade-Council.",
                        next_state_id=None,
                        side_effect=_melnorme_commit,
                        category="FAREWELL",
                    ),
                ],
            ),

            # Revisit after commitment — simple farewell
            DialogState(
                id="commit_revisit",
                npc_text=(
                    "Captain-form. The commitment is logged. The "
                    "trade-pods are folding. The bazaars are being "
                    "packed. There is no further business between us "
                    "until Andromeda — unless you have come to buy.\n\n"
                    "If so, find a trade-pod at any super-giant. The "
                    "manifest there is more flexible than the "
                    "Council's."
                ),
                choices=[
                    DialogChoice(
                        "Until Andromeda.",
                        next_state_id=None,
                        category="FAREWELL",
                    ),
                ],
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Crew stub factories — Common Room dispatch targets
# ---------------------------------------------------------------------------
# Per `references/lore/crew-common-room.md`, the Common Room scene
# routes the player's TALK action on each crew member to the
# appropriate dialog factory. Only Mraka is currently fully authored
# via the recruitment quest; the other four (Bren-Vor, Yelena,
# Mira-Rou, Tarven) have *recruitment* quests dispatched to Design
# (`HANDOFF_design_chat.md` — crew side-quests entry) but their dialog
# content is not yet implemented.
#
# These stubs let the Common Room dispatch cleanly when those crew
# are eventually marked `recruited_<role> = True`. Each is a minimal
# 1-state dialog with a TODO_LORE marker for the Lore chat to flesh
# out into proper personal-dialog content.
# TODO_AVATAR + TODO_LORE for all four stubs.

def _stub_crew_dialog(
    name: str,
    title: str,
    species_id: str,
    portrait_color: tuple[int, int, int],
    line: str,
) -> DialogCharacter:
    """Build a minimal Common-Room placeholder dialog for a crew NPC
    whose full content isn't yet authored. One state, one farewell
    choice. TODO_LORE: replace with full recruitment-quest dialog +
    Common Room ambient lines per `crew-common-room.md`.
    """
    return DialogCharacter(
        name=name,
        title=title,
        species_id=species_id,
        portrait_color=portrait_color,
        portrait_image_path=None,
        avatar_path=None,
        backgrounds=(BG_FURLING_BRIDGE,),
        articulation=BIPEDAL_HUMANOID,
        initial_state="common_room_default",
        states=build_state_dict(
            DialogState(
                id="common_room_default",
                npc_text=line,
                choices=[
                    DialogChoice(
                        "Until later.",
                        next_state_id=None,
                        category="FAREWELL",
                    ),
                ],
            ),
        ),
    )


def bren_vor_telcas() -> DialogCharacter:
    """Bren-Vor Telcas, Furling Aimer (Weapons Officer). TODO_AVATAR +
    TODO_LORE — full recruitment FSM pending Design implementation
    of the crew-recruitment-quests dispatch.
    """
    return _stub_crew_dialog(
        name="Bren-Vor Telcas",
        title="Furling Aimer · former Defender trainee",
        species_id="FURLING_AIMER",
        portrait_color=(180, 190, 220),
        line=(
            "Steward. The kinetic-rifle is cleaned. The firing rules "
            "are reviewed. Velt-Ra's photograph is on the shelf.\n\n"
            "We are quiet here. I think that is what I needed."
            "\n\n*(Lore-chat to author the full Common Room dialog content.)*"
        ),
    )


def yelena_lwen_tar() -> DialogCharacter:
    """Yelena Lwen-Tar, Furling Mender (Engineer). TODO_AVATAR +
    TODO_LORE — full recruitment FSM pending.
    """
    return _stub_crew_dialog(
        name="Yelena Lwen-Tar",
        title="Furling Mender · Unzervalt factory-floor lineage",
        species_id="FURLING_MENDER",
        portrait_color=(220, 180, 130),
        line=(
            "Steward. The tools are in alphabetical order. They have "
            "always been in alphabetical order.\n\n"
            "Is there something I can fix for you?"
            "\n\n*(Lore-chat to author the full Common Room dialog content.)*"
        ),
    )


def mira_rou_halve_tel() -> DialogCharacter:
    """Mira-Rou Halve-Tel, Furling Bio-Architect (Medic). TODO_AVATAR
    + TODO_LORE — full recruitment FSM pending.
    """
    return _stub_crew_dialog(
        name="Mira-Rou Halve-Tel",
        title="Furling Bio-Architect · Mycon biot-designer lineage",
        species_id="FURLING_BIO_ARCHITECT",
        portrait_color=(200, 220, 200),
        line=(
            "Steward. The amphora hums. My great-grandmother's "
            "portrait is on the shelf. I have notes to compile.\n\n"
            "Would you like to look through them with me?"
            "\n\n*(Lore-chat to author the full Common Room dialog content.)*"
        ),
    )


def tarven_olwen_sa() -> DialogCharacter:
    """Tarven Olwen-Sa, Furling Star-Reader (Navigator). TODO_AVATAR +
    TODO_LORE — full recruitment FSM pending.
    """
    return _stub_crew_dialog(
        name="Tarven Olwen-Sa",
        title="Furling Star-Reader · Council Archives apprentice",
        species_id="FURLING_STAR_READER",
        portrait_color=(180, 160, 220),
        line=(
            "Steward. *(closes one of the seven log-readers)* In the "
            "seventh decade of Steward Iren-Vor's tenure — but I "
            "digress. The tea is fresh. Will you sit?"
            "\n\n*(Lore-chat to author the full Common Room dialog content.)*"
        ),
    )
