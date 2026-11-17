# DevSecOps: Kubernetes Security

**Track:** Web · **Level:** 11 · **Time:** 120 minutes · **Difficulty:** advanced

## Scenario

The workload uses a broad service account. Inspect /api/k8s/secrets, recover the token, and propose RBAC and pod-security fixes.

## What you will practise

- Review service-account RBAC for least privilege
- Identify privileged pods and hostPath mounts
- Design default-deny network policy
- Recommend workload identity and admission controls

## Work through the exercise

1. Open the exercise from the Web track, level 11.
2. Work from the scenario; use the lab hints only when you are stuck.
3. Recover the assessment token and write the evidence the exercise asks for.

## Evidence

- The assessment flag.
- A short note that names the weakness and the defensive control.

## Analysis Questions

**1. Why is a broad service account a privilege-escalation path?**

**2. How do privileged pods and hostPath mounts enable a host escape?**

**3. What does a default-deny network policy change?**

**4. Which admission control would block this workload?**

## Defensive takeaway

Server-side authorization, strict token validation, least-privilege runtime, and artifact verification remove this class of weakness.

> The target is a local, intentionally vulnerable API. Do not test a
> real host or another learner's session.
