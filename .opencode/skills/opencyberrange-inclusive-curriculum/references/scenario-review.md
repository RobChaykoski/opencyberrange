# Scenario Review: Inclusive, Near-Future, Teachable

Use this reference with the `OpenCyberRange Inclusive Curriculum` skill.

## Scenario card

Copy this into the lab design note or PR description.

```text
Lab / course:
Learner role:
Setting:
People affected:
Asset or decision at risk:
Near-future AI element:
Uncanny detail (1-2, explainable):
Evidence path (source -> second channel -> context -> clues):
Access route (device / no-device / low-bandwidth):
Sensitive content and support route:
Defensive takeaway:
Inclusive check passed by:
```

The card is deliberately short. If a field is hard to fill, the scenario is
probably relying on atmosphere instead of a teachable decision.

## Review checklist

### Scenario and role

- [ ] The learner has a named job or community role, not "the user".
- [ ] The opening says what decision is due, not just what tool to run.
- [ ] The scenario would still make sense if the technical tool changed.
- [ ] The lab does not assume the learner is a penetration tester.
- [ ] The organisation is fictional, or permission is explicit.

### Representation

- [ ] The cast is not all young, male, able-bodied, and technically confident.
- [ ] Names, pronouns, ages, and family structures vary naturally.
- [ ] A disabled person can be the expert, the decision-maker, or the learner.
- [ ] The villain is an organisation, incentive, or behaviour, not an identity.
- [ ] The victim is not described as naive, greedy, or foolish.
- [ ] The scenario does not use poverty, immigration status, or mental illness
      as the explanation for crime.
- [ ] Cultural references are explained or unnecessary.
- [ ] Indigenous data sovereignty is treated as governance, not decoration.

### Near-future AI

- [ ] The AI element is plausible within roughly the next one to three years.
- [ ] The AI sits inside a normal workflow (scheduling, support, hiring,
      translation, moderation, recommendation, reporting).
- [ ] The uncanny detail is small, specific, and explainable.
- [ ] The learner verifies provenance and corroboration, not just artefacts.
- [ ] The lab does not imply the AI is sentient, magical, or always malicious.
- [ ] The lab distinguishes a tool failure from a human decision to misuse it.
- [ ] The AI does not replace the actual security lesson.

### Access and language

- [ ] Acronyms are defined on first use.
- [ ] Reading level fits the stated audience.
- [ ] Instructions avoid "just", "simply", "obviously", and "everyone knows".
- [ ] A no-device or low-bandwidth path exists.
- [ ] A keyboard-only and screen-reader path is possible.
- [ ] Media has captions, transcripts, or alt text.
- [ ] The learner can opt out of sensitive content without explaining why.

### Safety and assessment

- [ ] The lab uses only fictional data, credentials, and systems.
- [ ] No real person, classmate, colleague, or local case is identifiable.
- [ ] Sensitive topics use clinical language and provide a support route.
- [ ] The flag and automated tests match the workbook.
- [ ] There is more than one reasonable route to a good decision.
- [ ] The assessment rewards reasoning, not speed alone.
- [ ] The defensive takeaway is usable outside the lab.

## Worked rewrites

### 1. From "hoodie hacker" to a community clinic

**Stock:** "A hacker in a hoodie scans a hospital network and finds an open
port."

**Rewrite:** "You coordinate privacy at a community health clinic. The new AI
receptionist has started booking patients into a retired doctor's calendar. The
confirmations are fluent, polite, and wrong. Before you change anything, work
out whether this is a scheduling bug, a stale directory, or someone using the
assistant to hide a different change."

**Why it works:** the learner is a privacy coordinator, the harm is plausible,
the AI is embedded in ordinary work, and the decision is about evidence and
containment instead of scanning a stranger's network.

### 2. From "foreign cybercriminal" to an ordinary vendor failure

**Stock:** "A foreign attacker sends a phishing email to steal the company
payroll."

**Rewrite:** "You run operations for a small food co-op. Payroll receives a
polished notice from the co-op's payroll vendor asking everyone to re-verify
their bank details before the long weekend. The vendor's real portal is down,
the notice links to a look-alike page, and one employee has already started
entering details. Decide what to stop, what to preserve, and who to call."

**Why it works:** the threat is an impersonated vendor and a real operational
pressure, not a nationality. The learner has to act under time pressure without
a stereotype doing the explanatory work.

### 3. From "spot the deepfake" to a school-newsletter decision

**Stock:** "Find the AI-generated image by looking at the hands."

**Rewrite:** "You edit the school board's family newsletter. A submitted photo
shows a new playground that has not been built, with a ribbon-cutting date next
week. The image is sharp, the caption is plausible, and two parents have already
shared it. Trace the source, check the board's facilities record, and decide
what to publish while the evidence is incomplete."

**Why it works:** the learner practises provenance and corroboration in a
familiar setting. The uncanny detail is a place that does not exist yet, not a
monster in the pixels.

## Future-texture bank

Use one or two per lab, not all of them.

| Texture | Near-future use | Uncanny detail |
|---|---|---|
| AI receptionist | Booking, reminders, triage | Confirms an appointment with a person who left |
| Synthetic voice note | Family emergency, vendor call | Right names, wrong phrasing, odd background |
| AI newsletter | School, municipal, community update | Flawless layout, one closed venue or wrong date |
| Recommendation feed | Library, training, shopping | Confident suggestion that does not exist |
| AI tutor | Homework help, onboarding | Correct tone, subtly wrong citation |
| AI hiring screen | Application, reference, portfolio | Polished materials, generic references |
| Translation assistant | Settlement services, clinics | Fluent translation, one cultural mismatch |
| Moderation bot | Community forum, game chat | Removes the wrong post, misses the real threat |
| Smart device | Home, clinic, workshop | Normal telemetry, unexpected remote command |
| AI-generated record | Archive, registry, case file | Consistent format, impossible timeline |

### Calibration

| Too subtle | Useful | Too far |
|---|---|---|
| No way to verify | One source check settles it | A single clue proves everything |
| The AI is perfect | The AI is fluent and slightly wrong | The AI is omniscient |
| A normal day | A normal day with one wrong detail | A dystopian world |
| The learner guesses | The learner traces and corroborates | The learner fights the robot |

## Inclusive language quick edits

| Instead of | Try |
|---|---|
| "guys" | "everyone", "team", "learners" |
| "normal user" | "typical user", "most people", "a busy employee" |
| "he" when the person is unknown | "they" |
| "third-world country" | "under-resourced region", "a region with limited infrastructure" |
| "crazy", "insane", "psycho" | "unexpected", "unusual", "disruptive" |
| "just run" | "run" |
| "simply click" | "select" |
| "obviously" | remove it |
| "victim was careless" | "the fake was convincing; here is the procedure that helps" |
| "foreign hacker" | "the criminal group", "the vendor impersonator", "the operator" |
| "black-hat genius" | "the attacker", "the operator", "the criminal business" |

## Sensitive-content note

For sextortion, self-harm, family violence, immigration status, disability, and
mental health:

- use pattern-level language, not graphic detail;
- never use a real local case or a real student;
- provide an opt-out and a support route;
- keep the learner's dignity in the copy;
- make the defensive procedure the point, not the trauma.

## Review output template

```text
Inclusive curriculum review

Lab / course:
Verdict: pass / revise / blocked

Strengths:
- ...

Risks:
- stock trope:
- representation gap:
- access gap:
- future-texture problem:

Three smallest edits:
1.
2.
3.

Evidence path check:
- source:
- second channel:
- context:
- clues:
- decision:

Workbook/test alignment:
- flag:
- test steps:
- workbook:
```
