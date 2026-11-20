# CIP/EtherNet-IP — including a ControlLogix reboot

**Process control &amp; PLC testbeds** · **Medium** · 0.0 MB · 0 capture file(s)

> CIP/EtherNet-IP captures, including a controller reboot/restart command.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

CIP/EtherNet-IP captures, including a controller reboot/restart command.

CIP/EtherNet-IP captures gathered from various resources, including a ControlLogix reboot/restart command.

## Objectives

- Identify devices and protocol roles.
- Find and characterize the malicious activity.
- Use the dataset's labels/companion files to check yourself.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py cip-enip-engage-svg
```

- **[CIP / EtherNet-IP captures (incl. controller reboot)](../DATASETS.md#cip-enip-engage-svg)** (`cip-enip-engage-svg`), ~13.8 MB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (3.6 MB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/cip-enip-engage-svg.tar.part000) (3.6 MB)
  - **Original source:** [github.com/engage-svg/ICS-PCAPs](https://github.com/engage-svg/ICS-PCAPs)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/cip-enip-engage-svg/CIP/CIP.pcap' --overview
```

**2. Deep-dive with Pcapper (--enip --cip --pccc)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/cip-enip-engage-svg/CIP/CIP.pcap' --enip --cip --pccc --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/cip-enip-engage-svg/CIP/CIP.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/cip-enip-engage-svg/CIP/CIP.pcap'
tshark -r 'data/cip-enip-engage-svg/CIP/CIP.pcap' -q -z io,phs | head -40
```

**2. Map the EtherNet/IP &amp; CIP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/cip-enip-engage-svg/CIP/CIP.pcap' -Y enip -T fields -e ip.src -e ip.dst -e enip.command -e cip.sc | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag CIP Reset (0x05), Start (0x06), Stop (0x07), Set Attribute Single (0x10), Execute PCCC (0x4B), Write Tag (0x4D), Write Tag Fragmented (0x53); ENIP ListIdentity (0x63) is the classic discovery broadcast.

```bash
tshark -r 'data/cip-enip-engage-svg/CIP/CIP.pcap' -Y 'cip.sc in {0x05, 0x06, 0x07, 0x10, 0x4b, 0x4d, 0x53} || enip.command == 0x63' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
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

**Computed evidence (auto-extracted with tshark — verify it yourself):** EtherNet/IP &amp; CIP operations — Execute PCCC ×18801, Get Attribute List ×1312, Read Tag ×620, Multiple Service Packet ×116, Set Attribute List ×112, 0x8 ×86, Get Attributes All ×30, Forward Open ×23; dangerous-operation matches: 18807 (top sources: 192.168.0.65 ×9428, 192.168.0.30 ×9353, 192.168.10.105 ×13); top conversations in ENIP_CIP-CM.pcap: 192.168.100.28↔192.168.100.36 (8 pkts), 192.168.100.28↔192.168.100.35 (1 pkts) (basis: 3 of 6 capture file(s), first 300,000 packets each, smallest files carrying EtherNet/IP &amp; CIP chosen)

_Dataset credit: engage-svg (GitHub) · License: MIT._

</details>

## Dataset & credit

**engage-svg (GitHub)** — license: MIT

- [Dataset source — CIP / EtherNet-IP captures (incl. controller reboot)](https://github.com/engage-svg/ICS-PCAPs)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (6)</summary>

- `data/cip-enip-engage-svg/CIP/CIP.pcap`
- `data/cip-enip-engage-svg/CIP/CIPvalue.pcap`
- `data/cip-enip-engage-svg/CIP/CL5000EIP-Reboot-or-Restart.pcap`
- `data/cip-enip-engage-svg/CIP/ENIP_CIP-CM.pcap`
- `data/cip-enip-engage-svg/CIP/cip_only.pcap`
- `data/cip-enip-engage-svg/Malware/industroyer2-full.pcapng`

</details>
