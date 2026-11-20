# TU Wien Smart Factory — the unlabeled DoS attack day

**Manufacturing &amp; smart factory** · **Expert** · 0.0 MB · 0 capture file(s)

> A full extra attack day from a real factory cell — including a DoS — and nobody labeled it. That's your job.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller. 3 of these captures carry executable files (Windows PE / Linux ELF) inside the traffic, and some may be malware: work offline, hash anything you extract and never run it.

## Scenario

The TU Wien smart-factory dataset includes an extra attack day containing a denial-of-service attack that the authors did NOT label. The captures were split into &lt;2 GB parts on ingest.

Characterize the day: baseline the factory protocols (OPC UA, Modbus/TCP, MQTT), find the DoS window and source, and determine which devices it affected.

## Objectives

- Baseline the normal factory traffic.
- Find the start/end of the DoS and its source(s).
- Determine affected devices/protocols.
- Find any other malicious activity on that day.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py tuwien-smart-factory
```

- **[TU Wien Smart Factory — Malware Communication in Smart Factories](../DATASETS.md#tuwien-smart-factory)** (`tuwien-smart-factory`), ~127.15 GB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 21 parts (39.02 GB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/tuwien-smart-factory.tar.part000) (1.90 GB) · [part001](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/tuwien-smart-factory.tar.part001) (1.90 GB) · [part002](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/tuwien-smart-factory.tar.part002) (1.90 GB) · [part003](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/tuwien-smart-factory.tar.part003) (1.90 GB) · [part004](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/tuwien-smart-factory.tar.part004) (1.90 GB) · [part005](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/tuwien-smart-factory.tar.part005) (1.90 GB) · [part006](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/tuwien-smart-factory.tar.part006) (1.90 GB) · [part007](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/tuwien-smart-factory.tar.part007) (1.90 GB) · [part008](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/tuwien-smart-factory.tar.part008) (1.90 GB) · [part009](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/tuwien-smart-factory.tar.part009) (1.90 GB) · [part010](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/tuwien-smart-factory.tar.part010) (1.90 GB) · [part011](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/tuwien-smart-factory.tar.part011) (1.90 GB) · [part012](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/tuwien-smart-factory.tar.part012) (1.90 GB) · [part013](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/tuwien-smart-factory.tar.part013) (1.90 GB) · [part014](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/tuwien-smart-factory.tar.part014) (1.90 GB) · [part015](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/tuwien-smart-factory.tar.part015) (1.90 GB) · [part016](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/tuwien-smart-factory.tar.part016) (1.90 GB) · [part017](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/tuwien-smart-factory.tar.part017) (1.90 GB) · [part018](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/tuwien-smart-factory.tar.part018) (1.90 GB) · [part019](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/tuwien-smart-factory.tar.part019) (1.90 GB) · [part020](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/tuwien-smart-factory.tar.part020) (1.02 GB)
  - **Original source:** [researchdata.tuwien.ac.at/records/ghdc6-45k78](https://researchdata.tuwien.ac.at/records/ghdc6-45k78) · [doi:10.48436/ghdc6-45k78](https://doi.org/10.48436/ghdc6-45k78)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Inventory the parts**

```bash
ls -lh 'data/tuwien-smart-factory/captures'/*tuesday*
```

**2. Overview with Pcapper**

```bash
pcapper 'data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part000.pcap' --overview --scan
```

**3. Every control and write, normalized**

--ot-commands lists every OT control/write command across protocols; --threats consolidates Pcapper's detections.

```bash
pcapper 'data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part000.pcap' --ot-commands --threats
```

**4. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part000.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part000.pcap'
tshark -r 'data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part000.pcap' -q -z io,phs | head -40
```

**2. Inventory the parts**

```bash
ls -lh 'data/tuwien-smart-factory/captures'/*tuesday*
```

**3. Rate over time (find the DoS window)**

```bash
tshark -r 'data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part000.pcap' -q -z io,stat,60 | head -80
```

**4. Top talkers**

```bash
tshark -r 'data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part000.pcap' -q -z conv,ip | head -25
```

## Hints

<details><summary>Hint 1</summary>

Use per-minute io,stat first — a DoS is a step change in packets/s.

</details>

<details><summary>Hint 2</summary>

Compare with the labeled attack days (a_day1/a_day2) in the same folder.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

Unlabeled by design — you produce the label. A good answer gives the DoS window (start/end), source IP(s), target(s), technique (e.g. SYN/UDP/application flood) and the effect on the factory protocols.

**Computed evidence (auto-extracted with tshark — verify it yourself):** OPC UA operations — 2480322531 ×1, 49 ×1; dangerous-operation matches: 0 for the OPC UA filter (92 OPC UA packets present, so the zero is real); top conversations in a_day_tuesday_dos.pcap.part006.pcap: 192.168.10.55↔192.168.10.63 (263 pkts), 192.168.10.55↔192.168.10.61 (253 pkts), 192.168.10.55↔192.168.10.62 (253 pkts) (basis: 3 of 55 capture file(s), first 300,000 packets each, smallest files carrying OPC UA chosen)

_Dataset credit: Brenner, B., Fabini, J., Offermanns, M., Semper, S. &amp; Zseby, T. (TU Wien) (2025) — doi:10.48436/ghdc6-45k78 · License: CC BY 4.0._

</details>

## Dataset & credit

**Brenner, B., Fabini, J., Offermanns, M., Semper, S. &amp; Zseby, T. (TU Wien) (2025) — doi:10.48436/ghdc6-45k78** — license: CC BY 4.0

- [Dataset source — TU Wien Smart Factory — Malware Communication in Smart Facto](https://researchdata.tuwien.ac.at/records/ghdc6-45k78)
- [DOI 10.48436/ghdc6-45k78](https://doi.org/10.48436/ghdc6-45k78)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (55)</summary>

- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part000.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part001.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part002.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part003.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part004.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part005.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part006.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part007.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part008.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part009.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part010.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part011.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part012.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part013.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part014.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part015.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part016.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part017.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part018.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part019.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part020.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part021.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part022.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part023.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part024.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part025.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part026.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part027.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part028.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part029.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part030.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part031.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part032.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part033.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part034.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part035.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part036.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part037.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part038.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part039.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part040.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part041.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part042.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part043.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part044.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part045.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part046.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part047.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part048.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part049.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part050.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part051.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part052.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part053.pcap`
- `data/tuwien-smart-factory/captures/a_day_tuesday_dos.pcap.part054.pcap`

</details>
