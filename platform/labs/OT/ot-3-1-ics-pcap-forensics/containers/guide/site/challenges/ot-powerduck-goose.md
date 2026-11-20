# PowerDuck — GOOSE attacks on a substation

**Power grid &amp; substations** · **Hard** · 0.0 MB · 0 capture file(s)

> Fake trip insertion, measurement distortion, flooding and more — all against IEC 61850 GOOSE. Each attack capture has a JSON label.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Fake trip insertion, measurement distortion, flooding and more — all against IEC 61850 GOOSE. Each attack capture has a JSON label.

IEC 61850 GOOSE attack captures: fake trip/open insertion (with and without intermediate frames), measurement distortion, flooding/bloat, replay and more, each with a JSON label of the malicious frames.

## Objectives

- Identify devices and protocol roles.
- Find and characterize the malicious activity.
- Use the dataset's labels/companion files to check yourself.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py powerduck-goose-attacks
```

- **[PowerDuck — GOOSE cyberattack dataset (substations)](../DATASETS.md#powerduck-goose-attacks)** (`powerduck-goose-attacks`), ~0.96 GB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (5.6 MB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/powerduck-goose-attacks.tar.part000) (5.6 MB)
  - **Original source:** [zenodo.org/records/6974112](https://zenodo.org/records/6974112) · [doi:10.5281/zenodo.6974112](https://doi.org/10.5281/zenodo.6974112)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/powerduck-goose-attacks/dataset/raw/Attack/01-replay-opening-switch-isolated.pcapng' --overview
```

**2. Deep-dive with Pcapper (--goose)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/powerduck-goose-attacks/dataset/raw/Attack/01-replay-opening-switch-isolated.pcapng' --goose --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/powerduck-goose-attacks/dataset/raw/Attack/01-replay-opening-switch-isolated.pcapng' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/powerduck-goose-attacks/dataset/raw/Attack/01-replay-opening-switch-isolated.pcapng'
tshark -r 'data/powerduck-goose-attacks/dataset/raw/Attack/01-replay-opening-switch-isolated.pcapng' -q -z io,phs | head -40
```

**2. Map the IEC 61850 GOOSE conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/powerduck-goose-attacks/dataset/raw/Attack/01-replay-opening-switch-isolated.pcapng' -Y goose -T fields -e eth.src -e goose.gocbRef -e goose.stNum -e goose.sqNum -e goose.timeAllowedtoLive | head -40
```

**3. Hunt the dangerous operations**

Flag GOOSE has no confirmed 'write' — the attack surface is the event stream itself: stNum jumping without a real state change, sqNum resets, bursts far above the retransmission curve, the test/simulation flag, or an unexpected source MAC publishing a known gocbRef.

```bash
tshark -r 'data/powerduck-goose-attacks/dataset/raw/Attack/01-replay-opening-switch-isolated.pcapng' -Y 'goose' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

## Hints

<details><summary>Hint 1</summary>

Look for label files (CSV/JSON/logs) next to the captures — they are the answer key.

</details>

<details><summary>Hint 2</summary>

Compare attack captures against the clean/normal ones.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

The dataset's bundled labels and companion files are the authoritative answer key; the computed evidence below summarizes what the packets show.

**Computed evidence (auto-extracted with tshark — verify it yourself):** IEC 61850 GOOSE packets matching `goose`: 6,083; GOOSE streams — SIP1_Abgang1MEAS/LLN0$GO$Control_DataSet from b4:b1:5a:0e:84:3b: 1032 frames, 66 distinct stNum, 90 sqNum resets; SIP2_Abgang2MEAS/LLN0$GO$Control_DataSet from b4:b1:5a:0e:84:44: 980 frames, 62 distinct stNum, 60 sqNum resets; SIP3_Abgang3MEAS/LLN0$GO$Control_DataSet from b4:b1:5a:0e:84:4a: 949 frames, 60 distinct stNum, 58 sqNum resets; SIP1_Abgang1CTRL/LLN0$GO$Control_DataSet from b4:b1:5a:0e:84:3b: 646 frames, 5 distinct stNum, 148 sqNum resets; SIP2_Abgang2CTRL/LLN0$GO$Control_DataSet from b4:b1:5a:0e:84:44: 505 frames, 4 distinct stNum, 4 sqNum resets (basis: 3 of 20 capture file(s), first 300,000 packets each, smallest files carrying IEC 61850 GOOSE chosen)

_Dataset credit: Sven Zemanek; Immanuel Hacker; Konrad Wolsing; Eric Wagner; Martin Henze; Martin Serror (2022) — doi:10.5281/zenodo.6974112 · License: CC BY 4.0._

</details>

## Dataset & credit

**Sven Zemanek; Immanuel Hacker; Konrad Wolsing; Eric Wagner; Martin Henze; Martin Serror (2022) — doi:10.5281/zenodo.6974112** — license: CC BY 4.0

- [Dataset source — PowerDuck — GOOSE cyberattack dataset (substations)](https://zenodo.org/records/6974112)
- [DOI 10.5281/zenodo.6974112](https://doi.org/10.5281/zenodo.6974112)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (20)</summary>

- `data/powerduck-goose-attacks/dataset/raw/Attack/01-replay-opening-switch-isolated.pcapng`
- `data/powerduck-goose-attacks/dataset/raw/Attack/02-replay-opening-switch-w-context.pcapng`
- `data/powerduck-goose-attacks/dataset/raw/Attack/03-replay-old-measurements.pcapng`
- `data/powerduck-goose-attacks/dataset/raw/Attack/04-insert-fake-open-w-intermediate.pcapng`
- `data/powerduck-goose-attacks/dataset/raw/Attack/05-insert-fake-open-only-end.pcapng`
- `data/powerduck-goose-attacks/dataset/raw/Attack/06-insert-distort-meas-up-grad.pcapng`
- `data/powerduck-goose-attacks/dataset/raw/Attack/07-insert-distort-meas-down-grad.pcapng`
- `data/powerduck-goose-attacks/dataset/raw/Attack/08-insert-distort-meas-up-sharp.pcapng`
- `data/powerduck-goose-attacks/dataset/raw/Attack/09-insert-distort-meas-down-sharp.pcapng`
- `data/powerduck-goose-attacks/dataset/raw/Attack/10-sup-1-1-tbv0.pcapng`
- `data/powerduck-goose-attacks/dataset/raw/Attack/11-sup-1-1-tbv1.pcapng`
- `data/powerduck-goose-attacks/dataset/raw/Attack/12-sup-1-1-tbv2.pcapng`
- `data/powerduck-goose-attacks/dataset/raw/Attack/13-sup-2.pcapng`
- `data/powerduck-goose-attacks/dataset/raw/Attack/14-sup-1.pcapng`
- `data/powerduck-goose-attacks/dataset/raw/Attack/15-flood-repeat.pcapng`
- `data/powerduck-goose-attacks/dataset/raw/Attack/16-flood-bloat-repeat.pcapng`
- `data/powerduck-goose-attacks/dataset/raw/Normal/01-normal-1.pcapng`
- `data/powerduck-goose-attacks/dataset/raw/Normal/02-normal-2.pcapng`
- `data/powerduck-goose-attacks/dataset/raw/Normal/03-normal-3.pcapng`
- `data/powerduck-goose-attacks/dataset/raw/Normal/04-normal-4.pcapng`

</details>
