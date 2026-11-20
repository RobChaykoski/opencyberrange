# Mininet power-system — scanning attack

**Power grid &amp; substations** · **Easy** · 0.0 MB · 0 capture file(s)

> Scanning against an emulated cyber-physical power-system network.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Scanning against an emulated cyber-physical power-system network.

Scanning-attack traffic from an emulated (Mininet) cyber-physical power-system network.

## Objectives

- Identify devices and protocol roles.
- Find and characterize the malicious activity.
- Use the dataset's labels/companion files to check yourself.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py mininet-power-system-scanning
```

- **[Mininet cyber-physical power system — scanning attack](../DATASETS.md#mininet-power-system-scanning)** (`mininet-power-system-scanning`), ~1.1 MB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (0.3 MB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/mininet-power-system-scanning.tar.part000) (0.3 MB)
  - **Original source:** [zenodo.org/records/23055644](https://zenodo.org/records/23055644) · [doi:10.5281/zenodo.23055644](https://doi.org/10.5281/zenodo.23055644)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix. If no industrial dissector recognises the traffic, identifying it is the puzzle.

```bash
pcapper 'data/mininet-power-system-scanning/scanningattack_packets.pcapng' --overview
```

**2. Let Pcapper look for structure**

--strings surfaces cleartext and --carve reassembles streams and carves files.

```bash
pcapper 'data/mininet-power-system-scanning/scanningattack_packets.pcapng' --strings --carve
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/mininet-power-system-scanning/scanningattack_packets.pcapng' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix. If no industrial dissector recognises the traffic, identifying it is the puzzle.

```bash
capinfos 'data/mininet-power-system-scanning/scanningattack_packets.pcapng'
tshark -r 'data/mininet-power-system-scanning/scanningattack_packets.pcapng' -q -z io,phs | head -30
```

**2. Who talks on which port?**

Payload-carrying packets per conversation and server port: the busiest port carries the protocol you need to identify.

```bash
tshark -r 'data/mininet-power-system-scanning/scanningattack_packets.pcapng' -Y 'tcp.len > 0 || udp.length > 8' -T fields -e ip.src -e ip.dst -e tcp.dstport -e udp.dstport | sort | uniq -c | sort -rn | head -20
```

**3. Read the payloads**

Look for magic bytes, length fields, sequence counters and ASCII (device names, tags, flags).

```bash
tshark -r 'data/mininet-power-system-scanning/scanningattack_packets.pcapng' -qz follow,tcp,hex,0 | head -60
tshark -r 'data/mininet-power-system-scanning/scanningattack_packets.pcapng' -Y 'tcp.len > 0 || udp.length > 8' -T fields -e frame.number -e data.data | head -20
```

**4. Try the industrial dissectors on that port**

Replace &lt;port&gt; with the busiest server port from step 2. A clean decode (no malformed packets, length fields that match) identifies a standard protocol on a non-standard port.

```bash
for p in tpkt mbtcp dnp3 enip iec60870_104; do echo "== $p"; tshark -r 'data/mininet-power-system-scanning/scanningattack_packets.pcapng' -d tcp.port==<port>,$p 2>/dev/null | head -4; done
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

**Computed evidence (auto-extracted with tshark — verify it yourself):** top conversations in scanningattack_packets.pcapng: 100.0.0.13↔100.27.0.13 (4,016 pkts), 100.0.0.13↔100.12.0.12 (3,040 pkts), 100.0.0.13↔100.25.0.1 (2,206 pkts) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: May Myat Thwe; Stefanov, Alexandru (2026) — doi:10.5281/zenodo.23055644 · License: CC BY 4.0._

</details>

## Dataset & credit

**May Myat Thwe; Stefanov, Alexandru (2026) — doi:10.5281/zenodo.23055644** — license: CC BY 4.0

- [Dataset source — Mininet cyber-physical power system — scanning attack](https://zenodo.org/records/23055644)
- [DOI 10.5281/zenodo.23055644](https://doi.org/10.5281/zenodo.23055644)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/mininet-power-system-scanning/scanningattack_packets.pcapng`

</details>
