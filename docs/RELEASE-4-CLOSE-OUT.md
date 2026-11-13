# Release 4 close-out

Status: **closed.**
Date: **13 November 2026**
Tag: **`v4`** (signed annotated tag)
Release line: **Release 4** (Community / Academic, Professional, Enterprise profiles)

## Shipped

- OIDC, SAML 2.0, and LDAP/Active Directory single sign-on, with a deployment-wide
  on/off switch and a local break-glass administrator.
- Mandatory `SETUP_TOKEN` for first-run setup; the wizard cannot claim an admin
  account on a fresh install without the operator token.
- Network device topology engine and four routed labs.
- HttpOnly `wiki_session` cookie, runtime **Wiki** settings for the wiki origin,
  cookie domain, and frame ancestor, with a safe same-origin fallback.
- `safeHttpUrl` on the tool panel, question-bank, and community-event URL
  bindings, plus a CI guard that fails if those bindings regress.
- SSO privacy export/erasure, institution sign-in accessibility, API exposure
  fixes, and the Release 4 dependency pass.
- Signed supply-chain lock, refreshed runtime integrity manifest, and a signed
  `v4` tag.

## Production hotfix `v4.0.1`

The first Release 4 production build called the authenticated wiki-cookie
endpoint from the login page. Its 401 triggered the global redirect interceptor,
which reloaded `/login` and repeated the probe. The hotfix:

- skips the wiki-cookie probe when there is no token;
- excludes the probe and `/login` from the 401 redirect interceptor;
- refreshes the wiki cookie only when the app has a token.

Verified in production: `/login` renders with no console or network errors, and
a real sign-in reaches `/dashboard` without a reload loop.

## Deployments

| Environment | Status |
|---|---|
| Development `.44` | Release 4, healthy, 179 active labs |
| Production `.41` / `ctfd.swocts.com` | Release 4, healthy, 179 active labs |

Release 5 is **not** deployed to production.

## Verification

- Backend: **335 passed, 219 skipped**.
- Frontend build and lint: clean (existing warnings only).
- Lab validator: 179 labs, no errors.
- Ten randomly selected labs: validation, workbook, flag/hint/outcome, and API
  discoverability all passed.
- Live workspace regression on development: **25/25** checks, including RangeBox
  VNC, workbook frame, hints, flag error handling, theme toggle, mobile fallback,
  and Stop Exercise.
- Authenticated page pass: dashboard, exercises, Windows track, workbooks,
  courses, profile, events, certificate verification, admin users, and admin
  settings all loaded without page or console errors.
- CI, CodeQL, Trivy, Quality checks, Security delta review, OpenSSF Scorecard,
  and Dependency Graph: green.
- `v4` signature verified against release key
  `8E81B5F3FDC5F5A62B0C258791FD6FBC4ADAFDA2`.

## Known boundary

Production currently uses the same-origin wiki fallback because the only second
hostname available (`ocr.swocts.com`) is a different deployment. The wiki
settings are ready for a same-instance custom hostname; adding DNS/TLS and the
three values is a deployment change, not a code change. The JWT is not exposed
to the framed wiki: the cookie is HttpOnly and the fallback sandbox has an opaque
origin.

## Next

Release 5 work is tracked in [`RELEASE-5-SCOPE.md`](RELEASE-5-SCOPE.md):
LTI 1.3 Advantage, multi-tenancy/RBAC, accommodation, minor-account mode,
procurement artifacts, RangeBox modernization, and the frontend serving-layer
evaluation. Development starts on a `release5` branch and a local Docker stack;
production stays on Release 4.
