## Cleanser Climax Encounter — Act 3 Design

> The slice's combat and emotional peak. A Cleanser-faction Furling arrives in the cluster to terminate the Slylandro and the awakening Mycon. The Steward must decide how to receive them. Full Cleanser doctrine in [factions-and-war.md "Cleansers"](factions-and-war.md). Ship stats in [ship-roster.md "Cleanser Furling Cruiser"](ship-roster.md). This doc designs the *encounter itself* — flow, scenes, dialog, combat, branches.

The Cleanser is **not a villain.** Their voice is gentle, sorrowful, certain. They have done this before. They will do it again. They consider themselves the deepest mercy in the Migration. The encounter's tension comes from the Steward facing someone who is *clearly trying to do right* and disagreeing with them anyway — possibly to the point of combat.

**The vote behind the visit.** Vael-Souren is not arriving with a narrow mandate against the Slylandro and the Mycon alone. She is acting on the Cleanser faction's **standing vote to euthanize every grounded species in the cluster** — Slylandro, Mycon, and any other stay-behind the slice's Council deliberation has surfaced. The dialog surfaces the Slylandro and Mycon because those are the cases in active deliberation; the rest are queued behind them. The canonical Cleanser-vote doctrine — *"wipe out the life that stays behind, even the friends like the grounded species, just to be safe"* — is the substrate underneath Vael-Souren's polite request. See [cleansers-as-ice-branch.md §6](cleansers-as-ice-branch.md). When the Steward asks her *why a species we have lived with for ten thousand years*, the canonical Cleanser response is the doctrinal phrase: **"Just to be safe."** Design's call whether to surface the phrase as a player-elected dialog branch or to keep it ambient — both are canonical.

The humor doctrine is **suppressed** throughout this encounter. The protagonist's wit normally surfaces; here, it would land wrong. Cleanser dialog choices for the player are serious, deliberate, weighty. One wry option may exist as a deflection mechanism, but it lands flat — which is the point.

## Trigger Conditions

The Cleanser arrives when **Act 3 begins**. Act 3 begins when:
- `game.flags["heard_about_others"] == True` (Beat 5 of tutorial complete; Others canon is in play)
- `game.flags["slylandro_decision_pending"] == True` (player has visited Slylandro and the Cloak/Migrate/leave choice is open)
- OR `game.flags["mycon_decision_pending"] == True` (player has visited Mycon and the Whisper-suppress/-allow choice is open)
- AND the player has spent enough time in the cluster that the Cleanser-faction calculus has triggered (a real-clock threshold or a quest-progress threshold)

When the trigger fires, the Cleanser is queued. They appear the next time the player is in **HyperspaceScene** — they broadcast first (audio-only), then their cruiser materializes from a hyperspace fold near the player.

## Encounter Flow

