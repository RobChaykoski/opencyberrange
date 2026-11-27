# First-time user test

**Status:** ready to run; no participants recorded yet.  
**Owner:** Learning experience / platform research.  
**Target:** first accepted flag in **under 15 minutes** for every persona.  
**Kit:** [`first-time-user-test/`](first-time-user-test/README.md)

This protocol measures the real onboarding path, not a demo. A participant
starts with no account and no VPN profile, registers, joins a course, connects
the VPN where the chosen lab needs it, launches a lab, and submits the first
flag. The facilitator records where the participant hesitates, asks for help, or
backs out.

The 15-minute target is deliberately demanding. It forces the team to treat
registration, approval, VPN setup, lab start, and the first flag as one product,
not five independent features.

## 1. Questions

1. Can a first-time user reach an accepted flag in under 15 minutes?
2. Which step consumes the most time for each persona?
3. Where do users get stuck, and what do they believe is wrong?
4. Does the flow work for a non-technical learner, a high-school learner, and a
   security professional without facilitator rescue?
5. Which fixes would move the most people under the target?

## 2. Personas

| Persona | Profile | Expected friction | Lab |
|---|---|---|---|
| Software developer | Comfortable with terminals, Git, and APIs; new to cyber range tooling | VPN client, course invite, lab network model | `linux-1-1-ssh-service-detection` |
| General IT technician | Windows/desktop support, some networking; little Linux | WireGuard install, terminal use, flag format | `linux-1-1-ssh-service-detection` |
| College student | Digital native, limited networking; motivated by the course | Registration rules, VPN, first terminal command | `linux-1-1-ssh-service-detection` |
| High school student | Grades 9-12; minor-safe stream; guardian consent | Account rules, browser lab, reading the brief | A High School lab, no live target |
| Security professional | Pentester or analyst; knows the tools, not this platform | Finding the course, VPN profile, lab start | `linux-1-1-ssh-service-detection` |

A persona is a test lens, not a stereotype. Recruit people who match the
description and let them use their own device and browser. Do not coach a
persona into the "expected" behavior.

## 3. Target and success rule

| Measure | Target |
|---|---|
| Median total time, all personas | **< 15:00** |
| Participants under 15:00 with no more than a neutral prompt | **>= 80%** |
| Median time to register | < 4:00 |
| Median time to VPN connected | < 5:00 after approval |
| Median time to lab ready | < 3:00 after VPN |
| Median time to first accepted flag | < 4:00 after lab ready |
| Participants who abandon the flow | 0 in the pilot |

**Assistance levels.** Record every intervention.

| Level | Meaning | Counts toward target? |
|---|---|---|
| L0 | No help; facilitator only observes | yes |
| L1 | Neutral prompt: "What are you trying to do?" or "What do you see?" | yes |
| L2 | Directional hint: names a control, menu, or step | no |
| L3 | Facilitator does the step or takes the keyboard | no |

A participant who needs L2 or L3 still counts in the overall time and in the
stuck-point analysis, but not in the unassisted pass rate. Report both.

## 4. Sample

- Pilot: **1 participant per persona** (5 total) to debug the protocol.
- Baseline: **3 participants per persona** (15 total), or as many as the
  recruitment window allows.
- Report the sample size per persona. Do not pool personas to hide a weak one.
- Recruit outside the project team. A colleague who built the flow is not a
  first-time user.

## 5. Session flow

| Minute | Activity |
|---:|---|
| -10 | Confirm environment, test device, VPN server, test course, and reset state |
| -5 | Read the participant brief; sign consent (and guardian consent for a minor) |
| 0 | Start timer. Read the task card. Participant begins |
| 0-15 | Observe and record. Use one neutral prompt at 3:00, another at 7:00 |
| 15 | Stop if no accepted flag. Record outcome and debrief |
| +5 | Debrief: what was clear, what was confusing, one fix |
| +5 | Cleanup: delete account, VPN peer, browser profile, local downloads |

Time starts when the participant says they are ready and the facilitator says
"begin". It stops when the platform shows the flag accepted.

## 6. Task card

Read this exactly:

> You are joining a short cybersecurity course. Starting from this browser with
> no account, create an account, join the course with the invite code on the
> card, connect the VPN if the exercise asks for it, start the first lab, and
> submit the flag. The course card has the invite code and the lab name. Please
> think aloud as you go. I will not help unless you are stuck for a while. There
> is no penalty for asking; I am testing the platform, not you.

