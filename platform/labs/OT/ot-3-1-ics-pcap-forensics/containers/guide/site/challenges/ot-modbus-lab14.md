# Modbus lab 14 — Attack chain

**Process control &amp; PLC testbeds** · **Hard** · 0.0 MB · 0 capture file(s)

> Recon → enumeration → manipulation in one capture. Reconstruct the kill chain.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Lab 14 of a 16-part Modbus/TCP lab series that walks from baseline traffic to a capstone attack. Recon → enumeration → manipulation in one capture. Reconstruct the kill chain.

## Objectives

- Answer the lab's question from the packets.
- Record source, unit ID, function code and addresses for anything abnormal.
- Note the ATT&amp;CK for ICS technique.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py modbus-labs-solymx
```

- **[Modbus/TCP lab series (baseline → recon → writes)](../DATASETS.md#modbus-labs-solymx)** (`modbus-labs-solymx`), ~3.4 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/solymx/modbus_pcap_test](https://github.com/solymx/modbus_pcap_test)

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Open the lab**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/modbus-labs-solymx/lab14_attack_chain.pcap' --overview
```

**2. Deep-dive with Pcapper (--modbus)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/modbus-labs-solymx/lab14_attack_chain.pcap' --modbus --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/modbus-labs-solymx/lab14_attack_chain.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Open the lab**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/modbus-labs-solymx/lab14_attack_chain.pcap'
tshark -r 'data/modbus-labs-solymx/lab14_attack_chain.pcap' -q -z io,phs | head -40
```

**2. Map the Modbus/TCP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/modbus-labs-solymx/lab14_attack_chain.pcap' -Y mbtcp -T fields -e ip.src -e ip.dst -e mbtcp.unit_id -e modbus.func_code | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag writes (FC 5/6/15/16/22/23), diagnostics (FC 8 — restart / force-listen-only), device identification (FC 43/14, recon) and Schneider UMAS (FC 90, engineering).

```bash
tshark -r 'data/modbus-labs-solymx/lab14_attack_chain.pcap' -Y 'modbus.func_code in {5, 6, 15, 16, 22, 23, 8, 43, 90}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

## Hints

<details><summary>Hint 1</summary>

Do the labs in order — each one assumes you know the previous baseline.

</details>

<details><summary>Hint 2</summary>

Exception responses have the function code's high bit set (FC + 0x80).

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

A full sequence: discovery, enumeration of function codes/registers, then writes/manipulation — order it on a timeline.

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Read Input Registers ×746, Read Holding Registers ×378, Read Coils ×376, Read Discrete Inputs ×190, Write Single Coil ×4, Write Single Register ×4, Diagnostics ×2, Write Multiple Coils ×2; dangerous-operation matches: 16 (top sources: 192.168.10.66 ×8, 192.168.10.12 ×8); top conversations in lab14_attack_chain.pcap: 192.168.10.10↔192.168.10.12 (1,567 pkts), 192.168.10.10↔192.168.10.13 (1,551 pkts), 192.168.10.12↔192.168.10.66 (389 pkts) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: solymx (GitHub) · License: No license stated in repo — credit the author._

</details>

## Dataset & credit

**solymx (GitHub)** — license: No license stated in repo — credit the author

- [Dataset source — Modbus/TCP lab series (baseline → recon → writes)](https://github.com/solymx/modbus_pcap_test)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/modbus-labs-solymx/lab14_attack_chain.pcap`

</details>
