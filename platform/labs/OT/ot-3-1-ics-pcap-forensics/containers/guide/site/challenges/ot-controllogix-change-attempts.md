# ControlLogix 5000 — change date/time and port-configuration attempts

**ICS malware &amp; intrusions** · **Hard** · 0.0 MB · 0 capture file(s)

> Someone tried to change a ControlLogix's clock and its Ethernet port configuration over EtherNet/IP. Reconstruct each attempt.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Three captures of attempts against an Allen-Bradley ControlLogix (CL5000) over EtherNet/IP/CIP: changing the controller's date, its time, and its Ethernet port configuration. Clock changes break event timelines and scheduled logic; port reconfiguration can cut the controller off the network.

For each attempt, identify the CIP object/attribute targeted, the service used, and whether the controller accepted it (general status).

## Objectives

- Identify the CIP service and object/attribute targeted in each capture.
- Determine whether each attempt succeeded (CIP general status).
- Map each attempt to ATT&amp;CK for ICS.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py s7comm-scenarios-jenilv07
```

- **[ICS sample collection (jenilv-07) — S7comm scenarios, ControlLogix attack attempts, BACnet, Modbus, Omron, Tridium](../DATASETS.md#s7comm-scenarios-jenilv07)** (`s7comm-scenarios-jenilv07`), ~34.1 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/jenilv-07/ICS-pcap-files](https://github.com/jenilv-07/ICS-pcap-files)

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/s7comm-scenarios-jenilv07/comman/CL5000EIP-Change-Date-Attempt.pcap' --overview
```

**2. Deep-dive with Pcapper (--enip --cip --pccc)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/s7comm-scenarios-jenilv07/comman/CL5000EIP-Change-Date-Attempt.pcap' --enip --cip --pccc --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/s7comm-scenarios-jenilv07/comman/CL5000EIP-Change-Date-Attempt.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/s7comm-scenarios-jenilv07/comman/CL5000EIP-Change-Date-Attempt.pcap'
tshark -r 'data/s7comm-scenarios-jenilv07/comman/CL5000EIP-Change-Date-Attempt.pcap' -q -z io,phs | head -40
```

**2. Map the EtherNet/IP &amp; CIP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/s7comm-scenarios-jenilv07/comman/CL5000EIP-Change-Date-Attempt.pcap' -Y enip -T fields -e ip.src -e ip.dst -e enip.command -e cip.sc | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag CIP Reset (0x05), Start (0x06), Stop (0x07), Set Attribute Single (0x10), Execute PCCC (0x4B), Write Tag (0x4D), Write Tag Fragmented (0x53); ENIP ListIdentity (0x63) is the classic discovery broadcast.

```bash
tshark -r 'data/s7comm-scenarios-jenilv07/comman/CL5000EIP-Change-Date-Attempt.pcap' -Y 'cip.sc in {0x05, 0x06, 0x07, 0x10, 0x4b, 0x4d, 0x53} || enip.command == 0x63' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Read the CIP status of every reply**

General status 0x00 = success; anything else = rejected.

```bash
tshark -r 'data/s7comm-scenarios-jenilv07/comman/CL5000EIP-Change-Date-Attempt.pcap' -Y cip -T fields -e frame.number -e ip.src -e cip.sc -e cip.genstat -e cip.epath | head -40
```

## Hints

<details><summary>Hint 1</summary>

Set Attribute Single (0x10) / Set Attribute List (0x04) against the Time Sync or TCP/IP Interface / Ethernet Link objects is what to look for.

</details>

<details><summary>Hint 2</summary>

The response's general status tells you if the controller accepted the change.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

Each capture holds a CIP set-attribute style request: against the controller's time/clock attributes (date, time) or the TCP/IP Interface / Ethernet Link object (port configuration). Check cip.genstat on the replies to see which attempts the controller accepted. ATT&amp;CK for ICS: T0836 Modify Parameter; port reconfiguration also maps to T0814 Denial of Service; clock tampering degrades forensics (T0872 Indicator Removal on Host is a stretch — note it as impact on timelines).

**Computed evidence (auto-extracted with tshark — verify it yourself):** EtherNet/IP &amp; CIP operations — Get Attribute List ×3227, Multiple Service Packet ×243, Get Attribute Single ×10, Set Attribute List ×4, Get Attributes All ×4, Set Attribute Single ×2; dangerous-operation matches: 2 (top sources: 192.168.10.105 ×1, 192.168.10.121 ×1); top conversations in CL5000EIP-Change-Date-Attempt.pcap: 192.168.10.105↔192.168.10.120 (351 pkts) (basis: 3 of 3 capture file(s), first 300,000 packets each)

_Dataset credit: jenilv-07 (GitHub) · License: No license stated in repo — credit the author._

</details>

## Dataset & credit

**jenilv-07 (GitHub)** — license: No license stated in repo — credit the author

- [Dataset source — ICS sample collection (jenilv-07) — S7comm scenarios, Contro](https://github.com/jenilv-07/ICS-pcap-files)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (3)</summary>

- `data/s7comm-scenarios-jenilv07/comman/CL5000EIP-Change-Date-Attempt.pcap`
- `data/s7comm-scenarios-jenilv07/comman/CL5000EIP-Change-Port-Configuration-Attempt.pcap`
- `data/s7comm-scenarios-jenilv07/comman/CL5000EIP-Change-Time-Attempt.pcap`

</details>
