"""Test harness — script-driven playthroughs with optional speed multiplier.

Per Aaron's design (inspired by Factorio's test methodology):
- A *script* is a sequence of timed actions: press buttons, hold axes, wait,
  set speed, assert current scene, etc.
- The *harness* feeds the script into the running game by overlaying
  scripted input on top of the normal InputManager fields each frame.
- Game speed is a multiplier on dt — at speed=3.0, the game advances 3x
  faster while still rendering at the normal frame rate, so Aaron can
  watch the playback in real time at an accelerated pace.
- The game window stays interactive; real input still flows, so you can
  take over a running test by pressing buttons yourself.

Use:
    scz --test walk_tutorial_path     # built-in script
"""
