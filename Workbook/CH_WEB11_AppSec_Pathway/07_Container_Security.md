# DevSecOps: Container Security

**Track:** Web · **Level:** 11 · **Time:** 90 minutes · **Difficulty:** intermediate

## Scenario

The service runs as root with a broad profile. Inspect /api/runtime, recover the token, and propose a hardened Dockerfile and compose profile.

## What you will practise

- Review a container for root and privilege issues
- Identify missing capability drops and read-only filesystems
- Recommend a minimal runtime profile
- Verify the fix

## Work through the exercise

1. Open the exercise from the Web track, level 11.
2. Work from the scenario; use the lab hints only when you are stuck.
3. Recover the assessment token and write the evidence the exercise asks for.

## Evidence

- The assessment flag.
- A short note that names the weakness and the defensive control.

## Analysis Questions

**1. Why does running as root increase the impact of a container compromise?**

**2. Which runtime controls form a minimal container profile?**

**3. How do you verify the hardened profile actually took effect?**

**4. Which alert detects a privileged container or host mount?**

## Defensive takeaway

Server-side authorization, strict token validation, least-privilege runtime, and artifact verification remove this class of weakness.

> The target is a local, intentionally vulnerable API. Do not test a
> real host or another learner's session.
