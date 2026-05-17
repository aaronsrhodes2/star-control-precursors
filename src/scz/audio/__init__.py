"""Runtime audio system for Star Control Zero.

Per references/lore/music-system.md:
- Music is composed at build time as 4-6 stems per context.
- The game mixes stems at runtime with variation knobs:
  tempo jitter, stem mute, key transposition, lead instrument swap,
  section reorder, density modulation, state-driven layers.
- pygame.mixer.Channel is the backbone (8 simultaneous channels;
  plenty for 6-stem tracks).

This package contains:
- mixer.py: thin pygame.mixer wrapper for stem playback
- director.py: scene-context → track selection + variation knobs
- state_layers.py: disposition → per-stem volume mapping

Build-time generation lives in tools/audio_*.py and the audio-server
(port 5006). This package is pure runtime.
"""

from __future__ import annotations
