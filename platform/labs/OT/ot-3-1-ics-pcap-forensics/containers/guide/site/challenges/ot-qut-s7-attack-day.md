# QUT S7comm — hunt the whole attack session

**Process control &amp; PLC testbeds** · **Expert** · 0.0 MB · 0 capture file(s)

> Every attack run in one long session. Find them all, in order.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

QUT built a small Siemens S7 process plant — a reactor, a conveyor belt with a diverter gate and a water tank, controlled by S7 PLCs and an HMI — and attacked it with crafted S7comm writes from an attacker host. Each attack run was captured from the **attacker**, the **HMI** and the **master** PLC.

This is the complete attack session (22 labelled attack types, 64 runs) captured continuously. The individual run folders are the answer key.

## Objectives

- Baseline the HMI↔PLC polling.
- Find every attacker write and its time.
- Name the process effect of each.
- Reconstruct the attack timeline.

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
pcapper 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/attacker.pcap/attacker.pcap' --overview
```

**2. Deep-dive with Pcapper (--s7)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/attacker.pcap/attacker.pcap' --s7 --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/attacker.pcap/attacker.pcap' --mitre
```

**4. Check yourself against the run folders**

```bash
ls 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830' | head -80
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the master's view**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/attacker.pcap/attacker.pcap'
tshark -r 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/attacker.pcap/attacker.pcap' -q -z io,phs | head -40
```

**2. Map the S7comm conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/attacker.pcap/attacker.pcap' -Y s7comm -T fields -e ip.src -e ip.dst -e s7comm.header.rosctr -e s7comm.param.func -e s7comm.param.userdata.funcgroup -e s7comm.param.userdata.subfunc | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag write variable (0x05), program download (0x1A–0x1C), program upload (0x1D–0x1F — logic theft), PI-service (0x28 — start/restart/compress), PLC STOP (0x29) and security/password userdata (function group 5); SZL reads (function group 4) are device recon.

```bash
tshark -r 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/attacker.pcap/attacker.pcap' -Y 's7comm.param.func in {0x05, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 0x28, 0x29} || s7comm.param.userdata.funcgroup == 5' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Every write in the session**

```bash
tshark -r 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/attacker.pcap/attacker.pcap' -Y 's7comm.param.func == 0x05' -T fields -e frame.time -e ip.src -e ip.dst -e s7comm.param.item.area -e s7comm.param.item.db -e s7comm.param.item.address | head -80
```

**5. Check yourself against the run folders**

```bash
ls 'data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/20161216202830' | head -80
```

## Hints

<details><summary>Hint 1</summary>

Legitimate writes come from the HMI; the attacker host is the odd one out.

</details>

<details><summary>Hint 2</summary>

Solve the per-area QUT S7comm challenges first to know the tag map.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

The run folders (timestamp.AttackName) list every attack in order; the attacker logs under Logs/ give its timing. Score yourself on attacks found and correctly named.

**Computed evidence (auto-extracted with tshark — verify it yourself):** S7comm operations — Write Var ×445623, Read Var ×249423, Setup Communication ×10, CPU services ×4; dangerous-operation matches: 445623 (top sources: 10.10.10.10 ×222813, 10.10.10.66 ×221825, 10.10.10.20 ×985); top conversations in attacker.pcap: 10.10.10.10↔10.10.10.66 (292,394 pkts), 10.10.10.200↔255.255.255.255 (466 pkts), 10.10.10.20↔10.10.10.255 (29 pkts) (basis: 3 of 3 capture file(s), first 300,000 packets each)

_Dataset credit: Rodofile, N. R., Radke, K., Foo, E. (Queensland University of Technology) (2017) · License: No license stated — credit the authors._

</details>

## Dataset & credit

**Rodofile, N. R., Radke, K., Foo, E. (Queensland University of Technology) (2017)** — license: No license stated — credit the authors

- [Dataset source — QUT 2017 S7comm — mining-refinery testbed (64 attacks, 13 ty](https://github.com/qut-infosec/2017QUT_S7comm)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (3)</summary>

- `data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/attacker.pcap/attacker.pcap`
- `data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/hmi.pcap/hmi.pcap`
- `data/qut-s7comm-2017/2017QUT_S7comm-master/LabelledDataset/20161215163606_s7_process_attacks/master.pcap/master.pcap`

</details>
