# Greystone Manufacturing - SNMP Community Strings

!!! note "Workbook generated from the lab definition"
    This walkthrough was generated from `linux-2-8-snmp-community-strings/lab.yaml` and reviewed for
    structure. Verify the target name, commands, and output against the running
    lab before relying on them. Do not copy a flag from the lab definition; use
    the flag you recover in the environment.

## Before You Begin

- [ ] Launched **Greystone Manufacturing - SNMP Community Strings** in the platform
- [ ] Opened the lab browser or terminal
- [ ] You can reach the target shown in the exercise
- [ ] Estimated time: **35 minutes** · Difficulty: **beginner**

## Targets and Tools

- Use the target address shown in the exercise.

- No special tool list is declared; use the terminal or browser provided by the lab.

## Scenario

Greystone Manufacturing operates a production facility in Pittsburgh,
Pennsylvania. Their operational technology (OT) team recently deployed a
network monitoring gateway to track equipment status across the factory
floor. The gateway runs SNMP for network management.

Your security assessment covers the gateway's SNMP exposure. Karl Weber
(OT Security Lead) is skeptical: "SNMP is just for monitoring, there's
nothing sensitive there. We use the standard community string - it's an
internal network anyway."

Prove him wrong. The SNMP service may expose more than he thinks. Three
assessment tokens have been embedded in the SNMP MIB data. Extract them
using SNMP enumeration tools.

## Your Objectives

- Discover SNMP services using UDP port scanning
- Enumerate system information using standard SNMP community strings
- Perform comprehensive SNMP walks to extract detailed system data
- Identify sensitive information exposed through SNMP MIB trees
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

**SNMP port 161 is accessible**

```bash
snmpwalk -v2c -c public -t 5 <target> 1.3.6.1.2.1.1.1.0 2>&1 | head -1
```

Expected: `Greystone`

**Extract token 1 from sysDescr**

```bash
snmpwalk -v2c -c public -t 5 <target> 1.3.6.1.2.1.1.1.0 2>&1 | grep -o 'Token: [a-z0-9_]*' | awk '{print $2}'
```

Expected: `snmp`

**Extract token 2 from sysLocation**

```bash
snmpwalk -v2c -c public -t 5 <target> 1.3.6.1.2.1.1.6.0 2>&1 | grep -o 'Token: [a-z0-9_]*' | awk '{print $2}'
```

Expected: `w4lk`

**Extract token 3 from sysContact**

```bash
snmpwalk -v2c -c public -t 5 <target> 1.3.6.1.2.1.1.4.0 2>&1 | grep -o 'Token: [a-z0-9_]*' | awk '{print $2}'
```

Expected: `c0mmun1ty`

**Verify complete flag**

```bash
echo 'OCR{...}'
```

Expected: `OCR{...}`


### Hint ladder

<details><summary>Hint 1 (unlocks after 8 minutes)</summary>

SNMP runs on UDP port 161. Standard nmap TCP scans won't find it.
Use a UDP scan: nmap -sU -p 161 <target_ip>
Then try: snmpwalk -v2c -c public <target_ip>

</details>

<details><summary>Hint 2 (unlocks after 16 minutes)</summary>

The "public" community string gives access to standard system info.
Do a full walk and examine the output carefully. Look at sysDescr,
sysContact, and sysLocation - the tokens are embedded in these fields.

</details>

<details><summary>Hint 3 (unlocks after 22 minutes)</summary>

Run: snmpwalk -v2c -c public <target_ip> system
Token 1 is in sysDescr (1.3.6.1.2.1.1.1.0)
Token 2 is in sysLocation (1.3.6.1.2.1.1.6.0)
Token 3 is in sysContact (1.3.6.1.2.1.1.4.0)
Extract the token values after "Token:" in each field.

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
