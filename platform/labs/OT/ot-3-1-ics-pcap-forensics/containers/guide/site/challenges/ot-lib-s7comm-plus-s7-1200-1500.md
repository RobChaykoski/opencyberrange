# Protocol deep-dive — S7comm-plus (S7-1200/1500) (20 unique captures)

**Protocol library** · **Medium** · 0.0 MB · 1 capture file(s)

> A deduplicated library of 20 S7comm-plus (S7-1200/1500) captures from 4 public collections. Learn the protocol's grammar, then hunt its dangerous operations.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Every public S7comm-plus (S7-1200/1500) sample in this range, deduplicated by SHA-256 across cisa-icsnpp-test-traces, emreekin-ics-pcaps, inl-malcolm-ot-artifacts, iti-ics-security-tools-pcaps. Use it to learn what the protocol looks like on the wire — roles, operations, normal cadence — and to practice spotting the operations attackers abuse: S7comm-plus (0x72) from TIA Portal / HMIs to S7-1200/1500 PLCs; version 3 adds a 32-byte integrity digest and tshark has no built-in dissector, so read it structurally: who talks to the PLC, how often, message sizes, and payloads that repeat (a replay repeats its digest).

## Objectives

- Identify clients/masters and servers/outstations across the samples.
- Enumerate the S7comm-plus (S7-1200/1500) operations present.
- Flag every dangerous operation and its source.
- Map findings to ATT&amp;CK for ICS (T0843 Program Download · T0855 Unauthorized Command Message · T0831 Manipulation of Control).

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch its 4 datasets first, from the repo root:

```bash
python3 scripts/fetch.py cisa-icsnpp-test-traces emreekin-ics-pcaps inl-malcolm-ot-artifacts iti-ics-security-tools-pcaps
```

