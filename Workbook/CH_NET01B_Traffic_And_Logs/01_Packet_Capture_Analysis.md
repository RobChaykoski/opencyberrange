# Avalon Biotech - Suspicious Traffic Analysis

!!! note "Workbook generated from the lab definition"
    This walkthrough was generated from `network-1-1-packet-capture-analysis/lab.yaml` and reviewed for
    structure. Verify the target name, commands, and output against the running
    lab before relying on them. Do not copy a flag from the lab definition; use
    the flag you recover in the environment.

## Before You Begin

- [ ] Launched **Avalon Biotech - Suspicious Traffic Analysis** in the platform
- [ ] Opened the lab browser or terminal
- [ ] You can reach the target shown in the exercise
- [ ] Estimated time: **60 minutes** · Difficulty: **intermediate**

## Targets and Tools

- Use the target address shown in the exercise.

- No special tool list is declared; use the terminal or browser provided by the lab.

## Scenario

Avalon Biotech, a pharmaceutical research company in San Diego, California, has
flagged suspicious network activity on their internal network. Their SIEM
triggered alerts for unusual outbound connections from a workstation in the R&D
department (10.20.1.105) to multiple external IP addresses over the past 48 hours.

The incident response team captured a 5-minute segment of the workstation's
network traffic before the employee (Mark Sullivan, Research Associate) was
informed. The capture has been placed on an analysis workstation for your review.

Dr. Priya Sharma (CISO) needs your analysis ASAP: "We need to know exactly what
happened. What data was accessed? What credentials were used? How was the data
moved out? If Mark is exfiltrating our proprietary drug trial data, we need
evidence for legal. Pull everything you can from that capture."

The evidence capture is at /home/analyst/evidence/capture.pcap. Three indicators
of compromise have been flagged by automated tools - extract each IOC marker to
complete the analysis.

**Credentials**

- Analysis Workstation SSH: `analyst` / `Av4l0n_S0C#`

## Your Objectives

- Analyze a network packet capture using command-line tools (tcpdump, tshark)
- Identify suspicious HTTP traffic and extract leaked credentials from POST requests
- Reconstruct FTP sessions to discover data exfiltration activity
- Detect DNS-based data exfiltration techniques
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

**Extract IOC 1 from HTTP POST body**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'tcpdump -r /home/analyst/evidence/capture.pcap -A 2>/dev/null | grep -o "token=[a-z0-9_]*" | sed "s/^token=//" | head -1' 2>&1
```

Expected: `p4ck3t`

**Extract IOC 2 from FTP PASS command**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'tcpdump -r /home/analyst/evidence/capture.pcap -A 2>/dev/null | grep -o "PASS [a-z0-9_]*" | sed "s/^PASS //" | head -1' 2>&1
```

Expected: `4n4lyz3`

**Extract IOC 3 from DNS exfiltration query**

```bash
sshpass -p '{cred.analyst.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.analyst.user}@<target> 'tcpdump -r /home/analyst/evidence/capture.pcap -n port 53 2>/dev/null | grep -o "token_[a-z0-9]*\.data\.evil-c2\.net" | head -1 | sed "s/token_//;s/\..*//"' 2>&1
```

Expected: `3xf1l`

**Assemble and verify complete flag**

```bash
echo 'OCR{...}'
```

Expected: `OCR{...}`


### Hint ladder

<details><summary>Hint 1 (unlocks after 10 minutes)</summary>

Start by getting an overview of the capture. How many packets are there?
What protocols are used? Who is the workstation (10.20.1.105) talking to?
Try: tcpdump -r capture.pcap -n | head -50
Or: tshark -r capture.pcap -q -z conv,ip

</details>

<details><summary>Hint 2 (unlocks after 20 minutes)</summary>

There are three types of suspicious outbound traffic from 10.20.1.105:
1. HTTP POST to an external IP (198.51.100.47) - look at the POST body
2. FTP session to another external IP (203.0.113.22) - check the PASS command
3. DNS TXT queries to a suspicious domain - the subdomain is the IOC
Filter by protocol: tshark -r capture.pcap -Y "http" or "ftp" or "dns.qry.type==16"

</details>

<details><summary>Hint 3 (unlocks after 30 minutes)</summary>

Extract the three IOC markers:
1. HTTP POST body contains token=p4ck3t:
   tshark -r capture.pcap -Y "http.request.method==POST" -T fields -e http.file_data
   Or: tcpdump -r capture.pcap -A port 80 | grep token=
2. FTP PASS command contains the second marker:
   tshark -r capture.pcap -Y "ftp.request.command==PASS" -T fields -e ftp.request.arg
   Or: tcpdump -r capture.pcap -A port 21 | grep PASS
3. DNS TXT query subdomain is the third marker:
   tshark -r capture.pcap -Y "dns.qry.type==16" -T fields -e dns.qry.name
   Look for the query prefixed with "token_" in evil-c2.net. The value after "token_" is the IOC.

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
