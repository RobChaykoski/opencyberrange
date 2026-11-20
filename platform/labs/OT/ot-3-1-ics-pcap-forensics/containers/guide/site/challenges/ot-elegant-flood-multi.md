# ELEGANT — flood against multiple PLCs

**Process control &amp; PLC testbeds** · **Hard** · 0.0 MB · 0 capture file(s)

> A flood spread over several PLCs at once.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

The ELEGANT project (University of Coimbra) built a digital-twin testbed of Modbus/TCP programmable logic controllers and attacked it: denial-of-service (flooding and amplification, against one PLC or many) and man-in-the-middle (ARP poisoning, then the full attack chain). Each scenario was captured as rotating 10 MB files named cap_&lt;n&gt;_&lt;timestamp&gt;.

This challenge is **flood against multiple PLCs**. Quantify it against the normal-traffic challenge.

## Objectives

- Identify the Modbus master, the PLCs and any attacker host (IP and MAC).
- Find the attack, its start and its source.
- Measure the impact on the Modbus exchange (latency, gaps, failed requests).
- Write a detection that would fire on this scenario but not on normal traffic.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py elegant-plc-dos-mitm
```

- **[ELEGANT — DoS and man-in-the-middle attacks on PLCs](../DATASETS.md#elegant-plc-dos-mitm)** (`elegant-plc-dos-mitm`), ~19.06 GB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 2 parts (3.12 GB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/elegant-plc-dos-mitm.tar.part000) (1.90 GB) · [part001](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/elegant-plc-dos-mitm.tar.part001) (1.22 GB)
  - **Original source:** [ieee-dataport.org/open-access/denial-service-and-man-midd…](https://ieee-dataport.org/open-access/denial-service-and-man-middle-attacks-programmable-logic-controllers) · [doi:10.21227/mewp-g646](https://doi.org/10.21227/mewp-g646)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00001_20210314005755.pcapng' --overview
```

**2. Deep-dive with Pcapper (--modbus)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00001_20210314005755.pcapng' --modbus --ot-commands
```

**3. Threats and timeline with Pcapper**

```bash
pcapper 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00001_20210314005755.pcapng' --threats --scan
```

**4. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00001_20210314005755.pcapng' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00001_20210314005755.pcapng'
tshark -r 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00001_20210314005755.pcapng' -q -z io,phs | head -40
```

**2. Map the Modbus/TCP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00001_20210314005755.pcapng' -Y mbtcp -T fields -e ip.src -e ip.dst -e mbtcp.unit_id -e modbus.func_code | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag writes (FC 5/6/15/16/22/23), diagnostics (FC 8 — restart / force-listen-only), device identification (FC 43/14, recon) and Schneider UMAS (FC 90, engineering).

