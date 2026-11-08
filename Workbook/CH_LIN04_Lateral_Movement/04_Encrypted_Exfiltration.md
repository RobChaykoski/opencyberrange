# Obsidian Analytics - Encrypted Exfiltration

!!! note "Workbook generated from the lab definition"
    This walkthrough was generated from `linux-4-4-encrypted-exfiltration/lab.yaml` and reviewed for
    structure. Verify the target name, commands, and output against the running
    lab before relying on them. Do not copy a flag from the lab definition; use
    the flag you recover in the environment.

## Before You Begin

- [ ] Launched **Obsidian Analytics - Encrypted Exfiltration** in the platform
- [ ] Opened the lab browser or terminal
- [ ] You can reach the target shown in the exercise
- [ ] Estimated time: **50 minutes** · Difficulty: **intermediate**

## Targets and Tools

- Use the target address shown in the exercise.

- No special tool list is declared; use the terminal or browser provided by the lab.

## Scenario

Obsidian Analytics, a threat intelligence firm based in Denver, has been
compromised. Your red team secured operator-level access on their primary
data processing server through a vulnerability chain documented in earlier
phases.

Now it's time for exfiltration. Your team lead, Maya Chen, wants proof of
impact: "We have access on the Obsidian box. I need you to demonstrate that
their data protection is insufficient. They've been using encoding, encryption,
and obfuscation to conceal sensitive exports - find everything. Show them that
security through obscurity doesn't cut it."

Your credentials are operator / 0bs1d14n_0ps# (with sudo access).

Three assessment markers have been hidden across the server using different
concealment techniques: base64 encoding, GPG symmetric encryption, and hex
encoding. Find and decode them all to demonstrate comprehensive exfiltration
capability.

## Your Objectives

- Locate and decode a base64-encoded export file on the compromised server
- Discover GPG decryption credentials from shell history artifacts
- Decrypt a GPG-encrypted archive to extract concealed data
- Reverse hex-encoded content from a hidden dotfile
- Assemble all three tokens into the final flag

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

**SSH as operator with sudo**

```bash
sshpass -p '{cred.operator.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.operator.user}@<target> 'sudo whoami' 2>&1
```

Expected: `root`

**Decode base64 file for token 1**

```bash
sshpass -p '{cred.operator.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.operator.user}@<target> 'base64 -d /var/backups/obsidian/export.b64 | grep -o "assessment_marker: [a-z0-9_]*" | awk "{print \$2}"' 2>&1
```

Expected: `3ncrypt`

**Read bash history for GPG password**

```bash
sshpass -p '{cred.operator.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.operator.user}@<target> 'grep passphrase /home/operator/.bash_history' 2>&1
```

Expected: `0bs1d14n_Vault#`

**Decrypt GPG file for token 2**

```bash
sshpass -p '{cred.operator.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.operator.user}@<target> 'gpg --batch --passphrase 0bs1d14n_Vault# -d /opt/obsidian/data/archive.gpg 2>/dev/null | grep -o "marker_value=[a-z0-9_]*" | cut -d= -f2' 2>&1
```

Expected: `d3c0d3`

**Decode hex file for token 3**

```bash
sshpass -p '{cred.operator.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.operator.user}@<target> 'cat /opt/obsidian/.cache/.data_store | xxd -r -p' 2>&1
```

Expected: `3xf1l`

**Verify complete flag**

```bash
echo 'OCR{...}'
```

Expected: `OCR{...}`


### Hint ladder

<details><summary>Hint 1 (unlocks after 15 minutes)</summary>

You have sudo access. Start by searching common data directories:
/var/backups, /opt, and hidden dotfiles. Look for files with unusual
extensions (.b64, .gpg) and hidden directories. The command
find / -name ".*" -type f 2>/dev/null can reveal concealed files.

</details>

<details><summary>Hint 2 (unlocks after 25 minutes)</summary>

Token 1 is in a base64-encoded file under /var/backups/obsidian/.
Token 2 is locked in a GPG-encrypted archive under /opt/obsidian/data/ -
check the operator's shell history for the decryption passphrase.
Token 3 is hex-encoded inside a hidden dotfile under /opt/obsidian/.

</details>

<details><summary>Hint 3 (unlocks after 35 minutes)</summary>

1. base64 -d /var/backups/obsidian/export.b64 and look for the assessment_marker value
2. Check ~/.bash_history for the gpg command with --passphrase, then run it
3. cat /opt/obsidian/.cache/.data_store | xxd -r -p

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
