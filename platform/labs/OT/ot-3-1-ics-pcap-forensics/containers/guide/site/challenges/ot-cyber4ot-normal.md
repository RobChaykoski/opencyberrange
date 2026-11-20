# Cyber4OT — normal OT activity (switch and PLC port)

**Process control &amp; PLC testbeds** · **Easy** · 0.0 MB · 0 capture file(s)

> Normal Modbus/TCP operation captured at the central switch (001–003) and at the PLC port (069–071).

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Cyber4OT (Warsaw University of Technology testbed) records an OT network's normal activity and a full attack: reconnaissance, then disconnection of the legitimate Modbus/TCP session and PLC hijacking. This challenge covers one band of the dataset's 96 traces, as described in its README.

Normal Modbus/TCP operation captured at the central switch (001–003) and at the PLC port (069–071).

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
pcapper 'data/cyber4ot/data/traces/Cyber4OT_001.pcapng' --overview
```

**2. Deep-dive with Pcapper (--modbus)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/cyber4ot/data/traces/Cyber4OT_001.pcapng' --modbus --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/cyber4ot/data/traces/Cyber4OT_001.pcapng' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Open a representative trace**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/cyber4ot/data/traces/Cyber4OT_001.pcapng'
tshark -r 'data/cyber4ot/data/traces/Cyber4OT_001.pcapng' -q -z io,phs | head -40
```

**2. Map the Modbus/TCP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/cyber4ot/data/traces/Cyber4OT_001.pcapng' -Y mbtcp -T fields -e ip.src -e ip.dst -e mbtcp.unit_id -e modbus.func_code | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag writes (FC 5/6/15/16/22/23), diagnostics (FC 8 — restart / force-listen-only), device identification (FC 43/14, recon) and Schneider UMAS (FC 90, engineering).

```bash
tshark -r 'data/cyber4ot/data/traces/Cyber4OT_001.pcapng' -Y 'modbus.func_code in {5, 6, 15, 16, 22, 23, 8, 43, 90}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
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

Your baseline: steady master↔PLC Modbus polling.

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Read Input Registers ×10772, Write Multiple Registers ×3614; dangerous-operation matches: 3614 (top sources: 192.168.127.20 ×1807, 192.168.127.21 ×1807); top conversations in Cyber4OT_069.pcapng: 192.168.127.20↔192.168.127.21 (2,718 pkts), 192.168.127.21↔192.168.127.6 (890 pkts), 192.168.127.127↔192.168.127.6 (11 pkts) (basis: 3 of 6 capture file(s), first 300,000 packets each, smallest files carrying Modbus/TCP chosen)

_Dataset credit: Cabaj, K.; Plamowski, S.; Chaber, P.; Ławryńczuk, M.; Marusak, P.; Nebeluk, R.; Wojtulewicz, A.; Zarzycki, K. (2025) — doi:10.5281/zenodo.15005190 · License: CC BY-NC 4.0._

</details>

## Dataset & credit

**Cabaj, K.; Plamowski, S.; Chaber, P.; Ławryńczuk, M.; Marusak, P.; Nebeluk, R.; Wojtulewicz, A.; Zarzycki, K. (2025) — doi:10.5281/zenodo.15005190** — license: CC BY-NC 4.0

- [Dataset source — Cyber4OT: ICS network traces containing normal activity and ](https://zenodo.org/records/15005190)
- [DOI 10.5281/zenodo.15005190](https://doi.org/10.5281/zenodo.15005190)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (6)</summary>

- `data/cyber4ot/data/traces/Cyber4OT_001.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_002.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_003.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_069.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_070.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_071.pcapng`

</details>
