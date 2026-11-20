# 4SICS Geek Lounge — triage a live ICS lab (3 days)

**CTF &amp; conference labs** · **Medium** · 0.0 MB · 0 capture file(s)

> Three days of a conference ICS lab — real PLCs, RTUs and HMIs open to attendees. Inventory it, then catch the attendees misbehaving.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

At 4SICS (now CS3STHLM), the 'Geek Lounge' ICS lab — real PLCs, RTUs, HMIs/servers, industrial switches and firewalls — was open for hands-on testing by conference attendees, and Netresec captured the lab network for three days.

You are the lab's NSM analyst. Build an asset inventory from the traffic alone, learn what each controller normally does, and find the moments attendees did things a real plant would page someone at 3 a.m. for.

## Objectives

- Inventory devices and vendors from protocol banners (ENIP ListIdentity, S7 SZL, LLDP/PROFINET DCP, Modbus device ID).
- Identify each OT protocol's clients and servers.
- Find scanning and discovery sweeps.
- Find write, stop/start, download and other control operations and attribute them to a source.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py netresec-4sics-2015
```

- **[4SICS Geek Lounge ICS lab captures (2015)](../DATASETS.md#netresec-4sics-2015)** (`netresec-4sics-2015`), ~0.37 GB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [netresec.com/?page=PCAP4SICS](https://www.netresec.com/?page=PCAP4SICS)

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Overview with Pcapper**

Auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/netresec-4sics-2015/4SICS-GeekLounge-151022.pcap' --overview
```

**2. Control operations across protocols**

Writes, PLC stop/start, program transfer — attribute each to a source.

```bash
pcapper 'data/netresec-4sics-2015/4SICS-GeekLounge-151022.pcap' --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/netresec-4sics-2015/4SICS-GeekLounge-151020.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Size up all three days**

Day 2 and day 3 are the busy ones — check before you open anything in a GUI.

```bash
capinfos 'data/netresec-4sics-2015/4SICS-GeekLounge-151020.pcap' 'data/netresec-4sics-2015/4SICS-GeekLounge-151021.pcap' 'data/netresec-4sics-2015/4SICS-GeekLounge-151022.pcap'
tshark -r 'data/netresec-4sics-2015/4SICS-GeekLounge-151020.pcap' -q -z io,phs | head -40
```

**2. Asset inventory from discovery protocols**

ListIdentity replies carry vendor/product names; LLDP and PROFINET DCP carry device names.

```bash
tshark -r 'data/netresec-4sics-2015/4SICS-GeekLounge-151022.pcap' -Y 'enip.command == 0x63' -T fields -e ip.src -e enip.lir.name | sort -u
tshark -r 'data/netresec-4sics-2015/4SICS-GeekLounge-151022.pcap' -Y 'lldp || pn_dcp' -T fields -e eth.src -e lldp.tlv.system.name -e pn_dcp.suboption_device_nameofstation | sort -u
```

**3. Who scanned the lab?**

Many SYNs from one host to many ports/hosts = a scanner.

```bash
tshark -r 'data/netresec-4sics-2015/4SICS-GeekLounge-151022.pcap' -Y 'tcp.flags.syn==1 && tcp.flags.ack==0' -T fields -e ip.src | sort | uniq -c | sort -rn | head
```

**4. Control operations across protocols**

Writes, PLC stop/start, program transfer — attribute each to a source.

```bash
tshark -r 'data/netresec-4sics-2015/4SICS-GeekLounge-151022.pcap' -Y 's7comm.param.func in {0x05, 0x1a, 0x1b, 0x1c, 0x28, 0x29} || modbus.func_code in {5, 6, 15, 16} || cip.sc in {0x05, 0x06, 0x07, 0x4d, 0x53}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Protocol -e _ws.col.Info | head -40
```

## Hints

<details><summary>Hint 1</summary>

Start from Pcapper --overview or tshark io,phs: the protocol hierarchy tells you which controllers were in the lab.

</details>

<details><summary>Hint 2</summary>

ENIP ListIdentity and S7 SZL (userdata function group 4) responses name the hardware.

</details>

<details><summary>Hint 3</summary>

Attendees scan first, then poke: find the scanner, then follow that IP's subsequent control traffic.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

There is no single flag — this is open lab traffic. A good answer is an asset table (IP ↔ vendor/model ↔ protocol), the scanner IPs, and a timeline of the control operations (S7 stop/start or downloads, Modbus writes, CIP service calls) with their sources.

**Computed evidence (auto-extracted with tshark — verify it yourself):** S7comm operations — Read Var ×183070, Write Var ×68, Setup Communication ×16; dangerous-operation matches: 68 (top sources: 10.10.10.10 ×34, 10.10.10.30 ×23, 192.168.1.10 ×6); top conversations in 4SICS-GeekLounge-151020.pcap: 10.10.10.10↔10.10.10.20 (146,329 pkts), 10.10.10.10↔10.10.10.30 (62,611 pkts), 192.168.88.1↔192.168.88.61 (24,661 pkts) (basis: 3 of 3 capture file(s), first 300,000 packets each)

_Dataset credit: Netresec AB and the 4SICS (now CS3STHLM) crew (2015) · License: Freely published by Netresec for research/training — credit Netresec and 4SICS/CS3STHLM._

</details>

## Dataset & credit

**Netresec AB and the 4SICS (now CS3STHLM) crew (2015)** — license: Freely published by Netresec for research/training — credit Netresec and 4SICS/CS3STHLM

- [Dataset source — 4SICS Geek Lounge ICS lab captures (2015)](https://www.netresec.com/?page=PCAP4SICS)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (3)</summary>

- `data/netresec-4sics-2015/4SICS-GeekLounge-151020.pcap`
- `data/netresec-4sics-2015/4SICS-GeekLounge-151021.pcap`
- `data/netresec-4sics-2015/4SICS-GeekLounge-151022.pcap`

</details>
