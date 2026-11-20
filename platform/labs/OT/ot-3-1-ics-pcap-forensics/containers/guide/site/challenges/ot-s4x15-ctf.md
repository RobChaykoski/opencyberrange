# S4x15 ICS Village CTF — reconstruct the competition

**CTF &amp; conference labs** · **Hard** · 0.0 MB · 0 capture file(s)

> Captures from the S4x15 ICS Village Capture-the-Flag: PLCs, HMIs, BACnet and a corporate PC under attack by CTF teams.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

These captures were taken during the S4x15 Capture-the-Flag in Digital Bond's ICS Village — a mix of PLCs (Schneider Modicon, Allen-Bradley MicroLogix), GE iFIX HMI client/server, BACnet building controllers, an Advantech device and a Windows XP corporate host. CTF teams were scoring points by attacking them.

Reconstruct what the teams did: which devices were targeted, with which protocols, and what changed on the controllers.

## Objectives

- Identify every device and its role from the per-host captures.
- Find reconnaissance against each device.
- Find the control/engineering operations that would have scored CTF points.
- Build a timeline of the attacks.

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

**1. Overview with Pcapper (all hosts at once)**

Pcapper accepts a directory.

```bash
pcapper data/digitalbond-s4x15-ctf/ --overview
```

**2. Map it to ATT&amp;CK for ICS**

```bash
pcapper data/digitalbond-s4x15-ctf/ --mitre
```

**3. Let Pcapper hunt for the flag**

--ctf runs Pcapper's flag finder and decoders; --strings surfaces cleartext that a flag may hide in.

```bash
pcapper 'data/digitalbond-s4x15-ctf/Advantech.pcap' --ctf --strings
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Per-host inventory**

Each file was captured for one device — size and protocol mix tell you where the action was.

```bash
for f in data/digitalbond-s4x15-ctf/*.pcap; do echo "== $f"; capinfos -c -u "$f" | tail -2; done
```

**2. Protocol mix per device**

```bash
for f in data/digitalbond-s4x15-ctf/*.pcap; do echo "== $f"; tshark -r "$f" -q -z io,phs | grep -E 'mbtcp|modbus|enip|cip|bacnet|s7comm|http|smb|rdp' ; done
```

**3. Control operations against the PLCs**

```bash
tshark -r data/digitalbond-s4x15-ctf/Modicon.pcap -Y 'modbus.func_code in {5, 6, 15, 16, 90}' -T fields -e frame.time -e ip.src -e modbus.func_code | head
tshark -r data/digitalbond-s4x15-ctf/MicroLogix56.pcap -Y 'cip.sc in {0x4b, 0x4d, 0x53, 0x05, 0x06, 0x07}' -T fields -e frame.time -e ip.src -e cip.sc | head
```

## Hints

<details><summary>Hint 1</summary>

The Modicon speaks Modbus (and Schneider's UMAS function 90); the MicroLogix speaks EtherNet/IP with PCCC encapsulated in CIP (service 0x4B).

</details>

<details><summary>Hint 2</summary>

The iFIX HMI captures show what the operators saw — and whether anyone else talked to the PLCs directly.

</details>

<details><summary>Hint 3</summary>

Look for BACnet writeProperty/reinitializeDevice against the building controllers.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

Expect classic CTF tradecraft: discovery scans, then unauthenticated Modbus/UMAS writes against the Modicon, PCCC/CIP writes or mode changes against the MicroLogix, BACnet property writes against the building controllers, and IT-side attacks (SMB/HTTP) against the Windows XP and Advantech hosts. Score yourself on the device ↔ attack ↔ protocol table and the timeline. Netresec's S4x15 page links the original CTF description.

**Computed evidence (auto-extracted with tshark — verify it yourself):** BACnet operations — readProperty ×60048, readPropertyMultiple ×1897, atomicReadFile ×9; dangerous-operation matches: 0 for the BACnet filter (121,623 BACnet packets present, so the zero is real); top conversations in BACnet_FIU.pcap: 10.200.1.77↔131.94.238.11 (38,212 pkts), 10.200.1.202↔131.94.238.11 (36,656 pkts), 10.200.1.251↔131.94.238.11 (14,910 pkts); flag-like strings found by `strings`: none in plain text (decode protocol fields) (basis: 2 of 8 capture file(s), first 300,000 packets each)

_Dataset credit: Digital Bond — Dale Peterson &amp; Reid Wightman (S4x15); published by Netresec (2015) · License: Published by Netresec with permission from Dale Peterson and Reid Wightman — credit S4/Digital Bond and Netresec._

</details>

## Dataset & credit

**Digital Bond — Dale Peterson &amp; Reid Wightman (S4x15); published by Netresec (2015)** — license: Published by Netresec with permission from Dale Peterson and Reid Wightman — credit S4/Digital Bond and Netresec

- [Dataset source — S4x15 ICS Village CTF captures (Digital Bond)](https://www.netresec.com/?page=DigitalBond_S4)
- [Netresec — S4x15 ICS Village PCAPs](https://www.netresec.com/?page=DigitalBond_S4)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (8)</summary>

- `data/digitalbond-s4x15-ctf/Advantech.pcap`
- `data/digitalbond-s4x15-ctf/BACnet_FIU.pcap`
- `data/digitalbond-s4x15-ctf/BACnet_Host.pcap`
- `data/digitalbond-s4x15-ctf/MicroLogix56.pcap`
- `data/digitalbond-s4x15-ctf/Modicon.pcap`
- `data/digitalbond-s4x15-ctf/WinXP.pcap`
- `data/digitalbond-s4x15-ctf/iFix_Client86.pcap`
- `data/digitalbond-s4x15-ctf/iFix_Server119.pcap`

</details>
