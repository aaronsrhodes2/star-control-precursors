# Lore Notes — Star Control Zero: The Precursors

Distilled from primary sources. The canonical worldbuilding for our fan-game is in [`precursor-worldbuilding.md`](precursor-worldbuilding.md); this file captures supplementary facts and design implications.

## Sources

- **Aaron's worldbuilding doc** ([Google Doc](https://docs.google.com/document/d/1qUAz9he-oLuHMwJ4JIwd_WYQSkxi46SvSUaOkuoAhcI/edit), exported to `precursor-worldbuilding.md`) — **canonical for this project**
- **The Ur-Quan Masters source** — cloned to [`../uqm-source/`](../uqm-source/) for dialog/combat reference
- **Star Control 2 starmap** — [`../maps/sc2-starmap.png`](../maps/sc2-starmap.png) (the iconic full-galaxy map)
- **QuasiSpace map** — [`../maps/quasispace.png`](../maps/quasispace.png) (Arilou-side portal map)
- **Wikipedia + Fandom search hits** (saved query results below) — block WebFetch but reachable in a browser

## Canon Facts We Anchor To

### The Precursors
- Vanished ~250,000 years before SC2.
- "Shaggy Giants" — 5-8m tall, non-bipedal, woolly-mammoth-like (Slylandro testimony).
- The Great Departure was deliberate, organized, not a collapse.
- Fled into **Quasi-Space** to escape **"Them"** — trans-dimensional predators they accidentally summoned by tunneling.
- Left behind: the **Sa-Matra**, the **Rainbow Worlds** (arrow pointing to Galactic Core), the **Mycon biots**, factory worlds (e.g., Unzervalt/Vela).

### The Sentient Milieu (pre-Departure era)
- The Sentient Milieu was a multi-species alliance of the era. Four founding races, including the **Mael-Num** (one-eyed creatures).
- Important: the Milieu existed *before* the Ur-Quan rose, then *fell* when the Kohr-Ah and Kzer-Za split. Our game is set in the Precursor era — the Milieu is contemporary background. We can name some races in passing.

### Connection Map
| SC2-era entity | Origin in Precursor era |
|---|---|
| Mycon | Precursor terraforming biots, still obedient |
| Sa-Matra | Precursor weapon, being built/finalized |
| Rainbow Worlds | Precursor markers being placed |
| Arilou Lalee'lay | Cousin race, already partway into Quasi-Space |
| Ur-Quan | Pre-sentient limpet creatures being shepherded |
| VUX | "In their infancy" per worldbuilding doc |
| Orz | "Cleaners" / byproduct of Precursor dimensional tunneling |
| The Dnyarri | (Future Mind-Controllers) — not yet relevant in slice |

## The UQM Dialog Pattern — What We Mirror

After studying `sc2/src/uqm/comm/comandr/`:

**Structure per species:**
- `<species>.c` — state functions
- `strings.h` — enums of NPC phrase IDs and player phrase IDs (lowercase convention)
- `resinst.h` — resource IDs (graphics, music)

**State function shape (from `comandr.c::ByeBye`):**
```c
static void ByeBye (RESPONSE_REF R) {
    if (PLAYER_SAID (R, ok_i_will_get_radios))
        NPCPhrase (THANKS_FOR_HELPING);
    else if (PLAYER_SAID (R, some_other_choice))
        NPCPhrase (OTHER_RESPONSE);

    Response (next_player_choice_1, NextState);
    Response (next_player_choice_2, NextState);

    SET_GAME_STATE (WILL_DESTROY_BASE, 1);
}
```

**The pattern:**
1. `PLAYER_SAID(R, id)` — dispatch on the player's chosen phrase
2. `NPCPhrase(ID)` — emit NPC dialog (looked up in strings table)
3. `Response(id, fn)` — register the next available player choices and their successor state function
4. `SET_GAME_STATE(FLAG, value)` — mutate global game state (deterministic side effect)

**Our LLM-augmented version (the two-layer architecture):**
- Keep the FSM exactly. Each state function maps cleanly to a Python function or a YAML entry.
- Replace `NPCPhrase(THANKS_FOR_HELPING)` with `npc_phrase("THANKS_FOR_HELPING", semantic_content="Express gratitude and explain you'll alert the base")` — the *intent* is hard-coded, the *words* are LLM-rendered.
- Replace `Response(ok_i_will_get_radios, ByeBye)` with `response(category="AGREE_HELP", next_state=bye_bye, semantic_content="Agree to retrieve the radioactives")` — the *category* + *intent* are hard-coded, the *surface phrasing* is LLM-rendered each time.
- `SET_GAME_STATE(...)` stays exactly the same — deterministic.

**Why this is safe:**
- Game logic never parses LLM output. The state machine sees only categories.
- LLM failures fall back to canned text per (state, intent).
- Save files store FSM state, not chat history — re-renders are okay.

## Slice Design Implications

- We need **4 species profiles** with: voice/language description, lore facts, disposition variables, FSM definition, fallback text table.
- The Slylandro voice (run-on awed sentences) and Mycon voice (fragmented ritual phrases) come from canon — start there for the prompt examples.
- Each species' first-meeting state, ~6-8 follow-up states, and one combat-trigger state should be enough for the slice.
- Reuse the UQM convention of UPPERCASE for NPC phrase IDs and lowercase for player phrase IDs in our YAML — keeps things readable when comparing to the source.

## What We Skipped (Recoverable Later)

- The [Precursor wiki page](https://wiki.starcontrol.com/index.php/Precursor) — site blocks programmatic fetches (403). Aaron can browser-save the HTML and drop it in this directory if/when needed; everything important is captured above.
- The full GameFAQs walkthrough — also blocked. Not critical since we're not replicating SC2's plot.
- MobyGames screenshots — visual reference only; UQM `references/uqm-source/sc2/content/` may contain the actual sprites once we pull the content package.
