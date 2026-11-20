# Lemay SCADA — MS08-067 exploitation inside the control network

**ICS malware &amp; intrusions** · **Hard** · 0.0 MB · 0 capture file(s)

> A Windows host on the SCADA LAN gets exploited with MS08-067 while the polling carries on. Find the exploit in the noise.

> ⚠️ **Safety:** Contains live exploit/malware traffic. Carve and hash only — never execute, and never replay. This capture carries executable files (Windows PE / Linux ELF) inside the traffic, and some may be malware: work offline, hash anything you extract and never run it.

## Scenario

Lemay &amp; Fernandez (CSET 2016) built simulated SCADA networks — a master polling Modbus RTUs — and recorded normal operation plus labelled malicious activity, to give ICS intrusion-detection research realistic data.

A Windows host on the SCADA LAN gets exploited with MS08-067 while the polling carries on. Find the exploit in the noise.

## Objectives

- Separate normal polling from everything else.
- Identify the malicious activity, its source and its targets.
- Explain how a defender would detect it.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py lemay-scada-modbus-cset2016
```

- **[Lemay &amp; Fernandez SCADA Modbus dataset (CSET 2016)](../DATASETS.md#lemay-scada-modbus-cset2016)** (`lemay-scada-modbus-cset2016`), ~84.5 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/antoine-lemay/Modbus_dataset](https://github.com/antoine-lemay/Modbus_dataset)

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage with Pcapper**

```bash
pcapper 'data/lemay-scada-modbus-cset2016/exploit_ms08_netapi_modbus_6RTU_with_operate.pcap' --overview
```

**2. Normalize all control operations**

```bash
pcapper 'data/lemay-scada-modbus-cset2016/exploit_ms08_netapi_modbus_6RTU_with_operate.pcap' --modbus --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/lemay-scada-modbus-cset2016/exploit_ms08_netapi_modbus_6RTU_with_operate.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage with Pcapper**

```bash
capinfos 'data/lemay-scada-modbus-cset2016/exploit_ms08_netapi_modbus_6RTU_with_operate.pcap'
tshark -r 'data/lemay-scada-modbus-cset2016/exploit_ms08_netapi_modbus_6RTU_with_operate.pcap' -q -z io,phs | head -40
```

**2. Who talks to whom**

```bash
tshark -r 'data/lemay-scada-modbus-cset2016/exploit_ms08_netapi_modbus_6RTU_with_operate.pcap' -q -z conv,tcp | head -25
```

**3. Find the non-SCADA traffic**

On a pure polling network, anything that isn't Modbus deserves a look.

```bash
tshark -r 'data/lemay-scada-modbus-cset2016/exploit_ms08_netapi_modbus_6RTU_with_operate.pcap' -Y '!mbtcp && tcp' -q -z conv,tcp | head -20
tshark -r 'data/lemay-scada-modbus-cset2016/exploit_ms08_netapi_modbus_6RTU_with_operate.pcap' -Y 'smb || smb2 || dcerpc' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

## Hints

<details><summary>Hint 1</summary>

Do the baseline challenge first — the attacks only stand out against the normal cycle.

</details>

<details><summary>Hint 2</summary>

Anything that isn't Modbus on this network is suspicious by default.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

An attacker exploits MS08-067 (the Windows Server service / NetAPI vulnerability) over SMB/DCE-RPC on TCP 445 against a Windows host on the SCADA network — the IT-style compromise that precedes OT impact. Look for SMB/DCERPC traffic to 445 that has no place on a polling network, and what that host does next. The capture's filename is the dataset's ground-truth label.

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Read Holding Registers ×48, Read Discrete Inputs ×48, Read Coils ×48; dangerous-operation matches: 0 for the Modbus/TCP filter (144 Modbus/TCP packets present, so the zero is real); top conversations in exploit_ms08_netapi_modbus_6RTU_with_operate.pcap: 192.168.1.101↔192.168.1.105 (1,200 pkts), 192.168.1.100↔192.168.1.105 (108 pkts), 192.168.1.100↔192.168.1.101 (108 pkts) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: Antoine Lemay &amp; José M. Fernandez (Polytechnique Montréal) (2016) · License: No license stated in repo — credit the author._

</details>

## Dataset & credit

**Antoine Lemay &amp; José M. Fernandez (Polytechnique Montréal) (2016)** — license: No license stated in repo — credit the author

- [Dataset source — Lemay &amp; Fernandez SCADA Modbus dataset (CSET 2016)](https://github.com/antoine-lemay/Modbus_dataset)
- [Lemay &amp; Fernandez, CSET '16 (USENIX)](https://www.usenix.org/conference/cset16/workshop-program/presentation/lemay)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/lemay-scada-modbus-cset2016/exploit_ms08_netapi_modbus_6RTU_with_operate.pcap`

</details>
