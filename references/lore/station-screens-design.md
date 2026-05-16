## Station Screens — Trade + Ship Customization + Bio-Archive (UX design)

> Three Station sub-scenes that gate Beat 5 of the tutorial and several slice quest rewards. All three are currently stubs in `src/scz/scenes/stubs.py`. This doc designs them as concrete implementable scenes: control flow, what they show, what they mutate, where the data lives.

All three follow the established universal menu convention: vertical list, wrap-around, A select, B back, D-pad / arrow keys / L-stick to navigate. Aaron's canonical control scheme. See [project_controls_and_menus](D:/Aaron/development/star-control-precursors/references/lore/notes.md) and the existing `StationScene` + `SceneSwitcher` for reference implementations.

## Resource Types (canon — used by Trade, Customization, and the planet collection loop)

Already defined in `src/scz/planet/deposits.py`:

| Type | Visual | Use |
|---|---|---|
| **COMMON** | Yellow-brown rocks | Generic minerals; main currency-source via Trade. Plentiful. |
| **USEFUL** | Bright orange crystals | Higher-value minerals; module crafting input |
| **BIO** | Green organic | Biological data — for Archive entries, certain module crafts |
| **ENERGY** | Blue-white shards | Rare energy crystals; weapon-module upgrades |

The Trade scene converts these to **Council Credits** (a new abstract resource — int counter, no visual mass). Modules cost credits + sometimes specific resource types. Quest items (Scanner Mk III, Cloaking Satellite, Bio-Architect, etc.) are NOT tradeable — they sit in a separate non-stackable inventory.

### Pricing baseline (first-pass; tune in playtest)

| Resource → Credits | Sell price |
|---|---|
| 1× COMMON | 1 credit |
| 1× USEFUL | 4 credits |
| 1× BIO | 6 credits |
| 1× ENERGY | 12 credits |

Module costs scale: a Tier-1 ship module is ~50-100 credits + 5-10 USEFUL or BIO; Tier-2 is ~200+ + 20 USEFUL/BIO/ENERGY; quest-reward modules are *free* (the player earned them by completing the quest).

## 1. Trade Scene

**Class**: `TradeScene` in `src/scz/station/trade.py` (new).

**Entry**: Station menu → "Trade resources" → TradeScene. Parent scene: StationScene. B returns to StationScene.

**Layout**:

```
┌─────────────────────────────────────────────────────────────┐
│  TRADE  ·  Mh-Lai Station                                   │
│                                                              │
│  CARGO HOLD                          │  COUNCIL CREDITS      │
│                                       │                       │
│  ► Common minerals     127           │   credits: 412        │
│    Useful minerals      28           │                       │
│    Bio-data             14           │   exchange rate:      │
│    Energy crystals       3           │     common  →  1c     │
│                                       │     useful  →  4c     │
│  QUEST ITEMS (not for sale)          │     bio     →  6c     │
│    · Distress Beacon                 │     energy  → 12c     │
│    · Scanner Mk III (uninstalled)    │                       │
│                                       │                       │
│  ACTIONS                                                     │
│   ► Sell COMMON minerals  (127 → 127 credits)                │
│     Sell USEFUL minerals  (28  → 112 credits)                │
│     Sell BIO-data         (14  → 84 credits)                 │
│     Sell ENERGY crystals  (3   → 36 credits)                 │
│     Sell ALL minerals     (= 359 credits total)              │
│     Back to Station                                          │
│                                                              │
│  [Up/Down nav · A confirm · B back]                          │
└─────────────────────────────────────────────────────────────┘
```

**Update flow**:
- Player picks "Sell X" → cargo[X] = 0, credits += sold amount. Floater text "+N credits" briefly.
- Player picks "Sell ALL minerals" → all four mineral types sold, single floater.
- Quest items NEVER sellable — they're shown for inventory awareness but have no Sell action attached.
- Buying is a separate UI (Ship Customization handles that — see below). Trade is sell-only.

**Read/writes**:
- Reads: `game.cargo` (the shared cargo dict — needs to be promoted from PlanetSurfaceScene-local to Game-level; currently `PlanetSurfaceScene.cargo` is scene-local. Promote to `game.cargo: dict[str, int]` so it persists across scenes), `game.flags["council_credits"]`
- Writes: same — decrements cargo, increments credits

