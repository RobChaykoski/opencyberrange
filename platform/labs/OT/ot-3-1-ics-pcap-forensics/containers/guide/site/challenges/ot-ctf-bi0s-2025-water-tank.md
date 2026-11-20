# bi0sCTF 2025 — Water Tank

**CTF &amp; conference labs** · **Medium** · 0.0 MB · 0 capture file(s)

> CTF: Water Tank (Modbus/TCP).

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

A capture-the-flag challenge from bi0sCTF 2025 — hardware/ICS. The full challenge also has a live valve part; the capture works on its own for analysis.

ICS CTF flags usually hide in protocol fields — register values, write payloads, function codes or timing — rather than in plain text. Work it like an analyst: map the protocol, find the operations that don't belong, then decode.

## Objectives

- Identify the protocol(s), roles and endpoints.
- Find the anomalous operations or payloads.
- Extract and decode the flag.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py ctf-bi0s-2025
```

- **[bi0sCTF 2025 — hardware/ICS](../DATASETS.md#ctf-bi0s-2025)** (`ctf-bi0s-2025`), ~1.4 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/teambi0s/bi0sCTF](https://github.com/teambi0s/bi0sCTF)

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Let Pcapper hunt the flag**

--ctf runs Pcapper's flag finder and decoders; --overview runs the right OT analyzer.

```bash
pcapper 'data/ctf-bi0s-2025/water-tank/modbus_capture.pcap' --ctf --overview
```

**2. Let Pcapper hunt for the flag**

--ctf runs Pcapper's flag finder and decoders; --strings surfaces cleartext that a flag may hide in.

```bash
pcapper 'data/ctf-bi0s-2025/water-tank/modbus_capture.pcap' --ctf --strings
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/ctf-bi0s-2025/water-tank/modbus_capture.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Let Pcapper hunt the flag**

```bash
capinfos 'data/ctf-bi0s-2025/water-tank/modbus_capture.pcap'
tshark -r 'data/ctf-bi0s-2025/water-tank/modbus_capture.pcap' -q -z io,phs | head -40
```

**2. Map the Modbus/TCP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/ctf-bi0s-2025/water-tank/modbus_capture.pcap' -Y mbtcp -T fields -e ip.src -e ip.dst -e mbtcp.unit_id -e modbus.func_code | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag writes (FC 5/6/15/16/22/23), diagnostics (FC 8 — restart / force-listen-only), device identification (FC 43/14, recon) and Schneider UMAS (FC 90, engineering).

```bash
tshark -r 'data/ctf-bi0s-2025/water-tank/modbus_capture.pcap' -Y 'modbus.func_code in {5, 6, 15, 16, 22, 23, 8, 43, 90}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Decode the protocol fields**

Register values, write payloads and odd function codes are the usual hiding places — try ASCII.

```bash
tshark -r 'data/ctf-bi0s-2025/water-tank/modbus_capture.pcap' -Y 'modbus.regval_uint16' -T fields -e modbus.regval_uint16 | head -60
strings -n 6 'data/ctf-bi0s-2025/water-tank/modbus_capture.pcap' | grep -iE 'flag|ctf|\{' | head
```

## Hints

<details><summary>Hint 1</summary>

Pcapper --ctf tries common encodings automatically.

</details>

<details><summary>Hint 2</summary>

Read writes, not just reads — the flag is often written.

</details>

<details><summary>Hint 3</summary>

Concatenate register values in order and decode the 16-bit words as ASCII.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

A public write-up exists — work it yourself first, then compare: https://github.com/teambi0s/bi0sCTF/tree/main/2025/HW/water%20tank

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Read Discrete Inputs ×2064, Read Coils ×1932, Read Input Registers ×1915, Read Holding Registers ×1902, Write Multiple Registers ×363, Write Multiple Coils ×353, Write Single Coil ×329, Write Single Register ×319; dangerous-operation matches: 1364 (top sources: 192.168.235.132 ×1364); top conversations in modbus_capture.pcap: 192.168.1.100↔192.168.235.132 (10,000 pkts), 192.168.1.10↔192.168.1.100 (10,000 pkts); flag-like strings found by `strings`: none in plain text (decode protocol fields) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: team bi0s (official repo) (2025) · License: None stated — credit team bi0s._

</details>

## Dataset & credit

**team bi0s (official repo) (2025)** — license: None stated — credit team bi0s

- [Dataset source — bi0sCTF 2025 — hardware/ICS](https://github.com/teambi0s/bi0sCTF)
- [Write-up / solution](https://github.com/teambi0s/bi0sCTF/tree/main/2025/HW/water%20tank)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/ctf-bi0s-2025/water-tank/modbus_capture.pcap`

</details>
