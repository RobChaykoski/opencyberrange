# Compliance posture: privacy, accessibility, automated scoring, and integration

Status: **working compliance dossier for Release 4. Not a certification.**
Owner: platform maintainers. Review with counsel, the institution's DPO/privacy
office, and its accessibility office before a procurement submission.

This page separates three things that are often mixed together in a vendor
questionnaire:

1. **Controls implemented in the product** — evidence is a file in this repo.
2. **Deployment choices** — the institution's host, region, retention, and
   identity provider decide these; the product supplies the hooks.
3. **Organizational certifications** — SOC 2, ISO 27001, and a signed VPAT are
   audits/attestations. This repository does not contain them, and no statement
   here should be read as claiming them.

## At a glance

| Requirement | Status | Where the control lives |
|---|---|---|
| FERPA (US education records) | Partial — product controls; institution remains controller | Role-based access, audit trail, export/erasure, no ad tech |
| COPPA (under 13) | Partial — deployment policy | `is_minor` flag, consent events, erasure, no targeted ads |
| GDPR / UK GDPR | Partial — product controls; DPA and transfer terms are organizational | Export, erasure ledger, retention, encryption, audit |
| CCPA/CPRA, SOPIPA (US states) | Partial | No sale/advertising, opt-outs, deletion, data minimisation |
| PIPEDA / FIPPA / MFIPPA (Canada) | Partial | Same controls; Canadian residency is a deployment choice |
| Quebec Law 25 | Partial — PIA and transfer assessment are organizational | Data inventory, export/erasure, breach-relevant audit, automated-decision transparency (see below) |
| WCAG 2.1/2.2 AA | Partial — tested surfaces pass; no full audit | `docs/ACCESSIBILITY.md` |
| ADA / Section 504 / 508 | Partial — accommodations implemented; VPAT not signed | Extended-time scaling, keyboard/screen-reader fixes |
| EU AI Act (high-risk AI) | Not triggered by the product's scoring | Deterministic flag check, no model, no profiling |
| GDPR Article 22 | Partial — human review path is institutional | Evidence + audit trail; final grades remain a human decision |
| LTI 1.3 / LTI Advantage | **Not implemented** | `docs/LTI.md` |
| HECVAT Full | Draft answer pack, not a completed third-party assessment | `docs/HECVAT.md` |
| SOC 2 Type II / ISO 27001 | **Not held** | Would require an external audit |
| VPAT / ACR | Draft, not signed | `docs/ACCESSIBILITY.md` |
| Canadian cloud hosting | Deployment choice | Self-hosted; the operator selects the region |
| Sub-processors | None by default | Self-hosted; optional SMTP provider only |

## 1. Data storage and privacy

### What the product does

- **Data minimisation.** Registration collects the account fields the
  institution configures; labs do not receive learner email addresses.
- **Lawful basis and notices.** `docs/PRIVACY-NOTICE.md` is the template the
  institution adapts. `docs/PRIVACY-AND-DATA-DELETION.md` documents purpose,
  retention, and deletion. `docs/ANALYTICS-GOVERNANCE.md` governs learning
  analytics and small-cohort suppression.
- **Access and portability.** `GET /api/auth/export` returns the account,
  course, completion, activity, VPN, consent, and identity-federation records.
  Secrets (password hash, TOTP secret, recovery codes, trusted-device tokens,
  WireGuard private key, IdP client secret, encrypted ID token) are excluded.
- **Erasure.** `app/services/erasure.py` deletes user-owned rows, anonymises
  security records, removes external identity links and SSO sessions/tickets,
  writes a keyed suppression entry so a backup restore cannot resurrect the
  account, and then performs best-effort external cleanup. The default backup
  retention is 30 days; restores re-apply the suppression ledger.
- **Encryption.** TLS is terminated at nginx for the browser and for OIDC
  discovery/token calls. Password hashes use Argon2id (bcrypt is verified and
  upgraded on login). WireGuard keys, TOTP secrets, IdP secrets, and OIDC ID
  tokens are encrypted with the application key. Database-at-rest encryption is
  a host/volume choice, not provided by the application.
- **Minors.** `is_minor` drives analytics/reporting exclusion. Consent events are
  recorded with a version. Auto-provisioned SSO accounts still need the
  institution's own parental-consent process; the product cannot infer age from
  an IdP assertion.
- **Logging.** Security events record actor, action, target, and IP; erasure
  removes or redacts identifying fields from activity records. Debug logging
  never writes secrets or learner email addresses.