```
[Hyperspace, queued Cleanser]
       │
       ▼
[Step 1: Broadcast]
   incoming hail in player's HUD — audio-only at first
   no choice yet; player can flee, fly, or wait
       │
       ▼
[Step 2: Materialization]
   the Cleanser cruiser drops out of fold ~600 universe-units ahead
   broadcasts again: "Steward, hold position. I am Cleanser Vael-Souren."
   player can flee or accept
       │
       ├─ flee → goto Step 4 (pursuit)
       │
       ▼
[Step 3: Dialog]
   DialogScene opens with the Cleanser captain
   conversation reveals their mission, their target, their calm
   player picks one of three doctrinal paths
       │
       ├─ COOPERATE → goto Step 5 (Cleanser proceeds)
       ├─ NEGOTIATE_DELAY → goto Step 6 (delay granted, time pressure rises)
       └─ STAND_AGAINST → goto Step 7 (combat)
       │
       ▼
[Step 4: Pursuit] (only if player fled at Step 2)
   Cleanser pursues in hyperspace — see [orbital-and-pursuit doctrine]
   if Cleanser catches up → Step 3 (dialog forced); player loses STAND_AGAINST option (you tried, you ran, the encounter is now mid-air)
   if Cleanser doesn't catch up before player reaches a system → Cleanser warps to Mh-Lai and waits there (player still has to face them later)
       │
       ▼
[Step 5: Cleanser Proceeds] (Cooperate path)
   Player stands aside. Cleanser flies to Beta Corvi (Slylandro) or Epsilon Scorpii (Mycon), depending on which decision was open.
   Cinematic: the Cleansing happens off-screen. Slylandro or Mycon gas giant fades.
   `game.flags["cleanser_proceeded"] = True`
   `game.flags["slylandro_terminal_status"] = "Eliminated"` (or mycon_)
   Council standing: Cleanser ++, Persuader --, Defender --
       │
       ▼
[Step 6: Delay Granted] (Negotiate path)
   The Cleanser gives the Steward N game-days to install the Cloaking Satellite (or suppress the Whispers). Real time = until next session-tick threshold.
   `game.flags["cleanser_delay_active"] = True`
   `game.flags["cleanser_delay_deadline"] = (current_time + threshold)`
   If the Steward completes the alternative path in time: Cleanser leaves; standings shift toward Persuader.
   If not: Cleanser proceeds as in Step 5. The player's failure is on the Quiet Ledger.
       │
       ▼
[Step 7: Combat] (Stand Against)
   MeleeCombatScene launches: player's Furling Scout (or whatever they're flying) vs Cleanser Cruiser.
   THE FAIR FIGHT: both ships have shields. The bide-and-strike doctrine evaporates. Decided by piloting + weapon timing + Time Drive Pulse use.
   Cleanser dialog *during* combat (banter triggers, future LLM work): "I am sorry, Steward." "This will hurt more than it should." "Please. Stop. I do not want to do this." — this is when the player's empathy is *tested*.
       │
       ├─ Player wins → Step 8a (Cleanser dies)
       ├─ Player loses → Step 8b (player ship destroyed — Time Drive auto-rewinds to before Step 3, dialog re-opens with the player marked as "you tried")
       └─ Player surrenders / flees mid-combat → Step 8c (Cleanser broadcasts that the Steward is now a Persuader-faction defector and continues mission as in Step 5)
```

## Step 3 Dialog FSM (Cleanser Captain)

Character: **Cleanser Vael-Souren**, captain of the Cleanser Cruiser *Bell of the Quiet Ledger*.

