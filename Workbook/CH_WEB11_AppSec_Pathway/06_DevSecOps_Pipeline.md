# DevSecOps: CI/CD Pipeline Security

**Track:** Web · **Level:** 11 · **Time:** 90 minutes · **Difficulty:** intermediate

## Scenario

A CI service exposes a build artefact. Inspect it, recover the token, and recommend least-privilege workflow permissions.

## What you will practise

- Review a CI pipeline for secret exposure
- Identify over-broad workflow tokens
- Recommend secret scanning and provenance
- Write a remediation plan

## Work through the exercise

1. Open the exercise from the Web track, level 11.
2. Work from the scenario; use the lab hints only when you are stuck.
3. Recover the assessment token and write the evidence the exercise asks for.

## Evidence

- The assessment flag.
- A short note that names the weakness and the defensive control.

## Analysis Questions

**1. Which pipeline artefact exposed the secret?**

**2. Why are broad workflow token permissions dangerous?**

**3. What is the difference between secret scanning and secret rotation?**

**4. Which provenance control would you add before deployment?**

## Defensive takeaway

Server-side authorization, strict token validation, least-privilege runtime, and artifact verification remove this class of weakness.

> The target is a local, intentionally vulnerable API. Do not test a
> real host or another learner's session.
