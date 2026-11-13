# Procurement requirements: traceability

Status: **Release 5 in progress.** Reviewed against the code in this branch on
2026-11-13. Each row states what exists, what is partial, and what is a
deployment or organizational obligation. "Implemented" means there is code and a
test or documented evidence in this repository — not a certification.

## Legend

- **Yes** — implemented in the product.
- **Partial** — a control exists, but a scope limit or manual step remains.
- **Gap** — not implemented.
- **Org** — the institution or operator must provide it (audit, hosting,
  contract, policy). The product can supply evidence but not the attestation.
- **N/A** — the product does not perform the activity.

## 1. Data protection and residency

| Requirement | Status | Evidence / limit |
|---|---|---|
| Sub-processor localization (Canada or PII-stripped) | Partial / Org | Self-hosted by default; the only optional outbound service is SMTP. No analytics, error-logging, or AI SDK is bundled. The operator chooses the SMTP and hosting region. |
| Encryption in transit, TLS 1.2/1.3 | Yes | `platform/frontend/nginx-ssl.conf` sets `TLSv1.2 TLSv1.3`. Backend-to-IdP calls use TLS; `SSO_ALLOW_INSECURE_HTTP` is a dev-only opt-in. |
| Encryption at rest, AES-256 | Org | Secrets (WireGuard keys, TOTP, IdP secrets, OIDC ID tokens) are encrypted with the application key. Database/file backup encryption is a host/volume responsibility; the repo does not enforce LUKS or an encrypted object store. |
| Tenant isolation (one university cannot see another) | Gap for shared hosting; Yes for single-tenant | This is a **single-tenant deployment**. Two institutions on one database are not isolated. Multi-tenancy is a schema-wide change and is not in Release 4. |
| Granular RBAC: University Admin / Instructor / TA / Student | Partial | Roles are `admin`, `instructor`, `student` (`models.py:105`). There is **no TA role**. Instructor access is scoped to owned courses, and admin is global. A TA role with section-level scope is a gap. |
| Automated retention and term-end purge | Partial | Account erasure, activity purge, backup retention (30 days), and SSO state/ticket cleanup exist. There is no institution-level "purge this term" batch tool or contract-termination export. |
| Full record export for institutional archiving | Partial | Self-service `GET /api/auth/export` and admin user transfer exist. A whole-institution archive export is a gap. |
| Breach-relevant logging | Yes | Admin/activity audit trail with actor, action, target, IP; erasure anonymises it. |
| Quebec Law 25 PIA | Org | The product supplies this inventory, `docs/PRIVACY-AND-DATA-DELETION.md`, and the automated-decision statement below. A PIA is completed by the institution. |
| Quebec Law 25 transfer assessment | Org | Deployment region and any sub-processor are operator choices. |
| 72-hour breach notification | Org | The audit trail supports investigation; notification is an institutional process. |

## 2. Authentication and LMS integration

| Requirement | Status | Evidence / limit |
|---|---|---|
| SAML 2.0 SSO | Yes | `app/services/saml_auth.py`, admin IdP panel, signed assertion tests. |
| OIDC SSO | Yes | `app/services/oidc.py`, PKCE, nonce, JWKS, single-use state/ticket. |
| LDAP directory login | Yes | `app/services/ldap_auth.py`, role mapping from `memberOf`. |
| Canadian Access Federation (CAF) | Partial | CAF is SAML 2.0 metadata plus federation trust. The product accepts standard IdP metadata; CAF onboarding is an institutional/federation process. |
| LTI 1.3 core launch | Partial | Implemented on `release5`: platform registry, OIDC login (GET and form POST), signed `id_token` validation, single-use state, external-identity linking, and the SPA exchange. End-to-end verified against a Moodle 5.0.2 staging site; Canvas and Brightspace remain recommended. |
| LTI Advantage AGS grade passback | Partial | Implemented: private_key_jwt token exchange, line-item create/reuse, reviewed score form, result retrieval, append-only ledger. A reviewed score reached the Moodle 5.0.2 gradebook; Canvas and Brightspace remain recommended. |
| LTI NRPS roster sync | Partial | Implemented: explicit admin sync persists only subject, roles, status, and context, including the LIS 2.0 membership container. No names or email. Verified against Moodle 5.0.2; other LMSs remain recommended. |
| LTI Deep Linking | Partial | Implemented: single-use picker session, signed `LtiDeepLinkingResponse`, lab launch content items, selection limits, and deep-linked assignment routing. Verified end to end in Moodle 5.0.2; Canvas and Brightspace remain recommended. |
| Minimal LTI claims (sub, role, context) | Yes | Launch provisioning keys on `sub` + issuer. Email is used only when the LMS sends it; name is not required. NRPS persists the minimum fields. |
| Avoid standalone student passwords | Yes | SSO-provisioned accounts set `password_login_disabled` and cannot use the local form. |

`docs/LTI.md` holds the design contract and test plan. LTI has passed an
end-to-end Moodle 5.0.2 staging test; validate Canvas or Brightspace before
representing it as available on those platforms.

