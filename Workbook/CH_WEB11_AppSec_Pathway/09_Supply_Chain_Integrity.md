# DevSecOps: Supply Chain and Artifact Integrity

**Track:** Web · **Level:** 11 · **Time:** 80 minutes · **Difficulty:** intermediate

## Scenario

A registry serves an artefact without a valid signature. Inspect the SBOM, recover the token, and add the verification gate.

## What you will practise

- Read an SBOM and identify components
- Verify an artifact signature and provenance
- Identify an unsigned or substituted artefact
- Recommend signing and verification gates

## Work through the exercise

1. Open the exercise from the Web track, level 11.
2. Work from the scenario; use the lab hints only when you are stuck.
3. Recover the assessment token and write the evidence the exercise asks for.

## Evidence

- The assessment flag.
- A short note that names the weakness and the defensive control.

## Analysis Questions

**1. What does an SBOM prove, and what does it not prove?**

**2. Why is a hash comparison insufficient without a trusted signature?**

**3. Where should signature verification run in the pipeline?**

**4. Which response step is required after a substituted artefact is found?**

## Defensive takeaway

Server-side authorization, strict token validation, least-privilege runtime, and artifact verification remove this class of weakness.

> The target is a local, intentionally vulnerable API. Do not test a
> real host or another learner's session.
