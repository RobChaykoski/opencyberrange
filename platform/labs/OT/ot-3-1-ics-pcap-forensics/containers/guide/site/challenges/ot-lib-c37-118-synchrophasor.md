# Protocol deep-dive — C37.118 synchrophasor (13 unique captures)

**Protocol library** · **Medium** · 3.9 MB · 10 capture file(s)

> A deduplicated library of 13 C37.118 synchrophasor captures from 3 public collections. Learn the protocol's grammar, then hunt its dangerous operations.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Every public C37.118 synchrophasor sample in this range, deduplicated by SHA-256 across cisa-icsnpp-test-traces, inl-malcolm-ot-artifacts, iti-ics-security-tools-pcaps. Use it to learn what the protocol looks like on the wire — roles, operations, normal cadence — and to practice spotting the operations attackers abuse: command frames (frame type 4) can turn PMU data transmission off or request configuration — normal from the PDC, suspicious from anywhere else.

## Objectives

- Identify clients/masters and servers/outstations across the samples.
- Enumerate the C37.118 synchrophasor operations present.
- Flag every dangerous operation and its source.
- Map findings to ATT&amp;CK for ICS (T0855 Unauthorized Command Message · T0815 Denial of View).

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch its 3 datasets first, from the repo root:

```bash
python3 scripts/fetch.py cisa-icsnpp-test-traces inl-malcolm-ot-artifacts iti-ics-security-tools-pcaps
```

