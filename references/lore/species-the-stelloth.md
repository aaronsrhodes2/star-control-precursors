# The Stelloth — *The Bargainers* (three-body chord-beings; Precursor-faction artifact-traders)

> Authored 2026-05-17 (Skippy creative pass). Replaces the THE_BARGAINERS
> placeholder row in the species spreadsheet. Aaron's brief: "go exotic."
> Exotic vector: **a single Stelloth individual is THREE coordinated bodies
> linked by biological cords, each body operating at a DIFFERENT perceptual
> timescale.** They cannot act unless all three are aligned.

## The Concept

A Stelloth individual is a **chord** — three specialized bodies bound by
braided biological cords (the *murrer*). The bodies are:

- **The Speaker** — operates in normal time. Talks. Negotiates. The front-
  body the visitor interacts with.
- **The Witness** — operates in *fast-motion perception* (~4× the Speaker's
  perceptual rate). Sees every micro-expression, every contractual nuance,
  every twitch the Speaker is too busy to notice. Records via head-mounted
  cognition-crystals that the Witness can later replay for the chord.
- **The Counter** — operates in *deep-time calculation* (~1/10 the
  Speaker's perceptual rate). Slowly evaluates the long-term ramifications
  of every transaction. Clicks shells on its own abdomen at a slow
  metronomic tempo — the click rhythm is the chord's external indicator
  of how the Counter feels about the deal.

A Stelloth **cannot make a contract** unless all three bodies are present
and aligned. A chord-fragment (a Stelloth missing one of its bodies)
becomes paralyzed and goes catatonic until a new third can be cultivated
or borrowed from another chord. **They take partnerships very seriously
because they are physically incapable of doing anything important alone.**

This is why they're the slice's *Bargainers*: their entire civilization
is structured around *the careful contract*. Their economic and legal
system is the most rigorous in the cluster. The Furlings find this
useful and unsettling in equal measure.

## Body Plan

- **Form**: tall, thin, mantis-like — each body is ~1.8m, jointed
  exoskeleton, four delicate manipulator-limbs per body. Twelve limbs
  total across the chord. They move in choreographed-tripartite
  coordination — when the Speaker steps forward, the Witness shifts
  laterally to maintain sight-line, the Counter holds position to
  preserve the cord-tension.
- **The Murrer (binding cords)**: braided biological cords ~1m long
  connecting the three bodies. Severable but lethally so — cutting a
  murrer collapses the chord-cognition and all three bodies die within
  hours. The murrer carries hormonal, electrical, and chemical
  signals between bodies.
- **Carapace**: dark pearl-grey with iridescent green-violet sheen.
  The Counter's carapace is patterned with the chord's *ledger-marks* —
  a visible record of contracts honored, contracts broken, partnerships
  ended. New chords have unmarked carapaces; ancient chords carry
  centuries of ledger-history.
- **Eyes**: large multifaceted compound eyes. The Witness has the most
  developed eyes (essentially head-mounted recording apparatus). The
  Counter has the smallest eyes (mostly closed; deep-time perception
  doesn't require fast visual input).
- **The Speaker's mouth**: a vertical chitinous slit at the front of
  the body. The Speaker's voice resonates through chest-plate vibration.
- **The Witness has no mouth**: communicates only through clicked
  signals to the chord internally.
- **The Counter has a small ventral mouth**: speaks rarely, in deep slow
  tones, usually only at the chord's most weighty moments.

## Voice (the chord)

- **Three-voice harmonic chord**: when a Stelloth "speaks," all three
  bodies contribute. The Speaker delivers the words. The Witness adds
  high-pitched click-emphasis at moments of contractual significance.
  The Counter adds low-tone bass-affirmation at moments of long-term
  consequence. Together they form a *chord* — three voices in different
  registers, slightly offset in cadence.
- **Sample line** (greeting the Steward):
  > **Speaker** *(formal, clear, modulated)*: "Steward. We are the
  > Stelloth. We are interested in your story."
  > **Witness** *(high click-emphasis, ~0.2 seconds before the Speaker
  > finishes "story")*: *click-click* (interest spike; the Witness has
  > noticed the Steward's quasispace cargo-residue).
  > **Counter** *(deep slow bass, ~1.5 seconds after the Speaker
  > finishes)*: "We will trade."
- **Pronouns**: first-person plural always ("we who chord," "the
  three-of-us") — never singular.
- **Tone**: formal, precise, *patient with the trade but impatient
  with vagueness*. They want clarity. Verbal handwaves frustrate them.
  The Witness will *click-correct* the Speaker mid-sentence if the
  phrasing is loose.
- **The chord can disagree internally**: rarely, the Counter's bass
  will *contradict* the Speaker's offer (a held low-tone of refusal).
  When this happens, the Speaker stops mid-sentence and re-negotiates
  with itself in front of the visitor. It is unsettling and ethically
  reassuring.

## Faction Alignment

**Precursor (Stay-Go)**, with a twist: the Stelloth are *not native to
the slice cluster*. They are visitors — a Migrating chord-fleet that
came through hyperspace to *collect* cultural artifacts from
endangered civilizations before the Culling, with the intent to carry
the artifacts to Andromeda as cultural memory.

Their chord-fleet flies between super-giant trading posts and active
slice species, paying for artifacts in:
- **Rare minerals** (BIO, ENERGY)
- **Stelloth contracts** (formal letters of obligation, redeemable
  in the post-Migration galaxy)
- **Long-time pattern information** (Counter-perceived deep-time
  predictions about the buyer's future — *"You will need water in
  the year of the third Cleanser vote"* — accurate, vague,
  expensive)

They will Migrate with the Furlings. **Terminal: Migrated.**

## In the Slice

**Encounter location**: a different super-giant from the Melnorme
trading posts — the Stelloth occupy a specific super-giant the
Steward can find via the canonical Stelloth Beacon (a quasispace
echo distinct from the Melnorme's ionization pattern). One Stelloth
chord-vessel orbits there: the *Three-Voice Arc*. The Steward can
visit anytime after the tutorial.

**Encounter shape**: the Speaker greets formally; the Witness scans
the Steward's cargo (and notices everything — including artifacts
the Steward forgot they had); the Counter clicks shells slowly
while evaluating. The trade is conducted carefully; contracts are
inscribed on shell-plates the Steward receives as proof.

**What they want**: cultural artifacts from slice species. Lemmkin
archives, Burvixese audio recordings, Utwig pre-doctrine voice
samples, Taalo shield-fragments, Androsynth shear-injury-pattern
data, Thinn shed-ribbon iridescence samples, etc. They pay for each
based on Counter-evaluated rarity.

**What we want**: rare resources, deep-time predictions, and a
network of post-Migration Stelloth contacts in Andromeda (cosmetic
slice-epilogue flavor + lore-info modules).

**Quest** `stelloth_artifact_trade` in `tools/quest_inventory.csv`:
branches honest-trade (standard) / hide-something-the-Witness-finds
(reputation collapse — the Stelloth refuse to trade with you again
unless you make formal restitution) / Cleanser-pressure (Council
asks if the Stelloth's traffic in dying-civilization-cognition is
suspicious; the Stelloth politely refuse to be euthanized, and they
are *correct* — Cleanser doctrine doesn't apply to Migrating species).

## Ship — The Stelloth Three-Voice Arc

A trading vessel, not a combat ship. ~140 points, hull 80, shields 30,
medium speed, mediocre maneuverability. Glass cannon? No — *trader*.

- Primary: **Contract-Resonance Lance** — a kinetic-binding beam that
  *binds* an enemy ship's drive systems briefly (slows them ~30% for
  3s). Damage low but the binding effect is the value
- Special: **Chord-Witness Scanner** — passive ability; once per fight,
  reveals the enemy ship's hidden stats (cargo, fuel, faction-standing
  with the Stelloth). Information-warfare flavor; doesn't damage
- Defensive: shields recharge unusually fast when not under fire (the
  chord-coordination effect: when not pressured, the chord realigns
  efficiently)
- AI style: defensive-trader; flees if pressed; will not initiate combat

## Visual canon (for Image chat)

- **Body**: three-body mantis-stack linked by braided cords; dark
  pearl-grey carapace with green-violet iridescent sheen; the Counter
  at the back has ledger-marks (visible scribed-shell patterns); all
  three bodies in synchronized choreographed pose
- **Eye sets**: Speaker normal, Witness huge multifaceted, Counter
  small and partially closed
- **Color cue**: the chord glows faintly when *all three are aligned* —
  a subtle harmonic-yellow glow along the murrer cords. When the chord
  is mid-disagreement, the glow flickers asymmetrically
- **Trading vessel exterior**: an elegant elongated craft, three
  sections linked by visible tethers (mirroring the chord-body); each
  section operates semi-independently; the ship has its own three-fold
  asymmetric design

## Authoring Notes

- **Don't make them sinister.** The Stelloth are *formal*, not menacing.
  They treat every contract with extraordinary care. Their unsettling
  quality is in the *attention* — they notice things, they remember
  things, they wait patiently while the Counter calculates.
- **The Witness as joke material**: the Witness's high-click-emphasis
  is a recurring small-comedy beat — every time the Steward says
  something vague or evasive, *click-click*, the Counter pauses; the
  Speaker re-asks for clarity. The protagonist's humor doctrine works
  well here.
- **Their named NPC**: **Tarvel-Three-Voices** (the chord-name; the
  Speaker, Witness, and Counter share this designation). When asked
  individually, each body identifies as a *facet* of the chord: *"I am
  Tarvel-Speaker, of Tarvel-Three-Voices,"* etc.
- **Slice positioning**: optional super-giant encounter; parallel-but-
  distinct from the Melnorme. The Stelloth-Melnorme distinction in
  trade currency (BIO vs artifacts) keeps both vendors meaningful.
