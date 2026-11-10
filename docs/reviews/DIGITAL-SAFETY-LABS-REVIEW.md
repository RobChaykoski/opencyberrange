# Digital-safety and email labs: design, student-tester, and curriculum review

Date: **2026-11-10**
Scope: four new High School labs, their workbook pages, and the shared target
changes that support them.

## Sample

| Lab | Track / level | Difficulty | Estimated time | Target mode |
|---|---|---|---|---|
| `high-school-9-6-read-the-link` | High School / Grade 9 | beginner | 20 min | Lookalike link and encoded path |
| `high-school-9-7-know-the-file` | High School / Grade 9 | beginner | 20 min | Disguised ZIP archive |
| `high-school-9-8-forwarded-message` | High School / Grade 9 | beginner | 25 min | Link + file capstone |
| `high-school-10-3-email-metadata` | High School / Grade 10 | beginner | 25 min | Raw email headers |

Environment: static lab validation, in-process target smoke tests, workbook
review, and documentation checks. No live RangeBox desktop session or live
platform completion was recorded.

## Summary

| Lab | Discoverability | Prerequisites | Instructions | Commands | Hints | Flag path | Consistency | Timing | Language/access | Learning outcome | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Read the link | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | Pass |
| Know the file | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | Pass |
| Forwarded message | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | Pass |
| Dissect an email | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | Pass |

Timing is scored 1 for every lab because the estimates are provisional until a
live learner walkthrough is recorded.

## Design decisions

- **A coherent unit, not four unrelated topics.** Grade 9 moves from decoding
  data (CyberChef) to making a decision about a link, then a file, then a
  capstone that combines both. Grade 10 moves from HTTP headers and page source
  to message headers.
- **Scaffolding fades.** The link and file labs teach one habit each. The
  capstone does not introduce a new tool; it asks the learner to choose and
  combine the two habits and explain the decision.
- **The industry tools stay visible.** Students use CyberChef, `curl`, `file`,
  `unzip`, and a text editor. The email lab reads the raw message rather than a
  simplified "header viewer", so the skill transfers to a real mail client.
- **No new runtime dependency.** Every lab uses the existing shared target
  image, Python standard library, and OS utilities. There is no new package,
  container image, or licence obligation.
- **One target, one concept, one flag.** Each lab has a single reachable flag
  and a deterministic test path. Decoys are announced in the hints and
  explained in the workbook.

## Inclusive curriculum review

- Scenarios use community library, community centre, and volunteer roles. No
  learner is cast as a hoodie-wearing attacker, and no identity is used as the
  explanation for a crime.
- The person who received the suspicious message is not blamed. The workbook
  explains why a polished fake is plausible and what procedure would have
  helped.
- Language is plain and defines every term: userinfo, host, percent-encoding,
  magic bytes, SPF, DKIM, DMARC, and envelope sender.
- Every lab has a keyboard path, a text-only path, and a browser fallback where
  one is technically possible. There are no colour-only states and no
  emoji-only icons.
- No real personal data, credentials, malware, or live external services are
  used. All domains are reserved `.example` names and all addresses are
  documentation ranges.

## Safety review

- The link labs never require clicking a link. The lookalike host is a reserved
  `.example` domain and cannot resolve to a real service.
- The file lab serves a ZIP archive under a misleading `.png` name. It contains
  text only; there is no executable payload.
- The email lab serves a fictional `.eml` file with documentation IP ranges and
  reserved domains. The body contains a decoy token so a grep-only shortcut does
  not produce the answer.
- The shared target is read-only, drops all capabilities, sets
  `no-new-privileges`, and caps CPU and memory. This review also added
  `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`,
  `X-Frame-Options: DENY`, a restrictive `Content-Security-Policy`, and a
  permissions policy to every response.
- The email lab explains that SPF/DKIM/DMARC failures are evidence, not proof.
  It does not teach that a passing check makes a message safe.

## Evidence

- `validate-lab.py` for each lab: **22/22 checks passed**.
- In-process target smoke tests covered every shared mode, including the four
  new modes: page served, expected artifact served, the flag was not in the
  landing page, and the taught path recovered the flag.
- Link lab: the raw message contains no plain-text `OCR{`, contains the
  lookalike host and the `@` userinfo trick, and URL-decoding recovers the
  token and the hidden path.
- File lab: the disguised file starts with `PK`, extracts to `token.txt`, and
  the budget decoy is present but is not the real flag.
- Capstone: the notice contains no plain-text token, URL-decoding reveals
  `/files/grant-pack.png`, the download is a ZIP, and extraction recovers the
  token.
- Email lab: three `Received` hops, `spf=fail`, `dkim=none`, `dmarc=fail`,
  `X-OCR-Case-Token` metadata, and a body decoy that differs from the real flag.
- Workbook/lab agreement: hostnames, ports, paths, flags, operation order, and
  workbook links agree across `lab.yaml`, the workbook pages, and
  `Workbook/COVERAGE.md`.
- Hints scaffold concept, observation, and answer; none contains the real flag.
- `Workbook/COVERAGE.md` regenerated: High School now reports **13** labs with
  workbooks and the total is **147**.

## Findings

### Blocker / Major

None.

### Minor

1. **Live UI and RangeBox not verified.** The targets and solve paths were
   smoke-tested, but the in-platform lab cards, workbook rendering, RangeBox
   desktop, and real learner completion were not exercised in a browser
   session. Record a live walkthrough before calling the timings final.
2. **CyberChef remains an external dependency for two browser-only paths.**
   The Grade 9 link and capstone labs use CyberChef's URL Decode operation. If a
   deployment blocks the public CyberChef site, the learner needs an approved
   local copy or the Python fallback in the workbook.
3. **Synthetic email headers are simplified.** Real messages vary in header
   order and can include many more `Received` hops. The workbook tells students
   to read header names, not line positions, and the lab explains that
   authentication failures are evidence rather than proof.

### Suggestions

- Record one live learner walkthrough for each lab and replace the provisional
  timing.
- Consider a short instructor answer key with the expected verdict sentences
  for the capstone and email labs.
- When the self-hosted CyberChef deployment lands, update the workbook
  fallbacks to the local address and remove the external-site caveat.

## Cross-lab themes

- Read the evidence before acting: host, path, file type, sender, route.
- A label is not proof. A display name, filename, padlock, or polished message
  can all be misleading.
- Combine independent clues; one clue can be a mistake.
- Stopping and verifying through a second channel is a successful outcome.
- The learner writes a decision in plain language, not just a flag.

## Not verified

- Live browser rendering of the Grade 9 and Grade 10 lab cards and workbook
  navigation.
- RangeBox access to the public CyberChef site on a restricted network.
- Actual learner completion time and the capstone verdict quality with a real
  class.
- The platform's in-app exercise-tester execution of every new test step on a
  deployed host.
