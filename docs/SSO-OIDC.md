# OIDC single sign-on

Status: **Enterprise 3.1.0**. OIDC login is implemented. SAML and LDAP provider
settings are stored, but their login adapters are not part of 3.1.0.

This guide is for administrators configuring an OpenID Connect provider, and for
operators validating it on an HA control plane.

## How it works

1. The login page lists enabled OIDC providers.
2. The learner selects a provider.
3. The backend creates a state, nonce, and PKCE verifier and redirects to the
   IdP.
4. The IdP redirects back to the stable callback URL.
5. The backend exchanges the code, validates the ID token, links or provisions
   the local account, and creates a one-time ticket.
6. The SPA exchanges the ticket for the platform JWT and opens the dashboard.
7. On logout, the platform revokes the JWT and, when the IdP advertises an
   end-session endpoint, redirects through RP-initiated logout.

The flow state and tickets are stored in PostgreSQL, so the login can start on
one API replica and finish on another. No sticky session is required.

## Prerequisites

- The platform is served over HTTPS at a stable origin.
- `PUBLIC_BASE_URL` is set to that origin, for example
  `https://lab.example.edu`. If it is unset, the platform uses
  `https://SERVER_PUBLIC_HOST`.
- The control plane has at least two API replicas and a shared PostgreSQL
  database for HA.
- An OIDC application at the identity provider with the redirect URI below.
- Register the post-logout redirect URI if the IdP supports RP-initiated
  logout:

  ```text
  https://<public-origin>/login
  ```

- An administrator account for provider configuration. Keep a local
  break-glass administrator account.

## Configure the provider

1. Open **Admin → Settings → Identity providers**.
2. Select **Add provider**.
3. Choose **OpenID Connect**.
4. Enter:
   - **Issuer URL** — the provider issuer, without a trailing slash.
   - **Client ID** — from the IdP application.
   - **Client secret** — from the IdP application. It is encrypted and never
     returned by the API.
   - **Scopes** — normally `openid email profile`.
   - **Discovery URL** — optional. Leave blank in normal deployments; use an
     override only for split-horizon DNS or local testing.
   - **Default role** — `student` or `instructor`. Auto-provisioned admins are
     not supported.
   - **Auto-provision new users** — create a local account on first login.
   - **Auto-approve provisioned users** — skip the pending queue. Disable this
     if an administrator must approve every new SSO account.
   - **Link existing accounts by verified email** — link an existing student or
     instructor account when the IdP asserts a verified email. Admin accounts
     are never auto-linked.
5. Save the provider.
6. Copy the **Redirect URI** shown on the provider card and register it in the
   IdP application. It has this shape:

   ```text
   https://<public-origin>/api/auth/sso/oidc/<provider-id>/callback
   ```

7. Enable the provider and optionally make it the default.
8. Select **Test** to fetch the discovery document and JWKS.

If the provider is the default, the login page shows its button first.

## Logout

The platform revokes the current JWT on logout. If the JWT was issued through
SSO and the provider advertises an `end_session_endpoint`, the platform also
redirects to the IdP with:

- `id_token_hint` — the encrypted ID token stored for that session;
- `client_id`;
- `session_state`, when the IdP returned one;
- `post_logout_redirect_uri=https://<public-origin>/login`.

Register the post-logout redirect URI at the IdP. If discovery or the
end-session endpoint is unavailable, logout stays local. A local password login
for an SSO-linked account never redirects to the IdP.

## Account mapping

| IdP claim | Local field | Notes |
|---|---|---|
| `sub` | `external_identities.subject` | Stable identity key; never use email as the key |
| `email` | `users.email` | Required for auto-provisioning |
| `email_verified` | Link policy | Required for automatic linking to an existing account |
| `preferred_username` | `users.username` | Sanitized and de-duplicated |
| `given_name` / `family_name` | first/last name | Falls back to `name` |
| `name` | display name | Used when given/family names are absent |

Provider config can override the claim names with `username_claim`,
`email_claim`, and `name_claim` if an IdP uses non-standard claims.

## Provisioning policy

- New SSO accounts get `password_login_disabled=true` and a random unusable
  local password. They sign in through the IdP.
