# The Crew Common Room

> The canonical physical space aboard the Furling Scout where the
> recruited crew lives, eats, sleeps, argues, and is *encountered* by
> the Steward outside of mission-active dialog. Authored 2026-05-17
> (Skippy creative pass) per Aaron's brief: *"a whole crew gathering
> spot in the ship and images for that, and a way to chat and
> interface with the crew."*
>
> **Cross-references**: [crew-recruitment-quests.md](crew-recruitment-quests.md) for backstories + side-quests; [the-furlings-and-the-others.md §1](the-furlings-and-the-others.md) for the Furling fur-everywhere aesthetic that applies in full here; HANDOFF dispatches at `HANDOFF_design_chat.md` (scene+UI), `HANDOFF_image_chat.md` (visuals), `HANDOFF_audio_chat.md` (ambient + banter).

## Why the Common Room Matters

Without a Common Room, crew are abstract stat-bumps. With one, they
are **characters the player knows**. The Common Room serves four
overlapping purposes:

1. **Discovery** — when a crew member's side-quest goalpost-triggers,
   the player has somewhere to *find them* and hear them ask
2. **Personality showcase** — between missions, crew banter at the
   table; ambient lines that reveal personality without taking up
   mission-critical dialog space
3. **Slice-content reflection** — the room accumulates *physical
   objects* as the slice progresses (Bren-Vor's journal on his bunk,
   Mira-Rou's amphora on the medbay-window shelf, Yelena's family
   photo from the Unzervalt launch, Mraka's recovered Drifter-trophy,
   Tarven's prior-Steward logbooks). The room becomes a *memorial of
   the player's choices*
4. **Bond-deepening** — the player CAN initiate non-mission dialog
   with any crew member at any time. The Common Room is where you go
   when you want to *talk to* someone, not just *task* them

## Physical Layout (canonical)

The Common Room is the **central social hub** of the Furling Scout's
habitable section. Approximately 8m × 5m × 3m. **Single shared
space** with five named-crew alcoves arranged around the perimeter,
plus a central long-table with bench seating for the whole crew at
once, plus a Steward's bunk corner (the player's own bed).

### Furling fur aesthetic (canonical)

Per the slice's *"aesthetic-of-the-fur"* canon, EVERY touched surface
in the Common Room is **fur-covered**:

- Bench seating: long-luxurious-shag pile (mammoth/musk-ox texture)
- The central table: short-dense-pile fur on the surface (mole/otter)
- Light fixtures: translucent pale-fur diffusers ("for proper diffusion")
- Walls: long shag along the upper third (decorative); short pile on
  handhold-height grips (functional)
- The Steward's bunk: ceremonial-soft-underfur (status comfort)
- The five crew alcoves: each wears its own regional/personal fur
  palette (see per-crew below)

### Five named-crew alcoves

Each recruited crew member has a small personal alcove (~1.5m × 1.2m)
with their bunk, a personal shelf for bond-objects, and the canonical
*posture-they-occupy* when in the Common Room.

#### Mraka Yenn-Sa's Pilot Alcove (port-forward corner)

- **Posture**: standing at the alcove's small window, looking out at
  whatever hyperspace pattern is currently outside
- **Bunk fur**: weathered umber pile (Drifter-Circuit colors)
- **Bond-objects** *(accumulate as slice progresses)*:
  - Default: small Drifter's Circuit medal-display (her three cluster-cup wins)
  - After Last Race side-quest favorable: Soren Kel-Var's drive-fix
    component (a saved-piece-of-his-ship she keeps as a *reconciliation
    artifact*); also a small Olwen-Veth clan-marker (gift from Soren)
  - Always: small framed *un-named* family portrait (the Olwen-Veth clan
    she failed to save; she will not name them aloud)

#### Forward's OR Bren-Vor's Weapons Alcove (starboard-mid corner) — shared slot

> **Canon 2026-05-17**: the weapons-officer alcove is occupied by **either Forward (Thinn rebel) OR Bren-Vor Telcas (Furling Aimer)**, mutually exclusive per crew-slot. Whichever is recruited occupies this alcove. Their bond-objects and posture differ entirely.

#### Forward's variant (if `recruited_weapons_officer_thinn=True`)

