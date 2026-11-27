# First-time user test kit

Use this kit with the [protocol](../FIRST-TIME-USER-TEST.md). Run the pilot on a
staging deployment, with a disposable course and accounts.

## Contents

| File | Use |
|---|---|
| [personas.md](personas.md) | Recruitment profiles and what each persona tests |
| [moderator-script.md](moderator-script.md) | Exact welcome, task card, prompts, debrief |
| [participant-brief.md](participant-brief.md) | One-page brief for the participant |
| [consent-and-privacy.md](consent-and-privacy.md) | Consent text, minors, data handling |
| [environment-setup.md](environment-setup.md) | Staging, course, VPN, reset checklist |
| [timing-sheet.csv](timing-sheet.csv) | One row per participant; quantitative record |
| [observation-log.md](observation-log.md) | Narrative notes and stuck points |
| [analysis-template.md](analysis-template.md) | Report structure and decision rules |

## Run order

1. Complete the environment checklist and reset state.
2. Read the participant brief and sign consent (guardian consent for a minor).
3. Start the timer and read the task card from the moderator script.
4. Record timestamps in the timing sheet and notes in the observation log.
5. Stop at the accepted flag or at 15:00.
6. Debrief, then clean up the account and VPN peer.
7. Run `python scripts/first_time_user_test.py <timing-sheet.csv>`.
8. Complete the analysis template and attach both files to the release evidence.

## Rules

- One participant per session.
- No proactive help; use one neutral prompt at 3:00 and 7:00.
- Record assistance level L0-L3.
- Record the phase where the participant got stuck, not just "slow".
- Never put a name, email, student number, or token in the sheet.
- A technical failure is not a participant failure; fix the environment and
  re-run that participant.

## Target

Median total time under 15:00 for every persona, and at least 80% of
participants under 15:00 with no more than a neutral prompt.
