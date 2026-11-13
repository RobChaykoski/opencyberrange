# Release 5 scope: enterprise procurement and compliance

Status: **in development on the `release5` branch.** Production remains on the
signed Release 4 tag. The local image/stack bring-up is documented in
[`RELEASE-5-LOCAL.md`](RELEASE-5-LOCAL.md). Everything below is Release 5.

Source requirements: the university procurement pack covering FERPA, COPPA,
GDPR/UK GDPR, CCPA/SOPIPA, PIPEDA/FIPPA/MFIPPA, Quebec Law 25, AODA/WCAG 2.2 AA,
the EU AI Act, GDPR Article 22, HECVAT, LTI 1.3 Advantage, and Canadian data
localization.

## 1. Identity and LMS integration

- **LTI 1.3 core launch** - OIDC third-party initiated login, signed `id_token`
  validation, issuer/client/deployment binding, replay protection.
  Status: platform registry, login redirect, launch validation, account linking,
  AGS 2.0, NRPS 2.0, Deep Linking 2.0, and the admin console are implemented on
  `release5`; a real LMS staging test remains.
- **LTI Advantage AGS 2.0** — line items, score passback, result retrieval, and
  an instructor-review gate before any score leaves the platform.
- **NRPS 2.0** — roster sync with the minimum claims (`sub`, role, context).
  Email and display name are opt-in per institution.
- **Deep Linking 2.0** — resource selection from the LMS.
- **Canadian Access Federation** — CAF metadata onboarding and test plan.
- **LTI admin console** — per-LMS registration, key rotation, enable/disable,
  and a delivery log.

Exit criteria: a launch and a grade passback pass against at least one real LMS
(Canvas, Brightspace, or Moodle) in a staging tenant, with PII-minimal claims.

## 2. Multi-tenancy and RBAC

- **Tenant isolation** — a tenant key on every learner-owned table, enforced in
  the session/query layer, with a migration and a cross-tenant test suite.
  Alternatively, a documented single-tenant appliance with one database per
  institution.
- **TA role** — section/course scoping, no global roster access, no account
  administration.
- **Permission matrix** — university admin, instructor, TA, student; audited on
  every privileged action.
- **Per-tenant retention and purge** — term-end purge, contract-termination
  archive export, and anonymisation, with a dry-run preview.

Exit criteria: a cross-tenant access test cannot read another tenant's rows;
TA access is denied outside the assigned section.

## 3. Accommodation engine

- Per-student time multiplier (1.5x, 2x, custom) attached to the user and
  applied consistently to labs, quizzes, and assignments.
- Pause/resume clock with a recorded reason and an audit trail.
- Per-student due-date extensions that persist across a course.
- Instructor/administrator UI, export coverage, and a WCAG 2.2 AA review.

Exit criteria: the same student receives the multiplier and extension in every
assessment type, and the values survive export/import.

## 4. Automated decision transparency

- A per-submission notice that the result was produced by deterministic logic.
- The primary factors shown to the student (flag match, rubric criterion,
  attempt, time).
- A "request human review" workflow routed to the instructor, with status and
  outcome.
- An append-only score ledger: calculation inputs, rule version, timestamp,
  reviewer, and override reason.
- A bias/validation note limited to what the product actually does: deterministic
  flag matching and equal-access testing. No writing-style model exists.

Exit criteria: a student can see why a result was produced and obtain a human
decision; the override is auditable.

## 4a. Minor-account mode and retention

The high-school track means a deployment can include learners under 18 (and,
depending on jurisdiction, under 16). The product already has an `is_minor`
flag, consent events, analytics exclusion, and erasure; Release 5 turns those
controls into a documented mode.

- **Enrollment consent capture** — record the institution's parental/guardian
  consent reference at enrollment. The institution owns the consent process;
  the platform records that it happened, not the identity documents.
- **Restricted surfaces** — minor accounts are excluded from public
  leaderboards, public celebrations, career salary views, and cohort analytics
  unless the institution explicitly opts in with a documented basis.
