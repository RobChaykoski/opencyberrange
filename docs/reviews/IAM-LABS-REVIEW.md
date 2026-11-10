# Identity & Access labs: design, student-tester, and curriculum review

Date: **2026-11-10**
Scope: the new Identity & Access track, three labs, the shared target, and the
workbook chapter.

## Sample

| Lab | Level | Difficulty | Estimated time | Target mode |
|---|---|---|---|---|
| `identity-1-1-secure-authentication` | 1 | beginner | 45 min | Forgeable session cookie |
| `identity-1-2-oauth-oidc-sso` | 1 | intermediate | 50 min | OAuth redirect and token trust |
| `identity-2-1-identity-lifecycle` | 2 | beginner | 40 min | Stale leaver account and token |

Environment: static lab validation, in-process target smoke tests, workbook
review, and documentation checks. No live RangeBox desktop session or live
platform completion was recorded.

## Summary

| Lab | Discoverability | Prerequisites | Instructions | Commands | Hints | Flag path | Consistency | Timing | Language/access | Learning outcome | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Secure authentication | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | Pass |
| OAuth/OIDC | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | Pass |
| Identity lifecycle | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | Pass |

Timing is scored 1 because the estimates are provisional until a live learner
walkthrough is recorded.

## Design decisions

- **A dedicated track, not a stray lab.** Identity and access is a distinct
  domain with its own vocabulary and controls. The track has two levels:
  authentication/federation and lifecycle.
- **Scaffolding fades.** Lab 1 gives the learner a demo account and a debug
  cookie format. Lab 2 requires tracing a multi-step federation flow. Lab 3
  returns to evidence reading and asks for an offboarding decision.
- **The target is deliberately vulnerable only in the taught area.** The
  session lab intentionally lacks cookie attributes and server-side sessions;
  the OAuth lab intentionally lacks a redirect allowlist, `state`, and PKCE; the
  lifecycle lab intentionally leaves a leaver token active. Nothing else is
  weakened.
- **One concept, one flag.** Each lab has a deterministic path and a single
  reachable flag. The capstone is a workbook review, not another target.
- **Builder and defender outcomes.** Each lab ends with a fix table and analysis
  questions, so the learner practises remediation language as well as the
  exploit.

## Inclusive curriculum review

- Scenarios use a community centre, a volunteer portal, and a fictional
  single sign-on provider. No learner is cast as a hoodie-wearing attacker.
- The person who reported the issue and the person who left the organisation
  are not blamed. The workbook explains the process failure.
- Plain language defines session, cookie attribute, authorization code, state,
  PKCE, access token, joiner/mover/leaver, least privilege, and access review.
- Every lab has a browser path and a terminal path where one is useful. The
  lifecycle lab can be completed with a form; the authentication lab can use
  `curl`.
- No colour-only status and no emoji-only icons.

## Safety review

- All accounts, tokens, domains, and providers are fictional. Domains use
  reserved `.example` names; the OAuth attacker callback is a simulation on the
  same training host.
- The targets are read-only, run as a non-root user, drop all capabilities, set
  `no-new-privileges`, and cap CPU and memory.
- The target never calls the internet or a real identity provider.
- The intentionally weak cookie is confined to the isolated target. The
  workbook explains that it is a teaching defect, not a pattern to deploy.
- No real credentials, sessions, personal data, or production tokens are used.

## Evidence

- `validate-lab.py` for each lab: **21/21 checks passed**.
- In-process target smoke tests: **39 checks passed** across the three modes.
  Covered: page rendering, no flag in the landing page, security headers,
  login and cookie issuance, staff denial, forged admin access, redirect URI
  delivery, token exchange, profile access, anonymous denial, directory
  evidence, read-only token denial, admin token access, and the flag.
- Lab test steps:
  - Authentication: login sets a cookie, staff is denied, forged admin reaches
    the flag.
  - OAuth: the code redirects to the unvalidated callback, the code exchanges,
    anonymous `/me` is denied, the token reads the profile.
  - Lifecycle: anonymous and read-only tokens are denied, the stale admin token
    reaches the flag.
- Workbook and lab metadata agree on hostnames, ports, paths, flags, tokens,
  and the order of operations.
- Hints scaffold concept, observation, and fix; none contains the real flag.
- `Workbook/COVERAGE.md` and the NICE mapping are updated with the new track.

## Findings

### Blocker / Major

None.

### Minor

1. **Live UI and RangeBox not verified.** The targets and test paths were
   smoke-tested, but the in-platform track card, level unlock, workbook
   rendering, and real learner completion were not exercised in a browser
   session. Record a live walkthrough before calling the timings final.
2. **The OAuth lab simulates the provider, client, and attacker callback on one
   host.** This is deliberate and explained in the workbook. A learner may ask
   why the attacker domain is not separate; the answer is that the exercise
   isolates the control, not the network topology.
3. **The password-hashing weakness is discussed but not exploited.** The lab
   focuses on session forgery. Cracking an MD5 hash would be a different lab and
   would distract from the session lesson. The workbook still asks why fast
   hashes are unsuitable.

### Suggestions

- Add a follow-on **passkeys/WebAuthn** lab for phishing-resistant MFA.
- Add an **OAuth resource-server** lab for token audience and scope validation.
- Add an **access-review artefact** exercise where the learner produces a
  signed review record, not only a flag.
- Record a live learner walkthrough for each lab and replace the provisional
  timings.

## Cross-lab themes

- Identity is the control plane: a valid-looking account or token can be the
  whole attack.
- A login event is not a session design; authentication is not authorization.
- Federation trust depends on exact redirects, state, PKCE, and token checks.
- Access does not expire by itself; lifecycle work is a process, not a setting.
- The learner should be able to name the failed control and the fix, not only
  recover the flag.

## Not verified

- Live browser rendering of the new track, level cards, and workbook pages.
- RangeBox access to the target hostnames on a restricted network.
- Actual learner completion time and the quality of the capstone answers with a
  real class.
- The platform's in-app exercise tester executing every new test step on a
  deployed host.
