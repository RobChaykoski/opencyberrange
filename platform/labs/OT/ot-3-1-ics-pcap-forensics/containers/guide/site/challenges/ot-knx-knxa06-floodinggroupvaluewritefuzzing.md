# KNXnet/IP — flooding with fuzzed GroupValueWrites

**Building automation** · **Hard** · 0.0 MB · 0 capture file(s)

> KNXnet/IP building automation: flooding with fuzzed GroupValueWrites — 1 capture(s).

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

The University of Western Macedonia recorded KNXnet/IP building-automation traffic with one attack per capture — fuzzing, master reset, network and bus scanning, flooding with valid or fuzzed group-value reads/writes, and unauthorised group-value writes. Each folder ships labelled KNX and CIC flow CSVs: your answer key.

This challenge covers the 'KNXA06_FloodingGroupValueWriteFuzzing' set (1 capture file(s)). Characterize it, find the attack (if any) and write a detection.

## Objectives

- Identify the protocol roles (masters/clients vs. outstations/servers).
- Find the malicious operations and their source.
- Measure the attack (count, rate, window).
- Write a detection and check it against the dataset's labels.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py knxnetip-ids
```

- **[KNXnet/IP intrusion dataset — building automation attacks (UOWM)](../DATASETS.md#knxnetip-ids)** (`knxnetip-ids`), ~3.05 GB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (1.49 GB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/knxnetip-ids.tar.part000) (1.49 GB)
  - **Original source:** [zenodo.org/records/16957517](https://zenodo.org/records/16957517) · [doi:10.5281/zenodo.16957517](https://doi.org/10.5281/zenodo.16957517)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/knxnetip-ids/KNXA06_FloodingGroupValueWriteFuzzing/KNXA06_20250619_FloodingGroupValueWriteFuzzing.pcap' --overview
```

**2. Deep-dive with Pcapper (--overview)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/knxnetip-ids/KNXA06_FloodingGroupValueWriteFuzzing/KNXA06_20250619_FloodingGroupValueWriteFuzzing.pcap' --overview --ot-commands
```

**3. Every control and write, normalized**

--ot-commands lists every OT control/write command across protocols; --threats consolidates Pcapper's detections.

```bash
pcapper 'data/knxnetip-ids/KNXA06_FloodingGroupValueWriteFuzzing/KNXA06_20250619_FloodingGroupValueWriteFuzzing.pcap' --ot-commands --threats
```

**4. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/knxnetip-ids/KNXA06_FloodingGroupValueWriteFuzzing/KNXA06_20250619_FloodingGroupValueWriteFuzzing.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/knxnetip-ids/KNXA06_FloodingGroupValueWriteFuzzing/KNXA06_20250619_FloodingGroupValueWriteFuzzing.pcap'
tshark -r 'data/knxnetip-ids/KNXA06_FloodingGroupValueWriteFuzzing/KNXA06_20250619_FloodingGroupValueWriteFuzzing.pcap' -q -z io,phs | head -40
```

**2. Map the KNXnet/IP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/knxnetip-ids/KNXA06_FloodingGroupValueWriteFuzzing/KNXA06_20250619_FloodingGroupValueWriteFuzzing.pcap' -Y cemi -T fields -e ip.src -e cemi.da -e cemi.ac | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag GroupValueWrite (cEMI APCI 0x0002) changes building group values — lights, blinds, HVAC set-points, door locks; property reads/resets and bus scans are reconnaissance or disruption.

```bash
tshark -r 'data/knxnetip-ids/KNXA06_FloodingGroupValueWriteFuzzing/KNXA06_20250619_FloodingGroupValueWriteFuzzing.pcap' -Y 'cemi.ac == 2' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
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

**Computed evidence (auto-extracted with tshark — verify it yourself):** KNXnet/IP packets matching `kip`: 287,470; dangerous-operation matches: 103456 (top sources: 192.168.21.242 ×79280, 192.168.21.220 ×24176); top conversations in KNXA06_20250619_FloodingGroupValueWriteFuzzing.pcap: 192.168.21.220↔192.168.21.242 (165,750 pkts), 192.168.21.242↔192.168.21.250 (121,720 pkts), 10.64.117.119↔255.255.255.255 (6,110 pkts) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: Dalamagkas, Radoglou-Grammatikis, et al. (Univ. of Western Macedonia) (2025) — doi:10.5281/zenodo.16957517 · License: CC BY 4.0._

</details>

## Dataset & credit

**Dalamagkas, Radoglou-Grammatikis, et al. (Univ. of Western Macedonia) (2025) — doi:10.5281/zenodo.16957517** — license: CC BY 4.0

- [Dataset source — KNXnet/IP intrusion dataset — building automation attacks (U](https://zenodo.org/records/16957517)
- [DOI 10.5281/zenodo.16957517](https://doi.org/10.5281/zenodo.16957517)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/knxnetip-ids/KNXA06_FloodingGroupValueWriteFuzzing/KNXA06_20250619_FloodingGroupValueWriteFuzzing.pcap`

</details>
