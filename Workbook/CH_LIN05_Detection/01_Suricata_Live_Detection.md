# Sentinel Defense Corp - Live IDS Detection

!!! note "Workbook generated from the lab definition"
    This walkthrough was generated from `linux-5-4-suricata-live-detection/lab.yaml` and reviewed for
    structure. Verify the target name, commands, and output against the running
    lab before relying on them. Do not copy a flag from the lab definition; use
    the flag you recover in the environment.

## Before You Begin

- [ ] Launched **Sentinel Defense Corp - Live IDS Detection** in the platform
- [ ] Opened the lab browser or terminal
- [ ] You can reach the target shown in the exercise
- [ ] Estimated time: **75 minutes** · Difficulty: **intermediate**

## Targets and Tools

- Use the target address shown in the exercise.

- No special tool list is declared; use the terminal or browser provided by the lab.

## Scenario

Sentinel Defense Corp, a boutique cybersecurity consulting firm based in Arlington,
Virginia, has detected anomalous network traffic on their DMZ segment. The Network
Operations Center flagged repeated connections from an unidentified source targeting
multiple hosts in the 10.100.x.0/24 range. Initial triage suggests automated
reconnaissance and exploitation attempts.

You're a junior SOC analyst pulling the night shift. Your supervisor, Marcus Chen
(Senior Threat Hunter), left you a voicemail before signing off: "We've got active
probing hitting the DMZ. The IDS sensor is online but we never deployed custom
detection rules - it's running blind. I need you to analyze the traffic, write
Suricata rules that catch the specific attack signatures, and pull the IOCs from
the captured payloads. Also check the web portal - I think the attacker got some
hits there. Extract everything you can. I'll review your findings in the morning."

Your toolkit: SSH access to the IDS sensor (Suricata + tcpdump) and the corporate
web portal. The attack is ongoing - new malicious requests arrive every few seconds.
The clock is ticking.

**Credentials**

- IDS Sensor SSH: `analyst` / `S3nt1n3l_S0C#`
- Web Server SSH: `webadmin` / `Dmz_Adm1n_2024#`

## Your Objectives

- Observe live attack traffic on the IDS sensor using packet capture tools
- Identify distinct attack signatures in the traffic (SQL injection, command injection)
- Write custom Suricata IDS rules to detect each attack vector
- Extract indicators of compromise from Suricata alert payloads
- Investigate the target web server's logs for additional forensic evidence
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

**Verify analyst SSH access**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'echo connected' 2>&1
```

Expected: `connected`

**Verify Suricata is running on IDS sensor**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'pgrep -x Suricata-Main > /dev/null && echo suricata_running' 2>&1
```

Expected: `suricata_running`

**Observe attack traffic arriving on the IDS sensor**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'sudo timeout 25 tcpdump -i eth0 -A -c 5 port 80 2>/dev/null | grep -ci http' 2>&1
```

Expected: `success`

**Write Suricata rules for SQLi and command injection detection**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'printf "alert http any any -> any any (msg:\"SQLi Attack Detected\"; content:\"UNION SELECT\"; nocase; http_uri; sid:1000001; rev:1;)\nalert http any any -> any any (msg:\"Command Injection Detected\"; content:\"cat /etc\"; nocase; http_client_body; sid:1000002; rev:1;)\n" > /etc/suricata/rules/local.rules && sudo kill -USR2 $(pgrep -x Suricata-Main) && echo rules_deployed' 2>&1
```

Expected: `rules_deployed`

**Wait for attack cycle and verify Suricata alerts fire**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'sleep 20 && jq -r "select(.alert) | .alert.signature" /var/log/suricata/eve.json 2>/dev/null | sort -u' 2>&1
```

Expected: `Detected`

**Extract flag part 1 from SQLi alert payload (campaign tag)**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'jq -r "select(.alert) | select(.alert.signature_id == 1000001) | .http.url" /var/log/suricata/eve.json 2>/dev/null | grep -o "campaign=[^&]*" | sed "s/^campaign=//" | head -1' 2>&1
```

Expected: `d3t3ct`

**Extract flag part 2 from CMDi alert payload (exfil tag)**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'jq -r "select(.alert) | select(.alert.signature_id == 1000002) | .payload_printable" /var/log/suricata/eve.json 2>/dev/null | grep -o "exfil=[^& ]*" | sed "s/^exfil=//" | head -1' 2>&1
```

Expected: `rul3`

**SSH to target and extract attacker User-Agent from access log**

```bash
sshpass -p '{cred.webadmin.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.webadmin.user}@<target> 'grep -o "SentinelBreaker/[a-zA-Z0-9_]*" /var/log/nginx/access.log | head -1 | cut -d/ -f2' 2>&1
```

Expected: `wr1t3r`

**Assemble and verify complete flag**

```bash
echo 'OCR{...}'
```

Expected: `OCR{...}`


### Hint ladder

<details><summary>Hint 1 (unlocks after 10 minutes)</summary>

Start on the IDS sensor. Use tcpdump to observe traffic on port 80 - you
should see HTTP requests arriving every few seconds. Look at the request
methods, URIs, and bodies. The attacker is using two different attack
techniques. Identify the patterns before writing rules.

</details>

<details><summary>Hint 2 (unlocks after 20 minutes)</summary>

The attacker sends two types of HTTP attacks to the IDS sensor: GET requests
with SQL injection in the URL query string (look for UNION SELECT), and POST
requests with command injection in the body (look for system commands like
cat /etc). Write a separate Suricata rule for each in
/etc/suricata/rules/local.rules on the analyst box, then reload with:
sudo kill -USR2 $(pgrep -x Suricata-Main)

</details>

<details><summary>Hint 3 (unlocks after 30 minutes)</summary>

Example Suricata rules:
alert http any any -> any any (msg:"SQLi Detected"; content:"UNION SELECT"; nocase; http_uri; sid:1000001; rev:1;)
alert http any any -> any any (msg:"CMDi Detected"; content:"cat /etc"; nocase; http_client_body; sid:1000002; rev:1;)

After reloading, wait 15-20 seconds for the next attack cycle. Then check:
jq 'select(.alert)' /var/log/suricata/eve.json

The payloads contain campaign and exfil tags - those are your first two flag
parts. For the third part, SSH to the target web portal and examine the nginx
access log. The attacker's User-Agent string contains the final IOC.

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
