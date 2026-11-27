# Legal and institutional readiness

Status: **checklist, not legal advice.** Review with Ontario/Canadian counsel
before a pilot or a paid deployment. Items marked "verify" have not been
confirmed against the current tree or a contract.

This page maps the risks that come with software that teaches real attack
techniques, holds student data, serves minors, and issues completion
certificates. It links the existing policy pages and names the gaps.

## Before pilots

| Area | Risk | Current state | Next step |
|---|---|---|---|
| Entity and insurance | Personal liability if an institution blames the platform for an incident | Repository and signing keys are under a personal account; no entity or insurance is recorded here | Incorporate, hold the trademark and release keys in the entity, and obtain general liability plus cyber/E&O cover |
| Acceptable use and terms | Taught techniques used outside an authorised lab | No Acceptable Use Policy or Terms of Service page exists (verify) | Add an AUP and ToS: authorised-training-only, prohibited use, account termination, and a link from registration and login |
| Minors and education privacy | Student data and under-18 learners | High School track exists; analytics excludes under-18s; `PRIVACY-NOTICE.md`, `DPA-TEMPLATE.md`, `PIA-TRA-FINDINGS.md`, `RETENTION-POLICIES.md` exist | Ask the pilot institution which regime governs (MFIPPA/FIPPA in Ontario, Law 25 in Quebec, PIPEDA federally), add a minors schedule, and confirm Canadian data residency in writing |
| Certificate wording | Certificates read as academic credentials | Certificates attest to lab completion; no explicit disclaimer is recorded here (verify) | State on every certificate and export that it is completion evidence, not a credit, diploma, or regulated credential |
| Lab content | Defamation, confusion, or unsafe artefacts | Scenarios use fictional organisations; malware samples are excluded from the repository | Keep the authoring rules: no real people in OSINT personas, no real company branding, no live malware, and a "simulated" marker in phishing artefacts |
| Contracts | Unbounded liability and unclear security duties | `DPA-TEMPLATE.md` exists; no MSA/SOW template is recorded here (verify) | Have counsel produce one pilot MSA/SOW: liability capped at fees paid, no warranty, who patches and who holds backup keys, deletion on exit, termination |

## Structural

| Area | Risk | Current state | Next step |
|---|---|---|---|
| Licence compliance | A dependency or bundled tool incompatible with the chosen licence | PolyForm Noncommercial 1.0.0 today; third-party inventory in `THIRD_PARTY_NOTICES.md`; Trivy and the supply-chain lock run in CI | Audit dependencies before any relicensing; generate an SBOM on every release; check tool and image redistribution terms (including Kali) |
| Upstream rights | Relicensing a derivative without the copyright holder's permission | `LICENSE` names Lewis Heuermann as copyright holder with a `Required Notice`; see [the permission request](UPSTREAM-LICENSE-PERMISSION-REQUEST.md) | Obtain written permission before changing the licence; until then, keep PolyForm and preserve the notice |
| Contributions | Curriculum IP disputes and unclear relicensing rights | No DCO or CLA is recorded here (verify) | Add a DCO sign-off to `CONTRIBUTING.md`; state that submitted curriculum is distributed under the project licence and that the institution retains no claim over the distributed copy |
| Breach readiness | Failure to meet breach-reporting duties | Security event store and audit logging exist (`SECURITY-EVENTS.md`, `SECURITY.md`) | Write and test a platform incident-response plan and a breach-notification decision tree; name the decision owner |
| Accessibility | AODA/WCAG expectations in Ontario procurement | `ACCESSIBILITY.md` and `ACCESSIBILITY-TEST.md` exist (verify the conformance target) | Publish a WCAG 2.1 AA conformance statement with the test evidence, rather than promising it only in a contract |

## Operating rules

- **No learner data in a federation bundle, AI prompt, or warehouse.** This is
  already a product rule; keep it in every contract exhibit.
- **Separate learning evidence from platform telemetry.**
- **No AI grading.** Instructors remain the final authority.
- **Fictional data only** in labs, workbooks, screenshots, and events.

## Sequencing

1. Entity, insurance, AUP, and ToS disclaimers.
2. Minors/privacy schedule alongside the first pilot contract.
3. Dependency and SBOM audit during any licence change.
4. Incident-response and accessibility evidence before the first institutional
   review.

## Open decisions

- Written permission from the upstream author for any relicensing
  ([request draft](UPSTREAM-LICENSE-PERMISSION-REQUEST.md)).
- Which privacy regime governs the first pilot, and whether a minors schedule or
  a separate consent model is required.
- Whether certificates need an institutional co-brand, and who signs them.
