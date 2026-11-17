# API Security: JWT

**Track:** Web · **Level:** 11 · **Time:** 90 minutes · **Difficulty:** intermediate

## Scenario

The API accepts a debug token. Decode it, test the algorithm handling, and read the token from the debug endpoint.

## What you will practise

- Decode a JWT and inspect its claims
- Test signature validation and the alg=none weakness
- Explain issuer, audience, and expiry validation
- Recommend server-side verification and key rotation

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