Then hand over the course card:

```text
Course: First-Time User Test
Invite code: <test invite code>
Lab: <lab title>
Lab slug: <lab slug>
```

## 7. What to record

Use the [timing sheet](first-time-user-test/timing-sheet.csv). Record:

- one row per participant;
- ISO-8601 UTC timestamps for start, registration, approval/login, VPN, lab
  ready, and flag accepted;
- participant id only, never a name, email, or student number;
- persona, device, OS, browser, network;
- stuck phases from the fixed list;
- assistance level and a short quote;
- outcome (`completed`, `completed_assisted`, `abandoned`, `technical_failure`).

The [observation log](first-time-user-test/observation-log.md) captures the
narrative: what the participant clicked, what they said, and where they paused.
The timing sheet is the quantitative record.

## 8. Stuck-point taxonomy

Use these labels so the analysis is comparable across sessions:

```text
landing
registration_form
username_email_rules
password_rules
approval_wait
login
course_join
vpn_download
vpn_install
vpn_import
vpn_connect
lab_catalogue
lab_launch
rangebox
brief_reading
tools_terminal
finding_flag
submitting_flag
accessibility
language
device_browser
network_firewall
other
```

A participant can have more than one stuck point. Record the phase where the
pause started and the phase where they recovered (or abandoned).

## 9. Environment setup

Run the test on a staging or development deployment, never production.

1. Create a course named `First-Time User Test` with the selected lab assigned
   and active. Use a fresh invite code.
2. Keep the approval gate on so approval wait is measured. The facilitator
   approves the account when it appears.
3. Confirm the VPN server, peer manager, and firewall rules work on the test
   network.
4. Prepare a fresh browser profile per participant. Do not reuse a logged-in
   profile.
5. Prepare the course card and the lab card. Do not include a hint in the card.
6. For a high-school participant, use a minor-safe High School lab and have the
   guardian consent form ready. No live OSINT extension, no personal data.
7. Have a reset step ready: delete the account, revoke the VPN peer, remove the
   browser profile, and delete downloads.

Full checklist: [environment setup](first-time-user-test/environment-setup.md).

## 10. Ethics and privacy

- This is an operational usability test. If results will be generalized as
  research, use the [REB-ready survey package](REB-SURVEY-PACKAGE.md) and obtain
  approval before recruiting.
- Collect the minimum: participant id, persona, timings, device/browser,
  observed friction, and a short quote. No name, email, IP, student number, or
  screen recording by default.
- A minor needs guardian consent and a facilitator present. Do not record the
  minor's face or voice. Use the minor-safe lab.
- A participant can stop at any time and ask for their data to be removed.
- Keep raw notes on the encrypted test drive for 90 days, then delete. Keep only
  aggregate results in the report.
- Do not put a real learner row or a real credential in the report.

Full text: [consent and privacy](first-time-user-test/consent-and-privacy.md).

## 11. Analysis

Run the aggregator on the timing sheet:

```bash
python scripts/first_time_user_test.py docs/research/first-time-user-test/timing-sheet.csv
```

It prints per-persona counts, medians, p90, the share under 15 minutes, the
assistance mix, and the most frequent stuck phases. Use
[the analysis template](first-time-user-test/analysis-template.md) for the
write-up.

Report:

1. A per-persona table with n, median, p90, under-15 rate, and assist mix.
2. The three slowest phases overall and per persona.
3. The top five stuck points with a quote and a proposed fix.
4. A decision: ship, fix, or re-test.
5. Owners and target release for each fix.

## 12. Decision rules

- **Ship the onboarding** if the median is under 15:00 for every persona and
  the unassisted pass rate is at least 80%.
- **Fix and re-test** if one persona is over 15:00 or one phase is over half the
  total time.
- **Stop and redesign** if participants cannot explain what a lab is, cannot
  find the invite code field, or cannot connect the VPN after two attempts.
- A technical failure is not a participant failure. Record it, fix the
  environment, and re-run that participant.

## 13. Run record

| Date | Persona | Participant | Total | Assist | Outcome | Report |
|---|---|---|---|---:|---|---|
| | | | | | | |
| | | | | | | |
| | | | | | | |

Link the completed timing sheet and analysis here when the pilot runs.
