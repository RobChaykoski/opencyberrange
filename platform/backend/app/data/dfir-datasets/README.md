# Synthetic DFIR evidence pack

These files are **synthetic**. They contain no real people, credentials, hosts,
or institutional evidence. Names, addresses, and hashes are fictional and use
documentation ranges (`10.20.0.0/24`, `example.org`, `lab.example`).

| File | Purpose | Pathway module |
|---|---|---|
| `windows-memory.md` | Case brief for the existing Volatility lab | DFIR-01 |
| `network-call.md` | Case brief for the existing VoIP lab | DFIR-02 |
| `linux-memory.md` | Case brief for the existing live-memory lab | DFIR-03 |
| `windows-artifacts.jsonl` | Security, Sysmon, registry, service, task, prefetch, Amcache, and Shimcache records | DFIR-04 |
| `linux-logs.jsonl` | sshd, sudo, cron, and systemd records | DFIR-05 |
| `email-triage.json` | One synthetic phishing message and attachment metadata | DFIR-06 |
| `browser-history.jsonl` | History, downloads, and file-hash records | DFIR-07 |
| `timeline-events.jsonl` | Mixed-source events for normalisation | DFIR-08, DFIR-11, DFIR-12 |
| `disk-events.jsonl` | Partition, MFT, USN, and deleted-file records | DFIR-09 |
| `plaso-timeline.jsonl` | Plaso/Timesketch-style timeline output | DFIR-09 |
| `memory-pcap-correlation.jsonl` | Process, connection, DNS, and TLS records | DFIR-10, DFIR-12 |
| `ransomware-case.yaml` | Capstone case, affected hosts, and indicators | DFIR-12 |
| `report-template.md` | Required analyst report structure | DFIR-11, DFIR-12 |

## Policy

- No keystrokes, mouse movement, or exhaustive terminal history.
- No real personal data or real credentials.
- Do not replace this pack with live learner telemetry.
- A flag alone is not completion evidence. Every module requires an analyst
  report or a reviewed evidence artifact.
