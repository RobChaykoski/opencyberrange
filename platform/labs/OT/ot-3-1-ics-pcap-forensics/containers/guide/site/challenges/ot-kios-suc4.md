# KIOS/ELECTRON — FDI and masquerade on a power system

**Power grid &amp; substations** · **Hard** · 0.0 MB · 0 capture file(s)

> False-data-injection and masquerade attacks on a power-system use case, with physical measurements aligned to the packets.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

False-data-injection and masquerade attacks on a power-system use case, with physical measurements aligned to the packets.

Sandboxed power-system use case: traffic for normal operation, false-data-injection (S1) and masquerade (S2) attacks, with time-aligned physical measurements (CSV) — correlate packets with the physics.

## Objectives

- Identify devices and protocol roles.
- Find and characterize the malicious activity.
- Use the dataset's labels/companion files to check yourself.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py kios-electron-suc4-power-attacks
```

- **[KIOS/ELECTRON SUC4 — FDI and masquerade attacks on a power system](../DATASETS.md#kios-electron-suc4-power-attacks)** (`kios-electron-suc4-power-attacks`), ~0.18 GB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (0.18 GB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/kios-electron-suc4-power-attacks.tar.part000) (0.18 GB)
  - **Original source:** [zenodo.org/records/12960228](https://zenodo.org/records/12960228) · [doi:10.5281/zenodo.12960228](https://doi.org/10.5281/zenodo.12960228)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/kios-electron-suc4-power-attacks/Electron_SUC4_S1_FDI_Attack_Traffic.pcapng' --overview
```

**2. Deep-dive with Pcapper (--goose)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/kios-electron-suc4-power-attacks/Electron_SUC4_S1_FDI_Attack_Traffic.pcapng' --goose --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/kios-electron-suc4-power-attacks/Electron_SUC4_S1_FDI_Attack_Traffic.pcapng' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/kios-electron-suc4-power-attacks/Electron_SUC4_S1_FDI_Attack_Traffic.pcapng'
tshark -r 'data/kios-electron-suc4-power-attacks/Electron_SUC4_S1_FDI_Attack_Traffic.pcapng' -q -z io,phs | head -40
```

**2. Map the IEC 61850 GOOSE conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/kios-electron-suc4-power-attacks/Electron_SUC4_S1_FDI_Attack_Traffic.pcapng' -Y goose -T fields -e eth.src -e goose.gocbRef -e goose.stNum -e goose.sqNum -e goose.timeAllowedtoLive | head -40
```

**3. Hunt the dangerous operations**

Flag GOOSE has no confirmed 'write' — the attack surface is the event stream itself: stNum jumping without a real state change, sqNum resets, bursts far above the retransmission curve, the test/simulation flag, or an unexpected source MAC publishing a known gocbRef.

```bash
tshark -r 'data/kios-electron-suc4-power-attacks/Electron_SUC4_S1_FDI_Attack_Traffic.pcapng' -Y 'goose' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
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

**Computed evidence (auto-extracted with tshark — verify it yourself):** IEC 61850 GOOSE packets matching `goose`: 1,138; GOOSE streams — SERVER-GOOSE2LDevice1/LLN0$GO$CB_Goose_4BOOL from 00:26:55:dc:cd:cf: 715 frames, 8 distinct stNum, 230 sqNum resets; SERVER-GOOSE1LDevice1/LLN0$GO$CB_Goose_2BOOL from ac:1f:6b:69:c4:35: 423 frames, 6 distinct stNum, 10 sqNum resets; top conversations in Electron_SUC4_S2_MS_Attack_Traffic.pcapng: 192.168.20.82↔194.42.14.97 (112 pkts), 192.168.20.82↔8.8.8.8 (107 pkts), 192.168.20.1,192.168.20.82↔192.168.20.82,194.42.14.97 (56 pkts) (basis: 3 of 4 capture file(s), first 300,000 packets each, smallest files carrying IEC 61850 GOOSE chosen)

_Dataset credit: Tekki, Eleni; Hadjidemetriou, Lenos; Asprou, Markos; Ciornei, Irina (2024) — doi:10.5281/zenodo.12960228 · License: CC BY 4.0._

</details>

## Dataset & credit

**Tekki, Eleni; Hadjidemetriou, Lenos; Asprou, Markos; Ciornei, Irina (2024) — doi:10.5281/zenodo.12960228** — license: CC BY 4.0

- [Dataset source — KIOS/ELECTRON SUC4 — FDI and masquerade attacks on a power s](https://zenodo.org/records/12960228)
- [DOI 10.5281/zenodo.12960228](https://doi.org/10.5281/zenodo.12960228)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (4)</summary>

- `data/kios-electron-suc4-power-attacks/Electron_SUC4_S1_FDI_Attack_Traffic.pcapng`
- `data/kios-electron-suc4-power-attacks/Electron_SUC4_S1_Without_Attack_Traffic.pcapng`
- `data/kios-electron-suc4-power-attacks/Electron_SUC4_S2_MS_Attack_Traffic.pcapng`
- `data/kios-electron-suc4-power-attacks/Electron_SUC4_S2_Without_Attack_Traffic.pcapng`

</details>
