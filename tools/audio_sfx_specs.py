"""All slice sound-effect specs as data.

Per Aaron's 2026-05-17 scope expansion:
  - UI feedback (12)
  - Per-ship weapon SFX: primary FIRE + primary IMPACT + special FIRE
    + special IMPACT, for each of 11 ships in src/scz/combat/ships.py (44)
  - Lander resource-gathering minigame (11)
  - Planet scanning sequence (7)
  TOTAL: 74 SFX

Sonic prompts are grounded in the per-species sonic_signature column
of tools/species_inventory.csv (the audio-chat update of 2026-05-17).
When the lore is specific, the prompt cites the lore. When the lore is
silent, the prompt fills in something creative + distinct from other
species (also per Aaron's directive).

Round 1 (the 4-sound validation sample so Aaron can hear the prompt
template before we burn the rest):
  ui_menu_select, weapon_furling_scout_primary_fire,
  lander_pickup_clink, scan_ping

Rounds 2+ contain the remaining 70 sounds.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SfxSpec:
    """A single sound-effect generation request."""
    name: str                # filename stem (no extension)
    category: str            # ui | weapon | lander | scan
    out_subdir: str          # path under assets/sfx/ where this file lands
    prompt: str              # ElevenLabs sound-generation prompt
    duration_s: float = 1.0  # 0.5-30; clamped at call time
    loop: bool = False       # eleven_text_to_sound_v2 only
    prompt_influence: float = 0.7
    species_id: str = ""     # cross-ref into species_inventory.csv
    # 1 = Round-1 sample; 2 = Round-2 expanded sample (targeted, ~20 sounds);
    # 3 = Round-3 re-rolls from listen-pass-2 feedback;
    # 4+ = remaining inventory queued for future rounds. Default is 4 so a
    # newly-added spec doesn't accidentally fire on the next --round N run.
    round: int = 4
    notes: str = ""
    # If set ("out_subdir/name"), the generator skips ElevenLabs and
    # produces this SFX by sample-reversing the named source SFX.
    # Use for fire/un-fire pair symmetries (e.g. Furling Scout's
    # special_fire = time-freeze; special_impact = time-unfreeze).
    reverse_of: str = ""


# ---------------------------------------------------------------------------
# A. UI feedback sounds (12) — under assets/sfx/ui/
# Standardize the prompt template: "<short verb-phrase>, sharp attack,
# quick decay, <retro/scifi modifier>". The 0.5s API floor is awkward
# for ticks; front-loaded transient + quick tail makes the perceived
# hit feel ~100-150ms.
# ---------------------------------------------------------------------------

UI_SFX: list[SfxSpec] = [
    # Round 2 (2026-05-17 re-roll): Aaron called Round-1 SFX "hard to
    # hear." Bumped durations slightly, sharpened the transient
    # descriptors, raised prompt_influence so the model leans harder
    # into the brief.
    SfxSpec(
        name="menu_select", category="ui", out_subdir="ui",
        prompt="loud confident retro-synth menu select click, percussive front-loaded transient, "
               "satisfying tactile feedback, FRONT-LOADED energy, bright but not shrill, "
               "1990s sci-fi computer interface, pronounced and audible",
        duration_s=0.6, prompt_influence=0.85, round=2,
        notes="Round-2 re-roll of Round-1 sample.",
    ),
    SfxSpec(
        name="menu_confirm", category="ui", out_subdir="ui",
        # Round 3: Aaron — "short higher-pitched bump similar to cancel but optimistic"
        prompt="very short bright optimistic bump, single high-pitched percussive blip, "
               "warm retro-synth attack with instant decay, sci-fi UI confirm, "
               "the OK sibling of a low cancel-bump",
        duration_s=0.3, prompt_influence=0.9, round=3,
        notes="Round-3 re-roll: short higher-pitch bump pair with menu_cancel",
    ),
    SfxSpec(
        name="menu_cancel", category="ui", out_subdir="ui",
        # Round 3: Aaron — "cancel should just be a short low bump sound"
        prompt="very short low bump, single deep percussive thump, "
               "warm muted retro-synth attack with instant decay, neutral sci-fi UI cancel, "
               "no melodic motif, just a low audible bump",
        duration_s=0.3, prompt_influence=0.9, round=3,
        notes="Round-3 re-roll: short low bump",
    ),
    SfxSpec(
        name="menu_invalid", category="ui", out_subdir="ui",
        prompt="dissonant low buzz error tone, sharp attack into short flat dampened decay, "
               "retro 16-bit error sound, frustrating but brief, clearly audible",
        duration_s=0.6, prompt_influence=0.85, round=2,
    ),
    SfxSpec(
        name="screen_transition", category="ui", out_subdir="ui",
        prompt="quick whoosh swelling and fading, sci-fi UI panel transition, "
               "subtle high-frequency sweep, no impact, smooth",
        duration_s=0.8,
    ),
    SfxSpec(
        name="modal_open", category="ui", out_subdir="ui",
        prompt="soft synth swell upward, gentle 200ms attack, mid-range pad, "
               "warm sci-fi panel-opening tone",
        duration_s=0.8,
    ),
    SfxSpec(
        name="modal_close", category="ui", out_subdir="ui",
        prompt="soft synth swell downward, gentle decay, mid-range pad, "
               "warm sci-fi panel-closing tone",
        duration_s=0.8,
    ),
    SfxSpec(
        name="notification", category="ui", out_subdir="ui",
        prompt="pleasant single-bell chime, gentle decay, mid-bright tone, "
               "sci-fi notification ding, not intrusive",
        duration_s=1.0,
    ),
    SfxSpec(
        name="alert_warning", category="ui", out_subdir="ui",
        prompt="amber-coded warning pulse, two-tone alternating siren, "
               "moderate urgency, sci-fi HUD alert, not panicked",
        duration_s=1.2,
    ),
    SfxSpec(
        name="alert_danger", category="ui", out_subdir="ui",
        # Round 3: Aaron — "less annoying, more fuzzy"
        prompt="fuzzy low warm red-alert pulse, slow modulated synth-wash siren with "
               "soft distorted analog edges, urgent but not piercing, sci-fi bridge "
               "warning, audible without being shrill or annoying",
        duration_s=1.5, prompt_influence=0.85, round=3,
        notes="Round-3 re-roll: less annoying, more fuzzy",
    ),
    SfxSpec(
        name="hud_acknowledge", category="ui", out_subdir="ui",
        prompt="brief computer beep, neutral tone, sci-fi acknowledgement, "
               "command-accepted chirp, very short",
        duration_s=0.5,
    ),
    # scan_lock dropped 2026-05-17 per Aaron's listen-pass: "This is no
    # good. What is scan lock anyway?" -- no clear gameplay slot in the
    # slice for a targeting reticle lock-on, so retiring it. The .wav
    # file is removed; the manifest entry's status of 'reject' stays as
    # the historical record.
]


# ---------------------------------------------------------------------------
# B. Per-ship weapon SFX (44) — under assets/sfx/ships/<ship_id>/
#
# For each of the 11 ships in src/scz/combat/ships.py we produce four
# sounds: primary FIRE, primary IMPACT, special FIRE, special IMPACT.
# The specials aren't yet implemented in code (Phase 4+) but the SFX
# are content-authoring work that can land independently.
#
# Each prompt is anchored to the species' sonic_signature in the CSV.
# Short, distinctive, lore-grounded.
# ---------------------------------------------------------------------------

def _ship(species_id: str, ship_id: str, primary_fire: str, primary_impact: str,
          special_fire: str, special_impact: str, *, round_no: int = 4) -> list[SfxSpec]:
    """Emit the 4-SFX bundle for one ship."""
    sub = f"ships/{ship_id}"
    return [
        SfxSpec(name="primary_fire",   category="weapon", out_subdir=sub,
                prompt=primary_fire, duration_s=0.6, species_id=species_id,
                round=round_no),
        SfxSpec(name="primary_impact", category="weapon", out_subdir=sub,
                prompt=primary_impact, duration_s=0.6, species_id=species_id,
                round=round_no),
        SfxSpec(name="special_fire",   category="weapon", out_subdir=sub,
                prompt=special_fire, duration_s=1.2, species_id=species_id,
                round=round_no),
        SfxSpec(name="special_impact", category="weapon", out_subdir=sub,
                prompt=special_impact, duration_s=1.0, species_id=species_id,
                round=round_no),
    ]


SHIP_SFX: list[SfxSpec] = []

# Furling Scout (player) — Warm-organic-tech: fur-cushioned gong, copper bells.
# Round 2 (2026-05-17 re-roll): Aaron called the Round-1 sample "not very
# dramatic." Bumped duration 0.6 -> 1.0, swapped in DRAMATIC + LOUD
# descriptors, raised prompt_influence to 0.85.
SHIP_SFX.extend([
    SfxSpec(name="primary_fire", category="weapon", out_subdir="ships/furling_scout",
            # Round 3: Aaron — "like warping the fabric of space, with a
            # snap-back feedback sound at the end"
            prompt="spatial-fabric warp weapon: building wobble-bend of low-frequency "
                   "space-distortion swelling outward, then a sharp SNAP-BACK feedback "
                   "tail like an elastic membrane releasing, reality-bending Furling "
                   "primary shot, audible warp-then-snap signature",
            duration_s=1.0, species_id="FURLING_SCOUT", round=3,
            prompt_influence=0.9,
            notes="Round-3 re-roll: warp-fabric + snap-back tail."),
    SfxSpec(name="primary_impact", category="weapon", out_subdir="ships/furling_scout",
            # Round 3: Aaron — "Should sound like tearing through metal"
            prompt="violent metallic tear: sharp ripping shriek of steel being torn open, "
                   "scrape-and-shred contact, brief sustained metallic groan after impact, "
                   "weighty and brutal, no soft cushioning",
            duration_s=0.8, species_id="FURLING_SCOUT", round=3,
            prompt_influence=0.9,
            notes="Round-3 re-roll: tearing through metal."),
    SfxSpec(name="special_fire", category="weapon", out_subdir="ships/furling_scout",
            # Round 3: Aaron — "the special ability is it immediately stops us where
            # we are and when we let go, we resume our previous direction and momentum"
            # (the Time Drive freeze mechanic)
            prompt="time-freeze instant stop: sharp transient snap into sudden silence-shimmer, "
                   "audio of momentum being held in place, deep low hum sustaining "
                   "the frozen moment, sense of reality paused, Furling Time Drive activation",
            duration_s=1.5, species_id="FURLING_SCOUT", round=3,
            prompt_influence=0.9,
            notes="Round-3 re-roll: time-freeze (Time Drive pause)."),
    SfxSpec(name="special_impact", category="weapon", out_subdir="ships/furling_scout",
            # Round 3: Aaron — "No special impact, but it should just be the reverse
            # of the special weapon fire sound in this case." Sample-reversal of
            # special_fire = time-unfreeze (we resume direction and momentum).
            prompt="(derived: sample-reverse of ships/furling_scout/special_fire — "
                   "produces time-unfreeze: reality un-pausing, momentum resuming)",
            duration_s=1.5, species_id="FURLING_SCOUT", round=3,
            reverse_of="ships/furling_scout/special_fire",
            notes="Round-3: derived by reversing special_fire (time-unfreeze)."),
])

# --- Round 2 ship weapons: primary_fire for 4 more ships so Aaron can
#     hear species-distinctness across the roster ---
SHIP_SFX.extend([
    SfxSpec(name="primary_fire", category="weapon", out_subdir="ships/cleanser_cruiser",
            # Round 3: Aaron — "Need this to be the same as the Furling scout,
            # but bigger and louder." Same warp-snap signature, bigger scale.
            prompt="MASSIVE spatial-fabric warp weapon: huge low-frequency space-distortion "
                   "swelling outward with extra depth and breadth, then a brutal "
                   "SNAP-BACK feedback tail like an enormous elastic membrane "
                   "releasing, bigger and louder than a Furling Scout shot, "
                   "reality-bending Cleanser cruiser primary, monolithic warp-then-snap",
            duration_s=1.3, species_id="CLEANSER_FACTION", round=3,
            prompt_influence=0.9,
            notes="Round-3 re-roll: Furling-scout shape, bigger + louder."),
    SfxSpec(name="primary_fire", category="weapon", out_subdir="ships/arilou_skiff",
            # Round 3: Aaron — "skiff was a zippy lazer sound, start high, go low tri-tone"
            prompt="zippy laser shot, sharp three-note descending pitch sweep from "
                   "high to low (tri-tone), bright electronic zap with quick decay, "
                   "Arilou skiff fast-attack weapon, audible and snappy",
            duration_s=0.7, species_id="ARILOU", round=3,
            prompt_influence=0.9,
            notes="Round-3 re-roll: zippy laser, tri-tone high-to-low."),
    SfxSpec(name="primary_fire", category="weapon", out_subdir="ships/mmrnmhrm_sentinel",
            prompt="DRAMATIC Mmrnmhrm precision beam: silent millisecond charge-up "
                   "into sharp cold cutting laser-beam discharge, surgical robotic precision, "
                   "high-frequency directed-energy with crisp transient, "
                   "alien clinical efficiency, LOUD and AUDIBLE",
            duration_s=0.8, species_id="MMRNMHRM", round=2,
            prompt_influence=0.85),
    SfxSpec(name="primary_fire", category="weapon", out_subdir="ships/androsynth_cruiser",
            prompt="DRAMATIC Androsynth jury-rigged charged-particle cannon: "
                   "loud sharp tinny retro-Atari zap front-loaded with warm analog "
                   "low-end thump, human-improvised refugee tech, crunchy gritty "
                   "satisfying weapons-fire, present and audible",
            duration_s=1.0, species_id="ANDROSYNTH", round=2,
            prompt_influence=0.85),
])

# Persuader Vessel — Diplomatic-reluctant: soft strings, almost-apologetic.
SHIP_SFX.extend(_ship(
    "PERSUADER_FACTION", "persuader_vessel",
    primary_fire="non-lethal warning shot, gentle electrostatic siren wind-up, "
                 "soft strings under, Furling diplomatic-faction reluctance",
    primary_impact="soft electrostatic disorient impact, brief shimmering buzz, "
                   "not harmful-sounding, almost-apologetic tone",
    special_fire="diplomatic-restraint field activation, warm low chord swell, "
                 "Furling negotiator-tech wind-up, persuasive resonance",
    special_impact="pacifying wash, harmonic suppression of hostility, "
                   "warm dampening of motion",
))

# Arilou Skiff — Quietly weird, quasi-space displaced: phase-shifting chimes.
SHIP_SFX.extend(_ship(
    "ARILOU", "arilou_skiff",
    primary_fire="dimensional warble, soft phase-shifting whistle, "
                 "quasi-space displacement, gentle Arilou weapon discharge",
    primary_impact="delayed dimensional reverb impact, phased echo of contact, "
                   "soft warble of displaced reality",
    special_fire="quasi-space portal wind-up, gentle time-stretched chime, "
                 "phase-cycling shimmer, Arilou special technology",
    special_impact="reality-folding hush, soft inward suction, "
                   "dimensional re-stitching whisper",
))

# Androsynth Cruiser — Human-improvised: retro-Atari-on-warm-analog.
SHIP_SFX.extend(_ship(
    "ANDROSYNTH", "androsynth_cruiser",
    primary_fire="jury-rigged charged-particle burst, sharp tinny retro zap, "
                 "Atari-era PCM blast with warm analog tail, human-improvised",
    primary_impact="crunchy improvised impact, slight metallic clatter, "
                   "retro 16-bit hit with warm analog body",
    special_fire="overcharged capacitor wind-up, ominous low hum building, "
                 "Androsynth refugee-tech jury-rig with safety margins ignored",
    special_impact="capacitor discharge, bright electrical burst, "
                   "improvised-tech crackle, slight resonant aftershock",
))

# Cleanser Cruiser (Vael-Souren) — Monolithic religious dread.
SHIP_SFX.extend(_ship(
    "CLEANSER_FACTION", "cleanser_cruiser",
    primary_fire="slow ceremonial ratchet windup ending in hangman-bell toll, "
                 "deep dread, Cleanser Furling Cruiser primary weapon",
    primary_impact="finishing-blow heavy bell toll, ceremonial execution-tone, "
                   "monolithic sustained dread",
    special_fire="cathedral-organ swell of righteous conviction, "
                 "Furling chant fragments under, Cleanser purification ritual",
    special_impact="purifying flash and sustained reverberating doom-toll, "
                   "religious certainty rendered as sound",
))

# Melnorme Trader — Bio-cargo trader: gold/silver chimes, cargo bass.
SHIP_SFX.extend(_ship(
    "MELNORME", "melnorme_trader",
    primary_fire="resonant trade-network burst, long gold-silver bell wind-up "
                 "into sharp dispersal pulse, enigmatic Melnorme weapon",
    primary_impact="soft dispersal impact, scattering metallic chimes, "
                   "reluctant cargo-protective harm",
    special_fire="bio-cargo containment field flare, deep gravelly cargo-hold "
                 "bass with bright chimes, Melnorme prefer-not-to-fight tech",
    special_impact="contained-cargo-flash impact, brief gold-silver shower, "
                   "trade-economics calculated harm",
))

# Defender Vessel — Stalwart-honest: brass-and-steel reliability.
SHIP_SFX.extend(_ship(
    "DEFENDER_FACTION", "defender_vessel",
    primary_fire="solid honest mechanical chunk, clean kinetic cannon, "
                 "Furling Defender-faction reliable weapon, no theatrics",
    primary_impact="clean steel-on-steel impact, satisfying hit, "
                   "no embellishment, stalwart military thud",
    special_fire="brass-and-steel battery wind-up, three-stage mechanical "
                 "engagement, Furling Defender heavy ordnance",
    special_impact="heavy decisive impact, lingering steel resonance, "
                   "honest finishing blow",
))

# Mmrnmhrm Sentinel — Cold-precise robot: synthetic perfection.
SHIP_SFX.extend(_ship(
    "MMRNMHRM", "mmrnmhrm_sentinel",
    primary_fire="silent click into crisp surgical beam pulse, "
                 "no warmth, perfect-frequency Mmrnmhrm robot weapon",
    primary_impact="crisp surgical hit, no aftershock, microsecond-precise "
                   "directed-energy impact",
    special_fire="cold synthetic hum building to focused-beam discharge, "
                 "robotic Mmrnmhrm Sentinel special, no organic warmth",
    special_impact="precision energy detonation, surgical clinical impact, "
                   "no roar, just clean transfer",
))

# Proto-Ur-Quan Warship — Primordial-raw: organic kinetics, animal calls.
SHIP_SFX.extend(_ship(
    "PROTO_URQUAN_LIMPETS", "proto_ur_quan",
    primary_fire="animal roar of release followed by wet organic projectile "
                 "whistle, primordial pre-sentient Ur-Quan weapon, raw",
    primary_impact="wet organic impact, splatter and dripping aftermath, "
                   "claws-and-acid hit, primal",
    special_fire="deep guttural call building to bio-acid surge, "
                 "primordial Ur-Quan war-cry into chemical attack",
    special_impact="acidic dissolution impact, hissing organic damage, "
                   "wet primal devastation",
))

# Sentry Drone 47-Theta — Industrial-robotic: Furling-built enforcer.
SHIP_SFX.extend(_ship(
    "SENTRY_DRONE_47T", "sentry_drone_47t",
    primary_fire="industrial buzzing electrical zap, clinical stun discharge, "
                 "Furling-built sentry drone weapon, no warmth",
    primary_impact="clinical disable impact, brief electrical seize-up tone, "
                   "industrial robot-zap hit",
    special_fire="multi-coil charge wind-up, sentry-drone special-protocol "
                 "activation, industrial servo whines",
    special_impact="full-body disable arc, sustained electrical clamp, "
                   "industrial-robot heavy-stun impact",
))

# Proto-Qor-Ah Marauder — Primordial-aggressive divergence: sharper, harder.
SHIP_SFX.extend(_ship(
    "PROTO_QOR_AH", "proto_qor_ah",
    primary_fire="sharp chitinous strike sound, dissonant attack-shriek, "
                 "more aggressive than its proto-Ur-Quan cousin, primordial",
    primary_impact="splintering bone-and-chitin impact, harder edge than "
                   "proto-Ur-Quan version, raw aggressive hit",
    special_fire="aggressive guttural war-cry into projectile-storm windup, "
                 "primordial Qor-Ah ferocity, dissonant",
    special_impact="overwhelming swarm impact, multiple sharp chitin strikes, "
                   "primordial annihilation",
))


# ---------------------------------------------------------------------------
# C. Lander resource-gathering minigame (11) — under assets/sfx/lander/
# ---------------------------------------------------------------------------

LANDER_SFX: list[SfxSpec] = [
    SfxSpec(
        name="lander_deploy", category="lander", out_subdir="lander",
        # Round 3 re-roll: Aaron flagged for re-roll without specific notes;
        # bumping toward more mechanical specificity (real thruster ignition,
        # not a generic swell).
        prompt="lander thrusters igniting: sharp initial click of solenoid release, "
               "then building roar of bipropellant thrusters with crackling rocket "
               "exhaust, audible mechanical character, sci-fi but grounded",
        duration_s=1.6, round=3, prompt_influence=0.9,
        notes="Round-3 re-roll: more mechanical thruster character.",
    ),
    SfxSpec(
        name="atmospheric_entry", category="lander", out_subdir="lander",
        prompt="atmospheric reentry roar, sustained turbulence rumble, "
               "wind-buffeted lander hull, loopable",
        duration_s=3.0, loop=True,
    ),
    SfxSpec(
        name="lander_touchdown", category="lander", out_subdir="lander",
        # Round 3 re-roll.
        prompt="lander touchdown: three loud weighty thumps as landing legs "
               "make contact with rocky planet surface in rapid succession, "
               "soft pneumatic hiss of suspension absorbing impact, brief "
               "settling creak, satisfying mechanical contact",
        duration_s=1.4, round=3, prompt_influence=0.9,
        notes="Round-3 re-roll: more weight + specific 3-thump landing.",
    ),
    SfxSpec(
        name="engine_idle", category="lander", out_subdir="lander",
        prompt="Furling lander engine idle hum, warm low-mid drone with "
               "subtle harmonics, loopable, surface-deployed",
        duration_s=2.5, loop=True,
    ),
    SfxSpec(
        name="scan_ping", category="lander", out_subdir="lander",
        prompt="lander surface scanner ping, single rising sonar chirp, "
               "brief sci-fi detection sweep, satisfying",
        duration_s=0.8,
    ),
    SfxSpec(
        name="resource_chime_mineral", category="lander", out_subdir="lander",
        prompt="metallic crystalline chime, bright mineral-discovery tone, "
               "Furling scanner positive-reading idiom",
        duration_s=0.8,
    ),
    SfxSpec(
        name="resource_chime_bio", category="lander", out_subdir="lander",
        prompt="organic warm chime, soft fluttering bio-life-detected tone, "
               "Furling scanner biological-reading idiom",
        duration_s=0.8,
    ),
    SfxSpec(
        name="pickup_clink", category="lander", out_subdir="lander",
        # Round 3 re-roll.
        prompt="classic retro space-game pickup chime: bright two-note ascending "
               "ding-dong, satisfying coin-into-coffer feedback, short and "
               "rewarding, audible UI confirmation",
        duration_s=0.5, round=3, prompt_influence=0.9,
        notes="Round-3 re-roll: more clearly a 'pickup' chime (2-note up).",
    ),
    SfxSpec(
        name="hazard_warning", category="lander", out_subdir="lander",
        prompt="proximity-hazard warble, low-mid two-tone alarm, "
               "Furling lander HUD danger-near alert, urgent but not panicked",
        duration_s=1.2,
    ),
    SfxSpec(
        name="damage_taken", category="lander", out_subdir="lander",
        prompt="lander hull damage thump, brief metallic strain creak, "
               "structural-warning aftertone, Furling lander hit",
        duration_s=1.0,
    ),
    SfxSpec(
        name="lift_off", category="lander", out_subdir="lander",
        prompt="lander lift-off thrusters, building roar of takeoff, "
               "Furling warm-tech engine surge, departing the surface",
        duration_s=2.5,
    ),
]


# ---------------------------------------------------------------------------
# D. Planet scanning sequence (7) — under assets/sfx/scan/
# ---------------------------------------------------------------------------

SCAN_SFX: list[SfxSpec] = [
    SfxSpec(
        name="enter_orbit", category="scan", out_subdir="scan",
        prompt="orbital insertion success tone, brief Furling-tech "
               "stabilization chime followed by smooth orbital hum",
        duration_s=1.5,
    ),
    SfxSpec(
        name="scan_begin", category="scan", out_subdir="scan",
        # Round 3 re-roll (rejected in R2; treating as re-roll with bumped
        # specificity since no specific note was attached).
        prompt="planet scanner activating: short pre-spin click of switches, "
               "then quick rising mechanical hum into the steady operating "
               "tone, sci-fi instrument coming online, audible engagement",
        duration_s=1.2, round=3, prompt_influence=0.9,
        notes="Round-3 re-roll: more mechanical activation character.",
    ),
    SfxSpec(
        name="scan_complete", category="scan", out_subdir="scan",
        # Round 3 re-roll.
        prompt="scan-complete chime: bright three-note ascending arpeggio "
               "ending on a sustained satisfying high note, retro space-game "
               "task-done positive feedback, audible and rewarding",
        duration_s=1.2, round=3, prompt_influence=0.9,
        notes="Round-3 re-roll: shorter, more chime-like, less ambient.",
    ),
    SfxSpec(
        name="scan_sweep", category="scan", out_subdir="scan",
        prompt="LOUD continuous orbital scan sweep loop, slow rotating sonar "
               "pulse with crisp ping-and-decay cycle, Furling scanner "
               "steady-state operation, AUDIBLE and present, loopable",
        duration_s=3.0, loop=True, round=2, prompt_influence=0.85,
        notes="Round-2 re-roll of Round-1 sample.",
    ),
    SfxSpec(
        name="scan_progress_tick", category="scan", out_subdir="scan",
        prompt="single soft scan-progress tick, brief crystalline detection "
               "blip, percentage-complete advance",
        duration_s=0.5,
    ),
    SfxSpec(
        name="scan_complete", category="scan", out_subdir="scan",
        prompt="planet scan complete fanfare, three-note ascending Furling "
               "completion chime, summary-ready positive tone",
        duration_s=1.5,
    ),
    SfxSpec(
        name="cloak_engage", category="scan", out_subdir="scan",
        prompt="Furling cloak field engaging, descending phase-shift whoosh "
               "into hushed sustained safe-tone, in-orbit invisibility",
        duration_s=1.5,
    ),
    SfxSpec(
        name="cloak_disengage", category="scan", out_subdir="scan",
        prompt="Furling cloak field disengaging, ascending phase-shift "
               "whoosh into bright reveal-tone, vulnerability restored",
        duration_s=1.5,
    ),
]


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

ALL_SFX: list[SfxSpec] = (
    UI_SFX + SHIP_SFX + LANDER_SFX + SCAN_SFX
)


def get(name: str, out_subdir: str = "") -> SfxSpec:
    """Look up a spec by name (and optional subdir-disambiguator).

    Names are not globally unique because per-ship sfx all share the
    same stem names (primary_fire, primary_impact, special_fire,
    special_impact); pass out_subdir to disambiguate."""
    matches = [s for s in ALL_SFX if s.name == name]
    if out_subdir:
        matches = [s for s in matches if s.out_subdir == out_subdir]
    if not matches:
        raise KeyError(f"no SFX spec for {name!r} (subdir={out_subdir!r})")
    if len(matches) > 1:
        raise KeyError(
            f"{name!r} is ambiguous; provide out_subdir from: "
            f"{[m.out_subdir for m in matches]}"
        )
    return matches[0]


def for_round(round_num: int) -> list[SfxSpec]:
    """Return all specs in a given round."""
    return [s for s in ALL_SFX if s.round == round_num]


def by_category(category: str) -> list[SfxSpec]:
    return [s for s in ALL_SFX if s.category == category]
