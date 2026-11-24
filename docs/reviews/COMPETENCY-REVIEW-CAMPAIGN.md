# Competency review campaign

Snapshot: 24 November 2026. Usage counts are from production; review
counts are from the contract overrides.

## Status

- Total contracts: **215**
- Reviewed: **25** (11.6%)
- Pending: **190**

| Track | Total | Reviewed | Pending |
|---|---:|---:|---:|
| Windows | 64 | 16 | 48 |
| Linux | 37 | 6 | 31 |
| Web | 26 | 1 | 25 |
| Network | 22 | 2 | 20 |
| High School | 18 | 0 | 18 |
| Malware | 10 | 0 | 10 |
| OSINT | 9 | 0 | 9 |
| Metasploit | 8 | 0 | 8 |
| AI | 5 | 0 | 5 |
| Forensics | 5 | 0 | 5 |
| OT | 5 | 0 | 5 |
| Identity | 4 | 0 | 4 |
| Software Security | 2 | 0 | 2 |

## Where signatures live

The 25 unsigned drafts exist on **development** and **production** (seeded
24 November 2026). The strict export gate reads the database of the host
where it runs, so signatures must be recorded on **production** (or imported
with the administrator export) before the gate can pass there.

Signing on development does not satisfy production. The gate refuses a
`review_status: reviewed` override without a matching signed database row on
the host where it runs.

## First batch: the 25 legacy drafts

These already have drafts and are the shortest path to a meaningful gate:

- `linux-1-1-ssh-service-detection` - 8 completions, 1 assignments, 11 sessions
- `linux-1-2-multi-service-discovery` - 2 completions, 1 assignments, 3 sessions
- `linux-1-3-service-interaction` - 2 completions, 1 assignments, 0 sessions
- `linux-1-4-non-standard-port-discovery` - 2 completions, 1 assignments, 0 sessions
- `linux-1-5-nse-script-enumeration` - 2 completions, 1 assignments, 0 sessions
- `linux-1-6-version-vulnerability-identification` - 2 completions, 1 assignments, 0 sessions
- `network-0-1-ping-basics` - 2 completions, 1 assignments, 3 sessions
- `network-0-2-dns-basics` - 2 completions, 1 assignments, 0 sessions
- `web-1-1-basic-directory-enumeration` - 3 completions, 1 assignments, 5 sessions
- `windows-1-1-basic-port-scan` - 8 completions, 1 assignments, 5 sessions
- `windows-1-2-multiple-port-discovery` - 6 completions, 1 assignments, 1 sessions
- `windows-1-3-windows-service-version-detection` - 5 completions, 1 assignments, 0 sessions
- `windows-1-4-windows-os-detection` - 5 completions, 1 assignments, 0 sessions
- `windows-1-5-comprehensive-windows-enumeration` - 3 completions, 1 assignments, 0 sessions
- `windows-2-1-smb-connection-test` - 3 completions, 1 assignments, 0 sessions
- `windows-2-2-smb-share-listing` - 3 completions, 1 assignments, 0 sessions
- `windows-2-3-smb-anonymous-share-access` - 3 completions, 1 assignments, 0 sessions
- `windows-2-4-smb-file-retrieval` - 3 completions, 1 assignments, 0 sessions
- `windows-2-5-smb-null-session-connection` - 3 completions, 1 assignments, 0 sessions
- `windows-2-6-smb-null-session-share-enumeration` - 3 completions, 1 assignments, 0 sessions
- `windows-2-7-smb-user-enumeration-via-null-session` - 3 completions, 1 assignments, 0 sessions
- `windows-2-8-smb-comprehensive-null-session-enumeration` - 3 completions, 1 assignments, 0 sessions
- `windows-3-1-smb-manual-credential-test` - 3 completions, 1 assignments, 0 sessions
- `windows-3-2-smb-multiple-credential-testing` - 3 completions, 1 assignments, 0 sessions
- `windows-3-3-smb-single-user-brute-force` - 3 completions, 1 assignments, 0 sessions

## Highest-use pending labs

Ranked by `3 x completions + 2 x assignments + sessions` on production.

