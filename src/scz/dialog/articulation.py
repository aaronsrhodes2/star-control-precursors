"""Articulation rig presets for dialog character avatars.

Each preset is an ArticulationSpec describing the joints / pivot points
the avatar exposes, what amplitude of procedural movement reads as
natural for that body plan, and which joints the (future) per-frame
animator should target first.

These specs are *cited in prompts* so generated avatar art comes back
with each joint legible — clear shoulder seams, visible neck-on-collar,
non-occluded tendril roots, etc. They are also *carried with the
character* so the variation-layer PortraitAnimator can read the rig
without having to infer it from the image.

Today's procedural animator (DialogScene) only uses the amplitude/tilt
hints; the joint list is documentation. When Flask-SD or a comparable
service can generate per-frame mouth/limb banks on demand, the joint
list becomes the index into those frame banks.
"""

from __future__ import annotations

from scz.dialog.data import ArticulationSpec, Joint


# ---------------------------------------------------------------------------
# Humanoid rig — used for Furlings, Androsynth, Talos, anyone with the
# bipedal "two arms, two legs, head on neck" body plan.
# ---------------------------------------------------------------------------

BIPEDAL_HUMANOID = ArticulationSpec(
    rig_type="bipedal_humanoid",
    joints=(
        Joint("head",       pivot=(0.50, 0.18), rot_range_rad=(-0.15, 0.15), size_hint=(0.28, 0.22)),
        Joint("neck",       pivot=(0.50, 0.27), rot_range_rad=(-0.12, 0.12), size_hint=(0.10, 0.06)),
        Joint("shoulder_l", pivot=(0.36, 0.32), rot_range_rad=(-0.35, 0.20), size_hint=(0.08, 0.08)),
        Joint("shoulder_r", pivot=(0.64, 0.32), rot_range_rad=(-0.20, 0.35), size_hint=(0.08, 0.08)),
        Joint("elbow_l",    pivot=(0.30, 0.50), rot_range_rad=(-0.40, 0.40), size_hint=(0.06, 0.06)),
        Joint("elbow_r",    pivot=(0.70, 0.50), rot_range_rad=(-0.40, 0.40), size_hint=(0.06, 0.06)),
        Joint("wrist_l",    pivot=(0.28, 0.66), rot_range_rad=(-0.30, 0.30), size_hint=(0.05, 0.05)),
        Joint("wrist_r",    pivot=(0.72, 0.66), rot_range_rad=(-0.30, 0.30), size_hint=(0.05, 0.05)),
        Joint("torso",      pivot=(0.50, 0.50), rot_range_rad=(-0.05, 0.05), size_hint=(0.30, 0.30)),
    ),
    breath_amplitude_px=1.5,
    sway_amplitude_px=2.0,
    speak_bob_amplitude_px=1.5,
    speak_tilt_amplitude_rad=0.02,
)


# ---------------------------------------------------------------------------
# Mechanical-humanoid rig — Mmrnmhrm. Same joint topology as bipedal,
# but tighter rotation ranges (servo-driven) and zero breath.
# ---------------------------------------------------------------------------

ROBOT_HUMANOID = ArticulationSpec(
    rig_type="robot_humanoid",
    joints=BIPEDAL_HUMANOID.joints,
    breath_amplitude_px=0.0,           # robots don't breathe
    sway_amplitude_px=0.8,             # tighter stance
    speak_bob_amplitude_px=0.6,
    speak_tilt_amplitude_rad=0.012,
)


# ---------------------------------------------------------------------------
# Gas-bag tendril rig — Slylandro and similar floating-bell aliens.
# Six tendrils splay around a central bell. Tendril tip rotation is wide
# because tendrils are soft; bell rotation is small.
# ---------------------------------------------------------------------------

GASBAG_TENDRIL = ArticulationSpec(
    rig_type="gasbag_tendril",
    joints=(
        Joint("bell",       pivot=(0.50, 0.30), rot_range_rad=(-0.10, 0.10), size_hint=(0.45, 0.40)),
        Joint("tendril_1",  pivot=(0.25, 0.55), rot_range_rad=(-0.40, 0.40), size_hint=(0.08, 0.35)),
        Joint("tendril_2",  pivot=(0.35, 0.65), rot_range_rad=(-0.40, 0.40), size_hint=(0.08, 0.35)),
        Joint("tendril_3",  pivot=(0.45, 0.70), rot_range_rad=(-0.40, 0.40), size_hint=(0.08, 0.35)),
        Joint("tendril_4",  pivot=(0.55, 0.70), rot_range_rad=(-0.40, 0.40), size_hint=(0.08, 0.35)),
        Joint("tendril_5",  pivot=(0.65, 0.65), rot_range_rad=(-0.40, 0.40), size_hint=(0.08, 0.35)),
        Joint("tendril_6",  pivot=(0.75, 0.55), rot_range_rad=(-0.40, 0.40), size_hint=(0.08, 0.35)),
    ),
    breath_amplitude_px=2.5,           # the bell visibly inflates
    sway_amplitude_px=2.5,             # they drift in atmosphere
    speak_bob_amplitude_px=1.0,
    speak_tilt_amplitude_rad=0.03,
)


