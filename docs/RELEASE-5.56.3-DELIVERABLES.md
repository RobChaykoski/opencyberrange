# Release 5.56.3 deliverables

Release date: **2026-11-26**  
Tag: `v5.56.3`  
Base: `v5.56.2`

## Delivered

| Item | Evidence |
|---|---|
| Analytics minor exclusion | `analytics.py`; pulse/survey regression tests |
| Pseudonymous survey ids | `privacy.pseudonymous_user_id`; API no longer returns raw user id or display name |
| RBAC course-staff scope | `CourseStaff` check in `authorization.py`; role-matrix tests |
| RBAC drift report | `rbac.drift_report`; `/api/admin/security/rbac/drift`; prune test |
| Break-glass approval | default true; private permissions require approval; admin role check |
| TOTP replay guard | `mfa_last_used_step`, Alembic `0068_mfa_replay_guard` |
| Recovery-code hashing | Argon2id with legacy SHA-256 verification |
| Legacy secret migration | startup re-encryption of plaintext TOTP secrets |
| Release QA kits | release test matrix, accessibility, lab QA, first-time user test |

## Verification

- Backend pytest: 671 passed, 569 skipped.
- Alembic: single head `0068_mfa_replay_guard`.
- `lab_qa.py --static`: 0 errors, 222 labs; warnings are review items.
- Documentation map and links: pass.
- Supply-chain lock: signed and verified.

## Follow-ups

- Passkeys/WebAuthn and mandatory privileged MFA are Release 6 scope.
- Recovery-code login email notification is a follow-up; the security event exists.
- The 197 competency contracts still need subject-matter review.
