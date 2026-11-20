# CIARRES smart grid — normal operations (baseline)

**Power grid &amp; substations** · **Hard** · 0.0 MB · 0 capture file(s)

> CIARRES smart grid: normal operations (baseline).

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

CIARRES captured an anonymised smart-grid substation network: normal traffic plus GOOSE fuzzing, GOOSE injection, an MMS scanner, a smurf DDoS and a SYN flood.

This challenge is the capture labeled **normal operations (baseline)**.

## Objectives

- Characterize the capture.
- Find the malicious or abnormal activity it is labeled for.
- Write a detection and test it against the normal capture.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py ciarres-smart-grid-attacks
```

- **[CIARRES smart-grid attacks — GOOSE, MMS and Modbus](../DATASETS.md#ciarres-smart-grid-attacks)** (`ciarres-smart-grid-attacks`), ~11.39 GB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 2 parts (3.65 GB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/ciarres-smart-grid-attacks.tar.part000) (1.90 GB) · [part001](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/ciarres-smart-grid-attacks.tar.part001) (1.75 GB)
  - **Original source:** [kaggle.com/datasets/javiersandeuc3m/ciarres-smart-grid-at…](https://www.kaggle.com/datasets/javiersandeuc3m/ciarres-smart-grid-attacks)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/ciarres-smart-grid-attacks/normal/normal_anonymized.pcap.part000.pcap' --overview
```

**2. Deep-dive with Pcapper (--goose)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/ciarres-smart-grid-attacks/normal/normal_anonymized.pcap.part000.pcap' --goose --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/ciarres-smart-grid-attacks/normal/normal_anonymized.pcap.part000.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/ciarres-smart-grid-attacks/normal/normal_anonymized.pcap.part000.pcap'
tshark -r 'data/ciarres-smart-grid-attacks/normal/normal_anonymized.pcap.part000.pcap' -q -z io,phs | head -40
```

**2. Map the IEC 61850 GOOSE conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/ciarres-smart-grid-attacks/normal/normal_anonymized.pcap.part000.pcap' -Y goose -T fields -e eth.src -e goose.gocbRef -e goose.stNum -e goose.sqNum -e goose.timeAllowedtoLive | head -40
```

**3. Hunt the dangerous operations**

Flag GOOSE has no confirmed 'write' — the attack surface is the event stream itself: stNum jumping without a real state change, sqNum resets, bursts far above the retransmission curve, the test/simulation flag, or an unexpected source MAC publishing a known gocbRef.

```bash
tshark -r 'data/ciarres-smart-grid-attacks/normal/normal_anonymized.pcap.part000.pcap' -Y 'goose' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

## Hints

<details><summary>Hint 1</summary>

The filename is the dataset's label — prove it from the packets.

</details>

<details><summary>Hint 2</summary>

Compare against the normal/baseline capture of the same dataset.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

Labeled by the dataset as 'normal operations (baseline)'. The computed evidence summarizes the operations present.

**Computed evidence (auto-extracted with tshark — verify it yourself):** IEC 61850 GOOSE packets matching `goose`: 7,143; GOOSE streams — PM01LogicalDevice/LLN0$GO$securityEvent from 62:63:f9:a2:3a:5b: 2193 frames, 238 distinct stNum, 236 sqNum resets; PM02LogicalDevice/LLN0$GO$securityEvent from 62:63:f9:a2:3a:5b: 2164 frames, 230 distinct stNum, 228 sqNum resets; PM03LogicalDevice/LLN0$GO$securityEvent from 62:63:f9:a2:3a:5b: 1420 frames, 22 distinct stNum, 20 sqNum resets; PM04LogicalDevice/LLN0$GO$securityEvent from 62:63:f9:a2:3a:5b: 1366 frames, 4 distinct stNum, 3 sqNum resets; top conversations in normal_anonymized.pcap.part000.pcap: 10.0.0.3↔10.0.0.4 (180,757 pkts), 10.0.0.3↔10.0.2.1 (23,857 pkts), 10.0.0.3↔10.0.1.1 (23,670 pkts) (basis: 2 of 2 capture file(s), first 300,000 packets each)

_Dataset credit: CIARRES project (Kaggle user 'javiersandeuc3m') (2025) · License: GPL-3.0 (as declared on Kaggle)._

</details>

## Dataset & credit

**CIARRES project (Kaggle user 'javiersandeuc3m') (2025)** — license: GPL-3.0 (as declared on Kaggle)

- [Dataset source — CIARRES smart-grid attacks — GOOSE, MMS and Modbus](https://www.kaggle.com/datasets/javiersandeuc3m/ciarres-smart-grid-attacks)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (2)</summary>

- `data/ciarres-smart-grid-attacks/normal/normal_anonymized.pcap.part000.pcap`
- `data/ciarres-smart-grid-attacks/normal/normal_anonymized.pcap.part001.pcap`

</details>