- **[CISA ICSNPP — Zeek ICS parser test traces](../DATASETS.md#cisa-icsnpp-test-traces)** (`cisa-icsnpp-test-traces`), ~14.8 MB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (3.3 MB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/cisa-icsnpp-test-traces.tar.part000) (3.3 MB)
  - **Original source:** [github.com/cisagov/ICSNPP](https://github.com/cisagov/ICSNPP)
- **[ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset](../DATASETS.md#emreekin-ics-pcaps)** (`emreekin-ics-pcaps`), ~0.26 GB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/EmreEkin/ICS-Pcaps](https://github.com/EmreEkin/ICS-Pcaps)
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
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-s7comm/s7comm_plus.pcap' --overview
```

**2. Deep-dive with Pcapper (--s7)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-s7comm/s7comm_plus.pcap' --s7 --ot-commands
```

**3. Sweep the whole library**

```bash
pcapper data/cisa-icsnpp-test-traces/ --s7 --ot-commands
```

**4. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-s7comm/s7comm_plus.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/cisa-icsnpp-test-traces/icsnpp-s7comm/s7comm_plus.pcap'
tshark -r 'data/cisa-icsnpp-test-traces/icsnpp-s7comm/s7comm_plus.pcap' -q -z io,phs | head -40
```

**2. Map the S7comm-plus (S7-1200/1500) conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/cisa-icsnpp-test-traces/icsnpp-s7comm/s7comm_plus.pcap' -Y 'tcp.port == 102 && tcp.payload[0:2] == 03:00 && ((tcp.payload[4:3] == 02:f0:80 && tcp.payload[7] == 0x72 && tcp.payload[8] <= 3) || (tcp.payload[4] == 2 && tcp.payload[5] == 0x72 && tcp.payload[6] <= 3))' -T fields -e ip.src -e ip.dst -e tcp.len | sort | uniq -c | sort -rn | head -25
```

**3. Look for repeated and unusual messages**

S7comm-plus (0x72) from TIA Portal / HMIs to S7-1200/1500 PLCs; version 3 adds a 32-byte integrity digest and tshark has no built-in dissector, so read it structurally: who talks to the PLC, how often, message sizes, and payloads that repeat (a replay repeats its digest).

```bash
tshark -r 'data/cisa-icsnpp-test-traces/icsnpp-s7comm/s7comm_plus.pcap' -Y 'tcp.port == 102 && tcp.payload[0:2] == 03:00 && ((tcp.payload[4:3] == 02:f0:80 && tcp.payload[7] == 0x72 && tcp.payload[8] <= 3) || (tcp.payload[4] == 2 && tcp.payload[5] == 0x72 && tcp.payload[6] <= 3))' -T fields -e ip.src -e tcp.payload | sort | uniq -c | sort -rn | head -15
```

**4. Sweep the whole library**

```bash
for f in 'data/cisa-icsnpp-test-traces/icsnpp-s7comm/s7comm_plus.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/bro/modbus/modbusBig.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/s7/s7-1200-hmi.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/s7/S7-1200-Uploading-OB1-TIAV12.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/s7/V13_1200_TP1200sim_MW100_Int_SPS_5s_MW102_Int_SPS_10s_MW102_ab_1000_Timer_sync.pcapng' 'data/iti-ics-security-tools-pcaps/pcaps/s7/V13_1200_TP1200sim_MW100_Int_SPS_5s_MW102_Int_SPS_10s_MW102_ab_1000_Timer_sync_FehlerbeiMW100.pcapng' 'data/iti-ics-security-tools-pcaps/pcaps/s7/S7-1511-opc-request-all-types.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/s7/S7-1511_db3_var1_HMI.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/s7/S7-1511_db2_var1_HMI.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/s7/S7-1511_db6w0_HMI.pcap'; do echo "== $f"; tshark -r "$f" -Y '' 2>/dev/null | head -3; done
```

## Hints

<details><summary>Hint 1</summary>

Wireshark display filter for the protocol: tcp.port == 102 &amp;&amp; tcp.payload[0:2] == 03:00 &amp;&amp; ((tcp.payload[4:3] == 02:f0:80 &amp;&amp; tcp.payload[7] == 0x72 &amp;&amp; tcp.payload[8] &lt;= 3) || (tcp.payload[4] == 2 &amp;&amp; tcp.payload[5] == 0x72 &amp;&amp; tcp.payload[6] &lt;= 3))

</details>

<details><summary>Hint 2</summary>

Dangerous-operation filter: 

</details>

<details><summary>Hint 3</summary>

Many library files are tiny protocol samples — read them packet by packet in Wireshark.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

A library, not a single puzzle: the deliverable is a per-capture table of roles and operations, with the dangerous ones flagged (S7comm-plus (0x72) from TIA Portal / HMIs to S7-1200/1500 PLCs; version 3 adds a 32-byte integrity digest and tshark has no built-in dissector, so read it structurally: who talks to the PLC, how often, message sizes, and payloads that repeat (a replay repeats its digest)). ATT&amp;CK for ICS: T0843 Program Download · T0855 Unauthorized Command Message · T0831 Manipulation of Control. Sources are credited per collection in each folder's PROVENANCE.md.

**Computed evidence (auto-extracted with tshark — verify it yourself):** S7comm-plus (S7-1200/1500) packets (matched by the protocol filter used in the steps): 45; top conversations in S7-1511_db6w0_HMI.pcap: 192.168.25.139↔192.168.25.146 (18 pkts) (basis: 3 of 20 capture file(s), first 300,000 packets each, smallest files carrying S7comm-plus (S7-1200/1500) chosen)

_Captures credited to: CISA ICSNPP — Zeek ICS parser test traces — CISA and Idaho National Laboratory (ICSNPP project) · ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset — Emre Ekin (ICS Defense, icsdefense.net) · INL Malcolm test artifacts — OT protocol samples — Idaho National Laboratory (Malcolm) · ITI ICS-Security-Tools — sample ICS protocol captures — Information Trust Institute (ITI), University of Illinois Urbana-Champaign._

</details>

## Dataset & credit

**CISA ICSNPP — Zeek ICS parser test traces — CISA and Idaho National Laboratory (ICSNPP project) · ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset — Emre Ekin (ICS Defense, icsdefense.net) · INL Malcolm test artifacts — OT protocol samples — Idaho National Laboratory (Malcolm) · ITI ICS-Security-Tools — sample ICS protocol captures — Information Trust Institute (ITI), University of Illinois Urbana-Champaign** — license: varies by collection — see each folder's PROVENANCE.md

- [Dataset source — CISA ICSNPP — Zeek ICS parser test traces](https://github.com/cisagov/ICSNPP)
- [Dataset source — ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset](https://github.com/EmreEkin/ICS-Pcaps)
- [Dataset source — INL Malcolm test artifacts — OT protocol samples](https://github.com/idaholab/Malcolm-Test-Artifacts)
- [Dataset source — ITI ICS-Security-Tools — sample ICS protocol captures](https://github.com/ITI/ICS-Security-Tools/tree/master/pcaps)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/cisa-icsnpp-test-traces/icsnpp-s7comm/s7comm_plus.pcap`

</details>