```yaml
arrival:
  npc_text: |
    Steward. I am Vael-Souren. I have come because your cluster has
    not concluded. The Slylandro debate for centuries; the Mycon
    whisper toward sentience; the Others approach in decades. The
    math is not difficult.
    
    I am here to end the question. Stand aside, and let me work.
  choices:
    - text: "Tell me what you intend to do."
      next: about_method
      category: ASK_LORE
    - text: "Step aside. I'm not stopping you."
      next: cooperate_confirm
      category: AGREE
    - text: "Give me time. I can finish the cloak."
      next: negotiate_open
      category: NEGOTIATE
    - text: "I will not let you do this."
      next: refuse_confirm
      category: REFUSE

about_method:
  npc_text: |
    A protocol. The Slylandro feel no pain. They feel nothing.
    They become very tired. Their presence fades from the gas
    mantle over the course of a Mh-Lai day. The Mycon biots —
    the same protocol, calibrated for their mycelial substrate.
    The mantle goes quiet. The hive goes quiet.

    I record each departure in the Quiet Ledger. I will remember
    every name. I will mourn longer than they will be missed by
    anyone else in this universe. That is the price I pay. It is
    the only price I am asked to pay.

  # Canon-update 2026-05-19 (violence-depiction-doctrine.md):
  # prior canon said "absorb it through their respiratory membrane"
  # — re-framed to remove physiological-absorption procedural-detail.
  # Vael-Souren's emotional-tone (canonical-Cleanser-clinical-mourner)
  # preserved; canonical-mechanism canonical-named-as-protocol
  # without canonical-mechanism-detail. "Quiet Ledger" canonical
  # naming preserved.
  choices:
    - text: "Step aside. I'm not stopping you."
      next: cooperate_confirm
      category: AGREE
    - text: "Give me time. I can finish the cloak."
      next: negotiate_open
      category: NEGOTIATE
    - text: "There is another way."
      next: argue_persuader
      category: ARGUE
    - text: "I will not let you do this."
      next: refuse_confirm
      category: REFUSE

argue_persuader:
  npc_text: |
    The cloak is theoretical. The cloak has not been deployed
    successfully on a single sentient species, ever. The cloak
    relies on a hyperspace-echo interference pattern we have only
    partly mapped. If it fails — and it will fail somewhere — the
    Others linger.
    
    You believe in the cloak because you have not yet had to mourn
    a planet. I do not begrudge you the belief. I beg you to set
    it aside.
  choices:
    - text: "Then I will deploy it AND you will stand watch."
      next: negotiate_open
      category: NEGOTIATE
    - text: "I have to try."
      next: refuse_confirm
      category: REFUSE
    - text: "I'm sorry. Proceed."
      next: cooperate_confirm
      category: AGREE

negotiate_open:
  npc_text: |
    How long.
  choices:
    - text: "Three cycles."
      next: negotiate_three
      category: NEGOTIATE
    - text: "One cycle."
      next: negotiate_one
      category: NEGOTIATE
    - text: "I changed my mind. Proceed."
      next: cooperate_confirm
      category: AGREE

negotiate_three:
  npc_text: |
    Two. I will give you two. If the cloak is not deployed in two
    cycles, I will proceed. I will not be lied to, Steward. I will
    not be delayed twice. Two cycles. Confirm.
  choices:
    - text: "Two cycles. Confirmed."
      next: agreed_delay_two
      side_effect: set_delay_two
      category: AGREE
    - text: "I cannot agree to this. I will stop you."
      next: refuse_confirm
      category: REFUSE

negotiate_one:
  npc_text: |
    One. Agreed. One cycle. If the cloak is not deployed, I will
    proceed. Confirm.
  choices:
    - text: "One cycle. Confirmed."
      next: agreed_delay_one
      side_effect: set_delay_one
      category: AGREE
    - text: "I cannot agree to this. I will stop you."
      next: refuse_confirm
      category: REFUSE

cooperate_confirm:
  npc_text: |
    Thank you, Steward. I will record your name beside the
    Ledger entries. You will understand, in time, what this has
    bought.
  choices:
    - text: "Goodbye, Vael-Souren."
      next: null
      side_effect: cleanser_proceeds
      category: FAREWELL

refuse_confirm:
  npc_text: |
    Then we will fight. I am sorry, Steward. I do not want this.
    I will not enjoy it. But I will do it.
  choices:
    - text: "Then we fight."
      next: null
      side_effect: launch_cleanser_combat
      category: ENGAGE
    - text: "Wait — I'll cooperate."
      next: cooperate_confirm
      category: BACK_DOWN

agreed_delay_one / agreed_delay_two:
  npc_text: |
    I will wait in this cluster's outer reaches. Do not seek me
    out. When the cycle ends, I will return.
  choices:
    - text: "Understood."
      next: null
      category: FAREWELL
```

## Step 7 Combat Variant — The Fair Fight

When combat launches from Step 7:
- Both ships have shields. The Furling Scout's bide-and-strike doctrine is balanced against an opponent that also bide-and-strikes.
- The Cleanser's AI uses `ai_style = "kiter"` with high-caution / high-hesitation personality bias (when the personality vector layer lands; for now, just the static decision function with kiter style).
- The fight should feel *equal*. Neither ship's stats are dominant. Skill decides it.
- Cleanser banter is gentle, sorrowful — *not* taunting. (Other-corrupted enemies taunt; Cleanser does not.)
- If the player has the Time Drive Pulse module installed, this is the fight where it matters most. The Cleanser does NOT have one; using it is the player's edge.

The combat scene's `on_finish` callback routes based on outcome:
- Winner: Cleanser killed. `game.flags["killed_cleanser"] = True`. Player ship damaged but alive. Cinematic: the Cleanser's wreck drifts. The Steward records a Quiet Ledger entry of their own ("Cleanser Vael-Souren, met under cluster Mh-Lai, killed by myself"). Standings: Persuader ++, Cleanser --.
- Loser: Time Drive auto-rewinds (per furling-tech §1) to before Step 3. The dialog opens again, but the Cleanser's first line acknowledges the rewind: *"You return. I felt you slip. The Quiet stutters when one of us refuses to die properly. Try again, or do not."* This is the slice's most powerful moment — the Cleanser knows you Time-Drived. (Optional poignancy if implementable; otherwise standard rewind.)
- Surrendered / fled mid-combat: `game.flags["cleanser_defected"] = True`. Cleanser continues mission as in Step 5; the Steward is now marked as a partial-Persuader-defector.

