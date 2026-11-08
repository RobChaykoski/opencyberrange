# CryptoVault: Recovery Operation

!!! note "Workbook generated from the lab definition"
    This walkthrough was generated from `linux-9-2-cryptovault-recovery-operation/lab.yaml` and reviewed for
    structure. Verify the target name, commands, and output against the running
    lab before relying on them. Do not copy a flag from the lab definition; use
    the flag you recover in the environment.

## Before You Begin

- [ ] Launched **CryptoVault: Recovery Operation** in the platform
- [ ] Opened the lab browser or terminal
- [ ] You can reach the target shown in the exercise
- [ ] Estimated time: **60 minutes** · Difficulty: **intermediate**

## Targets and Tools

- Use the target address shown in the exercise.

- No special tool list is declared; use the terminal or browser provided by the lab.

## Scenario

CryptoVault Solutions is a cybersecurity consulting firm based in Austin, Texas.
A senior consultant, Marcus Webb, departed the company abruptly two weeks ago.
His laptop has been reimaged, but his encrypted backups remain on the shared
analyst workstation.

Your manager, Diana Reeves (Director of Operations), explains: "Marcus was
working on a sensitive internal audit before he left. The audit report is in
one of his encrypted backup files, but we can't access it. Our company has a
standard recovery procedure for encrypted data. The passphrase format is
documented in our internal policy. I need you to follow the recovery process,
decrypt the correct file, and retrieve the audit report."

Diana provides SSH credentials for the analyst workstation. She reminds you
that company policy dictates the passphrase construction method. You should
not need to brute force anything. "Everything you need is on that workstation."

**Credentials**

- Analyst Workstation SSH: `analyst` / `CV_4n4lyst_2024#`

## Your Objectives

- Enumerate the analyst workstation and departed employee's files
- Identify the encryption method used from shell history artifacts
- Locate and interpret the company password recovery policy
- Reconstruct the passphrase from policy format and employee records
- Decrypt the correct archive and retrieve the assessment finding
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

**SSH to workstation as analyst**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'whoami' 2>&1
```

Expected: `analyst`

**Departed employee home directory is readable**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'ls /home/mwebb/' 2>&1
```

Expected: `audit_backup.enc`

**Bash history reveals openssl encryption**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'cat /home/mwebb/.bash_history 2>/dev/null | grep openssl' 2>&1
```

Expected: `aes-256-cbc`

**Company encryption policy exists**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'cat /etc/company-policy/encryption-standard.txt' 2>&1
```

Expected: `Company_Prefix`

**Employee record contains employee ID**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'cat /home/mwebb/employee-record.txt' 2>&1
```

Expected: `EMP-4471`

**Decrypt the correct archive with reconstructed passphrase**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'openssl enc -aes-256-cbc -d -pbkdf2 -in /home/mwebb/audit_backup.enc -pass pass:CryptoVault-EMP-4471-2025 2>/dev/null' 2>&1
```

Expected: `OCR{`


### Hint ladder

<details><summary>Hint 1 (unlocks after 10 minutes)</summary>

Start by examining the departed employee's home directory. Look for
encrypted files, shell history, notes, and any personal documents.
The encryption method matters. Not all files use the same tool.

</details>

<details><summary>Hint 2 (unlocks after 18 minutes)</summary>

Check the .bash_history file in the departed employee's home directory.
It reveals that Marcus used openssl enc (not GPG) to encrypt his files.
The company's passphrase recovery policy is in /etc/company-policy/.
The passphrase follows a specific format combining company data with
employee information.

</details>

<details><summary>Hint 3 (unlocks after 25 minutes)</summary>

The passphrase format from /etc/company-policy/encryption-standard.txt is:
{Company_Prefix}-{Employee_ID}-{Year}
Marcus's employee ID is in /home/mwebb/employee-record.txt (EMP-4471).
The company prefix is CryptoVault. Assemble: CryptoVault-EMP-4471-2025
Then decrypt: openssl enc -aes-256-cbc -d -pbkdf2 -in audit_backup.enc
-out audit.txt -pass pass:CryptoVault-EMP-4471-2025

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
