# Orion TechWorks - Network Discovery

!!! note "Workbook generated from the lab definition"
    This walkthrough was generated from `linux-1-7-network-discovery/lab.yaml` and reviewed for
    structure. Verify the target name, commands, and output against the running
    lab before relying on them. Do not copy a flag from the lab definition; use
    the flag you recover in the environment.

## Before You Begin

- [ ] Launched **Orion TechWorks - Network Discovery** in the platform
- [ ] Opened the lab browser or terminal
- [ ] You can reach the target shown in the exercise
- [ ] Estimated time: **30 minutes** · Difficulty: **beginner**

## Targets and Tools

- Use the target address shown in the exercise.

- No special tool list is declared; use the terminal or browser provided by the lab.

## Scenario

Orion TechWorks, a small IT managed services provider in Boise, Idaho, has
hired your firm to perform an external network assessment of one of their
servers. The engagement is limited to a single host on their DMZ.

Your point of contact, Jake Morrison (Network Administrator), provided the
IP address and a simple directive: "We want to know exactly what's exposed.
Scan it, identify every service, and tell us what an attacker could learn from
each one. We think we've only got SSH and a web server running, but honestly,
I haven't audited the box in a while."

This is your first engagement of the semester. Start with a comprehensive
port scan and work through each discovered service systematically. Three
security tokens have been placed across the services for you to find.

## Your Objectives

- Use nmap to perform TCP port scanning against a target host
- Identify all running services and their version information
- Interact with discovered services to extract information
- Discover services running on non-standard ports
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

**Port scan discovers multiple services**

```bash
nmap -sV -p 21,22,80,8888 <target> 2>&1 | grep -c open
```

Expected: `4`

**Extract token 1 from web page source**

```bash
curl -s http://<target>/ | grep -o 'Token: [a-z0-9_]*' | awk '{print $2}'
```

Expected: `sc4nn3d`

**Extract token 2 from FTP anonymous access**

```bash
curl -s --ftp-port - ftp://<target>/token.txt --connect-timeout 10 || curl -s ftp://<target>/token.txt --connect-timeout 10
```

Expected: `4n0n`

**Extract token 3 from service banner on port 8888**

```bash
timeout 3 bash -c 'cat < /dev/tcp/<target>/8888' 2>&1 | grep -o 'Token: [a-z0-9_]*' | awk '{print $2}'
```

Expected: `h1dd3n`

**Verify complete flag**

```bash
echo 'OCR{...}'
```

Expected: `OCR{...}`


### Hint ladder

<details><summary>Hint 1 (unlocks after 5 minutes)</summary>

Start with a comprehensive nmap scan. Use -sV for version detection and
scan a wide port range. The default 1000 ports may miss services on
non-standard ports. Try: nmap -sV -p 1-10000 <target_ip>

</details>

<details><summary>Hint 2 (unlocks after 12 minutes)</summary>

You should discover at least four services. For each one, interact with
it directly: curl for HTTP, ftp for FTP (try anonymous login), and
netcat (nc) for unknown services. Check page source for HTTP, download
files from FTP, and read banners on other ports.

</details>

<details><summary>Hint 3 (unlocks after 18 minutes)</summary>

Token 1 is in the HTML source of the web page (port 80) - view source.
Token 2 is in a file on the FTP server (port 21) - login as anonymous.
Token 3 is in the banner of a service on port 8888 - use: nc <ip> 8888

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
