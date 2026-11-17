# Curriculum drift report

Generated **16 November 2026** from the tree at release **5.17.5**.

## Totals

| Definition | Value | Source |
|---|---:|---|
| Lab definitions | **210** | every `platform/labs/**/lab.yaml` |
| Tester manifests | **210** | `platform/tester/manifests/*.yaml` |
| Competency contracts | **210** | `platform/backend/app/data/competency-contracts.yaml` |
| Workbook-mapped labs | **201** | non-empty `workbook:` |
| Labs without a workbook link | **9** | remaining |
| Tracks | **13** | track folders under `platform/labs` |
| Registered in production | **210** | after discovery, verified 16 November 2026 |

The canonical definitions are in [Lab and content counts](COUNTS.md).

## Per-track inventory

| Track | Labs | Levels present | Workbook-mapped |
|---|---:|---|---:|
| AI | 3 | 1 | 3 |
| Forensics | 5 | 1, 2, 3 | 5 |
| High School | 18 | 9, 10, 11, 12 | 18 |
| Identity | 3 | 1, 2 | 3 |
| Linux | 37 | 1, 2, 3, 4, 5, 9 | 30 |
| Malware | 10 | 1, 2 | 10 |
| Metasploit | 8 | 1, 2 | 8 |
| Network | 22 | 0, 1, 2, 12 | 22 |
| OSINT | 8 | 1, 2 | 8 |
| OT | 4 | 1, 2 | 4 |
| Software Security | 2 | 1, 2 | 2 |
| Web | 26 | 1, 2, 3, **11** | 26 |
| Windows | 64 | 1–11 | 62 |

## Progression

- **Windows** now spans levels 1–11; level 11 is the Active Directory
  attack-and-remediation pathway.
- **Web** spans levels 1–3 and level 11; level 11 is the modern
  application-security pathway.
- **Network** includes level 0 (foundations) and level 12 (firewalls).
- **Linux** ends at level 9 (capstone), consistent with its seed.
- Every track has at least one lab and a level assignment. Level-11 labs exist
  in the seed, so a fresh install and discovery create them.

## Validation performed

| Check | Result |
|---|---|
| `validate-lab.py --all` | **210 labs, 0 failed checks** |
| `validate_lab_metadata.py --quiet` | **210 lab.yaml validated** |
| `generate-lab-outcomes.py --check` | **PASS** |
| `generate-lab-manifests.py --check` | **210 labs current** |
| Achievement tests | **25 passed** (`test_achievements`, `test_achievement_catalogue`) |
| Backend suite (clean PostgreSQL) | **908 passed** |
| Frontend suite | **6 passed**, build passed |
| Production discovery | **191 → 210** after the level-11 fix |

## Drift found and corrected

1. **Lab count:** the tree grew from 191 to 210; the README, COUNTS, validation
   report, manual, and deployment statement now agree.
2. **Track count:** the tree has **13** track folders, not 12. README, COUNTS,
   and the content-gap analysis were corrected.
3. **Level-11 registration:** an existing installation skipped the new labs
   because the `levels` table stopped at 9. The seed now defines level 11 for
   `windows` and `web`, and CLI discovery creates missing structure.
4. **File permissions:** the new lab files were host-owned `660`, unreadable by
   the non-root backend. The deployment now requires `a+rX` on the lab tree.

## Future features and their status

| Area | Status | Where |
|---|---|---|
| Active Directory pathway (9 labs) | **Implemented** | [Active Directory pathway](ACTIVE-DIRECTORY-PATHWAY.md) |
| Modern application security (10 labs) | **Implemented** | [Modern application-security pathway](MODERN-APP-SECURITY-PATHWAY.md) |
| Phone OSINT exercises | **Implemented** | [Phone OSINT exercises](PHONE-OSINT-EXERCISES.md) |
| Live memory forensics | **Implemented** | [Live memory forensics](LIVE-MEMORY-FORENSICS.md) |
| Software Security starter track | **Implemented; deployment/browser rehearsal pending** | [Software security workstream](SOFTWARE-SECURITY-WORKSTREAM.md) |
| OWASP API Top 10 matrix | **Partly implemented** | [API security labs](API-SECURITY-LABS.md) |
| OWASP Top 10 2025 matrix | **Plan** | [OWASP Top 10 labs](OWASP-TOP10-LABS.md) |
| Agentic / agent-abuse modules | **Plan** | [AI security and agentic labs](AI-SECURITY-AGENTIC-LABS.md) |
| Juice Shop exercises | **Plan / author guidance** | [Juice Shop labs](JUICE-SHOP-LABS.md) |
| OT lab prompts | **Prompt material for shipped OT labs** | [OT lab prompts](OT01-LAB-PROMPTS.md) |
| V3 HA lab pool | **Enterprise preview; not Community / Academic** | [V3 HA lab pool](V3-HA-LAB-POOL.md) |
| DevFest 2027 Cyber Discovery | **Planning** | [DevFest 2027](DEVFEST-2027-CYBER-DISCOVERY.md) |

## Remaining work

- **9 labs without a workbook link.** Add pages or record an exemption.
- **Live harness:** the static validators are clean; the 210-lab live harness
  still needs three clean runs. One AD and one appsec container have been built
  and proved to serve their flags.
- **Independent security testing:** not yet commissioned; see
  [Independent security testing](INDEPENDENT-SECURITY-TESTING.md).
