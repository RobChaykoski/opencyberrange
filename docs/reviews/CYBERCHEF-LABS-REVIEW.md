# CyberChef labs: student-tester and curriculum review

Date: **2026-11-10**
Scope: three new High School / Grade 9 CyberChef labs and their workbook pages.

## Sample

| Lab | Difficulty | Estimated time | Target mode |
|---|---|---|---|
| `high-school-9-3-cyberchef-base64-basics` | beginner | 15 min | Base64 message |
| `high-school-9-4-cyberchef-caesar-shift` | beginner | 15 min | ROT13 message |
| `high-school-9-5-cyberchef-layered-message` | beginner | 20 min | Base64 + ROT13 |

Environment: static lab validation, local target smoke test, workbook review, and
platform UI review. No live RangeBox desktop session was recorded.

## Summary

| Lab | Discoverability | Prerequisites | Instructions | Commands | Hints | Flag path | Consistency | Timing | Language/access | Learning outcome | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Base64 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | Pass |
| Caesar shift | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | Pass |
| Two layers | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | Pass |

Timing is scored 1 because the estimates are provisional until a live learner
walkthrough is recorded.

## Evidence

- `validate-lab.py` for each lab: **22/22 checks passed**.
- Target smoke test for each mode: page served, message served, encoded message
  did not contain the flag, and the taught decoding order recovered the flag.
- Workbook and lab metadata agree on hostnames, ports, flags, and operation order.
- Hints scaffold the operation and the place to look; none contains the flag.
- The raw message never contains the flag, so copying the message alone is not a
  shortcut.
- All three labs offer a browser-only path and use plain language.
- CyberChef is presented as an external, client-side tool with an explicit
  warning to use only fictional lab data.

## Findings

### Blocker / Major

None.

### Minor

1. **Live UI and RangeBox not verified.** The target app and decode paths were
   smoke-tested locally, but the in-platform CyberChef menu item and RangeBox
   desktop were not exercised in a real browser session. Add a live learner
   walkthrough before calling the timing final.
2. **External tool dependency.** CyberChef is a public GCHQ site. If a deployment
   blocks it, the learner needs an approved local copy or an instructor-supplied
   alternative. The workbook already points to the direct URL and the platform
   menu item.

### Suggestions

- Record a short live walkthrough for each lab to confirm the estimated times.
- If the programme is not high-school-based, assign these labs through a course
  rather than relying on the High School track label.

## Cross-lab themes

- Encoding is consistently described as representation, not protection.
- Each lab has one concept, one target, and one flag.
- The operation order is stated before the learner needs it.
- Scenarios use a community library help desk rather than a hacker archetype.
- The shared target remains isolated, read-only, and dependency-free.

## Not verified

- Real browser rendering of the CyberChef menu item in the sidebar and active-lab
  panel.
- RangeBox desktop access to the external CyberChef site on a restricted network.
- Actual learner completion time.
