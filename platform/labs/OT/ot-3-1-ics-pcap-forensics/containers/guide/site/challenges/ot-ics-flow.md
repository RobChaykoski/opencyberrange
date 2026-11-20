# ICS-Flow — ICSSIM Modbus network attacks

**Process control &amp; PLC testbeds** · **Medium** · 0.0 MB · 0 capture file(s)

> An emulated Modbus ICS under simulated attack; flows and process logs are your answer key.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

An emulated Modbus ICS under simulated attack; flows and process logs are your answer key.

An emulated Modbus/TCP ICS built with ICSSIM, with simulated network attacks plus flow features and process logs.

## Objectives

- Identify devices and protocol roles.
- Characterize the traffic.
- Find and explain any attack or unusual operation.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py ics-flow-icssim
```

- **[ICS-Flow — ICSSIM Modbus attacks](../DATASETS.md#ics-flow-icssim)** (`ics-flow-icssim`), ~2.00 GB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (0.49 GB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/ics-flow-icssim.tar.part000) (0.49 GB)
  - **Original source:** [kaggle.com/datasets/alirezadehlaghi/icssim](https://www.kaggle.com/datasets/alirezadehlaghi/icssim)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/ics-flow-icssim/traffic.pcap' --overview
```

**2. Deep-dive with Pcapper (--modbus)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/ics-flow-icssim/traffic.pcap' --modbus --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/ics-flow-icssim/traffic.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/ics-flow-icssim/traffic.pcap'
tshark -r 'data/ics-flow-icssim/traffic.pcap' -q -z io,phs | head -40
```

**2. Map the Modbus/TCP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/ics-flow-icssim/traffic.pcap' -Y mbtcp -T fields -e ip.src -e ip.dst -e mbtcp.unit_id -e modbus.func_code | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag writes (FC 5/6/15/16/22/23), diagnostics (FC 8 — restart / force-listen-only), device identification (FC 43/14, recon) and Schneider UMAS (FC 90, engineering).

```bash
tshark -r 'data/ics-flow-icssim/traffic.pcap' -Y 'modbus.func_code in {5, 6, 15, 16, 22, 23, 8, 43, 90}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

## Hints

<details><summary>Hint 1</summary>

Pcapper --overview first, then the protocol analyzer.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

See the computed evidence and the dataset documentation.

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Read Holding Registers ×203776, Write Multiple Registers ×354; dangerous-operation matches: 354 (top sources: 192.168.0.23 ×177, 192.168.0.11 ×120, 192.168.0.12 ×57); top conversations in traffic.pcap: 192.168.0.11↔192.168.0.12 (132,187 pkts), 192.168.0.11↔192.168.0.21 (101,843 pkts), 192.168.0.12↔192.168.0.21 (65,208 pkts) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: Dehlaghi-Ghadim, A., et al. (Mälardalen University) (2023) · License: CC BY-NC-SA 4.0._

</details>

## Dataset & credit

**Dehlaghi-Ghadim, A., et al. (Mälardalen University) (2023)** — license: CC BY-NC-SA 4.0

- [Dataset source — ICS-Flow — ICSSIM Modbus attacks](https://www.kaggle.com/datasets/alirezadehlaghi/icssim)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/ics-flow-icssim/traffic.pcap`

</details>
