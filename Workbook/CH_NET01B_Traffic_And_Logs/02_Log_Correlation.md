# Horizon Aerospace - Log Correlation Investigation

!!! note "Workbook generated from the lab definition"
    This walkthrough was generated from `network-1-2-log-correlation/lab.yaml` and reviewed for
    structure. Verify the target name, commands, and output against the running
    lab before relying on them. Do not copy a flag from the lab definition; use
    the flag you recover in the environment.

## Before You Begin

- [ ] Launched **Horizon Aerospace - Log Correlation Investigation** in the platform
- [ ] Opened the lab browser or terminal
- [ ] You can reach the target shown in the exercise
- [ ] Estimated time: **60 minutes** · Difficulty: **intermediate**

## Targets and Tools

- Use the target address shown in the exercise.

- No special tool list is declared; use the terminal or browser provided by the lab.

## Scenario

Horizon Aerospace, a defense contractor specializing in next-generation avionics,
detected anomalous activity on their internal network during a routine SOC review.
Alerts from multiple sources - the network IDS, the SSH authentication service, and
the Apache web server - all point to a coordinated intrusion that occurred between
14:20 and 14:25 UTC on 2024-09-12.

The incident response team has collected three evidence artifacts from the affected
segment and placed them on a secure analysis workstation for your investigation:

  1. capture.pcap - network traffic from the suspicious window
  2. auth.log - SSH authentication log from the web server (10.30.1.50)
  3. access.log - Apache access log from the same web server

Your task is to correlate these sources, reconstruct the attack timeline, and
extract the three IOC markers hidden in the network traffic. The attacker's IP,
the compromised account, and the exfiltrated filename are all critical evidence,
but the flag itself is assembled from the three tokens found in the PCAP.

Chief Security Officer Rajan Mehta needs your report: "We need the full picture -
how they got in, what account they used, and what they took. Correlate everything.
The board meets tomorrow."

Evidence is at /home/analyst/evidence/. Tools are ready on the workstation.

**Credentials**

- Analysis Workstation SSH: `analyst` / `H0r1z0n_S0C#`

## Your Objectives

- Correlate timestamps between a PCAP and server log files to reconstruct an attack timeline
- Identify the attacker's IP address by cross-referencing network and host evidence
- Determine the compromised user account from authentication logs
- Trace exfiltrated data through web server access logs
- Assemble the composite flag from evidence tokens embedded across PCAP traffic

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

**SSH to analysis workstation**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'echo connected' 2>&1
```

Expected: `connected`

**Verify PCAP file exists**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'test -f /home/analyst/evidence/capture.pcap && echo pcap_found' 2>&1
```

Expected: `pcap_found`

**Extract token 1 from HTTP POST body**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'tcpdump -r /home/analyst/evidence/capture.pcap -A 2>/dev/null | grep -o "token=[a-z0-9_]*" | sed "s/^token=//" | head -1' 2>&1
```

Expected: `c0rr3l4t3`

**Extract token 2 from FTP PASS command**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'tcpdump -r /home/analyst/evidence/capture.pcap -A 2>/dev/null | grep -o "PASS [a-z0-9_]*" | sed "s/^PASS //" | head -1' 2>&1
```

Expected: `l0g`

**Extract token 3 from DNS exfiltration query**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'tcpdump -r /home/analyst/evidence/capture.pcap -n port 53 2>/dev/null | grep -o "token_[a-z0-9]*\.exfil\.evil-dns\.net" | head -1 | sed "s/token_//;s/\..*//"' 2>&1
```

Expected: `hunt`

**Assemble and verify complete flag**

```bash
echo 'OCR{...}'
```

Expected: `OCR{`


### Hint ladder

<details><summary>Hint 1 (unlocks after 15 minutes)</summary>

Start by reading the case brief, then examine each evidence file separately.
Look at auth.log for failed and successful logins - which IP stands out?
Check access.log for unusual requests - what was downloaded?
Use tcpdump or tshark to inspect the PCAP for HTTP, FTP, and DNS traffic.
Try: tcpdump -r capture.pcap -n | head -50

</details>

<details><summary>Hint 2 (unlocks after 25 minutes)</summary>

The attacker IP 10.30.1.105 appears across all three evidence sources:
- auth.log: brute-force SSH attempts then a successful login as "jenkins"
- access.log: POST /upload and GET /downloads/classified_plans.tar.gz
- capture.pcap: HTTP POST, FTP session, and DNS exfiltration queries
Focus on extracting the token values embedded in the PCAP traffic.
Filter: tcpdump -r capture.pcap -A | grep -E "token=|PASS |evil-dns"

</details>

<details><summary>Hint 3 (unlocks after 35 minutes)</summary>

Extract the three IOC tokens from the PCAP:
1. HTTP POST body has a "token=" parameter - use grep to find it
   tcpdump -r capture.pcap -A | grep -oP "token=\K[a-z0-9_]+"
2. FTP PASS command contains the second token
   tcpdump -r capture.pcap -A port 21 | grep "PASS "
3. DNS query to evil-dns.net. Look for the subdomain prefixed with "token_"
   tcpdump -r capture.pcap -n port 53 | grep token_
Assemble: OCR{token1_token2_token3}

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

Segment the network, deny unnecessary egress, and alert on scanning, credential failures, and unusual data flows.

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
