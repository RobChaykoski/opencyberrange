# QUT S7comm — flooding the process

**Process control &amp; PLC testbeds** · **Hard** · 0.0 MB · 0 capture file(s)

> The same process writes, sent thousands of times. What is flooded, and does it matter?

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

QUT built a small Siemens S7 process plant — a reactor, a conveyor belt with a diverter gate and a water tank, controlled by S7 PLCs and an HMI — and attacked it with crafted S7comm writes from an attacker host. Each attack run was captured from the **attacker**, the **HMI** and the **master** PLC.

These are the master-side captures of 9 flooding runs (ChangeUpperThreshold, ConveyorBeltGateChangeDirection, ConveyorBeltOff, ConveyorBeltOn, ReactorOff, ReactorOn, WaterTankOff, WaterTankOnAuto, WaterTankOnManu): the attacker repeats one process write at high rate.

## Objectives

- Measure the rate of each flood.
- Identify what each flood writes.
- Assess the process impact vs a single write.
- Write a rate-based detection.

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

**1. Triage the first flood**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215191717.ChangeUpperThreshold_Flooding/20161215191717.ChangeUpperThreshold_Flooding.master.pcap' --overview
```

**2. Deep-dive with Pcapper (--s7)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215191717.ChangeUpperThreshold_Flooding/20161215191717.ChangeUpperThreshold_Flooding.master.pcap' --s7 --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215191717.ChangeUpperThreshold_Flooding/20161215191717.ChangeUpperThreshold_Flooding.master.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the first flood**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215191717.ChangeUpperThreshold_Flooding/20161215191717.ChangeUpperThreshold_Flooding.master.pcap'
tshark -r 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215191717.ChangeUpperThreshold_Flooding/20161215191717.ChangeUpperThreshold_Flooding.master.pcap' -q -z io,phs | head -40
```

**2. Map the S7comm conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215191717.ChangeUpperThreshold_Flooding/20161215191717.ChangeUpperThreshold_Flooding.master.pcap' -Y s7comm -T fields -e ip.src -e ip.dst -e s7comm.header.rosctr -e s7comm.param.func -e s7comm.param.userdata.funcgroup -e s7comm.param.userdata.subfunc | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag write variable (0x05), program download (0x1A–0x1C), program upload (0x1D–0x1F — logic theft), PI-service (0x28 — start/restart/compress), PLC STOP (0x29) and security/password userdata (function group 5); SZL reads (function group 4) are device recon.

```bash
tshark -r 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215191717.ChangeUpperThreshold_Flooding/20161215191717.ChangeUpperThreshold_Flooding.master.pcap' -Y 's7comm.param.func in {0x05, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 0x28, 0x29} || s7comm.param.userdata.funcgroup == 5' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Rates for every flood**

```bash
for f in 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215191717.ChangeUpperThreshold_Flooding/20161215191717.ChangeUpperThreshold_Flooding.master.pcap' 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215185758.ConveyorBeltGateChangeDirection_Flooding/20161215185758.ConveyorBeltGateChangeDirection_Flooding.master.pcap' 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215200749.ConveyorBeltOff_Flooding/20161215200749.ConveyorBeltOff_Flooding.master.pcap' 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215192146.ConveyorBeltOn_Flooding/20161215192146.ConveyorBeltOn_Flooding.master.pcap' 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215205406.ReactorOff_Flooding/20161215205406.ReactorOff_Flooding.master.pcap' 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215195722.ReactorOn_Flooding/20161215195722.ReactorOn_Flooding.master.pcap' 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215203826.WaterTankOff_Flooding/20161215203826.WaterTankOff_Flooding.master.pcap' 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215193421.WaterTankOnAuto_Flooding/20161215193421.WaterTankOnAuto_Flooding.master.pcap' 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215190548.WaterTankOnManu_Flooding/20161215190548.WaterTankOnManu_Flooding.master.pcap'; do echo "== $f"; capinfos -c -u "$f" | tail -2; done
```

## Hints

<details><summary>Hint 1</summary>

Compare with the single-write runs in the other QUT S7comm challenges.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

Each folder is labelled &lt;attack&gt;_Flooding. Answer: per flood, the write (area/address/value) and the rate; detection by write rate per source.

**Computed evidence (auto-extracted with tshark — verify it yourself):** S7comm operations — Write Var ×117436, Read Var ×2034; dangerous-operation matches: 117436 (top sources: 10.10.10.10 ×58718, 10.10.10.66 ×58693, 10.10.10.20 ×25); top conversations in 20161215190548.WaterTankOnManu_Flooding.master.pcap: 10.10.10.10↔10.10.10.66 (35,763 pkts), 10.10.10.10↔10.10.10.20 (1,062 pkts) (basis: 3 of 9 capture file(s), first 300,000 packets each, smallest files carrying S7comm chosen)

_Dataset credit: Rodofile, N. R., Radke, K., Foo, E. (Queensland University of Technology) (2017) · License: No license stated — credit the authors._

</details>

## Dataset & credit

**Rodofile, N. R., Radke, K., Foo, E. (Queensland University of Technology) (2017)** — license: No license stated — credit the authors

- [Dataset source — QUT 2017 S7comm — mining-refinery testbed (64 attacks, 13 ty](https://github.com/qut-infosec/2017QUT_S7comm)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (9)</summary>

- `data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215191717.ChangeUpperThreshold_Flooding/20161215191717.ChangeUpperThreshold_Flooding.master.pcap`
- `data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215185758.ConveyorBeltGateChangeDirection_Flooding/20161215185758.ConveyorBeltGateChangeDirection_Flooding.master.pcap`
- `data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215200749.ConveyorBeltOff_Flooding/20161215200749.ConveyorBeltOff_Flooding.master.pcap`
- `data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215192146.ConveyorBeltOn_Flooding/20161215192146.ConveyorBeltOn_Flooding.master.pcap`
- `data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215205406.ReactorOff_Flooding/20161215205406.ReactorOff_Flooding.master.pcap`
- `data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215195722.ReactorOn_Flooding/20161215195722.ReactorOn_Flooding.master.pcap`
- `data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215203826.WaterTankOff_Flooding/20161215203826.WaterTankOff_Flooding.master.pcap`
- `data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215193421.WaterTankOnAuto_Flooding/20161215193421.WaterTankOnAuto_Flooding.master.pcap`
- `data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830/20161215190548.WaterTankOnManu_Flooding/20161215190548.WaterTankOnManu_Flooding.master.pcap`

</details>
