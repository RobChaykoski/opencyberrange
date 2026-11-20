# IEC-104 — single command (C_SC_NA_1, TypeID 45) — flood/DoS variant

**Power grid &amp; substations** · **Hard** · 0.0 MB · 0 capture file(s)

> UOWM IEC-104 IDS: single command (C_SC_NA_1, TypeID 45) — flood/DoS variant — 22 capture(s).

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

The University of Western Macedonia recorded IEC 60870-5-104 traffic with one attack type per capture set, for intrusion-detection research (ELECTRON/SPEAR projects).

This challenge covers the '20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS' set (22 capture file(s)). Characterize it, find the attack (if any) and write a detection.

## Objectives

- Identify the protocol roles (masters/clients vs. outstations/servers).
- Find the malicious operations and their source.
- Measure the attack (count, rate, window).
- Write a detection and check it against the dataset's labels.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py uowm-iec104-ids
```

- **[IEC 60870-5-104 Intrusion Detection Dataset (UOWM)](../DATASETS.md#uowm-iec104-ids)** (`uowm-iec104-ids`), ~8.50 GB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 2 parts (3.74 GB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/uowm-iec104-ids.tar.part000) (1.90 GB) · [part001](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/uowm-iec104-ids.tar.part001) (1.84 GB)
  - **Original source:** [zenodo.org/records/7108614](https://zenodo.org/records/7108614) · [doi:10.21227/fj7s-f281](https://doi.org/10.21227/fj7s-f281)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/uowm-iec104-ids/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_attacker1/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_attacker1.pcap' --overview
```

**2. Deep-dive with Pcapper (--iec104)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/uowm-iec104-ids/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_attacker1/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_attacker1.pcap' --iec104 --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/uowm-iec104-ids/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_attacker1/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_attacker1.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/uowm-iec104-ids/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_attacker1/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_attacker1.pcap'
tshark -r 'data/uowm-iec104-ids/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_attacker1/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_attacker1.pcap' -q -z io,phs | head -40
```

**2. Map the IEC-104 conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/uowm-iec104-ids/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_attacker1/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_attacker1.pcap' -Y iec60870_asdu -T fields -e ip.src -e ip.dst -e iec60870_asdu.typeid -e iec60870_asdu.causetx | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag control commands (TypeID 45 single, 46 double, 47 regulating step, 48–50 set-points, 51 bitstring, 58–64 time-tagged variants), interrogations (100 general, 101 counter), read (102), clock sync (103) and reset process (105).

```bash
tshark -r 'data/uowm-iec104-ids/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_attacker1/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_attacker1.pcap' -Y 'iec60870_asdu.typeid in {45, 46, 47, 48, 49, 50, 51, 58, 59, 60, 61, 62, 63, 64, 100, 101, 102, 103, 105}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

## Hints

<details><summary>Hint 1</summary>

The folder/file names and any bundled CSV/label files are the dataset's ground truth.

</details>

<details><summary>Hint 2</summary>

Baseline the normal exchange first, then look for the operations that break it.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

The dataset's own labels (folder name, bundled CSV/JSON/logs and paper) are the answer key for this set.

**Computed evidence (auto-extracted with tshark — verify it yourself):** IEC-104 operations — C_SC_NA_1 ×4482, M_SP_NA_1 ×1644, C_IC_NA_1 ×430; dangerous-operation matches: 4904 (top sources: 192.168.1.25 ×1786, 192.168.1.27 ×784, 192.168.1.26 ×592); top conversations in 20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_attacker2_iec104_only.pcap: 192.168.1.26↔192.168.1.27 (2,471 pkts), 192.168.1.25↔192.168.1.27 (2,233 pkts) (basis: 3 of 22 capture file(s), first 300,000 packets each, smallest files carrying IEC-104 chosen)

_Dataset credit: Panagiotis; Konstantinos; Thomas; Vasileios; Panagiotis (2022) — doi:10.21227/fj7s-f281 · License: CC BY 4.0._

</details>

## Dataset & credit

**Panagiotis; Konstantinos; Thomas; Vasileios; Panagiotis (2022) — doi:10.21227/fj7s-f281** — license: CC BY 4.0

- [Dataset source — IEC 60870-5-104 Intrusion Detection Dataset (UOWM)](https://zenodo.org/records/7108614)
- [DOI 10.21227/fj7s-f281](https://doi.org/10.21227/fj7s-f281)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (22)</summary>

- `data/uowm-iec104-ids/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_attacker1/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_attacker1.pcap`
- `data/uowm-iec104-ids/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_attacker1/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_attacker1_iec104_only.pcap`
- `data/uowm-iec104-ids/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_attacker2/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_attacker2.pcap`
- `data/uowm-iec104-ids/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_attacker2/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_attacker2_iec104_only.pcap`
- `data/uowm-iec104-ids/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_attacker3/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_attacker3.pcap`
- `data/uowm-iec104-ids/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_attacker3/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_attacker3_iec104_only.pcap`
- `data/uowm-iec104-ids/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_iecserver1/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_iecserver1.pcap`
- `data/uowm-iec104-ids/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_iecserver1/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_iecserver1_iec104_only.pcap`
- `data/uowm-iec104-ids/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_iecserver2/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_iecserver2.pcap`
- `data/uowm-iec104-ids/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_iecserver2/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_iecserver2_iec104_only.pcap`
- `data/uowm-iec104-ids/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_iecserver3/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_iecserver3.pcap`
- `data/uowm-iec104-ids/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_iecserver3/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_iecserver3_iec104_only.pcap`
- `data/uowm-iec104-ids/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_iecserver4/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_iecserver4.pcap`
- `data/uowm-iec104-ids/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_iecserver4/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_iecserver4_iec104_only.pcap`
- `data/uowm-iec104-ids/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_iecserver5/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_iecserver5.pcap`
- `data/uowm-iec104-ids/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_iecserver5/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_iecserver5_iec104_only.pcap`
- `data/uowm-iec104-ids/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_iecserver6/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_iecserver6.pcap`
- `data/uowm-iec104-ids/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_iecserver6/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_iecserver6_iec104_only.pcap`
- `data/uowm-iec104-ids/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_iecserver7/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_iecserver7.pcap`
- `data/uowm-iec104-ids/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_iecserver7/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_iecserver7_iec104_only.pcap`
- `data/uowm-iec104-ids/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_qtester/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_qtester.pcap`
- `data/uowm-iec104-ids/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_qtester/20200429_UOWM_IEC104_Dataset_c_sc_na_1_DoS_qtester_iec104_only.pcap`

</details>
