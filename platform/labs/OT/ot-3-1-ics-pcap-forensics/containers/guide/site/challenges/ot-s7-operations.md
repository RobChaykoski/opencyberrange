# S7comm — HMI monitoring vs. normal operations

**Process control &amp; PLC testbeds** · **Easy** · 0.0 MB · 0 capture file(s)

> Variable-service reads, cyclic data and VAT monitoring: what normal S7 operations look like.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

A set of scenario-named Siemens S7comm captures (one action per file — the filenames are the labels). Variable-service reads, cyclic data and VAT monitoring: what normal S7 operations look like.

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
pcapper 'data/s7comm-scenarios-jenilv07/comman/1-S7comm-VarService-Read-DB1DBD0.pcap' --overview
```

**2. Deep-dive with Pcapper (--s7)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/s7comm-scenarios-jenilv07/comman/1-S7comm-VarService-Read-DB1DBD0.pcap' --s7 --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/s7comm-scenarios-jenilv07/comman/1-S7comm-VarService-Read-DB1DBD0.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/s7comm-scenarios-jenilv07/comman/1-S7comm-VarService-Read-DB1DBD0.pcap'
tshark -r 'data/s7comm-scenarios-jenilv07/comman/1-S7comm-VarService-Read-DB1DBD0.pcap' -q -z io,phs | head -40
```

**2. Map the S7comm conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/s7comm-scenarios-jenilv07/comman/1-S7comm-VarService-Read-DB1DBD0.pcap' -Y s7comm -T fields -e ip.src -e ip.dst -e s7comm.header.rosctr -e s7comm.param.func -e s7comm.param.userdata.funcgroup -e s7comm.param.userdata.subfunc | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag write variable (0x05), program download (0x1A–0x1C), program upload (0x1D–0x1F — logic theft), PI-service (0x28 — start/restart/compress), PLC STOP (0x29) and security/password userdata (function group 5); SZL reads (function group 4) are device recon.

```bash
tshark -r 'data/s7comm-scenarios-jenilv07/comman/1-S7comm-VarService-Read-DB1DBD0.pcap' -Y 's7comm.param.func in {0x05, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 0x28, 0x29} || s7comm.param.userdata.funcgroup == 5' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
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

**Computed evidence (auto-extracted with tshark — verify it yourself):** S7comm operations — Read Var ×201, CPU services ×25, Setup Communication ×6; dangerous-operation matches: 0 for the S7comm filter (232 S7comm packets present, so the zero is real); top conversations in 1-S7comm-VarService-Read-DB1DBD0.pcap: 192.168.1.11↔192.168.1.180 (38 pkts) (basis: 3 of 3 capture file(s), first 300,000 packets each)

_Dataset credit: jenilv-07 (GitHub) · License: No license stated in repo — credit the author._

</details>

## Dataset & credit

**jenilv-07 (GitHub)** — license: No license stated in repo — credit the author

- [Dataset source — ICS sample collection (jenilv-07) — S7comm scenarios, Contro](https://github.com/jenilv-07/ICS-pcap-files)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (3)</summary>

- `data/s7comm-scenarios-jenilv07/comman/1-S7comm-VarService-Read-DB1DBD0.pcap`
- `data/s7comm-scenarios-jenilv07/comman/2-S7comm-VarService-CyclicData-1s.pcap`
- `data/s7comm-scenarios-jenilv07/comman/3-S7comm-VAT_MB100_MW200_MD300_M400-0.pcap`

</details>
