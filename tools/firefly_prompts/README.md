# Adobe Firefly image-prompt handoff

While Firefly is unlimited free (until 2026-05-20), this folder holds
ready-to-paste prompts for individual assets that need imagery.

## Workflow

1. Open Firefly: <https://firefly.adobe.com/generate/image>
2. Pick a `.txt` file in this folder — that's the prompt
3. Set model: **Gemini 3.1 (w/ Nano Banana 2)** in General Settings
4. Set aspect ratio per the prompt's `# aspect:` header (square for
   portraits/ships, 16:9 for planet vistas)
5. Paste the prompt body into Firefly's "Describe the image" box
6. Click Generate
7. Save the best result as `<slug>.png` (matching the prompt filename)
   into `assets/generated_drafts/firefly/`
8. Once 1-3 are dropped in, ping me and I'll wire them into the game

## Asset placement convention

```
assets/generated_drafts/firefly/
├── species_melnorme_portrait.png
├── species_mycon_biot_portrait.png
├── ship_melnorme_trader.png
├── planet_drahn.png
├── planet_xylos_prime.png
├── planet_ossuary.png
└── species_planar_blade_portrait.png
```

When I wire them in, I move them under their permanent paths
(`assets/comm/<species>/`, `assets/ships/`, `assets/planets/`) and
update `assets/_PLACEHOLDERS.json` to `status: replaced` per Rule 1.

## Prompt files

Each file is named `<category>_<slug>.txt`. Filename = output filename
(swap `.txt` for `.png`).

Header lines:
- `# aspect:` — aspect ratio (1:1, 4:3, 16:9)
- `# notes:` — what you might iterate on if first generation is off
