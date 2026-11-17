# API Security: OAuth and OIDC Abuse

**Track:** Web · **Level:** 11 · **Time:** 100 minutes · **Difficulty:** advanced

## Scenario

The API implements OAuth with a callback. Test redirect handling, recover the token, and propose the fix.

## What you will practise

- Map an OAuth authorization-code flow
- Test redirect URI validation
- Explain state, PKCE, and nonce controls
- Recommend exact redirect matching and token binding

## Work through the exercise

1. Open the exercise from the Web track, level 11.
2. Work from the scenario; use the lab hints only when you are stuck.
3. Recover the assessment token and write the evidence the exercise asks for.

## Evidence

- The assessment flag.
- A short note that names the weakness and the defensive control.

## Defensive takeaway

Server-side authorization, strict token validation, least-privilege runtime, and artifact verification remove this class of weakness.

> The target is a local, intentionally vulnerable API. Do not test a
> real host or another learner's session.
