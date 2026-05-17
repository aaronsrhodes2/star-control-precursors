# The Planar — *The Edge-On Invisible*

> A wholly invented Furling-era species, introduced 2026-05-16 from
> Aaron's premise: a two-dimensional sentient race with zero width.
> Body-plan, voice, ship mechanics, and faction alignment all flow from
> the single bizarre fact of their dimensional geometry — exactly the
> calibre of premise the Creative License section in
> `tools/gen_lore.py` is asking Gemini to match for new species.

## The Premise

The Planar are **literally two-dimensional.** A Planar individual is a
flat ribbon of iridescent biological membrane, several meters tall,
with **zero width** — viewed edge-on, they are invisible. Their entire
metabolism, cognition, and locomotion happen across a single
geometric plane.

How? *Nobody knows.* They appear to exist as a stable projection of a
higher-dimensional form into our 3D space — they themselves describe
their bodies as "the shadow of who we are." Furling xenophysiologists
have failed to even *measure* their thickness; the best instruments
report it as <1 Planck length, which is meaningless. They simply are
what they are.

## Body Plan

- **Form**: a vertical iridescent ribbon-sheet, ~2 meters tall, ~80cm
  across (the long axis), zero width (the perpendicular axis).
- **Color**: shifts through deep teal, royal violet, and gold-leaf
  yellow depending on viewing angle — like an oil slick or
  hummingbird feather. The shift is genuinely view-dependent (not
  pigment-based); it is a property of how their 2D structure refracts
  light.
- **"Face"**: along the ribbon's upper edge, a constellation of small
  dark optical points (8–16 of them, asymmetric per individual) that
  function as compound eyes. They have no mouth — vocalization is via
  membrane vibration of the entire ribbon.
- **"Arms"**: two planar appendages extending from the lower-mid
  edges, curving in graceful flat arcs like the edges of leaves. They
  manipulate objects by aligning their plane to the object and using
  the ribbon's surface tension.
- **Locomotion**: in air, they ride pressure differentials like sails.
  In space, they manipulate solar-wind ion pressure across their
  surface. They are *fast* in their preferred direction (broadside-to-
  flow) and basically immobile orthogonal to that direction.
- **Edge-on invisibility**: viewed perfectly along their plane, they
  cannot be seen, touched, or hit. Projectiles pass through their
  zero-width body. Lasers focused on the plane edge graze it without
  depositing energy. **This is the core combat fact.**
- **Slipstream**: the air or gas they're flying through deflects
  *around* their zero-thickness body, leaving visible vapor trails on
  either side of the ribbon. The slipstream gives away their position
  even when they're edge-on.

## Speech & Cognition

- **Voice**: vibration of the ribbon-membrane, producing a sound that
  is partly tonal, partly harmonic, like a glass instrument struck
  and then held. Furling translators render their speech as
  **second-person plural with collective verbs** — "We who are
  watching see you who are arriving" — because their cognition is
  distributed across the entire 2D surface and they do not have a
  singular "I"-axis.
- **Pronouns**: always plural ("we", "us") for self-reference; always
  collective ("you all", never "you") for addressees.
- **Tone**: contemplative, slow. They process visual input across
  their 2D field simultaneously, so their conversation has a
  *patient* quality — they have already considered all the angles you
  might present them with.
- **Quirk**: they reflexively turn edge-on when startled, briefly
  disappearing from sight. They will then re-orient when they have
  decided whether to engage. This is the equivalent of a Furling
  raising an eyebrow.

## Faction Alignment

**Homesteader (Stay-Side).** The Planar **cannot Migrate** — the
dimensional crossing involves a folding maneuver that would either
catastrophically destabilize their planar projection or, more likely,
delete it entirely. To survive the portal would mean leaving their
*shape* behind, and their shape *is them*.

They have known this for centuries. They have already accepted that
the Others will arrive and that they will die. They are not afraid.
They have prepared.

Their plan: **be edge-on when the Others look.** The Others sense
cognitive concentration; the Planar plan to suspend collective
cognition at the moment of arrival — pull their ribbon-bodies into
careful alignment with the Others' sensory axis, presenting
zero-cross-section to detection. Whether this works is unknown.
Furling Hider-faction researchers consider their plan **brilliant
or doomed in roughly equal proportion**.

## In the Slice

**Encounter location:** the Planar inhabit a single gas-rich
hydrogen-helium world ("Spire," a sub-Neptune in the slice cluster)
whose upper atmosphere has the pressure dynamics they require to
fly. Lower atmosphere is too dense; they would lose ribbon-stability.

**Encounter shape:** a polite, contemplative dialog with a Planar
elder ("We-Who-Witness-the-Edge"). They explain their plan. They
ask the Furling Steward to *not Migrate them* — they would die.
They ask the Furling Steward to *not interfere with their
edge-on suspension*. They thank the Steward for the courtesy of
having asked at all.

**Player choices** (per the slice's Convince/Intimidate/Dominate/
Eliminate/Cloak/Hide framework):
- **Honor their plan** — leave them alone; the slice records their
  fate as *Pending* (will they survive? unknown). Aligns Persuader.
