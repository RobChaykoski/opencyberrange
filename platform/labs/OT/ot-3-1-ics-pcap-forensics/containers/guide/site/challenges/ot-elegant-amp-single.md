# ELEGANT — amplification DoS against one PLC

**Process control &amp; PLC testbeds** · **Hard** · 0.0 MB · 0 capture file(s)

> An amplification attack against a single PLC, in two trial runs.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

The ELEGANT project (University of Coimbra) built a digital-twin testbed of Modbus/TCP programmable logic controllers and attacked it: denial-of-service (flooding and amplification, against one PLC or many) and man-in-the-middle (ARP poisoning, then the full attack chain). Each scenario was captured as rotating 10 MB files named cap_&lt;n&gt;_&lt;timestamp&gt;.

This challenge is **amplification DoS against one PLC**. Quantify it against the normal-traffic challenge.

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
pcapper 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00485_20210313201342.pcapng' --overview
```

**2. Deep-dive with Pcapper (--modbus)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00485_20210313201342.pcapng' --modbus --ot-commands
```

**3. Threats and timeline with Pcapper**

```bash
pcapper 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00485_20210313201342.pcapng' --threats --scan
```

**4. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00485_20210313201342.pcapng' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00485_20210313201342.pcapng'
tshark -r 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00485_20210313201342.pcapng' -q -z io,phs | head -40
```

**2. Map the Modbus/TCP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00485_20210313201342.pcapng' -Y mbtcp -T fields -e ip.src -e ip.dst -e mbtcp.unit_id -e modbus.func_code | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag writes (FC 5/6/15/16/22/23), diagnostics (FC 8 — restart / force-listen-only), device identification (FC 43/14, recon) and Schneider UMAS (FC 90, engineering).

```bash
tshark -r 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00485_20210313201342.pcapng' -Y 'modbus.func_code in {5, 6, 15, 16, 22, 23, 8, 43, 90}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Measure the attack**

Packets per second, who sends them, and how far the Modbus exchange is crowded out.

```bash
tshark -r 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00485_20210313201342.pcapng' -q -z io,stat,1 | head -40
tshark -r 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00485_20210313201342.pcapng' -q -z conv,ip | head -15
tshark -r 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00485_20210313201342.pcapng' -Y 'tcp.flags.syn == 1 && tcp.flags.ack == 0' -T fields -e ip.src | sort | uniq -c | sort -rn | head
```

**5. Does the PLC still answer?**

Compare Modbus request/response pairs and response gaps with the normal-traffic challenge.

