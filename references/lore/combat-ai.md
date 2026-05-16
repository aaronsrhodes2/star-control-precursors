# Combat AI — Three-Layer Architecture

> Applies the [variation-as-a-layer architecture](variation-architecture.md) to combat AI. Same pattern: a deterministic engine layer, a personality variation layer, and a banter (LLM) layer — each independent, each disablable, each cumulative in atmosphere.

## The SC2 Problem

In SC2 melee, every Ur-Quan Dreadnought played by the AI fought identically. Every Spathi Eluder ran the same way. Every Mycon Podship homed in with the same trigger conditions. Once you learned a ship's AI, you owned that matchup forever — and the AI never adapted, never surprised you, never *felt* like a different captain at the helm.

Looking at the UQM source: each ship has a `<species>_intelligence` function (e.g., `human_intelligence` in `ships/human/human.c:307`) that checks distance thresholds and sets input bits like SPECIAL or WEAPON. It's good 90s AI — clean, balanced, fast — and it's deterministic to a fault. Same input → same action, every time.

We can fix this without breaking balance.

## The Three Layers

```
┌─────────────────────────────────────────────────────────┐
│ Layer 1 — AI Engine (deterministic, balanced)           │
│   Rule-based decision function per ship class.          │
│   Inputs: sensor data, ship state, ObjectsOfConcern     │
│   Outputs: action bits (THRUST, LEFT, RIGHT, WEAPON,    │
│             SPECIAL, etc.) — exactly the UQM model.     │
└─────────────────────────────────────────────────────────┘
                       ▲
                       │ reads
                       │
┌─────────────────────────────────────────────────────────┐
│ Layer 2 — Personality (varied per encounter, seeded)    │
│   A personality vector biases the decision function's   │
│   thresholds. Same AI, different captain.               │
│   Vector: aggression, caution, patience, opportunism,   │
│           hesitation, persistence, vindictiveness       │
│   Persists for the duration of the fight.               │
└─────────────────────────────────────────────────────────┘
                       │
                       │ reads
                       ▼
┌─────────────────────────────────────────────────────────┐
│ Layer 3 — Banter (LLM-rendered, cosmetic)               │
│   At key moments — combat start, 50% health, near-miss, │
│   weapon depleted, last seconds — the LLM emits a       │
│   short utterance from the enemy. Personality + fight   │
│   state feed the prompt. Subtitled or voiced; doesn't   │
│   affect gameplay.                                      │
└─────────────────────────────────────────────────────────┘
```

Layer 1 is the engine — exactly the UQM model, fully balanced. Layer 2 introduces *variance in style* without changing the ship's strength. Layer 3 makes each fight feel like it's *narrated* by the enemy.

**Critical property**: Layer 2 must not change the ship's *effective* strength. A high-aggression Cleanser cruiser fires sooner but is also more often out of position; a high-caution Cleanser fires later but stays alive longer. The personality knobs are tradeoffs, not buffs. We tune the trade space so that no personality is strictly better than another. **The player should *never* think "I got an easy Cleanser this time" — only "I got an *aggressive* Cleanser this time."**

## Personality Vector (Layer 2)

Each vector has 0-100 axes, seeded by encounter ID. Most ships only use 3-4 of these.

| Axis | What it biases |
|---|---|
| **Aggression** | Fire range (high = fires sooner), pursuit distance (high = chases farther), risk tolerance (high = accepts shorter dodge windows) |
| **Caution** | Dodge trigger distance (high = dodges earlier), retreat threshold (high = retreats at higher HP), shield usage timing |
| **Patience** | Time between weapon volleys, willingness to circle without firing, ambush behavior (high = waits longer for ideal shot) |
| **Opportunism** | Likelihood of breaking off engagement to chase a kill on a weakened target, willingness to use one-shot specials |
| **Hesitation** | (Furling-specific) Pauses before firing, slightly reduces fire rate, never fully — they don't *want* to do this |
| **Persistence** | How long the AI commits to a tactic before reconsidering (high = sticks to plan, low = thrashes) |
| **Vindictiveness** | (Combat with prior history) Likelihood of targeting the player who beat them in a previous fight even when other targets are available |

