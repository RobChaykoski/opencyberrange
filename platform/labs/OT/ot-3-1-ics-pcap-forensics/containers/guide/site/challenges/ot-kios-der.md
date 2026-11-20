# KIOS — attacks on DER energy management &amp; control

**Power grid &amp; substations** · **Hard** · 0.0 MB · 0 capture file(s)

> Cyberattack scenarios against distributed-energy-resource energy management and control.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Cyberattack scenarios against distributed-energy-resource energy management and control.

Sandboxing use case on distributed-energy-resource (DER) energy management: attack scenarios S1–S4 against market-following generation control.

## Objectives

- Identify devices and protocol roles.
- Find and characterize the malicious activity.
- Use the dataset's labels/companion files to check yourself.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py kios-der-energy-mgmt-attacks
```

- **[KIOS — cyberattack scenarios on DER energy management &amp; control](../DATASETS.md#kios-der-energy-mgmt-attacks)** (`kios-der-energy-mgmt-attacks`), ~0.3 MB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (0.3 MB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/kios-der-energy-mgmt-attacks.tar.part000) (0.3 MB)
  - **Original source:** [zenodo.org/records/12773981](https://zenodo.org/records/12773981) · [doi:10.5281/zenodo.12773981](https://doi.org/10.5281/zenodo.12773981)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/kios-der-energy-mgmt-attacks/Electron_SUC1_S4_Modbus_Attack_Traffic.pcapng' --overview
```

**2. Deep-dive with Pcapper (--modbus)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/kios-der-energy-mgmt-attacks/Electron_SUC1_S4_Modbus_Attack_Traffic.pcapng' --modbus --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/kios-der-energy-mgmt-attacks/Electron_SUC1_S4_Modbus_Attack_Traffic.pcapng' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/kios-der-energy-mgmt-attacks/Electron_SUC1_S4_Modbus_Attack_Traffic.pcapng'
tshark -r 'data/kios-der-energy-mgmt-attacks/Electron_SUC1_S4_Modbus_Attack_Traffic.pcapng' -q -z io,phs | head -40
```

**2. Map the Modbus/TCP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/kios-der-energy-mgmt-attacks/Electron_SUC1_S4_Modbus_Attack_Traffic.pcapng' -Y mbtcp -T fields -e ip.src -e ip.dst -e mbtcp.unit_id -e modbus.func_code | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag writes (FC 5/6/15/16/22/23), diagnostics (FC 8 — restart / force-listen-only), device identification (FC 43/14, recon) and Schneider UMAS (FC 90, engineering).

```bash
tshark -r 'data/kios-der-energy-mgmt-attacks/Electron_SUC1_S4_Modbus_Attack_Traffic.pcapng' -Y 'modbus.func_code in {5, 6, 15, 16, 22, 23, 8, 43, 90}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
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

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Read Holding Registers ×137, Write Multiple Registers ×68; dangerous-operation matches: 68 (top sources: 192.168.20.54 ×34, 192.168.20.59 ×34); top conversations in Electron_SUC1_S4_Modbus_Attack_Traffic.pcapng: 192.168.20.54↔192.168.20.59 (568 pkts) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: Hadjidemetriou, Lenos; Asprou, Markos; Ciornei, Irina; Charalambous, Charalambos; Tekki, Eleni (2024) — doi:10.5281/zenodo.12773981 · License: CC BY 4.0._

</details>

## Dataset & credit

**Hadjidemetriou, Lenos; Asprou, Markos; Ciornei, Irina; Charalambous, Charalambos; Tekki, Eleni (2024) — doi:10.5281/zenodo.12773981** — license: CC BY 4.0

- [Dataset source — KIOS — cyberattack scenarios on DER energy management &amp; cont](https://zenodo.org/records/12773981)
- [DOI 10.5281/zenodo.12773981](https://doi.org/10.5281/zenodo.12773981)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/kios-der-energy-mgmt-attacks/Electron_SUC1_S4_Modbus_Attack_Traffic.pcapng`

</details>
