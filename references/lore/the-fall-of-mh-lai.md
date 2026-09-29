# The Fall of Mh-Lai

> The slice's biggest single emotional beat. Authored 2026-05-17 per
> Aaron's brief: *"a very emotional scene in the mid-point of the game
> where The Others find the council and consume the Furling home
> planet."*
>
> Phase 3.5 of the [Migration Timetable](migration-timetable.md) — the
> Others arrive **earlier than expected** and strike Mh-Lai first.
> Forced-acceleration event. Cannot be prevented. The player's choice
> is *how much can be saved* and *whether they witness from close or
> from far.*

## Canonical premise

The Furling Hider faction has been measuring dimensional ripples at
the cluster edge for years. Their best estimate had the Others
arriving in our cluster *toward the end of the slice* — well after
the Migration vanguard had departed and most evacuation logistics had
completed.

**That estimate was wrong by approximately six months.**

The Others have arrived early. They have *followed an Other-ripple
the Council itself was investigating* — a single careless Hider-faction
research probe sent into the cluster's outer halo, sniffing for
detection-threshold data. The probe pinged. The Others tracked the
ping back to its origin. **Mh-Lai is the origin.**

When the Steward learns of the approach, **the Furling Council is in
session at Mh-Lai.** Halia is presiding. The entire senior leadership
of the cluster's Persuader / Defender / Hider sub-factions is in the
chamber. The Cleansers had recused themselves from this particular
session (an internal-doctrine dispute) and are off-world; this turns
out to matter.

The Steward is **not at Mh-Lai**. They are somewhere else in the
cluster — wherever the current quest beat had them — and they cannot
get back in time to do more than *witness* and *choose how much they
witness from how close*.

## Trigger conditions (Design contract)

Suggested gating (Design refines):
- `tutorial_complete=True`
- `flag:has_distress_beacon=True` *(the Steward must already understand what the Others ARE)*
- `flag:systems_visited >= 5` *(slice midpoint cadence)*
- AND any one of: `flag:slylandro_decision_made=True` OR `flag:mycon_decision_made=True` *(at least one big slice-species decision has been processed; the player has had a "real" mission)*