## 3. Accessibility and evaluation

| Requirement | Status | Evidence / limit |
|---|---|---|
| WCAG 2.1/2.2 AA on student assessment screens | Partial | Keyboard operation, landmarks, labels, focus styles, error announcements, reduced-motion, and contrast work are in place. No full external audit. |
| VPAT 2.5 / ACR | Gap | Draft structure in `docs/ACCESSIBILITY.md`; not signed. |
| Per-student time multiplier (1.5x/2x/custom) | Yes | A per-student 1.0x–3.0x multiplier scales lab session length and extension. Managed in the instructor student panel; a per-student record replaces the operator-wide setting. Quizzes have no timed limit to scale. |
| Per-student pause-the-clock breaks | Yes | The learner pauses with a required reason; the countdown freezes, the expiry is credited on resume, and the scheduler skips paused sessions. Both events are audited. |
| Individual due-date extensions across quizzes/assignments | Partial | Per-student 0–365 day extensions shift assignment due dates. Quiz deadlines are not modelled today. |
| Accommodation persists across a course | Yes | The record is attached to the user, not the course, and is read on every lab session and assignment list. |

The accommodation engine covers the user-level multiplier, due-date extension,
and pause/resume clock. Export coverage and the external AA review remain.

## 4. Automated scoring, AI, and fairness

| Requirement | Status | Evidence / limit |
|---|---|---|
| AI/LLM grading or feedback | **N/A** | No LLM SDK, API key, or inference path exists. Flags are compared with a seeded hash. |
| Zero-data-retention AI contracts | N/A / Org | The product sends no learner work to an AI provider. If an institution adds one, the contract is theirs. |
| Human-in-the-loop before LMS sync | Yes | AGS requires reviewer sign-off in the **LTI platforms** panel before a score is posted; every passback is recorded append-only. Per-course auto-sync is not enabled. |
| Immutable audit of automated scores | Partial | Flag attempts, completion records, and admin activity are logged, and every LMS passback is appended to `lti_scores` with reviewer, time, score, and LMS response. Rubric criteria and confidence are not modelled because completion is a deterministic flag match. |
| Manual grade override with audit | Partial | Instructors can review evidence; there is no formal override record with reason. |
| Student notice that automated logic evaluated them | Partial | The UI states that completion is automated, but there is no per-submission notice or "request human review" workflow. |
| Explainable primary factors | Partial | Completion criteria and workbook rubric are visible; the score is a deterministic flag match, not a weighted model. |
| Bias/validation study across writing styles | N/A | The product does not grade free text or writing. Fairness testing should target accessibility and equal access, not model bias. |
| EU AI Act high-risk classification | Org | The product does not place an AI grading system on the market. An institution embedding it in a high-risk process owns that assessment. |
| GDPR Article 22 / Quebec Law 25 automated-decision notice | Partial / Org | No solely automated high-stakes decision exists in the product. Institutions using completion as a final grade must provide the human review route. |

## 5. Certifications and assessments

| Item | Status |
|---|---|
| HECVAT Full | Draft answer pack: `docs/HECVAT.md`. Not a completed third-party assessment. |
| SOC 2 Type II | **Not held.** Requires an independent auditor over an observation period. |
| ISO 27001 | **Not held.** Requires an accredited certification body and an operating ISMS. |
| VPAT 2.5 / ACR | **Not signed.** Draft in `docs/ACCESSIBILITY.md`. |
| Third-party penetration test | Not held. Internal review: `docs/SECURITY-REVIEW-2026-11.md`. |
| Canadian cloud hosting | **Operator choice.** The product is self-hosted; the repository cannot guarantee a region. |
| Completed Quebec PIA / TRA | **Institution.** The product supplies evidence, not the assessment. |

## Release boundaries

Release 4 can honestly ship:

- SSO (OIDC/SAML/LDAP) with role mapping and IdP administration.
- The network device topology engine.
- API exposure fixes (proxy-derived client IPs, audit addresses).
- Privacy corrections for SSO export/erasure.
- Accessibility corrections to the institution sign-in panel.
- This traceability pack and the compliance dossier.

Everything below is **Release 5**, not Release 4:

- LTI 1.3 / Advantage: launch, AGS, NRPS, and Deep Linking are implemented on
  `release5` and passed a Moodle 5.0.2 staging test; Canvas and Brightspace
  validation plus CAF onboarding remain.
- Multi-tenancy and the TA role.
- Per-student accommodations: multiplier, due-date extension, and pause/resume
  are implemented; export coverage and the external AA review remain.
- Automated-decision transparency and the human-review workflow.
- HECVAT Full, VPAT 2.5, SOC 2 Type II, ISO 27001, DPA finalization, Quebec
  PIA/TRA support, Canadian hosting profile.
- Whole-institution archive export and term-end purge tooling.

See `docs/RELEASE-5-SCOPE.md`. A buyer must not be told that Release 4 includes
LTI, multi-tenancy, a signed VPAT, SOC 2, or ISO 27001.
