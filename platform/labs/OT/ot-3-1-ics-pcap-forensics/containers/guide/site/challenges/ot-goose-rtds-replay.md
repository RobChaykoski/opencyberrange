# IEC 61850 GOOSE on RTDS — replay attack

**Power grid &amp; substations** · **Hard** · 0.0 MB · 0 capture file(s)

> GOOSE replay against IEDs on a real-time digital simulator and a physical IED. Find the attacker's frames.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

A real-time digital simulator (RTDS) and a physical IED exchange IEC 61850 GOOSE messages, under a replay attack. Each attack is captured as a train and a test set; for each there is a full capture and an attacker-only capture.

Find the malicious GOOSE frames in the full capture, explain how they differ from the legitimate publisher, and write a detection.

## Objectives

- Identify the legitimate GOOSE publishers (MAC, gocbRef, dataset).
- Find the replay frames.
- Explain the anomaly in stNum/sqNum/timing/content.
- Write a detection and test it on the test split.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py iec61850-goose-rtds-attacks
```

- **[IEC 61850 GOOSE attacks — RTDS simulator + physical IED](../DATASETS.md#iec61850-goose-rtds-attacks)** (`iec61850-goose-rtds-attacks`), ~8.51 GB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (1.63 GB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/iec61850-goose-rtds-attacks.tar.part000) (1.63 GB)
  - **Original source:** [kaggle.com/datasets/johnatandeoliveira/network-traffic-da…](https://www.kaggle.com/datasets/johnatandeoliveira/network-traffic-dataset-iec-61850-cyber-attacks) · [doi:10.1016/j.jisa.2025.104197](https://doi.org/10.1016/j.jisa.2025.104197)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/iec61850-goose-rtds-attacks/pcapng files/pcapng files/replay_train_total.pcapng' --overview
```

**2. Deep-dive with Pcapper (--goose)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/iec61850-goose-rtds-attacks/pcapng files/pcapng files/replay_train_total.pcapng' --goose --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/iec61850-goose-rtds-attacks/pcapng files/pcapng files/replay_train_total.pcapng' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/iec61850-goose-rtds-attacks/pcapng files/pcapng files/replay_train_total.pcapng'
tshark -r 'data/iec61850-goose-rtds-attacks/pcapng files/pcapng files/replay_train_total.pcapng' -q -z io,phs | head -40
```

**2. Map the IEC 61850 GOOSE conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/iec61850-goose-rtds-attacks/pcapng files/pcapng files/replay_train_total.pcapng' -Y goose -T fields -e eth.src -e goose.gocbRef -e goose.stNum -e goose.sqNum -e goose.timeAllowedtoLive | head -40
```

**3. Hunt the dangerous operations**

Flag GOOSE has no confirmed 'write' — the attack surface is the event stream itself: stNum jumping without a real state change, sqNum resets, bursts far above the retransmission curve, the test/simulation flag, or an unexpected source MAC publishing a known gocbRef.

```bash
tshark -r 'data/iec61850-goose-rtds-attacks/pcapng files/pcapng files/replay_train_total.pcapng' -Y 'goose' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Check yourself against the attacker-only capture**

The dataset isolates the attacker's frames — use it only after you have your own answer.

```bash
tshark -r 'data/iec61850-goose-rtds-attacks/pcapng files/pcapng files/replay_train_attacker.pcapng' -Y goose -T fields -e eth.src -e goose.gocbRef -e goose.stNum -e goose.sqNum | sort | uniq -c | sort -rn | head
```

## Hints

<details><summary>Hint 1</summary>

Track stNum/sqNum per gocbRef: legitimate publishers increment them in a strict pattern.

</details>

<details><summary>Hint 2</summary>

Masquerade and injection reuse a real gocbRef — the source MAC and the counters give them away.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

The attacker-only captures shipped with the dataset are the exact answer key; the preprocessed CSVs label every frame.

**Computed evidence (auto-extracted with tshark — verify it yourself):** IEC 61850 GOOSE packets matching `goose`: 539; GOOSE streams — SEL_421_distCFG/LLN0$GO$CB_disj1 from 00:30:a7:29:1f:5a: 170 frames, 19 distinct stNum, 3 sqNum resets; ied_protecaoPROT/LLN0$GO$trip2_dataset from 00:50:c2:4f:9d:cd: 145 frames, 12 distinct stNum, 2 sqNum resets; SEL_421_distCFG/LLN0$GO$CB_prot from 00:30:a7:29:1f:5a: 70 frames, 3 distinct stNum, 2 sqNum resets; ied_disjuntoried_disjuntor1/LLN0$GO$DISJ_cb from 00:50:c2:4f:9d:cd: 63 frames, 5 distinct stNum, 4 sqNum resets; ied_disjuntor2ied_disjuntor2/LLN0$GO$disjuntor2_CB from 00:50:c2:4f:9d:cd: 47 frames, 3 distinct stNum, 2 sqNum resets; top conversations in replay_test_attacker.pcapng: 172.20.11.125↔239.255.255.250 (60 pkts), 192.168.1.76↔224.0.0.251 (12 pkts), 192.168.1.190↔224.0.0.251 (12 pkts) (basis: 3 of 4 capture file(s), first 300,000 packets each, smallest files carrying IEC 61850 GOOSE chosen)

_Dataset credit: Kaggle user 'johnatandeoliveira' (paper in Journal of Information Security and Applications) (2025) — doi:10.1016/j.jisa.2025.104197 · License: CC BY-SA 4.0._

</details>

## Dataset & credit

**Kaggle user 'johnatandeoliveira' (paper in Journal of Information Security and Applications) (2025) — doi:10.1016/j.jisa.2025.104197** — license: CC BY-SA 4.0

- [Dataset source — IEC 61850 GOOSE attacks — RTDS simulator + physical IED](https://www.kaggle.com/datasets/johnatandeoliveira/network-traffic-dataset-iec-61850-cyber-attacks)
- [DOI 10.1016/j.jisa.2025.104197](https://doi.org/10.1016/j.jisa.2025.104197)
- [Paper (J. Inf. Sec. &amp; Appl., 2025)](https://doi.org/10.1016/j.jisa.2025.104197)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (4)</summary>

- `data/iec61850-goose-rtds-attacks/pcapng files/pcapng files/replay_test_total.pcapng`
- `data/iec61850-goose-rtds-attacks/pcapng files/pcapng files/replay_train_total.pcapng`
- `data/iec61850-goose-rtds-attacks/pcapng files/pcapng files/replay_test_attacker.pcapng`
- `data/iec61850-goose-rtds-attacks/pcapng files/pcapng files/replay_train_attacker.pcapng`

</details>
