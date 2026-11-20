# S4x15 CTF — the PLCs (Modicon &amp; MicroLogix)

**CTF &amp; conference labs** · **Medium** · 0.0 MB · 0 capture file(s)

> Two PLC captures from the CTF: a Schneider Modicon (Modbus/UMAS) and an Allen-Bradley MicroLogix (EtherNet/IP + PCCC).

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Part of the S4x15 ICS Village CTF capture set (see the main S4x15 challenge for context). Work this device group on its own: establish its normal role, then find what the CTF teams did to it.

## Objectives

- Establish the device's normal communication partners.
- Find reconnaissance against it.
- Find any control, write or exploit traffic and its source.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py digitalbond-s4x15-ctf
```

- **[S4x15 ICS Village CTF captures (Digital Bond)](../DATASETS.md#digitalbond-s4x15-ctf)** (`digitalbond-s4x15-ctf`), ~41.5 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [netresec.com/?page=DigitalBond_S4](https://www.netresec.com/?page=DigitalBond_S4)

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/digitalbond-s4x15-ctf/Modicon.pcap' --overview
```

**2. Deep-dive with Pcapper (--modbus)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/digitalbond-s4x15-ctf/Modicon.pcap' --modbus --ot-commands
```

**3. Let Pcapper hunt for the flag**

--ctf runs Pcapper's flag finder and decoders; --strings surfaces cleartext that a flag may hide in.

```bash
pcapper 'data/digitalbond-s4x15-ctf/Modicon.pcap' --ctf --strings
```

**4. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/digitalbond-s4x15-ctf/Modicon.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/digitalbond-s4x15-ctf/Modicon.pcap'
tshark -r 'data/digitalbond-s4x15-ctf/Modicon.pcap' -q -z io,phs | head -40
```

**2. Map the Modbus/TCP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/digitalbond-s4x15-ctf/Modicon.pcap' -Y mbtcp -T fields -e ip.src -e ip.dst -e mbtcp.unit_id -e modbus.func_code | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag writes (FC 5/6/15/16/22/23), diagnostics (FC 8 — restart / force-listen-only), device identification (FC 43/14, recon) and Schneider UMAS (FC 90, engineering).

```bash
tshark -r 'data/digitalbond-s4x15-ctf/Modicon.pcap' -Y 'modbus.func_code in {5, 6, 15, 16, 22, 23, 8, 43, 90}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

## Hints

<details><summary>Hint 1</summary>

Compare the first minutes (setup/normal) with the rest of the capture.

</details>

<details><summary>Hint 2</summary>

Attribute every write/control operation to a source IP.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

Score yourself on: the device's normal peers, the scanner(s), and each attack operation with its source and time. The CTF is real competition traffic — there is no published per-packet key.

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Read Holding Registers ×336; dangerous-operation matches: 0 for the Modbus/TCP filter (336 Modbus/TCP packets present, so the zero is real); top conversations in Modicon.pcap: 10.200.1.252↔10.50.1.52 (1,950 pkts), 10.200.1.193↔10.50.1.52 (720 pkts), 10.200.1.86↔10.50.1.52 (681 pkts); flag-like strings found by `strings`: none in plain text (decode protocol fields) (basis: 1 of 2 capture file(s), first 300,000 packets each)

_Dataset credit: Digital Bond — Dale Peterson &amp; Reid Wightman (S4x15); published by Netresec (2015) · License: Published by Netresec with permission from Dale Peterson and Reid Wightman — credit S4/Digital Bond and Netresec._

</details>

## Dataset & credit

**Digital Bond — Dale Peterson &amp; Reid Wightman (S4x15); published by Netresec (2015)** — license: Published by Netresec with permission from Dale Peterson and Reid Wightman — credit S4/Digital Bond and Netresec

- [Dataset source — S4x15 ICS Village CTF captures (Digital Bond)](https://www.netresec.com/?page=DigitalBond_S4)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (2)</summary>

- `data/digitalbond-s4x15-ctf/Modicon.pcap`
- `data/digitalbond-s4x15-ctf/MicroLogix56.pcap`

</details>