**Implementation notes**:
- The Trade scene needs `game.cargo` to be a persistent dict on Game (analogous to `game.flags`). Add this in `engine/game.py` next to `game.flags`. Initialize empty.
- PlanetSurfaceScene's existing `self.cargo` should sync to `game.cargo` on liftoff. Today PlanetSurfaceScene tracks cargo per-visit; it should read from + write to `game.cargo` instead, so multi-planet collection trips accumulate
- Trade has no item-by-item sell (no "sell 5 of these 127"); it's all-or-nothing per type. Simpler UI, faster decisions

## 2. Ship Customization Scene

**Class**: `ShipCustomizationScene` in `src/scz/station/customization.py` (new).

**Entry**: Station menu → "Upgrade ship" → ShipCustomizationScene. B returns to StationScene.

**Layout** (two-column with module-list + ship-state):

```
┌─────────────────────────────────────────────────────────────┐
│  SHIP CUSTOMIZATION  ·  Furling Scout                        │
│                                                              │
│  SHIP STATS                  │  AVAILABLE MODULES            │
│                              │                               │
│  Hull HP        100          │   ► Scanner Mk III  ★quest    │
│  Shield HP      80           │     (Sensor slot, +scan)      │
│  Top speed     220           │                               │
│  Turn rate     3.0           │     [Tier-1 modules]          │
│  Fuel max     100            │     · Fuel Tank +50  (60c)    │
│                              │     · Shield Booster (90c+5U) │
│  SLOTS                       │     · Beam Mod (75c)          │
│                              │                               │
│   Hull       Standard        │   [Tier-2 modules]            │
│   Drive      Standard        │     · Quasi-Drive (180c+8E)   │
│  ►Weapon     Standard Beam   │     · Sa-Matra Lance (locked) │
│   Sensor     [empty]         │                               │
│   Field      [empty]         │   [Quest rewards waiting]     │
│   Crew #1    [empty]         │     · Hyperspace-Echo Sensor  │
│   Crew #2    [empty]         │     · Bio-Architect (Mycon)   │
│                              │                               │
│   credits: 412               │                               │
│                                                              │
│  [Up/Down nav · Left/Right column · A install · B back]     │
└─────────────────────────────────────────────────────────────┘
```

**Flow**:
- Left column shows ship state: installed modules per slot, plus current effective stats
- Right column shows available modules — sorted Quest > Tier-1 > Tier-2 > Locked. Each has price + resource cost
- Player selects a module on the right → the matching slot is highlighted on the left
- A confirms install. If the slot is occupied, uninstall the current one first (it returns to inventory)
- Removing a module returns it to inventory (no penalty)
- Quest-reward modules show a ★ badge and have zero cost

**Update flow**:
- On install:
  - Module's `cost_credits` deducted from `game.flags["council_credits"]`
  - Module's `cost_resources` deducted from `game.cargo`
  - Module installed: `game.ship_modules[slot] = module_id`
  - Ship stats recalculated: `game.ship_stats[stat] = base + sum(module.deltas)`
- On uninstall:
  - Module returned to `game.uninstalled_modules` (inventory)
  - Slot cleared: `game.ship_modules[slot] = None`
  - Stats recalculated

**Read/writes**:
- Reads: `game.ship_modules`, `game.uninstalled_modules`, `game.flags["council_credits"]`, `game.cargo`, module catalog
- Writes: same — installs change `game.ship_modules` and stat derivations

**Module catalog**: lives in `src/scz/content/modules.py` (new). Schema:

```python
@dataclass
class Module:
    id: str
    name: str
    slot: str                   # "hull", "drive", "weapon", "sensor", "field", "crew"
    tier: int                   # 0 = quest-reward, 1 = standard, 2 = advanced
    cost_credits: int           # 0 for quest-reward
    cost_resources: dict[str, int]  # e.g. {"USEFUL": 5}
    deltas: dict[str, float]    # what stats this changes
    description: str            # one-line for the UI
    locked: bool = False        # quest-gated visibility
```

