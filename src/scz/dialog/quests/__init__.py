"""Quests — each file owns one self-contained dialog arc.

A "quest" here is one player-NPC interaction that has a beginning,
middle, and end (terminal status). The migration target is to move
each cluster of dialog states out of the monolithic dialog/characters.py
into per-quest modules so:

1. Each quest is playtestable in isolation via its own walk_<quest>
   test script (no need to walk the whole tutorial to reach a late
   beat).
2. The LLM dialog renderer (Phase 3.5) gets a clean per-quest scope
   for voice-prompt construction and recent-history accumulation —
   it doesn't see other quests' state.
3. Adding a new quest is a NEW FILE rather than touching the giant
   characters.py.

## Structure per quest file

    src/scz/dialog/quests/<slug>.py

    from scz.dialog.data import DialogCharacter, DialogState, DialogChoice
    from scz.dialog.articulation import <RIG>
    from scz.dialog.characters import <bg constant>

    def build_character(game) -> DialogCharacter:
        '''The DialogCharacter factory for this quest. game param lets
        the factory branch on flags (e.g. "if player already met them,
        skip the introduction state").'''
        return DialogCharacter(...)

    # Optional: side-effect callbacks
    def _grant_quest_reward(game) -> None: ...

    # Optional: a walk-test recipe registered with the test harness
    def walk(script): ...

## Walk-test integration

Each quest exports a `walk(script)` function that scripts a complete
interaction (open dialog → traverse all important branches →
verify terminal status). The test harness's scripts.py registers
these as `walk_<quest_slug>` so Aaron can run:

    .venv/Scripts/python.exe -m scz --test walk_arilou_sage_gift

…and exercise just that one dialog without running the whole tutorial.

## Migration plan

Today: existing dialog factories live in dialog/characters.py and are
re-exported there for backward compat. As each character is
playtested or rewritten with LLM voice, lift it into a per-quest
file and update characters.py to re-export from the new module.

Tutorial Pickup           → quests/tutorial_pickup.py        (Halia Beat 1)
Distress Beacon           → quests/distress_beacon.py        (Coel Tessar)
Others Revelation         → quests/others_revelation.py      (Halia Beat 5+7)
Arilou Sage Gift          → quests/arilou_sage_gift.py
Slylandro Witness         → quests/slylandro_witness.py      (Cloak install)
Sentry Drone Combat       → quests/sentry_drone_combat.py
Melnorme Trade            → quests/melnorme_trade.py

When the LLM-rendering layer lands the per-quest file is where the
voice profile + dialog-state-as-intent strings live. The fallback
canned text stays alongside as the "LLM unavailable" path.
"""

from __future__ import annotations
