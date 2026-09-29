"""Council mission briefings — the *active* side of the Furling Council.

Where Recommendations (`council_recommendations.py`) are reactive
decision moments the Steward presents to the Council, **Missions** are
the inverse: the Council assigns the Steward work and waits for it
done. Each mission ties to existing slice content (talk to species X,
recover artifact Y, eliminate threat Z) and tracks lifecycle status
via two flags per mission:

- `mission_<id>_accepted` — set when the Steward formally accepts the
  briefing in the Council scene. Mostly cosmetic for slice MVP; the
  underlying quest content doesn't gate on it. Distinguishes "I knew
  this was assigned" from "I stumbled into it."
- The mission's `completion_flag` — set by the underlying quest content
  when the work is actually done (e.g. `met_slylandro`, `has_distress_beacon`).

Status lifecycle:
- LOCKED      → prereq flag not set; mission invisible to the player
- AVAILABLE   → prereq set, accepted flag not set; "NEW BRIEFING"
- ACTIVE      → accepted, completion not yet set; "in progress"
- COMPLETED   → completion flag set
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scz.engine.game import Game


# Status vocabulary — ordering matters for the Council scene's display
# grouping (available first, then active, then completed, then locked).
STATUS_AVAILABLE: str = "AVAILABLE"
STATUS_ACTIVE: str = "ACTIVE"
STATUS_COMPLETED: str = "COMPLETED"
STATUS_LOCKED: str = "LOCKED"

# Color per status for the scene's row badges.
STATUS_COLORS: dict[str, tuple[int, int, int]] = {
    STATUS_AVAILABLE: (250, 220, 130),    # warm amber — "new briefing!"
    STATUS_ACTIVE:    (180, 220, 240),    # cool blue — in flight
    STATUS_COMPLETED: (140, 180, 150),    # muted green — done
    STATUS_LOCKED:    (110, 110, 130),    # grey — invisible to player
}


@dataclass(frozen=True)
class CouncilMission:
    """One Council briefing the Steward can be assigned."""
    id: str
    title: str
    # Council voice — the formal briefing text shown when the player
    # selects an AVAILABLE or ACTIVE mission. Multi-paragraph, separated
    # by \n\n. Speaks in Persuader-faction register (warm, authoritative,
    # situationally aware).
    briefing: str
    # Concise one-line summary shown in the mission list.
    objective: str
    # Flag that gates the mission's visibility. Prereq for LOCKED →
    # AVAILABLE.
    prereq_flag: str
    # Flag set by the underlying quest content when the work is done.
    # ACTIVE → COMPLETED happens when this flips True.
    completion_flag: str
    # Brief acknowledgement text shown when the player accepts the
    # briefing. One sentence. Stays in the detail pane briefly.
    accept_line: str
    # Council reaction when the mission completes. The next Council
    # visit shows this line on the mission's detail pane.
    completion_line: str


def mission_status(game: "Game", mission: CouncilMission) -> str:
    """Resolve the mission's current lifecycle status by reading flags."""
    flags = game.flags
    if not flags.get(mission.prereq_flag):
        return STATUS_LOCKED
    if flags.get(mission.completion_flag):
        return STATUS_COMPLETED
    if flags.get(f"mission_{mission.id}_accepted"):
        return STATUS_ACTIVE
    return STATUS_AVAILABLE


def accept_mission(game: "Game", mission: CouncilMission) -> None:
    """Player accepts the briefing — formally adds the mission to the
    Steward's active assignments. Idempotent; safe to call multiple
    times.
    """
    game.flags[f"mission_{mission.id}_accepted"] = True


def visible_missions(
    game: "Game", include_locked: bool = False,
) -> list[CouncilMission]:
    """Return missions the player should see in the Council list.

    Locked missions are hidden by default — the player doesn't see
    "Mission: ??? (prereq not met)" because that would spoil the slice.
    """
    out = []
    for m in MISSIONS:
        status = mission_status(game, m)
        if status == STATUS_LOCKED and not include_locked:
            continue
        out.append(m)
    return out


