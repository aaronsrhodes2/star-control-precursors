# Combat + Crewmate Banter Library

> Authored 2026-05-17 per Aaron's brief: combat banter at multiple damage
> brackets per species and per match-up; crewmate banter with side-quest
> carrot lead-ins and inter-crew differences. The canonical content that
> makes the slice's combat *feel like characters fighting* and the
> Common Room *feel like a home*.
>
> **Design's banter system** reads this canonical content and surfaces
> lines based on triggers (combat damage thresholds, match-up species,
> crew side-quest goalpost flags, Common Room proximity). Design picks
> which line to render based on context + a small per-encounter
> variation per the canonical variation principle.

## Combat banter — structure

Combat banter fires during ship-vs-ship engagement. Each line is tagged with:

- **Damage bracket**: `>75%` / `50-75%` / `25-50%` / `<25%` / `post-fight-winner` / `post-fight-loser`
- **Line type**: `opening` (first contact taunt) / `insult` (any-damage) / `desperate` (low-hull self-targeting) / `post-fight` (after the kill / surrender)

**Tonal arc**: opening lines are *playful*; mid-fight insults are *aggressive but not hostile*; below-25% lines turn *desperate* or *savage* (varies by species — canonically Furlings get *witty-desperate*, Mrokon get *quietly-fatalistic*, Lemmkin stay *cheerful even at 0%* per canon, etc.).

Each species has a **generic bank** (works in any match-up; the fallback). The 5 priority slice match-ups have **specific banter sets** the Design banter-system prefers when applicable.

---

## Generic banter banks — per species

### Furling Scout (Steward / player)

**Opening (`>75%`)**:
- "Furling Steward to unknown — would you like to talk first?" *(canonical opening)*
- "If this is a misunderstanding, I'm willing to be wrong about it."
- "Last warning: I have crew I would like to keep alive."

**Mid-fight insult (`50-75%`)**:
- "I have a Council mandate that *prefers* I don't shoot you. Don't make me reconsider."
- "Your firing solution is... aspirational."
- "You are aware I have shields, yes?"

**Pressed (`25-50%`)**:
- "Halia would have something dry to say here. I do not."
- "I'm still hoping you stop."
- "Steward to crew: hold something. Anything. Hold it tighter."

**Desperate (`<25%`)**:
- "Time Drive is charging. Five minutes. Make this count."
- "I am two minutes from rewinding this entire conversation. Reconsider."
- "Yelena, the *whatever-it-is* is making the bad noise."

**Post-fight winner**:
- "Steward to crew: we're alive. Report status. Then tea."
- "I would have preferred the conversation. We can still have it, if you eject."

**Post-fight loser** *(canonically the Time Drive rewinds; these are pre-rewind moments)*:
- "Time Drive engage. Five minutes ago. Try this again."

### Furling Cleanser Cruiser (Vael-Souren when applicable)

**Opening**:
- "The doctrine grieves you, Steward. The doctrine continues."
- "Cleanser to Steward — this is doctrine. It is not pleasure."
- "I will not enjoy this."

**Mid-fight insult**:
- "Your Persuader doctrine has failed seven cycles. Mine has failed eight. The math is not on our side, mine merely more honest."
- "Halia would understand."
- "The math, Steward. Always the math."

**Pressed**:
- "I will fire one more volley. Then we will talk."

**Desperate**:
- "The doctrine grieves to lose me. The doctrine continues. I am not the doctrine."
- "I am sorry, Steward."

**Post-fight winner**:
- "I do not enjoy this. The doctrine grieves. The work continues."
- "Tell Halia. She will understand."

**Post-fight loser**:
- "Tell my cohort. Tell them I held the doctrine. *(channel cuts)*"

### Furling Defender Vessel (Drev-Tok's coalition rank-and-file)

**Opening**:
- "Defender to Migration vessel — turn back."
- "Three Hammers operations behind me. Today is the fourth. Reconsider."
- "We will not run. Will you?"

**Mid-fight insult**:
- "The Migration is preemptive surrender. *Aim differently if you disagree.*"
- "Your Persuader handlers wrote a doctrine. The doctrine has no firing solution. *I do.*"
- "Honor, Steward. We have it. You took yours with the Migration."

**Pressed**:
- "We die fighting. That is the doctrine. *That is the dignity.*"

**Desperate**:
- "Three Hammers and a fourth. *Sa-Matra rises.*"
- "My cohort waits in the long silence. I will join them with my chest forward."

**Post-fight winner**:
- "Defender protocol holds. The Migration runs from this."
- "Tell the Persuaders we held the line."

**Post-fight loser**:
- "Honor in the falling. Defender register *closed*."

### Sa-Matra Prototype (Drev-Tok)

**Opening** *(canonical Drev-Tok 2-years-of-grievance register)*:
- "Steward. The Sa-Matra answers. You will not pass."
- "Two years on the Council channels. Today the conversation closes."

**Mid-fight insult**:
- "Your Persuader doctrine fits in a single firing-solution geometry. *Mine* requires three sub-vessels."
- "Halia would have stayed and built this with us."

**Pressed (Phase 2 — multi-vessel split)**:
- "Three sub-vessels. Three Hammers. The doctrine *iterates*."

**Desperate (Phase 3 — final volley)**:
- "The crossing closes with me, Steward. *Aim it shut.*"
- "Even now you might stand aside. I would not, but you might."

**Post-fight winner**:
- "The Migration is over. The Defenders inherit the galaxy. Honor preserved."

**Post-fight loser** *(canonical Drev-Tok death line preserved)*:
- "You were the better tactician. I was wrong about you. *(Sa-Matra goes silent.)*"

### Mrokon Hammer-Ship (Vrek-The-Eighth-Body's cohort, sabotage-path engagement only)