- **Retention clock** — per-cohort retention dates for learner records,
  exports, and backups, with a dry-run purge and a completion record.
- **Procurement handoff** — a one-page minor-mode statement, the retention
  schedule, and the DPA schedule that covers FIPPA/MFIPPA, PIPEDA, and COPPA
  where applicable.
- **Audit evidence** — consent, restriction changes, purge runs, and
  administrator overrides are recorded in the existing audit/ledger path.

Exit criteria: a minor account cannot appear in a public leaderboard or
identifiable analytics view by default; consent and retention events are
auditable; a term-end purge can be previewed and completed with evidence.

## 4b. RangeBox modernization

The current image is Xvfb + XFCE4 + x11vnc + websockify/noVNC on
`kalilinux/kali-rolling`. The platform contract is sound; the runtime inputs and
the browser-desktop layer need a Release 5 pass.

- **Reproducible inputs** — pin the Kali snapshot (and digest) and pin SecLists
  to a commit or verify a checksum. A rolling base with an unverified `master`
  download does not belong behind a signed supply-chain lock.
- **Resolve the security-model mismatch** — either remove passwordless sudo and
  grant only the capabilities the tooling needs, or document explicitly that
  the student has root inside a caged container and that the host firewall is
  the boundary. Re-enable the Firefox content sandbox, or record why it is off.
- **Browser-desktop evaluation** — benchmark KasmVNC as the drop-in replacement
  for x11vnc/noVNC. Evaluate Selkies as the WebRTC stretch goal only if pilot
  latency on school networks justifies the signaling/TURN work.
- **Terminal-only mode** — ship the PRD Phase 4 ttyd + xterm.js mode for slow
  connections and command-only labs.
- **Licensing discipline** — keep Burp Community and other non-redistributable
  tools out of the image; add only tools whose licences permit the bundle.

Exit criteria: two RangeBox builds from the same pinned inputs are equivalent;
the documented security model matches the image; one browser-desktop path is
selected and tested; terminal mode works for a command-only lab; the licence
inventory still passes.

## 4c. Frontend serving-layer modernization

Evaluate a Chainguard or distroless nginx base for the frontend image. This is a
serving-layer change only: the frontend container serves the SPA, proxies
`/api`, and gates `/wiki`; it does not execute lab content. RangeBox, UbuntuBox,
and RemnuxBox keep their own images and are not affected.

- **Remove the shell dependency.** The current `docker-entrypoint.sh` is a shell
  script that selects the TLS config at start-up. A distroless image has no
  shell, so move that choice to build time (separate HTTP/HTTPS images) or a
  tiny init/sidecar. The old envsubst templating for the wiki variables is
  already gone: `WIKI_BASE_URL` is a build-time fallback, `wiki_origin` and
  `wiki_cookie_domain` are runtime settings, and `frame-ancestors` is derived
  from the auth-subrequest header.
- **Preserve header behaviour verbatim.** Re-run
  `scripts/check-nginx-security-headers.py`, the CSP-hash check, and the wiki
  header checks. A missing `add_header` in one location is the exact failure
  mode the current config comments warn about.
- **Preserve the wiki auth path.** Confirm `auth_request`, the named 401/403
  redirect locations, and the CyberChef proxy path behave identically.
- **Provide a healthcheck that exists.** Distroless images may not ship
  `wget` or `curl`; use the base image's health mechanism or a sidecar.
- **Smoke-test the critical path.** Load one workbook-heavy exercise, open
  CyberChef, confirm the wiki frame and PDF export, and check the security
  headers. Lab images and exercise content do not need revalidation.

Exit criteria: the serving image builds without a shell, the header/auth/proxy
checks pass, and one workbook-loading exercise works end to end after the swap.

## 5. Procurement artifacts

- **HECVAT Full** — complete and review the draft in `docs/HECVAT.md`.
- **VPAT 2.5 / ACR** — commission an accessibility audit against the current
  build; publish the signed report.
