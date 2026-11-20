# Lemay SCADA — baseline Modbus polling (3, 6 and 12 RTUs)

**Process control &amp; PLC testbeds** · **Easy** · 0.0 MB · 0 capture file(s)

> Normal SCADA operation at three network sizes — your yardstick for the attack captures.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Lemay &amp; Fernandez (CSET 2016) built simulated SCADA networks — a master polling Modbus RTUs — and recorded normal operation plus labelled malicious activity, to give ICS intrusion-detection research realistic data.

Normal SCADA operation at three network sizes — your yardstick for the attack captures.

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
pcapper 'data/lemay-scada-modbus-cset2016/Modbus_polling_only_6RTU(2).pcap' --overview
```

**2. Normalize all control operations**

```bash
pcapper 'data/lemay-scada-modbus-cset2016/Modbus_polling_only_6RTU(2).pcap' --modbus --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/lemay-scada-modbus-cset2016/Modbus_polling_only_6RTU(2).pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage with Pcapper**

```bash
capinfos 'data/lemay-scada-modbus-cset2016/Modbus_polling_only_6RTU(2).pcap'
tshark -r 'data/lemay-scada-modbus-cset2016/Modbus_polling_only_6RTU(2).pcap' -q -z io,phs | head -40
```

**2. Who talks to whom**

```bash
tshark -r 'data/lemay-scada-modbus-cset2016/Modbus_polling_only_6RTU(2).pcap' -q -z conv,tcp | head -25
```

**3. Measure the polling cycle**

```bash
tshark -r 'data/lemay-scada-modbus-cset2016/Modbus_polling_only_6RTU(2).pcap' -q -z io,stat,1 | head -20
tshark -r 'data/lemay-scada-modbus-cset2016/Modbus_polling_only_6RTU(2).pcap' -Y mbtcp -T fields -e ip.dst -e mbtcp.unit_id -e modbus.func_code -e modbus.reference_num | sort | uniq -c | sort -rn | head -30
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

Normal polling of 3/6/12 RTUs by the SCADA master: fixed cycle, fixed function codes and register ranges per RTU, occasional operator 'operate' writes. This is the yardstick for the other Lemay challenges. The capture's filename is the dataset's ground-truth label.

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Read Holding Registers ×12900, Read Discrete Inputs ×12896, Read Coils ×12892, Write Single Coil ×386; dangerous-operation matches: 386 (top sources: 192.168.1.99 ×97, 192.168.1.100 ×96, 192.168.1.103 ×74); top conversations in Modbus_polling_only_6RTU(2).pcap: 192.168.1.100↔192.168.1.102 (9,854 pkts), 192.168.1.100↔192.168.1.101 (9,654 pkts), 192.168.1.100↔192.168.1.106 (9,639 pkts) (basis: 3 of 6 capture file(s), first 300,000 packets each, smallest files carrying Modbus/TCP chosen)

_Dataset credit: Antoine Lemay &amp; José M. Fernandez (Polytechnique Montréal) (2016) · License: No license stated in repo — credit the author._

</details>

## Dataset & credit

**Antoine Lemay &amp; José M. Fernandez (Polytechnique Montréal) (2016)** — license: No license stated in repo — credit the author

- [Dataset source — Lemay &amp; Fernandez SCADA Modbus dataset (CSET 2016)](https://github.com/antoine-lemay/Modbus_dataset)
- [Lemay &amp; Fernandez, CSET '16 (USENIX)](https://www.usenix.org/conference/cset16/workshop-program/presentation/lemay)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (6)</summary>

- `data/lemay-scada-modbus-cset2016/Modbus_polling_only_6RTU(2).pcap`
- `data/lemay-scada-modbus-cset2016/run1_3rtu_2s.pcap`
- `data/lemay-scada-modbus-cset2016/run1_6rtu(1).pcap`
- `data/lemay-scada-modbus-cset2016/run1_12rtu(1).pcap`
- `data/lemay-scada-modbus-cset2016/run8.pcap`
- `data/lemay-scada-modbus-cset2016/run11.pcap`

</details>
