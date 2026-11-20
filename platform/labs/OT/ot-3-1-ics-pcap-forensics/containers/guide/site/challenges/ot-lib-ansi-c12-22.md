# Protocol deep-dive — ANSI C12.22 (14 unique captures)

**Protocol library** · **Medium** · 0.0 MB · 12 capture file(s)

> A deduplicated library of 14 ANSI C12.22 captures from 3 public collections. Learn the protocol's grammar, then hunt its dangerous operations.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Every public ANSI C12.22 sample in this range, deduplicated by SHA-256 across cisa-icsnpp-test-traces, emreekin-ics-pcaps, inl-malcolm-ot-artifacts. Use it to learn what the protocol looks like on the wire — roles, operations, normal cadence — and to practice spotting the operations attackers abuse: C12.22 carries C12.19 table reads/writes to revenue meters — writes to configuration tables or procedure calls (e.g. disconnect) are the high-value operations.

## Objectives

- Identify clients/masters and servers/outstations across the samples.
- Enumerate the ANSI C12.22 operations present.
- Flag every dangerous operation and its source.
- Map findings to ATT&amp;CK for ICS (T0836 Modify Parameter · T0831 Manipulation of Control).

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch its 3 datasets first, from the repo root:

```bash
python3 scripts/fetch.py cisa-icsnpp-test-traces emreekin-ics-pcaps inl-malcolm-ot-artifacts
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

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-c1222/c1222_service_error_tcp.pcap' --overview
```

**2. Deep-dive with Pcapper (--overview)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-c1222/c1222_service_error_tcp.pcap' --overview --ot-commands
```

**3. Sweep the whole library**

```bash
pcapper data/cisa-icsnpp-test-traces/ --overview --ot-commands
```

**4. Every control and write, normalized**

--ot-commands lists every OT control/write command across protocols; --threats consolidates Pcapper's detections.

```bash
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-c1222/c1222_service_error_tcp.pcap' --ot-commands --threats
```

**5. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-c1222/c1222_service_error_tcp.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/cisa-icsnpp-test-traces/icsnpp-c1222/c1222_service_error_tcp.pcap'
tshark -r 'data/cisa-icsnpp-test-traces/icsnpp-c1222/c1222_service_error_tcp.pcap' -q -z io,phs | head -40
```

**2. Map the ANSI C12.22 conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/cisa-icsnpp-test-traces/icsnpp-c1222/c1222_service_error_tcp.pcap' -Y c1222 -T fields -e ip.src -e ip.dst | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag C12.22 carries C12.19 table reads/writes to revenue meters — writes to configuration tables or procedure calls (e.g. disconnect) are the high-value operations.

```bash
tshark -r 'data/cisa-icsnpp-test-traces/icsnpp-c1222/c1222_service_error_tcp.pcap' -Y 'c1222' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Sweep the whole library**

```bash
for f in 'data/cisa-icsnpp-test-traces/icsnpp-c1222/c1222_service_error_tcp.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-c1222/c1222_logon_service_tcp.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-c1222/c1222_ident_service_tcp.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-c1222/c1222_security_service_tcp.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-c1222/c1222_reg_service_tcp.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-c1222/c1222_rw_service_tcp.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-c1222/c1222_trace_service_tcp.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-c1222/c1222_wait_service_tcp.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-c1222/c1222_resolve_service_tcp.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-c1222/c1222overIPv4.cap'; do echo "== $f"; tshark -r "$f" -Y 'c1222' 2>/dev/null | head -3; done
```

## Hints

<details><summary>Hint 1</summary>

Wireshark display filter for the protocol: c1222

</details>

<details><summary>Hint 2</summary>

Dangerous-operation filter: c1222

</details>

<details><summary>Hint 3</summary>

Many library files are tiny protocol samples — read them packet by packet in Wireshark.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

A library, not a single puzzle: the deliverable is a per-capture table of roles and operations, with the dangerous ones flagged (C12.22 carries C12.19 table reads/writes to revenue meters — writes to configuration tables or procedure calls (e.g. disconnect) are the high-value operations). ATT&amp;CK for ICS: T0836 Modify Parameter · T0831 Manipulation of Control. Sources are credited per collection in each folder's PROVENANCE.md.

**Computed evidence (auto-extracted with tshark — verify it yourself):** ANSI C12.22 packets matching `c1222`: 6; top conversations in c1222_std_example8.pcap: 10.1.1.1↔10.2.2.2 (2 pkts) (basis: 3 of 14 capture file(s), first 300,000 packets each, smallest files carrying ANSI C12.22 chosen)

_Captures credited to: CISA ICSNPP — Zeek ICS parser test traces — CISA and Idaho National Laboratory (ICSNPP project) · ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset — Emre Ekin (ICS Defense, icsdefense.net) · INL Malcolm test artifacts — OT protocol samples — Idaho National Laboratory (Malcolm)._

</details>

## Dataset & credit

**CISA ICSNPP — Zeek ICS parser test traces — CISA and Idaho National Laboratory (ICSNPP project) · ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset — Emre Ekin (ICS Defense, icsdefense.net) · INL Malcolm test artifacts — OT protocol samples — Idaho National Laboratory (Malcolm)** — license: varies by collection — see each folder's PROVENANCE.md

- [Dataset source — CISA ICSNPP — Zeek ICS parser test traces](https://github.com/cisagov/ICSNPP)
- [Dataset source — ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset](https://github.com/EmreEkin/ICS-Pcaps)
- [Dataset source — INL Malcolm test artifacts — OT protocol samples](https://github.com/idaholab/Malcolm-Test-Artifacts)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (12)</summary>

- `data/cisa-icsnpp-test-traces/icsnpp-c1222/c1222_service_error_tcp.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-c1222/c1222_logon_service_tcp.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-c1222/c1222_ident_service_tcp.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-c1222/c1222_security_service_tcp.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-c1222/c1222_reg_service_tcp.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-c1222/c1222_rw_service_tcp.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-c1222/c1222_trace_service_tcp.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-c1222/c1222_wait_service_tcp.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-c1222/c1222_resolve_service_tcp.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-c1222/c1222overIPv4.cap`
- `data/cisa-icsnpp-test-traces/icsnpp-c1222/c1222_std_example8.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-c1222/c1222_over_ipv6.pcap`

</details>
