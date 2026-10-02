# Star Control Zero: The Precursors

A fan-game prequel to *Star Control II: The Ur-Quan Masters*, set 250,000 years before the events of SC2 — in the final centuries of the Precursor civilization, before their Great Migration into Quasi-Space.

## The Premise

You are a young Precursor Steward — a "Shaggy One" — assigned to a frontier star cluster. You fly a modular Precursor scout, explore worlds, meet pre-sentient and infant-sentient species, gather biological and mineral data, fight rogue creatures and Them-rift incursions in 1v1 melee combat, and make decisions that will ripple forward to shape the SC2 universe.

## Why This Game Exists

Two reasons:

1. **The story of the Precursors is the great mystery of SC2** — hinted at across every alien encounter but never directly told. This game tells that story from the inside.
2. **A specific, well-justified use of an LLM**: each alien species' dialog is rendered dynamically by an LLM over a fixed state machine. The game logic (choices: fight, flee, talk, gift) stays deterministic and authored; the words each species speaks vary by their lore, voice, mood, and history with the player. This eliminates the repetition that made SC2 dialog tedious on replays without giving up authorial control of the story.

## Status

Phase 2 (Engine MVP) in progress. The hyperspace scene works: the precursor-era starmap renders, the player ship can fly around it with controller or keyboard, and the HUD shows the nearest star with its lore tag.

## Running

Requires Python 3.12+. From the project root (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -e .
.venv\Scripts\python.exe -m scz
```

### Controls

Keyboard and controller are both live at all times.

| | Keyboard | Controller |
|---|---|---|
| Fly / move through menus | WASD or arrow keys | Left stick / D-pad |
| Select, autopilot | Space or Enter | A |
| Back, pause | Esc or Backspace | B |
| Zoom the star map | - and = (or [ and ]) | LB / RB |
| Time Drive (rewind) | R | Back / View |
| Fire, special | F, Shift | X or RT, Y or RB |

### Playing in a browser

The game also runs in a browser, compiled to WebAssembly with [pygbag](https://pygame-web.github.io/):

```bash
pip install pygbag pillow            # plus ffmpeg on PATH, and `git lfs pull` for the assets
python tools/build_web.py --serve    # builds build/web-dist/ and serves it
```

Then open <http://127.0.0.1:8000/> (not `localhost`: on `localhost:8000` the runtime looks for a
local copy of its support files and fails to start). `build/web-dist/` is plain static files and
can be hosted anywhere; `python tools/build_web.py --tarball` also writes `build/scz-web.tar.gz`,
the archive published as a GitHub Release and bundled into the Skippy Portal at `/starcontrol/`.

What differs from the desktop game:

- **Keyboard or controller only.** On a phone or tablet the page waits for a controller before it
  downloads anything.
- **Music is streamed**, one track at a time, instead of loaded from disk.
- **Saves stay in that browser** (its local storage). They survive reloads and new builds but do
  not follow you to another device.
- It runs on Python 3.12 (what the browser runtime ships), so the code must stay 3.12-compatible.

`?test=walk_trade` (or a comma-separated list, or `all`) on the page runs the scripted test walks
inside the browser build; results land in `window.sczTestResults` of the game frame.

### Tests

```bash
python -m scz --windowed --test walk_tutorial_path   # one scripted walk (65 of them; see src/scz/testing/scripts.py)
python tests/test_web_build.py                       # the browser build's own pieces (no browser needed)
```

## Status by Phase

- ✅ **Phase 0** — project skeleton, references, lore docs
- ✅ **Phase 0.5** — SC2 universe extracted to JSON, precursor-era derived
- 🚧 **Phase 2** — engine MVP
  - ✅ Hyperspace scene with starmap, player ship, controller/keyboard input
  - ⏸ Star system view
  - ⏸ Planet surface
  - ⏸ Melee combat
  - ⏸ Save/load
- ⏸ **Phase 3** — LLM dialog layer
- ⏸ **Phase 3.5** — variation layer (per-individual portraits, music stems, combat personality, banter)
- ⏸ **Phase 4** — vertical slice content (4 species, the Cleanser climax, Rainbow World seeding)

## Project Layout

- `src/scz/` — game source (Python + pygame-ce, provisional)
- `references/` — research material (UQM source mirror, lore, maps) — not shipped
- `assets/` — sprites, sounds, music
- `saves/` — local save files (gitignored)
- `tests/` — unit tests

## Lineage & Credits

This is a non-commercial fan project. The original *Star Control II* was created by Toys for Bob (Paul Reiche III & Fred Ford). The open-source release is *The Ur-Quan Masters* — see `references/uqm-source/` for the C source we study (not fork).
