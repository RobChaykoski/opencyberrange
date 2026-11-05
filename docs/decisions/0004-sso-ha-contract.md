# ADR 0004: SSO on the HA control plane

Status: **Accepted**
Date: 2026-11-05
Release: **Enterprise 3.1.0**
Related: [`../SSO-OIDC.md`](../SSO-OIDC.md), [`../V3-HA-LAB-POOL.md`](../V3-HA-LAB-POOL.md)

## Context

Enterprise needs institutional single sign-on. A login outage is more damaging
than an analytics outage: if SSO is tied to one API container, the whole
institution can lose access. The control-plane HA foundation now provides
replicated API replicas and shared PostgreSQL/Redis, so SSO can be built on a
replica-safe contract instead of retrofitted later.

The platform already stores LDAP/OIDC/SAML provider configuration and encrypted
secrets. It did not implement a login flow. The first implementation is OIDC
because it covers Entra ID, Okta, Keycloak, Google Workspace, and most modern
institutional IdPs with one protocol and standard discovery.

## Decision

### 1. OIDC authorization-code flow with PKCE

- Use authorization code + PKCE (S256), state, and nonce.
- Validate the ID token signature with the provider JWKS, plus issuer,
  audience, expiry, issued-at, and nonce.
- Do not accept unsigned tokens, `none`, or tokens without a matching nonce.
- Fetch discovery from the configured issuer, with an optional `discovery_url`
  override for split-horizon or local test deployments.

### 2. Flow state lives in PostgreSQL

- `sso_login_states` stores state, nonce, PKCE verifier, redirect URI, return
  target, and expiry.
- `sso_login_tickets` stores the one-time SPA exchange ticket.
- Both rows are consumed with an atomic conditional update, so replay is
  rejected even under concurrent requests.
- No in-process session, cache, or `/tmp` file is required. Any API replica can
  complete a callback started on another replica.

### 3. Stable callback URL

The redirect URI is derived from `PUBLIC_BASE_URL` (or
`https://SERVER_PUBLIC_HOST`), not from the incoming `Host` header:

```text
https://<public-origin>/api/auth/sso/oidc/<provider-id>/callback
```

The admin UI shows the exact URI to register at the IdP. Replicas must share the
same external origin.

### 4. One-time SPA exchange ticket

The callback never puts the platform JWT in a URL. It redirects to the SPA with
a short-lived, single-use ticket. The SPA calls `POST /api/auth/sso/exchange`,
stores the JWT in the existing localStorage flow, sets the wiki auth cookie, and
navigates to the return target. The ticket is removed on first use and expires
after 120 seconds by default.

### 5. Account provisioning and linking

- Existing `external_identities(provider_id, subject)` links are authoritative
  and stable.
- Automatic linking by email is allowed only when the IdP asserts
  `email_verified=true`.
- **Administrator accounts are never auto-linked.** An admin email match fails
  closed and requires explicit operator action.
- New users are auto-provisioned by default with role `student`; the provider can
  set `instructor`. Automatic `admin` provisioning is deliberately unsupported.
- `auto_provision` and `auto_approve` are per-provider settings.
- SSO-provisioned accounts get `password_login_disabled=true` and a random
  unusable local password. Existing local accounts keep their password unless an
  administrator changes the flag.
- The break-glass local administrator remains a separate local account and is
  not linked automatically.

### 6. Audit and observability

- Log `SSO_LOGIN_SUCCESS`, `SSO_USER_PROVISIONED`, and `SSO_ACCOUNT_LINKED` to
  the activity feed.
- Log provider create/update/default/test/delete to the admin audit log.
- Never log client secrets, ID tokens, authorization codes, or PKCE verifiers.
- Rate-limit login start, callback, and exchange.
- Provide `POST /api/identity/providers/{id}/test` for OIDC discovery and JWKS
  reachability.

### 7. Logout

- The backend revokes the platform JWT on logout.
- If the token was issued through SSO and the provider advertises an
  `end_session_endpoint`, the backend returns a `post_logout_url` with
  `id_token_hint`, `client_id`, `session_state`, and
  `post_logout_redirect_uri` set to `<frontend>/login`.
- The ID token is stored encrypted in `sso_sessions`, one row per
  user/provider, and removed after the logout URL is built.
- Register the post-logout redirect URI at the IdP.
- If discovery or the end-session endpoint is unavailable, logout falls back to
  local-only. Local password logins never redirect to the IdP.

## Consequences

- New tables: `external_identities`, `sso_login_states`, `sso_login_tickets`,
  and `sso_sessions`.
- New `users.password_login_disabled` column and startup migration.
- New config: `PUBLIC_BASE_URL`, `FRONTEND_BASE_URL`, state/ticket TTLs, HTTP
  timeout, discovery cache, and `SSO_ALLOW_INSECURE_HTTP` (development only).
- The control plane must have at least two API replicas and a shared database
  for the HA path to be meaningful.
- SAML and LDAP remain settings-only. Their adapters can follow without changing
  the state/ticket contract.
- A production deployment still needs a security review, IdP metadata/key
  rotation runbook, and a tested break-glass procedure.

## Failure modes

| Failure | Behaviour |
|---|---|
| IdP discovery unavailable | Login start returns to the login page with a generic unavailable message; local admin remains usable |
| State expired or replayed | Callback fails closed; the user starts again |
| Email not verified | No automatic link; clear failure, no account takeover |
| Admin email matches | No automatic link; operator action required |
| Auto-approve disabled | Account is created pending; no ticket is issued |
| One API replica dies | State/ticket rows are in the shared database; the other replica completes the flow |
| Database unavailable | SSO fails; this is a control-plane outage, not an SSO-specific state loss |

## Review

Review before the first production SSO deployment and at each Enterprise minor
release. Revisit SAML/LDAP, RP-initiated logout, group-to-role mapping, and
multi-tenant provider scoping in later ADRs.