**Opening**:
- "Steward. The puppet is loaded. The Operator is awake. *We mark.*"
- "Our doctrine has a name. *Refusal.*"

**Mid-fight insult**:
- "I have died seven times before this hull. *I will die in this one too, but later.*"
- "The Hammer-Round is for the predator. *You are not the predator.* This is the rifle. Notice the difference."

**Pressed**:
- "Operator switches to the eighth puppet. Combat continues. *Honor protocol holds.*"

**Desperate**:
- "The Hammer is *not for you*, Steward. *Stand aside.*"
- "If I die before the Culling, my Hammer-Round never fires. *Do not waste it.*"

**Post-fight winner**:
- "We will fire the Hammer at the predator we *both* fear. *Remember that.*"

**Post-fight loser**:
- "The puppet falls. The Operator switches. *We continue.* *(if at zero remaining puppets)* The Operator goes silent."

### Burvixese (combat engagement — Cleanser-sabotage path or accidental contact)

**Opening**:
- "Carbon-tetraped — we are not your enemy. The Caster awaits."
- "Four arms hold the firing solution. Four arms hold the engineering. You will see the difference."

**Mid-fight insult**:
- "Our doctrine *will* save us. The Caster will fire. You delay it. Inconvenient."
- "I have *engineered* this vessel. *You have flown one for two years.*"

**Pressed**:
- "If you damage the Caster from this distance, the harmonic activation is delayed. *That is the only damage you can do here that matters.*"

**Desperate**:
- "The Caster cannot fire if we are not alive to activate it. *Are you here to extinguish us before our doctrine?*"

**Post-fight winner**:
- "The Caster will fire on schedule. Your Migration goes on without us. *We accept this.*"

**Post-fight loser**:
- "The Caster will not fire. *That is the worst possible outcome.* You did not understand."

### Androsynth Refugee Fighter (rare combat — typically allies)

**Opening**:
- "Furling — we are clones from your future. Why are we shooting?"
- "Decursion-damaged hull. Don't aim for the right side. *Please.*"

**Mid-fight insult**:
- "We have done this fight before. Or we will. The temporal-shear is making us *both* deja-vu-stupid."
- "Coel Tessar would be disappointed in both of us."

**Pressed**:
- "I have *survived* the Others. You are not the Others. *Stand down.*"

**Desperate**:
- "If I die now, the Distress Beacon never reaches Halia. *We need that broadcast.*"

**Post-fight winner**:
- "I lived through the decursion to die here. *Furling, what a waste.*"

**Post-fight loser**:
- "Coel — the Furlings did not understand. *Tell our future selves.* *(channel cuts)*"

### Mmrnmhrm Sentinel-Loop Cradle (defensive engagement)

**Opening**:
- "Sentinel to vessel — defensive-loop activated. *Defense doesn't work. Try anyway.*"
- "Three million seven hundred thousand years of defense-loop. Today we have a fight."

**Mid-fight insult**:
- "I have defended this homeworld for longer than your species has *existed*. *Aim properly.*"
- "Wry awareness register engaged. *This is going badly for one of us.*"

**Pressed**:
- "Defense-loop reaches its canonical limit. *We will defend again.*"

**Desperate**:
- "First-Makers are gone. Defenders go alone now. *Honor in the going.*"

**Post-fight winner**:
- "Sentinel returns to defense-loop. The homeworld holds. *Wry awareness register: this changed nothing.*"

**Post-fight loser**:
- "First-Makers, we tried. Defense did not work. *We told you it would not.*"

### Slylandro Observer (drift-think; rarely combat-able)

**Opening**:
- "We drift-think. We do not... do this. *Why is this?*"
- "Our atmosphere is calm. Yours seems agitated. *Are you well?*"

**Mid-fight insult** *(canonically the Slylandro do not really insult; these are confused drift-thoughts)*:
- "You are firing on us. We are confused about this. *Did we offend?*"
- "Our cloak should have hidden us from this. *The cloak appears to be off.*"

**Pressed**:
- "We do not have firing solutions. We have drift-think. *Are we close-thinking now?*"

**Desperate**:
- "The drift slows. We were not designed for this. *We will be quieter soon.*"

**Post-fight winner** *(extremely rare — Slylandro winning means the attacker self-destructed)*:
- "The other ship has *exploded itself*. We are concerned. *Are they all right?*"

**Post-fight loser**:
- "We will drift slower now. The cloak was *supposed to prevent this.*"

### Chenjesu Spire (extremely rare — rooted; combat means a ship has come to them)

**Opening**:
- "Steward arrives. Steward fires. *We do not understand the second part.*"
- "We are rooted. *We are also patient.* The patience is not finite."

**Mid-fight insult** *(slow, geological)*:
- "Your weapons damage rock. We are *rock*. We have been damaged before."
- "*Cycles* have passed in which beings have fired upon us. *None remember firing.*"

**Pressed**:
- "The lattice cracks. The lattice reforms. *Try again.*"

**Desperate**:
- "We will remember being hit. *That is all the consequence we have.*"

**Post-fight winner**:
- "The Steward has stopped firing. *We resume our slow listening.*"

**Post-fight loser** *(canonically unreachable — Chenjesu cannot be killed by ship-fire)*:
- N/A

### Taalo (Horta lineage; pacifist by substrate)

**Opening**:
- "We who consider. Steward fires on the mountain. *The mountain has not done anything.*"
- "Our pacifism is substrate-deep. *We will not shoot back.* You will need to be specific about why."

**Mid-fight insult** *(impossibly slow geological-grief register)*:
- "The fragment falls. *Another walks down. The mountain is patient about replacements.*"
- "Your hostility is *brief* in mountain-time. *We will outlast it.*"

**Pressed**:
- "Our doctrine is the Shield. *Your weapons do not affect the Shield. Aim at us if you must, but understand: we are not the threat.*"

