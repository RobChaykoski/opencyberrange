# TU Delft substation — Reconnaissance

**Power grid &amp; substations** · **Hard** · 0.0 MB · 0 capture file(s)

> TU Delft digital substation: Reconnaissance — 8 capture(s).

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

TU Delft's IEC 61850 hardware-in-the-loop testbed (RTDS + physical and virtual IEDs) captured normal operation, power-system faults and cyberattacks.

This challenge covers the 'Reconnaissance' set (8 capture file(s)). Characterize it, find the attack (if any) and write a detection.

## Objectives

- Identify the protocol roles (masters/clients vs. outstations/servers).
- Find the malicious operations and their source.
- Measure the attack (count, rate, window).
- Write a detection and check it against the dataset's labels.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py tudelft-digital-substation-cpps
```

- **[TU Delft — cyber-physical power system dataset for digital substations](../DATASETS.md#tudelft-digital-substation-cpps)** (`tudelft-digital-substation-cpps`), ~6.12 GB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (1.77 GB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/tudelft-digital-substation-cpps.tar.part000) (1.77 GB)
  - **Original source:** [zenodo.org/records/23558261](https://zenodo.org/records/23558261) · [doi:10.5281/zenodo.23558261](https://doi.org/10.5281/zenodo.23558261)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/tudelft-digital-substation-cpps/2026_10_19_CPPS_Dataset_CyberSec_DigitalSubstation_TUD/Scenarios/Reconnaissance/nmap_aggressive/nmap_aggressive_attacker_anon.pcapng' --overview
```

**2. Deep-dive with Pcapper (--goose)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/tudelft-digital-substation-cpps/2026_10_19_CPPS_Dataset_CyberSec_DigitalSubstation_TUD/Scenarios/Reconnaissance/nmap_aggressive/nmap_aggressive_attacker_anon.pcapng' --goose --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/tudelft-digital-substation-cpps/2026_10_19_CPPS_Dataset_CyberSec_DigitalSubstation_TUD/Scenarios/Reconnaissance/nmap_aggressive/nmap_aggressive_attacker_anon.pcapng' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/tudelft-digital-substation-cpps/2026_10_19_CPPS_Dataset_CyberSec_DigitalSubstation_TUD/Scenarios/Reconnaissance/nmap_aggressive/nmap_aggressive_attacker_anon.pcapng'
tshark -r 'data/tudelft-digital-substation-cpps/2026_10_19_CPPS_Dataset_CyberSec_DigitalSubstation_TUD/Scenarios/Reconnaissance/nmap_aggressive/nmap_aggressive_attacker_anon.pcapng' -q -z io,phs | head -40
```

**2. Map the IEC 61850 GOOSE conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/tudelft-digital-substation-cpps/2026_10_19_CPPS_Dataset_CyberSec_DigitalSubstation_TUD/Scenarios/Reconnaissance/nmap_aggressive/nmap_aggressive_attacker_anon.pcapng' -Y goose -T fields -e eth.src -e goose.gocbRef -e goose.stNum -e goose.sqNum -e goose.timeAllowedtoLive | head -40
```

**3. Hunt the dangerous operations**

Flag GOOSE has no confirmed 'write' — the attack surface is the event stream itself: stNum jumping without a real state change, sqNum resets, bursts far above the retransmission curve, the test/simulation flag, or an unexpected source MAC publishing a known gocbRef.