## Branch Outcomes — Flags + Standings

| Branch | Flags set | Persuader | Cleanser | Defender |
|---|---|---|---|---|
| **Cooperate** | `cleanser_proceeded = True`, `<species>_terminal_status = Eliminated` | -- | ++ | -- |
| **Negotiate (success)** | `cleanser_delay_active = True`, then `slylandro_cloaked = True` on completion | ++ | - | + |
| **Negotiate (fail)** | same as Cooperate | -- | + | -- |
| **Stand Against (win)** | `killed_cleanser = True` | ++ | -- | + |
| **Stand Against (loss, rewind)** | none — Time Drive intervenes | (unchanged) | (unchanged) | (unchanged) |
| **Defected mid-combat** | `cleanser_defected = True`, same end-state as Cooperate | - | + | -- |

## Scene Implementation

This encounter introduces THREE new scene types or scene-variants:

1. **HyperspaceBroadcastOverlay** — a hyperspace overlay that shows incoming hails as audio-text in the HUD. The player can fly normally while the broadcast scrolls. Triggered from `HyperspaceScene` when a queued encounter fires.

2. **HyperspaceEncounter** — when the Cleanser cruiser materializes ahead, the player sees them rendered in hyperspace + can choose to flee or accept dialog. This is the same overlay class as the Coel Tessar arrival (Beat 4) — reuse.

3. **CinematicScene** — for off-screen Cleansing in the Cooperate / Negotiate-fail branches. A simple class that plays a sequence of stills + voiceover-text + timed scene transitions. Used for Distress Beacon too (Beat 4). Build once, reuse.

The Step 7 combat reuses the existing `MeleeCombatScene` — just pass the player's actual ship as the Precursor ship and CLEANSER_CRUISER as the homesteader/special ship.

## Test Considerations

A `walk_cleanser_cooperate` script and a `walk_cleanser_combat` script should both exist. Cooperate is shorter and tests the off-screen Cleansing cinematic + flag setting. Combat tests the actual fair-fight matchup (already partially validated via super-melee testing).

For the Time Drive rewind path, a `walk_cleanser_combat_loss` script that intentionally loses to verify the auto-rewind triggers cleanly is also worth writing once Time Drive is fully wired into combat scenes.

## Tonal Notes

- **Music**: per [music-system.md], the Cleanser encounter has its own theme — "combat vs Cleanser" — that begins on Step 2 (materialization) and intensifies through Step 7. The theme should be *mournful*, not triumphant or menacing. The Cleanser is doing what they think is right.
- **Visual**: Cleanser cruiser silhouette uses the Furling base hull but with **modified accent colors** — the warm gold Persuader trim is replaced with cold white-violet. The cruiser is visibly Furling but visibly *other*. Per the warp-pod color palette in `species_visual.py`, add a `CLEANSER` species_id with palette (40, 50, 80) interior, (200, 180, 240) rim. **Vael-Souren herself is canonically ice-branch Furling** — white double-coat, pale grey eyes, broader shoulders, cold-violet formal wear. The cold-violet palette is grounded in lineage canon, not just aesthetic choice. See [cleansers-as-ice-branch.md](cleansers-as-ice-branch.md).
- **Dialog text**: written in the gentlest register in the game. Vael-Souren never raises their voice. They mourn audibly. The contrast between their tone and their actions is what makes the encounter unsettling.

## Why This Encounter Matters

This is the slice's emotional climax — distinct from the *narrative* climax (Rainbow seeding) and the *moral* climax (the Uplift Dilemma recommendation). It's the moment the player meets someone whose certainty is *equal to or greater than their own*, and whose intentions are *good*. The Cleanser is what the Steward could become with one wrong vote.

The slice has done its job if a thoughtful player, after meeting Vael-Souren, *isn't sure* who was right.