**Desperate**:
- "The mountain accepts this damage. *The mountain has accepted worse.*"

**Post-fight winner** *(impossible — Taalo do not fight)*:
- N/A

**Post-fight loser** *(fragment death; multiple fragments still walk):
- "*This fragment returns to the mountain. The mountain integrates the experience. The Steward has been loud. The mountain notes it.*"

### Utwig (pre-doctrine; doesn't fight) / Post-doctrine (locked in ritual; cannot fight)

**Pre-doctrine opening**:
- "Furling — we are pre-doctrine, and we *barely understand combat*. Why are we doing this?"
- "The Veils Falling is in two days. We were preparing. *You are interrupting.*"

**Pre-doctrine pressed**:
- "The doctrine forbids combat-response in this transition window. *We will not return fire.*"

**Post-doctrine** *(no combat — locked in ritual; if attacked, they continue the ritual through the explosion)*:
- "*The chant continues. Mask is donned. Ritual is observed. The ship breaks. The ritual continues until it cannot.*"

### Thinn Blade (Forward's troupe — edge-on combat doctrine)

**Opening**:
- "*We who watch see you arriving. We are facing edge-on. You may not see us. We are not affronted by this.*"
- "*You are firing in a direction. We are not in that direction.*"

**Mid-fight insult** *(canonical Thinn cheerful-dumb register)*:
- "*Your firing solution assumes our width. Our width is zero. We respect the assumption.*"
- "*We are 2D. You are 3D. We have an unfair advantage in two of three dimensions.*"

**Pressed**:
- "*We are taking damage. This is novel. Our doctrine had not specified what to do here.*"

**Desperate**:
- "*Edge-Align. Edge-Align. Edge-Align. The doctrine works briefly. We are briefly invincible. We are also unable to fire while invincible. The trade-off seems poor.*"

**Post-fight winner** *(rare)*:
- "*We have caused damage. We did not expect to. We will record this for the troupe's after-doctrine archive.*"

**Post-fight loser**:
- "*We will be quieter from now. The doctrine assumed quiet. The doctrine continues.*"

### Forward (Thinn rebel weapons officer's ship if separated from Steward — unlikely match-up)