- **Insist on Cloak** — install a Cloaking Satellite, suppressing
  their cognition. The Planar accept reluctantly. Their fate becomes
  *Cloaked*. Aligns Compeller (forced help is still help).
- **Cleanse** — they were doomed anyway; do it cleanly. Aligns
  Cleanser. (This is the canonically darkest option in the slice.
  Aaron's humor doctrine: the Planar make jokes about edge-on right
  up to the end. Their last words are "We have always already been
  half-gone. Thank you for the punctuation.")
- **Defender** — equip them with Talos-style amplifier tech to "be
  loud" alongside the Talos enclave. They politely refuse — they
  understand the Talos plan and consider it (literally) flat-out
  wrong. (Pun: theirs.)

**Award if visited:** Bio-Archive entry + a unique inventory item:
a single Planar shed-ribbon (a piece of their molted-edge that
preserves the iridescent shift). Decorative; possibly a Furling
Council gift item in a future increment.

## Ship Design

**The Planar Blade** (per ship-roster authoring schema).

- **Form**: a flat sail-craft, roughly elliptical, with the Planar
  pilot embedded along the sail's spine. The ship itself is also
  zero-width-along-one-axis, mirroring its pilots.
- **side**: homesteader
- **points**: ~110 (lower than Furling Scout's 130; the Planar Blade
  is a glass cannon)
- **hull_max**: 50 (very fragile)
- **shield_max**: 0 (no shields — they don't believe in defending
  what's already invisible enough)
- **top_speed**: 360 (very fast in preferred direction)
- **turn_rate**: 1.5 (slow turn — they're a sail, not an arrow)
- **acceleration**: 200
- **ai_style**: clever_flier (a new style for the AI module — they
  prefer broadside-to-target attacks at long range, then turn
  edge-on between volleys)

**Primary weapon — Planar Arc.**
A shotgun-like cone of plasma that emerges from the ship's leading
edge. **Wider and weaker the further it travels.** Close range it
is devastating (5+ pellets at full damage); long range it is a
gentle scattering (1 pellet at half damage). Damage rolls off with
distance — the opposite of most beam weapons. Reload is fast.

- primary_damage: 4 per pellet, 6 pellets per shot at close, 1 pellet
  at max range
- primary_energy: 4
- primary_rate: 1.5 shots/sec
- primary_range: 600 (but useful only at <300)
- primary_speed: 800 (slow plasma cloud)

**Special — Edge-Align.**
The Planar Blade turns instantly edge-on to its current heading,
becoming **immune to primary fire from any ship pointed at it from
directly ahead** for 2 seconds. During Edge-Align it cannot fire and
cannot turn. Costs 30 energy. Cooldown 8 seconds.
- **Tactical wrinkle:** the immunity is from the FRONT only. A
  flanker can still hit them. The Planar Blade's player/AI must
  consciously face the threat to use Edge-Align defensively, which
  also leaves them unable to retreat directly during the immunity
  window — they must roll out of it before reorienting.
- **Counter:** orbit the Planar Blade so you're never on its forward
  axis. Or, hit it with a high-projectile-spread weapon that arrives
  from multiple angles simultaneously.

**Lore note on ship colors**: hull_color matches the Planar's own
iridescence — teal/violet/gold shifting in render based on the
ship's facing angle relative to the camera. (Cosmetic only; doesn't
affect gameplay.)

## What the Planar Add to the Slice's Thematic Picture

Every species in the slice tests a different theory about how to
survive the Others' arrival. The Planar are the **geometric
solution** — survive by *being too flat to register*. They are the
non-obvious thematic counterpart to the Slylandro (suppress signal
chemically), Mmrnmhrm (defense doesn't work, accept fate
robotically), Chenjesu (be slow enough that you read as geology),
Talos (be loud enough that you read as too costly), and Mycon
(accidentally awaken into a new signal).

The Planar take the cognition-detection threshold *literally* —
they reduce their own cross-section to zero. Whether the Others
detect cognition by cross-section or by some other metric is the
unanswered question their fate will settle.

## Authoring Notes

- **Don't make them fragile-and-tragic.** They are *contemplative*
  and *accepting*. The Steward's grief at meeting them should come
  from the player, not from the Planar themselves.
- **Their humor is geometric.** "We are not afraid of dying — we
  have been mostly-nothing our whole lives." This is delivered
  warmly, not bitterly.
- **The ship's "Edge-Align" special is the gameplay-mechanical
  echo of their philosophy.** When the player fights one (or pilots
  one in Super-Melee), they feel the strategy first-hand.
- **Their portrait (already generated, Round 1):** vertical
  iridescent ribbon-body, optical-point face on the upper edge,
  slipstream curling around the figure, magenta aurora backdrop.
  See `assets/generated_drafts/firefly/tier1_portraits/species_planar_blade_portrait.png`.
- **Naming**: the slug `planar_blade` refers to both the species
  ("Planar") and their ship class ("Planar Blade" — the blade being
  their primary weapon AND the shape of their body). The species
  themselves are just "the Planar."
