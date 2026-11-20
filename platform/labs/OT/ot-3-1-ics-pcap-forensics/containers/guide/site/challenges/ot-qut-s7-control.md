# QUT S7comm — the plant's normal session

**Process control &amp; PLC testbeds** · **Easy** · 0.0 MB · 0 capture file(s)

> Learn the S7 plant's normal polling before you attack-hunt.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

QUT built a small Siemens S7 process plant — a reactor, a conveyor belt with a diverter gate and a water tank, controlled by S7 PLCs and an HMI — and attacked it with crafted S7comm writes from an attacker host. Each attack run was captured from the **attacker**, the **HMI** and the **master** PLC.

This is the **control set**: no attacks. Baseline the HMI↔PLC S7comm traffic.

## Objectives

- Identify the HMI, PLCs and the (idle) attacker host.
- List the S7 functions and addresses polled, and their cadence.
- Note any writes in normal operation.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py qut-s7comm-2017
```

- **[QUT 2017 S7comm — mining-refinery testbed (64 attacks, 13 types)](../DATASETS.md#qut-s7comm-2017)** (`qut-s7comm-2017`), ~0.96 GB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/qut-infosec/2017QUT_S7comm](https://github.com/qut-infosec/2017QUT_S7comm)

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the master's view**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161219132813_control_set/attacker.pcap' --overview
```

**2. Deep-dive with Pcapper (--s7)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161219132813_control_set/attacker.pcap' --s7 --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161219132813_control_set/attacker.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the master's view**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161219132813_control_set/attacker.pcap'
tshark -r 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161219132813_control_set/attacker.pcap' -q -z io,phs | head -40
```

**2. Map the S7comm conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161219132813_control_set/attacker.pcap' -Y s7comm -T fields -e ip.src -e ip.dst -e s7comm.header.rosctr -e s7comm.param.func -e s7comm.param.userdata.funcgroup -e s7comm.param.userdata.subfunc | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag write variable (0x05), program download (0x1A–0x1C), program upload (0x1D–0x1F — logic theft), PI-service (0x28 — start/restart/compress), PLC STOP (0x29) and security/password userdata (function group 5); SZL reads (function group 4) are device recon.

```bash
tshark -r 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161219132813_control_set/attacker.pcap' -Y 's7comm.param.func in {0x05, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 0x28, 0x29} || s7comm.param.userdata.funcgroup == 5' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

## Hints

<details><summary>Hint 1</summary>

Count Read Var vs Write Var per source.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

Baseline only: HMI/PLC identities, the polled addresses and the polling interval. Use it to explain the attack sessions.

**Computed evidence (auto-extracted with tshark — verify it yourself):** S7comm operations — Read Var ×338378, Write Var ×992, Setup Communication ×4, CPU services ×4; dangerous-operation matches: 992 (top sources: 10.10.10.20 ×496, 10.10.10.10 ×496); top conversations in hmi.pcap: 10.10.10.10↔10.10.10.20 (279,629 pkts), 10.10.10.200↔255.255.255.255 (2,666 pkts), 10.10.10.20↔10.10.10.255 (93 pkts) (basis: 2 of 3 capture file(s), first 300,000 packets each)

_Dataset credit: Rodofile, N. R., Radke, K., Foo, E. (Queensland University of Technology) (2017) · License: No license stated — credit the authors._

</details>

## Dataset & credit

**Rodofile, N. R., Radke, K., Foo, E. (Queensland University of Technology) (2017)** — license: No license stated — credit the authors

- [Dataset source — QUT 2017 S7comm — mining-refinery testbed (64 attacks, 13 ty](https://github.com/qut-infosec/2017QUT_S7comm)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (3)</summary>

- `data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161219132813_control_set/attacker.pcap`
- `data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161219132813_control_set/hmi.pcap/hmi.pcap`
- `data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161219132813_control_set/master.pcap/master.pcap`

</details>
