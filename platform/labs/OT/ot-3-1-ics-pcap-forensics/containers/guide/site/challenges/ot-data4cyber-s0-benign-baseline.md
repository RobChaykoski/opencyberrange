# Data4Cyber — S0 — benign baseline

**Power grid &amp; substations** · **Medium** · 0.0 MB · 0 capture file(s)

> Data4Cyber: S0 — benign baseline — 3 capture(s).

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Data4Cyber is a labeled cyber-physical dataset for distribution-grid management systems: each scenario folder holds network-tap, attacker-only and benign-only captures plus aligned physical measurements.

This challenge covers the 'S0_benign_baseline' set (3 capture file(s)). Characterize it, find the attack (if any) and write a detection.

## Objectives

- Identify the protocol roles (masters/clients vs. outstations/servers).
- Find the malicious operations and their source.
- Measure the attack (count, rate, window).
- Write a detection and check it against the dataset's labels.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py data4cyber-distribution-grid
```

- **[Data4Cyber — labeled cyber-physical dataset for distribution-grid management](../DATASETS.md#data4cyber-distribution-grid)** (`data4cyber-distribution-grid`), ~0.79 GB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (0.43 GB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/data4cyber-distribution-grid.tar.part000) (0.43 GB)
  - **Original source:** [zenodo.org/records/24105329](https://zenodo.org/records/24105329) · [doi:10.5281/zenodo.24105329](https://doi.org/10.5281/zenodo.24105329)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/data4cyber-distribution-grid/data4cyber_dataset/S0_benign_baseline/attacker_only.pcapng' --overview
```

**2. Deep-dive with Pcapper (--modbus)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/data4cyber-distribution-grid/data4cyber_dataset/S0_benign_baseline/attacker_only.pcapng' --modbus --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/data4cyber-distribution-grid/data4cyber_dataset/S0_benign_baseline/attacker_only.pcapng' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/data4cyber-distribution-grid/data4cyber_dataset/S0_benign_baseline/attacker_only.pcapng'
tshark -r 'data/data4cyber-distribution-grid/data4cyber_dataset/S0_benign_baseline/attacker_only.pcapng' -q -z io,phs | head -40
```

**2. Map the Modbus/TCP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/data4cyber-distribution-grid/data4cyber_dataset/S0_benign_baseline/attacker_only.pcapng' -Y mbtcp -T fields -e ip.src -e ip.dst -e mbtcp.unit_id -e modbus.func_code | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag writes (FC 5/6/15/16/22/23), diagnostics (FC 8 — restart / force-listen-only), device identification (FC 43/14, recon) and Schneider UMAS (FC 90, engineering).

```bash
tshark -r 'data/data4cyber-distribution-grid/data4cyber_dataset/S0_benign_baseline/attacker_only.pcapng' -Y 'modbus.func_code in {5, 6, 15, 16, 22, 23, 8, 43, 90}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
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

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Read Holding Registers ×367162, Write Multiple Registers ×996, Write Single Register ×8; dangerous-operation matches: 1004 (top sources: 192.168.1.11 ×502, 192.168.1.184 ×498, 192.168.1.88 ×4); top conversations in benign_only.pcapng: 192.168.1.11↔192.168.1.61 (111,325 pkts), 192.168.1.11↔192.168.1.62 (110,804 pkts), 192.168.1.11↔192.168.1.65 (55,734 pkts) (basis: 2 of 3 capture file(s), first 300,000 packets each)

_Dataset credit: Sen, Ömer; Bader, Lennart; Emara, Marawan; Serror, Martin; Schwalm, Benedikt; Tsurumi, Junichi; Oba, Tatsumi; Izawa, Tomohiro; Ujiie, Yoshihiro (2026) — doi:10.5281/zenodo.24105329 · License: CC BY 4.0._

</details>

## Dataset & credit

**Sen, Ömer; Bader, Lennart; Emara, Marawan; Serror, Martin; Schwalm, Benedikt; Tsurumi, Junichi; Oba, Tatsumi; Izawa, Tomohiro; Ujiie, Yoshihiro (2026) — doi:10.5281/zenodo.24105329** — license: CC BY 4.0

- [Dataset source — Data4Cyber — labeled cyber-physical dataset for distribution](https://zenodo.org/records/24105329)
- [DOI 10.5281/zenodo.24105329](https://doi.org/10.5281/zenodo.24105329)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (3)</summary>

- `data/data4cyber-distribution-grid/data4cyber_dataset/S0_benign_baseline/attacker_only.pcapng`
- `data/data4cyber-distribution-grid/data4cyber_dataset/S0_benign_baseline/benign_only.pcapng`
- `data/data4cyber-distribution-grid/data4cyber_dataset/S0_benign_baseline/network_tap.pcapng`

</details>
