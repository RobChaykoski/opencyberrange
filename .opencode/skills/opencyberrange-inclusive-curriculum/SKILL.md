---
name: OpenCyberRange Inclusive Curriculum
description: Use when writing or reviewing OpenCyberRange courses, labs, scenarios, personas, workbooks, or achievements. Checks inclusive representation, avoids stock hacker tropes, and layers in a restrained near-future AI texture that creates useful uncanny-valley evidence without turning the lab into science fiction.
---

# OpenCyberRange Inclusive Curriculum

Use this skill for **course and exercise content**. For visual design, layout,
tokens, and Vue conventions, use the `opencyberrange-design` skill and its
`references/course-content.md`.

## What this skill is for

OpenCyberRange should feel like a place where many kinds of people learn to
defend the systems they actually use. That means the default scenario is not a
hoodie in a basement, the default villain is not a foreign cybercriminal, and
the default learner is not a young man who already knows the command line.

Use this skill to:

- review a lab, course, workbook chapter, persona, or achievement set;
- write a new scenario that is inclusive by construction;
- add a **near-future AI texture** that is ordinary, plausible, and slightly
  wrong, rather than science fiction;
- keep the learning goal first when representation and atmosphere compete.

## Core principles

1. **Start with a job, not a hacker archetype.** The learner is a librarian,
   clinic coordinator, apprentice, municipal clerk, dispatcher, archivist,
   settlement worker, accessibility advisor, student, or parent who has to make
   a decision. Technical skill is one part of the role, not a personality.
2. **Diversity is structural, not a costume.** Show different ages, genders,
   abilities, cultures, family structures, device access, and levels of
   confidence because real institutions contain them. Do not add a character
   solely to tick a box, and do not make one identity the whole plot.
3. **The near future is ordinary.** AI appears inside existing workflows:
   reception, scheduling, tutoring, hiring, moderation, translation, reporting,
   recommendation, and customer support. It is not a sentient character.
4. **Use the uncanny valley as evidence design.** The AI should be familiar,
   fluent, and just slightly off. The learner notices the wrongness through
   provenance, corroboration, and context, not through a monster reveal.
5. **Inclusive access is part of the puzzle.** Plain language, captions,
   transcripts, keyboard paths, screen-reader-friendly handouts, low-bandwidth
   options, and a no-device route are design requirements, not extras.
6. **Never blame the victim.** A person who trusts a polished fake is not
   foolish. The scenario should show why the fake was plausible and what
   procedure would have helped.
7. **Do not create new harm.** No real personal data, no real credentials, no
   real malware, no live systems outside the lab, no graphic abuse, no slurs,
   and no stereotype presented as the explanation for a crime.

## The scenario palette

Prefer settings where cybersecurity is already part of someone's day:

| Setting | Learner role | Natural security problem |
|---|---|---|
| Public library | Digital-literacy librarian | A fake AI reading list, account takeover, public Wi-Fi |
| Community health centre | Privacy lead / clinic coordinator | AI scheduling, referral leaks, voice-clone payment requests |
| Trades apprenticeship | Apprentice / shop steward | Credential phishing, invoice fraud, device handoff |
| Municipal office | Records clerk / communications officer | Synthetic council notices, public-record integrity |
| Settlement agency | Caseworker | Identity documents, multilingual scams, account recovery |
| Campus accessibility office | Accessibility advisor | Assistive-tech permissions, captions, data minimisation |
| Indigenous language program | Language keeper / program coordinator | Data sovereignty, consent, cultural material handling |
| Small co-op or charity | Operations lead | Shared passwords, donation fraud, vendor impersonation |
| Rural ISP or repair shop | Technician | Device handoff, recovery channels, customer privacy |
| Museum or archive | Archivist | Provenance, synthetic donations, rights and consent |

Avoid making every scenario a corporate penetration test. A lab can be
technical without being about "breaking into a company."

## The near-future AI texture

Use a **three-dial** approach. Turn each dial deliberately.

| Dial | Low | Useful middle | Too far |
|---|---|---|---|
| **Familiarity** | "A computer did something." | AI inside a normal workflow | A world rebuilt around AI |
| **Agency** | The AI is just a tool | A vendor, team, or incentive uses the AI | The AI has its own desires |
| **Wrongness** | Nothing is off | One or two subtle, explainable inconsistencies | Horror, magic, or a twist ending |

