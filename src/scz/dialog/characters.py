"""Character data: state graphs for each NPC the player talks to.

For Phase 2 + 3 we hand-author the FSM and canned text. When the LLM
renderer lands (Phase 3.5), the npc_text strings become the "intent" passed
to the LLM and the LLM produces the actual phrasing from a per-character
voice prompt. The FSM and choice categories stay deterministic.
"""

from __future__ import annotations

from typing import Any

from scz.dialog.data import DialogChoice, DialogCharacter, DialogState, build_state_dict


# ---------------------------------------------------------------------------
# Side effect helpers — used by DialogChoice.side_effect.
# ---------------------------------------------------------------------------

def _grant_quasispace_portal(game: Any) -> None:
    """The Sage's gift: a portal spawner + portal map. Sets the flag the
    HyperspaceScene reads to enable the Y-button portal opener.
    """
    game.flags["has_quasispace_portal"] = True


def _grant_distress_beacon(game: Any) -> None:
    """Coel Tessar's gift — the Distress Beacon recording, irrefutable
    proof of the Others' decursion attack on the Androsynth timeline."""
    game.flags["has_distress_beacon"] = True
    game.flags["met_androsynth"] = True
    game.flags["androsynth_aboard"] = True


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
    proper opens."""
    game.flags["heard_others_confirmed"] = True
    game.flags["tutorial_complete"] = True


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
        portrait_color=(220, 180, 100),  # Persuader amber
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
        portrait_color=(140, 240, 210),  # teal/mint Arilou
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
    """Build a side-effect that buys a tech module (drops into
    game.uninstalled_modules). Returns purchase_complete or
    insufficient_organics by overriding the choice's next_state_id."""
    item = next(i for i in MELNORME_TECH_ITEMS if i["id"] == item_id)

    def _do(game: Any) -> str | None:
        bio = game.cargo.get("BIO", 0)
        cost = item["bio_cost"]
        if bio < cost:
            return "insufficient_organics"
        game.cargo["BIO"] = bio - cost
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
        portrait_image_path="assets/comm/melnorme/melnorme-000.png",
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
                        "We will speak another time.",
                        next_state_id=None,
                        category="FAREWELL",
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
