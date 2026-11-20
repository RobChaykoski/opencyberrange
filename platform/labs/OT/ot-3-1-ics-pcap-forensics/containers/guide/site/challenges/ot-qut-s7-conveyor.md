# QUT S7comm — attacking the conveyor belt

**Process control &amp; PLC testbeds** · **Medium** · 0.0 MB · 0 capture file(s)

> Single S7comm writes that switch the conveyor belt. Decode every one and build the plant's tag map.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

QUT built a small Siemens S7 process plant — a reactor, a conveyor belt with a diverter gate and a water tank, controlled by S7 PLCs and an HMI — and attacked it with crafted S7comm writes from an attacker host. Each attack run was captured from the **attacker**, the **HMI** and the **master** PLC.

This challenge contains one run of each attack on **the conveyor belt**: ConveyorBeltOn, ConveyorBeltOff, ConveyorBeltReset, ConveyorBeltGateChangeDirection. Each run is tiny — the skill is decoding S7comm precisely.

## Objectives

- For each run: which PLC, which memory area / DB, which byte.bit address, which value?
- Build a tag map: address → process meaning.
- Write a detection for unauthorised writes to those addresses.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py qut-s7comm-2017
```

- **[QUT 2017 S7comm — mining-refinery testbed (64 attacks, 13 types)](../DATASETS.md#qut-s7comm-2017)** (`qut-s7comm-2017`), ~0.96 GB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/qut-infosec/2017QUT_S7comm](https://github.com/qut-infosec/2017QUT_S7comm)

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage with Pcapper**

Pcapper auto-detects the OT protocols and services and runs the matching deep-dive analyzers.

```bash
pcapper 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215181147.ConveyorBeltOn/20161215181147.ConveyorBeltOn.attacker.pcap' --overview
```

**2. Decode with Pcapper**

```bash
pcapper 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215181147.ConveyorBeltOn/20161215181147.ConveyorBeltOn.attacker.pcap' --s7 --ot-commands
```

**3. Build the tag map**

One row per attack: area/DB, byte.bit address, value written, and the process effect named by the run.

```bash
ls 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215172609.ConveyorBeltOff' 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215174700.ConveyorBeltGateChangeDirection' 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215181147.ConveyorBeltOn' 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215225915.ConveyorBeltReset'
```

**4. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215181147.ConveyorBeltOn/20161215181147.ConveyorBeltOn.attacker.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215181147.ConveyorBeltOn/20161215181147.ConveyorBeltOn.attacker.pcap'
tshark -r 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215181147.ConveyorBeltOn/20161215181147.ConveyorBeltOn.attacker.pcap' -q -z io,phs | head -40
```

**2. Decode each attack run**

Each run is a few packets: an S7comm Write Var job (function 0x05) with an address and a value. Read them all.

```bash
for f in 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215181147.ConveyorBeltOn/20161215181147.ConveyorBeltOn.attacker.pcap' 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215172609.ConveyorBeltOff/20161215172609.ConveyorBeltOff.attacker.pcap' 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215225915.ConveyorBeltReset/20161215225915.ConveyorBeltReset.attacker.pcap' 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215174700.ConveyorBeltGateChangeDirection/20161215174700.ConveyorBeltGateChangeDirection.attacker.pcap'; do echo "== $f"; tshark -r "$f" -Y s7comm -T fields -e ip.src -e ip.dst -e s7comm.param.func -e s7comm.param.item.area -e s7comm.param.item.db -e s7comm.param.item.address -e s7comm.resp.data; done
```

**3. Build the tag map**

One row per attack: area/DB, byte.bit address, value written, and the process effect named by the run.

```bash
ls 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215172609.ConveyorBeltOff' 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215174700.ConveyorBeltGateChangeDirection' 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215181147.ConveyorBeltOn' 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215225915.ConveyorBeltReset'
```

## Hints

<details><summary>Hint 1</summary>

S7comm function 0x05 = Write Var; 0x04 = Read Var.

</details>

<details><summary>Hint 2</summary>

The run's name tells you the effect — your job is to prove which bytes cause it.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

Each run's folder name is its label (e.g. ReactorOn). Expected answer: a table of run → S7 write (area/DB, address, value) and the same addresses flagged as safety-relevant in your detection.

**Computed evidence (auto-extracted with tshark — verify it yourself):** S7comm operations — Write Var ×6, Read Var ×4; dangerous-operation matches: 6 (top sources: 10.10.10.66 ×4, 10.10.10.10 ×2); top conversations in 20161215181147.ConveyorBeltOn.attacker.pcap: 10.10.10.10↔10.10.10.66 (2 pkts) (basis: 3 of 8 capture file(s), first 300,000 packets each, smallest files carrying S7comm chosen)

_Dataset credit: Rodofile, N. R., Radke, K., Foo, E. (Queensland University of Technology) (2017) · License: No license stated — credit the authors._

</details>

## Dataset & credit

**Rodofile, N. R., Radke, K., Foo, E. (Queensland University of Technology) (2017)** — license: No license stated — credit the authors

- [Dataset source — QUT 2017 S7comm — mining-refinery testbed (64 attacks, 13 ty](https://github.com/qut-infosec/2017QUT_S7comm)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (8)</summary>

- `data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215181147.ConveyorBeltOn/20161215181147.ConveyorBeltOn.attacker.pcap`
- `data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215181147.ConveyorBeltOn/20161215181147.ConveyorBeltOn.master.pcap`
- `data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215172609.ConveyorBeltOff/20161215172609.ConveyorBeltOff.attacker.pcap`
- `data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215172609.ConveyorBeltOff/20161215172609.ConveyorBeltOff.master.pcap`
- `data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215225915.ConveyorBeltReset/20161215225915.ConveyorBeltReset.attacker.pcap`
- `data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215225915.ConveyorBeltReset/20161215225915.ConveyorBeltReset.master.pcap`
- `data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215174700.ConveyorBeltGateChangeDirection/20161215174700.ConveyorBeltGateChangeDirection.attacker.pcap`
- `data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215174700.ConveyorBeltGateChangeDirection/20161215174700.ConveyorBeltGateChangeDirection.master.pcap`

</details>
