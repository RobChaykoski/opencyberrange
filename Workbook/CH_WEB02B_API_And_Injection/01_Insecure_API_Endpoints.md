# Metro Transit - Insecure API Endpoints

!!! note "Workbook generated from the lab definition"
    This walkthrough was generated from `web-2-2-insecure-api-endpoints/lab.yaml` and reviewed for
    structure. Verify the target name, commands, and output against the running
    lab before relying on them. Do not copy a flag from the lab definition; use
    the flag you recover in the environment.

## Before You Begin

- [ ] Launched **Metro Transit - Insecure API Endpoints** in the platform
- [ ] Opened the lab browser or terminal
- [ ] You can reach the target shown in the exercise
- [ ] Estimated time: **40 minutes** · Difficulty: **intermediate**

## Targets and Tools

- Use the target address shown in the exercise.

- No special tool list is declared; use the terminal or browser provided by the lab.

## Scenario

Metro Transit Authority (MTA) in Seattle has launched a public-facing REST
API for third-party developers to build transit apps. The API provides route
information, schedules, and real-time arrival data.

Lisa Park (Director of Digital Services) commissioned the assessment: "We
just opened the API to external developers. The public endpoints are
documented, but we also have internal admin endpoints for our ops team.
Those should require API keys. I want to make sure nobody can access the
admin stuff without proper credentials."

Your scope includes all API endpoints on the target host. Two assessment
tokens are hidden in endpoints that should not be publicly accessible.

## Your Objectives

- Enumerate API endpoints through documentation and fuzzing
- Identify broken access control vulnerabilities in REST APIs
- Access administrative endpoints that should require authentication
- Extract sensitive data from unprotected debug/admin interfaces
- Capture the flag

## Background and Approach

Read the scenario before touching the target. Identify what you control, where
that input goes, and what evidence would prove success. Work from discovery to
verification: confirm the service, collect the minimum evidence, then capture
the flag. Use the lab's target list rather than guessing an address.

## Walkthrough

1. Launch the exercise and note the target address shown by the platform.
2. Confirm the target is reachable with a simple check before running a larger
   scan or exploit.
3. Work through the objectives in order. Record the exact command and the
   relevant output for each step.
4. If a step stalls, use the hint ladder below rather than jumping to a later
   hint.
5. When you recover the flag, submit it in the **Submit Flag** form and record
   the result.

### Reference commands

These are the lab's verification commands, with the target replaced by
`<target>`. They are a check, not a substitute for understanding the objective.

**API responds on port 80**

```bash
curl -s http://<target>/api/docs | grep -ci transit
```

Expected: `success`

**Public endpoint works**

```bash
curl -s http://<target>/api/routes | grep -c route
```

Expected: `success`

**Admin endpoint accessible without auth (BOLA)**

```bash
curl -s http://<target>/api/admin/users | grep -o 'assessment_token[^a-z0-9_]*[a-z0-9_]*' | sed 's/.*[^a-z0-9_]//'
```

Expected: `4p1`

**Debug endpoint exposes config with token**

```bash
curl -s http://<target>/api/debug | grep -o 'debug_token[^a-z0-9_]*[a-z0-9_]*' | sed 's/.*[^a-z0-9_]//'
```

Expected: `br0k3n_acc3ss`

**Verify complete flag**

```bash
echo 'OCR{...}'
```

Expected: `OCR{...}`


### Hint ladder

<details><summary>Hint 1 (unlocks after 8 minutes)</summary>

Start by reading the API documentation. Visit the root URL and /api/docs.
Understand the public endpoints, then look for admin or internal endpoints
that might not be documented. Try common API paths: /api/admin, /api/debug,
/api/internal, /api/config.

</details>

<details><summary>Hint 2 (unlocks after 18 minutes)</summary>

The /api/admin/users endpoint returns user data without requiring
authentication - that's a broken access control vulnerability (OWASP A01).
The /api/debug endpoint exposes internal configuration. Both contain tokens.

</details>

<details><summary>Hint 3 (unlocks after 24 minutes)</summary>

Token 1: curl http://<target>/api/admin/users - look for assessment_token
Token 2: curl http://<target>/api/debug - look for debug_token
Assemble: OCR{token1_token2}

</details>


## Record Your Findings

| Item | Your result |
|---|---|
| Target address |  |
| Service or path discovered |  |
| Evidence that proves the objective |  |
| Flag recovered |  |
| What you would change defensively |  |

## Analysis Questions

1. What did you control, and where did that input reach?
2. Which check was missing or weak?
3. What evidence proves the objective was met, rather than only attempted?
4. What would a defender see in logs or monitoring?
5. What is the smallest fix that would stop the same path?

## Defensive Takeaway

Validate and encode input at the server, enforce authorization on every object, and monitor unusual request patterns.

## If You Get Stuck

If the target is unreachable, confirm the lab is running and use the hostname shown in the exercise. If a command returns an unexpected error, check the port, path, and credentials before assuming the technique failed. Report a persistent technical failure to the instructor so it is not mistaken for learning difficulty.

Separate a platform problem from a learning problem:

- **Target unreachable:** check the lab status and the target address first.
- **Command error:** read the exact error; check the port, path, and credentials.
- **Technique fails:** compare your command with the reference command and the
  hint ladder.
- **Persistent failure:** report it to the instructor with the command and error.

## Key Takeaways

- You practised the objective in an isolated, fictional environment.
- The flag is evidence of completion, not a grade.
- The defensive takeaway matters as much as the offensive step.
- Keep the exact evidence so another analyst can reproduce the result.
