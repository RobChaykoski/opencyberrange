# Vanguard Logistics - Service Triage

!!! note "Workbook generated from the lab definition"
    This walkthrough was generated from `linux-1-8-service-triage/lab.yaml` and reviewed for
    structure. Verify the target name, commands, and output against the running
    lab before relying on them. Do not copy a flag from the lab definition; use
    the flag you recover in the environment.

## Before You Begin

- [ ] Launched **Vanguard Logistics - Service Triage** in the platform
- [ ] Opened the lab browser or terminal
- [ ] You can reach the target shown in the exercise
- [ ] Estimated time: **40 minutes** · Difficulty: **beginner**

## Targets and Tools

- Use the target address shown in the exercise.

- No special tool list is declared; use the terminal or browser provided by the lab.

## Scenario

Vanguard Logistics, a mid-size freight and warehousing company based in
Charlotte, North Carolina, has contracted your security team for a targeted
assessment of their DMZ. The engagement scope covers three hosts on the same
subnet.

Your point of contact, Dana Reeves (IT Security Manager), explains: "We
recently decommissioned several servers but left a few online as honeypots.
Only one of these three hosts is our real production server. We need you to
figure out which one it is and document every service running on it. The
decoys should look convincing but won't have any of our company branding or
real data."

Scan all three hosts, identify the genuine Vanguard Logistics server by
correlating service banners and page content, then interact with its services
to extract three security tokens. Combine them into the flag format
OCR{token1_token2_token3}.

## Your Objectives

- Scan multiple hosts to enumerate running services and versions
- Differentiate decoy hosts from real targets using banner and content analysis
- Interact with HTTP, FTP, and custom services to extract tokens
- Assemble a composite flag from three separate tokens

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

**Verify target-alpha responds**

```bash
nmap -sn <target> 2>&1 | grep -c 'Host is up'
```

Expected: `1`

**Verify target-bravo responds**

```bash
nmap -sn <target> 2>&1 | grep -c 'Host is up'
```

Expected: `1`

**Verify target-charlie responds**

```bash
nmap -sn <target> 2>&1 | grep -c 'Host is up'
```

Expected: `1`

**Target-charlie web page contains Vanguard**

```bash
curl -s http://<target>/ | grep -q 'Vanguard' && echo yes
```

Expected: `yes`

**Extract token 1 from target-charlie web page**

```bash
curl -s http://<target>/ | grep -o 'Token: [a-z0-9_]*' | awk '{print $2}'
```

Expected: `tr14g3`

**Extract token 2 from target-charlie FTP**

```bash
curl -s ftp://<target>/token.txt --connect-timeout 10
```

Expected: `r34l`

**Extract token 3 from target-charlie port 9999**

```bash
timeout 3 bash -c 'cat < /dev/tcp/<target>/9999' 2>&1 | grep -o 'Token: [a-z0-9_]*' | awk '{print $2}'
```

Expected: `t4rg3t`

**Verify complete flag**

```bash
echo 'OCR{...}'
```

Expected: `OCR{`


### Hint ladder

<details><summary>Hint 1 (unlocks after 15 minutes)</summary>

Start by scanning all three hosts with nmap -sV to compare service
banners. Look for which host has web content that mentions the company
name "Vanguard Logistics" - the decoys serve generic pages.

</details>

<details><summary>Hint 2 (unlocks after 25 minutes)</summary>

The real target runs three distinct services: a web server, an FTP
server with anonymous access, and a custom service on a high port.
Use curl for HTTP, anonymous FTP to retrieve files, and netcat for
the custom service banner.

</details>

<details><summary>Hint 3 (unlocks after 35 minutes)</summary>

Token 1 is embedded in the HTML source of the web page - look for
an HTML comment or hidden element. Token 2 is in a file accessible
via anonymous FTP. Token 3 is in the banner of a service on port 9999.

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