### What the institution must decide

- Controller/processor roles and the DPA.
- Retention schedule (the product ships defaults, not legal advice).
- Whether any transfer outside the institution's region is permitted. The
  software is self-hosted, so the operator chooses the region and the
  sub-processors.
- A Quebec Law 25 PIA before deployment, including the automated-decision
  disclosure below.

## 2. Accessibility and evaluation

- Target: **WCAG 2.2 Level AA** for the learner-facing web application.
- Implemented: semantic landmarks, skip navigation, visible focus, keyboard
  operation, labelled form controls (including the institution sign-in panel),
  error announcements (`role="alert"`), reduced-motion handling, and the
  existing contrast work.
- Accommodations: `app/routers/labs.py` scales lab session length and extension
  by `session_accommodation_percent` (clamped to 100–300%) so an institution can
  grant extended time without special-casing a lab. There is no hard pass/fail
  timer in the learner path.
- Known limitations and the VPAT/ACR position are in `docs/ACCESSIBILITY.md`.
- A signed VPAT requires an accessibility audit against the current build; this
  repo provides the draft structure and evidence, not a signature.

## 3. Automated scoring and AI

- Scoring is **deterministic**: a submitted flag is compared with the session's
  seeded hash. There is no model, no inference, and no learner profiling in the
  grade path.
- The analytics and competency outputs are explicitly descriptive, not grades or
  predictions. The code and UI say so.
- Human oversight: final grades are set by the institution. The platform exposes
  completion evidence, attempts, hints, time, and an audit trail so a human can
  review a disputed outcome. There is no "AI assigns the final grade" path.
- EU AI Act: the product does not place an AI system on the market for
  high-stakes evaluation. If an institution uses the evidence inside its own
  high-risk process, that institution's risk management and human-oversight
  obligations apply.
- GDPR Article 22: because the product does not make a solely automated decision
  with legal or similarly significant effect, Article 22 is not engaged by the
  product itself. Institutions that treat a completion record as a final grade
  must provide the human-intervention and contest route described in
  `docs/AUTOMATED-SCORING.md`.
- Quebec Law 25: the same transparency statement applies; the institution must
  disclose automated decision-making in its own privacy notice and PIA.

## 4. LTI 1.3 / LTI Advantage

**Not implemented.** There is no launch, Deep Linking, NRPS, or AGS grade
passback endpoint in this build. The institution can use SSO (OIDC/SAML/LDAP)
for authentication today, but grades are not pushed to an LMS.

A compliant implementation needs at minimum:

- OIDC third-party initiated login and signed `id_token` validation against the
  LMS JWKS, with issuer/client/deployment binding and nonce/replay protection.
- Deep Linking 2.0 for resource selection.
- NRPS for rostering, or a deliberate decision to avoid roster import.
- AGS 2.0 line items, scores, and result retrieval using the LMS OAuth2 token
  endpoint and a signed client assertion.
- PII minimisation: map the LMS `sub` to a local account; do not forward email
  or names unless the institution enables it.
- Admin configuration for each LMS registration and a key-rotation path.

See `docs/LTI.md` for the design contract and test plan. Do not tell a buyer that
LTI works until those endpoints exist and have an integration test against at
least one LMS.

## 5. HECVAT and certifications

`docs/HECVAT.md` is a draft answer pack keyed to the HECVAT domains. It must be
reviewed and signed by the operator; it is not a completed HECVAT Full.

- **SOC 2 Type II:** not held. A Type II report requires an independent auditor
  over an observation period.
- **ISO 27001:** not held. Certification requires an accredited body and an ISMS
  operating over time.
- **VPAT/ACR:** draft only; see `docs/ACCESSIBILITY.md`.
- **Canadian hosting:** the product is self-hosted. The operator can deploy in a
  Canadian region; the repository cannot promise a region.
- **Penetration test:** internal review evidence is in
  `docs/SECURITY-REVIEW-2026-11.md`. That is not a third-party penetration test.

## Release 4 position

Release 4 ships SSO (OIDC/SAML/LDAP), the network device topology engine, the
security fixes in this branch, and the privacy/accessibility corrections above.
It does **not** claim LTI, SOC 2, ISO 27001, a signed VPAT, or a completed
HECVAT. Those are Release 5 work, tracked in `docs/RELEASE-5-SCOPE.md`, so a
procurement conversation starts from an accurate baseline.