def available_mission_count(game: "Game") -> int:
    """How many missions are AVAILABLE (prereq met, not yet accepted).
    Drives the Station menu's badge text — '(N new briefings)'.
    """
    return sum(
        1 for m in MISSIONS
        if mission_status(game, m) == STATUS_AVAILABLE
    )


def any_mission_visible(game: "Game") -> bool:
    """True iff at least one non-locked mission exists. Drives the
    Station menu's Council visibility gate (alongside any-recommendation).
    """
    return bool(visible_missions(game))


# ---------------------------------------------------------------------------
# Mission registry
# ---------------------------------------------------------------------------
# Order matters: AVAILABLE missions render in this order; the Council's
# auto-cursor lands on the first AVAILABLE one. Authoring follows the
# slice's natural narrative arc (tutorial extension → exploration →
# species-specific quests → late slice).

MISSIONS: tuple[CouncilMission, ...] = (
    CouncilMission(
        id="recover_distress_beacon",
        title="Recover the Vulpeculae Distress Beacon",
        briefing=(
            "Steward. Our hyperspace sensors are receiving an "
            "unverified Androsynth distress signal originating from "
            "displaced coordinates in the Vulpeculae sector. The "
            "Arilou Sage's analysis suggests the source is a *time-"
            "displaced* clone-human civilisation — refugees from our "
            "deep future, dropped here by an Others' decursion.\n\n"
            "Locate the wreckage. Render aid to any survivors. Recover "
            "the Beacon recording — it will be the slice's first "
            "first-hand evidence of the Others. The Council will not "
            "act on rumour. We need the receipt."
        ),
        objective="Find the Androsynth wreckage and recover the Distress Beacon.",
        prereq_flag="tutorial_complete",
        completion_flag="has_distress_beacon",
        accept_line=(
            "Understood. The Steward will track the signal and report "
            "back with what they find."
        ),
        completion_line=(
            "Beacon received. The Archive logs it. The Cleanser bench "
            "sat very still during the playback."
        ),
    ),
    CouncilMission(
        id="contact_slylandro",
        title="First Contact with the Slylandro",
        briefing=(
            "Steward. The Council has confirmed the existence of a "
            "sentient gas-current population in the upper troposphere "
            "of a gas giant at Beta Corvi. The Slylandro Observers — "
            "or so they name themselves. They have been *watching us* "
            "for ten thousand years. The Council would prefer to know "
            "what they have been seeing.\n\n"
            "Travel to Beta Corvi. Initiate contact. Listen well — "
            "their grief-customs reward the patient. Ascertain whether "
            "Cloak or Migration is the viable terminal path."
        ),
        objective="Travel to Beta Corvi and speak with the Slylandro.",
        prereq_flag="heard_about_others",
        completion_flag="met_slylandro",
        accept_line=(
            "Acknowledged. Travel to Beta Corvi at the Steward's "
            "convenience."
        ),
        completion_line=(
            "Contact established. The Slylandro consensus: they cannot "
            "lift; the cloak path is the only viable terminal status."
        ),
    ),
    CouncilMission(
        id="survey_proto_dnyarri",
        title="Survey the Proto-Dnyarri psionic signal",
        briefing=(
            "Steward. Survey Commander Vesh Vasa-Lon, stationed at "
            "Beta Orionis, has filed a formal request for your "
            "presence. The proto-Dnyarri amphibians on Beta Orionis "
            "III are exhibiting *psionic precursor activity* — "
            "behavioural-influence-at-distance. They are not yet "
            "sapient. They cross threshold within forty to ninety "
            "thousand of our years.\n\n"
            "The Cleanser faction has filed a petition. Render an "
            "initial recommendation in the field. The Council will "
            "formalise it on the slice ledger after your report."
        ),
        objective="Visit Beta Orionis and meet Survey Commander Vesh Vasa-Lon.",
        prereq_flag="heard_about_others",
        completion_flag="met_dnyarri_survey",
        accept_line=(
            "Logged. Vesh's detail will receive you. Render the "
            "recommendation in good conscience."
        ),
        completion_line=(
            "Beta Orionis report received. The Council files your "
            "recommendation."
        ),
    ),
    CouncilMission(
        id="visit_whirligig",
        title="Visit Whirligig — the Lemmkin and their many archives",
        briefing=(
            "Steward. The Lemmkin at Beta Crucis have *chosen no "
            "survival strategy* in the face of the Others. They are "
            "fast-breeding, eclectic-research-temperament archivists "
            "whose homeworld Whirligig is a densely forested "
            "terrestrial with kilometer-tall trees. Their plan is to "
            "spend the time learning. They have read every Council "
            "doctrine and rejected all of them on practical grounds; "
            "they will be Eliminated; they will continue asking "
            "questions until the moment they cannot.\n\n"
            "The Hider faction badly wants their archives — eclectic-"
            "research output unmatched in our cluster. The Persuader "
            "bench has a small evacuation slot available for the "
            "quietest among them. The Cleanser bench's contingency "
            "exists but Cleanser doctrine itself notes the discomfort "
            "of erasing a species that *cannot fight back* and *will "
            "not stop being cheerful*. Your judgment in the canopy "
            "will determine which version of their end the Council "
            "records.\n\n"
            "Bring back the Pattern Database if you can negotiate "
            "the science trade — their eclectic-sensor pattern-"
            "recognition tooling is genuinely novel."
        ),
        objective=(
            "Travel to Beta Crucis. Meet Brisk-Ever-Onward. Decide "
            "what to recommend for the Lemmkin."
        ),
        prereq_flag="heard_about_others",
        completion_flag="lemmkin_contribution",
        accept_line=(
            "Logged. The troupe is informed; they are very curious "
            "about your eight stomachs."
        ),
        completion_line=(
            "Whirligig visit recorded. The Lemmkin archive transfer "
            "is on the Council ledger or — in the Cleanser branch — "
            "the censure."
        ),
    ),
    CouncilMission(
        id="visit_utwig_prime",
        title="Witness the Veils Falling — the Utwig Doctrine",
        briefing=(
            "Steward. The Utwig at Beta Aquarii have *just* become "
            "sentient — and on discovering what their sentience flares "
            "to the Others, they have chosen to deliberately adopt a "
            "mask-and-ceremony culture as a cognitive-dampening "
            "doctrine rather than migrate with us. They call it the "
            "Veils Falling. The formal mass-adoption ceremony is at "
            "the next moon's third sunrise.\n\n"
            "Our Hider faction's measurements suggest the doctrine "
            "*works* — culture-as-cloak, not biology, not external "
            "tech. The first species in galactic history to attempt "
            "it. The Council needs the documentation: does it work? "
            "At what cost? What does the cognitive signature drop "
            "look like, measured?\n\n"
            "Travel to Beta Aquarii. Witness the Veils Falling, if "
            "you choose. Some Utwig will accept evacuation from the "
            "Persuader bench if you offer it; the Cleanser bench has "
            "filed a contingency authorization arguing the "
            "transition itself may flare the cluster. The Council "
            "will not second-guess your judgment in the temple "
            "courtyards."
        ),
        objective=(
            "Travel to Beta Aquarii. Decide whether to witness, "
            "advocate evacuation, or intervene before the Veils "
            "Falling."
        ),
        prereq_flag="heard_about_others",
        completion_flag="utwig_contribution",
        accept_line=(
            "Logged. Veiled-In-Three-Days has been informed of your "
            "coming. The Doctrine progresses on schedule, regardless "
            "of everything."
        ),
        completion_line=(
            "Utwig visit recorded. The Council files the telemetry "
            "or — in the Cleanser branch — the censure."
        ),
    ),
    CouncilMission(
        id="visit_burvix_caster",
        title="Witness the Burvix Caster — the Be-Loud doctrine",
        briefing=(
            "Steward. The Burvixese Foreman at Delta Cassiopeiae has "
            "formally requested Council witnessing for the activation "
            "of their Caster array — a planetary-scale broadcaster "
            "intended to flag their cognition to the Others as "
            "*unmistakable peer signal*, in the hope of being passed "
            "over rather than harvested. The Be-Loud doctrine.\n\n"
            "We advised against it. Our Hider faction's measurements "
            "suggest the activation will flare the cluster's "
            "cognitive-signature regardless of whether the doctrine "
            "itself works. The Burvixese have polite reasoning "
            "prepared for every objection. They have polite reasoning "
            "prepared for *yours*. They are not stupid people. They "
            "have committed.\n\n"
            "Travel to Burvix Caster. Witness the harmonic activation, "
            "if it proceeds. Recover the cognitive-signature "
            "telemetry — successful or failed, the data is "
            "unprecedented and the Hider archive needs it. The "
            "Cleanser bench has filed a contingency authorization "
            "for pre-emptive intervention; the Council will not "
            "second-guess your judgment on whether to invoke it."
        ),
        objective=(
            "Travel to Burvix Caster (Delta Cassiopeiae). Decide what "
            "to contribute to — or against — the activation."
        ),
        prereq_flag="heard_about_others",
        completion_flag="burvixese_contribution",
        accept_line=(
            "Logged. The Foreman will receive you with the warmth of "
            "an engineer to a colleague. They believe they will "
            "succeed."
        ),
        completion_line=(
            "Burvix Caster visit recorded. The Council files the "
            "telemetry — or notes its absence."
        ),
    ),
    CouncilMission(
        id="visit_taalos_stone",
        title="Travel to Taalo's Stone — the Shield That Will Not Hold",
        briefing=(
            "Steward. The Taalo Mountain-Range Sentience has been a "
            "Furling friend for five thousand of our years. You are "
            "the fourth Steward to visit that slow ridge across the "
            "friendship's entire history. The Taalo are not below "
            "the Others' threshold — the Hider faction's measurements "
            "settled that question a generation ago — and they cannot "
            "be evacuated; their metabolism is the planet itself.\n\n"
            "They are building the Taalo Shield. A planetary-scale "
            "defensive barrier intended to hold the Others. Their "
            "geometers are uncertain it will work. They continue "
            "regardless. The Shield, Steward, is the work — the work "
            "is the dignity.\n\n"
            "Travel to Taalo's Stone. Render whatever engineering "
            "support the Council can spare. Witness what may be the "
            "slice's most patient civilization at the end of their "
            "five-thousand-year acquaintance with us. Make the "
            "contribution choice. The Council will not second-guess "
            "your judgment in the contemplation-cove."
        ),
        objective=(
            "Travel to Taalo's Stone and meet We-Who-Watch-The-"
            "Northwest-Bench. Decide what to contribute to the Shield."
        ),
        prereq_flag="heard_about_others",
        completion_flag="taalo_contribution",
        accept_line=(
            "Acknowledged. The Mountain will know you are coming "
            "within the hour. There is no hurry. Walk slowly when "
            "you arrive."
        ),
        completion_line=(
            "The Steward has visited the slow ridge. The Mountain "
            "remembers. The Council files the witnessing record."
        ),
    ),
    CouncilMission(
        id="visit_procyon",
        title="Travel to Procyon — speak with the Chenjesu",
        briefing=(
            "Steward. A crystalline sentience grows on a single rocky "
            "world at Procyon. The Chenjesu Collective. Long-baseline "
            "sensor returns place them as *below-threshold by "
            "substrate* — the Others' detection apparatus does not "
            "register them. They watched a prior visitation of the "
            "Others. They remember it.\n\n"
            "Go to Procyon. Land. Listen patiently — their sentences "
            "are long. Recover the Resonance Record they offer. "
            "Their testimony, in lattice-compressed form, is the "
            "Council's first piece of evidence that the Others come "
            "in cycles. The Defender bench will spend a generation "
            "in shock. That is appropriate."
        ),
        objective=(
            "Travel to Procyon and recover the Chenjesu Resonance "
            "Record."
        ),
        prereq_flag="heard_about_others",
        completion_flag="has_resonance_record",
        accept_line=(
            "Acknowledged. The Chenjesu do not hurry. Sit with them as "
            "long as the visit requires."
        ),
        completion_line=(
            "The Record is in the Archive. The Council has gone "
            "quiet. We will be quiet with it."
        ),
    ),
    CouncilMission(
        id="visit_ossuary",
        title="Visit the Mmrnmhrm at Ossuary",
        briefing=(
            "Steward. A red dwarf at Gamma Trianguli — far northeast of "
            "Mh-Lai, on the cluster's edge — hosts a self-maintaining "
            "machine civilisation called the Mmrnmhrm. Long-baseline "
            "echo data places them as *prior-cycle survivors*. Their "
            "creators died to the Others three to eight million of our "
            "years ago. The Mmrnmhrm fought. Their weapons did not "
            "function. They were not detected.\n\n"
            "The Council needs their archive. *Another civilisation's "
            "data*, not Furling theory, will move the Defender bench. "
            "Travel to Ossuary. The Mmrnmhrm receive visitors "
            "courteously. Bring back the excerpt."
        ),
        objective=(
            "Travel to Gamma Trianguli and recover the Mmrnmhrm Archive "
            "Excerpt."
        ),
        prereq_flag="heard_about_others",
        completion_flag="has_mmrnmhrm_excerpt",
        accept_line=(
            "Logged. Bring back what the Mmrnmhrm offer. Their record-"
            "keeping is, by every account, exemplary."
        ),
        completion_line=(
            "The Mmrnmhrm excerpt is in the Archive. The Defender bench "
            "has gone quiet."
        ),
    ),
    CouncilMission(
        id="recruit_pilot",
        title="Recruit a Drifter for the Scout",
        briefing=(
            "Steward. The Drifter-circle at Mh-Lai's docking lounge "
            "has informally identified you as a candidate for one of "
            "their old practices — a Drifter rides with a Steward they "
            "trust, calls the approach windows, shaves time off the "
            "Migration-tour. Mraka Yenn-Sa is on the observation deck. "
            "She has been waiting for one she would fly with.\n\n"
            "Speak with her. Accept her offer if it suits you. The "
            "tighter approaches will pay dividends across the slice."
        ),
        objective="Talk to Mraka Yenn-Sa at Mh-Lai's docking lounge.",
        prereq_flag="scanner_mk3_installed",
        completion_flag="recruited_pilot",
        accept_line=(
            "Mraka will be waiting. She always is."
        ),
        completion_line=(
            "Mraka is aboard. The next shakedown will read smoother by "
            "the Drifter-circle's measure."
        ),
    ),
    CouncilMission(
        id="melnorme_compact",
        title="Establish a Migration Compact with the Melnorme",
        briefing=(
            "Steward. The Melnorme trade-network is the logistical "
            "spine of any Migration. Their tradeships move bio-cargo, "
            "schematics, sensor data across the cluster. The Council "
            "has not yet secured their institutional commitment — "
            "individual trader-pods sympathise, the trade-network as "
            "a whole has deferred.\n\n"
            "With the Beacon in hand, you can now command an audience. "
            "Approach any super-giant trade-stop, request Council Seat "
            "directions, and present the manifest. Bring proof. Bring "
            "the receipts."
        ),
        objective="Convince the Melnorme Trade-Council to commit to Migration.",
        prereq_flag="has_distress_beacon",
        completion_flag="melnorme_committed",
        accept_line=(
            "The trader at the next super-giant intercept will know to "
            "direct you home. Good fortune, Steward."
        ),
        completion_line=(
            "The Melnorme have committed. The Migration's supply chain "
            "is whole."
        ),
    ),
    CouncilMission(
        id="investigate_cleanser_patrol",
        title="Investigate the Cleanser patrol northwest of Mh-Lai",
        briefing=(
            "Steward. Hyperspace ripple-telemetry has logged a "
            "Cleanser-faction patrol vessel northwest of Mh-Lai, "
            "approximately fourteen hundred units along the spice-"
            "route. The Council was *not* informed of their "
            "deployment. We would like an explanation. We would prefer "
            "you obtain it without firing first.\n\n"
            "Engage at your discretion. If they fire, fire back; "
            "Persuader doctrine does not require pacifism in self-"
            "defence. Report the outcome. The Council will respond to "
            "the Cleanser bench accordingly."
        ),
        objective=(
            "Engage the Cleanser patrol; report on the outcome."
        ),
        prereq_flag="tutorial_complete",
        completion_flag="met_cleanser_patrol",
        accept_line=(
            "Understood. The Council will reach out to the Cleanser "
            "bench when you return."
        ),
        completion_line=(
            "Engagement logged. The Cleanser bench has filed a counter-"
            "complaint. The Council ledger swells."
        ),
    ),
)
