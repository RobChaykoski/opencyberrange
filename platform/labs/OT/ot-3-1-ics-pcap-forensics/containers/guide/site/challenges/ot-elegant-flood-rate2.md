# ELEGANT — flood against one PLC (rate 2)

**Process control &amp; PLC testbeds** · **Medium** · 0.0 MB · 0 capture file(s)

> The same single-PLC flood at the higher rate, in two trial runs.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

The ELEGANT project (University of Coimbra) built a digital-twin testbed of Modbus/TCP programmable logic controllers and attacked it: denial-of-service (flooding and amplification, against one PLC or many) and man-in-the-middle (ARP poisoning, then the full attack chain). Each scenario was captured as rotating 10 MB files named cap_&lt;n&gt;_&lt;timestamp&gt;.

This challenge is **flood against one PLC (rate 2)**. Quantify it against the normal-traffic challenge.

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
pcapper 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00016_20210313195826.pcapng' --overview
```

**2. Deep-dive with Pcapper (--modbus)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00016_20210313195826.pcapng' --modbus --ot-commands
```

**3. Threats and timeline with Pcapper**

```bash
pcapper 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00016_20210313195826.pcapng' --threats --scan
```

**4. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00016_20210313195826.pcapng' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00016_20210313195826.pcapng'
tshark -r 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00016_20210313195826.pcapng' -q -z io,phs | head -40
```

**2. Map the Modbus/TCP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00016_20210313195826.pcapng' -Y mbtcp -T fields -e ip.src -e ip.dst -e mbtcp.unit_id -e modbus.func_code | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag writes (FC 5/6/15/16/22/23), diagnostics (FC 8 — restart / force-listen-only), device identification (FC 43/14, recon) and Schneider UMAS (FC 90, engineering).

```bash
tshark -r 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00016_20210313195826.pcapng' -Y 'modbus.func_code in {5, 6, 15, 16, 22, 23, 8, 43, 90}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Measure the attack**

Packets per second, who sends them, and how far the Modbus exchange is crowded out.

```bash
tshark -r 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00016_20210313195826.pcapng' -q -z io,stat,1 | head -40
tshark -r 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00016_20210313195826.pcapng' -q -z conv,ip | head -15
tshark -r 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00016_20210313195826.pcapng' -Y 'tcp.flags.syn == 1 && tcp.flags.ack == 0' -T fields -e ip.src | sort | uniq -c | sort -rn | head
```

**5. Does the PLC still answer?**

Compare Modbus request/response pairs and response gaps with the normal-traffic challenge.