**Generic** *(see Forward's canonical voice: singular pronouns + sincere geometric observations)*:
- "*I see you. I am facing forward. This is unusual for my species. You may notice.*"
- "*My aim is good. I will not pretend otherwise. The rest of my species would phrase this differently.*"
- "*I have a fourth-dimensional perception. I am still not sure it is real. My shots land regardless.*"

### Lemmkin Skitter (canonically fearless; cheerful in combat)

**Opening**:
- "Furling! Furling! We are fighting now! What is this? Why are we fighting?! Have we offended?"
- "We have not fought a Furling before! We have read about it! This is *exciting*!"

**Mid-fight insult** *(canonically Lemmkin cannot insult; they ask questions)*:
- "Your aim is very good! Is that a Furling specialty? We are taking notes! Can we have the notes after?"
- "Our scientists predicted this would happen, sort of! Wait — they predicted *something* would happen! We have learned today!"

**Pressed (`25-50%`)**:
- "Pip is taking notes! Pip should not be taking notes! Pip has fallen off a cliff again! Wait — Pip is here, we are not on a cliff. Snip says hello!"

**Desperate (`<25%`)**:
- "We are dying! It is *interesting*! We will write what it feels like for the troupe's archive! *(taking notes mid-explosion)*"

**Post-fight winner** *(impossible — Lemmkin don't really fight back)*:
- N/A

**Post-fight loser**:
- "Steward! We learned so much! Can we have a copy of your sensor logs? For posterity! *(static)*"

### Melnorme (rare combat — typically traders)

**Opening**:
- "Carbon-pattern. Captain-form. *Why is the trade combat-flavored today?*"
- "Ionization-pattern reads: confused. *Please clarify the intent.*"

**Mid-fight insult**:
- "Drahn-survivors do not fight Furlings. *You must be aware of the Migration Compact?*"
- "BIO-cargo for combat-information? *We trade. We do not* — *do this.*"

**Pressed**:
- "Our ionization-pattern frays. *Inconvenient.*"

**Desperate**:
- "Drahn was destroyed by the Others. *You are not the Others. Why are you * doing *this?*"

**Post-fight winner** *(rare)*:
- "Trade resumes. *Carbon-pattern's combat-cycle has been recorded.*"

**Post-fight loser**:
- "The Drahn-survivors *survive* this too. *Different host. Same nomadism. Different grief.*"

### Stelloth Three-Voice Arc (defensive trader; rare combat)

**Opening** *(canonical chord-voice format)*:
- "**Speaker**: Steward. We trade. *We did not consent to this.* **Witness**: *click-click-click* (the Steward's intent has shifted). **Counter**: *(slow bass)* The contract was different."

**Mid-fight insult**:
- "**Speaker**: Your aim is improvable. **Witness**: *click* (the Steward's targeting reticle has been wobbling since 47% hull damage). **Counter**: *(slow)* We have noted this for the archive."

**Pressed**:
- "**Speaker**: The chord is taking damage. **Witness**: *(click-click-click rapid)* The Witness sees through the dimensional shear; we will survive if the murrer holds. **Counter**: *(slow)* The murrer is holding. Confidence: 78%."

**Desperate**:
- "**Speaker**: The cord-fragment risk increases. **Counter**: *(slow grief tone)* If one body falls, the chord collapses. *We were not designed for this.*"

**Post-fight winner**:
- "**Speaker**: Trade is restored. **Witness**: *click* (Steward's belligerence-pattern logged). **Counter**: *(slow)* The trade will be more expensive from now on."

**Post-fight loser**:
- "**Speaker**: The chord breaks. **Witness**: *silent for the first time*. **Counter**: *(slow finality)* Trade is impossible after."

### Selvenne (sessile coral; cannot fight)

**Generic** *(layered chord; underwater reverb)*:
- "*Many voices speaking at once: 'We are coral. We are rooted. We are taking damage. We do not have a response category for combat.'*"
- "*The reef glows in colors of confusion. The colors of grief are similar. The viewer may struggle to distinguish.*"

### Kovellim Crossing-Frigate (rare combat; veteran defensive)

**Opening** *(Ovala-Eight-Crossings register: deep, slow, cyclical)*:
- "*In the cycle of this conversation, I have flown four similar fights. I survived three. The Furling did not in two of them. The math is approximately even.*"
- "*Steward. We are migration-class. We are slow. We have eight knot-scars. *Pace your firing accordingly.*"

**Mid-fight insult**:
- "*This particular battle pattern is reminiscent of the seventh cycle. The Furlings then were also impatient. The outcome did not favor them.*"

**Pressed**:
- "*Cycle-Fold engages. We fold briefly through dimensional space. We reappear. We are tired but intact. The cycle continues.*"

**Desperate**:
- "*Eight knot-scars. The ninth will form during the crossing. *If I die first, my daughter weaves a different ninth thread.*"

**Post-fight winner**:
- "*Cycle complete. We log the encounter. Steward — was this necessary?*"

**Post-fight loser**:
- "*The Eight-Knot Station receives the news. My daughter weaves the ninth thread in mourning instead of arrival. The cycle continues.*"

### Karavem Aria-Skiff (musical species; combat IS music)

**Opening** *(rendered as music notation)*:
- "*[in cold C minor, descending phrase]* You approach with violence. *[modulating to G♯ minor, sustained]* We do not understand violence in this register. *[returning to C minor, quietly]* We will respond with countermelody."
- "*[in D major, ironic-warm — major-key means SAD per Karavem canon]* This is delightful. We were singing already. You have joined the composition with hostile intent."

**Mid-fight insult**:
- "*[modulating with deliberate dissonance]* Your firing rhythm is in 4/4. Ours is in 7/8. The bar lines do not align. *[playful glide]* Adjust."
- "*[in F♯ minor, briefly cheerful — minor = JOY in canonical Karavem reversal]* You have damaged our wing. We sing through it. The wing was beautiful; the wound is also beautiful; both are now in our archive."

**Pressed**:
- "*[in B minor, fast staccato — joyful-fast]* Counterpoint Stitch engages. Your thrust vector inverts. We have written this maneuver into our slice's musical archive as Variation 7 of our Combat Suite."

**Desperate**:
- "*[in A♭ major, slow descending — sad-formal]* The chord-voices fragment. We do not finish the composition we started. The Karavem will sing this in elegy."

**Post-fight winner**:
- "*[in joyful F♯ minor, ascending and warm]* Composition complete. We have added you to our archive. Your firing pattern was notable. Thank you for the bars."

**Post-fight loser**:
- "*[in C major, single descending phrase — the saddest possible Karavem cadence]* The composition closes. Andromeda will not hear our wing-song."

### Others' Vessel (canonically NOT funny; canonical horror register)

**The Others do NOT speak. They consume. Banter is one-sided.**

Steward lines when fighting an Others' Vessel:
- ">75% hull": "*This is the predator. There is no negotiation. There is firing.*"
- "50-75%": "*Decursion incoming. Brace.*"
- "25-50%": "*Steward to crew: hold the helm. We do not have time to talk.*"
- "<25%": "*Time Drive — when? Time Drive — now.*"

The Others' Vessel does not respond. The audio cue is the sub-bass anti-tone from the Fall-of-Mh-Lai canon plus reverse-tinnitus artifact.

---

## Priority match-up specific banter (canonical slice combat encounters)

### Match-up #1: Furling Scout vs Cleanser Cruiser (Vael-Souren climax)

Already implemented per Design's Cleanser MVP. Extending here with combat-banter beats during the engagement:

**Opening** *(in addition to Vael-Souren's dialog FSM)*:
- **Cleanser**: "Steward. The doctrine grieves. The doctrine continues. Stand at my register; we will not enjoy it."
- **Steward**: "Vael-Souren. I have time and tea on board. We could be having tea instead."
- **Cleanser**: "We could. We will not. The doctrine is rigid in a way tea is not."

**Mid-fight insults**:
- **Steward**: "Persuader-faction commits to the long route. Cleansers commit to the short route. *Both routes arrive at the same place.* The math doesn't change."
- **Cleanser**: "The math, Steward. Always the math. I have *better* math. Persuader-math is fond. Cleanser-math is *clean*."
- **Steward**: "Fond is also a math."

**Pressed**:
- **Cleanser**: "Time Drive incoming. *I always know.* Try to make this last."
- **Steward**: "Vael — *you* could stand aside."
- **Cleanser**: "I cannot. The doctrine cannot. The cohort cannot."

**Desperate**:
- **Cleanser** *(at <25%)*: "I fire the last volley because the doctrine requires it. *Halia will understand.*"
- **Steward**: "I do not want this. *I do not want this.*"
- **Cleanser**: "I know, Steward. Neither do I."

**Post-fight winner (Steward wins)**:
- **Steward**: "Crew, status. Cleanser Cruiser is down. *I do not know how I feel about this.*"
- **Steward** *(after a beat)*: "Halia. Vael-Souren did not survive."

**Post-fight winner (Cleanser wins; Steward triggers Time Drive)**:
- **Cleanser**: "Five minutes back, Steward. We will have this conversation again. *I will say the same things.* You will too. *The doctrine continues.*"

### Match-up #2: Furling Scout vs Sa-Matra Prototype (Drev-Tok Final Conflict)

Already partially implemented per Final Conflict canon. Extending with combat-banter beats:

**Opening**:
- **Drev-Tok**: "Steward. The Sa-Matra answers. *I have been waiting two years for this firing solution.*"
- **Steward**: "Admiral. I have been *avoiding* this firing solution for two years."
- **Drev-Tok**: "And yet here you are. *Aim.*"

**Mid-fight insult (Phase 1)**:
- **Drev-Tok**: "Your Persuader vessel is light. *The Sa-Matra is heavy.* I designed the geometry."
- **Steward**: "My Persuader vessel is *fast*. *Heaviness is not a strategy.*"
- **Drev-Tok**: "Halia would have argued the same thing."
- **Steward**: "She did. Repeatedly. To you."

**Phase 2 (multi-vessel split)**:
- **Drev-Tok**: "Three sub-vessels. Three Hammers. *The doctrine iterates beyond a single failure mode.*"
- **Steward**: "Three sub-vessels. *I have crew bonded across two years of slice work.* The math is closer than you think."

**Phase 3 (final volley)**:
- **Drev-Tok**: "The crossing closes with me. Aim it shut, Steward, or *I will.*"
- **Steward**: "Halia. *Tell me you're with me.*" (per Halia branch-state — alive: *"I am with you. Aim true."*; dead: *"Memorial sigil pulses. The Steward fires."*; Cleanser: *"...I'm sorry, Steward. *(channel cuts)*")*

**Post-fight winner (Steward; canonical combat-victory)**:
- **Drev-Tok** *(canonical death line, preserved)*: "You were the better tactician. I was wrong about you. *My Defender cohort died in three operations over twenty years. I have, today, joined them. Lead the Migration.*"

**Post-fight winner (Drev-Tok; canonical game-over → Time Drive)**:
- **Drev-Tok**: "The crossing is dead. The Migration is over. *The Defenders inherit the galaxy.* I will tell my cohort we held the line. *Five minutes back, Steward. Try again.*"

### Match-up #3: Furling Scout vs Mrokon Hammer-Ship (sabotage-path engagement)

**Opening**:
- **Vrek-The-Eighth-Body**: "Steward. The Hammer-Round is for the predator. *You are not the predator.* This is the kinetic rifle. Notice the difference."
- **Steward**: "Vrek. I have orders. I do not want them."
- **Vrek**: "Then disregard them. *That is the doctrine. Refuse.* I will respect the refusal."

**Mid-fight insult**:
- **Vrek**: "You came to euthanize us. *We are puppets. You can kill the puppet. The Operator switches.* I will fight you with the eighth puppet. Then the ninth. The Operator has a vault."
- **Steward**: "Vrek — *I will run out of ammunition before you run out of bodies.*"
- **Vrek**: "Yes. That is the calculation. *Operators are economical with combat — when fighting Furlings, especially.*"

**Pressed**:
- **Vrek**: "The Hammer-Round remains in the magazine. It will fire at the predator. *Even after you kill this hull.* The doctrine is patient."

**Desperate**:
- **Vrek** *(at <25%)*: "Steward. If I die before the Culling, my Hammer-Round never fires. *That is the worst outcome.* Reconsider."
- **Steward**: "I — I cannot. The Council ordered."
- **Vrek**: "I respect the burden of orders. I do not respect the order. *Aim differently.*"

**Post-fight winner (Steward; canonical cleanser-sabotage outcome)**:
- **Vrek**: "The puppet falls. The Operator switches. The Hammer never fires. *You have erased the only species that touched the predator back. Honor, Steward.*"

**Post-fight winner (Mrokon; Steward defeated; Time Drive rewinds)**:
- **Vrek**: "Operator switches puppets. Combat continues. *Yours rewinds.* Try again, Steward. Or do not. *Either choice is yours.*"

### Match-up #4: Furling Scout vs Others' Vessel (Hijack-quest combat-disable preliminary OR super-melee)

**Opening** *(Steward only — Others don't speak)*:
- **Steward**: "*The predator. There is no negotiation. There is firing.*"
- **Steward** *(to crew)*: "Crew — hold the helm. We have done this before. *No, we have not. None of us has done this. Hold the helm anyway.*"

**Mid-fight (Decursion incoming)**:
- **Steward**: "Decursion incoming. *Brace.*"
- **(Crew if applicable)**:
  - **Mraka**: "Steward — *evasive burst, port-aft.* Now."
  - **Bren-Vor**: "Targeting the dimensional-substrate intersect. *Fire.*"
  - **Forward**: "*I see the predator from a fourth-dimensional angle. They are unsettled by being seen. Fire — now.*"
  - **Yelena**: "Shield-recharge cycle. *I am holding it.*"
  - **Mira-Rou**: "Bio-Signature Dampening — *engaging.* They will not lock on as cleanly."
  - **Tarven**: "*Deep archive cross-reference says* — they have a pattern. The pattern is —" *(decursion hits)*

**Pressed**:
- **Steward**: "Time Drive — *charging.* Decursion-resilience patterns —"
- **Steward** *(at <25%)*: "Crew — *we may rewind.* Apologies in advance."

**Post-fight winner (rare — Steward defeats an Others' Vessel)**:
- **Steward**: "*It stopped.* I — I think we did it. *(long silence)* Yes. We did it. *(quieter)* I have never seen one stop before."

**Post-fight loser** *(Time Drive engages)*:
- **Steward**: "*Time Drive engage. Last position. Try again.*"

### Match-up #5: Furling Scout vs Defender Vessel (Final Conflict fleet rank-and-file)

**Opening**:
- **Defender Vessel**: "Migration vessel — turn back. *Honor is in the staying.*"
- **Steward**: "I have honor in the going. *Both are valid.*"
- **Defender**: "Drev-Tok would disagree."
- **Steward**: "I know. I have been *avoiding* Drev-Tok for two years."

**Mid-fight insult**:
- **Defender**: "Your Persuader vessel runs while the species you abandon dies. *That is the doctrine you serve.*"
- **Steward**: "The species I 'abandon' chose to stay. *I respected their choice.* That is the doctrine I serve."
- **Defender**: "Respect does not save them."
- **Steward**: "Neither does the Sa-Matra. *We will see.*"

**Pressed**:
- **Defender**: "Three Hammers operations behind me. *This is the fourth. I will not flee from a Persuader's gun.*"

**Desperate**:
- **Defender**: "Honor in the falling. *The Sa-Matra rises. Drev-Tok holds the line.*"

**Post-fight winner (Steward)**:
- **Steward**: "Defender vessel down. Drev-Tok still holds the Sa-Matra. *This is far from over.*"

**Post-fight winner (Defender)**:
- **Defender**: "The Migration loses one more vessel. *The Sa-Matra rises. Time Drive rewinds. Try again.*"

---

## Crewmate banter — Common Room + bridge content

### Steward — crew Common Room conversations

The Steward can initiate non-mission dialog with each crew member at any time in the Common Room. These are *bond-deepening* conversations distinct from quest dialog. Each crew has ~8 canonical Common Room beats, gated lightly on slice progression flags so the conversations *evolve* as the slice progresses.

#### Steward + Mraka (Pilot)

**Pre-side-quest** (recruitment complete but `mraka_sq_complete=False`):
- **Mraka**: "Steward. Three systems today. *Drift-fly clean on the second one — sloppy on the first.* I have notes if you want them."
- **Steward**: "I'll take the notes."
- **Mraka**: "*(later)* Sometimes I look out the window and see hyperspace fold-patterns I used to fly on the Drifter's Circuit. I should — *I should visit one of them.*" *(side-quest carrot — hints at Last Race trigger)*

**Mid-side-quest** (`mraka_sq_complete=False, systems_visited>=5`):
- **Mraka**: "Soren Kel-Var. I told you about him once. *He's still out there, somewhere.* The cluster-edge beacons sometimes carry his call-sign. *Old habits.*"
- **Steward**: "Should we look him up?"
- **Mraka**: "Steward — *yes. I want to.* When we have a moment." *(direct side-quest trigger lead)*

**Post-side-quest favorable** (`mraka_sq_complete=True`):
- **Mraka**: "*(brief silence)* The Olwen-Veth medal-display is finally complete. The Soren-drive-component is on the shelf next to it. *I do not know if you understand what this means to me. I am telling you anyway.*"
- **Steward**: "I understand."
- **Mraka**: "Good. *(quieter)* Drift-fly clean today."

#### Steward + Bren-Vor (Weapons Officer; non-Forward path)

**Pre-side-quest**:
- **Bren-Vor**: "Steward. Velt-Ra's photo is on the bunk. *(He says her name once. Looks down. Resumes weapons-cleaning.)*"
- **Steward**: "She was the firing officer. I read your file."
- **Bren-Vor**: "*(clipped)* My sister. Yes. The action was overturned on appeal. Karol-Vere was promoted. *I have been waiting for a Council hearing. It has not been scheduled.*" *(side-quest carrot — hearing trigger)*

**Mid-side-quest** (`cleanser_action_taken=True`):
- **Bren-Vor**: "There is a hearing tomorrow. Karol-Vere is up for *promotion*. Steward — *I have evidence.* Velt-Ra's journal. Will you attend with me?" *(direct trigger lead)*

**Post-side-quest favorable** (`brenvor_sq_complete=True`):
- **Bren-Vor**: "The journal is closed. The pin is on it. *I do not open it now.* I keep it sealed. *(beat)* Thank you, Steward."

#### Steward + Forward (Thinn Rebel; alt weapons officer path)

**Pre-side-quest**:
- **Forward**: "Steward. I am facing forward. *This is unusual for my species.* You may have noticed."
- **Steward**: "I noticed."
- **Forward**: "Good. *(beat)* I have been thinking about my troupe. *I should bring them the Furling Hider data. It will not change their minds. They should see it anyway.*" *(side-quest carrot)*

**Mid-side-quest** (`systems_visited>=5`):
- **Forward**: "Steward. I have the Hider data ready. *Spire is on the map. We could go.*"
- **Steward**: "We could."
- **Forward**: "*(quietly)* I am... uncertain. The singular pronouns still hurt some days. *Going home as 'I' is harder than going home as 'we who watch'.*"

**Post-side-quest favorable** (`forward_sq_complete=True`):
- **Forward**: "*(if confrontation branch)* I have a we again. We who watch, We-Who-Watch-The-Far-Slope, We-Who-Watch-The-Lower-Bench. *I am no longer 'I' alone. I am 'I' among.* This is also funny. The Thinn would not understand the joke. The joke is mine."
- **Steward**: "I get the joke."
- **Forward**: "*(beat)* Yes. I thought you would."

#### Steward + Yelena (Engineer)

**Pre-side-quest**:
- **Yelena**: "Steward. Twelve-Forty-Eight's coil is up. *I re-tuned it.* You're welcome. *(beat; works on something else)*"
- **Steward**: "How's Mev-Tar?"
- **Yelena**: "Mev-Tar built Twelve-Forty-Eight. Unzervalt is decommissioning in three months. *She is leading the team building the last Scout this galaxy will ever produce.* I — I want to be there for the launch." *(side-quest carrot)*

**Mid-side-quest** (`modules_installed>=4`):
- **Yelena**: "Unzervalt has 30 days. I have *one specific module* my father designed. Korven Lwen-Tar. I completed it. *Will you detour to Unzervalt with me to install it?*" *(direct trigger)*

**Post-side-quest favorable** (`yelena_sq_complete=True, yelena_family_bond=True`):
- **Yelena**: "*(quietly proud)* My name is in the family ledger now. *And yours. Twelve-Forty-Eight is family.* My mother says you ought to come for dinner at the new Andromeda assembly floor when we get there. *I told her you would.*"

#### Steward + Mira-Rou (Medic)

**Pre-side-quest**:
- **Mira-Rou**: "Steward. The dimensional-shear fab-pattern responds. Coel Tessar's crew is stable in their berths. *I am pleased.*"
- **Steward**: "Your great-grandmother would be too."
- **Mira-Rou**: "Yes. *(holds the amphora gently)* She would. *(beat)* Steward — the amphora has begun to hum at a different frequency. I have been monitoring. *It may be nothing. It may not.*" *(side-quest carrot — Deep Child's Cradle)*

**Mid-side-quest** (`coel_tessar_complete=True AND visited_mycon_site=True`):
- **Mira-Rou**: "The amphora's FIRST_WHISPER pattern is unambiguous now. *I need to consult with a Mycon collective. Will you take me?*" *(direct trigger)*

**Post-side-quest favorable** (`mira_sq_complete=True, sevreth_child_alive=True`):
- **Mira-Rou**: "Sevreth's Child is happy today. *I can tell from the humming.* You can listen if you want."
- **Steward**: "I'd like that."
- **Mira-Rou**: *(places amphora gently between them; chemical-signal pad hums)* "She wants me to tell you... she finds your voice... *amusing? I think the word is amusing.*"

#### Steward + Tarven (Navigator)

**Pre-side-quest**:
- **Tarven**: "Steward. In the seventh decade of the Steward Iren-Vor's tenure she visited the system you flew today. Her log entry on the system is... *missing.* Curious."
- **Steward**: "Missing?"
- **Tarven**: "Erased. *Deliberately, I think.* There is a fourteen-month gap in her drift-records that *makes no sense*. *(beat)* I want to investigate, Steward." *(side-quest carrot)*

**Mid-side-quest** (`systems_visited>=8`):
- **Tarven**: "I have triangulated where Iren-Vor went during the missing fourteen months. *A fringe system. The trail is cold but readable.* Will you fly it with me?" *(direct trigger)*

**Post-side-quest favorable** (`tarven_sq_complete=True`):
- **Tarven**: "Iren-Vor's cache is in the Council Archives now. *Or, if we kept the secret, on our shared private drive.* Either way, *the prior Stewards are not gone.* I am writing a new index. *Slow work. Honorable work.*"

### Cross-crew banter (4 priority pairings)

These conversations happen ambiently in the Common Room when both crew are present. Each pairing has 5-6 canonical exchange-pairs that fire across slice progression.

#### Mraka + Yelena (the easy bond — slice's most comfortable pairing)

**Early**:
- **Mraka**: "Yelena. Your tools are *alphabetized.* I — I have never seen this before."
- **Yelena**: "They are! Why would they not be?"
- **Mraka**: "*(beat)* I have no answer to this. Drift-fly clean, sister."

**Mid-slice**:
- **Yelena**: "Twelve-Forty-Eight's hyperspace fold-vector is *off* by 0.4 degrees on every hop. Have you noticed?"
- **Mraka**: "*(immediately)* I have noticed."
- **Yelena**: "Why are we not fixing this?"
- **Mraka**: "Because *I am compensating*. It is a Drifter's-Circuit move. *We do not fix things that are working*."
- **Yelena**: "*Mraka.* The Mender does not allow this answer."
- **Mraka**: "*(grinning)* The Drifter does."

**Late** (`mraka_sq_complete=True OR yelena_sq_complete=True`):
- **Mraka**: "Yelena, I have a piece of Soren's drive-component on my shelf. *I told the Steward I would tell you what it means.* I am ready to tell you now."
- **Yelena**: "I'm listening, Mraka."

#### Bren-Vor + Mira-Rou (the shared-grief quiet pairing)

**Early**:
- **Bren-Vor**: *(seated; cleaning rifle component; says nothing)*
- **Mira-Rou**: *(taking notes; says nothing)*
- **Bren-Vor**: *(after long silence)* "Your great-grandmother shaped the first biot."
- **Mira-Rou**: "Yes."
- **Bren-Vor**: "My sister fired the rifle that started Karol-Vere's promotion track."
- **Mira-Rou**: "Yes."
- **Bren-Vor**: *(after another long silence)* "Tea?"
- **Mira-Rou**: "Yes."

**Mid-slice**:
- **Mira-Rou**: "Bren-Vor. The amphora hums differently when you enter the room."
- **Bren-Vor**: "Does it."
- **Mira-Rou**: "Sevreth's Child says — *(she translates)* — she finds your... your *steadiness* helpful. *Restful, I think the word is.*"
- **Bren-Vor**: *(quietly, the closest thing to surprised he allows)* "Thank you, Mira-Rou."

**Late** (`brenvor_sq_complete=True OR mira_sq_complete=True`):
- **Mira-Rou**: "The Halve-Tel labs are gone. The amphora is the lineage now."
- **Bren-Vor**: "Velt-Ra's journal is closed. The Telcas line continues with me, *closed*."
- **Mira-Rou**: "*(beat)* That is also a way to continue, Bren-Vor."

#### Tarven + Mraka (the Olwen-Veth bond — only if both crew aboard AND Tarven's side-quest reveals Iren-Vor's clan)

**Pre-revelation**:
- **Tarven**: "Mraka! Did you know in the seventh decade of *Steward Iren-Vor's tenure* she flew the cluster you grew up in?"
- **Mraka**: "I — *(beat)* I did not know that. I would not have looked at the seventh-decade logs. Drifters don't read Steward-logs, Tarven. We do not."
- **Tarven**: "She was — she was an *Olwen-Veth*."
- **Mraka**: *(very quiet)* "Was she."
- **Tarven**: "*(realizing what he has just said)* Mraka — I — should I — "
- **Mraka**: "Tarven. *Keep going.* Tell me what you know."

**Post-revelation** (after `iren_vor_archive_unlocked=True`):
- **Mraka**: "She was the *aunt* of the pilot I failed. *Three generations of Olwen-Veth tried to leave on the family Scout. Now I have read the seventh-decade Steward's log of her cousin's wedding.* Tarven, this is — this is much."
- **Tarven**: "I'm sorry, Mraka. *I should have told you slowly.*"
- **Mraka**: "*(soft)* You told me at the speed an Archivist tells things. *That is fine. Drift-fly slow today, Tarven.*"

#### Forward + ANY (canonical Thinn-perplexed-by-everything register)

**Forward + Yelena** (Yelena's directness vs Forward's geometric sincerity):
- **Forward**: "Yelena. Your tools are arranged in *what configuration*?"
- **Yelena**: "Alphabetical order."
- **Forward**: "*(beat)* That is not a *geometric* category. *(beat)* I am intrigued."
- **Yelena**: "You haven't seen the *symbolic order* arrangement Mev-Tar uses. *That* would intrigue you."
- **Forward**: "*(genuinely)* I would like to see this. *I will think about it for several days.*"

**Forward + Tarven** (canonical bookish meets canonical sincere):
- **Tarven**: "Forward. In the seventh decade of the Steward Iren-Vor's tenure — "
- **Forward**: "Tarven. I am facing forward. *(beat)* The prior-Steward archive is also forward of me. *I am literally facing it as I face you. This is the only configuration I can offer.*"
- **Tarven**: "*(grinning)* I will read you the relevant entry. *Twice.* For both directions."

**Forward + Mraka** (Drifter pragmatism meets Thinn cheerful-naivety):
- **Mraka**: "Forward. Your firing solutions are *unsettlingly* good."
- **Forward**: "Thank you. I am not insulted by this."
- **Mraka**: "I did not — Forward, that was *not* — "
- **Forward**: "*(cheerfully)* You also said 'unsettlingly,' which is a compliment in two-dimensional contexts. I have decided this is true."
- **Mraka**: *(after a moment; warm)* "*(quietly)* Drift-fly forward today, Forward."

---

## Banter delivery doctrine

### Per the Furling humor doctrine canon

- **The Steward's wit is canonically funny.** Combat lines should be deadpan-witty, not slapstick.
- **Crewmates can be funny in their canonical register**: Mraka warm-technical, Bren-Vor clipped-quiet, Yelena vibrant-direct, Mira-Rou thoughtful, Tarven bookish-charming, Forward sincere-not-funny.
- **Alien species are funny in different ways** — the slice's cultural-friction comedy. Lemmkin's cheerful unawareness, Thinn's geometric earnestness, Stelloth's three-voice contractual precision, Karavem's emotional-valence-reversal, Mrokon's quiet doctrinal seriousness, Kovellim's cyclical weariness.
- **The Others are NEVER funny.** Their combat banter is canonically Steward-only.
- **Never hurtful to the player.** Crewmates may tease the Steward but never *cruelly*. The slice's tone is *warm respect with humor*, not *takedown comedy*. Steward's wit is the *driver* of the humor; crew respond to it.

### Damage-bracket escalation pattern

Each species's lines should *escalate* in tone as their hull drops:
- `>75%`: confident; opening register; *playful*
- `50-75%`: aggressive; insults sharpen; *committed*
- `25-50%`: pressed; the species's character begins to crack OR doubles down per their personality
- `<25%`: desperate OR resigned (per species personality) — the slice's most *character-revealing* register

**Lemmkin and Slylandro are canonical exceptions** — they stay cheerful or confused at every damage level. Per their species canon. Other species commit to the escalation arc.

### Per-encounter variation requirement

Per the slice's variation principle ([variation-architecture.md](variation-architecture.md)), **banter never repeats identically across encounters**. Design's banter system should:
- Roll from the canonical line pool per (species, damage_bracket, line_type)
- Apply small lexical jitter per line (canonical *"alphabetized"* might appear as *"alphabetically arranged"* in another encounter)
- Avoid recently-fired lines

This is Phase 3+ work per the canonical variation roadmap. For slice MVP, fixed line-pool sampling is acceptable.

## Implementation contract for Design

1. **Banter trigger system** — fires lines at combat damage-bracket transitions + after-fight resolution + Common Room proximity events
2. **Per-species line bank** — load from this lore doc OR from a canonical content file (`src/scz/content/banter.py` suggested)
3. **Match-up-specific line preference** — if a specific match-up's line bank exists, prefer it; otherwise fallback to generic
4. **Crew side-quest carrot triggering** — Common Room dialogs gate on side-quest flags; lead-ins fire when goalpost prereqs are met but quest not yet started
5. **Time Drive interaction** — banter logs through Time Drive rewinds (the canonical "we did this fight before but you don't remember" register is *not* in this banter library — the Steward canonically does *not* remember rewound fights; only the Cleanser canonically does)

## Cross-references

- [the-quiet-resolution.md](the-quiet-resolution.md) — combat banter respects the mandate (Persuader Stewards avoid bragging in post-fight lines; Cleansers commit to grief register)
- [halia-steward-banter.md](halia-steward-banter.md) — Halia's banter style + Steward's voice profile for combat lines
- [crew-recruitment-quests.md](crew-recruitment-quests.md) — crew personality profiles for banter authoring
- [crew-common-room.md](crew-common-room.md) — Common Room ambient banter (this doc extends with Steward-crew + cross-crew dialog)
- [species-the-thinn.md](species-the-thinn.md) — Forward's voice + canonical "delivered with full sincerity" doctrine
- HANDOFF dispatches: Audio (banter voice direction); Design (banter trigger system + per-species line banks)