When all conditions met → the scene auto-triggers at the next hyperspace traversal (the Steward's sensors pick up the dimensional ripple approaching Mh-Lai). The trigger CANNOT be deferred — once detected, the Steward must respond now.

## The Scene — five beats

### Beat 1 — The Detection (forced)

The Steward is in hyperspace, mid-route to wherever they were
going. The Hyperspace-Echo Sensor (or any equivalent Others-detection
module) **pings hard**. A large, slow, structured dimensional
signature is approaching the cluster center. The display shows the
trajectory unambiguously: **inbound on Mh-Lai**.

The ship's comm comes alive. **It is Halia.** Brief, calm, urgent.
She knows. She tells the Steward.

### Beat 2 — Halia's First Transmission

> **Commander Halia, Mh-Lai Council chambers, broadcast on the
> Persuader-priority channel**:
>
> *"Steward. They are coming. The Hider probes confirmed it twenty
> minutes ago. The Council is sealed in the chamber; we have triggered
> the planetary evacuation protocols. The Migration vessels are at
> standby orbit and will accept Council members and senior staff. Some
> will reach them. **Most will not.***
>
> *Whatever you are doing right now — finish it. Or come back. Either
> is acceptable. I will not pretend the choice is easy. The math is
> the math: by the time you reach Mh-Lai, the windows will be small.*
>
> *If you come: I am in the Council chamber. Find me. We will reach
> a vessel together if we can.*
>
> *If you do not come: I am still in the Council chamber. The work
> continues. Migrate. Go.*
>
> *I love you, Steward. I have been your commander. I have been your
> friend. Either way — keep going."*

### Beat 3 — The Decision

The Steward chooses. The choice is **time-constrained** (Design:
~60 real-time seconds of pause-able decision window; if the player
times out, the *don't-race* branch defaults).

**Branches** *(see canonical FSM in quest spreadsheet)*:

- **Race to Mh-Lai (high-effort)** — break the current trajectory,
  burn through fuel reserves, slam the Quasi-Drive if available;
  arrive ~20 minutes before the Others; aboard the Council chamber;
  fight to evacuate Halia + ~30% of the Council. Successful evacuation
  preserves Persuader leadership through the Migration. **Tense
  combat-and-dialog sequence; ship damage taken; high cost; high
  payoff.**
- **Race but accept it will be too late** — burn for Mh-Lai but the
  math doesn't work; arrive in orbit *as Mh-Lai is being consumed*;
  witness directly; Halia's last transmission is broadcast from the
  burning chamber. The Steward sees what the Others do *up close.*
  Mid payoff: an Archive entry of unprecedented detail and the
  Steward's own personal grief-as-fuel.
- **Do not race; honor the Migration timetable** — stay on current
  trajectory; finish the current beat as planned; Halia's last
  transmission arrives via long-range comm. The Steward grieves
  from a distance. The Furling Council is gone. Most senior Persuader
  leadership dies in the chamber. The slice continues with the
  Steward as one of the most-senior surviving Persuader voices.
  This is **the canonical "you accepted the math" branch.**
- **Cleanser-aligned acceleration variant** — only available if
  Cleanser standing ≥ 3 AND the Steward had previously authorized
  any Cleanser-pre-emption action: the Cleansers had **already**
  evacuated themselves AND some senior Persuaders pre-emptively
  (citing the Hider probe risk). Halia is *off-world* on a Cleanser
  vessel. She survives. **But Cleanser doctrine now controls the
  Council remnant.** The Persuader faction's voice collapses into
  Cleanser supervision for the rest of the slice. Halia is alive
  and *miserable.* This branch is canonically the worst surviving-
  Halia outcome.

### Beat 4 — The Fall (cinematic)

Regardless of the branch, **Mh-Lai falls.** The cinematic plays:

- The dimensional ripple approaches Mh-Lai's outer halo
- The atmosphere flickers — a brief planetary aurora as the Others
  cross the threshold into our space
- The atmosphere goes *dark* in waves as the Others' substrate
  intersects the planet's biosphere; cognition extinguishes en masse
- The Council chamber's last data transmission cuts mid-broadcast
- The Migration vessels in standby orbit pull away — silent;
  unprotected; carrying what they could
- Mh-Lai's surface continues to *unmake* itself for hours; orbital
  observation shows the canonical Others-aftermath (no debris field;
  no rubble; the planet is *less than it was*, smoothed over by the
  Others' passage)
- The Steward's ship (wherever they are) receives the news; the
  comm cuts to **silence**

This is the slice's quietest cinematic by design. **Humor doctrine
ZERO.** The Steward's wit options are unavailable throughout the
fall and for several beats afterward.

### Beat 5 — The Aftermath (gameplay-state)

- **Mh-Lai Station is gone.** All Mh-Lai-only services (Trade,
  Customization, Bio-Archive, the install-gate for tier-1+ modules)
  transfer to a **Migration Flagship** — canonically the *Furling
  Migration vessel **Hearth-of-Iron***, commanded by whoever is
  senior in the Persuader-vessel chain by this point. Mev-Tar
  Lwen-Tar (Yelena's mother) is canonically aboard Hearth-of-Iron;
  she has moved the Unzervalt tooling there; the install-gate
  service continues.
- **The Common Room weight shifts.** The Steward's bunk corner is
  now their *only* home. Bond-objects in the Common Room carry
  additional weight. The crew's reaction to Mh-Lai's fall plays out
  in the next Common Room visit (specific banter per crew below).
- **Migration vessels become the new home base.** The hyperspace
  HUD reflects the new docking-point. The Mh-Lai system in
  slice-cluster.md flags as `mh_lai_destroyed=True`.
- **Quest-state pre-checks update.** Any future Council scene that
  would have referenced Halia must now check `halia_alive=True/False`
  and `halia_status` (free-Persuader / Cleanser-supervised / dead).
- **The Migration timetable accelerates.** Phase 4 (Last-Wave) is
  effectively now — every remaining Precursor-aligned species must
  evacuate ASAP. Quest beats that would have happened in Phase 4
  trigger in compressed time.

## Crew reactions in the Common Room (next visit after fall)

Each named crew reacts in their own register. The Common Room becomes
*acoustically quieter* than usual; the canonical fur-muting effect is
*heavier* in the post-fall mood.

- **Mraka** — at her alcove window, looking at the dark spot where
  Mh-Lai used to be. *"They came here. To us. Not to a species we
  warned about. To us. I — Steward, did Halia survive?"* (Branch-
  responsive)
- **Bren-Vor** — seated still on his bunk, weapons-cleaning kit
  *closed* for once. *"Velt-Ra would have had a firing solution.
  She would have... I would have... we don't have one. The doctrine
  doesn't apply here."* He is *not okay.* Heavy beat.
- **Yelena** — at her workbench, but not working. Her tools are
  *still*. *"Mev-Tar is on Hearth-of-Iron. She — she sent a
  message. She's safe. The Unzervalt tooling moved with her.
  Twelve-Forty-Eight is the last hull built at Unzervalt now.
  Steward — Twelve-Forty-Eight is the LAST."* (Quiet pride and
  quiet grief.)
- **Mira-Rou** — at her amphora, holding it carefully. *"My
  ancestors made things here. The Halve-Tel labs are gone. The
  fragment in this amphora is — it may be the last biot-fragment
  of its lineage in this galaxy. I will carry it. I will arrive
  with it. We will continue."* (Steady; quietly fierce.)
- **Tarven** — surrounded by log-readers, but the readers are
  *off*. *"Seven prior Stewards. Their archives were at Mh-Lai.
  They are gone now. I have the local copies. I have... I have
  most of them. But the ones I didn't copy — they are gone. The
  prior Stewards are *gone*."* He is shaking slightly. The eternal
  tea-cup is empty.

If **Sevreth's Child is alive**: chemical-signal humming in the
amphora is rapid, urgent — Mira-Rou translates: *"Sevreth's Child
asks what happened. I have explained. Sevreth's Child is sad. I
am sad with Sevreth's Child."*

## Halia's canonical fate (per branch)

| Branch | Halia outcome | Persuader faction effect |
|---|---|---|
| **Race + evacuate (success)** | Alive; on Hearth-of-Iron; commands Migration completion | Strong Persuader leadership; positive epilogue |
| **Race + too late** | Dies on Mh-Lai chamber; final transmission heard | Persuader leadership transfers; emotional fuel for Steward |
| **Don't race** | Dies on Mh-Lai chamber; final transmission heard from afar | Same as above; Steward did not bear witness up close |
| **Cleanser-acceleration** | Alive on Cleanser vessel; **politically captured**; transmits formally only | Persuader faction collapses into Cleanser supervision |

## What this scene does for the slice

- **Establishes the Others as concrete and personal.** Until now the Others have been *theoretical* or witnessed-through-other-species-deaths. Now they have killed the Steward's *home*. The slice's stakes become *the Steward's stakes*.
- **Accelerates Migration urgency.** The remaining species-quests' clocks tighten. Players who were dawdling now feel pressure. Players who were rushing now feel justified.
- **Tests faction allegiance.** The Cleanser-acceleration branch reveals the *cost* of high Cleanser-standing in the most painful way — *they saved your commander, but they took the Persuader voice with her.*
- **Anchors the Migration epilogue.** Whatever Halia's fate, the slice's Andromeda-arrival epilogue references this moment. The Furlings who arrive in Andromeda *carry Mh-Lai with them*.
- **Sets up the Common Room as memorial.** The room is *now* the home; before this it was the ship. The shift is mechanical (services transfer) and emotional (the room means more).

## What does NOT change

- The Steward's own ship survives.
- The Common Room is intact (it's on the Furling Scout, not on Mh-Lai).
- The slice's species quests continue — they just compress in available time.
- The Migration **completes** to Andromeda regardless. The Fall of Mh-Lai is *catastrophic*, not *terminal*.
- The Steward continues to be the slice's protagonist and decision-maker.
- The Cleanser-acceleration branch does NOT end the slice; it just makes the rest of it *worse*.

## Cross-references

- [migration-timetable.md](migration-timetable.md) — Phase 3.5 added with this event
- [slice-cluster.md](slice-cluster.md) — Mh-Lai system #1 — post-fall flag `mh_lai_destroyed=True` should be respected
- [crew-common-room.md](crew-common-room.md) — Common Room mood shifts post-fall; crew banter per above
- [crew-recruitment-quests.md](crew-recruitment-quests.md) — Yelena's Last Hull quest references Mev-Tar's transfer to Hearth-of-Iron post-fall
- `tools/quest_inventory.csv` — `the_fall_of_mh_lai` quest encodes the FSM
- HANDOFF dispatches at the same date for Image (cinematic frames), Audio (silence + Halia's transmission), Design (scene trigger + Migration-vessel-as-new-base + service-transfer)