- **[CISA ICSNPP — Zeek ICS parser test traces](../DATASETS.md#cisa-icsnpp-test-traces)** (`cisa-icsnpp-test-traces`), ~14.8 MB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (3.3 MB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/cisa-icsnpp-test-traces.tar.part000) (3.3 MB)
  - **Original source:** [github.com/cisagov/ICSNPP](https://github.com/cisagov/ICSNPP)
- **[INL Malcolm test artifacts — OT protocol samples](../DATASETS.md#inl-malcolm-ot-artifacts)** (`inl-malcolm-ot-artifacts`), ~99.2 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/idaholab/Malcolm-Test-Artifacts](https://github.com/idaholab/Malcolm-Test-Artifacts)
- **[ITI ICS-Security-Tools — sample ICS protocol captures](../DATASETS.md#iti-ics-security-tools-pcaps)** (`iti-ics-security-tools-pcaps`), ~0.12 GB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/ITI/ICS-Security-Tools/tree/master/pcaps](https://github.com/ITI/ICS-Security-Tools/tree/master/pcaps)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-synchrophasor/c37_pmu_clean.pcap' --overview
```

**2. Deep-dive with Pcapper (--synchrophasor)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-synchrophasor/c37_pmu_clean.pcap' --synchrophasor --ot-commands
```

**3. Sweep the whole library**

```bash
pcapper data/cisa-icsnpp-test-traces/ --synchrophasor --ot-commands
```

**4. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-synchrophasor/c37_pmu_clean.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/cisa-icsnpp-test-traces/icsnpp-synchrophasor/c37_pmu_clean.pcap'
tshark -r 'data/cisa-icsnpp-test-traces/icsnpp-synchrophasor/c37_pmu_clean.pcap' -q -z io,phs | head -40
```

**2. Map the C37.118 synchrophasor conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/cisa-icsnpp-test-traces/icsnpp-synchrophasor/c37_pmu_clean.pcap' -Y synphasor -T fields -e ip.src -e ip.dst -e synphasor.frtype -e synphasor.idcode_stream_source | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag command frames (frame type 4) can turn PMU data transmission off or request configuration — normal from the PDC, suspicious from anywhere else.

```bash
tshark -r 'data/cisa-icsnpp-test-traces/icsnpp-synchrophasor/c37_pmu_clean.pcap' -Y 'synphasor.frtype == 4' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Sweep the whole library**

```bash
for f in 'data/cisa-icsnpp-test-traces/icsnpp-synchrophasor/c37_pmu_clean.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-synchrophasor/C37.118_1PMU_UDP_minimal.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-synchrophasor/c37118_1100_unclean.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-synchrophasor/C37.118_2PMUsInSync_TCP.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-synchrophasor/c37_1100_fullclean.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-synchrophasor/C37.118_4in1PMU_TCP.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-synchrophasor/c37_1100_clean_tcp.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-synchrophasor/c37_pmu_unclean.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-synchrophasor/C37.118_1PMU_TCP.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-synchrophasor/C37.118_1PMU_UDP.pcap'; do echo "== $f"; tshark -r "$f" -Y 'synphasor.frtype == 4' 2>/dev/null | head -3; done
```

## Hints

<details><summary>Hint 1</summary>

Wireshark display filter for the protocol: synphasor

</details>

<details><summary>Hint 2</summary>

Dangerous-operation filter: synphasor.frtype == 4

</details>

<details><summary>Hint 3</summary>

Many library files are tiny protocol samples — read them packet by packet in Wireshark.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

A library, not a single puzzle: the deliverable is a per-capture table of roles and operations, with the dangerous ones flagged (command frames (frame type 4) can turn PMU data transmission off or request configuration — normal from the PDC, suspicious from anywhere else). ATT&amp;CK for ICS: T0855 Unauthorized Command Message · T0815 Denial of View. Sources are credited per collection in each folder's PROVENANCE.md.

**Computed evidence (auto-extracted with tshark — verify it yourself):** C37.118 synchrophasor operations — data ×609, command ×10, config-2 ×3; dangerous-operation matches: 10 (top sources: 192.168.0.10 ×7, 192.168.0.20 ×3); top conversations in C37.118_1PMU_UDP_minimal.pcap: 192.168.0.10↔192.168.0.60 (5 pkts) (basis: 3 of 13 capture file(s), first 300,000 packets each, smallest files carrying C37.118 synchrophasor chosen)

_Captures credited to: CISA ICSNPP — Zeek ICS parser test traces — CISA and Idaho National Laboratory (ICSNPP project) · INL Malcolm test artifacts — OT protocol samples — Idaho National Laboratory (Malcolm) · ITI ICS-Security-Tools — sample ICS protocol captures — Information Trust Institute (ITI), University of Illinois Urbana-Champaign._

</details>

## Dataset & credit

**CISA ICSNPP — Zeek ICS parser test traces — CISA and Idaho National Laboratory (ICSNPP project) · INL Malcolm test artifacts — OT protocol samples — Idaho National Laboratory (Malcolm) · ITI ICS-Security-Tools — sample ICS protocol captures — Information Trust Institute (ITI), University of Illinois Urbana-Champaign** — license: varies by collection — see each folder's PROVENANCE.md

- [Dataset source — CISA ICSNPP — Zeek ICS parser test traces](https://github.com/cisagov/ICSNPP)
- [Dataset source — INL Malcolm test artifacts — OT protocol samples](https://github.com/idaholab/Malcolm-Test-Artifacts)
- [Dataset source — ITI ICS-Security-Tools — sample ICS protocol captures](https://github.com/ITI/ICS-Security-Tools/tree/master/pcaps)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (10)</summary>

- `data/cisa-icsnpp-test-traces/icsnpp-synchrophasor/c37_pmu_clean.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-synchrophasor/C37.118_1PMU_UDP_minimal.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-synchrophasor/c37118_1100_unclean.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-synchrophasor/C37.118_2PMUsInSync_TCP.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-synchrophasor/c37_1100_fullclean.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-synchrophasor/C37.118_4in1PMU_TCP.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-synchrophasor/c37_1100_clean_tcp.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-synchrophasor/c37_pmu_unclean.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-synchrophasor/C37.118_1PMU_TCP.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-synchrophasor/C37.118_1PMU_UDP.pcap`

</details>
