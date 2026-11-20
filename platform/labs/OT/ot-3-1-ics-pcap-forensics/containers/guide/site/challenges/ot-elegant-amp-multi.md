# ELEGANT — amplification DoS against multiple PLCs

**Process control &amp; PLC testbeds** · **Expert** · 0.0 MB · 0 capture file(s)

> Amplification against several PLCs at once.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

The ELEGANT project (University of Coimbra) built a digital-twin testbed of Modbus/TCP programmable logic controllers and attacked it: denial-of-service (flooding and amplification, against one PLC or many) and man-in-the-middle (ARP poisoning, then the full attack chain). Each scenario was captured as rotating 10 MB files named cap_&lt;n&gt;_&lt;timestamp&gt;.

This challenge is **amplification DoS against multiple PLCs**. Quantify it against the normal-traffic challenge.

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
pcapper 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00001_20210314013327.pcapng' --overview
```

**2. Deep-dive with Pcapper (--modbus)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00001_20210314013327.pcapng' --modbus --ot-commands
```

**3. Threats and timeline with Pcapper**

```bash
pcapper 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00001_20210314013327.pcapng' --threats --scan
```

**4. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00001_20210314013327.pcapng' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00001_20210314013327.pcapng'
tshark -r 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00001_20210314013327.pcapng' -q -z io,phs | head -40
```

**2. Map the Modbus/TCP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00001_20210314013327.pcapng' -Y mbtcp -T fields -e ip.src -e ip.dst -e mbtcp.unit_id -e modbus.func_code | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag writes (FC 5/6/15/16/22/23), diagnostics (FC 8 — restart / force-listen-only), device identification (FC 43/14, recon) and Schneider UMAS (FC 90, engineering).

```bash
tshark -r 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00001_20210314013327.pcapng' -Y 'modbus.func_code in {5, 6, 15, 16, 22, 23, 8, 43, 90}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Measure the attack**

Packets per second, who sends them, and how far the Modbus exchange is crowded out.

```bash
tshark -r 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00001_20210314013327.pcapng' -q -z io,stat,1 | head -40
tshark -r 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00001_20210314013327.pcapng' -q -z conv,ip | head -15
tshark -r 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00001_20210314013327.pcapng' -Y 'tcp.flags.syn == 1 && tcp.flags.ack == 0' -T fields -e ip.src | sort | uniq -c | sort -rn | head
```

**5. Does the PLC still answer?**

Compare Modbus request/response pairs and response gaps with the normal-traffic challenge.

