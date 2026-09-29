"""Dialog FSM exhaustive coverage audit.

Walks every DialogCharacter factory's FSM via graph traversal from the
`initial_state`. Reports:

- **Total states defined** vs **reachable from initial**
- **Orphan states** — defined but unreachable from initial
- **Dead-end states** — has no choices AND not marked `is_terminal`
  (these are *trap* states the player can't exit)
- **Broken transitions** — choice.next_state_id points to a state that
  doesn't exist in the FSM
- **Choices with side-effects** — listed for sanity-checking which
  flag-mutations the dialog can trigger

Auto-discovers DialogCharacter factories by introspecting
`scz.dialog.characters`. Any module-level callable with a default-arg-
free signature OR an optional `game` arg, that returns a
DialogCharacter, is treated as a factory.

Exit code: 0 if all dialogs clean, 1 if any FSM issue found.
"""

from __future__ import annotations

import inspect
import sys
from collections import deque
from pathlib import Path


_SCRIPT_DIR = Path(__file__).resolve().parent
_SRC_DIR = _SCRIPT_DIR.parent / "src"
sys.path.insert(0, str(_SRC_DIR))


def _discover_factories() -> list[tuple[str, callable]]:
    """Find every DialogCharacter-returning function in
    scz.dialog.characters. Returns (name, callable) pairs.
    """
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    import pygame
    pygame.init()
    pygame.display.set_mode((1280, 720))

    from scz.dialog import characters as ch
    from scz.dialog.data import DialogCharacter

    factories: list[tuple[str, callable]] = []
    for name in sorted(dir(ch)):
        if name.startswith("_"):
            continue
        obj = getattr(ch, name)
        if not callable(obj):
            continue
        # Heuristic: real factories accept either zero args or an
        # optional `game` arg, and return DialogCharacter. We skip
        # the internal `_stub_crew_dialog` helper (starts with
        # underscore) and constants.
        try:
            sig = inspect.signature(obj)
        except (ValueError, TypeError):
            continue
        params = list(sig.parameters.values())
        if any(
            p.default is inspect.Parameter.empty
            and p.kind != inspect.Parameter.VAR_KEYWORD
            and p.kind != inspect.Parameter.VAR_POSITIONAL
            for p in params
        ):
            # Has a required positional arg — likely not a zero-arg
            # factory.
            continue
        # Try invoking; if it returns DialogCharacter, keep it.
        try:
            char = obj() if not params else obj(None)
        except (TypeError, RuntimeError, AttributeError):
            continue
        if isinstance(char, DialogCharacter):
            factories.append((name, obj))
    return factories


def audit_dialog(name: str, factory: callable) -> dict:
    """Run the audit on one character factory. Returns a result dict."""
    from scz.dialog.data import DialogCharacter
    # Build the character; pass None for game-aware factories
    try:
        sig = inspect.signature(factory)
        if sig.parameters:
            char: DialogCharacter = factory(None)
        else:
            char = factory()
    except Exception as e:
        return {
            "name": name,
            "ok": False,
            "error": f"factory raised: {e!r}",
        }
    states = char.states
    state_ids = set(states.keys())
    initial = char.initial_state

    if initial not in state_ids:
        return {
            "name": name,
            "ok": False,
            "error": (
                f"initial_state={initial!r} is not in states dict"
            ),
        }

    # BFS reachable from initial
    reachable: set[str] = set()
    side_effects: list[tuple[str, str]] = []     # (state, choice_text)
    broken: list[tuple[str, str, str]] = []      # (state, choice_text, missing_target)
    dead_ends: list[str] = []
    queue = deque([initial])
    while queue:
        sid = queue.popleft()
        if sid in reachable:
            continue
        reachable.add(sid)
        state = states.get(sid)
        if state is None:
            continue
        # No choices and not flagged terminal = dead-end trap
        if not state.choices and not getattr(state, "is_terminal", False):
            dead_ends.append(sid)
        for choice in state.choices:
            if choice.side_effect is not None:
                side_effects.append((sid, choice.text))
            next_id = choice.next_state_id
            if next_id is None:
                continue   # terminal — closes the dialog
            if next_id not in state_ids:
                broken.append((sid, choice.text, next_id))
                continue
            if next_id not in reachable:
                queue.append(next_id)

    orphans = sorted(state_ids - reachable)
    return {
        "name": name,
        "ok": (not broken) and (not dead_ends),
        "total_states": len(state_ids),
        "reachable_states": len(reachable),
        "orphans": orphans,
        "dead_ends": dead_ends,
        "broken_transitions": broken,
        "side_effects": side_effects,
    }


def main() -> int:
    factories = _discover_factories()
    if not factories:
        print("[dialog-coverage] no DialogCharacter factories discovered.",
              file=sys.stderr)
        return 2

    print(f"[dialog-coverage] auditing {len(factories)} factories ...\n")
    failures = 0
    warnings = 0
    for name, fn in factories:
        result = audit_dialog(name, fn)
        if not result.get("ok"):
            failures += 1
        if "error" in result:
            print(f"  [ERR ] {name:38s}  {result['error']}")
            continue
        # Compose a single line
        n_states = result["total_states"]
        n_reach = result["reachable_states"]
        orphan_n = len(result["orphans"])
        dead_n = len(result["dead_ends"])
        broken_n = len(result["broken_transitions"])
        if broken_n > 0 or dead_n > 0:
            badge = "FAIL"
        elif orphan_n > 0:
            badge = "WARN"
            warnings += 1
        else:
            badge = "OK  "
        print(
            f"  [{badge}] {name:38s}  "
            f"{n_reach}/{n_states} reachable  "
            f"orphans={orphan_n}  "
            f"dead-ends={dead_n}  "
            f"broken={broken_n}"
        )
        if dead_n > 0:
            for sid in result["dead_ends"]:
                print(f"          dead-end: {sid}")
        if broken_n > 0:
            for sid, text, target in result["broken_transitions"]:
                print(
                    f"          broken: {sid} -> "
                    f"{target!r} (via {text[:40]!r})"
                )
        if orphan_n > 0:
            sample = result["orphans"][:5]
            more = "" if orphan_n <= 5 else f"  (+{orphan_n - 5} more)"
            print(f"          orphans: {', '.join(sample)}{more}")

    print()
    print("=" * 62)
    print(
        f"[dialog-coverage] {len(factories)} factories audited  ·  "
        f"{failures} failed  ·  {warnings} with orphans"
    )
    print("=" * 62)
    return 1 if failures > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
