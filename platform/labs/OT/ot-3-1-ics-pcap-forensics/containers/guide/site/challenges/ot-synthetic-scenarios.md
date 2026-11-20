# Synthetic OT — benign plant vs. attack scenarios

**Process control &amp; PLC testbeds** · **Easy** · 0.0 MB · 0 capture file(s)

> Small synthetic captures: a benign plant baseline, multi-protocol OT traffic and attack scenarios — a quick warm-up.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Small synthetic captures: a benign plant baseline, multi-protocol OT traffic and attack scenarios — a quick warm-up.

Small synthetic captures shipped with an OT pcap analyzer: a benign plant baseline, multi-protocol OT traffic and attack scenarios.

## Objectives

- Identify devices and protocol roles.
- Find and characterize the malicious activity.
- Use the dataset's labels/companion files to check yourself.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py synthetic-ot-scenarios-lindseynguyen
```

- **[Synthetic OT scenarios — benign plant vs. attack](../DATASETS.md#synthetic-ot-scenarios-lindseynguyen)** (`synthetic-ot-scenarios-lindseynguyen`), ~0.5 MB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (0.5 MB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/synthetic-ot-scenarios-lindseynguyen.tar.part000) (0.5 MB)
  - **Original source:** [github.com/lindseynguyen/ics-pcap-analyzer](https://github.com/lindseynguyen/ics-pcap-analyzer)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/synthetic-ot-scenarios-lindseynguyen/samples/attack_scenarios.pcap' --overview
```

**2. Deep-dive with Pcapper (--modbus)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/synthetic-ot-scenarios-lindseynguyen/samples/attack_scenarios.pcap' --modbus --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/synthetic-ot-scenarios-lindseynguyen/samples/attack_scenarios.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/synthetic-ot-scenarios-lindseynguyen/samples/attack_scenarios.pcap'
tshark -r 'data/synthetic-ot-scenarios-lindseynguyen/samples/attack_scenarios.pcap' -q -z io,phs | head -40
```

**2. Map the Modbus/TCP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/synthetic-ot-scenarios-lindseynguyen/samples/attack_scenarios.pcap' -Y mbtcp -T fields -e ip.src -e ip.dst -e mbtcp.unit_id -e modbus.func_code | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag writes (FC 5/6/15/16/22/23), diagnostics (FC 8 — restart / force-listen-only), device identification (FC 43/14, recon) and Schneider UMAS (FC 90, engineering).

```bash
tshark -r 'data/synthetic-ot-scenarios-lindseynguyen/samples/attack_scenarios.pcap' -Y 'modbus.func_code in {5, 6, 15, 16, 22, 23, 8, 43, 90}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
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

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Read Holding Registers ×270, Write Single Register ×91, Diagnostics ×2, Write Single Coil ×1, UMAS ×1, Write Multiple Registers ×1, Read Coils ×1; dangerous-operation matches: 96 (top sources: 192.168.10.66 ×93, 192.168.10.10 ×3); top conversations in attack_scenarios.pcap: 192.168.10.10↔203.0.113.50 (300 pkts), 192.168.10.20↔192.168.10.66 (221 pkts), 192.168.10.66↔192.168.10.80 (167 pkts) (basis: 3 of 3 capture file(s), first 300,000 packets each)

_Dataset credit: lindseynguyen (GitHub) · License: MIT._

</details>

## Dataset & credit

**lindseynguyen (GitHub)** — license: MIT

- [Dataset source — Synthetic OT scenarios — benign plant vs. attack](https://github.com/lindseynguyen/ics-pcap-analyzer)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (3)</summary>

- `data/synthetic-ot-scenarios-lindseynguyen/samples/attack_scenarios.pcap`
- `data/synthetic-ot-scenarios-lindseynguyen/samples/benign_plant.pcap`
- `data/synthetic-ot-scenarios-lindseynguyen/samples/ot_protocols.pcap`

</details>