**Tier-1 modules** (purchasable from the start; pad the Trade-economy with a meaningful sink):
- Fuel Tank +50 (Drive slot, +50 fuel_max, 60 credits)
- Shield Booster I (Field slot, +20 shield_max, 90 credits + 5 USEFUL)
- Beam Mod I (Weapon slot, +2 primary_damage, 75 credits)
- Cargo Pod +50 (Hull slot, +50 cargo_max, 50 credits)

**Tier-2 modules** (gated by Bio-Architect or quest-reward):
- Quasi-Drive Compact (Drive slot, enables Quasi-Space portal use without Sage gift — alternate path, 180 credits + 8 ENERGY)
- Sa-Matra Lance Replica (Weapon slot, **locked** — unlock requires specific Defender-faction quest progress, not slice-scope)

**Quest-reward modules** (zero cost, gated by quest completion flags):
- **Scanner Mk III** — `game.flags["scanner_mk3_in_cargo"]` (Sensor slot, +sensor_range)
- **Hyperspace-Echo Sensor** — `game.flags["slylandro_quest_complete"]` (Sensor slot, +Other-detection range)
- **Mantle-Resonance Bio-Architect** — `game.flags["mycon_bio_architect_received"]` (Crew slot, +tractor_beam_radius, +lander_replication_speed)
- **Rainbow Resonator** — `game.flags["resonator_blueprint_received"]` (Field slot, *required* for the slice climax Rainbow seeding action)

The Crew specialist slots (Archivist, Bio-Architect, Warden, Tunneler) are crew-class modules: they fit in the two Crew slots and provide passive bonuses. They are **NOT redshirts** — see [furling-tech-mechanics.md §5](furling-tech-mechanics.md). Crew never die.

## 3. Bio-Archive Scene

**Class**: `BioArchiveScene` in `src/scz/station/archive.py` (new).

**Entry**: Station menu → "Bio-Archive" (new menu item added once any artifact is collected) → BioArchiveScene. B returns to StationScene.

**Purpose**: shows the player what they've collected — Archive entries are the visible-progress system. Most quest rewards drop a one-line entry here. The Archive is also where the Distress Beacon, Resonance Record, Mmrnmhrm Archive Excerpt, etc. live for re-viewing.

**Layout** (categorized list with detail pane):

```
┌─────────────────────────────────────────────────────────────┐
│  FURLING BIO-ARCHIVE                                         │
│                                                              │
│  CATEGORIES               │  ENTRIES                         │
│                           │                                  │
│  ► SPECIES (4)            │   ► Slylandro Observer          │
│    ARTIFACTS (2)          │     (Beta Corvi, fmt 4-6m drift)│
│    COUNCIL (1)            │   · Arilou Sage (Outpost)        │
│    THE OTHERS (1)         │   · Mycon biot (Epsilon Scorpii) │
│                           │   · proto-human (Sol III)        │
│                           │                                  │
│  ENTRY DETAIL                                                │
│                                                              │
│   "Slylandro Observer.  Witnessed Beta Corvi  upper          │
│    troposphere.  4-6 meter drift body, translucent           │
│    silicone-rich membrane.  Plural 'we' speech.              │
│    Self-naming via witnessed weather phenomena.              │
│    Pacifist; cannot defend if attacked.                      │
│                                                              │
│    Disposition: awe high. Last contact: 2 cycles ago."       │
│                                                              │
│  [Up/Down nav · Left/Right column · A view detail · B back] │
└─────────────────────────────────────────────────────────────┘
```

**Categories** (per [stubs.py:ArchiveScene](D:/Aaron/development/star-control-precursors/src/scz/scenes/stubs.py)):
- **SPECIES** — every alien encountered, growing list. Includes proto-species observations
- **ARTIFACTS** — every quest-reward item received (Distress Beacon, Resonance Record, Cloaking Satellite blueprint, etc.). Re-watchable cinematics (e.g. the Distress Beacon can be replayed from here)
- **COUNCIL** — recommendations made and their outcomes; faction-standing history
- **THE OTHERS** — accumulated evidence and testimony — grows with each Androsynth / Chenjesu / Mmrnmhrm encounter

