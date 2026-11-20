# TRITON/TRISIS — TriStation traffic of the SIS malware

**ICS malware &amp; intrusions** · **Expert** · 0.2 MB · 1 capture file(s)

> The engineering-protocol traffic of TRITON, the first malware built to attack a safety instrumented system (Schneider Triconex).

> ⚠️ **Safety:** Real ICS-malware protocol traffic against a safety controller. Analyze offline only.

## Scenario

TRITON (a.k.a. TRISIS / HatMan) targeted Schneider Electric Triconex safety controllers at a petrochemical plant in 2017 — malware designed to disable the system that keeps people alive. It talked to the controller using TriStation, Triconex's proprietary engineering protocol on UDP 1502.

Nozomi Networks Labs captured TriStation traffic of the malware's execution against a Triconex setup and released it with their tricotools. Analyze the protocol exchange.

## Objectives

- Identify the engineering workstation and the safety controller.
- Reconstruct the TriStation command sequence.
- Identify the program/memory operations that correspond to TRITON's payload injection.
- Describe how a defender could detect TriStation misuse.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py nozomi-triton-tristation
```

- **[TRITON/TRISIS — TriStation malware execution capture (Nozomi tricotools)](../DATASETS.md#nozomi-triton-tristation)** (`nozomi-triton-tristation`), ~0.2 MB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (0.1 MB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/nozomi-triton-tristation.tar.part000) (0.1 MB)
  - **Original source:** [github.com/NozomiNetworks/tricotools](https://github.com/NozomiNetworks/tricotools)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage with Pcapper's safety analyzer**

--safety detects Triconex/TriStation.

```bash
pcapper 'data/nozomi-triton-tristation/malware_exec.pcap' --safety --overview
```

**2. Map it to ATT&amp;CK for ICS**

```bash
pcapper 'data/nozomi-triton-tristation/malware_exec.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage with Pcapper's safety analyzer**

--safety detects Triconex/TriStation.

```bash
capinfos 'data/nozomi-triton-tristation/malware_exec.pcap'
tshark -r 'data/nozomi-triton-tristation/malware_exec.pcap' -q -z io,phs | head -40
```

**2. Isolate TriStation**

```bash
tshark -r 'data/nozomi-triton-tristation/malware_exec.pcap' -Y 'udp.port == 1502' -T fields -e frame.number -e frame.time_relative -e ip.src -e ip.dst -e udp.length | head -60
```

**3. Decode it properly**

Wireshark has no built-in TriStation dissector; Nozomi Networks' tricotools ships one as a Lua script. The clone is pinned to the commit this walkthrough was written against, and tshark loads the script only if its SHA-256 matches. Read it first anyway: a tshark Lua plugin runs with your privileges.

```bash
git clone https://github.com/NozomiNetworks/tricotools && git -C tricotools checkout --quiet 2f768c8209d96dbb58dfea40c5a5ba9eb51ad6b0
less tricotools/TriStation.lua
echo '05fe82c2fa90a6ca69dd7473ffb220a1bdf4bebece896906d79b2a28a7b08fed  tricotools/TriStation.lua' | sha256sum -c - && tshark -X lua_script:tricotools/TriStation.lua -r 'data/nozomi-triton-tristation/malware_exec.pcap' -Y tristation -V | less
```

## Hints

<details><summary>Hint 1</summary>

Everything interesting is on UDP 1502.

</details>

<details><summary>Hint 2</summary>

Look for the program-download / memory-write style command codes and the payload-sized frames.

</details>

<details><summary>Hint 3</summary>

TRITON's known chain: connect, check controller state, append a program, then inject the payload into memory.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

TRITON used TriStation to (1) identify and check the controller's state, (2) download a modified program, and (3) inject its payload (the inject.bin/imain.bin stages described in public analyses) into the controller's memory, attempting to persist a backdoor in the safety controller's firmware region. On the wire this appears as an engineering session from a workstation to the Triconex on UDP 1502 with program-download/write commands and payload-sized frames. Detection: any TriStation traffic outside a planned engineering window, or from a non-engineering host, is a critical alert — SIS engineering access should be physically keyed and rare.

**Computed evidence (auto-extracted with tshark — verify it yourself):** TriStation packets matching `udp.port == 1502`: 896; dangerous-operation matches: 896 (top sources: 192.168.1.88 ×448, 192.168.1.2 ×448); top conversations in malware_exec.pcap: 192.168.1.2↔192.168.1.88 (896 pkts) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: Nozomi Networks Labs (2018) · License: BSD-3-Clause._

</details>

## Dataset & credit

**Nozomi Networks Labs (2018)** — license: BSD-3-Clause

- [Dataset source — TRITON/TRISIS — TriStation malware execution capture (Nozomi](https://github.com/NozomiNetworks/tricotools)
- [Nozomi Networks — tricotools](https://github.com/NozomiNetworks/tricotools)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/nozomi-triton-tristation/malware_exec.pcap`

</details>
