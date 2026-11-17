# API Security: GraphQL

**Track:** Web · **Level:** 11 · **Time:** 90 minutes · **Difficulty:** intermediate

## Scenario

The API exposes GraphQL with introspection enabled. Recover the schema, find the debug field, and read the token.

## What you will practise

- Use GraphQL introspection to recover a schema
- Identify sensitive fields and missing field-level authorization
- Test query depth and cost limits
- Recommend introspection and query controls

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