- **Posture**: standing FORWARD-FACING (the only Thinn ever to refuse edge-on; this is canonically his entire identity); his iridescent teal-violet-gold ribbon-body shifts slowly as he watches the Common Room
- **Alcove fur palette**: standard Furling fur on the base surfaces, BUT **the alcove has been adapted for him** with an iridescent-mineral wall-panel he installed (Thinn-aesthetic overlay on the Furling base); his bunk is a vertical resting-rack (Thinn don't sleep horizontally) with soft pale fur on the contact-edge
- **Bond-objects**:
  - Default: a diagram of his "perpendicular reality" doctrine, hand-drawn by him on a paper sheet (incomprehensible to anyone but him; consists of arrows pointing in seven directions and a small handwritten note that reads *"this one"*)
  - Default: a single shed Thinn ribbon-fragment from his pre-rebellion days at Spire (iridescent; this is canonically *his last connection to we-who-watch*)
  - Default: his "Forward" emblem — a single arrow pointing forward; just one; *not multiple, not multi-directional*
  - After Forward's side-quest favorable (confrontation branch): a small Spire-rock the troupe gave him as parting gift; ALSO the two additional Thinn ribbon-bodies (We-Who-Watch-The-Far-Slope and We-Who-Watch-The-Lower-Bench) sharing his alcove, standing edge-on per their preserved doctrine while Forward stands forward-facing
  - After Forward's side-quest favorable (quiet-goodbye branch): a folded paper-letter from his old troupe in canonical multi-Thinn-collective handwriting; the letter is addressed *"to Forward"* without any plural form
  - Always: his self-coined name on the alcove plate — just *"Forward"* — single word

#### Bren-Vor's variant (if `recruited_weapons_officer=True AND NOT recruited_weapons_officer_thinn`)

- **Posture**: seated on his bunk-edge, weapons-cleaning kit deployed,
  cleaning a kinetic-rifle component he has cleaned eighty-seven times
- *(The rest of Bren-Vor's section follows; preserved from original canon)*
- **Bunk fur**: short-dense pile in muted grey-blue (Defender colors,
  retained though he transferred to Persuader; canonically he kept the
  cloak)
- **Bond-objects**:
  - Default: Velt-Ra Telcas's photograph (face turned slightly away from
    the camera — she didn't like having her photo taken; canonical)
  - After Aimer's Verdict favorable: Velt-Ra's journal, closed and
    placed on the shelf with a small Persuader pin on top — *"I keep it
    closed now"*
  - Always: a *single firing-rule notebook* containing thirty-two pages
    of personal annotations on combat-restraint scenarios

#### Yelena Lwen-Tar's Mender Alcove (starboard-aft corner)

- **Posture**: at her workbench (canonically the densest object-cluster
  in the Common Room), repairing or modifying something small (a coil,
  a sensor, a coffee maker the Steward broke)
- **Bunk fur**: cinnamon-and-cream pile (Lwen-Tar family colors)
- **Bond-objects**:
  - Default: family photograph (Mev-Tar Lwen-Tar + Yelena as a child
    holding a wrench almost as big as her arm)
  - After Last Hull side-quest favorable: a fragment of the Unzervalt
    factory floor (the *last fragment of the last Scout's cradle*); also
    her father Korven's tool-belt buckle (the only personal item that
    survived the coolant accident)
  - Always: seventeen alphabetized specialized tools in a rack — *"in
    alphabetical order"* she will defensively note

#### Mira-Rou Halve-Tel's Bio-Architect Alcove (port-aft corner)

- **Posture**: at her medbay-window observation post, taking notes on
  whatever the ship is currently passing through; her glass amphora is
  on the shelf in clear view
- **Bunk fur**: soft white-and-pale-green (Bio-Architect colors)
- **Bond-objects**:
  - Default: the glass amphora containing her heirloom biot-fragment
    (faint sub-aural humming canonical); a portrait of her great-
    grandmother Olune Halve-Tel
  - After Deep Child's Cradle (suppress branch): the amphora's hum is
    again normal-quiet; Mira-Rou has framed a Furling Hider citation
    for the cognitive-substrate research her work has informed
  - After Deep Child's Cradle (allow-emergence): the amphora is now
    Sevreth's Child's *home* — a tiny bioluminescent presence is
    visibly alive inside; Mira-Rou has begun keeping a translation-log
    of Sevreth's Child's chemical signals
  - Always: a small portable shear-repair fab pattern (canonical
    medical equipment)

#### Tarven Olwen-Sa's Star-Reader Alcove (port-forward-mid corner)

- **Posture**: seated cross-legged on his bunk with at least two
  log-readers open, reading at high speed; occasionally muttering
  cross-references aloud
- **Bunk fur**: deep brown shag (Archivist family colors)
- **Bond-objects**:
  - Default: the seven prior-Steward portrait miniatures (a row of
    framed faces with full clan suffixes — *"In the seventh decade of
    Steward Iren-Vor's tenure—"*)
  - After Erased Logs (report-to-Council favorable): Iren-Vor Olwen-
    Veth's recorded-voice cache is on the shelf — the full data,
    proudly displayed
  - After Erased Logs (keep-secret): the cache is on the shelf, but
    with a small physical lock-seal (his and Steward's secret)
  - Always: an inexhaustible supply of tea cups (Tarven canonically
    drinks tea relentlessly)

### Central long-table

The eating + arguing space. Capacity ~8 (full Furling crew plus 2
visitors). When the player approaches the table, **whichever crew are
currently chatting will be visible** and the player can sit and listen,
join, or move on.

The table's surface has accumulated *small carved name-marks* from
prior-Steward crews — Tarven points out each one when asked, with full
clan suffix.

### Steward's bunk corner

The player's own bed. Furred ceremonial-soft-underfur. The shelf above
the Steward's bunk accumulates *the slice's milestone artifacts* — the
Distress Beacon recorder, the Mantle-Resonance Bio-Architect spare,
the Rainbow Resonator (once acquired), etc. The Common Room is also
where the player can *review* the Bio-Archive in narrative format if
they prefer (a more *room-like* alternative to the Mh-Lai Bio-Archive
scene).

### Generic-crew rotating residents

The three shop-buyable crew (Archivist, Warden, Tunneler) share a
*rotating bunk* in the Common Room's secondary alcove. Only one is
present at a time (whichever the Steward has currently installed).
Their posture is generic-crew default; they don't have personal bond-
objects but they do have small *role-specific tools* in their alcove
(Archivist: a portable Council-logger; Warden: a Defender-training
weights-rack; Tunneler: a Quasi-Space portal-pattern oscilloscope).

## Interaction Flow

### Approaching a crew member

The Steward walks/menus into the Common Room. Each present crew is
visible at their alcove or the central table. The player approaches a
specific crew member; a **"TALK"** prompt appears; pressing the
interact button opens that crew's dialog FSM.

### Side-quest goalpost trigger

When a crew member's side-quest goalpost prereqs are met (e.g.,
`systems_visited >= 5` for Mraka, `modules_installed >= 4` for
Yelena), a **notification badge** appears on that crew's alcove —
a small "!" rendered alongside the crew portrait. The player knows to
go talk to them. The badge clears when the side-quest's `q_<role>_sq_start`
is entered.

### Non-mission ambient banter

When the player enters the Common Room without selecting a specific
crew member, **ambient banter** plays among whichever crew are
currently present. Banter content is **per-encounter-varying** (per
the slice's variation principle — never repeats identically). Banter
is canonical-personality flavored:

- **Mraka + Yelena** (if both aboard): technical-detail conversation
  about hyperspace navigation efficiency; Mraka teaches Yelena
  Drifter-circuit math; Yelena corrects Mraka's coffee-maker repair
- **Bren-Vor + Mira-Rou** (if both aboard): quiet shared-grief
  conversations (he about his sister, she about her ancestors); they
  recognize each other's weight without naming it
- **Tarven + ANY**: Tarven reading aloud from a prior-Steward log,
  losing track of the original question, being gently redirected
- **Any + Sevreth's Child** (allow-emergence branch): chemical-signal
  conversations Mira-Rou translates ("Sevreth's Child finds your
  voice... amusing? I think the word is *amusing*")

### Initiating personal dialog

The player can initiate **non-mission dialog** with any crew member at
any time. The crew member responds with personality-appropriate
content — Mraka with technical advice or Drifter stories; Bren-Vor
with quiet observation; Yelena with whatever she's currently fixing;
Mira-Rou with biological context for whatever the player just
encountered; Tarven with prior-Steward annotations relevant to current
location.

This is the slice's **bond-deepening surface**. Players who linger and
talk to their crew between missions get a richer slice; players who
just complete missions still get the full quest content.

## Common Room as Slice-Long Memorial

By slice end, the Common Room has accumulated:
- All bond-objects from completed side-quests
- The Steward's milestone artifacts on the bunk-shelf
- Carved name-marks from this Steward's run on the central table
- A *quiet sense of having been lived in*

When the Migration begins, the Common Room departs intact — the
Furling Scout carries her crew and her accumulated history into
Andromeda. This is the slice's most *physically* hopeful image:
*the room you've lived in becomes the room you arrive with.*

## What does NOT belong in the Common Room

- **No combat content** — the room is the *safe space*
- **No quest-FSM blocking content** — side-quests trigger HERE but
  the actual quest gameplay happens elsewhere (Soren's stranded ship,
  the Council hearing, Unzervalt factory, Mycon biot site, fringe-
  system data-cache)
- **No Furling Council formal scenes** — those happen at Mh-Lai
  station or designated Council-chamber settings
- **No alien encounters** — alien NPCs do not visit the Common Room
  (the room is *Furling-only* canonically)
- **No Steward-protagonist personal-quarters scene** — the Steward
  lives IN the Common Room; they don't have a separate bedroom
