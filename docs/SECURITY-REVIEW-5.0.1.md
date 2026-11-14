# Security and compliance review — Release 5.0.1

Date: 2026-11-14. Scope: SSO/federation handlers, client-side route guards and
bundle exposure, frontend third-party licences, and IdP settings portability.
The 5.0.1 patch carries the code fixes listed here.

## SSO and federation

### Verified controls

- **SAML validation** — `strict=True`, `wantAssertionsSigned=True`, deprecated
  algorithms rejected, `InResponseTo` matched to the stored AuthnRequest ID,
  and RelayState stored server-side and consumed once (`saml_auth.py`,
  `sso.py`). Unsolicited responses are rejected because RelayState is required.
- **XML hardening** — `onelogin/saml2/xmlparser.py` parses with
  `resolve_entities=False`, `no_network=True`, `forbid_dtd=True`,
  `forbid_entities=True`, and `huge_tree=False`; signature wrapping is covered
  by python3-saml's duplicate-ID and duplicate-Reference checks.
- **LDAP** — usernames are escaped with `escape_filter_chars` before the search
  filter; the bind DN comes from the directory entry, not user input; two
  search matches are rejected; service bind is followed by a user rebind; TLS
  validates the chain and hostname; credential failures are indistinguishable
  from unknown users.
- **OIDC** — PKCE S256, server-side state/nonce/verifier, issuer/audience/
  exp/iat/sub validation, TLS verification, encrypted ID token for logout.
- **Identity policy** — SSO can only create `student` or `instructor`; an
  existing administrator email cannot be linked; administrators are never
  demoted by directory claims; local break-glass login is unaffected because
  `password_login_disabled` is set only on SSO-provisioned accounts.

### Findings fixed in 5.0.1

1. **LDAP referral chasing** — the connection now passes
   `auto_referrals=False`, so a directory-controlled referral cannot redirect
   the bind to another server.
2. **Plaintext LDAP** — `ldap://` without StartTLS is rejected unless the
   provider explicitly sets `allow_plaintext` for an isolated lab network.
3. **OIDC signing algorithms** — the discovery document is provider-controlled,
   so its algorithm list is filtered through an asymmetric allowlist (RS/ES/PS/
   EdDSA). A provider that only advertises `HS*` or `none` now fails closed.
4. **Post-login redirect** — `return_to` rejects backslashes and control
   characters in both the backend and `SsoCallback.vue`; `/\host` no longer
   passes as a site path.
5. **Nonce comparison** — uses `hmac.compare_digest`.

Regression tests: `tests/test_sso_hardening.py`.

### Residual notes

- `wantMessagesSigned=False` is acceptable because assertions must be signed.
  An IdP that signs only the response will fail closed.
- Directory role sync is fail-closed: if an instructor's group claim is absent,
  the account falls back to `default_role`. Document this for IdP operators.
- Production had no identity providers configured at review time, so none of
  these findings were live exposure.

## Client-side route guards and bundle exposure

- Guards cover authentication, instructor/admin roles, and module access, and
  redirect to `/dashboard` or `/login` on failure (`router/index.js:238-291`).
  Role data comes from `localStorage`, so the guard is a UX boundary only.
- Backend enforcement is present where it matters: admin and LTI administration
  use `get_current_admin_user`; reports use `get_current_instructor_user`;
  reviews and accommodations check the course manager; module API paths return
  404 when the module is disabled (`main.py:947-966`); entitlement limits are
  enforced for privileged accounts and active courses.
- Every view is a dynamic import. `dist/index.html` preloads only the entry,
  Vue runtime, and shared helpers. `Admin`, `InstructorPanel`, `Reports`, and
  dashboard chunks are separate files and are not preloaded from the login page.
- The entry chunk contains route names and dynamic-import strings, not admin
  schemas or credentials. No `retention_*`, `review_requests`, `lti_platforms`,
  `client_secret`, or `JWT_SECRET` strings appear in the entry bundle. The only
  build-time variable is `VITE_WIKI_BASE_URL`, which is a public origin.
- Static chunks remain downloadable by anyone, which is inherent to an SPA; the
  protection for their data is the API authorization above.
- **Observation:** no route declares `meta.module`, so the guard's module branch
  is currently dead code. Disabled modules are still blocked by the backend
  middleware and hidden by feature flags in the admin/instructor/profile views.
  Either remove the branch or add `meta.module` when a module contributes routes.

## Frontend licence compliance

Scanned the installed tree (188 packages) and compared it with
`THIRD_PARTY_NOTICES.md`:

- MIT 150, Apache-2.0 15, BSD-2-Clause 8, ISC 7, MPL-2.0 3, BlueOak-1.0.0 2,
  BSD-3-Clause 2, MPL-2.0/Apache-2.0 dual 1.
- **No GPL, AGPL, SSPL, Commons Clause, CC-BY-SA, or unlicensed packages.**
- All runtime dependencies are named in the notices table. MPL obligations for
  `@novnc/novnc` are recorded; `dompurify` uses its Apache-2.0 option.
- `@eslint/js`, `@vitejs/plugin-vue`, `eslint-plugin-vue`, and `globals` are
  development-only and are covered by the notices' dev-tooling paragraph rather
  than one row each. No action.

## IdP settings import/export (implemented in 5.1)

`GET /api/identity/providers/export` returns a versioned bundle of provider
metadata and non-secret config with `secrets_exported: false`; secret values are
never serialized. `POST /api/identity/providers/import` accepts the bundle,
defaults to a dry run, skips existing names unless `update_existing` is set, and
forces a provider disabled when its required secrets are absent. Provided
secrets are encrypted at rest using the same path as the create/update API, and
imports are audited. The admin Identity providers panel has Export and Import
actions.

Operators still re-enter secrets after a cross-environment import; the UI states
this explicitly. The bundle is admin-only and should be handled as sensitive
infrastructure configuration even though it contains no secrets.