**Entry data model**:
```python
@dataclass
class ArchiveEntry:
    id: str
    category: str        # "species" / "artifact" / "council" / "others"
    name: str
    short_desc: str      # one-line summary for the list
    long_desc: str       # multi-paragraph detail body
    flags_gating: list[str]   # game.flags that must all be True for this to appear
    cinematic_id: str | None = None   # if non-None, A on entry replays a cinematic
```

**Catalog** lives in `src/scz/content/archive_entries.py`. Populated as the player progresses. Initial slice content:

| Entry | Category | Gating flag |
|---|---|---|
| Slylandro Observer | species | `game.flags["met_slylandro"]` |
| Arilou Sage | species | `game.flags["met_arilou_sage"]` (already implemented via dialog) |
| Mycon Biot | species | `game.flags["met_mycon"]` |
| Proto-Ur-Quan | species | `game.flags["observed_proto_uq"]` |
| Proto-Qor-Ah | species | `game.flags["observed_proto_qa"]` |
| Androsynth Refugee | species | `game.flags["met_androsynth"]` |
| Mmrnmhrm Sentinel | species | `game.flags["met_mmrnmhrm"]` |
| Chenjesu Collective | species | `game.flags["met_chenjesu"]` |
| Proto-Human | species | `game.flags["observed_proto_human"]` (Sol III observation) |
| Distress Beacon | artifact | `game.flags["has_distress_beacon"]` — REPLAYABLE cinematic |
| Resonance Record | artifact | `game.flags["has_resonance_record"]` |
| Mmrnmhrm Archive Excerpt | artifact | `game.flags["has_mmrnmhrm_excerpt"]` |
| Slylandro Cloak Blueprint | artifact | `game.flags["slylandro_cloak_active"]` |
| Hyperspace-Echo Sensor Pattern | artifact | `game.flags["has_echo_sensor"]` |
| Rainbow Resonator | artifact | `game.flags["has_rainbow_resonator"]` |
| Council Recommendation: UQ/QA | council | `game.flags["uplift_recommendation_made"]` |
| The Others — early ripples | others | `game.flags["heard_about_others"]` |
| The Others — decursion attack | others | `game.flags["has_distress_beacon"]` |
| The Others — prior cycles | others | `game.flags["has_resonance_record"]` |
| The Others — rift sighting | others | `game.flags["saw_orz_rift"]` |

Long-form descriptions for each entry should be drawn from the existing lore docs verbatim where possible — the Archive is the in-game version of those docs.

## Implementation Order

1. **Promote `game.cargo` and `game.flags["council_credits"]`** to engine layer. Update PlanetSurfaceScene to read/write `game.cargo`. Small refactor; no scene-author changes
2. **Module catalog** (`src/scz/content/modules.py`) — pure data file, no scene work
3. **TradeScene** — sells minerals, returns credits. Wire StationScene's "Trade resources" menu item to launch it
4. **ShipCustomizationScene** — installs modules, derives stats. Wire StationScene's "Upgrade ship" menu item
5. **Effective ship stats** — `game.ship_stats` derivation function: base Furling Scout stats + sum of installed module deltas. Used by combat (when player-controlled) and by anywhere that shows ship stats
6. **Archive entry catalog** (`src/scz/content/archive_entries.py`) — pure data file
7. **BioArchiveScene** — categorized list view. Wire StationScene with new "Bio-Archive" menu item (visible once any artifact collected)

## Test Harness Considerations

Add harness verbs (optional):
- `expect_cargo(type, value)` — check `game.cargo[type] == value`
- `expect_credits(value)` — check `game.flags["council_credits"] == value`
- `expect_module_installed(slot, module_id)` — check `game.ship_modules[slot] == module_id`

These help test the Beat 5 flow precisely.

## Out of slice scope

- Buying minerals (only selling)
- Module crafting (only purchasable + quest-reward)
- Module trading with other stations (only Mh-Lai trades for the slice)
- Faction-priced modules (Persuader gives diplomatic modules at a discount — Phase 5+)
- Archive search / filter (slice has small enough entry count that linear nav is fine)