```bash
tshark -r 'data/tudelft-digital-substation-cpps/2026_10_19_CPPS_Dataset_CyberSec_DigitalSubstation_TUD/Scenarios/Reconnaissance/nmap_aggressive/nmap_aggressive_attacker_anon.pcapng' -Y 'goose' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
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

**Computed evidence (auto-extracted with tshark — verify it yourself):** IEC 61850 GOOSE packets matching `goose`: 769; GOOSE streams — IEDBSystem/LLN0$GO$gcb01 from 12:c5:b1:f1:f1:f1: 185 frames, 1 distinct stNum, 1 sqNum resets; IEDA_SVSystem/LLN0$GO$gcb01 from 12:c5:b1:f1:f1:f2: 185 frames, 1 distinct stNum, 1 sqNum resets; IEDA_SVSystem/LLN0$GO$gcb02 from 12:c5:b1:f1:f1:f2: 184 frames, 1 distinct stNum, 1 sqNum resets; vied_protHTA/LLN0$GO$EVENT_GSE_TRIP_TG from f5:a0:8d:e8:8f:2d: 123 frames, 1 distinct stNum, 1 sqNum resets; IEDC_BCB1/LLN0$GO$Control_DataSet from 02:00:00:00:00:01: 92 frames, 1 distinct stNum, 1 sqNum resets; top conversations in nmap_insane_vied_anon.pcapng: 192.168.0.10↔192.168.0.11 (2,273 pkts), 192.168.0.10↔198.18.0.4 (384 pkts), 192.168.0.10↔198.18.3.1 (16 pkts) (basis: 3 of 8 capture file(s), first 300,000 packets each, smallest files carrying IEC 61850 GOOSE chosen)

_Dataset credit: Cibin, Nicola; Kabbara, Nadine; Presekal, Alfan; Semertzis, Ioannis; Rajkumar, Vetrivel; Goyel, Himanshu; Palensky, Peter; Stefanov, Alexandru (2026) — doi:10.5281/zenodo.23558261 · License: CC BY 4.0._

</details>

## Dataset & credit

**Cibin, Nicola; Kabbara, Nadine; Presekal, Alfan; Semertzis, Ioannis; Rajkumar, Vetrivel; Goyel, Himanshu; Palensky, Peter; Stefanov, Alexandru (2026) — doi:10.5281/zenodo.23558261** — license: CC BY 4.0

- [Dataset source — TU Delft — cyber-physical power system dataset for digital s](https://zenodo.org/records/23558261)
- [DOI 10.5281/zenodo.23558261](https://doi.org/10.5281/zenodo.23558261)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (8)</summary>

- `data/tudelft-digital-substation-cpps/2026_10_19_CPPS_Dataset_CyberSec_DigitalSubstation_TUD/Scenarios/Reconnaissance/nmap_aggressive/nmap_aggressive_attacker_anon.pcapng`
- `data/tudelft-digital-substation-cpps/2026_10_19_CPPS_Dataset_CyberSec_DigitalSubstation_TUD/Scenarios/Reconnaissance/nmap_aggressive/nmap_aggressive_vied_anon.pcapng`
- `data/tudelft-digital-substation-cpps/2026_10_19_CPPS_Dataset_CyberSec_DigitalSubstation_TUD/Scenarios/Reconnaissance/nmap_insane/nmap_insane_attacker_anon.pcapng`
- `data/tudelft-digital-substation-cpps/2026_10_19_CPPS_Dataset_CyberSec_DigitalSubstation_TUD/Scenarios/Reconnaissance/nmap_insane/nmap_insane_vied_anon.pcapng`
- `data/tudelft-digital-substation-cpps/2026_10_19_CPPS_Dataset_CyberSec_DigitalSubstation_TUD/Scenarios/Reconnaissance/nmap_normal/nmap_normal_attacker_anon.pcapng`
- `data/tudelft-digital-substation-cpps/2026_10_19_CPPS_Dataset_CyberSec_DigitalSubstation_TUD/Scenarios/Reconnaissance/nmap_normal/nmap_normal_vied_anon.pcapng`
- `data/tudelft-digital-substation-cpps/2026_10_19_CPPS_Dataset_CyberSec_DigitalSubstation_TUD/Scenarios/Reconnaissance/nmap_polite/nmap_polite_attacker_anon.pcapng`
- `data/tudelft-digital-substation-cpps/2026_10_19_CPPS_Dataset_CyberSec_DigitalSubstation_TUD/Scenarios/Reconnaissance/nmap_polite/nmap_polite_vied_anon.pcapng`

</details>
