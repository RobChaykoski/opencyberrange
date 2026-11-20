# Synthetic OT samples mapped to ATT&amp;CK for ICS

**Process control &amp; PLC testbeds** · **Easy** · 0.0 MB · 0 capture file(s)

> Benign plant, cleartext credentials, DNS tunnelling and ICS commands — map each to ATT&amp;CK for ICS.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Benign plant, cleartext credentials, DNS tunnelling and ICS commands — map each to ATT&amp;CK for ICS.

Sample captures from an ICS-PCAP-to-MITRE viewer: benign plant, cleartext credentials, DNS tunnelling, ICS commands.

## Objectives

- Identify devices and protocol roles.
- Find and characterize the malicious activity.
- Use the dataset's labels/companion files to check yourself.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py synthetic-ot-mitre-samples
```

- **[Synthetic OT samples mapped to ATT&amp;CK for ICS](../DATASETS.md#synthetic-ot-mitre-samples)** (`synthetic-ot-mitre-samples`), ~0.1 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/AndreFroneman/ICS-PCAP-MITRE-Viewing-Tool](https://github.com/AndreFroneman/ICS-PCAP-MITRE-Viewing-Tool)

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/synthetic-ot-mitre-samples/public/samples/benign-plant.pcap' --overview
```

**2. Deep-dive with Pcapper (--modbus)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/synthetic-ot-mitre-samples/public/samples/benign-plant.pcap' --modbus --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/synthetic-ot-mitre-samples/public/samples/benign-plant.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/synthetic-ot-mitre-samples/public/samples/benign-plant.pcap'
tshark -r 'data/synthetic-ot-mitre-samples/public/samples/benign-plant.pcap' -q -z io,phs | head -40
```

**2. Map the Modbus/TCP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/synthetic-ot-mitre-samples/public/samples/benign-plant.pcap' -Y mbtcp -T fields -e ip.src -e ip.dst -e mbtcp.unit_id -e modbus.func_code | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag writes (FC 5/6/15/16/22/23), diagnostics (FC 8 — restart / force-listen-only), device identification (FC 43/14, recon) and Schneider UMAS (FC 90, engineering).

```bash
tshark -r 'data/synthetic-ot-mitre-samples/public/samples/benign-plant.pcap' -Y 'modbus.func_code in {5, 6, 15, 16, 22, 23, 8, 43, 90}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
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

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Read Holding Registers ×20, Write Single Coil ×13, Write Multiple Registers ×1, Write Single Register ×1; dangerous-operation matches: 15 (top sources: 10.10.1.80 ×15); top conversations in modbus-writes.pcap: 10.10.1.30↔10.10.1.50 (7 pkts), 10.10.1.50↔10.10.1.80 (6 pkts) (basis: 3 of 7 capture file(s), first 300,000 packets each, smallest files carrying Modbus/TCP chosen)

_Dataset credit: AndreFroneman (GitHub) · License: No license stated in repo — credit the author._

</details>

## Dataset & credit

**AndreFroneman (GitHub)** — license: No license stated in repo — credit the author

- [Dataset source — Synthetic OT samples mapped to ATT&amp;CK for ICS](https://github.com/AndreFroneman/ICS-PCAP-MITRE-Viewing-Tool)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (7)</summary>

- `data/synthetic-ot-mitre-samples/public/samples/benign-plant.pcap`
- `data/synthetic-ot-mitre-samples/public/samples/cleartext-creds.pcap`
- `data/synthetic-ot-mitre-samples/public/samples/dns-tunnel.pcap`
- `data/synthetic-ot-mitre-samples/public/samples/ics-commands.pcapng`
- `data/synthetic-ot-mitre-samples/public/samples/modbus-writes.pcap`
- `data/synthetic-ot-mitre-samples/public/samples/plant-shift.pcap`
- `data/synthetic-ot-mitre-samples/public/samples/port-scan.pcap`

</details>
