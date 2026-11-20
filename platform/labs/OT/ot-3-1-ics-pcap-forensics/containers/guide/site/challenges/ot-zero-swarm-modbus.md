# Zero-SWARM — Modbus normal, flooding and Nmap

**Process control &amp; PLC testbeds** · **Easy** · 0.0 MB · 0 capture file(s)

> Normal Modbus/TCP operation plus flooding and Nmap scanning from the Zero-SWARM project.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Normal Modbus/TCP operation plus flooding and Nmap scanning from the Zero-SWARM project.

Modbus/TCP captures from the Zero-SWARM project: normal operation plus flooding and Nmap scanning attacks.

## Objectives

- Identify devices and protocol roles.
- Find and characterize the malicious activity.
- Use the dataset's labels/companion files to check yourself.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py zero-swarm-modbus
```

- **[Zero-SWARM — Modbus normal and malicious traffic](../DATASETS.md#zero-swarm-modbus)** (`zero-swarm-modbus`), ~0.27 GB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (67.5 MB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/zero-swarm-modbus.tar.part000) (67.5 MB)
  - **Original source:** [zenodo.org/records/15082260](https://zenodo.org/records/15082260) · [doi:10.5281/zenodo.15082260](https://doi.org/10.5281/zenodo.15082260)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/zero-swarm-modbus/ZeroSWARM Normal data_v2.pcap' --overview
```

**2. Deep-dive with Pcapper (--modbus)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/zero-swarm-modbus/ZeroSWARM Normal data_v2.pcap' --modbus --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/zero-swarm-modbus/ZeroSWARM Normal data_v2.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/zero-swarm-modbus/ZeroSWARM Normal data_v2.pcap'
tshark -r 'data/zero-swarm-modbus/ZeroSWARM Normal data_v2.pcap' -q -z io,phs | head -40
```

**2. Map the Modbus/TCP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/zero-swarm-modbus/ZeroSWARM Normal data_v2.pcap' -Y mbtcp -T fields -e ip.src -e ip.dst -e mbtcp.unit_id -e modbus.func_code | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag writes (FC 5/6/15/16/22/23), diagnostics (FC 8 — restart / force-listen-only), device identification (FC 43/14, recon) and Schneider UMAS (FC 90, engineering).

```bash
tshark -r 'data/zero-swarm-modbus/ZeroSWARM Normal data_v2.pcap' -Y 'modbus.func_code in {5, 6, 15, 16, 22, 23, 8, 43, 90}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

## Hints

<details><summary>Hint 1</summary>

Look for label files (CSV/JSON/logs) next to the captures — they are the answer key.

</details>

<details><summary>Hint 2</summary>

Compare attack captures against the clean/normal ones.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

The dataset's bundled labels and companion files are the authoritative answer key; the computed evidence below summarizes what the packets show.

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Read Discrete Inputs ×53365, Write Multiple Coils ×53362, Read Input Registers ×53362, Read Holding Registers ×53362, Write Multiple Registers ×53362; dangerous-operation matches: 106724 (top sources: 192.168.88.201 ×53362, 192.168.88.31 ×32560, 192.168.88.100 ×20802); top conversations in [Zero-SWARM] Flooding Attack_v1.pcap: 192.168.88.100↔192.168.88.201 (69,546 pkts), 192.168.88.100↔224.0.0.251 (12 pkts), 192.168.88.100↔239.255.255.250 (11 pkts) (basis: 3 of 4 capture file(s), first 300,000 packets each, smallest files carrying Modbus/TCP chosen)

_Dataset credit: Lazaridis, George; Mpatziakas, Asterios (2025) — doi:10.5281/zenodo.15082260 · License: CC BY 4.0._

</details>

## Dataset & credit

**Lazaridis, George; Mpatziakas, Asterios (2025) — doi:10.5281/zenodo.15082260** — license: CC BY 4.0

- [Dataset source — Zero-SWARM — Modbus normal and malicious traffic](https://zenodo.org/records/15082260)
- [DOI 10.5281/zenodo.15082260](https://doi.org/10.5281/zenodo.15082260)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (4)</summary>

- `data/zero-swarm-modbus/ZeroSWARM Normal data_v2.pcap`
- `data/zero-swarm-modbus/ZeroSWARM Normal data_v2b.pcap`
- `data/zero-swarm-modbus/[Zero-SWARM] Flooding Attack_v1.pcap`
- `data/zero-swarm-modbus/[Zero-SWARM] Nmap_v1.pcap`

</details>