```bash
tshark -r 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00001_20210314005755.pcapng' -Y 'modbus.func_code in {5, 6, 15, 16, 22, 23, 8, 43, 90}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Measure the attack**

Packets per second, who sends them, and how far the Modbus exchange is crowded out.

```bash
tshark -r 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00001_20210314005755.pcapng' -q -z io,stat,1 | head -40
tshark -r 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00001_20210314005755.pcapng' -q -z conv,ip | head -15
tshark -r 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00001_20210314005755.pcapng' -Y 'tcp.flags.syn == 1 && tcp.flags.ack == 0' -T fields -e ip.src | sort | uniq -c | sort -rn | head
```

**5. Does the PLC still answer?**

Compare Modbus request/response pairs and response gaps with the normal-traffic challenge.

```bash
tshark -r 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00001_20210314005755.pcapng' -Y mbtcp -T fields -e frame.time_relative -e ip.src -e ip.dst -e modbus.func_code | head -40
```

## Hints

<details><summary>Hint 1</summary>

The capture is a series of 10 MB files — mergecap them or work file by file.

</details>

<details><summary>Hint 2</summary>

Diff every number against the normal PLC traffic.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

Labelled by the dataset as flood against multiple PLCs (folder multiple_flood_…). Expected answer: the attacker, the window, the mechanism and the measured effect on Modbus.

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Read Holding Registers ×36969; dangerous-operation matches: 0 for the Modbus/TCP filter (36,969 Modbus/TCP packets present, so the zero is real); top conversations in cap_00244_20210314012538.pcapng: 192.168.10.2↔192.168.20.2 (1,758 pkts), 192.168.10.2↔192.168.20.3 (1,758 pkts), 192.168.10.2↔192.168.20.4 (1,758 pkts) (basis: 3 of 263 capture file(s), first 300,000 packets each, smallest files carrying Modbus/TCP chosen)

_Dataset credit: Sousa, B.; Arieiro, M.; Pereira, V.; Cruz, T. (University of Coimbra) (2021) — doi:10.21227/mewp-g646 · License: CC BY 4.0._

</details>

## Dataset & credit

**Sousa, B.; Arieiro, M.; Pereira, V.; Cruz, T. (University of Coimbra) (2021) — doi:10.21227/mewp-g646** — license: CC BY 4.0

- [Dataset source — ELEGANT — DoS and man-in-the-middle attacks on PLCs](https://ieee-dataport.org/open-access/denial-service-and-man-middle-attacks-programmable-logic-controllers)
- [DOI 10.21227/mewp-g646](https://doi.org/10.21227/mewp-g646)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (263)</summary>

- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00001_20210314005755.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00001_20210314010944.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00002_20210314010231.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00002_20210314011221.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00003_20210314010240.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00003_20210314011223.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00004_20210314010250.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00004_20210314011224.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00005_20210314010259.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00005_20210314011226.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00006_20210314010309.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00006_20210314011227.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00007_20210314010319.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00007_20210314011229.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00008_20210314010329.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00008_20210314011230.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00009_20210314010338.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00009_20210314011232.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00010_20210314010348.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00010_20210314011234.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00011_20210314010358.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00011_20210314011235.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00012_20210314010407.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00012_20210314011237.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00013_20210314010417.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00013_20210314011238.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00014_20210314010427.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00014_20210314011240.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00015_20210314010437.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00015_20210314011241.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00016_20210314010446.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00016_20210314011243.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00017_20210314010456.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00017_20210314011245.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00018_20210314010506.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00018_20210314011246.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00019_20210314010515.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00019_20210314011248.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00020_20210314011250.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00021_20210314011251.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00022_20210314011253.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00023_20210314011254.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00024_20210314011256.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00025_20210314011258.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00026_20210314011259.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00027_20210314011301.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00028_20210314011303.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00029_20210314011304.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00030_20210314011306.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00031_20210314011307.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00032_20210314011309.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00033_20210314011310.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00034_20210314011312.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00035_20210314011313.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00036_20210314011315.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00037_20210314011316.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00038_20210314011318.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00039_20210314011319.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00040_20210314011321.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00041_20210314011322.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00042_20210314011324.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00043_20210314011325.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00044_20210314011327.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00045_20210314011329.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00046_20210314011331.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00047_20210314011332.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00048_20210314011334.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00049_20210314011335.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00050_20210314011337.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00051_20210314011338.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00052_20210314011340.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00053_20210314011341.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00054_20210314011343.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00055_20210314011345.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00056_20210314011346.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00057_20210314011348.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00058_20210314011349.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00059_20210314011351.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00060_20210314011353.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00061_20210314011354.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00062_20210314011356.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00063_20210314011357.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00064_20210314011359.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00065_20210314011401.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00066_20210314011402.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00067_20210314011404.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00068_20210314011405.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00069_20210314011407.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00070_20210314011408.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00071_20210314011410.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00072_20210314011411.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00073_20210314011413.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00074_20210314011414.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00075_20210314011416.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00076_20210314011417.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00077_20210314011419.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00078_20210314011420.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00079_20210314011422.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00080_20210314011424.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00081_20210314011425.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00082_20210314011427.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00083_20210314011428.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00084_20210314011430.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00085_20210314011431.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00086_20210314011433.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00087_20210314011434.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00088_20210314011436.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00089_20210314011437.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00090_20210314011439.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00091_20210314011440.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00092_20210314011442.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00093_20210314011443.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00094_20210314011445.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00095_20210314011446.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00096_20210314011448.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00097_20210314011450.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00098_20210314011451.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00099_20210314011453.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00100_20210314011454.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00101_20210314011456.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00102_20210314011457.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00103_20210314011459.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00104_20210314011501.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00105_20210314011502.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00106_20210314011504.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00107_20210314011505.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00108_20210314011507.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00109_20210314011509.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00110_20210314011510.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00111_20210314011512.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00112_20210314011513.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00113_20210314011515.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00114_20210314011516.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00115_20210314011518.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00116_20210314011519.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00117_20210314011521.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00118_20210314011523.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00119_20210314011524.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00120_20210314011526.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00121_20210314011918.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00122_20210314011920.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00123_20210314011921.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00124_20210314011923.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00125_20210314011924.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00126_20210314011926.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00127_20210314011927.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00128_20210314011929.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00129_20210314011931.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00130_20210314011932.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00131_20210314011934.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00132_20210314011935.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00133_20210314011937.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00134_20210314011938.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00135_20210314011940.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00136_20210314011941.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00137_20210314011943.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00138_20210314011944.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00139_20210314011946.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00140_20210314011947.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00141_20210314011949.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00142_20210314011950.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00143_20210314011952.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00144_20210314011953.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00145_20210314011955.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00146_20210314011956.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00147_20210314011958.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00148_20210314011959.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00149_20210314012001.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00150_20210314012002.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00151_20210314012004.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00152_20210314012006.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00153_20210314012007.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00154_20210314012009.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00155_20210314012010.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00156_20210314012012.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00157_20210314012013.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00158_20210314012015.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00159_20210314012016.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00160_20210314012018.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00161_20210314012019.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00162_20210314012021.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00163_20210314012022.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00164_20210314012024.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00165_20210314012025.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00166_20210314012027.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00167_20210314012028.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00168_20210314012030.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00169_20210314012031.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00170_20210314012033.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00171_20210314012034.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00172_20210314012036.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00173_20210314012038.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00174_20210314012039.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00175_20210314012041.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00176_20210314012042.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00177_20210314012044.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00178_20210314012045.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00179_20210314012047.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00180_20210314012048.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00181_20210314012050.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00182_20210314012051.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00183_20210314012053.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00184_20210314012054.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00185_20210314012056.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00186_20210314012057.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00187_20210314012059.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00188_20210314012100.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00189_20210314012102.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00190_20210314012104.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00191_20210314012105.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00192_20210314012107.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00193_20210314012108.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00194_20210314012110.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00195_20210314012111.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00196_20210314012113.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00197_20210314012114.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00198_20210314012116.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00199_20210314012118.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00200_20210314012120.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00201_20210314012121.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00202_20210314012123.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00203_20210314012124.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00204_20210314012126.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00205_20210314012127.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00206_20210314012129.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00207_20210314012130.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00208_20210314012132.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00209_20210314012133.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00210_20210314012135.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00211_20210314012136.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00212_20210314012138.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00213_20210314012140.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00214_20210314012141.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00215_20210314012143.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00216_20210314012144.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00217_20210314012146.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00218_20210314012147.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00219_20210314012149.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00220_20210314012150.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00221_20210314012152.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00222_20210314012154.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00223_20210314012155.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00224_20210314012157.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00225_20210314012158.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00226_20210314012200.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00227_20210314012201.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00228_20210314012203.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00229_20210314012204.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00230_20210314012206.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00231_20210314012207.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00232_20210314012209.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00233_20210314012210.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00234_20210314012212.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00235_20210314012213.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00236_20210314012215.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00237_20210314012217.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00238_20210314012218.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00239_20210314012220.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00240_20210314012221.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00241_20210314012223.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00242_20210314012224.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00243_20210314012226.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_flood_0100_0125/capture/cap_00244_20210314012538.pcapng`

</details>
