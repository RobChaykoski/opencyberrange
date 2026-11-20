# Sherlock — Rural topology

**Power grid &amp; substations** · **Hard** · 0.0 MB · 0 capture file(s)

> Sherlock power-grid IDS: Rural topology — 8 capture(s).

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Sherlock simulates power-grid communication networks in three topologies (Basic, Semiurban, Rural) with switch mirror-port captures and physical-process logs for process-aware intrusion detection.

This challenge covers the '03-Rural' set (8 capture file(s)). Characterize it, find the attack (if any) and write a detection.

## Objectives

- Identify the protocol roles (masters/clients vs. outstations/servers).
- Find the malicious operations and their source.
- Measure the attack (count, rate, window).
- Write a detection and check it against the dataset's labels.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py sherlock-power-grid-ids
```

- **[Sherlock — process-aware intrusion detection on power-grid networks](../DATASETS.md#sherlock-power-grid-ids)** (`sherlock-power-grid-ids`), ~2.68 GB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (0.89 GB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/sherlock-power-grid-ids.tar.part000) (0.89 GB)
  - **Original source:** [zenodo.org/records/18467070](https://zenodo.org/records/18467070) · [doi:10.5281/zenodo.18467070](https://doi.org/10.5281/zenodo.18467070)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/sherlock-power-grid-ids/03-Rural/raw/test/pcap/switch-n402-pcap-mir2.pcap' --overview
```

**2. Deep-dive with Pcapper (--iec104)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/sherlock-power-grid-ids/03-Rural/raw/test/pcap/switch-n402-pcap-mir2.pcap' --iec104 --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/sherlock-power-grid-ids/03-Rural/raw/test/pcap/switch-n402-pcap-mir2.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/sherlock-power-grid-ids/03-Rural/raw/test/pcap/switch-n402-pcap-mir2.pcap'
tshark -r 'data/sherlock-power-grid-ids/03-Rural/raw/test/pcap/switch-n402-pcap-mir2.pcap' -q -z io,phs | head -40
```

**2. Map the IEC-104 conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/sherlock-power-grid-ids/03-Rural/raw/test/pcap/switch-n402-pcap-mir2.pcap' -Y iec60870_asdu -T fields -e ip.src -e ip.dst -e iec60870_asdu.typeid -e iec60870_asdu.causetx | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag control commands (TypeID 45 single, 46 double, 47 regulating step, 48–50 set-points, 51 bitstring, 58–64 time-tagged variants), interrogations (100 general, 101 counter), read (102), clock sync (103) and reset process (105).

```bash
tshark -r 'data/sherlock-power-grid-ids/03-Rural/raw/test/pcap/switch-n402-pcap-mir2.pcap' -Y 'iec60870_asdu.typeid in {45, 46, 47, 48, 49, 50, 51, 58, 59, 60, 61, 62, 63, 64, 100, 101, 102, 103, 105}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
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

**Computed evidence (auto-extracted with tshark — verify it yourself):** IEC-104 operations — M_ME_NC_1 ×157983, C_SE_NC_1 ×372, C_SC_NA_1 ×94, C_IC_NA_1 ×12, C_CS_NA_1 ×8, M_SP_NA_1 ×5; dangerous-operation matches: 486 (top sources: 172.16.5.3 ×189, 172.16.5.12 ×187, 172.16.5.5 ×49); top conversations in switch-n403-pcap-mir5.pcap: 172.16.1.2↔172.16.2.5 (51,976 pkts), 172.16.1.2↔172.16.2.4 (43,496 pkts), 172.16.1.2↔172.16.2.2 (41,513 pkts) (basis: 3 of 8 capture file(s), first 300,000 packets each, smallest files carrying IEC-104 chosen)

_Dataset credit: Wagner, Eric; Bader, Lennart; Wolsing, Konrad; Serror, Martin (2026) — doi:10.5281/zenodo.18467070 · License: CC BY 4.0._

</details>

## Dataset & credit

**Wagner, Eric; Bader, Lennart; Wolsing, Konrad; Serror, Martin (2026) — doi:10.5281/zenodo.18467070** — license: CC BY 4.0

- [Dataset source — Sherlock — process-aware intrusion detection on power-grid n](https://zenodo.org/records/18467070)
- [DOI 10.5281/zenodo.18467070](https://doi.org/10.5281/zenodo.18467070)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (8)</summary>

- `data/sherlock-power-grid-ids/03-Rural/raw/test/pcap/switch-n402-pcap-mir2.pcap`
- `data/sherlock-power-grid-ids/03-Rural/raw/test/pcap/switch-n403-pcap-mir5.pcap`
- `data/sherlock-power-grid-ids/03-Rural/raw/test/pcap/switch-n468-pcap-mir3.pcap`
- `data/sherlock-power-grid-ids/03-Rural/raw/test/pcap/switch-n472-pcap-mir4.pcap`
- `data/sherlock-power-grid-ids/03-Rural/raw/test/pcap/switch-n477-pcap-mir3.pcap`
- `data/sherlock-power-grid-ids/03-Rural/raw/test/pcap/switch-n484-pcap-mir4.pcap`
- `data/sherlock-power-grid-ids/03-Rural/raw/test/pcap/switch-n493-pcap-mir4.pcap`
- `data/sherlock-power-grid-ids/03-Rural/raw/test/pcap/switch-n502-pcap-mir4.pcap`

</details>
