# Economy and Trade Loops

> Companion to [furling-tech-mechanics.md](furling-tech-mechanics.md). Establishes the slice's three-vendor economy and the **return-home schematic loop** that gives the player a continuous reason to visit Mh-Lai Station. Authored 2026-05-17 (Lore chat).

## Premise

The slice has a deliberately tight economy with **three vendor niches that do not overlap**:

| Vendor | Niche | Currency | Installation |
|---|---|---|---|
| **Mh-Lai Station** (home) | Ship mods + allied-species ships + schematic consumption | Credits + minerals + schematics | Mh-Lai only |
| **Melnorme** (super-giant traders) | Sensor upgrades + lander-hardening | BIO-cargo | In-field, instant |
| **Allied species** | Their own quest-reward modules | Quest-completion | In-field, at the species' location |

The non-overlap is intentional: the player never has to ask "*which vendor* should I check?" — each vendor has a clear and distinct catalog. The architecture also enforces a soft **return-home loop** without resorting to SC2's "drag the player back to base every game-week" pattern. The player goes home **when they want to install a new mod**, and that's the only place they can do it.

## The Mh-Lai Niche — Home Station

**Mh-Lai sells**:
- **Ship mods** — all hull / drive / weapon / field modules at tier 1 and above. The full library of permanent ship upgrades. This is the *only* place to acquire ship mods. The catalog grows as the player turns in schematics.
- **Allied species ships** — once the Steward has earned alliance with a species, that species' canonical ship hull becomes available for purchase at Mh-Lai. The player's Furling Scout remains the primary; allied ships are alternate-loadout options for specific missions. (See *Allied Species Ships* below.)
- **Schematic conversion** — the Schematic Vault sub-screen consumes a schematic from the player's hold and unlocks its corresponding mod for purchase. One schematic, one unlocked mod, gone.

**Mh-Lai is the only place ship mods can be installed.** This is the slice's most distinctive economic constraint. The lore frame:

> Furling fabrication is precision-tight. Compatibility tolerances on a modular Scout are measured in fractions of a wavelength. The shipyard fabricators at Mh-Lai are individually calibrated to every Scout that has ever flown out of Unzervalt's factory floor — they remember each hull. A field-fitted mod will mis-seat by a hair and the ship will be down-tuned for the rest of its career. The Stewards joke: *"My ship knows when she's home."* They are not entirely joking.

This applies to tier-1 and tier-2 modules (the purchasables). **Tier-0 quest-reward modules are exempt** — those are pre-installed by the quest-giving species using *their* fabrication discipline (Slylandro atmospheric integration, Mycon biological growth, Arilou dimensional precision). Mh-Lai's tight-tolerance rule is for Furling-shipyard work specifically.

## The Melnorme Niche — Super-Giant Traders

**Melnorme sell**:
- **Sensor upgrades** — pattern sensors, range extenders, anomaly scanners, life-signature filters. Already canon: `MELNORME_PATTERN_SENSOR` (boosts Others detection + dialog context depth). Future entries: Melnorme-grade variants of the bio-sense, enemy, anomaly, and hazard scanners.
- **Lander-hardening upgrades** — sub-system modules that increase lander survival on hostile planets. Lander armor, hazard shielding (lava / lightning / biological), tractor-beam improvements that don't fall under the Mycon Mantle-Resonance lineage. These are *not* ship mods — they're lander-system mods, a separate sub-system that doesn't share the tight-tolerance rule and can be field-fitted on the spot.

**Melnorme do NOT sell**: ship mods (weapons, shields, hull, drive, field). They sell *sensors* (which slot into the sensor slot and are field-installable, like quest-rewards) and *lander-hardening* (which slots into the lander sub-system, also field-installable).

**Currency**: BIO-cargo, per the canonical Melnorme entry in `project_melnorme.md`. No credits, no minerals other than BIO. The Melnorme will hand-wave the trade — "we will assist your sensoring; we accept your living things." Lore frame: they need biological material for their own dimensional-pattern research.

**Travel cost**: Melnorme are at super-giant stars, which are rare and far from Mh-Lai. A trip to a Melnorme trader is a deliberate side-jaunt, not a routine stop. The player goes when their BIO-cargo hold is full and they want a sensor upgrade.

