# Cyber4OT — Modbus Recon &amp; PLC Hijacking

**Process control &amp; PLC testbeds** · **Medium** · 0.0 MB · 0 capture file(s)

> 96 small Modbus/TCP traces: normal OT activity, reconnaissance, and PLC-hijacking / interruption attacks.

> ⚠️ **Safety:** Passive Modbus analysis only. Do not replay write commands toward any real PLC.

## Scenario

The Cyber4OT trace set: 96 PCAPNG captures of Modbus/TCP activity spanning normal operation, OT reconnaissance, and interruption / PLC-hijacking attacks. Small and focused — ideal for learning the Modbus attack surface precisely.

## Objectives

- Separate normal Modbus polling from recon and attack traces.
- Identify abusive function codes (writes to coils/registers).
- Spot an unauthorized master hijacking the PLC.
- Map findings to ATT&amp;CK for ICS techniques.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py cyber4ot
```

- **[Cyber4OT: ICS network traces containing normal activity and full attack traffic](../DATASETS.md#cyber4ot)** (`cyber4ot`), ~0.40 GB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (69.0 MB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/cyber4ot.tar.part000) (69.0 MB)
  - **Original source:** [zenodo.org/records/15005190](https://zenodo.org/records/15005190) · [doi:10.5281/zenodo.15005190](https://doi.org/10.5281/zenodo.15005190)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage with Pcapper**

Pcapper auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/cyber4ot/data/traces/Cyber4OT_001.pcapng' --overview
```

**2. Inventory the traces**

```bash
ls data/cyber4ot/data/traces/ | head
# read the accompanying README describing each trace
```

**3. Normalize every OT command with Pcapper**

```bash
pcapper 'data/cyber4ot/data/traces/Cyber4OT_001.pcapng' --ot-commands --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/cyber4ot/data/traces/Cyber4OT_001.pcapng'
tshark -r 'data/cyber4ot/data/traces/Cyber4OT_001.pcapng' -q -z io,phs | head -40
```

**2. Inventory the traces**

```bash
ls data/cyber4ot/data/traces/ | head
# read the accompanying README describing each trace
```

**3. Modbus function-code profile**

Reads (fc 1-4) are normal polling; writes (fc 5/6/15/16) to a PLC are the interesting ones.

```bash
for f in data/cyber4ot/data/traces/*.pcapng; do c=$(tshark -r "$f" -Y modbus -T fields -e modbus.func_code 2>/dev/null | sort -u | tr '\n' ','); echo "$c  $f"; done | head
```

**4. Find the recon**

Sequential register sweeps = enumeration of the PLC's memory map.

```bash
tshark -r <recon>.pcapng -Y 'modbus' -T fields -e ip.src -e modbus.func_code -e modbus.reference_num | head
```

**5. Catch the hijack**

An unexpected source issuing writes = the hijacking master.

```bash
tshark -r <attack>.pcapng -Y 'modbus.func_code==5 || modbus.func_code==6 || modbus.func_code==16' -T fields -e ip.src -e modbus.func_code
```

## Hints

<details><summary>Hint 1</summary>

Function codes 1-4 are reads (normal); 5/6/15/16 are writes (control).

</details>

<details><summary>Hint 2</summary>

A new source IP suddenly writing to coils/registers is the PLC hijack.

</details>

<details><summary>Hint 3</summary>

The README names each trace — use it to check your classification.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

Classify each trace by its Modbus function-code profile and source set: read-only polling = normal; sequential reads from a new host = reconnaissance; unexpected writes (fc 5/6/15/16) from an unauthorized master = interruption / PLC hijacking. The dataset README gives the ground-truth label per trace.

</details>

## Dataset & credit

**Cabaj, K., Plamowski, S., Chaber, P., Ławryńczuk, M., Marusak, P., Nebeluk, R., Wojtulewicz, A. &amp; Zarzycki, K. (2025) — DOI 10.5281/zenodo.15005190 — CC BY-NC 4.0.** — license: CC BY-NC 4.0 (non-commercial)

- [Cyber4OT dataset (Zenodo)](https://zenodo.org/records/15005190)
- [DOI 10.5281/zenodo.15005190](https://doi.org/10.5281/zenodo.15005190)

<details><summary>Capture files (96)</summary>

- `data/cyber4ot/data/traces/Cyber4OT_001.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_002.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_003.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_004.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_005.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_006.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_007.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_008.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_009.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_010.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_011.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_012.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_013.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_014.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_015.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_016.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_017.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_018.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_019.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_020.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_021.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_022.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_023.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_024.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_025.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_026.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_027.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_028.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_029.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_030.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_031.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_032.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_033.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_034.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_035.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_036.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_037.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_038.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_039.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_040.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_041.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_042.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_043.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_044.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_045.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_046.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_047.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_048.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_049.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_050.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_051.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_052.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_053.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_054.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_055.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_056.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_057.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_058.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_059.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_060.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_061.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_062.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_063.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_064.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_065.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_066.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_067.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_068.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_069.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_070.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_071.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_072.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_073.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_074.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_075.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_076.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_077.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_078.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_079.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_080.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_081.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_082.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_083.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_084.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_085.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_086.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_087.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_088.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_089.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_090.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_091.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_092.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_093.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_094.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_095.pcapng`
- `data/cyber4ot/data/traces/Cyber4OT_096.pcapng`

</details>
