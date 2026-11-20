# S7comm — engineering actions (downloads, passwords, mode changes)

**Process control &amp; PLC testbeds** · **Medium** · 0.0 MB · 0 capture file(s)

> Program transfer, password requests and run/stop — the S7 operations an attacker wants and a defender must catch.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

A set of scenario-named Siemens S7comm captures (one action per file — the filenames are the labels). Program transfer, password requests and run/stop — the S7 operations an attacker wants and a defender must catch.

## Objectives

- Classify each capture by S7 function and userdata group.
- Distinguish HMI/monitoring traffic from engineering-workstation traffic.
- Identify the operations that would change the PLC.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py s7comm-scenarios-jenilv07
```

- **[ICS sample collection (jenilv-07) — S7comm scenarios, ControlLogix attack attempts, BACnet, Modbus, Omron, Tridium](../DATASETS.md#s7comm-scenarios-jenilv07)** (`s7comm-scenarios-jenilv07`), ~34.1 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/jenilv-07/ICS-pcap-files](https://github.com/jenilv-07/ICS-pcap-files)

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/s7comm-scenarios-jenilv07/comman/4-S7comm-Download-DB1-with-password-request.pcap' --overview
```

**2. Deep-dive with Pcapper (--s7)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/s7comm-scenarios-jenilv07/comman/4-S7comm-Download-DB1-with-password-request.pcap' --s7 --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/s7comm-scenarios-jenilv07/comman/4-S7comm-Download-DB1-with-password-request.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/s7comm-scenarios-jenilv07/comman/4-S7comm-Download-DB1-with-password-request.pcap'
tshark -r 'data/s7comm-scenarios-jenilv07/comman/4-S7comm-Download-DB1-with-password-request.pcap' -q -z io,phs | head -40
```

**2. Map the S7comm conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/s7comm-scenarios-jenilv07/comman/4-S7comm-Download-DB1-with-password-request.pcap' -Y s7comm -T fields -e ip.src -e ip.dst -e s7comm.header.rosctr -e s7comm.param.func -e s7comm.param.userdata.funcgroup -e s7comm.param.userdata.subfunc | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag write variable (0x05), program download (0x1A–0x1C), program upload (0x1D–0x1F — logic theft), PI-service (0x28 — start/restart/compress), PLC STOP (0x29) and security/password userdata (function group 5); SZL reads (function group 4) are device recon.

```bash
tshark -r 'data/s7comm-scenarios-jenilv07/comman/4-S7comm-Download-DB1-with-password-request.pcap' -Y 's7comm.param.func in {0x05, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 0x28, 0x29} || s7comm.param.userdata.funcgroup == 5' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

## Hints

<details><summary>Hint 1</summary>

ROSCTR 1 = job, 3 = ack-data, 7 = userdata — read the function code inside.

</details>

<details><summary>Hint 2</summary>

Program download = 0x1A/0x1B/0x1C; PLC STOP = 0x29; userdata group 5 = security/password.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

Each file demonstrates one S7 action named in its filename. Monitoring/HMI captures are dominated by Read Var (0x04) and cyclic userdata; engineering captures show download (0x1A–0x1C), upload (0x1D–0x1F), PI-service start/stop (0x28/0x29) or security (group 5) exchanges.

**Computed evidence (auto-extracted with tshark — verify it yourself):** S7comm operations — CPU services ×20, Setup Communication ×2, Request Download ×2, Download Block ×2, Download Ended ×2, PI-Service ×2; dangerous-operation matches: 10 (top sources: 192.168.178.32 ×5, 192.168.178.230 ×5); top conversations in 4-S7comm-Download-DB1-with-password-request.pcap: 192.168.178.230↔192.168.178.32 (82 pkts) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: jenilv-07 (GitHub) · License: No license stated in repo — credit the author._

</details>

## Dataset & credit

**jenilv-07 (GitHub)** — license: No license stated in repo — credit the author

- [Dataset source — ICS sample collection (jenilv-07) — S7comm scenarios, Contro](https://github.com/jenilv-07/ICS-pcap-files)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/s7comm-scenarios-jenilv07/comman/4-S7comm-Download-DB1-with-password-request.pcap`

</details>
