# Career Stories

Status: **design briefs** (12 November 2026). These are the exercise shape behind
the DevFest Cyber Discovery experience. They are not CTF challenges: the learner
becomes the person, makes a decision, and leaves with an artifact.

## The shape

Each Career Story has five parts:

1. **Role and situation** — who you are and what just landed on your desk.
2. **Three beats** — a short sequence that mirrors the job.
3. **A decision** — one trade-off with no perfect answer.
4. **An artifact** — the thing a real practitioner would produce.
5. **A reflection** — what the learner would do differently next time.

The artifact is the assessment evidence. A flag can confirm a step, but it is not
the outcome.

## 1. Day in the Life of a SOC Analyst

**Role:** Tier 1 analyst on a healthcare SOC.

**Situation:** A ransomware alert fires at 08:10. The endpoint is still online.

**Beats:**

1. Triage the alert and decide whether it is a true positive.
2. Pivot through authentication, process, and network evidence.
3. Brief the incident lead with a timeline and a containment recommendation.

**Decision:** Isolate the endpoint now, or preserve it for investigation while
the user keeps working? Explain the trade-off.

**Artifact:** A one-page incident brief with:

- what happened, in plain language;
- the evidence and its limits;
- the containment decision and the reason;
- the next owner and the next update time.

**Competencies:** IR-001, SIEM-002, SOC-001.

## 2. Day in the Life of an OT Security Analyst

**Role:** OT security analyst supporting a water treatment facility.

**Situation:** Operations reports a chemical dosing irregularity. The PLC is
still running.

**Beats:**

1. Review Modbus traffic and identify the changed register.
2. Compare the change with the approved maintenance window.
3. Coordinate a safe response with the operations lead.

**Decision:** Stop the process, or keep it running while you gather evidence?
Explain the safety and production consequences.

**Artifact:** An operations-safe change note with:

- the observed change and the evidence;
- the safety impact;
- the agreed response and rollback;
- the communication log.

**Competencies:** OT-001, OT-006, OT-011.

## 3. Day in the Life of a Threat Hunter

**Role:** Threat hunter on a small detection team.

**Situation:** A peer mentions unusual outbound traffic. There is no alert yet.

**Beats:**

1. Form a hypothesis from the available telemetry.
2. Hunt for the behaviour and map it to MITRE ATT&CK.
3. Build one detection and explain its false-positive risk.

**Decision:** Publish the detection now, or wait for more evidence? Explain the
risk of each choice.

**Artifact:** A hunt memo and a detection rule with:

- the hypothesis;
- the query or rule;
- the evidence and the ATT&CK mapping;
- the false-positive plan and the owner.

**Competencies:** TH-001, TH-004, TH-007.

## 4. Day in the Life of a Digital Forensics Examiner

**Role:** DFIR examiner supporting an internal investigation.

**Situation:** A laptop is seized. The legal team needs a defensible timeline.

**Beats:**

1. Image the drive and verify the hash.
2. Reconstruct a timeline from file system, browser, and log evidence.
3. Present the evidence with its limits.

**Decision:** Report a strong lead that is not yet corroborated, or wait for a
second source? Explain the evidentiary risk.

**Artifact:** A forensic timeline and evidence summary with:

- the acquisition and hash;
- the timeline and the source of each event;
- the corroboration and the gaps;
- the limits of the conclusion.

**Competencies:** FOR-005, FOR-007, FOR-011.

## Assessment rubric

Use four levels, and keep the language about the evidence, not the person.

| Level | What the artifact shows |
|---|---|
| **Awareness** | Names the role and the main evidence, with help. |
| **Guided** | Follows the beats and produces a partial artifact. |
| **Applied** | Produces a complete artifact and explains the decision. |
| **Professional** | Produces a complete artifact, names the limits, and communicates it to a non-specialist. |

The event certificate records participation. The artifact can be added to the
learner's professional portfolio as a work sample.

## Build notes

- Reuse the existing lab runtime and workbook structure. Do not build a new
  exercise engine.
- Keep the scenario synthetic. Use fictional organisations, hosts, and people.
- The SOC and DFIR stories are the first build: they reuse the existing incident
  and forensics labs and need the least new content.
- The OT story needs a Modbus trace and a safe-response script.
- The threat-hunter story needs a small telemetry set and a detection rule.
- Add each story to the DevFest event as a lab or a workbook chapter, then map it
  to the competencies above.