- **SOC 2 Type II** — engage an auditor and operate the controls over the
  observation window.
- **ISO 27001** — optional; requires an accredited body and an operating ISMS.
- **DPA** — counsel review of `docs/DPA-TEMPLATE.md`, with the institution's
  FIPPA/MFIPPA/Law 25 schedules completed.
- **Quebec PIA and TRA support pack** — data inventory, transfer map, and
  automated-decision statement for the institution's assessment.
- **Canadian hosting** — a documented deployment profile with a Canadian region,
  encrypted volumes, and a sub-processor register.

Exit criteria: no procurement claim is made that is not backed by a dated
artifact or an external report.

## 6. Security and retention operations

- Whole-institution archive export.
- Term-end and contract-end purge jobs with a dry run and a certificate of
  destruction.
- Encryption-at-rest profile for database volumes and backups (LUKS or an
  encrypted object store), documented per deployment.
- Sub-processor register and a PII-stripping rule for any optional outbound
  service (SMTP is the only default candidate).

Exit criteria: an operator can produce an export, purge a term, and show the
encryption profile without touching the database by hand.

## 7. Weekly challenge quizzes (Jeopardy-style)

- **Weekly board** — a server-published set of categories and clues, with
  difficulty values (for example 100–500), a fixed open/close window, and a
  documented retry policy per clue.
- **Answer integrity** — clues and answers are graded server-side. The client
  never receives the answer key before submission, and the bank rotates per
  cohort so a shared answer sheet does not carry week to week.
- **Cyber DNA points** — a correct clue awards points to the competency branch
  it assesses, subject to the existing **99 cap**, per-branch decay, and a
  published weekly earning ceiling. Points are evidence of practice, not a
  grade, a public ranking, or a prediction of ability.
- **Question bank** — items map to `competency-taxonomy.yaml` and are reviewed
  for accuracy, accessibility, and answer quality. Each item records its source,
  difficulty, category, and the DNA branch it feeds.
- **Instructor tools** — schedule a week, preview the board, inspect item-level
  difficulty and discrimination, and retire a faulty clue without rewriting the
  learner's history.
- **Accessibility** — keyboard-first board, no colour-only categories, screen
  reader labels for values and state, and accommodation-aware timers.
- **Anti-farming** — weekly ceiling, first-correct-only scoring, no points for
  replaying a clue, and an audit trail for any manual adjustment.

Exit criteria: a learner completes a weekly board, DNA increases only within the
published cap and ceiling, replaying a clue cannot farm points, and an instructor
can retire a faulty clue without rewriting the week.

The seeded bank is
`platform/backend/app/data/certification-question-banks.yaml` (81 original items
across 9 certification pathways, each with a career pathway). Source and licence
notes are in `docs/QUESTION-BANK-SOURCES.md`.

## Not in Release 5 by default

- A general-purpose AI grader. The product does not grade free text and does not
  send learner work to an LLM. Adding one would trigger the EU AI Act high-risk
  and Article 22 work as a separate program.
- SOC 2 or ISO certification before an auditor has issued a report.

## Release boundaries

| Release | Contents |
|---|---|
| Release 4 | SSO (OIDC/SAML/LDAP) with a deployment-wide switch, network device topology engine, API exposure fixes, SSO privacy export/erasure, institution sign-in accessibility, mandatory setup token, HttpOnly wiki session and runtime wiki-origin settings, signed release and supply chain |
| Release 5 | LTI 1.3 Advantage, multi-tenancy/TA/RBAC, accommodation engine, minor-account mode and retention, automated-decision transparency, HECVAT/VPAT/SOC 2/ISO/DPA/PIA artifacts, RangeBox modernization, frontend serving-layer modernization, weekly Jeopardy-style challenge quizzes that feed Cyber DNA |

Candidate additions for Release 5 (not yet committed in this scope):

- Open Badges 3.0 credential issuance from the existing certificate data.
- Minor-account mode, parental-consent handoff, and a published retention
  schedule to complete the procurement pack.
