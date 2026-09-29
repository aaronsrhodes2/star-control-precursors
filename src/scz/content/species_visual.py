"""Per-species visual identity — warp-pod colors, used by hyperspace,
combat scenes, and any other view that renders ships.

The lore frame (Aaron's design): each species' warp-drive technology
produces a differently-colored ovoid envelope around the ship. SC2-era
observers saw red because Furling pods are red — but every other species
has its own. Seeing a magenta pod converging on you in hyperspace is
*instant identification* — you know it's an Androsynth refugee, you know
who you're talking to before any dialog opens.

Color philosophy:
- Each species' color reflects its lore (Mycon = sickly fungal yellow-green;
  Arilou = teal Quasi-Space mint; Androsynth = magenta human-cyber tech;
  Mmrnmhrm = silver machine; Proto-Qor-Ah = sickly-green / black, hinting
  at the SC2 Kohr-Ah; etc.)
- "interior" is the dark inner fill of the pod
- "rim" is the brighter outline (most visually identifying color)
- "glow" is the translucent halo around the pod; 4th value is alpha 0-255

When we add encounters in hyperspace, each encountering ship is drawn with
the warp pod colored by its species ID. Players learn the palette by play.
"""

from __future__ import annotations


# Per-species warp pod color set. Add entries as new species ship in.
SPECIES_WARP_POD: dict[str, dict[str, tuple]] = {
    # ----- Furlings (player's people + factions) -----
    "FURLING_SCOUT": {
        # The player's default. Classic SC2-hyperspace red.
        "interior": (50, 14, 16),
        "rim":      (200, 80, 80),
        "glow":     (220, 80, 80, 60),
    },
    "FURLING_PERSUADER": {
        # Diplomatic faction — warm amber, suggests dialogue
        "interior": (40, 24, 10),
        "rim":      (220, 180, 100),
        "glow":     (230, 190, 100, 60),
    },
    "FURLING_COMPELLER": {
        # Pragmatist faction — between Persuader amber and Cleanser orange
        "interior": (50, 24, 12),
        "rim":      (230, 150, 70),
        "glow":     (230, 150, 70, 60),
    },
    "FURLING_CLEANSER": {
        # Cleansers — orange-red, "burning gift" feel. Identifiable as
        # Furling-related but distinctly hostile to Homesteader cases.
        "interior": (60, 20, 8),
        "rim":      (240, 120, 60),
        "glow":     (240, 120, 60, 70),
    },
    "FURLING_DEFENDER": {
        # Defenders — deep blood-red, Sa-Matra-builder palette
        "interior": (40, 8, 8),
        "rim":      (160, 40, 40),
        "glow":     (180, 40, 40, 70),
    },

    # ----- Refugee / time-displaced species -----
    "ANDROSYNTH": {
        # Late-22nd-century human clone-tech: cool magenta
        "interior": (40, 20, 60),
        "rim":      (200, 100, 240),
        "glow":     (200, 100, 240, 60),
    },

    # ----- Sentient observed in slice -----
    "SLYLANDRO": {
        # Slylandro don't fly — but their Cloaking Satellite emits a faint
        # gold envelope they use for orbital craft. Pale gas-giant gold.
        "interior": (60, 50, 20),
        "rim":      (240, 220, 140),
        "glow":     (240, 220, 140, 60),
    },
    "ARILOU": {
        # Quasi-Space adapted — pale teal/mint, suggests "halfway here"
        "interior": (20, 60, 50),
        "rim":      (140, 240, 210),
        "glow":     (140, 240, 210, 60),
    },
    "MMRNMHRM": {
        # Machine consciousness — clean silver-white
        "interior": (50, 50, 60),
        "rim":      (220, 220, 240),
        "glow":     (220, 220, 240, 60),
    },

    # ----- Pre-sentient / observation-only -----
    "DNYARRI": {
        # Mind-controlling brain-creatures; in our era pre-sentient
        # microfauna riding host species on a single planet. No warp
        # tech — but the species' canonical SC2 color is sickly
        # bilious yellow-green, which doubles as their hyperspace-
        # presence marker once the Echo Sensor picks them up.
        "interior": (40, 40, 10),
        "rim":      (220, 220, 80),
        "glow":     (220, 220, 80, 60),
    },

    # ----- Uplift-project subspecies -----
    "MYCON_BIOT": {
        # Spore-driven fungal — sickly chartreuse, organic and uneasy
        "interior": (40, 40, 14),
        "rim":      (180, 200, 80),
        "glow":     (180, 200, 80, 60),
    },
    "PROTO_URQUAN": {
        # Foreshadows SC2 Kzer-Za — imperial purple, slaver overtones
        "interior": (50, 30, 60),
        "rim":      (200, 120, 240),
        "glow":     (200, 120, 240, 60),
    },
    "PROTO_QORAH": {
        # Foreshadows SC2 Kohr-Ah — sickly green-black, ritual lethality
        "interior": (20, 40, 20),
        "rim":      (100, 200, 100),
        "glow":     (60, 140, 60, 80),
    },

    # ----- Canonical SC2 species filled out in our era -----
    "TAALO": {
        # Peaceful crystalline-amphibian — luminous pale cyan
        "interior": (30, 50, 60),
        "rim":      (140, 220, 240),
        "glow":     (140, 220, 240, 60),
    },
    "BURVIXESE": {
        # Industrious engineers — bright industrial gold
        "interior": (60, 50, 20),
        "rim":      (240, 200, 80),
        "glow":     (240, 200, 80, 60),
    },
    "MELNORME": {
        # Gas-cloud energy-being nomadic traders. Plasma-violet —
        # ionization-pattern signaling rendered as a warp-pod color.
        # Distinct enough from Androsynth magenta to read at a glance.
        "interior": (32, 16, 64),
        "rim":      (180, 100, 255),
        "glow":     (160, 80, 240, 70),
    },

    # ----- Invented species (placeholder concepts) -----
    "DEFIANT": {
        # Combat-coded proud-doomed Homesteader — defiant hot pink
        "interior": (60, 20, 40),
        "rim":      (240, 80, 180),
        "glow":     (240, 80, 180, 60),
    },
    "CURIOUS": {
        # Wide-eyed exploratory Precursor-faction species — sky blue
        "interior": (20, 50, 60),
        "rim":      (140, 220, 255),
        "glow":     (140, 220, 255, 60),
    },

    # ----- The Others' vessel (special; hijack-only ship) -----
    "OTHERS": {
        # Not actually a warp pod — a projection of an entity from outside
        # 3D space. Black core with blood-red rim. Unsettling.
        "interior": (8, 6, 10),
        "rim":      (200, 50, 50),
        "glow":     (60, 0, 0, 110),
    },
}


# Fallback if a species ID isn't in the palette — light gray pod
DEFAULT_WARP_POD: dict[str, tuple] = {
    "interior": (40, 40, 50),
    "rim":      (200, 200, 220),
    "glow":     (200, 200, 220, 50),
}


def get_warp_pod_colors(species_id: str) -> dict[str, tuple]:
    """Return the warp-pod color set for a species, or a default if missing."""
    return SPECIES_WARP_POD.get(species_id, DEFAULT_WARP_POD)
