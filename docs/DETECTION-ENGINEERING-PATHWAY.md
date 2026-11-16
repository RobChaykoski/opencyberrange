# Defensive detection-engineering pathway

Audience: curriculum designers, instructors, and reviewers who need a
defensible route from offensive fundamentals into detection, triage, and
hunting.

This pathway complements the existing Linux and Windows offensive tracks. It
does not replace them. Learners who can enumerate, exploit, and pivot need a
second skill: proving that the activity would have been seen, deciding whether
the alert is real, and writing the rule that catches it next time.

## Design principles

1. **Detection is a hypothesis.** Each module starts with a behaviour, names
   the data source that should record it, and states the expected evidence.
2. **One evidence chain.** Windows Event Logs, Sysmon, Zeek, Suricata, and
   OpenSearch/Elastic with KQL-style queries are taught together. A learner
   should be able to move from an endpoint event to a network flow to a SIEM
   alert without changing vocabulary.
3. **Every rule is reviewable.** A Sigma rule ships with a title, logsource,
   selection, condition, false-positive note, and severity. A KQL query ships
   with its index, field assumptions, and expected result.
4. **Synthetic data only.** The teaching datasets use documentation ranges
   (`10.20.0.0/24`), `lab.example` hostnames, and fictional accounts. No live
   learner telemetry is embedded in a lab.
5. **Minimum necessary telemetry.** The pathway explicitly prohibits
   keystrokes, mouse movement, and exhaustive terminal history. Detection
   exercises collect the events needed for a decision, not a surveillance feed.

## Prerequisites

- Completed beginner pathway or equivalent terminal and networking experience.
- Baseline competencies: `NET-029`, `NET-030`, `NET-031`, `LIN-018`, `WIN-005`.
- Recommended prior pathways: `BEG04`, `NET00`, `LIN01`.
- Comfort with a terminal, a browser, JSON, and reading a packet or log line.

## Progression

| Module | Title | Difficulty | Minutes | Focus |
|---|---|---|---|---|
| DET-01 | Windows Event Log Triage | beginner | 90 | 4624/4625/4688/4720/4672, account and source pivots |
| DET-02 | Sysmon Process and Network Telemetry | beginner | 120 | process trees, network events, LSASS access |
| DET-03 | Sigma Rule Authoring and Review | intermediate | 150 | logsource, selection, condition, false positives |
| DET-04 | Zeek Network Evidence | intermediate | 150 | conn/DNS/HTTP baselines and tunnelling |
| DET-05 | Suricata Alert Triage | intermediate | 120 | signature context, disposition, escalation |
| DET-06 | OpenSearch, Elastic, and KQL-Style Hunting | intermediate | 180 | indexes, fields, Sigma-to-KQL translation |
| DET-07 | Capstone: Multi-Stage Intrusion Hunt | advanced | 240 | one timeline across endpoint, network, and SIEM |

Each module lists weighted competencies from the shared taxonomy. The weights
sum to 1.0 so a module grade is reproducible even when a reviewer changes the
rubric. The source of truth is
`platform/backend/app/data/detection-pathway.yaml`.

### DET-01 — Windows Event Log Triage

Outcomes: explain the difference between 4624, 4625, 4688, 4720, and 4672;
pivot from a failed-logon cluster to the account and source host; write a
triage note with a decision and confidence.

Evidence: query result, triage note, artefact. Assessment is deterministic:
automated query checks plus a short triage rubric.

### DET-02 — Sysmon Process and Network Telemetry

Outcomes: reconstruct an Office-to-PowerShell process tree from Sysmon Event ID
1; correlate a Sysmon network event with a DNS or TLS flow; identify LSASS
access and explain why it is credential access.

Evidence: query result, triage note, artefact.

### DET-03 — Sigma Rule Authoring and Review

Outcomes: translate a behaviour into a Sigma logsource, selection, and
condition; test a rule against a positive and a benign synthetic event;
document false positives and a response recommendation.

Evidence: detection rule, query result, triage note. Assessment checks the
rule schema, a positive synthetic match, and a documented false-positive test.

### DET-04 — Zeek Network Evidence

Outcomes: build a baseline from Zeek `conn` and DNS logs; identify a long-label
TXT query consistent with DNS tunnelling; correlate the DNS answer, HTTP POST,
and host process evidence.

Existing labs: `network-1-2-log-correlation`,
`network-1-3-dns-anomaly-detection`.

### DET-05 — Suricata Alert Triage

