# Cyber4OT — Nmap full port scans of each device

**Process control &amp; PLC testbeds** · **Medium** · 0.0 MB · 0 capture file(s)

> Full Nmap scans of each discovered device (and the PLC) at five timing templates.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Cyber4OT (Warsaw University of Technology testbed) records an OT network's normal activity and a full attack: reconnaissance, then disconnection of the legitimate Modbus/TCP session and PLC hijacking. This challenge covers one band of the dataset's 96 traces, as described in its README.

Full Nmap scans of each discovered device (and the PLC) at five timing templates.

## Objectives

- Characterize the traffic in this band.
- Identify attacker, technique and targets.
- Explain how you would detect it on a real OT network.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py cyber4ot
```

- **[Cyber4OT: ICS network traces containing normal activity and full attack traffic](../DATASETS.md#cyber4ot)** (`cyber4ot`), ~0.40 GB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (69.0 MB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/cyber4ot.tar.part000) (69.0 MB)
  - **Original source:** [zenodo.org/records/15005190](https://zenodo.org/records/15005190) · [doi:10.5281/zenodo.15005190](https://doi.org/10.5281/zenodo.15005190)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Open a representative trace**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/cyber4ot/data/traces/Cyber4OT_009.pcapng' --overview
```

**2. Profile the scan**

Probe rate, ports and inter-packet timing reveal the Nmap timing template.

```bash
pcapper 'data/cyber4ot/data/traces/Cyber4OT_009.pcapng' --scan
```

**3. Deep-dive with Pcapper (--modbus)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/cyber4ot/data/traces/Cyber4OT_009.pcapng' --modbus --ot-commands
```

**4. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/cyber4ot/data/traces/Cyber4OT_009.pcapng' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Open a representative trace**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/cyber4ot/data/traces/Cyber4OT_009.pcapng'
tshark -r 'data/cyber4ot/data/traces/Cyber4OT_009.pcapng' -q -z io,phs | head -40
```

**2. Map the Modbus/TCP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/cyber4ot/data/traces/Cyber4OT_009.pcapng' -Y mbtcp -T fields -e ip.src -e ip.dst -e mbtcp.unit_id -e modbus.func_code | sort | uniq -c | sort -rn | head -25
```

**3. Profile the scan**

Probe rate, ports and inter-packet timing reveal the Nmap timing template.

```bash
tshark -r 'data/cyber4ot/data/traces/Cyber4OT_009.pcapng' -Y 'tcp.flags.syn==1 && tcp.flags.ack==0' -T fields -e frame.time_relative -e ip.src -e ip.dst -e tcp.dstport | head -30
```

**4. Hunt the dangerous operations**

Flag writes (FC 5/6/15/16/22/23), diagnostics (FC 8 — restart / force-listen-only), device identification (FC 43/14, recon) and Schneider UMAS (FC 90, engineering).

```bash
tshark -r 'data/cyber4ot/data/traces/Cyber4OT_009.pcapng' -Y 'modbus.func_code in {5, 6, 15, 16, 22, 23, 8, 43, 90}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

## Hints

<details><summary>Hint 1</summary>

The dataset README (data/README.txt) describes each trace band — use it to check yourself.

</details>

<details><summary>Hint 2</summary>

Compare against the normal-activity band.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

Per-device full scans — fingerprint the scanner, the targets and each timing template.

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Read Input Registers ×4973, Write Multiple Registers ×2486; dangerous-operation matches: 2486 (top sources: 192.168.127.20 ×1243, 192.168.127.21 ×1243); top conversations in Cyber4OT_081.pcapng: 192.168.127.20↔192.168.127.21 (5,419 pkts), 192.168.127.21↔192.168.127.6 (236 pkts), 192.168.127.126↔192.168.127.21 (76 pkts) (basis: 3 of 65 capture file(s), first 300,000 packets each, smallest files carrying Modbus/TCP chosen)

_Dataset credit: Cabaj, K.; Plamowski, S.; Chaber, P.; Ławryńczuk, M.; Marusak, P.; Nebeluk, R.; Wojtulewicz, A.; Zarzycki, K. (2025) — doi:10.5281/zenodo.15005190 · License: CC BY-NC 4.0._

</details>

## Dataset & credit

**Cabaj, K.; Plamowski, S.; Chaber, P.; Ławryńczuk, M.; Marusak, P.; Nebeluk, R.; Wojtulewicz, A.; Zarzycki, K. (2025) — doi:10.5281/zenodo.15005190** — license: CC BY-NC 4.0

- [Dataset source — Cyber4OT: ICS network traces containing normal activity and ](https://zenodo.org/records/15005190)
- [DOI 10.5281/zenodo.15005190](https://doi.org/10.5281/zenodo.15005190)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (65)</summary>

- `data/cyber4ot/data/traces/Cyber4OT_009.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_010.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_011.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_012.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_013.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_014.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_015.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_016.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_017.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_018.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_019.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_020.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_021.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_022.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_023.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_024.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_025.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_026.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_027.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_028.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_029.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_030.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_031.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_032.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_033.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_034.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_035.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_036.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_037.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_038.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_039.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_040.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_041.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_042.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_043.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_044.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_045.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_046.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_047.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_048.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_049.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_050.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_051.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_052.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_053.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_054.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_055.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_056.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_057.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_058.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_059.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_060.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_061.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_062.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_063.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_064.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_065.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_066.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_067.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_068.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_077.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_078.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_079.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_080.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_081.pcapng`

</details>