# ---------------------------------------------------------------------------
# Ribbon-planar rig — the Planar (zero-width 2D species). Edge-on is
# invisible, so we depict them face-on; the two appendages are the only
# articulating limbs.
# ---------------------------------------------------------------------------

RIBBON_PLANAR = ArticulationSpec(
    rig_type="ribbon_planar",
    joints=(
        Joint("top_edge",     pivot=(0.50, 0.10), rot_range_rad=(-0.08, 0.08), size_hint=(0.50, 0.10)),
        Joint("appendage_l",  pivot=(0.30, 0.55), rot_range_rad=(-0.50, 0.50), size_hint=(0.10, 0.40)),
        Joint("appendage_r",  pivot=(0.70, 0.55), rot_range_rad=(-0.50, 0.50), size_hint=(0.10, 0.40)),
        Joint("center_axis",  pivot=(0.50, 0.50), rot_range_rad=(-0.20, 0.20), size_hint=(0.05, 0.80)),
    ),
    breath_amplitude_px=1.0,
    sway_amplitude_px=4.0,             # ribbon-body drifts more in air
    speak_bob_amplitude_px=2.0,
    speak_tilt_amplitude_rad=0.04,
)


# ---------------------------------------------------------------------------
# Composite-cloud rig — Melnorme (sentient gas-cloud-in-pod). The visible
# body is a featureless cloud inside a glass pod, so the only articulating
# elements are the cloud's internal swirl and pod-mounted manipulators.
# ---------------------------------------------------------------------------

COMPOSITE_CLOUD = ArticulationSpec(
    rig_type="composite_cloud",
    joints=(
        Joint("pod_top",        pivot=(0.50, 0.15), rot_range_rad=(-0.06, 0.06), size_hint=(0.40, 0.10)),
        Joint("cloud_swirl",    pivot=(0.50, 0.50), rot_range_rad=(-0.30, 0.30), size_hint=(0.55, 0.55)),
        Joint("manipulator_l",  pivot=(0.30, 0.55), rot_range_rad=(-0.25, 0.25), size_hint=(0.10, 0.30)),
        Joint("manipulator_r",  pivot=(0.70, 0.55), rot_range_rad=(-0.25, 0.25), size_hint=(0.10, 0.30)),
    ),
    breath_amplitude_px=0.5,
    sway_amplitude_px=1.5,
    speak_bob_amplitude_px=0.8,
    speak_tilt_amplitude_rad=0.015,
)


# ---------------------------------------------------------------------------
# Floating-drone rig — Sentry Drone 47-T and similar small UAV bodies.
# No limbs; just hover oscillation and turret rotation.
# ---------------------------------------------------------------------------

FLOATING_DRONE = ArticulationSpec(
    rig_type="floating_drone",
    joints=(
        Joint("body",      pivot=(0.50, 0.50), rot_range_rad=(-0.20, 0.20), size_hint=(0.50, 0.50)),
        Joint("turret",    pivot=(0.50, 0.35), rot_range_rad=(-0.35, 0.35), size_hint=(0.20, 0.15)),
    ),
    breath_amplitude_px=0.0,
    sway_amplitude_px=1.0,
    speak_bob_amplitude_px=3.0,        # drones expressively hover up/down when speaking
    speak_tilt_amplitude_rad=0.05,
)


# ---------------------------------------------------------------------------
# Lookup helpers for prompt-authoring code.
# ---------------------------------------------------------------------------

ALL_RIGS: dict[str, ArticulationSpec] = {
    rig.rig_type: rig
    for rig in (
        BIPEDAL_HUMANOID,
        ROBOT_HUMANOID,
        GASBAG_TENDRIL,
        RIBBON_PLANAR,
        COMPOSITE_CLOUD,
        FLOATING_DRONE,
    )
}


def articulation_brief(spec: ArticulationSpec) -> str:
    """Format an articulation spec as a prompt-friendly brief. Embedded
    in avatar-generation prompts so Firefly / Flask-SD produces images
    with each joint legible and the body in a pose the future animator
    can easily decompose."""
    joint_lines = "\n".join(
        f"  - {j.name}: pivot near ({j.pivot[0]:.2f}, {j.pivot[1]:.2f}) of frame"
        for j in spec.joints
    )
    return (
        f"ARTICULATION BRIEF (rig: {spec.rig_type}):\n"
        f"- Pose: neutral standing/floating, full body or upper-body visible.\n"
        f"- Each named joint must be legible against the body silhouette\n"
        f"  (clear shoulder seams, visible neck-on-collar, etc.). Avoid\n"
        f"  crossed limbs, occluded hands, or tendril tangles.\n"
        f"- Joints (normalized image coords; the animator will pivot here):\n"
        f"{joint_lines}\n"
        f"- Background: solid matte dark navy #0a0e1a, edge-to-edge, no\n"
        f"  scene elements. The avatar will be composited onto separate\n"
        f"  background art at runtime.\n"
        f"- Lighting: even three-point, no dramatic cast shadows ON the\n"
        f"  body — keep silhouette clean so alpha extraction is easy."
    )