```bash
tshark -r 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00016_20210313195826.pcapng' -Y mbtcp -T fields -e frame.time_relative -e ip.src -e ip.dst -e modbus.func_code | head -40
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

Labelled by the dataset as flood against one PLC (rate 2) (folder single_flood_rate_2_t…). Expected answer: the attacker, the window, the mechanism and the measured effect on Modbus.

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Read Holding Registers ×29; dangerous-operation matches: 0 for the Modbus/TCP filter (29 Modbus/TCP packets present, so the zero is real); top conversations in cap_00122_20210313200405.pcapng: 192.168.10.2↔192.168.12.2 (7 pkts), 192.168.10.2↔192.168.11.2 (4 pkts), 12.194.211.173↔192.168.10.2 (2 pkts) (basis: 3 of 471 capture file(s), first 300,000 packets each, smallest files carrying Modbus/TCP chosen)

_Dataset credit: Sousa, B.; Arieiro, M.; Pereira, V.; Cruz, T. (University of Coimbra) (2021) — doi:10.21227/mewp-g646 · License: CC BY 4.0._

</details>

## Dataset & credit

**Sousa, B.; Arieiro, M.; Pereira, V.; Cruz, T. (University of Coimbra) (2021) — doi:10.21227/mewp-g646** — license: CC BY 4.0

- [Dataset source — ELEGANT — DoS and man-in-the-middle attacks on PLCs](https://ieee-dataport.org/open-access/denial-service-and-man-middle-attacks-programmable-logic-controllers)
- [DOI 10.21227/mewp-g646](https://doi.org/10.21227/mewp-g646)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (471)</summary>

- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00016_20210313195826.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00017_20210313200245.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00018_20210313200245.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00019_20210313200246.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00020_20210313200247.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00021_20210313200248.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00022_20210313200248.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00023_20210313200249.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00024_20210313200250.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00025_20210313200251.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00026_20210313200251.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00027_20210313200252.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00028_20210313200253.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00029_20210313200254.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00030_20210313200254.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00031_20210313200255.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00032_20210313200256.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00033_20210313200257.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00034_20210313200257.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00035_20210313200258.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00036_20210313200259.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00037_20210313200300.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00038_20210313200301.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00039_20210313200301.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00040_20210313200302.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00041_20210313200303.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00042_20210313200304.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00043_20210313200304.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00044_20210313200305.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00045_20210313200306.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00046_20210313200307.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00047_20210313200307.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00048_20210313200308.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00049_20210313200309.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00050_20210313200310.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00051_20210313200310.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00052_20210313200311.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00053_20210313200312.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00054_20210313200313.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00055_20210313200313.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00056_20210313200314.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00057_20210313200315.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00058_20210313200316.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00059_20210313200317.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00060_20210313200317.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00061_20210313200318.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00062_20210313200319.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00063_20210313200320.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00064_20210313200320.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00065_20210313200321.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00066_20210313200322.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00067_20210313200323.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00068_20210313200323.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00069_20210313200324.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00070_20210313200325.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00071_20210313200326.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00072_20210313200326.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00073_20210313200327.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00074_20210313200328.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00075_20210313200329.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00076_20210313200329.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00077_20210313200330.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00078_20210313200331.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00079_20210313200332.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00080_20210313200333.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00081_20210313200333.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00082_20210313200334.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00083_20210313200335.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00084_20210313200336.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00085_20210313200336.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00086_20210313200337.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00087_20210313200338.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00088_20210313200339.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00089_20210313200339.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00090_20210313200340.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00091_20210313200341.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00092_20210313200342.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00093_20210313200342.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00094_20210313200344.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00095_20210313200344.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00096_20210313200345.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00097_20210313200346.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00098_20210313200346.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00099_20210313200347.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00100_20210313200348.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00101_20210313200349.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00102_20210313200350.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00103_20210313200350.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00104_20210313200351.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00105_20210313200352.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00106_20210313200353.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00107_20210313200353.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00108_20210313200354.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00109_20210313200355.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00110_20210313200356.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00111_20210313200357.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00112_20210313200357.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00113_20210313200358.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00114_20210313200359.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00115_20210313200400.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00116_20210313200400.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00117_20210313200401.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00118_20210313200402.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00119_20210313200403.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00120_20210313200404.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00121_20210313200404.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00122_20210313200405.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00123_20210313200406.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00124_20210313200407.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00125_20210313200408.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00126_20210313200408.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00127_20210313200409.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00128_20210313200410.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00129_20210313200411.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00130_20210313200411.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00131_20210313200412.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00132_20210313200413.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00133_20210313200414.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00134_20210313200414.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00135_20210313200415.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00136_20210313200416.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00137_20210313200417.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00138_20210313200417.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00139_20210313200418.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00140_20210313200419.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00141_20210313200420.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00142_20210313200421.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00143_20210313200421.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00144_20210313200422.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00145_20210313200423.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00146_20210313200424.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00147_20210313200424.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00148_20210313200425.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00149_20210313200426.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00150_20210313200427.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00151_20210313200427.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00152_20210313200428.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00153_20210313200429.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00154_20210313200430.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00155_20210313200430.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00156_20210313200431.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00157_20210313200432.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00158_20210313200433.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00159_20210313200433.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00160_20210313200434.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00161_20210313200435.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00162_20210313200436.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00163_20210313200436.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00164_20210313200437.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00165_20210313200438.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00166_20210313200439.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00167_20210313200440.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00168_20210313200441.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00169_20210313200441.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00170_20210313200442.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00171_20210313200443.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00172_20210313200444.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00173_20210313200444.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00174_20210313200445.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00175_20210313200446.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00176_20210313200447.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00177_20210313200447.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00178_20210313200448.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00179_20210313200449.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00180_20210313200450.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00181_20210313200450.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00182_20210313200451.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00183_20210313200452.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00184_20210313200453.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00185_20210313200454.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00186_20210313200454.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00187_20210313200455.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00188_20210313200456.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00189_20210313200457.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00190_20210313200457.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00191_20210313200459.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00192_20210313200459.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00193_20210313200500.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00194_20210313200501.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00195_20210313200502.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00196_20210313200502.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00197_20210313200503.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00198_20210313200504.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00199_20210313200505.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00200_20210313200505.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00201_20210313200506.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00202_20210313200507.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00203_20210313200508.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00204_20210313200509.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00205_20210313200509.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00206_20210313200510.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00207_20210313200511.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00208_20210313200512.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00209_20210313200512.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00210_20210313200513.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00211_20210313200514.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00212_20210313200515.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00213_20210313200516.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00214_20210313200517.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00215_20210313200517.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00216_20210313200518.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00217_20210313200519.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00218_20210313200520.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00219_20210313200520.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00220_20210313200521.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00221_20210313200522.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00222_20210313200523.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00223_20210313200524.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00224_20210313200524.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00225_20210313200525.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00226_20210313200526.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00227_20210313200527.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00228_20210313200528.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00229_20210313200528.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00230_20210313200529.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00231_20210313200530.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00232_20210313200531.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00233_20210313200531.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00234_20210313200532.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00235_20210313200533.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00236_20210313200534.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00237_20210313200534.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00238_20210313200535.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00239_20210313200536.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00240_20210313200537.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00241_20210313200538.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00242_20210313200538.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00243_20210313200539.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00244_20210313200540.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00245_20210313200541.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00246_20210313200541.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00247_20210313200542.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00248_20210313200543.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t1/cap_00249_20210313200544.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00249_20210313200544.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00250_20210313201043.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00251_20210313201044.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00252_20210313201044.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00253_20210313201045.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00254_20210313201046.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00255_20210313201047.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00256_20210313201047.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00257_20210313201048.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00258_20210313201049.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00259_20210313201050.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00260_20210313201050.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00261_20210313201051.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00262_20210313201052.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00263_20210313201053.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00264_20210313201053.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00265_20210313201054.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00266_20210313201055.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00267_20210313201056.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00268_20210313201056.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00269_20210313201057.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00270_20210313201058.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00271_20210313201059.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00272_20210313201100.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00273_20210313201100.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00274_20210313201101.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00275_20210313201102.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00276_20210313201103.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00277_20210313201103.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00278_20210313201104.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00279_20210313201105.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00280_20210313201106.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00281_20210313201106.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00282_20210313201107.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00283_20210313201108.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00284_20210313201109.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00285_20210313201109.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00286_20210313201110.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00287_20210313201111.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00288_20210313201112.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00289_20210313201113.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00290_20210313201114.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00291_20210313201114.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00292_20210313201115.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00293_20210313201116.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00294_20210313201117.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00295_20210313201117.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00296_20210313201118.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00297_20210313201119.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00298_20210313201120.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00299_20210313201120.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00300_20210313201121.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00301_20210313201122.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00302_20210313201123.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00303_20210313201123.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00304_20210313201124.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00305_20210313201125.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00306_20210313201126.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00307_20210313201126.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00308_20210313201127.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00309_20210313201128.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00310_20210313201129.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00311_20210313201130.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00312_20210313201130.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00313_20210313201131.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00314_20210313201132.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00315_20210313201133.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00316_20210313201133.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00317_20210313201134.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00318_20210313201135.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00319_20210313201136.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00320_20210313201136.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00321_20210313201137.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00322_20210313201138.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00323_20210313201139.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00324_20210313201139.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00325_20210313201140.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00326_20210313201141.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00327_20210313201142.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00328_20210313201142.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00329_20210313201143.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00330_20210313201144.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00331_20210313201145.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00332_20210313201146.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00333_20210313201146.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00334_20210313201147.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00335_20210313201148.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00336_20210313201149.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00337_20210313201149.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00338_20210313201150.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00339_20210313201151.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00340_20210313201152.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00341_20210313201152.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00342_20210313201153.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00343_20210313201154.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00344_20210313201155.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00345_20210313201155.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00346_20210313201156.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00347_20210313201157.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00348_20210313201158.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00349_20210313201158.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00350_20210313201159.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00351_20210313201200.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00352_20210313201201.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00353_20210313201201.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00354_20210313201202.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00355_20210313201203.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00356_20210313201204.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00357_20210313201205.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00358_20210313201205.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00359_20210313201206.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00360_20210313201207.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00361_20210313201208.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00362_20210313201208.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00363_20210313201209.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00364_20210313201210.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00365_20210313201211.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00366_20210313201211.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00367_20210313201212.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00368_20210313201213.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00369_20210313201214.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00370_20210313201214.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00371_20210313201215.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00372_20210313201216.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00373_20210313201217.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00374_20210313201217.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00375_20210313201218.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00376_20210313201219.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00377_20210313201220.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00378_20210313201221.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00379_20210313201221.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00380_20210313201222.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00381_20210313201223.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00382_20210313201224.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00383_20210313201224.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00384_20210313201225.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00385_20210313201226.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00386_20210313201227.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00387_20210313201227.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00388_20210313201228.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00389_20210313201229.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00390_20210313201230.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00391_20210313201230.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00392_20210313201231.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00393_20210313201232.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00394_20210313201233.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00395_20210313201233.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00396_20210313201234.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00397_20210313201235.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00398_20210313201236.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00399_20210313201237.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00400_20210313201237.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00401_20210313201238.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00402_20210313201239.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00403_20210313201240.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00404_20210313201240.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00405_20210313201241.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00406_20210313201242.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00407_20210313201243.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00408_20210313201243.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00409_20210313201244.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00410_20210313201245.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00411_20210313201246.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00412_20210313201246.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00413_20210313201247.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00414_20210313201248.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00415_20210313201249.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00416_20210313201249.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00417_20210313201250.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00418_20210313201251.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00419_20210313201252.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00420_20210313201253.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00421_20210313201253.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00422_20210313201254.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00423_20210313201255.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00424_20210313201256.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00425_20210313201257.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00426_20210313201257.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00427_20210313201258.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00428_20210313201259.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00429_20210313201300.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00430_20210313201300.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00431_20210313201301.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00432_20210313201302.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00433_20210313201303.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00434_20210313201303.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00435_20210313201304.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00436_20210313201305.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00437_20210313201306.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00438_20210313201306.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00439_20210313201307.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00440_20210313201308.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00441_20210313201309.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00442_20210313201309.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00443_20210313201310.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00444_20210313201311.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00445_20210313201312.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00446_20210313201312.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00447_20210313201313.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00448_20210313201314.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00449_20210313201315.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00450_20210313201316.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00451_20210313201316.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00452_20210313201317.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00453_20210313201318.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00454_20210313201319.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00455_20210313201319.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00456_20210313201320.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00457_20210313201321.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00458_20210313201322.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00459_20210313201322.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00460_20210313201323.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00461_20210313201324.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00462_20210313201325.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00463_20210313201325.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00464_20210313201326.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00465_20210313201327.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00466_20210313201328.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00467_20210313201328.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00468_20210313201329.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00469_20210313201330.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00470_20210313201331.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00471_20210313201332.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00472_20210313201333.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00473_20210313201333.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00474_20210313201334.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00475_20210313201335.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00476_20210313201336.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00477_20210313201336.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00478_20210313201337.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00479_20210313201338.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00480_20210313201339.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00481_20210313201339.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00482_20210313201340.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00483_20210313201341.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00484_20210313201342.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_flood_rate_2_t2/cap_00485_20210313201342.pcapng`

</details>