| # | Lab | Track | Completions | Assignments | Sessions |
|---:|---|---|---:|---:|---:|
| 1 | `software-security-1-1-hidden-export-route` | Software Security | 3 | 1 | 7 |
| 2 | `ai-1-1-prompt-injection-basics` | AI | 2 | 1 | 6 |
| 3 | `high-school-9-1-rangebox-first-steps` | High School | 1 | 1 | 5 |
| 4 | `linux-2-1-ssh-basic-login` | Linux | 1 | 1 | 5 |
| 5 | `web-1-2-technology-identification` | Web | 2 | 1 | 1 |
| 6 | `windows-3-4-smb-username-enumeration-and-brute-force` | Windows | 2 | 1 | 1 |
| 7 | `osint-2-2-public-homepage` | OSINT | 0 | 1 | 6 |
| 8 | `software-security-2-1-diagnostics-command-injection` | Software Security | 0 | 1 | 6 |
| 9 | `web-1-3-http-methods-enumeration` | Web | 2 | 1 | 0 |
| 10 | `malware-1-1-eicar-triage` | Malware | 1 | 1 | 2 |
| 11 | `osint-1-1-public-footprint` | OSINT | 1 | 1 | 2 |
| 12 | `web-1-4-header-analysis` | Web | 1 | 1 | 2 |
| 13 | `high-school-12-1-devfest-community-portal` | High School | 1 | 1 | 1 |
| 14 | `osint-2-1-source-code-intelligence` | OSINT | 1 | 1 | 1 |
| 15 | `windows-6-2-mssql-version-and-instance-enumeration` | Windows | 1 | 1 | 1 |
| 16 | `forensics-1-1-windows-memory-volatility` | Forensics | 0 | 1 | 3 |
| 17 | `linux-2-2-ssh-user-discovery` | Linux | 1 | 1 | 0 |
| 18 | `linux-2-3-ssh-file-discovery` | Linux | 1 | 1 | 0 |
| 19 | `linux-2-4-ssh-command-execution` | Linux | 1 | 1 | 0 |
| 20 | `linux-2-5-ssh-history-analysis` | Linux | 1 | 1 | 0 |
| 21 | `linux-2-6-ssh-privilege-escalation` | Linux | 1 | 1 | 0 |
| 22 | `network-0-3-name-or-network` | Network | 1 | 1 | 0 |
| 23 | `network-1-1-port-scan-detection` | Network | 1 | 1 | 0 |
| 24 | `osint-1-2-image-intelligence` | OSINT | 1 | 1 | 0 |
| 25 | `web-1-5-subdomain-discovery` | Web | 1 | 1 | 0 |
| 26 | `web-1-6-comprehensive-web-reconnaissance` | Web | 1 | 1 | 0 |
| 27 | `web-2-1-basic-sql-injection-get` | Web | 1 | 1 | 0 |
| 28 | `windows-3-5-smb-full-credential-attack` | Windows | 1 | 1 | 0 |
| 29 | `windows-4-1-rdp-service-detection` | Windows | 1 | 1 | 0 |
| 30 | `windows-4-2-rdp-version-enumeration` | Windows | 1 | 1 | 0 |

## Process

1. Open **Contract review** as an instructor with subject-matter authority.
2. Inspect the contract snapshot, competencies, evidence, reliability, and criteria.
3. Sign, or request changes with a recorded rationale.
4. Export the approved rows:

   ```bash
   python scripts/export-contract-reviews.py --export --database-url "$DATABASE_URL"
   python scripts/export-contract-reviews.py --write-overrides --database-url "$DATABASE_URL"
   python scripts/export-contract-reviews.py --check
   ```

5. Commit the manifest and overrides, then run the release checks.
6. Set the next review date at 12 months and keep the refreshment cycle.

## Cadence

| Week | Batch | Target |
|---|---|---|
| 1 | The 25 legacy drafts | Sign all 25 |
| 2-3 | Top 30 pending by usage | Clear the highest-use labs |
| 4-6 | Windows remainder (48 pending) | Track complete |
| 7-8 | Linux (31) and Network (20) | Track complete |
| 9-10 | Web (25), High School (18) | Track complete |
| 11-12 | Malware, OSINT, Metasploit, AI, Forensics, OT, Identity, Software Security | Track complete |

## Progress record

| Date | Reviewed | Pending | Notes |
|---|---:|---:|---|
| 2026-11-24 | 25 | 190 | Campaign opened; usage ranking recorded |
