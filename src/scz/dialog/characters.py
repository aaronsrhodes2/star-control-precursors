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


# ---------------------------------------------------------------------------
# Commander Halia — Furling Persuader, runs Mh-Lai Station
# ---------------------------------------------------------------------------
# She's the player's home-base contact. Voice: warm, authoritative, slightly
# weary. Persuader-aligned: prefers diplomacy, takes the player seriously
# but doesn't catastrophize.

def commander_halia() -> DialogCharacter:
    """Tutorial-beat-1 commander. Mentions the Androsynth refugees and the
    Furlmart package errand. Returns to a top-level 'anything else?' loop.
    """
    return DialogCharacter(
        name="Commander Halia",
        title="Persuader, Mh-Lai Station",
        species_id="FURLING_PERSUADER",
        portrait_color=(220, 180, 100),  # Persuader amber
        initial_state="start",
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