Outcomes: separate a true positive from a noisy signature using context; map a
Suricata alert to the underlying flow and host evidence; record disposition,
severity, and escalation decision.

Existing labs: `linux-5-4-suricata-live-detection`,
`network-1-4-failed-login-analysis`.

### DET-06 — OpenSearch, Elastic, and KQL-Style Hunting

Outcomes: write KQL-style queries for process, authentication, DNS, and alert
data; translate a Sigma rule into an OpenSearch/Elastic query; explain index,
field, and timestamp assumptions.

Existing labs: `malware-1-4-c2-pcap-wireshark`,
`malware-1-5-inetsim-c2-detection`.

### DET-07 — Capstone: Multi-Stage Intrusion Hunt

Outcomes: build a hypothesis and select the minimum telemetry needed to test
it; correlate Windows, Sysmon, Zeek, Suricata, and SIEM evidence into one
timeline; write a detection rule and an incident note with containment and
recovery recommendations.

Existing labs: `network-1-3-dns-anomaly-detection`,
`network-1-4-failed-login-analysis`, `malware-1-4-c2-pcap-wireshark`,
`malware-1-5-inetsim-c2-detection`.

Planned labs: `detection-3-2-multi-stage-hunt`.

## Synthetic datasets

Assets live in `platform/backend/app/data/detection-datasets/`.

| Asset | Purpose |
|---|---|
| `windows-security.jsonl` | Windows Security events 4624, 4625, 4688, 4720, 4672, 4634 |
| `sysmon.jsonl` | Sysmon Event IDs 1, 3, 10, 11 |
| `zeek-conn.jsonl` | Connection baselining and beaconing |
| `zeek-dns.jsonl` | DNS tunnelling and long-label queries |
| `zeek-http.jsonl` | HTTP POST and beacon triage |
| `suricata-eve.jsonl` | Signature alerts and DNS events |
| `opensearch-events.jsonl` | ECS-style documents spanning Windows, Zeek, and Suricata |
| `sigma/` | `encoded_powershell.yml`, `lsass_access.yml`, `dns_tunnel.yml` |
| `kql-queries.yaml` | KQL-style queries for the SIEM modules |

The pack contains no real people, credentials, hosts, or production traffic.
A production deployment must not replace it with live learner telemetry. If an
institution wants a live exercise, use a separate governed dataset with an
approved purpose, retention, and access policy.

## Evidence and assessment

Every module asks for at least a query result and a triage note; most also ask
for an artefact or a detection rule. The pathway is deterministic where it can
be: a query either returns the synthetic event or it does not. Written work is
graded against a short rubric covering the hypothesis, the evidence, the
decision, confidence, and the next action.

A learner who completes DET-01 through DET-07 can:

- read an endpoint or network log and say what happened;
- select the cheapest telemetry that answers a question;
- write and review a Sigma rule and a SIEM query;
- separate a true positive from a noisy signature;
- produce a timeline and an incident note that another analyst can act on.

## Relationship to the offensive tracks

The offensive Windows and Linux tracks teach enumeration, exploitation, and
pivoting. This pathway reuses those behaviours as detection subjects: the same
Office-to-PowerShell chain, DNS tunnel, and credential-access pattern appears
in the synthetic logs. Learners do not need to re-run an exploit to practise
detection, and instructors do not need to expose a live target to teach it.

## Validation

`platform/backend/tests/test_detection_pathway.py` checks that:

- the seven modules are ordered, weighted, and have resolvable prerequisites;
- every competency exists in the shared taxonomy;
- every dataset and Sigma rule exists and is listed in the dataset README;
- every JSONL file parses, uses the documentation range, and contains no
  credential material;
- the data policy prohibits keystrokes, mouse movement, and exhaustive
  terminal history;
- Sigma rules carry a description, detection condition, false positives, and a
  valid severity;
- KQL queries are unique and reference a real dataset index;
- every referenced existing lab exists and every planned slug is new.

Run it with:

```bash
pytest platform/backend/tests/test_detection_pathway.py -q
```

## Extending the pathway

1. Add or update a synthetic asset and list it in the dataset README.
2. Add the module to `detection-pathway.yaml` with outcomes, evidence,
   competencies, and a planned lab slug.
3. Add a Sigma rule and a KQL query if the module teaches rule authoring or
   SIEM hunting.
4. Run the pathway test and the lab harness. Do not mark a module reviewed
   until it has a clean three-run harness result.
5. Update this document and the competency contracts together.
