"""Phase 1 simplified prompts for Firefly Image 3.

Original prompts at tools/firefly_prompts/tier1_*/ were 1500-2200 chars with
weapon/horror/anatomy terms that hit Firefly's content filter. These versions
are shortened to ~800 chars, stripped of weapon refs, with friendlier alien
anatomy language.

Usage: python tools/firefly_phase1_simplified.py <slug>
  e.g. python tools/firefly_phase1_simplified.py species_stelloth_chord

Outputs a JS snippet that sets the cached Firefly textarea.
"""

import sys, json

PROMPTS = {
    # === STELLOTH (three-body chord beings) ===
    "species_stelloth_chord": (
        "tier1_portraits",
        "Close-up portrait of an alien being composed of THREE bodies linked together as ONE individual. Three tall slim insectoid figures stacked in a chord — one in front, one upper-back, one lower-front. Each body has a jointed shell carapace in cool pearl-grey shading to green-violet at the joints with subtle iridescence. The three bodies are CONNECTED by braided BIOLOGICAL CORDS — visible as 3-5 vine-like dark-plum living tendrils running between shoulder-points and throats, binding the three into one entity. Each body has four slender manipulator-arms. Front body's head tilted forward in mid-sentence. Upper-back body has a translucent prismatic crystal on its head, slightly blurred at edges. Lower body has small geometric tally-marks etched on its torso shells. Background: solid matte dark navy. Lighting: cool pearl-grey key, green-violet rim from the cords. Style: stylized 1990s sci-fi game character portrait, painterly, precise composition.",
    ),
    "ship_stelloth_three_voice_arc": (
        "tier1_ships",
        "Top-down view of a stylized alien spaceship with a TRIPLE-HULL chord arrangement. Three slim parallel sub-hulls arranged in a tight arc formation, all linked by glowing pearl-grey cross-struts. Each sub-hull is elegant and tapered, pearl-grey shading to green-violet at the seams. Soft glowing pale-cyan plasma flows through the cross-struts linking the three hulls. Small thruster nozzles at the rear of each sub-hull glow soft pearl. The three hulls clearly read as ONE vessel — a unified chord-stack rather than three ships flying in formation. Color: cool pearl-grey hulls, green-violet edge accents, pale-cyan link-plasma. Background: deep starfield, near-black. Style: stylized 1990s sci-fi game art, painterly with crisp silhouette, precise architectural composition.",
    ),
    "bg_stelloth_trading_post": (
        "tier1_dialog_backgrounds",
        "Square interior view of an elegant alien trading station chamber. Cool pearl-grey + green-violet color palette. A semi-circular receiving room with curved walls made of layered translucent crystal panels. Tall narrow alcoves line the walls, each containing soft glowing pearl-toned light. Floor of polished violet-tinged stone with geometric tally-mark inlays. Mid-ground: a tall mantis-form alien stands at a curved console facing the viewer — three slim bodies linked together as one chord-being, jointed pearl-grey shells, slender manipulator-arms gesturing in greeting. Background through the chamber's tall windows: a deep starfield with a distant pale super-giant star casting cool light into the chamber. Lighting: cool pearl key from above, green-violet rim from the cords. Style: stylized 1990s sci-fi game backdrop, painterly, precise architectural composition.",
    ),
    # === SELVENNE (5cm bioluminescent coral polyps) ===
    "species_selvenne_polyp": (
        "tier1_portraits",
        "Close-up macro portrait of a tiny alien sea creature — a 5cm bioluminescent coral polyp. The polyp is a small bulbous translucent body, soft jelly-textured, glowing from within with warm amber-orange bioluminescence. Long fringe-like sensory tendrils extend outward in a delicate fan. The body surface ripples gently with chromatic waves of soft green and warm amber. The polyp is centered in the frame, viewed as if very close. Background: solid matte dark navy with a faint suggestion of underwater bioluminescence. Lighting: warm amber inner glow + cool blue rim from above. Style: stylized 1990s sci-fi game macro portrait, painterly, jewel-like precision, sense of tiny ancient quiet life.",
    ),
    "bg_selvenne_brain_coral_sanctum": (
        "tier1_dialog_backgrounds",
        "Square underwater chamber view inside a vast organic coral sanctum. The walls and ceiling are sculpted brain-coral structures — convoluted folds of amber and pale-rose biomineral, glowing from within with soft warm bioluminescence. Floor: smooth coral-stone in pale cream. Mid-ground: a central pool of clear water with small bioluminescent coral polyps glowing amber within. Above the pool, long fronds of coral arch overhead like a vaulted ceiling, dotted with thousands of tiny amber and cyan light-points. The atmosphere is warm, watery, ancient. Background: deeper coral chambers receding into soft amber haze. Lighting: warm amber inner glow + cool cyan rim from the pool. Style: stylized 1990s sci-fi game backdrop, painterly, organic ancient sanctum composition.",
    ),
    "cutscene_selvenne_memory_playback": (
        "tier1_cutscenes",
        "Widescreen 16:9 cinematic frame — a vision of warm bioluminescent memory. BORDER: a thick frame of glowing warm-amber and cool-cyan bioluminescence, organic coral-fronds curling inward from the edges, suggesting that the central image is being viewed through a living conduit. CENTER (the playback content): a stylized soft-focus scene of an ancient alien gathering — gentle silhouettes of figures around a warm fire-glow under a deep night sky with strange constellations. The whole inner-frame has a dreamy soft-focus quality, faded edges, slightly desaturated, as if the memory is being remembered rather than experienced. Lighting: warm amber from the border, cool blue-violet within the dream-scene. Style: stylized 1990s sci-fi cinematic, painterly, sense of qualia transmission, ancient quiet remembering.",
    ),
    # === MROKON (puppet + operator system) ===
    "species_mrokon_vrek_puppet": (
        "tier1_portraits",
        "Close-up portrait of a humanoid alien figure — a 2m tall slender puppet-being. Long lean limbs with smooth grey-violet skin, expressionless oval face with two dark almond eyes and no mouth. The figure stands relaxed but vacant. Across the bare chest: EIGHT small geometric ledger-marks tattooed in dark indigo in a horizontal row (representing eight life-cycles). At the back of the neck and base of the skull: visible BIOMECHANICAL CABLES — 4-5 dark organic tendrils running down between the shoulder blades, suggesting remote-control linkage to an operator elsewhere. Wears a simple loose grey-violet sleeveless tunic. Background: solid matte dark navy. Lighting: cool grey-violet key, warm amber rim from below suggesting cable-glow. Style: stylized 1990s sci-fi game character portrait, painterly, sense of a vessel piloted by someone elsewhere.",
    ),
    "species_mrokon_operator_bunker": (
        "tier1_portraits",
        "Close-up portrait of a small alien being — a 1m tall stocky bunker-dweller with thick wrinkled pale-cream skin and large dark observant eyes. The being sits surrounded by soft-glowing biomechanical control cables that snake into the back of its skull and into both arms. Posture: cross-legged, weight-distributed, settled-in-place — a being that does not move. The face is expressive, intelligent, weathered. Wears a simple cream wrap garment. Background: solid matte dark navy with a soft warm amber glow from below suggesting bunker-light. Lighting: warm amber from below, cool blue rim from above. Style: stylized 1990s sci-fi game character portrait, painterly, sense of an ancient operator who lives in safety while sending puppets out to act.",
    ),
    "planet_mrokons_stand_surface": (
        "tier1_planets",
        "Top-down view of an alien planet's surface — a rocky desert terrain. The ground is umber-bronze rocky regolith with scattered crystalline outcrops in pale-cream and dark-indigo. Across the landscape: many small DOMED BUNKER STRUCTURES half-buried in the regolith — low rounded shelters with cream-stone walls and small dark observation slits. Between the bunkers: a network of dark cable-channels carved into the regolith, all converging toward a large central bunker hub. The landscape has a sense of ancient methodical safety — a civilization that has dug in and stayed put for generations. Color: warm umber-bronze regolith, pale-cream bunker walls, dark-indigo cable-channels. Background: a dim sun in the upper corner casting long shadows. Style: stylized 1990s sci-fi game top-down terrain, painterly, sense of dug-in ancient civilization.",
    ),
    "ship_mrokon_hammer_ship": (
        "tier1_ships",
        "Top-down view of a stocky alien spaceship — a hammer-shaped vessel. Short heavy hull with a wide flat front-face (the hammer-head) and a narrower rear stem. The hammer-head is roughly square, armored with thick umber-bronze plates, with two small dark observation slits and a centered emitter aperture. The rear stem has two stubby thruster nozzles glowing soft amber. The ship's silhouette is deliberately blunt and weighty — not graceful. Color: warm umber-bronze armor plates dominant, dark-indigo recesses, soft amber thruster-glow. Background: deep starfield, near-black. Style: stylized 1990s sci-fi game art, painterly with crisp silhouette, weighty industrial composition. Tone: a vessel that strikes once and hard.",
    ),
    # === KOVELLIM (cycle-veterans, 8 knot-scars) ===
    "species_kovellim_ovala_elder": (
        "tier1_portraits",
        "Close-up bust portrait of an alien elder — a humanoid figure with weathered umber-bronze skin and a calm wise face. Deep-set amber eyes, a noble brow, a small soft beak-like mouth. The skin is leathery and aged. Visible across the chest and forearms: EIGHT small COILED KNOT-SCARS — small raised umber relief markings in a deliberate pattern (each scar represents one dimensional crossing the elder has personally survived). The eighth scar is fresh and slightly redder than the others. Wears a heavy ceremonial mantle of woven indigo and umber cord — the genealogy-cloak. Posture: still, contemplative. Background: solid matte dark navy. Lighting: warm amber key from upper-left, cool indigo rim from upper-right catching the cord-mantle. Style: stylized 1990s sci-fi game character portrait, painterly, ancient and proven.",
    ),
    "bg_kovellim_eight_knot_station": (
        "tier1_planets",
        "Top-down view of a small alien orbital station — an octagonal hub with eight distinct radial spokes extending outward to form a star-pattern. Each of the eight spokes carries a small docking arm at its tip. The central hub bears a large engraved coiled-knot pattern. Color palette: weathered umber-bronze hull plates dominant, patches of pale-gold where the armor has been worked smooth, dark-indigo recesses. Soft warm-amber light glows from many small windows along the spokes. Background: deep starfield, the station floats alone against the void. Style: stylized 1990s sci-fi game art, painterly with crisp silhouette, weighty archaeological composition. Tone: a station built once and maintained for eight crossings — durable, proven, ancient.",
    ),
    "bg_kovellim_receiving_chamber": (
        "tier1_dialog_backgrounds",
        "Square interior view of an alien receiving chamber inside an orbital station. The chamber is octagonal, with each of the eight walls carved deeply with a coiled-knot genealogy pattern in warm umber-bronze relief. Floor: polished dark-indigo stone with a central inlaid eight-knot insignia in pale-gold. Mid-ground: a single robed humanoid elder stands facing the viewer, weathered umber-bronze skin, indigo ceremonial mantle, calm posture. Behind the elder: a tall narrow window showing a deep starfield with a distant golden sun. The chamber feels old, proven, lived-in. Lighting: warm amber key from above, cool indigo fill from the floor-pattern. Style: stylized 1990s sci-fi game backdrop, painterly, weighty archaeological composition.",
    ),
    "ship_kovellim_crossing_frigate": (
        "tier1_ships",
        "Top-down view of a stout alien frigate — a thick barrel-shaped hull deliberately ROBUST and durable rather than graceful. Wider at the midline than at either end (a beer-keg silhouette), with chamfered armored shoulders and a rounded prow. The dorsal armor is covered with 7-9 small raised COILED KNOT-SCARS distributed in a deliberate pattern, each one a permanent record of a prior dimensional crossing. Color: weathered umber-bronze dominant, darker tarnished-copper recesses, patches of pale-gold where the armor has been worked smooth. The prow carries an engraved eight-braided coiled-knot insignia at large scale. Two stout main thruster nozzles at the rear glow soft pale-gold. Background: deep starfield. Style: stylized 1990s sci-fi game art, painterly with crisp silhouette, weighty archaeological composition.",
    ),
    # === KARAVEM (singing canyon people) ===
    "bg_karavem_welcome_choir": (
        "tier1_dialog_backgrounds",
        "Square view of a canyon-edge looking outward across a vast deep canyon. Foreground: a gracefully curved bronze-wood perch-platform with delicate carved railings. Mid-ground: a CHOIR of 12 alien beings arranged in a semicircle facing the viewer, perched on terraced cliff-edges across the canyon. Each is a slim winged humanoid about 1.5m tall with large feathered wings partially flexed outward, a complex throat-organ visibly engaged at the front of the neck, beak slightly open. The 12 are arranged in three plumage groups: LEFT (4) golden-rust plumage, CENTER (4) pale cream and sage-green plumage, RIGHT (4) deep indigo plumage with silver-tipped feathers. Their eyes glow bright yellow. Subtle faint geometric resonance-rings ripple outward from each throat in pale gold. Background: vast canyon walls with terraced cliff-cities carved into the rock, morning light slanting across in long golden shafts. Lighting: warm gold key from left, cool fill from canyon depths. Style: stylized 1990s sci-fi game backdrop, painterly, graceful aerial composition.",
    ),
    "species_karavem_veled_elder": (
        "tier1_portraits",
        "Close-up bust portrait of an alien elder — a winged humanoid being with DEEP-INDIGO PLUMAGE and silver-tipped feathers across the crown, cheeks, neck, and visible upper-wing edges. The plumage has subtle violet iridescence. Visible at the front of the neck: a prominent bulbous THROAT-ORGAN about the size of a small fist, with layered muscular-resonant tissue covered in fine soft feathers and three visible separable chambers (each producing one of three simultaneous notes that compose the species's speech). Head: a graceful beaked face with a narrow tapered burnished-bronze beak, wide-set eyes glowing soft RED-AMBER (contemplative mood), elegant feathered head-crest swept back. A single delicate four-fingered hand held in a conversational mid-gesture. Wears a simple cross-shoulder sash of pale-cream embroidered with conductor's-baton motifs. Background: solid matte dark navy. Lighting: warm gold key from upper-left, cool silver rim from upper-right catching the silver wing-tips, soft red-amber inner glow from the eyes. Style: stylized 1990s sci-fi game character portrait, painterly, graceful composition.",
    ),
    "bg_aeris_sing_canyons": (
        "tier1_planets",
        "Square landscape view of vast alien canyon-cities at slow-sunset. Composition: a vast deep canyon stretches diagonally across the frame, cliff-walls rising on both sides hundreds of meters high. The cliff faces are CARVED INTO TERRACED PERCH-CITIES — dozens of curved bronze-wood platforms, balconies, and small open-air amphitheaters recessed into the rock at varied heights, connected by graceful suspended bridges of pale-cream cable arching across the canyon. The walls themselves: warm gold-cream sandstone with mineral veins of soft silver. Long warm-amber shadows from a low golden-cream sun behind the right cliff-wall, deep cool blue-violet shadow filling the canyon bottom. PALE-CYAN BIOLUMINESCENT MOSS patches glow softly on the cliff-faces in shadow zones. Background: a vast deeper canyon system receding into pale gold haze. Style: stylized 1990s sci-fi game landscape, painterly, graceful aerial composition.",
    ),
}


def emit(slug):
    if slug not in PROMPTS:
        raise SystemExit(f"unknown slug: {slug}; valid: {list(PROMPTS)}")
    category, body = PROMPTS[slug]
    js_literal = json.dumps(body, ensure_ascii=False)
    snippet = (
        "const v = " + js_literal + ";\n"
        "window.__sczSetter.call(window.__sczTextarea, v);\n"
        "window.__sczTextarea.dispatchEvent(new Event('input', { bubbles: true }));\n"
        "JSON.stringify({ ok: true, slug: " + json.dumps(slug) + ", category: " + json.dumps(category) + ", len: v.length });"
    )
    sys.stdout.buffer.write(snippet.encode('utf-8'))


if __name__ == "__main__":
    emit(sys.argv[1])