```bash
tshark -r 'data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00485_20210313201342.pcapng' -Y mbtcp -T fields -e frame.time_relative -e ip.src -e ip.dst -e modbus.func_code | head -40
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

Labelled by the dataset as amplification DoS against one PLC (folder single_amp_t…). Expected answer: the attacker, the window, the mechanism and the measured effect on Modbus.

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Read Holding Registers ×68357; dangerous-operation matches: 0 for the Modbus/TCP filter (68,357 Modbus/TCP packets present, so the zero is real); top conversations in cap_00842_20210313204406.pcapng: 192.168.10.2↔192.168.12.2 (38,316 pkts), 192.168.10.2↔192.168.11.2 (38,314 pkts) (basis: 3 of 359 capture file(s), first 300,000 packets each, smallest files carrying Modbus/TCP chosen)

_Dataset credit: Sousa, B.; Arieiro, M.; Pereira, V.; Cruz, T. (University of Coimbra) (2021) — doi:10.21227/mewp-g646 · License: CC BY 4.0._

</details>

## Dataset & credit

**Sousa, B.; Arieiro, M.; Pereira, V.; Cruz, T. (University of Coimbra) (2021) — doi:10.21227/mewp-g646** — license: CC BY 4.0

- [Dataset source — ELEGANT — DoS and man-in-the-middle attacks on PLCs](https://ieee-dataport.org/open-access/denial-service-and-man-middle-attacks-programmable-logic-controllers)
- [DOI 10.21227/mewp-g646](https://doi.org/10.21227/mewp-g646)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (359)</summary>

- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00485_20210313201342.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00486_20210313202103.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00487_20210313202104.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00488_20210313202105.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00489_20210313202106.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00490_20210313202106.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00491_20210313202107.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00492_20210313202109.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00493_20210313202110.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00494_20210313202111.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00495_20210313202112.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00496_20210313202113.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00497_20210313202114.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00498_20210313202115.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00499_20210313202116.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00500_20210313202117.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00501_20210313202118.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00502_20210313202119.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00503_20210313202120.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00504_20210313202121.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00505_20210313202122.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00506_20210313202124.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00507_20210313202125.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00508_20210313202126.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00509_20210313202127.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00510_20210313202128.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00511_20210313202129.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00512_20210313202130.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00513_20210313202131.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00514_20210313202132.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00515_20210313202133.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00516_20210313202134.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00517_20210313202136.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00518_20210313202137.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00519_20210313202138.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00520_20210313202139.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00521_20210313202140.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00522_20210313202141.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00523_20210313202142.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00524_20210313202143.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00525_20210313202144.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00526_20210313202145.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00527_20210313202146.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00528_20210313202147.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00529_20210313202148.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00530_20210313202149.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00531_20210313202150.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00532_20210313202151.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00533_20210313202153.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00534_20210313202154.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00535_20210313202155.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00536_20210313202156.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00537_20210313202157.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00538_20210313202158.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00539_20210313202159.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00540_20210313202200.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00541_20210313202201.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00542_20210313202202.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00543_20210313202203.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00544_20210313202204.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00545_20210313202205.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00546_20210313202206.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00547_20210313202207.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00548_20210313202208.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00549_20210313202210.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00550_20210313202211.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00551_20210313202212.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00552_20210313202213.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00553_20210313202214.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00554_20210313202215.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00555_20210313202216.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00556_20210313202217.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00557_20210313202218.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00558_20210313202219.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00559_20210313202220.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00560_20210313202221.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00561_20210313202222.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00562_20210313202223.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00563_20210313202224.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00564_20210313202225.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00565_20210313202226.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00566_20210313202227.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00567_20210313202228.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00568_20210313202229.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00569_20210313202230.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00570_20210313202232.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00571_20210313202233.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00572_20210313202234.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00573_20210313202235.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00574_20210313202236.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00575_20210313202237.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00576_20210313202238.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00577_20210313202239.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00578_20210313202240.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00579_20210313202241.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00580_20210313202242.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00581_20210313202243.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00582_20210313202244.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00583_20210313202245.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00584_20210313202246.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00585_20210313202247.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00586_20210313202248.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00587_20210313202249.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00588_20210313202250.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00589_20210313202251.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00590_20210313202252.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00591_20210313202253.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00592_20210313202254.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00593_20210313202255.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00594_20210313202256.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00595_20210313202257.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00596_20210313202258.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00597_20210313202259.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00598_20210313202300.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00599_20210313202301.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00600_20210313202302.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00601_20210313202303.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00602_20210313202304.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00603_20210313202305.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00604_20210313202306.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00605_20210313202307.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00606_20210313202308.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00607_20210313202309.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00608_20210313202310.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00609_20210313202311.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00610_20210313202312.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00611_20210313202313.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00612_20210313202314.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00613_20210313202315.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00614_20210313202316.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00615_20210313202317.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00616_20210313202318.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00617_20210313202319.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00618_20210313202320.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00619_20210313202321.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00620_20210313202322.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00621_20210313202323.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00622_20210313202324.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00623_20210313202325.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00624_20210313202326.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00625_20210313202327.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00626_20210313202328.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00627_20210313202329.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00628_20210313202330.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00629_20210313202331.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00630_20210313202332.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00631_20210313202333.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00632_20210313202334.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00633_20210313202335.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00634_20210313202336.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00635_20210313202337.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00636_20210313202338.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00637_20210313202339.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00638_20210313202340.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00639_20210313202341.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00640_20210313202342.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00641_20210313202343.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00642_20210313202344.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00643_20210313202345.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00644_20210313202346.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00645_20210313202347.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00646_20210313202348.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00647_20210313202349.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00648_20210313202350.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00649_20210313202351.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00650_20210313202352.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00651_20210313202353.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00652_20210313202354.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00653_20210313202355.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00654_20210313202356.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00655_20210313202357.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00656_20210313202358.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00657_20210313202359.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00658_20210313202400.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00659_20210313202401.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00660_20210313202402.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t1/cap_00661_20210313202403.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00661_20210313202403.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00662_20210313202914.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00663_20210313202915.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00664_20210313202916.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00665_20210313202916.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00666_20210313202917.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00667_20210313202918.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00668_20210313202919.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00669_20210313202921.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00670_20210313202922.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00671_20210313202923.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00672_20210313202924.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00673_20210313202925.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00674_20210313202926.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00675_20210313202927.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00676_20210313202928.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00677_20210313202929.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00678_20210313202930.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00679_20210313202931.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00680_20210313202932.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00681_20210313202933.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00682_20210313202934.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00683_20210313202935.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00684_20210313202936.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00685_20210313202937.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00686_20210313202938.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00687_20210313202939.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00688_20210313202940.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00689_20210313202941.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00690_20210313202942.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00691_20210313202943.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00692_20210313202944.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00693_20210313202945.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00694_20210313202946.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00695_20210313202947.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00696_20210313202948.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00697_20210313202949.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00698_20210313202950.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00699_20210313202951.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00700_20210313202952.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00701_20210313202953.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00702_20210313202955.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00703_20210313202956.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00704_20210313202957.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00705_20210313202958.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00706_20210313202959.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00707_20210313203000.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00708_20210313203001.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00709_20210313203002.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00710_20210313203003.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00711_20210313203004.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00712_20210313203005.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00713_20210313203006.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00714_20210313203007.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00715_20210313203008.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00716_20210313203009.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00717_20210313203010.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00718_20210313203011.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00719_20210313203012.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00720_20210313203013.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00721_20210313203014.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00722_20210313203015.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00723_20210313203016.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00724_20210313203017.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00725_20210313203018.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00726_20210313203019.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00727_20210313203020.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00728_20210313203021.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00729_20210313203022.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00730_20210313203023.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00731_20210313203024.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00732_20210313203025.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00733_20210313203026.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00734_20210313203027.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00735_20210313203028.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00736_20210313203029.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00737_20210313203029.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00738_20210313203031.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00739_20210313203032.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00740_20210313203032.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00741_20210313203033.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00742_20210313203034.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00743_20210313203035.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00744_20210313203036.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00745_20210313203037.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00746_20210313203038.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00747_20210313203039.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00748_20210313203040.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00749_20210313203041.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00750_20210313203042.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00751_20210313203043.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00752_20210313203044.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00753_20210313203045.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00754_20210313203046.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00755_20210313203047.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00756_20210313203048.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00757_20210313203049.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00758_20210313203050.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00759_20210313203051.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00760_20210313203052.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00761_20210313203053.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00762_20210313203054.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00763_20210313203055.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00764_20210313203056.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00765_20210313203057.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00766_20210313203058.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00767_20210313203059.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00768_20210313203100.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00769_20210313203101.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00770_20210313203102.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00771_20210313203103.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00772_20210313203104.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00773_20210313203105.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00774_20210313203106.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00775_20210313203107.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00776_20210313203108.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00777_20210313203109.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00778_20210313203110.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00779_20210313203111.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00780_20210313203112.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00781_20210313203113.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00782_20210313203114.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00783_20210313203115.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00784_20210313203116.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00785_20210313203117.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00786_20210313203118.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00787_20210313203119.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00788_20210313203120.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00789_20210313203121.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00790_20210313203122.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00791_20210313203123.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00792_20210313203124.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00793_20210313203125.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00794_20210313203126.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00795_20210313203127.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00796_20210313203128.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00797_20210313203129.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00798_20210313203130.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00799_20210313203131.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00800_20210313203132.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00801_20210313203133.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00802_20210313203134.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00803_20210313203135.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00804_20210313203136.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00805_20210313203137.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00806_20210313203138.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00807_20210313203139.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00808_20210313203140.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00809_20210313203141.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00810_20210313203142.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00811_20210313203143.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00812_20210313203144.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00813_20210313203145.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00814_20210313203146.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00815_20210313203147.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00816_20210313203148.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00817_20210313203149.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00818_20210313203150.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00819_20210313203151.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00820_20210313203152.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00821_20210313203153.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00822_20210313203154.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00823_20210313203155.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00824_20210313203156.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00825_20210313203157.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00826_20210313203158.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00827_20210313203159.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00828_20210313203200.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00829_20210313203201.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00830_20210313203202.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00831_20210313203203.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00832_20210313203204.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00833_20210313203205.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00834_20210313203206.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00835_20210313203207.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00836_20210313203208.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00837_20210313203209.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00838_20210313203210.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00839_20210313203211.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00840_20210313203212.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00841_20210313203213.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/DoS/single_amp_t2/cap_00842_20210313204406.pcapng`

</details>