```bash
tshark -r 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00001_20210314013327.pcapng' -Y mbtcp -T fields -e frame.time_relative -e ip.src -e ip.dst -e modbus.func_code | head -40
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

Labelled by the dataset as amplification DoS against multiple PLCs (folder multiple_amp_…). Expected answer: the attacker, the window, the mechanism and the measured effect on Modbus.

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Read Holding Registers ×55809; dangerous-operation matches: 0 for the Modbus/TCP filter (55,809 Modbus/TCP packets present, so the zero is real); top conversations in cap_00265_20210314015502.pcapng: 192.168.10.2↔192.168.20.5 (13,965 pkts), 192.168.10.2↔192.168.20.4 (13,964 pkts), 192.168.10.2↔192.168.20.2 (13,961 pkts) (basis: 3 of 265 capture file(s), first 300,000 packets each, smallest files carrying Modbus/TCP chosen)

_Dataset credit: Sousa, B.; Arieiro, M.; Pereira, V.; Cruz, T. (University of Coimbra) (2021) — doi:10.21227/mewp-g646 · License: CC BY 4.0._

</details>

## Dataset & credit

**Sousa, B.; Arieiro, M.; Pereira, V.; Cruz, T. (University of Coimbra) (2021) — doi:10.21227/mewp-g646** — license: CC BY 4.0

- [Dataset source — ELEGANT — DoS and man-in-the-middle attacks on PLCs](https://ieee-dataport.org/open-access/denial-service-and-man-middle-attacks-programmable-logic-controllers)
- [DOI 10.21227/mewp-g646](https://doi.org/10.21227/mewp-g646)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (265)</summary>

- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00001_20210314013327.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00002_20210314013735.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00003_20210314013745.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00004_20210314013755.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00005_20210314013804.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00006_20210314013814.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00007_20210314013824.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00008_20210314013834.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00009_20210314013843.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00010_20210314013853.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00011_20210314013903.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00012_20210314013912.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00013_20210314013922.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00014_20210314013932.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00015_20210314013942.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00016_20210314013951.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00017_20210314014001.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00018_20210314014011.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00019_20210314014020.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00020_20210314014417.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00021_20210314014418.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00022_20210314014420.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00023_20210314014421.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00024_20210314014423.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00025_20210314014424.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00026_20210314014426.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00027_20210314014427.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00028_20210314014429.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00029_20210314014430.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00030_20210314014432.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00031_20210314014433.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00032_20210314014435.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00033_20210314014436.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00034_20210314014438.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00035_20210314014439.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00036_20210314014441.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00037_20210314014442.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00038_20210314014444.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00039_20210314014445.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00040_20210314014447.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00041_20210314014449.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00042_20210314014450.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00043_20210314014452.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00044_20210314014454.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00045_20210314014455.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00046_20210314014456.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00047_20210314014458.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00048_20210314014459.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00049_20210314014501.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00050_20210314014503.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00051_20210314014504.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00052_20210314014505.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00053_20210314014507.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00054_20210314014509.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00055_20210314014510.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00056_20210314014512.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00057_20210314014514.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00058_20210314014515.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00059_20210314014517.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00060_20210314014518.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00061_20210314014520.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00062_20210314014521.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00063_20210314014523.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00064_20210314014524.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00065_20210314014526.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00066_20210314014527.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00067_20210314014529.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00068_20210314014530.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00069_20210314014532.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00070_20210314014533.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00071_20210314014535.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00072_20210314014536.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00073_20210314014538.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00074_20210314014540.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00075_20210314014541.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00076_20210314014543.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00077_20210314014544.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00078_20210314014546.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00079_20210314014548.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00080_20210314014549.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00081_20210314014551.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00082_20210314014553.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00083_20210314014554.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00084_20210314014556.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00085_20210314014558.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00086_20210314014559.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00087_20210314014601.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00088_20210314014602.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00089_20210314014604.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00090_20210314014605.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00091_20210314014607.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00092_20210314014608.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00093_20210314014610.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00094_20210314014611.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00095_20210314014613.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00096_20210314014614.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00097_20210314014616.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00098_20210314014617.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00099_20210314014619.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00100_20210314014620.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00101_20210314014622.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00102_20210314014623.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00103_20210314014625.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00104_20210314014626.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00105_20210314014627.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00106_20210314014629.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00107_20210314014630.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00108_20210314014632.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00109_20210314014633.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00110_20210314014635.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00111_20210314014636.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00112_20210314014638.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00113_20210314014639.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00114_20210314014641.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00115_20210314014642.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00116_20210314014644.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00117_20210314014645.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00118_20210314014647.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00119_20210314014648.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00120_20210314014650.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00121_20210314014651.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00122_20210314014653.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00123_20210314014654.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00124_20210314014656.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00125_20210314014657.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00126_20210314014659.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00127_20210314014700.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00128_20210314014702.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00129_20210314014703.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00130_20210314014705.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00131_20210314014706.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00132_20210314014708.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00133_20210314014709.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00134_20210314014710.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00135_20210314014712.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00136_20210314014714.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00137_20210314014715.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00138_20210314014717.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00139_20210314014718.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00140_20210314014720.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00141_20210314014721.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00142_20210314014821.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00143_20210314015157.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00144_20210314015159.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00145_20210314015200.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00146_20210314015202.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00147_20210314015203.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00148_20210314015205.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00149_20210314015206.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00150_20210314015208.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00151_20210314015209.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00152_20210314015211.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00153_20210314015212.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00154_20210314015213.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00155_20210314015215.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00156_20210314015217.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00157_20210314015218.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00158_20210314015220.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00159_20210314015221.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00160_20210314015223.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00161_20210314015224.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00162_20210314015226.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00163_20210314015227.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00164_20210314015229.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00165_20210314015230.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00166_20210314015232.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00167_20210314015234.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00168_20210314015235.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00169_20210314015237.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00170_20210314015239.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00171_20210314015240.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00172_20210314015242.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00173_20210314015243.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00174_20210314015245.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00175_20210314015247.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00176_20210314015248.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00177_20210314015250.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00178_20210314015252.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00179_20210314015253.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00180_20210314015255.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00181_20210314015256.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00182_20210314015258.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00183_20210314015259.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00184_20210314015301.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00185_20210314015302.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00186_20210314015304.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00187_20210314015305.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00188_20210314015307.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00189_20210314015308.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00190_20210314015310.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00191_20210314015311.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00192_20210314015313.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00193_20210314015314.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00194_20210314015316.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00195_20210314015317.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00196_20210314015319.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00197_20210314015320.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00198_20210314015322.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00199_20210314015323.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00200_20210314015325.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00201_20210314015327.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00202_20210314015328.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00203_20210314015330.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00204_20210314015331.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00205_20210314015333.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00206_20210314015334.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00207_20210314015336.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00208_20210314015337.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00209_20210314015339.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00210_20210314015340.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00211_20210314015342.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00212_20210314015343.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00213_20210314015345.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00214_20210314015346.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00215_20210314015348.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00216_20210314015349.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00217_20210314015351.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00218_20210314015352.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00219_20210314015354.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00220_20210314015355.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00221_20210314015357.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00222_20210314015358.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00223_20210314015400.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00224_20210314015401.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00225_20210314015403.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00226_20210314015404.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00227_20210314015406.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00228_20210314015407.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00229_20210314015409.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00230_20210314015410.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00231_20210314015412.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00232_20210314015413.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00233_20210314015415.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00234_20210314015416.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00235_20210314015418.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00236_20210314015419.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00237_20210314015421.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00238_20210314015422.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00239_20210314015423.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00240_20210314015425.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00241_20210314015426.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00242_20210314015428.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00243_20210314015429.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00244_20210314015431.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00245_20210314015432.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00246_20210314015434.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00247_20210314015435.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00248_20210314015437.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00249_20210314015438.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00250_20210314015440.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00251_20210314015441.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00252_20210314015443.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00253_20210314015444.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00254_20210314015446.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00255_20210314015447.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00256_20210314015449.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00257_20210314015450.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00258_20210314015452.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00259_20210314015453.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00260_20210314015455.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00261_20210314015456.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00262_20210314015458.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00263_20210314015459.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00264_20210314015501.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/multiple_amp_0130_0200/capture/cap_00265_20210314015502.pcapng`

</details>
