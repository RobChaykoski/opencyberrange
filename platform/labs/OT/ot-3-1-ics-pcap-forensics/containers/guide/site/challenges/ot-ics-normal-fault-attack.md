# ICS Dataset — normal vs. physical fault vs. cyber attack

**Process control &amp; PLC testbeds** · **Medium** · 0.0 MB · 0 capture file(s)

> Three conditions of one ICS — normal operation, process faults and a cyber attack. Can you tell a fault from an attack on the wire?

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Three conditions of one ICS — normal operation, process faults and a cyber attack. Can you tell a fault from an attack on the wire?

Raw captures of an ICS in three operating conditions — normal, process faults and cyber attack — with CSV/log companions. A good exercise in telling a physical fault from an attack on the wire.

## Objectives

- Identify devices and protocol roles.
- Find and characterize the malicious activity.
- Use the dataset's labels/companion files to check yourself.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py ics-dataset-normal-fault-attack-2025
```

- **[ICS Dataset — normal vs. fault vs. attack traffic (2025)](../DATASETS.md#ics-dataset-normal-fault-attack-2025)** (`ics-dataset-normal-fault-attack-2025`), ~2.50 GB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (0.73 GB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/ics-dataset-normal-fault-attack-2025.tar.part000) (0.73 GB)
  - **Original source:** [zenodo.org/records/17165850](https://zenodo.org/records/17165850) · [doi:10.5281/zenodo.17165850](https://doi.org/10.5281/zenodo.17165850)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/ics-dataset-normal-fault-attack-2025/raw_data/attack/normal_traffic_2025-02-11_20_27_15.pcap' --overview
```

**2. Deep-dive with Pcapper (--modbus)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/ics-dataset-normal-fault-attack-2025/raw_data/attack/normal_traffic_2025-02-11_20_27_15.pcap' --modbus --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/ics-dataset-normal-fault-attack-2025/raw_data/attack/normal_traffic_2025-02-11_20_27_15.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/ics-dataset-normal-fault-attack-2025/raw_data/attack/normal_traffic_2025-02-11_20_27_15.pcap'
tshark -r 'data/ics-dataset-normal-fault-attack-2025/raw_data/attack/normal_traffic_2025-02-11_20_27_15.pcap' -q -z io,phs | head -40
```

**2. Map the Modbus/TCP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/ics-dataset-normal-fault-attack-2025/raw_data/attack/normal_traffic_2025-02-11_20_27_15.pcap' -Y mbtcp -T fields -e ip.src -e ip.dst -e mbtcp.unit_id -e modbus.func_code | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag writes (FC 5/6/15/16/22/23), diagnostics (FC 8 — restart / force-listen-only), device identification (FC 43/14, recon) and Schneider UMAS (FC 90, engineering).

```bash
tshark -r 'data/ics-dataset-normal-fault-attack-2025/raw_data/attack/normal_traffic_2025-02-11_20_27_15.pcap' -Y 'modbus.func_code in {5, 6, 15, 16, 22, 23, 8, 43, 90}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

## Hints

<details><summary>Hint 1</summary>

Look for label files (CSV/JSON/logs) next to the captures — they are the answer key.

</details>

<details><summary>Hint 2</summary>

Compare attack captures against the clean/normal ones.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

The dataset's bundled labels and companion files are the authoritative answer key; the computed evidence below summarizes what the packets show.

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Read Holding Registers ×546505, Write Multiple Registers ×1454; dangerous-operation matches: 1454 (top sources: 192.168.0.11 ×706, 192.168.0.12 ×676, 192.168.0.23 ×57); top conversations in normal_traffic_2025-02-11_20_27_15.pcap: 192.168.0.11↔192.168.0.41 (287,706 pkts), 192.168.0.11↔192.168.0.12 (3,670 pkts), 192.168.0.11↔192.168.0.21 (2,377 pkts) (basis: 3 of 3 capture file(s), first 300,000 packets each)

_Dataset credit: Sudyana, Didik (2025) — doi:10.5281/zenodo.17165850 · License: CC BY 4.0._

</details>

## Dataset & credit

**Sudyana, Didik (2025) — doi:10.5281/zenodo.17165850** — license: CC BY 4.0

- [Dataset source — ICS Dataset — normal vs. fault vs. attack traffic (2025)](https://zenodo.org/records/17165850)
- [DOI 10.5281/zenodo.17165850](https://doi.org/10.5281/zenodo.17165850)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (3)</summary>

- `data/ics-dataset-normal-fault-attack-2025/raw_data/attack/normal_traffic_2025-02-11_20_27_15.pcap`
- `data/ics-dataset-normal-fault-attack-2025/raw_data/fault/faults_traffic_2025-01-10_03_22_36.pcap`
- `data/ics-dataset-normal-fault-attack-2025/raw_data/normal/normal_traffic_2025-01-09_22_43_09.pcap`

</details>