### What "uncanny" means here

The uncanny detail should be small enough that a hurried person would miss it
and specific enough that evidence settles it.

Good examples:

- an AI receptionist books a patient with a doctor who retired last year;
- a synthetic school newsletter is perfectly formatted but names a closed venue;
- a cloned voice uses the right family names but a phrase the parent would never use;
- a chatbot cites a bylaw section that was repealed;
- an AI-generated book cover and blurb exist, but the book does not;
- a fake job reference speaks in the same polished cadence as the fabricated CV.

Avoid:

- sentient AI, AGI, robot emotions, or "the AI decided";
- neon cyberpunk, ubiquitous implants, or post-apocalyptic cities;
- a single "gotcha" artefact that proves everything in one glance;
- using "AI" as a synonym for "bad";
- making the learner feel stupid for not spotting the fake immediately.

### The teaching move

The learner should leave with a procedure:

1. **Source** — who published or sent this, and can that be verified?
2. **Second channel** — can an independent source confirm it?
3. **Context** — does this fit the person, place, and time?
4. **Clues** — what artefacts are present, and what else could explain them?
5. **Decision** — what is safe to do while the evidence is incomplete?

The AI is the reason the old "looks real" instinct fails. The lesson is the
procedure, not the anomaly.

## Inclusive representation checks

### People and roles

- Is the learner a person with a job, a stake, and a decision — not a generic
  "user" or a hacker stereotype?
- Are names, pronouns, ages, and family structures varied without commentary?
- Are disabled people present as experts and colleagues, not only as victims or
  as the "problem"?
- Are different levels of technical confidence treated with respect?
- Is the villain an organization, incentive, or behaviour — not an ethnicity,
  religion, class, or mental-health condition?
- Is the victim's mistake explained by context and pressure, not by naivety?

### Language and access

- Is the reading level appropriate for the stated audience?
- Are acronyms defined on first use?
- Are cultural references explained or removed?
- Is there a no-device or low-bandwidth path?
- Do handouts work with a screen reader and keyboard only?
- Are captions/transcripts/alt text part of the plan when media is used?
- Are instructions free of "just", "simply", "obviously", and "everyone knows"?
- Is the learner addressed directly and calmly, without hype or shame?

### Threat and sensitivity

- Is the harm described at the pattern level rather than with graphic detail?
- Are sextortion, self-harm, family violence, immigration status, and disability
  handled with clinical language and support routes?
- Is there an opt-out that requires no explanation?
- Are real cases anonymised and used only when their details are necessary?
- Is the lab clearly isolated, fictional, and safe to explore?
- Does the defensive takeaway explain what a real person could do next?

### Canadian and community context

- Are Canadian resources and legal references current and correctly attributed?
- Is Indigenous data sovereignty treated as a governance question, not decoration?
- Are rural, remote, low-income, newcomer, and multilingual realities considered?
- Are local names and institutions fictional unless permission is explicit?

## Review workflow

1. **Read the lab as a learner.** Name the job, the decision, and the evidence.
2. **Fill the scenario card** in `references/scenario-review.md`.
3. **Run the checklist.** Mark each item pass, revise, or not applicable.
4. **Rewrite the three weakest lines**, not the whole lab. Usually that is the
   scenario opening, the victim description, and the "what just happened" line.
5. **Add one near-future detail** that changes what the learner must verify.
6. **Check the workbook and assessment** still match the flag and test steps.
7. **Record the change** in the workbook's introduction or a short author note.

## Definition of done

A lab or course passes when:

- a learner can explain who they are and why the decision matters;
- the scenario does not rely on a stock hacker, a stock victim, or a stock
  foreign villain;
- the AI element is plausible within the next few years and has a clear
  evidence path;
- at least one access route does not require a personal device;
- the sensitive content has a support route and an opt-out;
- the defensive takeaway is actionable outside the lab;
- a colleague from a different background could read it without having to
  translate the cultural assumptions.

## References

- `references/scenario-review.md` — checklist, scenario card, worked rewrites,
  future-texture bank, and language edits.
- `../opencyberrange-design/references/course-content.md` — lab contract,
  workbook structure, AI-safety rules, and certificate rules.
