# LTI 1.3 Advantage: design contract

Status: **Release 5 in progress.** Implemented on the `release5` branch:
platform registration (API and **Admin -> Settings -> LTI platforms**), OIDC
third-party initiated login, launch `id_token` validation, account linking
through `external_identities`, the SPA exchange, an admin JWKS test, and
migrations `0015_lti_platforms` / `0016_lti_links_scores`. AGS 2.0 has the
private_key_jwt access token, line-item creation/reuse, reviewed score payload,
result retrieval, append-only score ledger, and admin link/score endpoints; the
instructor UI remains. NRPS 2.0, Deep Linking 2.0, and a real LMS staging test
are still to do. Do not tell a buyer LTI is complete until those pass.

## Why

Universities expect launches and grade passback from Canvas, Brightspace,
Moodle, and Blackboard without a standalone student password. SSO covers
authentication; LTI covers course placement and grades.

## Required flows

### 1. OIDC third-party initiated login

- `GET/POST /api/lti/login` receives `iss`, `login_hint`, `target_link_uri`,
  `lti_deployment_id`, `client_id`.
- Resolve the registered platform by `iss` + `client_id`.
- Create a single-use state/nonce row, then redirect to the LMS authorization
  endpoint with `response_type=id_token`, `response_mode=form_post`, `scope=openid`,
  `prompt=none`, and the state/nonce.
- Reuse the SSO state pattern: database-backed, single-use, short TTL.

### 2. Launch

- `POST /api/lti/launch` accepts the form-posted `id_token` and `state`.
- Fetch the LMS JWKS, verify the signature, and validate `iss`, `aud`, `exp`,
  `iat`, `nonce`, and the deployment ID.
- Require the LTI message type `LtiResourceLinkRequest` (or
  `LtiDeepLinkingRequest`).
- Map `sub` + `iss` to `external_identities` (new provider kind `lti`) and
  provision or link the local account. Do not request email or name unless the
  institution enables it.
- Issue a one-time platform ticket and redirect to `/sso/callback`, reusing the
  existing SSO exchange.

### 3. Assignment and Grade Services (AGS 2.0)

- Obtain an access token from the LMS token endpoint with a signed
  `client_assertion` (RS256, `private_key_jwt`).
- Create or reuse a line item for the lab/quiz.
- Post a score only after the platform's review gate:
  - default: instructor review required;
  - optional per-course setting: auto-sync when the institution explicitly
    enables it.
- Record the LMS response and the local score in an append-only ledger.
- Support result retrieval for reconciliation.

### 4. Names and Role Provisioning Services (NRPS 2.0)

- Fetch the membership page only when the institution enables roster sync.
- Store the minimum: LMS `sub`, role, context ID, and section IDs.
- Never import home address, phone, or demographic fields.

### 5. Deep Linking 2.0

- Accept `LtiDeepLinkingRequest`, render the platform's lab/quiz picker, and
  return a signed `LtiDeepLinkingResponse` with the selected content item.

## Data model

- `lti_platforms`: issuer, client_id, deployment_id, auth/token/jwks endpoints,
  public key or JWKS, private key (encrypted), enabled, created_at.
- `lti_links`: platform, context, resource_link_id, local lab/quiz, line_item.
- `lti_users`: platform, subject, local user, role, last_launch.
- `lti_scores`: link, user, score, max, timestamp, reviewer, override reason,
  LMS response.

Reuse `external_identities` for the account link where possible instead of a
second identity table.

## Security and privacy

- Validate every JWT against the registered platform; never accept an unsigned
  or algorithm-confused token.
- Bind state to the platform and consume it atomically.
- Do not log `id_token` or access tokens.
- Request minimal claims; email/name are opt-in.
- Grade passback is disabled until an instructor approves, unless the
  institution sets the per-course auto-sync flag.
- Every passback is audited with the local user, score, time, and reviewer.

## Tests

1. Login redirect contains the correct state/nonce and registered client.
2. A valid launch links the LMS `sub` and issues a single-use platform ticket.
3. A replayed state or ticket is rejected.
4. A token signed by the wrong key, wrong issuer, or wrong audience is rejected.
5. A score posts only after the review gate; auto-sync is opt-in.
6. A failed LMS call leaves the local record intact and retryable.
7. NRPS sync imports no fields outside the allow-list.
8. PII: the launch payload with email/name omitted still provisions.

## Release gate

An end-to-end test against a real LMS staging tenant, with a screenshot of the
grade appearing in the LMS gradebook and a second test proving the review gate
blocks an unreviewed score.
