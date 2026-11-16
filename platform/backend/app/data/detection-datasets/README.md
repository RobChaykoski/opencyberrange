# Synthetic detection datasets

These datasets are **synthetic**. They contain no real people, credentials,
hosts, or production traffic. Names, addresses, and hashes are deliberately
fictional and use documentation ranges (`10.20.0.0/24`, `lab.example`).

| File | Schema | Used by |
|---|---|---|
| `windows-security.jsonl` | Windows Security events (4624, 4625, 4688, 4720, 4672) | Windows log triage, failed-logon hunting, account creation |
| `sysmon.jsonl` | Sysmon Event IDs 1, 3, 10, 11 | Process, network, file, LSASS access |
| `zeek-conn.jsonl` | Zeek `conn.log` fields | Connection baselining, beaconing |
| `zeek-dns.jsonl` | Zeek `dns.log` fields | DNS tunnelling, long-label queries |
| `zeek-http.jsonl` | Zeek `http.log` fields | HTTP POST/beacon triage |
| `suricata-eve.jsonl` | Suricata `eve.json` alerts and DNS events | Alert triage, signature context |
| `opensearch-events.jsonl` | ECS-style documents covering Windows, Zeek, and Suricata | OpenSearch/Elastic and KQL-style hunting |
| `sigma/` | Sigma rules: `encoded_powershell.yml`, `lsass_access.yml`, `dns_tunnel.yml` | Rule authoring and review |
| `kql-queries.yaml` | KQL-style synthetic queries | OpenSearch/Elastic and KQL translation |

## Privacy and integrity

- The data is generated for teaching and testing, not collected from learners.
- No keystrokes, mouse movement, or terminal history are included.
- Queries and solver steps operate on these files; they do not inspect a real
  endpoint.
- A production deployment must not replace this pack with real learner data.
  Use a separate, governed dataset if an institution wants a live telemetry
  exercise.
