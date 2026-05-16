# Star Control Zero: The Precursors

A fan-game prequel to *Star Control II: The Ur-Quan Masters*, set 250,000 years before the events of SC2 — in the final centuries of the Precursor civilization, before their Great Migration into Quasi-Space.

## The Premise

You are a young Precursor Steward — a "Shaggy One" — assigned to a frontier star cluster. You fly a modular Precursor scout, explore worlds, meet pre-sentient and infant-sentient species, gather biological and mineral data, fight rogue creatures and Them-rift incursions in 1v1 melee combat, and make decisions that will ripple forward to shape the SC2 universe.

## Why This Game Exists

Two reasons:

1. **The story of the Precursors is the great mystery of SC2** — hinted at across every alien encounter but never directly told. This game tells that story from the inside.
2. **A specific, well-justified use of an LLM**: each alien species' dialog is rendered dynamically by an LLM over a fixed state machine. The game logic (choices: fight, flee, talk, gift) stays deterministic and authored; the words each species speaks vary by their lore, voice, mood, and history with the player. This eliminates the repetition that made SC2 dialog tedious on replays without giving up authorial control of the story.

## Status

Early development. See [the design plan](../../Users/aaron/.claude/plans/i-want-to-make-indexed-summit.md) for the full vertical slice scope and roadmap.

## Project Layout

- `src/scz/` — game source (Python + pygame-ce, provisional)
- `references/` — research material (UQM source mirror, lore, maps) — not shipped
- `assets/` — sprites, sounds, music
- `saves/` — local save files (gitignored)
- `tests/` — unit tests

## Lineage & Credits

This is a non-commercial fan project. The original *Star Control II* was created by Toys for Bob (Paul Reiche III & Fred Ford). The open-source release is *The Ur-Quan Masters* — see `references/uqm-source/` for the C source we study (not fork).
