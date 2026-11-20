# ADSC IEC 61850 — UnderFrequency

**Power grid &amp; substations** · **Hard** · 0.0 MB · 0 capture file(s)

> ADSC IEC 61850: UnderFrequency.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

ADSC (Singapore) recorded GOOSE traffic for normal operation, protection events (busbar, breaker failure, under-frequency load shedding), DoS, message suppression and data manipulation.

This challenge is the capture labeled **UnderFrequency**.

## Objectives

- Characterize the capture.
- Find the malicious or abnormal activity it is labeled for.
- Write a detection and test it against the normal capture.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py adsc-iec61850-security
```

- **[ADSC IEC 61850 security dataset — GOOSE protection events and attacks](../DATASETS.md#adsc-iec61850-security)** (`adsc-iec61850-security`), ~0.10 GB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/smartgridadsc/IEC61850SecurityDataset](https://github.com/smartgridadsc/IEC61850SecurityDataset)

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/adsc-iec61850-security/IEC61850SecurityDataset-master/Disturbance/Under frequency/UnderFrequency.pcapng' --overview
```

**2. Deep-dive with Pcapper (--goose)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/adsc-iec61850-security/IEC61850SecurityDataset-master/Disturbance/Under frequency/UnderFrequency.pcapng' --goose --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/adsc-iec61850-security/IEC61850SecurityDataset-master/Disturbance/Under frequency/UnderFrequency.pcapng' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/adsc-iec61850-security/IEC61850SecurityDataset-master/Disturbance/Under frequency/UnderFrequency.pcapng'
tshark -r 'data/adsc-iec61850-security/IEC61850SecurityDataset-master/Disturbance/Under frequency/UnderFrequency.pcapng' -q -z io,phs | head -40
```

**2. Map the IEC 61850 GOOSE conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/adsc-iec61850-security/IEC61850SecurityDataset-master/Disturbance/Under frequency/UnderFrequency.pcapng' -Y goose -T fields -e eth.src -e goose.gocbRef -e goose.stNum -e goose.sqNum -e goose.timeAllowedtoLive | head -40
```

**3. Hunt the dangerous operations**

Flag GOOSE has no confirmed 'write' — the attack surface is the event stream itself: stNum jumping without a real state change, sqNum resets, bursts far above the retransmission curve, the test/simulation flag, or an unexpected source MAC publishing a known gocbRef.

```bash
tshark -r 'data/adsc-iec61850-security/IEC61850SecurityDataset-master/Disturbance/Under frequency/UnderFrequency.pcapng' -Y 'goose' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
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

Labeled by the dataset as 'UnderFrequency'. The computed evidence summarizes the operations present.

**Computed evidence (auto-extracted with tshark — verify it yourself):** IEC 61850 GOOSE packets matching `goose`: 31,800; GOOSE streams — LIED10CTRL/LLN0$Status from 00:09:8e:21:73:33: 600 frames, 1 distinct stNum, 0 sqNum resets; LIED10PROT/LLN0$Alarm from 00:09:8e:21:73:33: 600 frames, 1 distinct stNum, 0 sqNum resets; LIED10MEAS/LLN0$Measurement from 00:09:8e:21:73:33: 600 frames, 1 distinct stNum, 0 sqNum resets; LIED11CTRL/LLN0$Status from 00:09:8e:21:73:32: 600 frames, 1 distinct stNum, 0 sqNum resets; LIED11PROT/LLN0$Alarm from 00:09:8e:21:73:32: 600 frames, 1 distinct stNum, 0 sqNum resets; top conversations in UnderFrequency.pcapng: 0.0.0.0↔255.255.255.255 (549 pkts) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: Advanced Digital Sciences Center (ADSC), Singapore (2019) · License: No license stated — credit ADSC._

</details>

## Dataset & credit

**Advanced Digital Sciences Center (ADSC), Singapore (2019)** — license: No license stated — credit ADSC

- [Dataset source — ADSC IEC 61850 security dataset — GOOSE protection events an](https://github.com/smartgridadsc/IEC61850SecurityDataset)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/adsc-iec61850-security/IEC61850SecurityDataset-master/Disturbance/Under frequency/UnderFrequency.pcapng`

</details>
