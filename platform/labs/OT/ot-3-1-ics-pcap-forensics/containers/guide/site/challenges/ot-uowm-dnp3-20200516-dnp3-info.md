# DNP3 — Info

**Power grid &amp; substations** · **Hard** · 0.0 MB · 0 capture file(s)

> UOWM DNP3 IDS: Info — 14 capture(s).

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

The University of Western Macedonia recorded DNP3 traffic with one attack type per capture set (nine attack types; the bundled ReadMe is authoritative).

This challenge covers the '20200516_DNP3_Info' set (14 capture file(s)). Characterize it, find the attack (if any) and write a detection.

## Objectives

- Identify the protocol roles (masters/clients vs. outstations/servers).
- Find the malicious operations and their source.
- Measure the attack (count, rate, window).
- Write a detection and check it against the dataset's labels.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py uowm-dnp3-ids
```

- **[DNP3 Intrusion Detection Dataset (UOWM)](../DATASETS.md#uowm-dnp3-ids)** (`uowm-dnp3-ids`), ~1.46 GB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (0.61 GB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/uowm-dnp3-ids.tar.part000) (0.61 GB)
  - **Original source:** [zenodo.org/records/7348493](https://zenodo.org/records/7348493) · [doi:10.21227/s7h0-b081](https://doi.org/10.21227/s7h0-b081)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/uowm-dnp3-ids/20200516_DNP3_Info/DNP3 PCAP Files/20200516_DNP3_info_UOWM_DNP3_Dataset_Attacker_01.pcap' --overview
```

**2. Deep-dive with Pcapper (--dnp3)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/uowm-dnp3-ids/20200516_DNP3_Info/DNP3 PCAP Files/20200516_DNP3_info_UOWM_DNP3_Dataset_Attacker_01.pcap' --dnp3 --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/uowm-dnp3-ids/20200516_DNP3_Info/DNP3 PCAP Files/20200516_DNP3_info_UOWM_DNP3_Dataset_Attacker_01.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/uowm-dnp3-ids/20200516_DNP3_Info/DNP3 PCAP Files/20200516_DNP3_info_UOWM_DNP3_Dataset_Attacker_01.pcap'
tshark -r 'data/uowm-dnp3-ids/20200516_DNP3_Info/DNP3 PCAP Files/20200516_DNP3_info_UOWM_DNP3_Dataset_Attacker_01.pcap' -q -z io,phs | head -40
```

**2. Map the DNP3 conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/uowm-dnp3-ids/20200516_DNP3_Info/DNP3 PCAP Files/20200516_DNP3_info_UOWM_DNP3_Dataset_Attacker_01.pcap' -Y dnp3 -T fields -e ip.src -e ip.dst -e dnp3.src -e dnp3.dst -e dnp3.al.func | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag WRITE (2), SELECT/OPERATE (3/4), DIRECT_OPERATE (5/6), COLD/WARM_RESTART (13/14), INITIALIZE_DATA/APPL (15/16), START/STOP_APPL (17/18), DISABLE_UNSOLICITED (21), OPEN/DELETE_FILE (25/27), ACTIVATE_CONFIG (31).

```bash
tshark -r 'data/uowm-dnp3-ids/20200516_DNP3_Info/DNP3 PCAP Files/20200516_DNP3_info_UOWM_DNP3_Dataset_Attacker_01.pcap' -Y 'dnp3.al.func in {2, 3, 4, 5, 6, 13, 14, 15, 16, 17, 18, 21, 25, 27, 31}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
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

**Computed evidence (auto-extracted with tshark — verify it yourself):** DNP3 operations — UNSOLICITED_RESPONSE ×1671; dangerous-operation matches: 0 for the DNP3 filter (3,342 DNP3 packets present, so the zero is real); top conversations in 20200516_DNP3_info_UOWM_DNP3_Dataset_Attacker_03.pcap: 192.168.1.12↔192.168.1.5 (1,108 pkts) (basis: 3 of 14 capture file(s), first 300,000 packets each, smallest files carrying DNP3 chosen)

_Dataset credit: Panagiotis; Vasiliki; Thomas; Vasileios; Panagiotis (2022) — doi:10.21227/s7h0-b081 · License: CC BY 4.0._

</details>

## Dataset & credit

**Panagiotis; Vasiliki; Thomas; Vasileios; Panagiotis (2022) — doi:10.21227/s7h0-b081** — license: CC BY 4.0

- [Dataset source — DNP3 Intrusion Detection Dataset (UOWM)](https://zenodo.org/records/7348493)
- [DOI 10.21227/s7h0-b081](https://doi.org/10.21227/s7h0-b081)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (14)</summary>

- `data/uowm-dnp3-ids/20200516_DNP3_Info/DNP3 PCAP Files/20200516_DNP3_info_UOWM_DNP3_Dataset_Attacker_01.pcap`
- `data/uowm-dnp3-ids/20200516_DNP3_Info/DNP3 PCAP Files/20200516_DNP3_info_UOWM_DNP3_Dataset_Attacker_02.pcap`
- `data/uowm-dnp3-ids/20200516_DNP3_Info/DNP3 PCAP Files/20200516_DNP3_info_UOWM_DNP3_Dataset_Attacker_03.pcap`
- `data/uowm-dnp3-ids/20200516_DNP3_Info/DNP3 PCAP Files/20200516_DNP3_info_UOWM_DNP3_Dataset_Master.pcap`
- `data/uowm-dnp3-ids/20200516_DNP3_Info/DNP3 PCAP Files/20200516_DNP3_info_UOWM_DNP3_Dataset_Slave_01.pcap`
- `data/uowm-dnp3-ids/20200516_DNP3_Info/DNP3 PCAP Files/20200516_DNP3_info_UOWM_DNP3_Dataset_Slave_02.pcap`
- `data/uowm-dnp3-ids/20200516_DNP3_Info/DNP3 PCAP Files/20200516_DNP3_info_UOWM_DNP3_Dataset_Slave_03.pcap`
- `data/uowm-dnp3-ids/20200516_DNP3_Info/Total PCAP Files/20200516_DNP3_info_UOWM_DNP3_Dataset_Attacker_01.pcap`
- `data/uowm-dnp3-ids/20200516_DNP3_Info/Total PCAP Files/20200516_DNP3_info_UOWM_DNP3_Dataset_Attacker_02.pcap`
- `data/uowm-dnp3-ids/20200516_DNP3_Info/Total PCAP Files/20200516_DNP3_info_UOWM_DNP3_Dataset_Attacker_03.pcap`
- `data/uowm-dnp3-ids/20200516_DNP3_Info/Total PCAP Files/20200516_DNP3_info_UOWM_DNP3_Dataset_Master.pcap`
- `data/uowm-dnp3-ids/20200516_DNP3_Info/Total PCAP Files/20200516_DNP3_info_UOWM_DNP3_Dataset_Slave_01.pcap`
- `data/uowm-dnp3-ids/20200516_DNP3_Info/Total PCAP Files/20200516_DNP3_info_UOWM_DNP3_Dataset_Slave_02.pcap`
- `data/uowm-dnp3-ids/20200516_DNP3_Info/Total PCAP Files/20200516_DNP3_info_UOWM_DNP3_Dataset_Slave_03.pcap`

</details>
