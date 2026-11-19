# Learner archetypes

Status: **proposal** (18 November 2026). A reflective lens over the existing
capabilities and learning signals. It is not a personality test and not a
fixed label.

Presentation follows [progressive disclosure](INFORMATION-DESIGN-PROGRESSIVE-DISCLOSURE.md): summary first, detail on request, and the learner controls what stays visible.

Four clusters describe how a learner tends to approach security work:

```text
Explorer  → Researcher → Investigator
Builder   → Engineer   → Architect
Defender  → Hunter     → Responder
Leader    → Collaborator → Communicator
```

A learner is not one type. The profile shows a **current pattern of evidence**
across all four clusters, and the learner decides which parts are useful.

## 1. The clusters

### Explorer → Researcher → Investigator

| Mode | What it looks like | Evidence |
|---|---|---|
| **Explorer** | Follows curiosity beyond the minimum | Optional labs, references, side investigations |
| **Researcher** | Turns curiosity into a structured question | Source list, hypothesis, search plan |
| **Investigator** | Answers the question with evidence | Timeline, evidence log, finding, decision |

This cluster is the discovery and evidence axis.

### Builder → Engineer → Architect

| Mode | What it looks like | Evidence |
|---|---|---|
| **Builder** | Makes something work | Script, lab target, tool, prototype |
| **Engineer** | Makes it reliable and safe | Tests, error handling, least privilege, documentation |
| **Architect** | Designs under constraints | Threat model, trust boundary, trade-off record |

This cluster is the construction and design axis.

### Defender → Hunter → Responder

| Mode | What it looks like | Evidence |
|---|---|---|
| **Defender** | Applies controls and keeps them working | Hardening, policy, monitoring, patch record |
| **Hunter** | Looks for what the controls missed | Hypothesis, query, ATT&CK map, finding |
| **Responder** | Acts under pressure and preserves evidence | Triage, containment, recovery, report |

This cluster is the security-operations axis.

### Leader → Collaborator → Communicator

| Mode | What it looks like | Evidence |
|---|---|---|
| **Leader** | Sets direction and owns a decision | Decision log, incident command, plan |
| **Collaborator** | Works across roles and handoffs | Team scenario, requests, peer review |
| **Communicator** | Explains to the right audience | Report, brief, executive summary |

This cluster is the human and organisational axis.

## 2. What the archetypes are not

- Not a personality type. Do not say "you are an Explorer" as a fixed identity.
- Not a hiring filter. An employer cannot reject a learner because their
  pattern is "Defender" rather than "Hunter".
- Not a replacement for competency scores. They summarise how the learner works,
  not what they know.
- Not a reason to narrow a learner's options. A learner can grow any cluster.
- Not a team-role assignment. Team roles are chosen for the scenario and rotated.

## 3. Scoring

Each cluster has a score from 0–100, with confidence and evidence count.

```text
Discovery & evidence   82  High
Construction & design  64  Medium
Security operations    88  High
People & organisation  71  Medium
```

Rubric:

- Use the existing capability, practice-index, and artifact evidence.
- Weight reviewed artifacts more than completions.
- Do not score a cluster with no opportunity.
- Show the three modes inside each cluster when expanded.
- Use a fixed window and formula version.
- Recompute as evidence accumulates; the pattern can change.

Example detail:

```text
Security operations 88
  Defender   91  Strong control and monitoring evidence
  Hunter     84  Two reviewed hunts with ATT&CK mapping
  Responder  86  IR capstone timeline and containment record
```

## 4. Visual design

Use a four-cluster **compass**, not a radar with twelve spokes:

```text
                 Discovery
                   82
                    |
Construction 64 ----+---- 88 Security operations
                    |
              People 71
```

- Show four cluster scores and labels.
- Expand a cluster to its three modes.
- Do not show twelve slices at once.
- Use text labels and confidence, not colour alone.
- The learner can hide a cluster they do not want to display.
- The default shows the two strongest and one growth cluster.

This is progressive disclosure: the compass is the signal; the modes are the
detail.

