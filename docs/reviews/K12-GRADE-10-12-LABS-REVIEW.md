# Grade 10–12 Digital Frontier labs: design and student-tester review

Date: **2026-11-10**
Scope: three new High School labs adapted from
`RobChaykoski/K12_Digital_Self_Defense_Framework` Program 3, plus their target
modes, quizzes, badges, and workbook pages.

## Source mapping

| Lab | K–12 source | Adaptation |
|---|---|---|
| MFA and the Lost Phone | MFA Mayhem (Session 2) | A fictional staff portal with MFA and a public recovery answer |
| Media Provenance: Is It Real? | Deepfake Detectives (Session 4) | Source, provenance, metadata, hash, and corroboration; no real people or deepfake imagery |
| Crypto Rug Pull: Follow the Liquidity | Crypto Rush & Rug Pulls (Session 8) | A simulated token page and ledger; no real wallets, tokens, or money |

The K–12 CTF flags are worksheet answers (`flag{...}`). Each lab uses the
platform `OCR{...}` format and a deterministic target path.

## Sample

| Lab | Grade | Difficulty | Estimated time | Target mode |
|---|---|---|---|---|
| `high-school-10-4-mfa-lost-phone` | 10 | beginner | 25 min | MFA recovery portal |
| `high-school-11-2-media-provenance` | 11 | intermediate | 35 min | Provenance archive |
| `high-school-12-2-crypto-rug-pull` | 12 | intermediate | 35 min | Token ledger |

## Summary

| Lab | Discoverability | Prerequisites | Instructions | Commands | Hints | Flag path | Consistency | Timing | Language/access | Learning outcome | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MFA recovery | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | Pass |
| Media provenance | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | Pass |
| Crypto rug pull | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | Pass |

Timing is scored 1 until a live learner walkthrough is recorded.

## Design decisions

- **One grade, one applied skill.** Grade 10 covers identity recovery, Grade 11
  covers evidence and provenance, and Grade 12 covers financial fraud and
  ledger tracing. The prerequisites chain them into a pathway.
- **Safe adaptations.** The K–12 lessons use real public deepfake examples and
  real crypto cases. The platform version uses fictional SVG media, synthetic
  metadata, and a simulated ledger. No real person, wallet, token, or money is
  involved.
- **Sensitive content stays instructor-led.** The K–12 sextortion and legal
  sessions were deliberately not turned into self-paced labs. They need the
  counsellor, opt-out, and reporting protocol from the source framework.
- **Evidence before emotion.** The provenance and crypto labs ask the learner to
  state what the evidence supports and what it does not prove.
- **One target, one flag.** Each lab has a deterministic path and a single
  reachable token.

## Progression and assessment wiring

- **Quizzes:** each lab has a six-question knowledge check mapped to CompTIA
  Security+ or CySA+.
- **Badges:** Recovery Architect, Provenance Analyst, and Liquidity Tracker are
  awarded on completion; Digital Frontier is awarded when all three are
  complete.
- **Skill DNA:** the categories map to Builder (identity), Investigator
  (provenance and fraud), and the existing six-branch radar.
- **Certificates:** the labs count toward the Grade 10, 11, and 12 level
  certificates. Learners who completed those levels before this release must
  complete the new exercises before the certificate is issued again.
- **Certification pathway:** the High School pathway now names ITF+, ISC2 CC,
  Security+, SC-900, CySA+, PenTest+, and CISSP, with roles from apprentice to
  digital literacy coordinator and identity support analyst.

## Inclusive curriculum review

- The scenarios use a community centre, a newsroom, and a volunteer
  coordinator. No learner is cast as a hacker archetype.
- The person who lost a phone or trusted a scam is not blamed. The workbook
  explains the recovery and prevention steps.
- Plain language defines MFA, SIM swap, provenance, corroboration, rug pull,
  liquidity, and recovery-agent scam.
- Every lab has a browser path and a terminal path. The crypto and provenance
  labs expose copyable JSON and text.
- No colour-only states and no emoji-only icons.

## Safety review

- The MFA target uses a fictional account and a mock recovery flow. No real
  authenticator code or password is used.
- The provenance target uses generated SVG illustrations and synthetic metadata.
  No real person's image is stored or uploaded.
- The crypto target is a simulation. It never asks for a seed phrase and never
  connects a wallet.
- The targets are read-only, non-root, drop all capabilities, and set
  `no-new-privileges` with resource limits.
- The `form-action 'self'` and `img-src 'self' data:` CSP additions are scoped to
  the shared High School target.

## Evidence

- `validate-lab.py`: 22/22 for each lab.
- In-process target smoke test: 39 checks across the three modes, including
  no-flag-on-landing-page, form handling, SVG media, synthetic verification
  denial, ledger tracing, and the flag.
- Quiz banks: six questions each, with explanations and references; the quiz
  checker validates structure.
- Workbook/lab agreement: hostnames, ports, paths, flags, tokens, and answer
  order agree.
- Hints scaffold concept, observation, and fix; none contains the real flag.
- `Workbook/COVERAGE.md` and the NICE mapping now include the new labs.

## Findings

### Blocker / Major

None.

### Minor

1. **Live UI and RangeBox not verified.** The target and test paths were
   smoke-tested, but the in-platform lab cards, level unlock, workbook
   rendering, and real learner completion were not exercised in a browser.
2. **K–12 sensitive sessions are intentionally absent.** Sextortion, legal
   reporting, and non-consensual image content remain instructor-led. That is a
   deliberate safeguarding decision, not a content gap.
3. **Timing is provisional.** The estimates need a live learner walkthrough.

### Suggestions

- Add a passkeys/WebAuthn follow-on to the MFA lab.
- Add a “fix the provenance policy” lab for a newsroom workflow.
- Add a consumer-protection reporting worksheet to the crypto lab for local
  jurisdictions.
- Record a live walkthrough and replace the provisional timings.

## Not verified

- Live browser rendering of the new Grade 10–12 lab cards and workbook pages.
- RangeBox access to the new target hostnames on a restricted network.
- Actual learner completion time and the quality of the written evidence briefs.
- The platform’s in-app exercise tester executing every test step on a deployed
  host.
