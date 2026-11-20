# Protocol deep-dive — ROC Plus (3 unique captures)

**Protocol library** · **Easy** · 0.0 MB · 2 capture file(s)

> A deduplicated library of 3 ROC Plus captures from 2 public collections. Learn the protocol's grammar, then hunt its dangerous operations.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Every public ROC Plus sample in this range, deduplicated by SHA-256 across cisa-icsnpp-test-traces, inl-malcolm-ot-artifacts. Use it to learn what the protocol looks like on the wire — roles, operations, normal cadence — and to practice spotting the operations attackers abuse: Emerson ROC Plus (oil &amp; gas flow computers) has no Wireshark dissector — use CISA's Zeek ICSNPP roc-plus parser; parameter writes and configuration changes are the targets.

## Objectives

- Identify clients/masters and servers/outstations across the samples.
- Enumerate the ROC Plus operations present.
- Flag every dangerous operation and its source.
- Map findings to ATT&amp;CK for ICS (T0836 Modify Parameter).

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch its 2 datasets first, from the repo root:

```bash
python3 scripts/fetch.py cisa-icsnpp-test-traces inl-malcolm-ot-artifacts
```

- **[CISA ICSNPP — Zeek ICS parser test traces](../DATASETS.md#cisa-icsnpp-test-traces)** (`cisa-icsnpp-test-traces`), ~14.8 MB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (3.3 MB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/cisa-icsnpp-test-traces.tar.part000) (3.3 MB)
  - **Original source:** [github.com/cisagov/ICSNPP](https://github.com/cisagov/ICSNPP)
- **[INL Malcolm test artifacts — OT protocol samples](../DATASETS.md#inl-malcolm-ot-artifacts)** (`inl-malcolm-ot-artifacts`), ~99.2 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/idaholab/Malcolm-Test-Artifacts](https://github.com/idaholab/Malcolm-Test-Artifacts)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-roc-plus/all_opcodes_udp.pcap' --overview
```

**2. Deep-dive with Pcapper (--overview)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-roc-plus/all_opcodes_udp.pcap' --overview --ot-commands
```

**3. Sweep the whole library**

```bash
pcapper data/cisa-icsnpp-test-traces/ --overview --ot-commands
```

**4. Every control and write, normalized**

--ot-commands lists every OT control/write command across protocols; --threats consolidates Pcapper's detections.

```bash
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-roc-plus/all_opcodes_udp.pcap' --ot-commands --threats
```

**5. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-roc-plus/all_opcodes_udp.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/cisa-icsnpp-test-traces/icsnpp-roc-plus/all_opcodes_udp.pcap'
tshark -r 'data/cisa-icsnpp-test-traces/icsnpp-roc-plus/all_opcodes_udp.pcap' -q -z io,phs | head -40
```

**2. Map the ROC Plus conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/cisa-icsnpp-test-traces/icsnpp-roc-plus/all_opcodes_udp.pcap' -Y 'tcp.port == 4000 || udp.port == 4000' -T fields -e ip.src -e ip.dst -e tcp.dstport -e udp.dstport | sort | uniq -c | sort -rn | head -20
```

**3. Hunt the dangerous operations**

Flag Emerson ROC Plus (oil &amp; gas flow computers) has no Wireshark dissector — use CISA's Zeek ICSNPP roc-plus parser; parameter writes and configuration changes are the targets.

```bash
tshark -r 'data/cisa-icsnpp-test-traces/icsnpp-roc-plus/all_opcodes_udp.pcap' -Y 'tcp.port == 4000 || udp.port == 4000' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Sweep the whole library**

```bash
for f in 'data/cisa-icsnpp-test-traces/icsnpp-roc-plus/all_opcodes_udp.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-roc-plus/all_opcodes_tcp.pcap' 'data/inl-malcolm-ot-artifacts/Malcolm-Test-Artifacts-main/pcap/protocols/ROCPlus.pcap'; do echo "== $f"; tshark -r "$f" -Y 'tcp.port == 4000 || udp.port == 4000' 2>/dev/null | head -3; done
```

## Hints

<details><summary>Hint 1</summary>

Wireshark display filter for the protocol: tcp.port == 4000 || udp.port == 4000

</details>

<details><summary>Hint 2</summary>

Dangerous-operation filter: tcp.port == 4000 || udp.port == 4000

</details>

<details><summary>Hint 3</summary>

Many library files are tiny protocol samples — read them packet by packet in Wireshark.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

A library, not a single puzzle: the deliverable is a per-capture table of roles and operations, with the dangerous ones flagged (Emerson ROC Plus (oil &amp; gas flow computers) has no Wireshark dissector — use CISA's Zeek ICSNPP roc-plus parser; parameter writes and configuration changes are the targets). ATT&amp;CK for ICS: T0836 Modify Parameter. Sources are credited per collection in each folder's PROVENANCE.md.

**Computed evidence (auto-extracted with tshark — verify it yourself):** ROC Plus packets matching `tcp.port == 4000 || udp.port == 4000`: 666; dangerous-operation matches: 666 (top sources: 192.168.1.200 ×344, 192.168.1.100 ×322); top conversations in all_opcodes_udp.pcap: 192.168.1.100↔192.168.1.200 (109 pkts) (basis: 3 of 3 capture file(s), first 300,000 packets each)

_Captures credited to: CISA ICSNPP — Zeek ICS parser test traces — CISA and Idaho National Laboratory (ICSNPP project) · INL Malcolm test artifacts — OT protocol samples — Idaho National Laboratory (Malcolm)._

</details>

## Dataset & credit

**CISA ICSNPP — Zeek ICS parser test traces — CISA and Idaho National Laboratory (ICSNPP project) · INL Malcolm test artifacts — OT protocol samples — Idaho National Laboratory (Malcolm)** — license: varies by collection — see each folder's PROVENANCE.md

- [Dataset source — CISA ICSNPP — Zeek ICS parser test traces](https://github.com/cisagov/ICSNPP)
- [Dataset source — INL Malcolm test artifacts — OT protocol samples](https://github.com/idaholab/Malcolm-Test-Artifacts)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (2)</summary>

- `data/cisa-icsnpp-test-traces/icsnpp-roc-plus/all_opcodes_udp.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-roc-plus/all_opcodes_tcp.pcap`

</details>
