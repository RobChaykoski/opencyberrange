# NIST process-control testbed — Active Directory with least privilege

**Process control &amp; PLC testbeds** · **Medium** · 0.0 MB · 0 capture file(s)

> A chemical-process control network (EtherNet/IP-CIP) during Active Directory domain services with least-privilege accounts.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

NIST's process-control testbed runs a Tennessee-Eastman-style chemical process with PLCs and HMIs talking EtherNet/IP-CIP, plus DCE-RPC from the Windows side. NIST recorded one run per low-baseline security control; this run is Active Directory domain services with least-privilege accounts. A process-simulation log (*_simlog.dat) sits next to the capture.

Characterize the control network, measure the footprint of this run's control on it, and decide whether the control is safe for the process.

## Objectives

- Inventory the controllers, HMIs and servers.
- Characterize the EtherNet/IP-CIP exchanges (implicit I/O vs. explicit messaging).
- For the scan run: identify the scanner, what it probed, and any disturbance to CIP traffic.
- Relate anomalies to the process log.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py nist-csms-process-control-pcs
```

- **[NIST CSMS testbed — process control system (baseline vs. Nessus scan)](../DATASETS.md#nist-csms-process-control-pcs)** (`nist-csms-process-control-pcs`), ~87.54 GB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 4 parts (5.79 GB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/nist-csms-process-control-pcs.tar.part000) (1.90 GB) · [part001](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/nist-csms-process-control-pcs.tar.part001) (1.90 GB) · [part002](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/nist-csms-process-control-pcs.tar.part002) (1.90 GB) · [part003](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/nist-csms-process-control-pcs.tar.part003) (85.8 MB)
  - **Original source:** [s3.amazonaws.com/nist-el/mfg_trustworthysystems/ts1_cyber…](https://s3.amazonaws.com/nist-el/mfg_trustworthysystems/ts1_cybersecurity/implementation/low_baseline/pcs/)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/nist-csms-process-control-pcs/PL002.1-activedirectory_leastPrivilege/capture.pcap.part000.pcap' --overview
```

**2. Deep-dive with Pcapper (--enip --cip --pccc)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/nist-csms-process-control-pcs/PL002.1-activedirectory_leastPrivilege/capture.pcap.part000.pcap' --enip --cip --pccc --ot-commands
```

**3. Footprint of this run's control**

New hosts, services and conversations that the baseline run doesn't have.

```bash
pcapper 'data/nist-csms-process-control-pcs/PL002.1-activedirectory_leastPrivilege/capture.pcap.part000.pcap' --scan --services
```

**4. Compare with the baseline run**

```bash
pcapper 'data/nist-csms-process-control-pcs/PL001.1-baseline/' --overview
```

**5. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/nist-csms-process-control-pcs/PL002.1-activedirectory_leastPrivilege/capture.pcap.part000.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/nist-csms-process-control-pcs/PL002.1-activedirectory_leastPrivilege/capture.pcap.part000.pcap'
tshark -r 'data/nist-csms-process-control-pcs/PL002.1-activedirectory_leastPrivilege/capture.pcap.part000.pcap' -q -z io,phs | head -40
```

**2. Map the EtherNet/IP &amp; CIP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/nist-csms-process-control-pcs/PL002.1-activedirectory_leastPrivilege/capture.pcap.part000.pcap' -Y enip -T fields -e ip.src -e ip.dst -e enip.command -e cip.sc | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag CIP Reset (0x05), Start (0x06), Stop (0x07), Set Attribute Single (0x10), Execute PCCC (0x4B), Write Tag (0x4D), Write Tag Fragmented (0x53); ENIP ListIdentity (0x63) is the classic discovery broadcast.

```bash
tshark -r 'data/nist-csms-process-control-pcs/PL002.1-activedirectory_leastPrivilege/capture.pcap.part000.pcap' -Y 'cip.sc in {0x05, 0x06, 0x07, 0x10, 0x4b, 0x4d, 0x53} || enip.command == 0x63' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Footprint of this run's control**

New hosts, services and conversations that the baseline run doesn't have.

```bash
tshark -r 'data/nist-csms-process-control-pcs/PL002.1-activedirectory_leastPrivilege/capture.pcap.part000.pcap' -q -z conv,tcp | head -25
```

## Hints

<details><summary>Hint 1</summary>

The capture is large and split into parts — start with part000.

</details>

<details><summary>Hint 2</summary>

Implicit (class 1) I/O is UDP 2222; explicit messaging is TCP 44818.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

Baseline: steady CIP implicit I/O and explicit messaging between controllers and HMIs, plus Windows/DCE-RPC management traffic. Nessus run: the same plus a scanner sweeping hosts and ports (including CIP/ENIP discovery) — quantify it and check for gaps in the cyclic I/O.

**Computed evidence (auto-extracted with tshark — verify it yourself):** EtherNet/IP &amp; CIP operations — Read Tag ×267163, Get Attribute List ×27746, Write Tag ×12336, Multiple Service Packet ×1914, Read Tag Fragmented ×380, Get Attributes All ×380; dangerous-operation matches: 12336 (top sources: 172.16.4.5 ×6168, 172.16.4.102 ×6168); top conversations in capture.pcap.part003.pcap: 172.16.4.102↔172.16.4.5 (278,191 pkts), 172.16.1.5↔172.16.2.5 (5,984 pkts), 172.16.1.4↔172.16.2.5 (5,549 pkts) (basis: 3 of 4 capture file(s), first 300,000 packets each, smallest files carrying EtherNet/IP &amp; CIP chosen)

_Dataset credit: NIST Engineering Laboratory — Cybersecurity for Smart Manufacturing Systems (CSMS) program (2019) · License: No license stated — U.S. Government work (NIST); credit NIST._

</details>

## Dataset & credit

**NIST Engineering Laboratory — Cybersecurity for Smart Manufacturing Systems (CSMS) program (2019)** — license: No license stated — U.S. Government work (NIST); credit NIST

- [Dataset source — NIST CSMS testbed — process control system (baseline vs. Nes](https://s3.amazonaws.com/nist-el/mfg_trustworthysystems/ts1_cybersecurity/implementation/low_baseline/pcs/)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (4)</summary>

- `data/nist-csms-process-control-pcs/PL002.1-activedirectory_leastPrivilege/capture.pcap.part000.pcap`
- `data/nist-csms-process-control-pcs/PL002.1-activedirectory_leastPrivilege/capture.pcap.part001.pcap`
- `data/nist-csms-process-control-pcs/PL002.1-activedirectory_leastPrivilege/capture.pcap.part002.pcap`
- `data/nist-csms-process-control-pcs/PL002.1-activedirectory_leastPrivilege/capture.pcap.part003.pcap`

</details>