## The Schematic Loop — the *go home* reason

This is the loop that makes the slice's return-home cadence work.

**Field acquisition**: schematics drop from multiple sources:
- **Quest rewards** — most species quests grant a schematic in addition to (or in place of) a direct module install. Example: completing the Slylandro Cloaking Satellite quest gives the Steward a *Hyperspace-Echo Sensor schematic*, which is consumed at Mh-Lai to unlock the sensor in the catalog (rather than the quest delivering the sensor pre-installed).
- **Salvage** — drifting Furling-era installations (rare), Cleanser caches (high-risk), abandoned Migration ships (limited).
- **Trade with proto-species** — very rare; some proto-species accidentally hand the Steward a schematic-grade artifact while interacting (e.g., a proto-Yehat tool that the Furling fabricators recognize as a *grav-hammer schematic* in seed form).
- **Bio-Archive payments** — completing certain witnessing quests (Taalo Shield, Burv Caster, Veils Falling) pays out as a schematic from the Hider faction's research fund.
- **Cleanser bargaining** — siding with Cleansers on a particular issue can yield a Cleanser-faction weapons schematic the player would otherwise never see.

**Storage**: schematics occupy a small `schematics` collection (NOT cargo — they don't take hold space). They don't decay. They can be carried indefinitely.

**Conversion at Mh-Lai**: in the Schematic Vault sub-screen, the player selects a schematic, confirms, the schematic is consumed, and the corresponding mod becomes available in the Customization shop catalog. The mod still costs credits + minerals to buy and install — the schematic is the *unlock*, not the purchase itself. This separates "I have the *blueprint*" from "I have the *resources to build it*."

**Why the loop works narratively**:
- Every schematic has a *story origin* — "I picked this up from Coel Tessar's data cache" or "I salvaged this from a Persuader-faction wreck near the Furling-fur-and-relics installation at $SYSTEM$." Each install at Mh-Lai is therefore a small moment of *the Steward's accumulated history showing up on the ship*.
- Schematics are tradeable currency between Furlings — the Steward can sometimes *gift* a schematic to a Furling faction in exchange for standing, deepening the slice's social texture.
- Some schematics are *unique* — only one drops in the slice — which makes the choice of "which mods do I unlock?" a real one if the player has too few schematics to unlock everything.

## Allied Species Ships (Mh-Lai catalog extension)

**Premise**: once the Steward has earned alliance with an alien species, that species' canonical ship hull becomes available for purchase at Mh-Lai. The player can swap out of the Furling Scout for missions where the allied hull's combat profile is better suited.

**Lore frame**: the allied species sends a representative hull (or hull-blueprint that Mh-Lai's fabricators can build to spec) to the home station as a gesture of alliance. The Steward keeps the Furling Scout as their primary; the allied ship is a second hull, garaged at Mh-Lai, available for specific missions.

**Eligible species (slice list)**:
- **Slylandro** — *Slylandro Lift* (post-cloak quest). A gas-bag atmospheric-lifter design, slow but durable, with a Slylandro consultant aboard for atmospheric-encounter missions.
- **Arilou** — *Arilou Skiff* (post-Sage's-gift, separate from the Quasi-Space portal). Already canonical from `ship-roster.md`. Quasi-Space-evasion defense layer.
- **Androsynth** — *Androsynth Refugee Fighter* (post-Distress-Beacon, only if refugees were stabilized). Glass-cannon design, shear-hardened hull.
- **Mmrnmhrm** — *Mmrnmhrm Sentinel* (post-Archive-Excerpt + optional cognitive-upgrade). Pure-hull, no shields, defensive doctrine; *uniquely* available to the Steward as a tribute hull.
- **Burvixese** — *Burvixese Skipper* (post-Caster-Reckoning, only if the Steward advocated pre-activation evacuation; otherwise the Burvixese are too dead to send a hull). Four-armed cockpit, high-amplitude broadcast jamming as a defensive layer.
- **Thinn** (renamed from *Planar* 2026-05-17) — *Thinn Blade* (only if the Steward witnessed and helped with their edge-on-alignment strategy; status of the alliance is *pending* by slice end, but Mh-Lai will conditionally fabricate the hull if asked). Already canonical from `species-the-thinn.md`.

**Ineligible species (no ships in our era)**:
- **Chenjesu** — rooted; no ships.
- **Taalo** — non-mobile mountain-substrate biology + Eliminated by slice end.
- **Utwig** — devolved by choice; their pre-doctrine ships exist but are sealed; the slice canonically does not offer them.
- **Mycon biots** — biological terraformer-organisms; not piloted as fighting ships.
- **Proto-species (proto-Ur-Quan, etc.)** — pre-sentient; no ships.

**Cost**: allied species ships cost significantly more credits than ship mods + may require a Mh-Lai-specific schematic + faction standing prerequisites. They are mid-to-late-slice content. The Furling Scout remains the primary; allied ships are *flavor choices*, not optimal play.

## Design Rationale

This three-vendor split solves several problems at once:

1. **Distinct vendors, no confusion.** A player never asks "which shop has this?" — they know weapons are at Mh-Lai, sensors are at Melnorme, quest-rewards are in-field.
2. **Return-home reason without grind.** The schematic loop pulls the player back to Mh-Lai *when they have something to install*, not on a calendar. Every return is meaningful.
3. **Schematic-as-narrative-anchor.** Each unlock at Mh-Lai is a tiny moment of "the Steward shows up holding a story." The Customization scene becomes a memorial of the Steward's adventures, not just a stat-tuning UI.
4. **Mh-Lai keeps mattering.** Without this architecture, Mh-Lai's role drops sharply after Beat 5 (tutorial completion). With it, every new schematic the player earns is a small "go home" pull.
5. **Allied-species-ships as alliance reward.** Adds a tangible, *mechanically interesting* reward for alliance beyond standings and dialogue.
6. **Melnorme has a clear niche.** Sensors + lander-hardening — both *non-ship-mod* sub-systems, both genuinely useful, both worth the trip to a super-giant. Melnorme do not compete with Mh-Lai because they sell *different categories of upgrades*.

## Slice Implications (for Design chat)

- **New scene**: `src/scz/station/schematic_vault.py` — the Mh-Lai sub-screen for converting schematics → unlocked mods. Catalog of unspent schematics, "use" action consumes one and unlocks its target mod in `MODULES` catalog visibility.
- **New content module**: `src/scz/content/schematics.py` — `Schematic` dataclass with `id`, `name`, `description`, `target_module_id`, `source_origin` (lore text), `rarity`. Plus a `SCHEMATICS: dict[str, Schematic]` registry.
- **New game state**: `Game.schematics: set[str]` (or list) tracking the Steward's held schematics. Persists across saves.
- **Mh-Lai customization filter change**: tier-1 and tier-2 mods become *hidden* from the shop until their `unlock_schematic` flag is met. This is a new field on `Module` — `unlock_schematic: str | None = None` — analogous to the `UNLOCKED_BY: recruited_<role>` convention for crew, but enforced as data not just a comment.
- **Mh-Lai installation gate**: the ship-mod install path (`ShipCustomizationScene.install_module`) checks `game.location == "mh_lai_station"` before installing tier-1+ modules. Tier-0 quest-reward modules pass-through (no gate). Crew modules are installed at Mh-Lai by definition (recruited there).
- **Melnorme module catalog narrowing**: `MELNORME_PLASMA_LANCE` is **out-of-canon** (Melnorme don't sell weapons in this canon). Design-chat to either (a) retire the entry, (b) relocate it to Mh-Lai with tier-1 + cost, or (c) reframe it as a *schematic that the Melnorme sells* which then gets consumed at Mh-Lai. Recommended path: (c) — turn it into `schematic_furling_coil_lance` sold by Melnorme for BIO-cargo, which then unlocks a Mh-Lai-buyable weapon. This preserves the Melnorme's lore role as an exotic-tech broker while honoring the home-station install rule.
- **Lander-hardening sub-system**: a new module category needed. Possible structure: a new `lander_armor` slot (parallel to `sensor`), with modules like `MELNORME_LANDER_ABLATIVE_HULL`, `MELNORME_LANDER_HAZARD_SHIELD`, `MELNORME_LANDER_TRACTOR_FOCUSER`. All tier-1+, BIO-cargo cost, field-installable.
- **Allied-species-ship purchases**: gate on faction-standing or quest-completion flags. Stored in `MODULES` as ship entries (or a separate `SHIPS` registry — likely cleaner). Mh-Lai sells these as "fly out in a different hull" rather than installable modules.
- **Existing tier-0 quest-reward modules** (Scanner Mk III, Hyperspace-Echo, Mantle-Resonance Bio-Architect, Rainbow Resonator) are exempt from the Mh-Lai install rule — they're pre-installed at the quest's location, per the lore-frame exemption above. No code change needed for these.

## Schematic Catalog (suggested — Lore-chat-authored stubs)

The slice should have approximately 10-15 schematics, each with a clear *source* and *target*. Initial catalog:

| Schematic ID | Source (in-fiction) | Target Module Unlock | Rarity |
|---|---|---|---|
| `schematic_furling_coil_lance` | Melnorme trade (BIO-cargo) | A Mh-Lai-buyable mid-tier energy weapon (replaces retired `MELNORME_PLASMA_LANCE`) | Common |
| `schematic_dimensional_armor` | Coel Tessar's hull-fragments (Androsynth Beacon quest) | Hull mod: +shear-resistance | Uncommon |
| `schematic_pulse_cannon` | Salvaged at the Slylandro Cloaking Satellite worksite | Weapon mod: high-cadence pulse cannon | Common |
| `schematic_quasi_field_projector` | Arilou Sage's gift (in addition to QS portal) | Field mod: quasi-space evasion | Uncommon |
| `schematic_shield_capacitor` | Persuader-faction reward for full Beacon-dissemination | Field mod: shield max +40 | Common |
| `schematic_mantle_resonator_mk2` | Mycon gift after the Deep Child Whisper quest | Crew mod variant: enhanced Bio-Architect | Rare |
| `schematic_chenjesu_resonance_skin` | Chenjesu Resonance Record quest | Hull mod: crystalline armor (resonance dampening) | Rare |
| `schematic_mmrnmhrm_sentinel_core` | Mmrnmhrm Archive Excerpt quest | Drive mod: defensive-loop autopilot | Uncommon |
| `schematic_taalo_substrate_fragment` | Taalo Shield Tragedy quest (any "help" branch) | Field mod: substrate-resonance shield (rare anti-Others ping reduction) | Rare; unique |
| `schematic_burv_broadcaster_node` | Burvixese Caster Reckoning quest (any branch where Caster activates) | Hull mod: comm-amplifier (cluster-wide dialog range) | Uncommon |
| `schematic_utwig_veil_optic` | Utwig Veils Falling quest (witnessed cleanly) | Sensor mod: signal-dampening sensor (low-amplitude detection) | Rare |
| `schematic_furling_warden_armor` | Defender-faction reward for siding with them at a key vote | Hull mod: high-armor variant | Common |
| `schematic_cleanser_pulse` | Cleanser-faction reward for siding with them at a key vote | Weapon mod: heavy disruptor | Common; faction-gated |
| `schematic_hider_camo` | Hider-faction reward for high cognitive-dampening telemetry contributions | Field mod: low-emissions cloak (passive) | Rare |
| `schematic_furling_drive_mk3` | Furling-relic installation drop (rare in-cluster salvage) | Drive mod: top-tier hyperspace efficiency | Rare |

Catalog is illustrative; final balance is Design-chat's. Each schematic's `description` field (Lore-chat-authored) should narratively connect the source to the target. The Schematic Vault sub-screen should surface the lore-text prominently — players who care will read it; players who don't can skim and convert.

## Authoring Priority (matches slice-arc priority)

1. **Schematic registry + Mh-Lai Schematic Vault scene** — Design-chat scaffolds the framework; Lore-chat populates the descriptions.
2. **Melnorme catalog narrowing** — retire `MELNORME_PLASMA_LANCE`, add lander-hardening stubs (~3-5 stubs initially).
3. **Tier-1 ship-mod gate** — extend `Module` with `unlock_schematic` field; filter `purchasable_modules()`.
4. **Mh-Lai install gate** — `ShipCustomizationScene` checks `location == "mh_lai_station"` for tier-1+ installs.
5. **Allied-species-ship registry** — new content module + Mh-Lai catalog UI; gates on alliance flags.
6. **First schematic landings in quest content** — start with the Slylandro Cloak satellite and Coel Tessar's hull-fragments (Beat 5-6 content).
