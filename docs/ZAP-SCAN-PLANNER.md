# OWASP ZAP scan planner

The platform exposes OWASP ZAP in the tool catalogue as a **scan planner**, not
as an embedded scanner. ZAP is a desktop application; it cannot run inside the
browser panel. The planner writes an authorised command, report paths, and a
triage checklist. It never sends a request or runs a scan.

## Where it lives

- **Tools → ZAP scan** in the sidebar, or **Tools → All tools → Open in panel**.
- **ZAP** in the active-lab toolbar.
- Direct route served from the frontend image: `/tools/zap-scan/`.

The panel is same-origin static HTML, so it works on an isolated range and needs
no CSP change. The **Download ZAP** button opens
<https://www.zaproxy.org/download/> in a new tab.

## What the planner generates

| Choice | Command |
|---|---|
| Baseline, Docker | `docker run --rm -t -v "$PWD:/zap/wrk/:rw" zaproxy/zap-stable zap-baseline.py -t '<target>' -r zap-report.html -J zap-report.json -m 5 -l WARN` |
| Full, Docker | The same image with `zap-full-scan.py` |
| Local install | `zap-baseline.py` or `zap-full-scan.py` with the same flags |

The planner supports HTML, JSON, and Markdown reports, a scan-minute budget, and
a minimum report level (`INFO`, `WARN`, `FAIL`). The copy button stays disabled
until the learner confirms:

1. written authorisation for the target and scan type;
2. a disposable target with a restore path;
3. a minimal scope (one practice app, no production host).

A full scan is an active scan. It can change or delete data, so the planner
shows a stronger warning and starts in baseline mode.

## Safety and privacy

- **No scan from the page.** It is a command builder and checklist.
- **No network egress.** The page does not resolve, probe, or fetch the target.
- **No credentials in the URL.** The URL validator rejects `user:password@` and
  characters that would need more than single-quote escaping.
- **No learner data.** A target, scan choice, or report is never sent to the
  platform. The planner has no API call and no storage beyond the local theme
  preference.
- **Targets are practice apps.** Use a lab target or a disposable local app. Do
  not point a full scan at a shared service.

## Reading the report

The planner's checklist follows the analyst workflow:

1. Sort by risk and read the request/response evidence, not only the alert name.
2. Reproduce each finding by hand. ZAP reports candidates; a person confirms an
   issue.
3. Mark false positives. A WAF, shared hosting, and a custom login flow create
   noise.
4. Write the impact in the app's own terms: what data, whose account, what
   action.
5. Record the fix, the retest, and the residual risk in the workbook or
   DefectDojo.

ZAP cannot tell you whether a business rule is wrong, whether one user can reach
another user's data, whether a finding is exploitable in this deployment's
network and identity context, or whether the app is safe. A clean scan is not a
security proof.

## Attribution

OWASP ZAP is an Apache-2.0 project by the ZAP community. The planner is
first-party static HTML; it does not bundle, download, or redistribute ZAP. If a
future lab image installs ZAP, add the licence text, SBOM entry, and image pin to
the release records.

## Lab follow-up

The dedicated Web application security lab is implemented as
`web-11-11-zap-baseline-triage`:

- **Target:** a local Flask practice app on the lab network, with synthetic
  community-arts content, a public export directory, missing headers, and no
  production dependency.
- **Task:** run a baseline scan, triage the report, confirm the directory
  browsing finding by hand, recover the assessment token, and write a
  remediation and retest note.
- **Evidence:** the learner's triage note and remediation plan, not the raw scan
  output. The report may contain target URLs and response snippets, so keep it
  in the lab and do not import it into a GRC record.
- **Pathway:** the lab is listed in `modern-appsec-pathway.yaml` under MAS-06
  (DevSecOps and CI/CD Security) and in the Web 11 workbook.
- **Harness:** the lab manifest is generated from `lab.yaml`; run
  `python scripts/lab_harness.py --lab web-11-11-zap-baseline-triage` and record
  the result in the lab review notes.
- **Out of scope for the planner:** authenticated scans that require real
  credentials, production hosts, and automated exploit chaining.

## Verified lab findings

A local ZAP baseline scan of `web-11-11-zap-baseline-triage` on 25 November 2026
returned the intended triage set: Directory Browsing (10033) at `/files/`, Cookie
No HttpOnly Flag (10010), Cookie without SameSite (10054), Server version
disclosure (10036), `X-Powered-By` disclosure (10037), CSP missing (10038),
anti-clickjacking header missing (10020), `X-Content-Type-Options` missing
(10021), Permissions Policy missing (10063), and CORP/COEP/COOP missing (90004).
The directory listing exposes `assessment-token.txt`, which is the manual
confirmation step.

## Acceptance checks

- A valid `http://` or `https://` target produces a command; invalid input does
  not.
- The copy button is disabled until all three authorisation boxes are ticked.
- Baseline and full modes produce different scripts; full mode shows the active
  scan warning.
- Docker and local modes produce the expected prefixes.
- The page makes no network request when a target is typed or a report format is
  changed.
- Keyboard and screen-reader use: labelled fields, a visible focus ring, and a
  status announcement after copying.
