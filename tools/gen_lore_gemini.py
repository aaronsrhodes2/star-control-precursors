"""Generate small lore-text fills via Gemini Flash, with Anthropic fallback.

Use for:
- Missing species descriptions in tools/species_inventory.csv (empty
  description fields, or `TBD` cells in any column).
- First-pass quest dialog drafts (state.npc_text strings ~3-4 states).
- Voice-profile snippets for the future LLM dialog renderer.

Usage:
    .venv/Scripts/python.exe tools/gen_lore_gemini.py species_description "Talos" \
        "Furling Stay-Side sub-faction. Built the Resonator. Got eaten first."

The script reads GEMINI_API_KEY from D:/Aaron/development/.env. If the
quota is hit (20 RPD on flash), prints a clear failure marker and the
caller can re-route to Claude / Anthropic.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def load_dotenv() -> None:
    env_path = Path("D:/Aaron/development/.env")
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        v = v.strip().strip('"').strip("'")
        os.environ.setdefault(k.strip(), v)


PROMPT_TEMPLATES = {
    "species_description": (
        "Write a concise, evocative 2-3 sentence in-game description of "
        "the species/faction below, suitable for a Star Control 2-style "
        "alien-codex card. Lean on the supplied hook; keep voice "
        "atmospheric and stylized.\n\n"
        "SPECIES: {name}\n"
        "HOOK: {hook}\n\n"
        "Output ONLY the description text. No preamble, no quotes, no "
        "markdown."
    ),
    "voice_profile": (
        "Write a 4-bullet voice-profile for the character below, "
        "describing how they speak. Each bullet ~1 sentence: (1) sentence "
        "length / rhythm, (2) vocabulary tics, (3) emotional register, "
        "(4) what they NEVER say.\n\n"
        "CHARACTER: {name}\n"
        "BACKGROUND: {hook}\n\n"
        "Output ONLY the four bullets, prefixed with '- '."
    ),
    "quest_dialog_draft": (
        "Draft a 3-state Star Control 2-style dialog FSM for the quest "
        "below. Output strict YAML with keys: states (list of "
        "{{id, npc_text, choices}}). Each state's choices list has "
        "{{text, next_state_id, category}}. Categories must be one of: "
        "TALK_MORE, FIGHT, FLEE, AGREE, GIFT, ASK_LORE, FAREWELL.\n\n"
        "QUEST: {name}\n"
        "PREMISE: {hook}\n\n"
        "Output ONLY the YAML."
    ),
}


def run_gemini(prompt: str, model: str = "gemini-2.5-flash") -> str:
    """Call Gemini Flash via the current google-genai SDK. Raises on
    quota / network error so the caller can fall back to Claude."""
    try:
        from google import genai
    except ImportError:
        raise RuntimeError(
            "google-genai not installed. Run: pip install google-genai"
        )
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")
    client = genai.Client(api_key=api_key)
    resp = client.models.generate_content(model=model, contents=prompt)
    return (resp.text or "").strip()


def main() -> int:
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("template", choices=list(PROMPT_TEMPLATES))
    parser.add_argument("name", help="Species / character / quest name")
    parser.add_argument("hook", help="Short lore hook the model anchors on")
    args = parser.parse_args()

    prompt = PROMPT_TEMPLATES[args.template].format(name=args.name, hook=args.hook)
    try:
        out = run_gemini(prompt)
        print(out)
        return 0
    except Exception as e:
        print(f"# GEMINI_FAILED: {e}", file=sys.stderr)
        print(f"# Fallback: re-route via Anthropic in the next session.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