## 5. Use in the platform

### Learner profile

- A small compass card with four scores and one sentence: "Your strongest
  current pattern is security operations, with growing construction and design
  evidence."
- Expand for the modes and the evidence.
- The learner chooses whether to show the compass on the shareable portfolio.

### Career reflection

Map the clusters to role families, not to a single job:

| Pattern | Possible directions |
|---|---|
| Discovery strong | OSINT, threat intelligence, research, detection |
| Construction strong | AppSec, DevSecOps, cloud, platform engineering |
| Security operations strong | SOC, detection, IR, threat hunting |
| People strong | GRC, consulting, security architecture, leadership |

A role usually needs more than one cluster. A SOC analyst needs security
operations plus communication; an architect needs construction plus people.

### Team scenarios

Use the compass to build a balanced team, then rotate roles:

- do not assign a learner to a role only because of their pattern;
- explain the role requirements;
- let the learner choose or rotate;
- score the role behaviour, not the archetype.

### Portfolio narrative

The learner can use the compass to tell a story:

> "My evidence is strongest in investigation and response. I am building
> architecture skills through threat modelling and design reviews."

That is more useful than a single label.

### Career direction check

The Profile page has an optional **Career direction check**: eight short
scenario questions that score the same four clusters. It is a reflection aid,
not a personality test, and the answers are used for that response only. The
result shows the current pattern, the strongest cluster, and directions to
explore. The learner can start over at any time.

## 6. Guardrails

- Do not use the archetypes for admissions, grading, or hiring.
- Do not infer personality, motivation, or mental health.
- Do not stereotype by gender, culture, language, disability, or background.
- Do not force a learner into a cluster.
- Do not hide the evidence behind the label.
- Do not compare learners publicly.
- Allow the learner to correct or hide the compass.
- A low cluster is a growth opportunity, not a deficiency.
- Review the model for bias and calibration each term.

## 7. Data model

| Table | Purpose |
|---|---|
| `archetype_definitions` | Cluster, mode, description, version |
| `archetype_snapshots` | Learner, cluster, score, confidence, evidence count, window, formula version |
| `archetype_evidence` | Snapshot, artifact or signal, weight |
| `archetype_preferences` | Learner, visible clusters, share setting |

Reuse existing capability and learning-signal evidence. Do not create a second
evidence store.

## 8. API shape

```json
{
  "learner": "s42",
  "formula_version": "archetype-2027.1",
  "clusters": [
    {"id": "discovery", "label": "Discovery and evidence", "score": 82, "confidence": "high"},
    {"id": "construction", "label": "Construction and design", "score": 64, "confidence": "medium"},
    {"id": "operations", "label": "Security operations", "score": 88, "confidence": "high"},
    {"id": "people", "label": "People and organisation", "score": 71, "confidence": "medium"}
  ],
  "strongest": "operations",
  "growth": "construction"
}
```

## 9. Implementation phases

1. **Phase 1 — definitions.** Publish the four clusters and twelve modes with
   evidence rules.
2. **Phase 2 — offline scoring.** Compute the compass for past learners and
   review with faculty.
3. **Phase 3 — learner card.** Add the compass, detail expansion, and hide/share
   controls.
4. **Phase 4 — career and team use.** Add role-family guidance and balanced-team
   suggestions.
5. **Phase 5 — calibration.** Compare with learner reflection and faculty
   observation; adjust.

## 10. Acceptance criteria

- The compass has four clusters and three modes each.
- Every score has confidence and evidence count.
- No cluster is scored without an opportunity.
- The learner can hide or share the compass.
- It is not used for admissions, grading, or hiring.
- The default view shows four clusters, not twelve modes.
- The model is versioned and reviewed for bias.
- The learner can correct the evidence.

## 11. Anti-patterns

- "You are a Defender" as a fixed identity.
- A twelve-spoke radar that nobody can read.
- Using the compass to shortlist candidates.
- Assigning team roles by archetype only.
- A low cluster presented as a weakness.
- Hiding the evidence.
- Never letting the learner change the display.
