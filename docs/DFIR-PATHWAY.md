# Digital forensics and incident response pathway

Audience: curriculum designers, instructors, and reviewers building the
Forensics track from the current memory and VoIP exercises into a complete
investigation progression.

The pathway starts with the existing Windows memory, VoIP, live Linux memory,
and topology exercises. It then adds the artifacts an analyst actually
correlates during an incident: Windows persistence, Linux logs, email,
browser history, a normalized timeline, disk evidence, memory-to-PCAP
correlation, reporting, and a ransomware capstone.

The source of truth is
`platform/backend/app/data/dfir-pathway.yaml`. The synthetic evidence pack is in
`platform/backend/app/data/dfir-datasets/`.

## Progression

| Module | Title | Level | Minutes | Focus |
|---|---|---|---|---|
| DFIR-01 | Windows Memory Analysis | beginner | 90 | Volatility, process triage, image hash, custody |
| DFIR-02 | VoIP and Network Call Reconstruction | beginner | 90 | SIP/RTP, codec, media reconstruction, provenance |
| DFIR-03 | Live Linux Memory Acquisition | intermediate | 100 | AVML, hashing, process environment, volatile evidence |
| DFIR-04 | Windows Artifact Investigation | intermediate | 150 | Security/Sysmon, registry, services, tasks, prefetch, Amcache, Shimcache |
| DFIR-05 | Linux Log Investigation | intermediate | 130 | sshd, sudo, cron, systemd, journal, audit |
| DFIR-06 | Email Triage and Header Analysis | intermediate | 120 | Received chain, SPF/DKIM/DMARC, attachment triage |
| DFIR-07 | Browser History and Download Forensics | intermediate | 120 | history, downloads, file hashes, execution linkage |
| DFIR-08 | Timeline Reconstruction | intermediate | 160 | normalization, clock assumptions, uncertainty |
| DFIR-09 | Disk Evidence and Plaso Timeline | advanced | 180 | image hash, MFT/USN, Plaso/Timesketch timeline, recovery, preservation |
| DFIR-10 | Memory and PCAP Correlation | advanced | 180 | process-to-flow matching, DNS/TLS, timestamp skew |
| DFIR-11 | Analyst Reporting and Peer Review | advanced | 120 | executive summary, evidence table, confidence |
| DFIR-12 | Capstone: Ransomware Investigation | advanced | 240 | full-chain reconstruction, impact, recovery, review |

Each module declares weighted competencies that sum to 1.0. The progression is
ordered: every prerequisite is an earlier module.

## Evidence requirement

**A flag alone is not completion evidence.** Every module requires a short
analyst finding and an analyst report or a reviewed evidence artifact. The
accepted evidence types are:

- analyst report;
- evidence artifact;
- timeline;
- command transcript;
- hashed acquisition record.

The report must use
`platform/backend/app/data/dfir-datasets/report-template.md` and include:

1. case and question;
2. evidence and custody table with source, time, SHA-256, and custodian;
3. method and missing sources;
4. findings separated from interpretation, with confidence and alternatives;
5. a normalized timeline;
6. impact and scope;
7. containment, eradication, recovery, and notification recommendations;
8. lessons learned;
9. reviewer sign-off.

The automated lab checks can still validate a flag or a query result, but the
module is not complete until the report or artifact is reviewed. DFIR-11 and
DFIR-12 are explicitly manual-review modules.

## Evidence pack

| Asset | Used by |
|---|---|
| `windows-memory.md` | DFIR-01 case brief |
| `network-call.md` | DFIR-02 case brief |
| `linux-memory.md` | DFIR-03 case brief |
| `windows-artifacts.jsonl` | DFIR-04 |
| `linux-logs.jsonl` | DFIR-05 |
| `email-triage.json` | DFIR-06 |
| `browser-history.jsonl` | DFIR-07 |
| `timeline-events.jsonl` | DFIR-08, DFIR-11, DFIR-12 |
| `disk-events.jsonl` | DFIR-09 |
| `plaso-timeline.jsonl` | DFIR-09 |
| `memory-pcap-correlation.jsonl` | DFIR-10, DFIR-12 |
| `ransomware-case.yaml` | DFIR-12 |
| `report-template.md` | DFIR-11, DFIR-12 |

The pack is synthetic. It uses documentation ranges (`10.20.0.0/24`),
`example.org`/`lab.example` hosts, and fictional people. It contains no real
personal data, credentials, institutional evidence, keystrokes, mouse movement,
or exhaustive terminal history.

## Existing and planned labs

Existing labs:

- `forensics-1-1-windows-memory-volatility`
- `forensics-2-1-voip-call-reconstruction`
- `forensics-2-2-topology-forensics-guided`
- `forensics-2-3-topology-forensics-independent`
- `forensics-3-1-live-linux-memory`

Planned labs:

- `forensics-4-1-windows-artifacts`
- `forensics-4-2-linux-log-investigation`
- `forensics-4-3-email-triage`
- `forensics-5-1-browser-history`
- `forensics-5-2-timeline-reconstruction`
- `forensics-6-1-disk-evidence`
- `forensics-6-2-memory-pcap-correlation`
- `forensics-7-1-analyst-report`
- `forensics-7-2-ransomware-capstone`

A module is not marked reviewed until the planned lab exists, the report or
artifact is reviewable, and the lab has a clean three-run harness result.

## Relationship to the offensive tracks

The offensive tracks teach how an intrusion is performed; this pathway teaches
how the evidence is preserved, correlated, and defended. The capstone reuses
the same phishing, execution, persistence, credential-access, and impact
behaviour in synthetic form, so learners do not need to attack a live system to
practise the investigation.

## Validation

`platform/backend/tests/test_dfir_pathway.py` checks:

- 12 ordered modules with resolvable prerequisites and weights summing to 1.0;
- every competency exists in the shared taxonomy;
- every module requires a short analyst finding, an analyst report, and an
  evidence artifact or timeline;
- the assessment policy rejects flag-only completion;
- every dataset exists and is listed in the evidence-pack README;
- JSONL/JSON/YAML files parse and contain no obvious real-provider PII;
- the report template contains the required sections;
- every existing lab exists and every planned slug is new.

Run:

```bash
pytest platform/backend/tests/test_dfir_pathway.py -q
```

## Extending the pathway

1. Add or update a synthetic evidence asset and list it in the README.
2. Add the module to `dfir-pathway.yaml` with outcomes, evidence, competencies,
   prerequisites, and a planned lab slug.
3. Keep the report requirement explicit; do not let a flag become the only
   completion evidence.
4. Add the workbook chapter and lab metadata when the planned lab is built.
5. Run the pathway test and the three-run lab harness before marking the module
   reviewed.