- Existing local accounts keep their password unless an administrator changes
  the flag. This preserves a local fallback.
- A verified email can link an existing **student or instructor** account.
- An **administrator** email match never auto-links. The login fails closed; an
  administrator must link the account explicitly or use a different email.
- If auto-approve is off, the account is created in the pending queue and no
  token is issued until an administrator approves it.

## Provider examples

### Microsoft Entra ID

- Create an **App registration**.
- Redirect URI: the platform callback shown above.
- Certificates & secrets: create a client secret.
- Issuer:

  ```text
  https://login.microsoftonline.com/<tenant-id>/v2.0
  ```

- Scopes: `openid email profile`.
- Ensure the app returns an email claim. If the tenant does not return
  `email_verified`, automatic linking to existing accounts will fail closed;
  new provisioning still works, and an administrator can link existing users.

### Okta

- Create an **OIDC Web Application**.
- Sign-in redirect URI: the platform callback.
- Issuer:

  ```text
  https://<org>.okta.com
  ```

- Scopes: `openid email profile`.

### Keycloak

- Create a confidential client with **Standard Flow** enabled.
- Valid redirect URI: the platform callback.
- Issuer:

  ```text
  https://<keycloak-host>/realms/<realm>
  ```

- Scopes: `openid email profile`.

### Google Workspace

- Create an OAuth 2.0 **Web application** client.
- Authorized redirect URI: the platform callback.
- Issuer: `https://accounts.google.com`.
- Scopes: `openid email profile`.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `redirect_uri_mismatch` at the IdP | Callback registered at the IdP differs from the provider card | Copy the exact Redirect URI from the provider card |
| Login returns `sso_failed` | Discovery, token exchange, signature, issuer, audience, or nonce validation failed | Use **Test**; check the backend log for the safe warning; verify the issuer and client ID |
| `Provider test failed` | Backend cannot reach the discovery or JWKS URL | Check DNS, egress, TLS trust, and the issuer URL |
| `pending_approval` | Auto-approve is off | Approve the user in Admin → Users |
| Existing user is not linked | Email is not verified or linking is disabled | Verify the IdP email claim or link the account explicitly |
| Administrator cannot sign in with SSO | Admin emails are never auto-linked | Use the local break-glass admin or link explicitly |
| Local password login fails for an SSO user | `password_login_disabled` is set | Use the IdP, or change the flag with an administrator decision |
| Login works on one replica only | State is not in the shared database or the replicas use different public URLs | Check the database connection and `PUBLIC_BASE_URL` on every replica |
| `state` expired or already used | The login took longer than the state TTL, or the callback was replayed | Start the login again; do not reuse a callback URL |
| Logout stays on the platform | The IdP does not advertise `end_session_endpoint`, or the post-logout redirect URI is not registered | Register `https://<public-origin>/login`; local logout still succeeds |
| IdP shows its own error after logout | The post-logout redirect URI is missing or mismatched | Add the exact `/login` URL to the IdP client |

## HA and security notes

- The callback URL is stable and derived from the public origin, not from the
  request `Host` header.
- Flow state and tickets are one-use database rows. A replay is rejected.
- JWT secrets, client secrets, authorization codes, and PKCE verifiers are not
  logged.
- Use HTTPS for the platform and the IdP. `SSO_ALLOW_INSECURE_HTTP` exists only
  for local test deployments and must stay off in production.
- Logout revokes the platform JWT. When the IdP supports it, the platform also
  performs RP-initiated logout with the stored ID token. The stored ID token is
  encrypted and deleted after the logout URL is built.
- Keep a local break-glass administrator account. Do not link it to the IdP.

## Local validation

A local mock OIDC provider can be used to validate the flow without an external
IdP. Set `SSO_ALLOW_INSECURE_HTTP=true` only in the local harness, use an HTTP
issuer, and register the platform callback. The 3.1 test suite covers:

- login start, callback, ticket exchange, and replay rejection;
- provisioning, verified-email linking, unverified-email refusal, and admin
  refusal;
- pending approval;
- state expiry;
- a callback completed on a second API replica;
- provider discovery/JWKS testing.
