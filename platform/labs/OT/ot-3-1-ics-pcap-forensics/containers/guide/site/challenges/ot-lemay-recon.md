# Lemay SCADA — characterization / reconnaissance

**Process control &amp; PLC testbeds** · **Medium** · 0.0 MB · 0 capture file(s)

> Something inside the SCADA network starts mapping the RTUs. Find it.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Lemay &amp; Fernandez (CSET 2016) built simulated SCADA networks — a master polling Modbus RTUs — and recorded normal operation plus labelled malicious activity, to give ICS intrusion-detection research realistic data.

Something inside the SCADA network starts mapping the RTUs. Find it.

## Objectives

- Separate normal polling from everything else.
- Identify the malicious activity, its source and its targets.
- Explain how a defender would detect it.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py lemay-scada-modbus-cset2016
```

- **[Lemay &amp; Fernandez SCADA Modbus dataset (CSET 2016)](../DATASETS.md#lemay-scada-modbus-cset2016)** (`lemay-scada-modbus-cset2016`), ~84.5 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/antoine-lemay/Modbus_dataset](https://github.com/antoine-lemay/Modbus_dataset)

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage with Pcapper**

```bash
pcapper 'data/lemay-scada-modbus-cset2016/characterization_modbus_6RTU_with_operate.pcap' --overview
```

**2. Normalize all control operations**

```bash
pcapper 'data/lemay-scada-modbus-cset2016/characterization_modbus_6RTU_with_operate.pcap' --modbus --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/lemay-scada-modbus-cset2016/characterization_modbus_6RTU_with_operate.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage with Pcapper**

```bash
capinfos 'data/lemay-scada-modbus-cset2016/characterization_modbus_6RTU_with_operate.pcap'
tshark -r 'data/lemay-scada-modbus-cset2016/characterization_modbus_6RTU_with_operate.pcap' -q -z io,phs | head -40
```

**2. Who talks to whom**

```bash
tshark -r 'data/lemay-scada-modbus-cset2016/characterization_modbus_6RTU_with_operate.pcap' -q -z conv,tcp | head -25
```

**3. Profile requests per source**

```bash
tshark -r 'data/lemay-scada-modbus-cset2016/characterization_modbus_6RTU_with_operate.pcap' -Y 'mbtcp' -T fields -e ip.src -e mbtcp.unit_id -e modbus.func_code | sort | uniq -c | sort -rn | head -30
```

## Hints

<details><summary>Hint 1</summary>

Do the baseline challenge first — the attacks only stand out against the normal cycle.

</details>

<details><summary>Hint 2</summary>

Anything that isn't Modbus on this network is suspicious by default.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

An intruder characterizes the Modbus network — sweeping unit IDs, function codes and register ranges beyond what the master normally polls. The anomalous source and its request pattern are the finding. The capture's filename is the dataset's ground-truth label.

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Read Input Registers ×6629, Read Holding Registers ×436, Read Discrete Inputs ×428, Read Coils ×420, Write Single Coil ×6; dangerous-operation matches: 6 (top sources: 192.168.1.100 ×3, 192.168.1.101 ×2, 192.168.1.103 ×1); top conversations in characterization_modbus_6RTU_with_operate.pcap: 192.168.1.101↔192.168.1.104 (6,719 pkts), 192.168.1.100↔192.168.1.104 (939 pkts), 192.168.1.100↔192.168.1.101 (936 pkts) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: Antoine Lemay &amp; José M. Fernandez (Polytechnique Montréal) (2016) · License: No license stated in repo — credit the author._

</details>

## Dataset & credit

**Antoine Lemay &amp; José M. Fernandez (Polytechnique Montréal) (2016)** — license: No license stated in repo — credit the author

- [Dataset source — Lemay &amp; Fernandez SCADA Modbus dataset (CSET 2016)](https://github.com/antoine-lemay/Modbus_dataset)
- [Lemay &amp; Fernandez, CSET '16 (USENIX)](https://www.usenix.org/conference/cset16/workshop-program/presentation/lemay)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/lemay-scada-modbus-cset2016/characterization_modbus_6RTU_with_operate.pcap`

</details>
