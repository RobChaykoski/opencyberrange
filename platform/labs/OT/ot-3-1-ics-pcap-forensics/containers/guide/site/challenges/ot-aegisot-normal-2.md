# AegisOT — normal operations (Normal Set2)

**Process control &amp; PLC testbeds** · **Medium** · 0.0 MB · 0 capture file(s)

> Baseline a containerised Modbus plant before you hunt in it.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

AegisOT is a containerised OT testbed — HMIs and PLCs speaking Modbus/TCP over a simulated physical process, with each attack mapped to one ATT&amp;CK for ICS technique. This capture is attack-free: learn the hosts, roles, function codes, registers and cadence. Every AegisOT technique challenge is measured against it.

## Objectives

- Identify every host and its role (HMI, PLC, engineering, other).
- Profile the Modbus operations per master→slave pair.
- Note the normal timing and which registers are written, by whom.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py aegisot-ics-attacks
```

- **[AegisOT — Modbus OT testbed with 11 ATT&amp;CK-for-ICS techniques](../DATASETS.md#aegisot-ics-attacks)** (`aegisot-ics-attacks`), ~3.13 GB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (0.56 GB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/aegisot-ics-attacks.tar.part000) (0.56 GB)
  - **Original source:** [kaggle.com/datasets/khadijadrira/industrial-cybersecurity…](https://www.kaggle.com/datasets/khadijadrira/industrial-cybersecurity-repository)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/aegisot-ics-attacks/ICS_Dataset/Normal_Data/Normal_Set2/Network_Level/Merged_Packet/output_normal_2.pcap' --overview
```

**2. Deep-dive with Pcapper (--modbus)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/aegisot-ics-attacks/ICS_Dataset/Normal_Data/Normal_Set2/Network_Level/Merged_Packet/output_normal_2.pcap' --modbus --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/aegisot-ics-attacks/ICS_Dataset/Normal_Data/Normal_Set2/Network_Level/Merged_Packet/output_normal_2.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/aegisot-ics-attacks/ICS_Dataset/Normal_Data/Normal_Set2/Network_Level/Merged_Packet/output_normal_2.pcap'
tshark -r 'data/aegisot-ics-attacks/ICS_Dataset/Normal_Data/Normal_Set2/Network_Level/Merged_Packet/output_normal_2.pcap' -q -z io,phs | head -40
```

**2. Map the Modbus/TCP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/aegisot-ics-attacks/ICS_Dataset/Normal_Data/Normal_Set2/Network_Level/Merged_Packet/output_normal_2.pcap' -Y mbtcp -T fields -e ip.src -e ip.dst -e mbtcp.unit_id -e modbus.func_code | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag writes (FC 5/6/15/16/22/23), diagnostics (FC 8 — restart / force-listen-only), device identification (FC 43/14, recon) and Schneider UMAS (FC 90, engineering).

```bash
tshark -r 'data/aegisot-ics-attacks/ICS_Dataset/Normal_Data/Normal_Set2/Network_Level/Merged_Packet/output_normal_2.pcap' -Y 'modbus.func_code in {5, 6, 15, 16, 22, 23, 8, 43, 90}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

## Hints

<details><summary>Hint 1</summary>

Count requests per function code per source — the baseline is a small, stable set.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

A normal-operations capture: the answer is your baseline table (hosts, roles, function codes, register ranges, cadence). Use it to explain each technique capture.

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Write Single Register ×47288, Read Input Registers ×19240, Read Coils ×14431, Read Holding Registers ×9624, Write Single Coil ×156; dangerous-operation matches: 47444 (top sources: 192.168.0.21 ×35548, 192.168.0.22 ×11892, 192.168.0.32 ×4); top conversations in output_normal_2.pcap: 192.168.0.21↔192.168.0.22 (71,309 pkts), 192.168.0.100↔192.168.0.200 (71,041 pkts), 192.168.0.21↔192.168.0.31 (51,366 pkts) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: Kaggle user 'khadijadrira' (2026) · License: CC BY-NC-SA 4.0._

</details>

## Dataset & credit

**Kaggle user 'khadijadrira' (2026)** — license: CC BY-NC-SA 4.0

- [Dataset source — AegisOT — Modbus OT testbed with 11 ATT&amp;CK-for-ICS technique](https://www.kaggle.com/datasets/khadijadrira/industrial-cybersecurity-repository)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/aegisot-ics-attacks/ICS_Dataset/Normal_Data/Normal_Set2/Network_Level/Merged_Packet/output_normal_2.pcap`

</details>
