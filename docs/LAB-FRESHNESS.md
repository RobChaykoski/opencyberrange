# Lab freshness

Generated: **2026-11-27**. Policy: review every **365 days**; provisional difficulty evidence is flagged after **180 days**.

- Labs: **222**
- Stale or missing review: **0**
- Provisional difficulty evidence: **216**
- Promotion candidates (5+ observations): **0**

## By track

| Track | Labs | Stale | Provisional | Provisional over 2 quarters |
|---|---:|---:|---:|---:|
| AI | 5 | 0 | 5 | 0 |
| Forensics | 5 | 0 | 5 | 0 |
| High School | 18 | 0 | 18 | 0 |
| Identity | 4 | 0 | 4 | 0 |
| Linux | 37 | 0 | 37 | 0 |
| Malware | 10 | 0 | 10 | 0 |
| Metasploit | 8 | 0 | 8 | 0 |
| Network | 23 | 0 | 22 | 0 |
| OSINT | 10 | 0 | 10 | 0 |
| OT | 5 | 0 | 5 | 0 |
| Software Security | 6 | 0 | 6 | 0 |
| Web | 27 | 0 | 27 | 0 |
| Windows | 64 | 0 | 59 | 0 |

## Stale or missing review

None. Every lab has a review date inside the policy window.

## Oldest reviews

| Lab | Track | Reviewed | Age (days) |
|---|---|---|---:|
| `ai-1-1-prompt-injection-basics` | AI | 2026-11-08 | 19 |
| `ai-1-2-jailbreak-policy-bypass` | AI | 2026-11-08 | 19 |
| `ai-1-3-indirect-prompt-injection` | AI | 2026-11-08 | 19 |
| `forensics-1-1-windows-memory-volatility` | Forensics | 2026-11-08 | 19 |
| `forensics-2-1-voip-call-reconstruction` | Forensics | 2026-11-08 | 19 |
| `high-school-11-1-rangebox-log-detective` | High School | 2026-11-08 | 19 |
| `high-school-12-1-devfest-community-portal` | High School | 2026-11-08 | 19 |
| `high-school-9-1-rangebox-first-steps` | High School | 2026-11-08 | 19 |
| `high-school-9-2-rangebox-file-hunt` | High School | 2026-11-08 | 19 |
| `linux-1-1-ssh-service-detection` | Linux | 2026-11-08 | 19 |

## Difficulty promotion candidates

None yet.

## How to clear a finding

1. Run the lab canary or a live walkthrough.
2. Update the content, links, ATT&CK mapping, and tool list if needed.
3. Change `reviewed_at` and `review_status` in the same pull request as the content.
4. Re-run `python scripts/check-lab-freshness.py`.
