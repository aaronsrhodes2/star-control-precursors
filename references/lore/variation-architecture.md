# Variation as a Layer — Architecture & Catalog

> The architectural form of the [three-pillar variation principle](the-furlings-and-the-others.md#9-the-three-pillar-variation-principle-the-games-core-design-philosophy). Documents the pattern, the catalog of variable elements, and why this is *easy* rather than hard.

## The Insight

Variation in Star Control Zero is not a feature woven through gameplay logic — it is a **cosmetic layer over a deterministic static engine**. The engine plays exactly like a 1990s 2D space game: fixed dialog FSMs, fixed ship stats, fixed planet generation, fixed combat physics. The variation layer sits *on top*, intercepting every render and audio output to produce something subtly different each time, *without changing what the engine does*.

This is what makes the whole approach tractable. The engine never has to know about variation. We can build the boring static engine first, ship it, then attach the variation layer incrementally. If the variation system breaks at any point, the game still plays — it just looks/sounds samey for a few hours until we fix it.

## The Pattern

```
                ┌───────────────────────────────────────┐
                │       Game Engine (deterministic)     │
                │   ┌────────┐  ┌─────────┐  ┌──────┐   │
                │   │ Dialog │  │ Combat  │  │Planet│   │
                │   │  FSM   │  │ Physics │  │ Gen  │   │
                │   └────────┘  └─────────┘  └──────┘   │
                │       │           │           │       │
                └───────┼───────────┼───────────┼───────┘
                        │           │           │
                        ▼           ▼           ▼
            ┌──────────────────────────────────────────┐
            │       Variation Layer (cosmetic)         │
            │   ┌────────┐  ┌──────┐  ┌─────┐  ┌────┐  │
            │   │  Text  │  │ Art  │  │Music│  │ FX │  │
            │   │ Render │  │Render│  │ Mix │  │Bake│  │
            │   └────────┘  └──────┘  └─────┘  └────┘  │
            │       │          │        │        │     │
            └───────┼──────────┼────────┼────────┼─────┘
                    ▼          ▼        ▼        ▼
                ┌──────────────────────────────────────┐
                │       Player Output (varied)         │
                └──────────────────────────────────────┘
```

The engine emits **semantic tokens**: "this NPC wants to express gratitude," "this ship is a Cleanser cruiser at full health," "this planet is a tide-locked rocky body around a yellow dwarf." The variation layer translates each token into actual rendered output, applying a per-token variation function. The translation is deterministic given the token + the encounter seed; reload the same scene and you get the same variations.

Critically: **the variation layer never sends information back to the engine.** The Slylandro's awe value affects the music; the music does not affect the Slylandro's awe value. This one-way data flow is what makes the system safe — gameplay logic can never be corrupted by variation bugs.

## The Universal Recipe

For any variable element in the game:

1. **Define the center**: the canonical version. The species archetype portrait, the canonical hyperspace theme, the standard Cleanser cruiser sprite, the standard ammonia-water-mineral pattern.
2. **Define the variation vectors**: the parameters along which this element varies. Color hue, accessory variation, tempo, layer mix, pose offset.
3. **Define the variation function**: input is the deterministic seed (e.g., entity ID, encounter ID); output is the chosen variation values.
4. **Cache aggressively**: variations are deterministic, so cache by (entity ID, variation type). Compute once, reuse forever.
5. **Provide a no-variation fallback**: the engine must run with the variation layer disabled. If anything fails, ship the canonical version.

## The Catalog — Everything Varied

What in SC2 was identical-on-repeat? All of these. Each gets a variation function.

### Already designed
- **Alien dialog text** — LLM-rendered surface text over FSM. See `species-precursor-era.md`.
- **Alien portraits** — SD-generated archetype + per-individual variation. See `project_art_approach`.
- **Music** — stem mixing + tempo/key/section knobs + disposition-tied stems. See `music-system.md`.

### Slice-scope but undesigned
- **Ship visuals** — each enemy ship (Cleanser cruiser, rogue biot, Defender courier) gets per-instance visual delta: paint scheme variation, hull decoration noise, lighting tint, fur or spore-pattern overlays. Behavior (stats, weapons, AI) is identical across instances.
- **Planet surface terrain** — base terrain generated procedurally from star seed (UQM's approach); variation layer adds local variation in color palette, biome decoration, structural noise on the same terrain. Two ammonia-water rocky planets look distinct even with the same elemental composition.
- **Mineral nodes** — base shape per element type (UQM convention); variation in cluster size, color intensity, and arrangement on the surface.
- **Biological specimens** — base creature per "biology pattern"; variation in coloration, size, motion-pattern speed, behavior arc. The 5th alpha-radiating creature you find is not visually identical to the 1st.
- **NPC names** — per-species naming grammar generates unique names. Slylandro: weather-phenomenon poetry ("Hail-Curtain-Of-A-Long-Decade"). Furling: traditional patronymic patterns. Cleanser: a numbered designation with a poetic suffix.
- **Asteroid shapes in combat** — base 3-4 silhouettes; per-asteroid rotation, scale, and detail noise.
- **Combat explosions** — base animation, per-instance color/size/timing variation.
- **UI sound effects** — even button-clicks vary subtly in pitch and timbre per press. The seventh click in a session doesn't sound identical to the first.

### Full-game scope
- **Star backgrounds in hyperspace** — base star field per coordinate region; variation in twinkling pattern, faint nebula tint, occasional shooting stars.
- **Quasi-space ambient visuals** — base "across the curtain" effect; per-visit variation in color flow.
- **Encounter setup descriptions** — the "you arrive at a yellow dwarf with 3 planets" text is templated; LLM varies the phrasing.
- **Council scene NPC arrangement** — same faction reps, but spatial arrangement and idle posture vary.
- **Lander deployment sequence** — base animation, per-deployment timing/effect variation.
- **Save-file load screen flavor text** — "Steward's Log: stardate XXXX" varied each load.

### Off-limits (do NOT vary)
- **Game-logic numbers** — ship stats, weapon damage, fuel costs, time-to-cross, mineral values per element. These must be deterministic and identical run-to-run for the game to be fair.
- **Dialog branch logic** — which states transition to which on which choice categories. The text varies; the FSM does not.
- **Quest/encounter triggers** — when an event fires must be predictable.
- **Save data structure** — the variation layer reads from save data but never writes to it (except cache).
- **Player ship visuals** — the Furling scout is YOUR ship. It looks the same every time you see it. Recognition matters more than variation here. (Customization is a different feature.)

## Why This Is Easy

Most attempts at "make the game more varied" fail because they try to vary the gameplay itself — different stats per encounter, different rules per session, different physics per scene. That's *hard* because variation now interacts with balance, save state, AI, and difficulty. Bugs in variation become bugs in the game.

The Star Control Zero approach is **the gameplay never varies**. Combat is the same. Dialog branches are the same. Mineral yields are the same. The variation only ever affects what the player *sees*, *hears*, and *reads* — never what the player *does* or what *happens*. A bug in the variation layer might make a Slylandro look wrong; it cannot make a Slylandro behave wrong.

That separation is what makes the per-asset authoring cost worth it. The architecture protects us from the variation system becoming a maintenance burden.

## Implementation Roadmap (Slice)

This sits cleanly on top of the existing Phase plan:

- **Phase 2 (Engine MVP)** — build the static engine. Fixed portraits, fixed dialog text (per-state canned lines, no LLM), fixed music tracks (mono mix), fixed ships, deterministic combat AI without personality variation. No variation layer yet. Game is playable but samey. **Ship this first — full slice end-to-end before any variation work begins.**
- **Phase 3.5 (Variation Layer)** — ONLY after the slice is playable end-to-end. The variation layer is a deliberate later phase, not concurrent work. Add in ROI order:
  1. LLM dialog rendering (the most repetitive thing in SC2 was the same words; biggest win to vary)
  2. Per-individual portraits (visible at every encounter; large impact per unit of work)
  3. Music stem mixing (player keeps the music on; huge for retention)
- **Phase 4 (Content)** — author the variation parameters per species, per track, per ship as we author the slice content.
- **Phase 5 (Polish)** — add the small-touches variation: UI clicks, explosion timing, name generators.

The slice MUST be playable at the end of Phase 2 with the engine alone — no LLM, no variation, just deterministic FSM dialog and static everything. The variation layer turns it from playable to *atmospheric* in a later pass. The progression is incremental and de-risked: every LLM/variation feature has a working static fallback we can ship without.

> **Deferral discipline (per Aaron, 2026-05)**: do not add LLM hooks, prompt scaffolding, or variation knobs to engine code until the full static slice is traversable end-to-end. Code added "in anticipation" of LLM integration tends to get the design wrong and the constraints wrong. We'll know the right shape only after the static engine forces us to confront which decisions need variation.

## What This Catalog Costs

For each new variable element added: one base asset + one variation function + one cache key + one fallback path. That's it. Once the layer pattern is in place, adding a new variable is a small task — author a base, define variation vectors, register the variation function. The marginal cost is low; the marginal benefit is constant atmosphere.

This is why the principle scales: it's a one-time architecture investment that compounds across the full content of the game.
