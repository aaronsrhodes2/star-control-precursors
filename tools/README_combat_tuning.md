# Combat tuning — sim harness + change log

## Quick start

```bash
# Default — all-vs-all, 10 seeds each, ~100 matchups, ~3-4 min wall time
python tools/sim_combat.py

# Higher confidence (N=30 takes ~10 min)
python tools/sim_combat.py --n 30

# Targeted matchup
python tools/sim_combat.py --a furling_scout --b cleanser_cruiser --n 50

# Trace one fight frame-by-frame (diagnostic)
python tools/sim_combat_trace.py furling_scout cleanser_cruiser 0
```

CSV output goes to `data/combat_sim.csv` by default; the summary prints
to stdout. Use `--quiet` to suppress the summary.

## What the sim measures

- **Same-pair fights** (Ship X vs Ship X). Should resolve in <60s and
  a_win% should be close to 50% — otherwise the AI has a spawn-side
  bias or the sim's tiebreak is biased.
- **Most imbalanced cross-pair matchups**. Top N matchups with the
  most extreme a_win% (closest to 0 or 100). A clean balance shows
  asymmetry but no auto-loss.
- **High-timeout matchups**. Fights that hit `max_duration` (60s)
  indicate AI passivity or shield-regen stalemate.
- **Per-ship average win rate**. Across all cross-pair matchups,
  averaged. The spread (top-bottom) is the balance gap.

## Tuning history (newest first)

### 2026-05-17 — first tuning pass

Before tuning: cleanser 99% / furling 99% / proto_qor_ah 0% — same-pair
fights timed out 100% with zero kills (friendly-fire bug in sim, since
same-side ships can't damage each other).

Changes applied:

| Change | File | Why |
|---|---|---|
| Force distinct `side` strings on the two ShipStates per fight | `tools/sim_combat.py` | Same-side matchups (e.g. furling_scout vs furling_scout) were blocked by the friendly-fire filter. The sim is a mirror-balance check, not a canon-side check. |
| Tiebreak randomization at timeout when scores within 3% | `src/scz/combat/scene.py` | Previously precursor always won ties, biasing same-side sim outcomes. The mirror fights at timeout were exactly tied (no damage taken). |
| Target leading on AI fire | `src/scz/combat/ai.py` | Slow-projectile ships (proto_ur_quan @ 600u/s, melnorme @ 400u/s, arilou @ 700u/s) had ~95% miss rate vs moving targets. Now they predict where the enemy will be when the projectile arrives. |
| Press-the-attack mode when shields healthy + enemy weakening | `src/scz/combat/ai.py` | Two shielded ships orbited at ideal_dist forever, hit rate × DPS < shield regen. Pressing closes to 40% of range and lands sustained damage. |
| Lateral evasion when taking sustained damage | `src/scz/combat/ai.py` | Adds strafing perpendicular to enemy — helps low-HP ships dodge during sustained exchanges. |
| Speed-inverse hit radius for projectiles | `src/scz/combat/scene.py` | Slow projectiles are now "wider" — missiles/plasma globs are easier to land than hitscan beams. Helped melnorme (+8pts) and proto_ur_quan (+4pts) in cross-pair win rate. |
| Cleanser Cruiser shield 100 → 70 | `src/scz/combat/ships.py` | Was beating *every* other ship including the player's base Furling Scout 100%. Slice climax should be hard, not auto-loss. Now ~92% — still dominant, but at least the base Furling Scout has a chance. |

Result after tuning (N=30 sweep, all-vs-all):

```
cleanser_cruiser    92.2%   (slice-climax fight, intentionally tough)
furling_scout       87.8%   (player base — modular hull, expected strong)
defender_vessel     72.8%
melnorme_trader     70.4%
mmrnmhrm_sentinel   59.1%
androsynth_cruiser  48.1%
persuader_vessel    35.4%
proto_ur_quan       22.0%   (specialist — close-range warship)
arilou_skiff        11.5%   (specialist — kiter, needs quasispace to shine)
proto_qor_ah         0.7%   (specialist — glass-cannon brawler, dies on approach)
```

Zero timeouts. Same-pair fights resolve in 12-52s. Cross-pair matchups
are asymmetric but no longer pathological for the middle tier.

### Known issues (deferred — require Aaron's ship-design sign-off)

- **proto_qor_ah at 0.7%** — range 120 + hull 60 means it dies during
  the approach against any ship with hitscan range 400+. Identity is
  "rapid close-range glass cannon brawler" but with no shield, no
  defensive special, and no homing weapons, the archetype doesn't
  work in 1v1. Needs a defensive special (e.g. SC2 Spathi BUTT
  missiles) or a damage-resistant approach (afterburner immunity
  window).

- **arilou_skiff at 11.5%** — designed as a quasispace kiter; without
  the QS escape mechanic in combat (currently only available outside
  combat), it has no edge over equivalent kiters that bring more hull
  / shield.

- **Tiered top: cleanser 92% / furling 88%** — both are above-average
  even after tuning. Furling Scout is intentionally the *modular base*
  ship (player gets stat boosts via Mh-Lai customization), so a strong
  baseline is fine. Cleanser is the slice climax — should feel
  oppressive but not auto-loss.

- **Tiebreak bias in same-pair**: a few same-pair fights still skew
  85-95% A wins (defender, cleanser, persuader). Spawn jitter and AI
  parity-based strafe may contribute. Not a balance crisis since the
  fights resolve cleanly (no timeouts) — just an asymmetry that would
  bother a strict mirror-balance check.

## When to re-run the sim

- After ANY change to `src/scz/combat/ai.py` or `src/scz/combat/scene.py`
- After ANY change to `src/scz/combat/ships.py` (stat tweak)
- Before merging a combat-related PR — diff CSV pre/post

## When NOT to use this

- Combat *feel* questions ("does the fight have good rhythm?") — you
  need the real game, not a sweep. Use `walk_super_melee` and watch.
- Combat with player input — the sim runs both ships on AI. Add
  player-input hooks if you want sim-vs-AI fights, but for now the
  sweep is AI-vs-AI only.
- Validating specials/abilities — none are implemented yet. When they
  land, the sim's AI hook needs a `should_special()` decision.
