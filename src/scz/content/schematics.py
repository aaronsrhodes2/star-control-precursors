"""Schematic registry — the *go-home* reason of the slice's economy.

Canon source: `references/lore/economy-and-trade-loops.md`
§Schematic Loop. The slice's central exploration-to-Mh-Lai loop is:

1. The Steward picks up a schematic in the field — quest reward,
   salvage, witness-payment, proto-species accidental gift, Cleanser
   bargain, etc. The schematic is stored in `game.schematics`.
2. The Steward eventually returns to Mh-Lai (the only place schematic
   conversion happens) and opens the Schematic Vault sub-scene.
3. The Vault lists held schematics; the Steward selects one + confirms.
4. The schematic is consumed: removed from `game.schematics`, its id
   added to `game.consumed_schematics`. The corresponding Module
   (matched by `Module.unlock_schematic`) now becomes visible in the
   shop catalog.
5. The Steward then purchases the unlocked Module at the
   Customization sub-scene with credits + minerals — the schematic
   is the *unlock*, not the purchase itself.

This separates "I have the blueprint" from "I have the resources to
build it" — and gives each Customization purchase a *story origin*
("the Coel Tessar data cache", "the Persuader wreck near $SYSTEM$").

**MVP catalog**: 5 schematics, paired with 5 new Modules in
`modules.py` (added in the same session). Future content can add
more — each new schematic just needs (a) a registry entry here,
(b) a Module with matching `unlock_schematic`, and (c) a path for
the player to pick it up (quest reward, salvage trigger, etc).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Schematic:
    """One schematic in the registry.

    Fields:

    - `id`: stable string used as the `Module.unlock_schematic` match
      key. Convention: `schematic_<target_mod_id>` so the relationship
      is grep-discoverable from either side.
    - `name`: short display label rendered in the Vault list
    - `target_module_id`: the Module id that this schematic unlocks
      when consumed (for cross-reference + UI display)
    - `rarity`: "common" / "uncommon" / "rare" / "unique" — drives
      visual hierarchy in the Vault list. Slice canon: most schematics
      are "uncommon"; a few "unique" entries exist for plot-tied unlocks.
    - `source_origin`: 1-2 sentence in-fiction blurb describing how the
      Steward came to hold it. Per canon §Schematic Loop bullet 1, this
      is *what makes the Customization scene a memorial of the Steward's
      adventures* — each install is a story moment.
    - `description`: short blurb on what the unlocked module does, in
      Furling-engineer voice
    """
    id: str
    name: str
    target_module_id: str
    rarity: str = "uncommon"
    source_origin: str = ""
    description: str = ""


# MVP catalog — 5 entries, paired with the 5 new Modules added to
# `modules.py` in the same session. Each id matches a Module's
# `unlock_schematic` field exactly.
SCHEMATICS: dict[str, Schematic] = {

    "schematic_furling_coil_lance": Schematic(
        id="schematic_furling_coil_lance",
        name="Furling Coil Lance schematic",
        target_module_id="furling_coil_lance",
        rarity="uncommon",
        source_origin=(
            "Sold by a Melnorme trader for BIO-cargo at a "
            "super-giant trade-stop. The Melnorme will not say "
            "where the lance design originated; canonical Melnorme "
            "register: *some questions are not on the manifest.*"
        ),
        description=(
            "A focused-coil weapon mod — replaces the Scout's "
            "primary beam with a high-precision lance pattern. "
            "Long-range, slow rate of fire, devastating on a clean "
            "lock."
        ),
    ),

    "schematic_dimensional_armor": Schematic(
        id="schematic_dimensional_armor",
        name="Dimensional Armor schematic",
        target_module_id="dimensional_armor",
        rarity="rare",
        source_origin=(
            "Recovered from a Persuader-faction wreck near Gamma "
            "Vulpeculae. Half the wreck was already inside the Orz "
            "Rift's dimensional bleed; the schematic was on the "
            "outside half, intact. The Steward retrieved it without "
            "comment."
        ),
        description=(
            "Hull mod — interleaves a thin dimensional-substrate "
            "layer through the Scout's primary armor. Reduces "
            "incoming damage by ~15%. The Hider faction approves."
        ),
    ),

    "schematic_pulse_cannon": Schematic(
        id="schematic_pulse_cannon",
        name="Pulse Cannon schematic",
        target_module_id="pulse_cannon",
        rarity="common",
        source_origin=(
            "Salvaged from a drifting Furling-era survey lifter "
            "near the Hearth. The lifter's crew is canonically "
            "long-evacuated; the schematic was in the captain's "
            "console drawer, tagged *spare copy*."
        ),
        description=(
            "Weapon mod — replaces the primary beam with a fast-"
            "cycle pulse-cannon pattern. Short range, high rate of "
            "fire. Reliable; not flashy."
        ),
    ),

    "schematic_mmrnmhrm_reinforced_plating": Schematic(
        id="schematic_mmrnmhrm_reinforced_plating",
        name="Mmrnmhrm Reinforced Plating schematic",
        target_module_id="mmrnmhrm_reinforced_plating",
        rarity="unique",
        source_origin=(
            "Gifted by archive consensus on the Steward's first "
            "visit to Ossuary. Sentinel-Aux Theta-Four presented "
            "the schematic personally. The First-Makers designed "
            "this plating; it did not save them, but the Mmrnmhrm "
            "believe the design is still good — *it was the "
            "engagement that was wrong, not the metal.*"
        ),
        description=(
            "Hull mod — patchwork-alloy reinforced plating in the "
            "Mmrnmhrm style. Heavier than standard armor but "
            "absorbs energy weapons especially well. Canonical "
            "First-Maker engineering."
        ),
    ),

    "schematic_arilou_phase_dampener": Schematic(
        id="schematic_arilou_phase_dampener",
        name="Arilou Phase Dampener schematic",
        target_module_id="arilou_phase_dampener",
        rarity="rare",
        source_origin=(
            "Slipped into the Steward's cargo manifest by Sage "
            "Lwen-Olou during the Quasi-Space portal gifting. The "
            "Sage did not announce it; the schematic appeared in "
            "the manifest after the meeting. The Steward did not "
            "comment; the Sage did not comment. Canonical Arilou "
            "register."
        ),
        description=(
            "Field mod — softens incoming projectile arrival by a "
            "fractional dimensional displacement. Damage reduction "
            "applies to specific projectile types; useless against "
            "beams. Subtle, like its source."
        ),
    ),

    # Schematic added 2026-05-18 to replace the prior `locked=True`
    # dead-code state of SA_MATRA_LANCE_REPLICA. The schematic itself
    # is granted by a future Defender-quest post-Final-Conflict
    # salvage handler (deferred); until that lands, this entry exists
    # so the Module's unlock_schematic reference resolves.
    "schematic_sa_matra_lance_replica": Schematic(
        id="schematic_sa_matra_lance_replica",
        name="Sa-Matra Lance Replica schematic",
        target_module_id="sa_matra_lance_replica",
        rarity="unique",
        source_origin=(
            "Recovered from a Defender-faction shipyard cache after "
            "the Sa-Matra Prototype's neutralization. The schematic "
            "is the lance's blueprint — not the lance itself, which "
            "exists in only one prototype and one replica. Canonical "
            "Defender register: *the blueprint is the legitimate "
            "inheritance.*"
        ),
        description=(
            "Weapon mod — replica of the Sa-Matra Prototype's primary "
            "lance. High damage per shot, slow cycle, requires "
            "considerable energy to maintain. The replica reads as "
            "the Defender doctrine in working hands."
        ),
    ),
}


def held_schematics(game) -> list[Schematic]:
    """Return the player's currently-held schematics (not yet
    consumed), sorted by rarity-then-name for stable display order.
    """
    held = getattr(game, "schematics", None) or set()
    out = [SCHEMATICS[i] for i in held if i in SCHEMATICS]
    # Rarity sort: unique → rare → uncommon → common (most-special
    # first); then name alphabetical within each tier
    rarity_order = {"unique": 0, "rare": 1, "uncommon": 2, "common": 3}
    out.sort(key=lambda s: (rarity_order.get(s.rarity, 4), s.name))
    return out


def consume(game, schematic_id: str) -> bool:
    """Consume a held schematic at the Vault — move from
    `game.schematics` to `game.consumed_schematics`. Idempotent: if
    already consumed, returns False; if never held, returns False.
    Successful consume returns True.
    """
    held = getattr(game, "schematics", None)
    if held is None or schematic_id not in held:
        return False
    held.discard(schematic_id)
    if not hasattr(game, "consumed_schematics") or game.consumed_schematics is None:
        game.consumed_schematics = set()
    game.consumed_schematics.add(schematic_id)
    return True


def has_held(game) -> bool:
    """True iff the player has any schematic in hand. Drives the
    Schematic Vault menu-entry visibility — hidden until the player
    has at least one to convert."""
    held = getattr(game, "schematics", None)
    return bool(held)
