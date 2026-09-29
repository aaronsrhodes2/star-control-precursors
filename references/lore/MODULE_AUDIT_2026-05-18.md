# Module Acquisition Audit — 2026-05-18

Audit of `src/scz/content/modules.py` against the live grant sites in
`src/scz/`. A *grant site* is production code that writes to
`game.uninstalled_modules[<id>]` or to `game.schematics`. References
inside `src/scz/testing/scripts.py` (walk_* scenes) and `tools/*` are
**test seeding**, not real gameplay grants — flagged separately.

## Summary

- **Total modules in MODULES**: 57
- **Purchasable (shop)**: 28 (filter: `tier ≥ 1 AND NOT locked AND no unlock_schematic`)
- **Purchasable via schematic**: 5 (all 5 schematics exist in `schematics.py`; **0 of 5 schematics have a production grant site** — entire schematic loop is currently unreachable in real gameplay)
- **Quest reward (tier-0 with grant site)**: 4 — `scanner_mk3`, `hyperspace_echo_sensor`, `melnorme_pattern_sensor`, `melnorme_plasma_lance`, `melnorme_trade_network_sensor`, `crew_pilot` (6 actually)
- **Locked-but-granted (tier-0/locked with grant site)**: 2 — `crew_pilot`, `melnorme_trade_network_sensor`
- **ORPHANS (in MODULES but no production grant)**: 16
  - **Tier-0 quest-rewards with no grant**: `bio_architect`, `rainbow_resonator`, `sa_matra_lance_replica`
  - **Locked crew (recruitment quest not yet implemented)**: `crew_weapons_officer`, `crew_engineer`, `crew_medic`, `crew_navigator`
  - **Locked sensor stubs (TODO render-layer)**: `bio_sense_scanner`, `enemy_scanner`, `anomaly_scanner`, `hazard_scanner`
  - **Schematic-gated (schematic-grant code missing)**: `furling_coil_lance`, `dimensional_armor`, `pulse_cannon`, `mmrnmhrm_reinforced_plating`, `arilou_phase_dampener`
- **Reverse-orphan (granted but NOT in MODULES)**: 1 — `lemmkin_pattern_database` is awarded by `dialog/characters.py:210` but has no `Module` definition

## Per-module table

