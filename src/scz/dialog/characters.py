"""Character data: state graphs for each NPC the player talks to.

For Phase 2 + 3 we hand-author the FSM and canned text. When the LLM
renderer lands (Phase 3.5), the npc_text strings become the "intent" passed
to the LLM and the LLM produces the actual phrasing from a per-character
voice prompt. The FSM and choice categories stay deterministic.
"""

from __future__ import annotations

from scz.dialog.data import DialogChoice, DialogCharacter, DialogState, build_state_dict


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
