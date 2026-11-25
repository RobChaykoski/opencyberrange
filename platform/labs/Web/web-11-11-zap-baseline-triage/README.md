# ZAP baseline triage lab

`web-11-11-zap-baseline-triage` is a Web application security lab about scanner
triage, not scanner worship. The learner runs an authorised ZAP baseline scan
against a small practice app, reads the report, confirms a directory-browsing
finding by hand, recovers the assessment token, and writes a remediation and
retest note.

## Target

- A single Flask practice app on port 80.
- Synthetic community-arts content only; no real member, donor, or event data.
- Deliberate weaknesses: a public `/files/` directory listing, missing security
  headers, an over-sharing cookie, a framework header, and a reflected search
  field for an optional full-scan comparison.
- The assessment token is in `containers/webapp/files/assessment-token.txt`.

## Safety

- Use the ZAP scan planner or ZAP locally against this lab target only.
- A baseline scan is passive. A full scan is active and can change data; keep it
  on this disposable target.
- Do not point ZAP at a public service, another learner's host, or a production
  deployment.
- The target makes no outbound calls and has no credentials.

## Files

| Path | Purpose |
|---|---|
| `docker-compose.yml` | Single `webapp` service with the lab `ip_offset` |
| `containers/webapp/app.py` | Flask target |
| `containers/webapp/files/` | Synthetic shared exports and the assessment token |
| `lab.yaml` | Scenario, outcomes, hints, topology and harness steps |
| `Workbook/CH_WEB11_AppSec_Pathway/11_ZAP_Baseline_Triage.md` | Learner workbook |

## Verified baseline findings (2026-11-25)

A local ZAP baseline scan against the lab target reported the intended
triage set:

| ZAP ID | Alert | Evidence |
|---|---|---|
| 10033 | Directory Browsing | `/files/` |
| 10010 | Cookie No HttpOnly Flag | `arts_session` |
| 10054 | Cookie without SameSite Attribute | `arts_session` |
| 10036 | Server Leaks Version Information | `Server: nginx/1.18.0` |
| 10037 | Server Leaks Information via `X-Powered-By` | `Flask practice app` |
| 10038 | Content Security Policy Header Not Set | `/`, `/files/`, `/search` |
| 10020 | Missing Anti-clickjacking Header | `/` |
| 10021 | X-Content-Type-Options Header Missing | `/` |
| 10063 | Permissions Policy Header Not Set | `/` and `/files/` |
| 90004 | CORP / COEP / COOP header missing | `/` and `/files/` |
| 20020 | nginx version with known vulnerabilities | synthetic `Server` header |

The first row is the intended manual-confirmation finding: the directory lists
`assessment-token.txt`. The rest are triage practice and a reminder that a
scanner report contains both real issues and low-value noise.

## Run and verify

```bash
docker compose -f platform/labs/Web/web-11-11-zap-baseline-triage/docker-compose.yml up -d --build
python scripts/generate-lab-manifests.py
python scripts/validate-lab.py platform/labs/Web/web-11-11-zap-baseline-triage
python scripts/lab_harness.py --lab web-11-11-zap-baseline-triage
```

The harness should pass the site, directory listing, token, framework-header and
flag steps. Record the run in the lab review notes.
