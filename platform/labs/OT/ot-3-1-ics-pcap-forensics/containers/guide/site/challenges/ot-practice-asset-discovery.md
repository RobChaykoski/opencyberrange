# ICS practice — asset discovery

**Process control &amp; PLC testbeds** · **Easy** · 0.0 MB · 0 capture file(s)

> Build an asset inventory from passive traffic.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Build an asset inventory from passive traffic.

## Objectives

- Answer the practice question from the packets.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py ics-practice-solymx
```

- **[ICS PCAP practice challenges (asset discovery, hidden Modbus threat)](../DATASETS.md#ics-practice-solymx)** (`ics-practice-solymx`), ~0.7 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/solymx/ICS_PCAP_Practice](https://github.com/solymx/ICS_PCAP_Practice)

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/ics-practice-solymx/lab_asset_discovery.pcap' --overview
```

**2. Deep-dive with Pcapper (--modbus)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/ics-practice-solymx/lab_asset_discovery.pcap' --modbus --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/ics-practice-solymx/lab_asset_discovery.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/ics-practice-solymx/lab_asset_discovery.pcap'
tshark -r 'data/ics-practice-solymx/lab_asset_discovery.pcap' -q -z io,phs | head -40
```

**2. Map the Modbus/TCP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/ics-practice-solymx/lab_asset_discovery.pcap' -Y mbtcp -T fields -e ip.src -e ip.dst -e mbtcp.unit_id -e modbus.func_code | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag writes (FC 5/6/15/16/22/23), diagnostics (FC 8 — restart / force-listen-only), device identification (FC 43/14, recon) and Schneider UMAS (FC 90, engineering).

```bash
tshark -r 'data/ics-practice-solymx/lab_asset_discovery.pcap' -Y 'modbus.func_code in {5, 6, 15, 16, 22, 23, 8, 43, 90}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

## Hints

<details><summary>Hint 1</summary>

Baseline first, then look for the outlier.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

List every device, its role and protocols from passive observation.

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Read Holding Registers ×3518, Read Input Registers ×32, Read Coils ×18, Write Single Register ×12; dangerous-operation matches: 12 (top sources: 172.20.10.10 ×3, 172.20.20.101 ×3, 172.20.10.88 ×3); top conversations in lab_asset_discovery.pcap: 172.20.10.1↔172.20.20.101 (1,065 pkts), 172.20.10.1↔172.20.20.102 (1,065 pkts), 172.20.10.1↔172.20.20.103 (1,065 pkts) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: solymx (GitHub) · License: No license stated in repo — credit the author._

</details>

## Dataset & credit

**solymx (GitHub)** — license: No license stated in repo — credit the author

- [Dataset source — ICS PCAP practice challenges (asset discovery, hidden Modbus](https://github.com/solymx/ICS_PCAP_Practice)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/ics-practice-solymx/lab_asset_discovery.pcap`

</details>