Each personality is generated at the start of the encounter from:
1. Faction preset (Cleanser cruisers default to medium-high hesitation, low aggression-relative-to-caution)
2. Per-encounter randomization within the preset's range
3. Seed = `(player_save_id, encounter_id, ship_id)` — same fight reloaded = same personality

### Faction Presets

The four likely combat opponents in the slice and their personality biases:

**Cleanser Furling cruiser** (the slice's combat climax)
- Aggression: 40-60 (moderate)
- Caution: 50-70 (high — they value their life, they know this is wrong)
- Patience: 60-80 (high — they wait for clean shots)
- Hesitation: 50-80 (high — they're killing their own people)
- Persistence: 70-90 (high — they have a mission)
- *Variance per individual*: which axis dominates. Some Cleansers are fast and decisive; some are slow and weighty.

**Defender Furling courier** (passing through, optional combat)
- Aggression: 60-80
- Caution: 30-50
- Patience: 30-50 (low — they want to fight *now*)
- Hesitation: 10-30 (low — they've made their peace with violence)
- Persistence: 80-95 (very high — they will not break)
- Vindictiveness: variable

**Rogue Mycon biot** (early-sentience Deep Child possessed)
- Aggression: 70-95 (high)
- Caution: 10-40 (low — they don't fear death)
- Patience: 20-40 (low)
- Hesitation: 0 (they cannot hesitate — the Deep Child speaks through them)
- Persistence: highly variable per individual — Deep Child instability
- *Variance per individual*: how *coherent* their tactics are. Heavily-possessed biots are wildly unpredictable; lightly-possessed biots execute simple kamikaze runs.

**Them-rift creature** (optional, the dimensional incursion)
- Doesn't use the standard vector
- Movement is sampled from a non-Euclidean distribution; tactics shift mid-fight at random intervals
- Fights without strategy — alien physics, alien decisions
- Banter is unsettling third-person description ("the shape vibrates and is now closer than it was")

## LLM Banter (Layer 3)

The dialog system already has the infrastructure — same renderer, different trigger contexts. Combat banter is **state-triggered** rather than choice-triggered.

### Banter triggers

| Trigger | When it fires | Banter intent |
|---|---|---|
| `COMBAT_START` | Once per encounter, on first frame | Declaration of intent |
| `FIRST_BLOOD` | Player or enemy takes first damage | Acknowledgment |
| `HALF_HEALTH` | Enemy HP hits 50% | Defiance, hesitation, or reconsideration |
| `NEAR_MISS` | Enemy weapon misses by < 50 units | Frustration or precision-pride |
| `WEAPON_LANDED` | Enemy weapon hits | Triumph or guilt (depending on faction) |
| `LOW_ENERGY` | Enemy energy < 20% | Tactical complaint |
| `BLED_OUT` | Enemy at <10% HP | Last words, surrender plea, or final commitment |
| `PLAYER_RETREATS` | Player tries to flee | Mocking, sad, or relieved |
| `STALEMATE` | 30 sec without damage | Restless flavor — both sides circle |
| `KILL` | Enemy dies | The line you remember |

### Banter LLM prompt structure

Same architecture as the species dialog, slimmer:

```
System: You are the captain of a {ship_class} aligned with the
{faction} faction. Your personality is {personality_vector_summary}.
You are speaking {trigger_intent} during combat with a Furling
Steward you {disposition_toward_player}. Your speech is short —
ten words or fewer. {voice_profile}.

User: {fight_state_summary} {trigger_event}
```

`fight_state_summary` includes: own HP%, own energy%, distance to player, weapon ready, last action taken, time since combat start.

### Example outputs (illustrative, not authored)

**Cleanser cruiser at COMBAT_START, high hesitation:**
> "Steward. Stand aside. Please."

**Cleanser cruiser at HALF_HEALTH, moderate aggression:**
> "You are killing the Slylandro by saving them."

**Cleanser cruiser at BLED_OUT, low aggression:**
> "Tell the Council the Quiet was almost mine."

**Rogue Mycon biot at NEAR_MISS, Deep Child whispering:**
> "the deep child sees. closer. closer."

**Defender Furling courier at COMBAT_START, high persistence:**
> "Run if you want. We are the wall."

**Them-rift creature at WEAPON_LANDED:**
> "the shape brightens where you bled. it tastes the same."

The LLM gets the fight state and produces something appropriate. **The line is not authored — it's varied.** Same encounter twice produces two different opening lines from the same Cleanser.

## Within-Fight Adaptation (Optional, Layer 1.5)

A genuinely interesting stretch: the AI tracks recent player behavior *within* the current fight and biases its next decisions accordingly.

Examples (cheap to implement):
- Player has dodged right 3 of last 4 times → next weapon aims slightly right of player's predicted position
- Player has stayed at long range for 10 seconds → AI commits to a closing maneuver
- Player has fired their special in the last 5 seconds → AI knows the special is on cooldown, becomes more aggressive

Implementation: a small sliding-window log of player actions feeds into the personality-modulated decision function. The AI's "adaptiveness" is itself a personality axis (a high-adaptiveness Cleanser learns within the fight; a low-adaptiveness rogue biot doesn't).

This *does* affect balance, so it must be tuned carefully — but it's the difference between "the AI is randomized" and "the AI is *paying attention*." It's also the layer that earns the description "less predictable than the original devs did."

**Note this breaks the strict variation-layer rule** (which is "cosmetic only"). Adaptation is gameplay-affecting. So it's its own thing — a tunable difficulty knob, not the variation layer. Treat adaptation as a separate feature with its own dial; ship the game with it off, then turn it on for higher difficulty.

## Cross-Fight Memory (Optional, Phase 6+)

A more ambitious stretch: enemies remember the player's previous tactics from earlier fights. Save-file state tracks "the player has shown preference for long-range attacks against Cleansers" and the *next* Cleanser cruiser arrives with a higher caution score against long-range openings.

This makes the universe feel reactive — the Cleansers learn about you over time. It is also a balance nightmare and a player-experience risk (people don't love when games "punish" them for playing a certain way). **Defer to Phase 6+ at earliest, and only if the personality layer alone hasn't produced enough variety.**

## Implementation Notes

### Modifying the UQM-style decision function

UQM's `<species>_intelligence` checks thresholds like `which_turn <= 4`. Our version:

```python
# Engine layer — same as UQM
def cleanser_intelligence(ship_state, objects_of_concern, personality):
    threats = objects_of_concern[ENEMY_WEAPON]
    enemy = objects_of_concern[ENEMY_SHIP]

    # Personality-modulated thresholds
    fire_range = baseline_fire_range * (1 + personality.aggression / 200)
    dodge_trigger = baseline_dodge_distance * (1 + personality.caution / 200)
    fire_hesitation_frames = personality.hesitation // 10

    if threats and threats.turns_to_impact < dodge_trigger:
        return dodge_action(ship_state, threats)

    if enemy and ship_state.distance_to(enemy) < fire_range:
        if ship_state.frames_since_last_fire >= fire_hesitation_frames:
            return weapon_fire_action()

    return approach_action(enemy)
```

The personality vector turns a single AI function into a *family* of AI behaviors. Same code paths, different feel.

### Banter integration

Banter calls are async (LLM has latency). Implementation:
- At each trigger, queue a banter request with the current state.
- Continue combat without blocking — combat runs at 60fps, LLM at ~1-3 sec.
- When the LLM response arrives, display the line as a subtitled bubble over the enemy ship.
- If the response arrives "too late" (fight state has changed materially), discard it. Don't show stale banter.

### Caching

Personality vectors are deterministic, so a save-and-reload reproduces the same fight. Banter text is *not* deterministic by default (LLMs are sampled), but we can seed the LLM call for reproducibility if that matters.

## Defensive Doctrine — Shields vs Hull (per furling-tech-mechanics §5)

Combat balance and AI behavior both turn on a single asymmetry: **the Furling Scout has regenerating shields; most other ships do not.** The full design lives in [furling-tech-mechanics.md "Annoyance #5"](furling-tech-mechanics.md); the short version that affects AI:

- Furling ships (Scout, Persuader, Defender, **Cleanser**) have shields. The Cleanser fight is therefore even on this axis.
- Almost everyone else has hull only. Damage them and they don't get it back — the engagement clock is one-way for them.
- The player's natural strategy against non-Furling enemies is **bide-and-strike**: attack, withdraw, let shields regen, attack again. The enemy can't match this cycle. AI on the player's opponents needs to *understand* this so it isn't trivially exploitable — caution + persistence axes interact with shield state.

For Layer 1 (engine AI): non-shielded ships factor in their bleed clock — they should NOT engage at the player's preferred range if the player is regenerating. The decision function reads `(my_hull_pct, my_has_shields, enemy_has_shields, enemy_shield_pct)` and biases retreat thresholds accordingly. Without this, every fight devolves to "stand at sniper range until the bleed wins."

Solo-captained ship: crew never die. Damage hits ship state only. AI never targets "crew" because it isn't a stat. Out-of-combat hull repair is a mineral cost paid at safe-zones.

## Auto-Fight Toggle (in every combat scene)

Combat exposes an **AUTO-FIGHT** toggle (default off) — when on, the engine AI flies the *player's* ship using the same decision function as the opponent. This is a first-class feature, not a debug switch:

- **Testability**: the test harness can launch combat encounters and watch them resolve without scripting stick deflections or weapon timing. The harness can validate "this fight is winnable" with a single binary outcome.
- **Player offload**: occasionally the player just wants to see a fight resolve — handing the wheel to the AI for a routine encounter is a fine option. We're not building a twitch game.
- **Fairness check**: identical AI on both sides is a clean test of raw ship balance. If a fight is unwinnable on auto-fight against a fair opponent, the ship balance is wrong.

Mechanically simple — same `<ship>_intelligence` function the opponent uses, with the player's ship state and the opponent as `enemy_of_concern`. Player can toggle mid-fight (X button or similar) to take over.

## Slice Scope

Phase 2 ships static AI — pure UQM-style decision functions per ship class. **No personality vector, no LLM banter — both are deferred to a later phase**. The Cleanser cruiser fight is winnable, balanced, predictable. The auto-fight toggle ships with Phase 2 from day one.

After the full static game works end-to-end (every scene playable, every species in slice has a real encounter, the slice can be completed without LLM):

1. **Personality vector** — ~1 week of work to add the threshold modulation to the 2-3 ship classes the slice has
2. **Banter layer** — reuses the dialog renderer infrastructure; another ~1 week

Phase 6 (post-slice):
- Within-fight adaptation
- Cross-fight memory
- More personality axes
- Per-ship-class unique tactics (Defender ramming, Cleanser disable-shot before kill-shot)

## Why This Matters

The Cleanser cruiser fight is the slice's emotional climax. Two outcomes need to be possible:

- **You fight a Cleanser who hates the work but does it anyway** — high hesitation, ten-word apologies between volleys, "the Slylandro will thank me later" at bled-out
- **You fight a Cleanser who has stopped feeling it** — low hesitation, sharp fire timing, "don't make this poetic" at bled-out

Both fights play with the *same balance*. The player can't tell from the win/loss numbers which Cleanser they got. They can tell from *every other detail of the fight.* That's what the layered AI buys.
