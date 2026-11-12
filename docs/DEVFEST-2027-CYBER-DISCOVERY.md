# DevFest 2027 Cyber Discovery Experience

Status: **planning** (12 November 2026). The machine-readable plan is
`platform/backend/app/data/devfest-2027.yaml`; validate it with
`python scripts/check-devfest-plan.py`.

## Positioning

**GDG Windsor DevFest 2027 — Cyber Discovery Experience**
*Powered by OpenCyberRange & SWOCTS*

**Discover Your Cyber DNA. Find Your Cyber Path.**

A six-hour, beginner-friendly experience for high-school students, college
students, developers, IT professionals, and career changers. It is not a CTF.
It is a career-discovery day built on the Career DNA and Cyber GPS layers already
in the platform.

## What makes it different

Most events teach people to solve challenges. This event helps them answer:

1. **Do I like cybersecurity?** — four short investigations across networking,
   forensics, OSINT, and AI security.
2. **What kind of cybersecurity?** — four career pathways in the afternoon.
3. **What am I naturally good at?** — a Cyber DNA snapshot from the evidence.
4. **What should I do next?** — a Cyber GPS report with next workbooks and
   certification suggestions.
5. **How has my identity changed?** — a permanent profile that grows at future
   events.

## Agenda

| Time | Activity |
|---|---|
| 09:00–09:30 | Opening keynote: what cybersecurity really is |
| 09:30–12:00 | Session 1: What does it take to become a cyber person? |
| 12:00–13:00 | Lunch and community networking |
| 13:00–15:30 | Session 2: Where can I go next? |
| 15:30–16:00 | Cyber DNA reveal and certificate ceremony |

## Morning: four investigations

Each block is short, story-led, and mapped to competencies that already exist in
the taxonomy.

| Exercise | Story | Competencies | Career signal |
|---|---|---|---|
| Packet Detective | A capture is the only evidence. | NET-021, NET-029, NET-030 | SOC, threat hunting |
| Digital Crime Scene | A suspicious workstation needs a timeline. | FOR-005, FOR-007, FOR-011 | DFIR, incident response |
| Find the Person | Synthetic public clues identify a person and place. | OSINT-001, OSINT-005, OSINT-009 | Threat intelligence, investigations |
| AI Security Escape Room | A fictional chatbot leaks hidden instructions. | AI-003, AI-005, AI-007 | AI security, AppSec |

The morning output is a **Cyber DNA snapshot** and a permanent profile. The
snapshot is descriptive: it shows where practice is concentrated, not a grade.

## Afternoon: four pathways

| Pathway | Scenario | Competencies |
|---|---|---|
| SOC Analyst | Healthcare ransomware attack. | IR-001, SIEM-002, SOC-001 |
| Threat Hunter | An unknown attacker is hiding. | TH-001, TH-004, TH-007 |
| OT Security Analyst | A water treatment anomaly. | OT-001, OT-006, OT-011 |
| AI Security Analyst | An AI application exposes company data. | AI-005, AI-007, AI-010 |

The afternoon output is a **Cyber GPS report**: a primary path, a readiness
percentage, recommended OpenCyberRange workbooks, and certification suggestions.
Readiness is a curriculum-coverage estimate, not a hiring prediction.

## Career Stories

The event introduces a new exercise shape: **Career Stories**. Instead of "find
the flag", the learner becomes the person:

- **Day in the Life of a SOC Analyst** — triage, investigate, brief leadership.
- **Day in the Life of an OT Security Analyst** — analyse PLC changes, review
  Modbus, coordinate with operations.
- **Day in the Life of a Threat Hunter** — form a hypothesis, hunt, build a
  detection.
- **Day in the Life of a Digital Forensics Examiner** — image a drive,
  reconstruct a timeline, present evidence.

Each story produces an artifact the learner can keep: an incident brief, a
change note, a detection rule, or a forensic timeline. The artifact is the
career evidence, not the flag.

## Ten concepts to adapt

The plan captures ten community-proven concepts. They are ranked by the
"I can't believe I figured that out" reaction, not technical difficulty:

1. The Accidental AI Insider
2. The Deleted Startup
3. Ransomware Monday
4. The Missing Person OSINT Hunt
5. Escape the Help Desk
6. Water Plant Under Attack
7. The Fake Employee
8. The Mystery PCAP
9. Shadow IT
10. The Cybersecurity Murder Mystery

The murder mystery is the strongest differentiator: no exploitation, only
evidence analysis, risk management, communication, and executive reporting.

## Using the existing event engine

The experience is a normal **Competition** event with one extra marker:
`experience_key = "devfest-2027"`. That marker turns on the Cyber Discovery
panel on the event detail page and the `discovery` certificate award. The event
engine continues to own:

- participants and opt-in;
- the event lab list;
- the leaderboard;
- sponsors and the event logo;
- the certificate and public verification.

Seed the event on a host with:

```bash
docker compose exec -T backend python -m app.scripts.seed_devfest_event --preview
```

`--preview` ends the event one minute ago so the certificate can be tested on
development. Omit it for the real 2027 window, or pass `--start` and `--end`.
The seed is idempotent: rerunning it refreshes the dates, labs, and sponsors.

The discovery panel reads:

- the event's labs, matched to the four morning investigations;
- the learner's existing completions and competency evidence;
- the Cyber DNA snapshot and the four afternoon pathway readiness scores;
- the exclusive `DVF-CYBER-2027` certificate serial.

The instructor overview uses the same event participants and the configured
minimum cohort size. It never names a learner.

## Build order

1. **Career Stories shell** — a learner-facing page that lists the four stories,
   their beats, and the artifact. Start with the SOC and DFIR stories.
2. **Event profile** — an event-scoped DNA/GPS view and an exclusive certificate
   template with the `DVF-CYBER-2027` prefix.
3. **Four morning exercises** — adapt existing labs first; build the synthetic AI
   escape room last.
4. **Four afternoon pathways** — reuse the role-readiness engine and the
   certification question banks.
5. **Instructor view** — aggregate pathway interest, competency gaps, and
   certificate counts with small-cohort suppression.
6. **Rehearsal** — run the full six hours on development with a mixed cohort,
   then capture the manual screenshots.

## Safety and privacy

- Use synthetic people, companies, and infrastructure. Do not search for real
  personal data.
- The OSINT block teaches method on fictional targets, not surveillance.
- GPS answers are optional and never stored.
- Instructor reports use the same minimum-cohort suppression as the rest of the
  platform.
- The certificate is event-exclusive and verified by the platform; it is not a
  certification or a hiring credential.

## Validation

```bash
python scripts/check-devfest-plan.py
python scripts/check-question-banks.py
python -m pytest tests/test_career_readiness.py tests/test_certification_quiz.py -q
```
