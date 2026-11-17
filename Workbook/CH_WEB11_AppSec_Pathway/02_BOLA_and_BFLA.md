# API Security: BOLA and BFLA

**Track:** Web · **Level:** 11 · **Time:** 80 minutes · **Difficulty:** intermediate

## Scenario

The API returns user objects by id. Your account is id 1. Request another object and the admin configuration.

## What you will practise

- Explain broken object-level authorization (BOLA)
- Explain broken function-level authorization (BFLA)
- Demonstrate access to another user's object
- Recommend server-side ownership checks

## Work through the exercise

1. Open the exercise from the Web track, level 11.
2. Work from the scenario; use the lab hints only when you are stuck.
3. Recover the assessment token and write the evidence the exercise asks for.

## Evidence

- The assessment flag.
- A short note that names the weakness and the defensive control.

## Analysis Questions

**1. What is the difference between BOLA and BFLA?**

**2. Why does hiding an object identifier not fix broken object-level authorization?**

**3. Where must the ownership check run, and what should it compare?**

**4. Which log signal detects access to another user's object?**

## Defensive takeaway

Server-side authorization, strict token validation, least-privilege runtime, and artifact verification remove this class of weakness.

> The target is a local, intentionally vulnerable API. Do not test a
> real host or another learner's session.
