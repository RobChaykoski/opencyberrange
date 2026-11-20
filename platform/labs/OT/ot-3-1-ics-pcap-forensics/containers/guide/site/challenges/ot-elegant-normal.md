# ELEGANT — normal PLC traffic (baseline)

**Process control &amp; PLC testbeds** · **Easy** · 0.0 MB · 0 capture file(s)

> The PLCs' ordinary Modbus/TCP polling — the yardstick for every ELEGANT attack challenge.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

The ELEGANT project (University of Coimbra) built a digital-twin testbed of Modbus/TCP programmable logic controllers and attacked it: denial-of-service (flooding and amplification, against one PLC or many) and man-in-the-middle (ARP poisoning, then the full attack chain). Each scenario was captured as rotating 10 MB files named cap_&lt;n&gt;_&lt;timestamp&gt;.

This challenge is **normal PLC traffic (baseline)** — the reference for the attack scenarios.

## Objectives

- Identify the Modbus master, the PLCs and any attacker host (IP and MAC).
- Characterize the normal Modbus exchange (function codes, registers, cadence).
- Note anything that would make an attack stand out.
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
pcapper 'data/elegant-plc-dos-mitm/IEEE_DataPort/MiTM/normal_PLC_traffic/cap_00001_20210318035345.pcapng' --overview
```

**2. Deep-dive with Pcapper (--modbus)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/elegant-plc-dos-mitm/IEEE_DataPort/MiTM/normal_PLC_traffic/cap_00001_20210318035345.pcapng' --modbus --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/elegant-plc-dos-mitm/IEEE_DataPort/MiTM/normal_PLC_traffic/cap_00001_20210318035345.pcapng' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/elegant-plc-dos-mitm/IEEE_DataPort/MiTM/normal_PLC_traffic/cap_00001_20210318035345.pcapng'
tshark -r 'data/elegant-plc-dos-mitm/IEEE_DataPort/MiTM/normal_PLC_traffic/cap_00001_20210318035345.pcapng' -q -z io,phs | head -40
```

**2. Map the Modbus/TCP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/elegant-plc-dos-mitm/IEEE_DataPort/MiTM/normal_PLC_traffic/cap_00001_20210318035345.pcapng' -Y mbtcp -T fields -e ip.src -e ip.dst -e mbtcp.unit_id -e modbus.func_code | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag writes (FC 5/6/15/16/22/23), diagnostics (FC 8 — restart / force-listen-only), device identification (FC 43/14, recon) and Schneider UMAS (FC 90, engineering).

```bash
tshark -r 'data/elegant-plc-dos-mitm/IEEE_DataPort/MiTM/normal_PLC_traffic/cap_00001_20210318035345.pcapng' -Y 'modbus.func_code in {5, 6, 15, 16, 22, 23, 8, 43, 90}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
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

Labelled by the dataset as normal PLC traffic (baseline) (folder normal_PLC_traffic). Expected answer: the attacker, the window, the mechanism and the measured effect on Modbus.

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Read Holding Registers ×165492; dangerous-operation matches: 0 for the Modbus/TCP filter (165,492 Modbus/TCP packets present, so the zero is real); top conversations in cap_00006_20210318080920.pcapng: 10.2.32.133↔10.2.33.223 (65,316 pkts) (basis: 3 of 6 capture file(s), first 300,000 packets each, smallest files carrying Modbus/TCP chosen)

_Dataset credit: Sousa, B.; Arieiro, M.; Pereira, V.; Cruz, T. (University of Coimbra) (2021) — doi:10.21227/mewp-g646 · License: CC BY 4.0._

</details>

## Dataset & credit

**Sousa, B.; Arieiro, M.; Pereira, V.; Cruz, T. (University of Coimbra) (2021) — doi:10.21227/mewp-g646** — license: CC BY 4.0

- [Dataset source — ELEGANT — DoS and man-in-the-middle attacks on PLCs](https://ieee-dataport.org/open-access/denial-service-and-man-middle-attacks-programmable-logic-controllers)
- [DOI 10.21227/mewp-g646](https://doi.org/10.21227/mewp-g646)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (6)</summary>

- `data/elegant-plc-dos-mitm/IEEE_DataPort/MiTM/normal_PLC_traffic/cap_00001_20210318035345.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/MiTM/normal_PLC_traffic/cap_00002_20210318044452.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/MiTM/normal_PLC_traffic/cap_00003_20210318053559.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/MiTM/normal_PLC_traffic/cap_00004_20210318062706.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/MiTM/normal_PLC_traffic/cap_00005_20210318071813.pcapng`
- `data/elegant-plc-dos-mitm/IEEE_DataPort/MiTM/normal_PLC_traffic/cap_00006_20210318080920.pcapng`

</details>
