# Substation ML-IDS — raw IEC-104 traffic

**Power grid &amp; substations** · **Hard** · 0.0 MB · 0 capture file(s)

> Substation ML-IDS: raw IEC-104 traffic — 8 capture(s).

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Raw IEC 61850 and IEC-104 substation traffic with attacks, curated to train ML intrusion detection for electrical substations.

This challenge covers the 'raw-iec104' set (8 capture file(s)). Characterize it, find the attack (if any) and write a detection.

## Objectives

- Identify the protocol roles (masters/clients vs. outstations/servers).
- Find the malicious operations and their source.
- Measure the attack (count, rate, window).
- Write a detection and check it against the dataset's labels.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py substation-ml-ids-iec61850-iec104
```

- **[Electrical-substation ML-IDS dataset — raw IEC 61850 &amp; IEC-104](../DATASETS.md#substation-ml-ids-iec61850-iec104)** (`substation-ml-ids-iec61850-iec104`), ~4.99 GB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (0.28 GB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/substation-ml-ids-iec61850-iec104.tar.part000) (0.28 GB)
  - **Original source:** [zenodo.org/records/15487636](https://zenodo.org/records/15487636) · [doi:10.5281/zenodo.15487636](https://doi.org/10.5281/zenodo.15487636)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/substation-ml-ids-iec61850-iec104/raw-iec104/raw/iec104/attack-data/capture104-dosattack.pcap' --overview
```

**2. Deep-dive with Pcapper (--iec104)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/substation-ml-ids-iec61850-iec104/raw-iec104/raw/iec104/attack-data/capture104-dosattack.pcap' --iec104 --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/substation-ml-ids-iec61850-iec104/raw-iec104/raw/iec104/attack-data/capture104-dosattack.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/substation-ml-ids-iec61850-iec104/raw-iec104/raw/iec104/attack-data/capture104-dosattack.pcap'
tshark -r 'data/substation-ml-ids-iec61850-iec104/raw-iec104/raw/iec104/attack-data/capture104-dosattack.pcap' -q -z io,phs | head -40
```

**2. Map the IEC-104 conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/substation-ml-ids-iec61850-iec104/raw-iec104/raw/iec104/attack-data/capture104-dosattack.pcap' -Y iec60870_asdu -T fields -e ip.src -e ip.dst -e iec60870_asdu.typeid -e iec60870_asdu.causetx | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag control commands (TypeID 45 single, 46 double, 47 regulating step, 48–50 set-points, 51 bitstring, 58–64 time-tagged variants), interrogations (100 general, 101 counter), read (102), clock sync (103) and reset process (105).

```bash
tshark -r 'data/substation-ml-ids-iec61850-iec104/raw-iec104/raw/iec104/attack-data/capture104-dosattack.pcap' -Y 'iec60870_asdu.typeid in {45, 46, 47, 48, 49, 50, 51, 58, 59, 60, 61, 62, 63, 64, 100, 101, 102, 103, 105}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
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

**Computed evidence (auto-extracted with tshark — verify it yourself):** IEC-104 operations — M_SP_NA_1 ×1443, M_ME_TF_1 ×987, 34 ×956, M_ME_NC_1 ×867, 5 ×427, C_CS_NA_1 ×376, M_DP_TB_1 ×293, 21 ×138; dangerous-operation matches: 376 (top sources: 121.142.26.13 ×19, 121.142.26.241 ×18, 121.142.26.88 ×18); top conversations in capture104-floodattack.pcap: 121.142.26.10↔121.142.26.5 (10,889 pkts) (basis: 3 of 8 capture file(s), first 300,000 packets each, smallest files carrying IEC-104 chosen)

_Dataset credit: Gutierrez Mlot, Esteban Damian; Saldana, Jose; Rodríguez, Ricardo J.; Kotsiuba, Igor; Hernández Gañán, Carlos (2024) — doi:10.5281/zenodo.15487636 · License: CC BY-NC-SA 4.0._

</details>

## Dataset & credit

**Gutierrez Mlot, Esteban Damian; Saldana, Jose; Rodríguez, Ricardo J.; Kotsiuba, Igor; Hernández Gañán, Carlos (2024) — doi:10.5281/zenodo.15487636** — license: CC BY-NC-SA 4.0

- [Dataset source — Electrical-substation ML-IDS dataset — raw IEC 61850 &amp; IEC-1](https://zenodo.org/records/15487636)
- [DOI 10.5281/zenodo.15487636](https://doi.org/10.5281/zenodo.15487636)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (8)</summary>

- `data/substation-ml-ids-iec61850-iec104/raw-iec104/raw/iec104/attack-data/capture104-dosattack.pcap`
- `data/substation-ml-ids-iec61850-iec104/raw-iec104/raw/iec104/attack-data/capture104-floodattack.pcap`
- `data/substation-ml-ids-iec61850-iec104/raw-iec104/raw/iec104/attack-data/capture104-fuzzyattack.pcap`
- `data/substation-ml-ids-iec61850-iec104/raw-iec104/raw/iec104/attack-data/capture104-iec104starvationattack.pcap`
- `data/substation-ml-ids-iec61850-iec104/raw-iec104/raw/iec104/attack-data/capture104-mitmattack.pcap`
- `data/substation-ml-ids-iec61850-iec104/raw-iec104/raw/iec104/attack-data/capture104-ntpddosattack.pcap`
- `data/substation-ml-ids-iec61850-iec104/raw-iec104/raw/iec104/attack-data/capture104-portscanattack.pcap`
- `data/substation-ml-ids-iec61850-iec104/raw-iec104/raw/iec104/attack-free-data/capture104-attackfree.pcap`

</details>