| Module ID | Slot | Tier | Locked | Acquisition Path | Notes |
|---|---|---|---|---|---|
| `scanner_mk3` | sensor | 0 | F | quest_reward | `planet/scene.py:576` (Furlmart PACKAGE_SCANNER_MK3 tractor) — tutorial pickup verified |
| `hyperspace_echo_sensor` | sensor | 0 | F | quest_reward | `dialog/characters.py:90` (`_grant_slylandro_cloak`) |
| `bio_architect` | crew_1 | 0 | F | **ORPHAN** | No grant — Mantle-Resonance Bio-Architect (Mycon gift) — Mycon quest not wiring grant |
| `rainbow_resonator` | field | 0 | F | **ORPHAN** | No grant — Rainbow World seeding; final-conflict gate checks for it but nothing AWARDS it |
| `lr_mineral_scanner` | sensor | 1 | F | shop | Mh-Lai Customization (purchasable_modules) |
| `melnorme_trade_network_sensor` | sensor | 0 | T | quest_reward | `dialog/characters.py:1593` (`_melnorme_commit`, Trader's Manifest Beat 5) |
| `backup_capacitor` | drive | 1 | F | shop | Standard tier-1 |
| `shield_booster_i` | field | 1 | F | shop | Standard tier-1 |
| `beam_mod_i` | weapon | 1 | F | shop | Standard tier-1 |
| `cargo_pod_plus_50` | hull | 1 | F | shop | Standard tier-1 |
| `quasi_drive_compact` | drive | 2 | F | shop | Tier-2; shown when `purchasable_modules` selects it |
| `sa_matra_lance_replica` | weapon | 2 | T | **ORPHAN** | `locked=True` "requires Defender quest progress" — no quest sets `locked=False` and no grant code; permanently shop-hidden |
| `melnorme_plasma_lance` | weapon | 0 | F | quest_reward | `dialog/characters.py:1482` (`_melnorme_try_buy_tech` via MELNORME_TECH_ITEMS) |
| `melnorme_pattern_sensor` | sensor | 0 | F | quest_reward | `dialog/characters.py:1482` (`_melnorme_try_buy_tech` via MELNORME_TECH_ITEMS) |
| `crew_archivist` | crew_1 | 1 | F | shop | Standard tier-1 named crew |
| `crew_warden` | crew_2 | 1 | F | shop | Standard tier-1 named crew |
| `crew_tunneler` | crew_2 | 1 | F | shop | Standard tier-1 named crew |
| `crew_pilot` | crew_1 | 1 | T | locked_quest_reward | `dialog/characters.py:506` (`_recruit_mraka` — The Sure-Foot quest) |
| `crew_weapons_officer` | crew_1 | 1 | T | **ORPHAN** | Bren-Vor Telcas; Common Room dialog is a stub (`bren_vor_telcas()` at characters.py:5272); `recruited_weapons_officer` flag is never set in production code |
| `crew_engineer` | crew_1 | 1 | T | **ORPHAN** | Yelena Lwen-Tar; same pattern — alcove + stub dialog, no recruitment FSM |
| `crew_medic` | crew_2 | 1 | T | **ORPHAN** | Mira-Rou Halve-Tel; same pattern |
| `crew_navigator` | crew_2 | 1 | T | **ORPHAN** | Tarven Olwen-Sa; same pattern |
| `bio_sense_scanner` | sensor | 1 | T | **ORPHAN** | Stub — TODO render-layer wiring (renderers not yet built) |
| `enemy_scanner` | sensor | 1 | T | **ORPHAN** | Stub — TODO render-layer wiring |
| `anomaly_scanner` | sensor | 1 | T | **ORPHAN** | Stub — TODO render-layer wiring |
| `hazard_scanner` | sensor | 1 | T | **ORPHAN** | Stub — TODO render-layer wiring |
| `weapon_mod_accuracy` | weapon | 1 | F | shop (free) | tier=1, `cost_credits=0` — free at shop. Unusual but valid |
| `weapon_mod_reload` | weapon | 1 | F | shop (free) | tier=1, `cost_credits=0` — free at shop. Unusual but valid |
| `mod_twin_beam` | weapon | 1 | F | shop | Combat mod (pattern override) |
| `mod_lance_coil` | weapon | 2 | F | shop | Combat mod (pattern override) |
| `mod_scatter_array` | weapon | 1 | F | shop | Combat mod (pattern override) |
| `mod_pulse_cannon` | weapon | 2 | F | shop | Combat mod (pattern override) — note ID collision: also a schematic-gated `pulse_cannon` exists separately |
| `mod_homing_mortar` | weapon | 2 | F | shop | Combat mod (pattern override) |
| `mod_burst_cannon` | weapon | 1 | F | shop | Combat mod (pattern override) |
| `mod_tracking_laser` | weapon | 2 | F | shop | Combat mod (pattern override) |
| `mod_lawnmower_disc` | weapon | 2 | F | shop | Combat mod (pattern override) |
| `mod_beam_mod_ii` | weapon | 2 | F | shop | Stat-only |
| `mod_engine_disruptor` | weapon | 2 | F | shop | Stat-only |
| `mod_shield_capacitor` | field | 2 | F | shop | Defensive |
| `mod_shield_catalyst` | field | 2 | F | shop | Defensive |
| `mod_crystalline_armor` | field | 2 | F | shop | Defensive |
| `mod_reactive_plating` | field | 2 | F | shop | Defensive |
| `mod_hull_reinforcement` | hull | 1 | F | shop | Hull |
| `mod_repair_drone` | hull | 2 | F | shop | Hull |
| `mod_ablative_coating` | hull | 1 | F | shop | Hull |
| `mod_thruster_boost` | drive | 1 | F | shop | Drive |
| `mod_maneuvering_jets` | drive | 1 | F | shop | Drive |
| `mod_gyro_stabilizer` | drive | 1 | F | shop | Drive |
| `mod_energy_cell` | drive | 2 | F | shop | Energy |
| `mod_power_regenerator` | drive | 2 | F | shop | Energy |
| `mod_phase_skip` | field | 2 | F | shop | Special-swap |
| `mod_chaff_spray` | field | 2 | F | shop | Special-swap |
| `furling_coil_lance` | weapon | 1 | F | **ORPHAN (schematic)** | `unlock_schematic=schematic_furling_coil_lance` — schematic registered but nothing grants it in production |
| `dimensional_armor` | hull | 2 | F | **ORPHAN (schematic)** | `unlock_schematic=schematic_dimensional_armor` — same |
| `pulse_cannon` | weapon | 1 | F | **ORPHAN (schematic)** | `unlock_schematic=schematic_pulse_cannon` — same |
| `mmrnmhrm_reinforced_plating` | hull | 1 | F | **ORPHAN (schematic)** | `unlock_schematic=schematic_mmrnmhrm_reinforced_plating` — same |
| `arilou_phase_dampener` | field | 2 | F | **ORPHAN (schematic)** | `unlock_schematic=schematic_arilou_phase_dampener` — same |

## Orphans (modules with no obtainability path)

### Tier-0 quest-reward orphans

- **`bio_architect`** (slot=crew_1, tier=0): Mantle-Resonance Bio-Architect, canonically the Mycon-quest gift. No Mycon-quest grant code adds it to `uninstalled_modules`. **Fix**: wire a side-effect handler in the Mycon dialog branch (mirror the pattern in `_grant_slylandro_cloak` at `dialog/characters.py:81-92`) when the Mycon quest enters its terminal Migrated/Honored state.
- **`rainbow_resonator`** (slot=field, tier=0): The slice-climax field module. `content/final_conflict.py:177` *checks* if it's installed; nothing *grants* it. **Fix**: wire a grant when the Rainbow Worlds arrow is solved (likely a Rainbow World quest terminal-state handler).
- **`sa_matra_lance_replica`** (slot=weapon, tier=2, locked=True): "Defender-faction prototype lance; locked — requires Defender quest progress." The Defender quest doesn't exist as production code that flips `locked=False` (the Module dataclass is `frozen=True` anyway, so this cannot mutate at runtime — the architecture currently has no path for it to become unlockable). **Fix**: either (a) implement as a grant rather than a lock-toggle (give it tier-0 and add a grant site, like `melnorme_trade_network_sensor`), or (b) remove from MODULES until the Defender questline lands.

### Locked-crew orphans (recruitment-quest content TODO)

These four match the `UNLOCKED_BY` comment pattern Aaron canonized in
the module catalog header, but the recruitment FSMs are documented as
"TODO_LORE pending Design implementation" in `characters.py` stubs
(`bren_vor_telcas`, `yelena_lwen_tar`, `mira_rou_halve_tel`,
`tarven_olwen_sa` at lines 5272–5342). Per the in-file note, these
stay locked + pre-staged until the recruitment quests are wired.

- **`crew_weapons_officer`** (slot=crew_1, tier=1): needs `_recruit_brenvor` handler that sets `recruited_weapons_officer` + grants module.
- **`crew_engineer`** (slot=crew_1, tier=1): needs `_recruit_yelena` handler.
- **`crew_medic`** (slot=crew_2, tier=1): needs `_recruit_mira` handler.
- **`crew_navigator`** (slot=crew_2, tier=1): needs `_recruit_tarven` handler.

These should be either (a) wired with a real recruitment FSM beat (the
pattern is established by `_recruit_mraka` at characters.py:493), or
(b) explicitly held back from MODULES until that work lands. Currently
they bloat the Bio-Archive's module-identity table without being
attainable.

### Sensor-stub orphans (TODO render-layer)

- **`bio_sense_scanner`** (slot=sensor, tier=1, locked=True)
- **`enemy_scanner`** (slot=sensor, tier=1, locked=True)
- **`anomaly_scanner`** (slot=sensor, tier=1, locked=True)
- **`hazard_scanner`** (slot=sensor, tier=1, locked=True)

Per the in-file comment at modules.py:467 — "All locked pending content:
the actual visualization layer needs to be wired in the scene render
path before each can ship." These are deliberate stubs awaiting render
work. Acceptable as catalog placeholders, but they are not currently
obtainable — flag if any quest/Lore doc promises one as a reward.

### Schematic-gated orphans (schematic loop never primed)

All 5 schematic-gated modules are orphans because the **schematics
themselves are never granted in production code**. The full schematic
loop is wired (`schematics.py`, `station/schematic_vault.py`,
`content/modules.py` filter on `consumed_schematics`), but no quest
side-effect ever calls `game.schematics.add(...)`. Test seeding via
`s.set_schematics([...])` (e.g. `testing/scripts.py:3251`) is the
only place schematics ever enter the player's possession.

- **`furling_coil_lance`** (slot=weapon, tier=1): needs `schematic_furling_coil_lance` to be sold by Melnorme per `schematics.py:71-88` source_origin. **Fix**: add a `_melnorme_buy_schematic` handler (parallel to `_melnorme_try_buy_tech` at characters.py:1470) that adds the schematic id to `game.schematics`.
- **`dimensional_armor`** (slot=hull, tier=2): needs `schematic_dimensional_armor` grant from a Persuader-wreck salvage scene (currently unimplemented — Gamma Vulpeculae Rift environmental pickup per source_origin).
- **`pulse_cannon`** (slot=weapon, tier=1): needs `schematic_pulse_cannon` grant from a Hearth survey-lifter salvage (unimplemented).
- **`mmrnmhrm_reinforced_plating`** (slot=hull, tier=1): needs `schematic_mmrnmhrm_reinforced_plating` grant from the Mmrnmhrm Ossuary visit by Sentinel-Aux Theta-Four (unimplemented).
- **`arilou_phase_dampener`** (slot=field, tier=2): needs `schematic_arilou_phase_dampener` grant slipped in by Sage Lwen-Olou during the Quasi-Space portal gifting (the Arilou Sage's QS portal handler should add this schematic as a silent side-effect, per source_origin).

### Reverse-orphan (granted, but no Module definition)

- **`lemmkin_pattern_database`** is granted at `dialog/characters.py:210` (`_lemmkin_science_trade`), but **no `Module` with this id exists in MODULES**. This means the customization scene cannot install or display it; `Module = MODULES.get(installed_id)` returns None at `customization.py:333` and the rendering falls back to a bare id. **Fix**: add a `LEMMKIN_PATTERN_DATABASE` Module entry (sensor slot, tier-0, deltas TBD from species-sheets.md `§9.3 Lemmkin reward stat block`).

## Schematic verification

| Schematic ID | Granted by | Target Module | Notes |
|---|---|---|---|
| `schematic_furling_coil_lance` | **NOWHERE** (production) | `furling_coil_lance` | Lore source: Melnorme trader — not implemented |
| `schematic_dimensional_armor` | **NOWHERE** (production) | `dimensional_armor` | Lore source: Persuader-wreck salvage at Gamma Vulpeculae — not implemented |
| `schematic_pulse_cannon` | **NOWHERE** (production) | `pulse_cannon` | Lore source: drifting survey lifter — not implemented; test seeds at `scripts.py:3251` |
| `schematic_mmrnmhrm_reinforced_plating` | **NOWHERE** (production) | `mmrnmhrm_reinforced_plating` | Lore source: Mmrnmhrm Ossuary archive consensus — not implemented |
| `schematic_arilou_phase_dampener` | **NOWHERE** (production) | `arilou_phase_dampener` | Lore source: Arilou Sage during QS-portal gifting — not implemented |

All 5 schematics are well-formed (registry id ↔ Module.unlock_schematic
pairings match perfectly) but the loop is not primed: no quest
side-effect ever adds an id to `game.schematics`. The Vault sub-scene
will always show "0 held" in real gameplay.

## Verified grant sites (real production grants, not test seeding)

| Grant site | Module ID | Trigger |
|---|---|---|
| `src/scz/planet/scene.py:576` | `scanner_mk3` | PACKAGE_SCANNER_MK3 deposit tractored on Furlmart pickup |
| `src/scz/dialog/characters.py:90` | `hyperspace_echo_sensor` | `_grant_slylandro_cloak` — Slylandro quest reward |
| `src/scz/dialog/characters.py:210` | `lemmkin_pattern_database` *(reverse-orphan)* | `_lemmkin_science_trade` — Lemmkin science-trade side-action |
| `src/scz/dialog/characters.py:506` | `crew_pilot` | `_recruit_mraka` — The Sure-Foot recruitment quest |
| `src/scz/dialog/characters.py:1482` | `melnorme_plasma_lance`, `melnorme_pattern_sensor` | `_melnorme_try_buy_tech` — Melnorme BIO-cargo purchase |
| `src/scz/dialog/characters.py:1593` | `melnorme_trade_network_sensor` | `_melnorme_commit` — Trader's Manifest Beat 5 commitment |

Only **6 production grant sites** in the entire codebase. Everything
else relies on the shop filter (`purchasable_modules`) or is currently
orphaned.

## Customization-scene impact

`station/customization.py:298-307` is the install path. When the
player picks a tier-0 module from inventory, it's decremented from
`uninstalled_modules`. When they pick a tier-1+ module, costs are
deducted and the install completes. Both paths require the module ID
to be in `MODULES` for the install to render correctly
(`customization.py:333` does `mod = MODULES.get(installed_id)` and
silently falls back if missing). The reverse-orphan
`lemmkin_pattern_database` will currently render as a bare id string
in the slot-uninstall confirmation toast.
