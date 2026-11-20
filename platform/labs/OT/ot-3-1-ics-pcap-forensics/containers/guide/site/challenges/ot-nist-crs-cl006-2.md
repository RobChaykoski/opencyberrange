# NIST robotics cell — Nessus authenticated scan (CL006.2)

**Manufacturing &amp; smart factory** · **Hard** · 0.0 MB · 0 capture file(s)

> What does Nessus authenticated scan do to a live robotics work cell's control network?

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

NIST's Cybersecurity for Smart Manufacturing Systems testbed includes a collaborative-robotics work cell: robots, a PLC and an HMI exchanging Modbus/TCP, captured at the cell switch and at each station. The captures are normal operation — no attacks — recorded while NIST exercised one low-baseline security control at a time.

This scenario (CL006.2) exercises **Nessus authenticated scan**. Your job is the question OT defenders actually face: what does this security activity look like on the wire, and does it disturb the control loop?

## Objectives

- Identify the robotics hosts (PLC, HMI, stations) and the security-tooling hosts.
- Characterize the traffic Nessus authenticated scan adds to the cell.
- Measure the effect on Modbus/TCP polling (rate, gaps, retransmissions).
- Compare with the baseline scenario (CL001.1) and decide whether this control is OT-safe.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py nist-csms-robotics-crs
```

- **[NIST CSMS testbed — collaborative robotics system (21 security-control scenarios)](../DATASETS.md#nist-csms-robotics-crs)** (`nist-csms-robotics-crs`), ~24.96 GB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 4 parts (6.44 GB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/nist-csms-robotics-crs.tar.part000) (1.90 GB) · [part001](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/nist-csms-robotics-crs.tar.part001) (1.90 GB) · [part002](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/nist-csms-robotics-crs.tar.part002) (1.90 GB) · [part003](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/nist-csms-robotics-crs.tar.part003) (0.74 GB)
  - **Original source:** [s3.amazonaws.com/nist-el/mfg_trustworthysystems/ts1_cyber…](https://s3.amazonaws.com/nist-el/mfg_trustworthysystems/ts1_cybersecurity/implementation/low_baseline/crs/)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Overview with Pcapper**

The cell-switch capture (capture.pcap) sees everything; station*/plc/hmi files are per-device views.

```bash
pcapper 'data/nist-csms-robotics-crs/CL006.2-NessusAuthenticatedScan/pcaps/capture.pcap' --overview
```

**2. Who's new on the network?**

Security tools (scanners, backup/AV servers) stand out from the robotics hosts by protocol and volume.

```bash
pcapper 'data/nist-csms-robotics-crs/CL006.2-NessusAuthenticatedScan/pcaps/capture.pcap' --services --scan
```

**3. Control-loop health**

Modbus request rate per second and response-time outliers during the activity.

```bash
pcapper 'data/nist-csms-robotics-crs/CL006.2-NessusAuthenticatedScan/pcaps/capture.pcap' --modbus --control-loop
```

**4. Compare with the baseline**

```bash
pcapper 'data/nist-csms-robotics-crs/CL001.1-Baseline/' --overview  # then diff against this scenario
```

**5. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/nist-csms-robotics-crs/CL006.2-NessusAuthenticatedScan/pcaps/capture.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/nist-csms-robotics-crs/CL006.2-NessusAuthenticatedScan/pcaps/capture.pcap'
tshark -r 'data/nist-csms-robotics-crs/CL006.2-NessusAuthenticatedScan/pcaps/capture.pcap' -q -z io,phs | head -40
```

**2. Who's new on the network?**

Security tools (scanners, backup/AV servers) stand out from the robotics hosts by protocol and volume.

```bash
tshark -r 'data/nist-csms-robotics-crs/CL006.2-NessusAuthenticatedScan/pcaps/capture.pcap' -q -z conv,ip | head -25
```

**3. Control-loop health**

Modbus request rate per second and response-time outliers during the activity.

```bash
tshark -r 'data/nist-csms-robotics-crs/CL006.2-NessusAuthenticatedScan/pcaps/capture.pcap' -q -z io,stat,1,mbtcp | head -40
```

## Hints

<details><summary>Hint 1</summary>

capture.pcap is the switch view; per-device captures help attribute traffic to a host.

</details>

<details><summary>Hint 2</summary>

Scanners announce themselves: one source touching many ports/hosts in a short window.

</details>

<details><summary>Hint 3</summary>

A control is 'OT-safe' if the Modbus cycle keeps its rate and timing while it runs.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

Normal operation plus Nessus authenticated scan. Expect the security tooling's protocols (e.g. SMB/RPC for backups and AV, a burst of probes from the scanner for Nessus/Open-AudIT, syslog/LDAP/Kerberos for AD and logging) layered over steady Modbus/TCP polling; the analysis deliverable is the footprint of the control and whether the polling cycle degraded. NIST published these measurements to answer exactly that question.

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Read Discrete Inputs ×228600, Read Input Registers ×228553, Read Holding Registers ×164070, Read Coils ×8282, Write Single Coil ×632, Write Single Register ×66, 17 ×32, Device Identification (MEI) ×10; dangerous-operation matches: 708 (top sources: 192.168.0.30 ×349, 192.168.1.101 ×205, 192.168.1.3 ×56); top conversations in hmi.pcap: 192.168.0.30↔192.168.0.98 (54,020 pkts), 192.168.0.98↔192.168.1.104 (28,539 pkts), 192.168.0.98↔192.168.1.102 (28,449 pkts) (basis: 3 of 4 capture file(s), first 300,000 packets each, smallest files carrying Modbus/TCP chosen)

_Dataset credit: NIST Engineering Laboratory — Cybersecurity for Smart Manufacturing Systems (CSMS) program (2019) · License: No license stated — U.S. Government work (NIST); credit NIST._

</details>

## Dataset & credit

**NIST Engineering Laboratory — Cybersecurity for Smart Manufacturing Systems (CSMS) program (2019)** — license: No license stated — U.S. Government work (NIST); credit NIST

- [Dataset source — NIST CSMS testbed — collaborative robotics system (21 securi](https://s3.amazonaws.com/nist-el/mfg_trustworthysystems/ts1_cybersecurity/implementation/low_baseline/crs/)
- [NIST — Cybersecurity for Smart Manufacturing Systems](https://www.nist.gov/programs-projects/cybersecurity-smart-manufacturing-systems)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (4)</summary>

- `data/nist-csms-robotics-crs/CL006.2-NessusAuthenticatedScan/pcaps/capture.pcap`
- `data/nist-csms-robotics-crs/CL006.2-NessusAuthenticatedScan/pcaps/hmi.pcap`
- `data/nist-csms-robotics-crs/CL006.2-NessusAuthenticatedScan/pcaps/plc.pcap`
- `data/nist-csms-robotics-crs/CL006.2-NessusAuthenticatedScan/pcaps/station1.pcap`

</details>
