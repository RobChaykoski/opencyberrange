# Aegis Security Corp - Brute Force Detection

!!! note "Workbook generated from the lab definition"
    This walkthrough was generated from `linux-5-6-brute-force-detection/lab.yaml` and reviewed for
    structure. Verify the target name, commands, and output against the running
    lab before relying on them. Do not copy a flag from the lab definition; use
    the flag you recover in the environment.

## Before You Begin

- [ ] Launched **Aegis Security Corp - Brute Force Detection** in the platform
- [ ] Opened the lab browser or terminal
- [ ] You can reach the target shown in the exercise
- [ ] Estimated time: **75 minutes** · Difficulty: **intermediate**

## Targets and Tools

- Use the target address shown in the exercise.

- No special tool list is declared; use the terminal or browser provided by the lab.

## Scenario

Aegis Security Corp, a managed security services provider headquartered in Denver,
Colorado, has observed a sustained brute-force attack against their client-facing
authentication portal. The Security Operations Center detected a high volume of
HTTP POST requests to the login endpoint originating from a single source, with
hundreds of different username/password combinations attempted over a short period.

You're an analyst on the incident response team. Your team lead, Sarah Nguyen
(Principal Threat Analyst), sent you this message: "We have an active credential
stuffing campaign hitting our auth gateway. The IDS sensor is deployed inline but
has no custom rules - it's not catching anything. I need you to write Suricata
detection rules for the brute-force POST traffic, find the campaign identifier
the attacker is using (they embed tracking tags in their payloads), and check the
web portal logs - I suspect the same actor is hitting that too with a custom tool.
Pull every IOC you can find. Brief me by end of shift."

Your toolkit: SSH access to the IDS sensor (Suricata + tcpdump) and the corporate
web portal. The brute-force attack is ongoing - new login attempts arrive every
few seconds. Work fast.

**Credentials**

- IDS Sensor SSH: `analyst` / `A3g1s_S0C_2024#`
- Web Server SSH: `webadmin` / `A3g1s_Adm1n#`

## Your Objectives

- Observe live brute-force HTTP POST login attempts on the IDS sensor
- Identify the attack pattern (repeated failed logins with different credentials)
- Write custom Suricata rules to detect brute-force POST requests containing password fields
- Write a Suricata rule to detect the successful login attempt with a campaign marker
- Extract indicators of compromise from Suricata alert payloads
- Investigate the target web server's nginx access log for attacker tool signatures
- Assemble the flag from three extracted tokens

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

**Verify analyst SSH access to IDS sensor**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'echo connected' 2>&1
```

Expected: `connected`

**Verify Suricata is running on IDS sensor**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'pgrep -x Suricata-Main > /dev/null && echo suricata_running' 2>&1
```

Expected: `suricata_running`

**Observe brute-force attack traffic arriving on the IDS sensor**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'sudo timeout 25 tcpdump -i eth0 -A -c 5 port 80 2>/dev/null | grep -ci post | awk "{print (\$1>=1)?\"traffic_detected\":\"none\"}"' 2>&1
```

Expected: `traffic_detected`

**Write Suricata rules for brute-force POST detection and campaign marker**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'printf "alert http any any -> any any (msg:\"Brute Force Login Attempt\"; flow:to_server,established; content:\"POST\"; http_method; content:\"password\"; http_client_body; sid:1000001; rev:1;)\nalert http any any -> any any (msg:\"Campaign Marker Detected\"; flow:to_server,established; content:\"POST\"; http_method; content:\"campaign=brut3\"; http_client_body; sid:1000002; rev:1;)\n" > /etc/suricata/rules/local.rules && sudo kill -USR2 $(pgrep -x Suricata-Main) && echo rules_deployed' 2>&1
```

Expected: `rules_deployed`

**Wait for attack cycle and verify Suricata alerts fire**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'sleep 20 && jq -r "select(.alert) | .alert.signature" /var/log/suricata/eve.json 2>/dev/null | sort -u' 2>&1
```

Expected: `Detected`

**Extract token 1 from campaign marker alert payload (campaign parameter)**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'jq -r "select(.alert) | select(.alert.signature_id == 1000002) | .payload_printable" /var/log/suricata/eve.json 2>/dev/null | grep -o "campaign=[^& ]*" | head -1 | cut -d= -f2' 2>&1
```

Expected: `brut3`

**Extract token 2 from brute-force alert payload (exfil parameter)**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'jq -r "select(.alert) | select(.alert.signature_id == 1000001) | .payload_printable" /var/log/suricata/eve.json 2>/dev/null | grep -o "exfil=[^& ]*" | head -1 | cut -d= -f2' 2>&1
```

Expected: `d3t3ct`

**SSH to target and extract attacker User-Agent from nginx access log**

```bash
sshpass -p '{cred.webadmin.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.webadmin.user}@<target> 'grep -o "AegisCracker/[a-zA-Z0-9_]*" /var/log/nginx/access.log | head -1 | cut -d/ -f2' 2>&1
```

Expected: `bl0ck`

**Assemble and verify complete flag**

```bash
echo 'OCR{...}'
```

Expected: `OCR{`


### Hint ladder

<details><summary>Hint 1 (unlocks after 15 minutes)</summary>

Start on the IDS sensor. Use tcpdump to observe traffic on port 80 - you
should see HTTP POST requests arriving every few seconds targeting the /login
endpoint. Look at the request bodies - the attacker is sending different
username/password combinations. Note that most responses contain "login_failed"
while some contain "login_success". Identify the patterns before writing rules.

</details>

<details><summary>Hint 2 (unlocks after 25 minutes)</summary>

The attacker sends HTTP POST login attempts to the IDS sensor every 3 seconds.
Write Suricata rules in /etc/suricata/rules/local.rules on the sensor:
- Rule 1: Detect POST requests with "password" in the body (brute-force attempts)
- Rule 2: Detect POST requests with "campaign=brut3" in the body (the successful login marker)
After writing rules, reload Suricata with:
sudo kill -USR2 $(pgrep -x Suricata-Main)

</details>

<details><summary>Hint 3 (unlocks after 35 minutes)</summary>

Example Suricata rules:
alert http any any -> any any (msg:"Brute Force Login Attempt"; flow:to_server,established; content:"POST"; http_method; content:"password"; http_client_body; sid:1000001; rev:1;)
alert http any any -> any any (msg:"Campaign Marker Detected"; flow:to_server,established; content:"POST"; http_method; content:"campaign=brut3"; http_client_body; sid:1000002; rev:1;)

After reloading, wait 15-20 seconds for the next attack cycle. Then check:
jq 'select(.alert)' /var/log/suricata/eve.json

Token 1 (brut3) is in the campaign parameter of the successful login payload.
Token 2 (d3t3ct) is in the exfil parameter of the failed login payloads.
For token 3, SSH to the target web portal and examine the nginx access log -
the attacker's User-Agent string contains the final IOC.

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
