# Geothermal well SCADA — intrusion detection (2026)

**Process control &amp; PLC testbeds** · **Hard** · 0.0 MB · 0 capture file(s)

> A semi-physical geothermal-well scale-inhibitor injection SCADA testbed: PLCs, operator and engineering stations. Find the attacks; the labeled CSVs are the key.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

A semi-physical geothermal-well scale-inhibitor injection SCADA testbed: PLCs, operator and engineering stations. Find the attacks; the labeled CSVs are the key.

Semi-physical SCADA testbed for geothermal-well scale-inhibitor injection: raw pcapng among PLCs, operator station, engineering station and collector, split train/test, plus labeled CSV samples (malicious flag + attack category) that serve as the answer key.

## Objectives

- Identify devices and protocol roles.
- Find and characterize the malicious activity.
- Use the dataset's labels/companion files to check yourself.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py geothermal-well-scada-ids-2026
```

- **[Geothermal well scale-inhibitor injection SCADA — intrusion dataset (2026)](../DATASETS.md#geothermal-well-scada-ids-2026)** (`geothermal-well-scada-ids-2026`), ~3.50 GB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (0.75 GB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/geothermal-well-scada-ids-2026.tar.part000) (0.75 GB)
  - **Original source:** [zenodo.org/records/23610536](https://zenodo.org/records/23610536) · [doi:10.5281/zenodo.23610536](https://doi.org/10.5281/zenodo.23610536)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/geothermal-well-scada-ids-2026/raw/test/202608060121~202608060824.pcapng' --overview
```

**2. Deep-dive with Pcapper (--s7)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/geothermal-well-scada-ids-2026/raw/test/202608060121~202608060824.pcapng' --s7 --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/geothermal-well-scada-ids-2026/raw/test/202608060121~202608060824.pcapng' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/geothermal-well-scada-ids-2026/raw/test/202608060121~202608060824.pcapng'
tshark -r 'data/geothermal-well-scada-ids-2026/raw/test/202608060121~202608060824.pcapng' -q -z io,phs | head -40
```

**2. Map the S7comm conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/geothermal-well-scada-ids-2026/raw/test/202608060121~202608060824.pcapng' -Y s7comm -T fields -e ip.src -e ip.dst -e s7comm.header.rosctr -e s7comm.param.func -e s7comm.param.userdata.funcgroup -e s7comm.param.userdata.subfunc | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag write variable (0x05), program download (0x1A–0x1C), program upload (0x1D–0x1F — logic theft), PI-service (0x28 — start/restart/compress), PLC STOP (0x29) and security/password userdata (function group 5); SZL reads (function group 4) are device recon.

```bash
tshark -r 'data/geothermal-well-scada-ids-2026/raw/test/202608060121~202608060824.pcapng' -Y 's7comm.param.func in {0x05, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 0x28, 0x29} || s7comm.param.userdata.funcgroup == 5' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
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

**Computed evidence (auto-extracted with tshark — verify it yourself):** S7comm operations — Read Var ×403115, Setup Communication ×128, CPU services ×18; dangerous-operation matches: 0 for the S7comm filter (403,261 S7comm packets present, so the zero is real); top conversations in 202608062246~202608070821.pcapng: 192.168.0.10↔192.168.0.2 (89,634 pkts), 192.168.0.1↔192.168.0.10 (89,626 pkts), 192.168.0.10↔192.168.0.3 (89,609 pkts) (basis: 3 of 17 capture file(s), first 300,000 packets each, smallest files carrying S7comm chosen)

_Dataset credit: Shui, Qianfeng (2026) — doi:10.5281/zenodo.23610536 · License: CC BY 4.0._

</details>

## Dataset & credit

**Shui, Qianfeng (2026) — doi:10.5281/zenodo.23610536** — license: CC BY 4.0

- [Dataset source — Geothermal well scale-inhibitor injection SCADA — intrusion ](https://zenodo.org/records/23610536)
- [DOI 10.5281/zenodo.23610536](https://doi.org/10.5281/zenodo.23610536)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (17)</summary>

- `data/geothermal-well-scada-ids-2026/raw/test/202608060121~202608060824.pcapng`
- `data/geothermal-well-scada-ids-2026/raw/test/202608060824~202608062246.pcapng`
- `data/geothermal-well-scada-ids-2026/raw/test/202608062246~202608070821.pcapng`
- `data/geothermal-well-scada-ids-2026/raw/test/202608070821~202608072228.pcapng`
- `data/geothermal-well-scada-ids-2026/raw/train/20251004_1430~20251005_1322.pcapng`
- `data/geothermal-well-scada-ids-2026/raw/train/20251005_1322~20251006_1337.pcapng`
- `data/geothermal-well-scada-ids-2026/raw/train/20251006_1337~20251007_1227.pcapng`
- `data/geothermal-well-scada-ids-2026/raw/train/20251007_1227~20251008_1355.pcapng`
- `data/geothermal-well-scada-ids-2026/raw/train/20251008_1355~20251009_1323.pcapng`
- `data/geothermal-well-scada-ids-2026/raw/train/20251009_1323~20251010_1221.pcapng`
- `data/geothermal-well-scada-ids-2026/raw/train/20251010_1221~20251011_1412.pcapng`
- `data/geothermal-well-scada-ids-2026/raw/train/20251011_1412~20251012_1410.pcapng`
- `data/geothermal-well-scada-ids-2026/raw/train/20251012_1410~20251013_1250.pcapng`
- `data/geothermal-well-scada-ids-2026/raw/train/20251013_1250~20251014_1250.pcapng`
- `data/geothermal-well-scada-ids-2026/raw/train/20251014_1250~20251015_1216.pcapng`
- `data/geothermal-well-scada-ids-2026/raw/train/20251015_1216~20251016_1242.pcapng`
- `data/geothermal-well-scada-ids-2026/raw/train/20251016_1242~20251017_2204.pcapng`

</details>
