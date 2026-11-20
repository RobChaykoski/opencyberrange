# Protocol deep-dive — POWERLINK (3 unique captures)

**Protocol library** · **Easy** · 0.0 MB · 0 capture file(s)

> A deduplicated library of 3 POWERLINK captures from 2 public collections. Learn the protocol's grammar, then hunt its dangerous operations.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Every public POWERLINK sample in this range, deduplicated by SHA-256 across automayt-ics-pcap, emreekin-ics-pcaps. Use it to learn what the protocol looks like on the wire — roles, operations, normal cadence — and to practice spotting the operations attackers abuse: the managing node's SoC/PReq/PRes/SoA cycle is deterministic — anything off-cycle or a second managing node is an anomaly.

## Objectives

- Identify clients/masters and servers/outstations across the samples.
- Enumerate the POWERLINK operations present.
- Flag every dangerous operation and its source.
- Map findings to ATT&amp;CK for ICS (T0814 Denial of Service).

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch its 2 datasets first, from the repo root:

```bash
python3 scripts/fetch.py automayt-ics-pcap emreekin-ics-pcaps
```

- **[ICS-pcap collection (automayt / Jason Smith)](../DATASETS.md#automayt-ics-pcap)** (`automayt-ics-pcap`), ~0.42 GB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/automayt/ICS-pcap](https://github.com/automayt/ICS-pcap)
- **[ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset](../DATASETS.md#emreekin-ics-pcaps)** (`emreekin-ics-pcaps`), ~0.26 GB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/EmreEkin/ICS-Pcaps](https://github.com/EmreEkin/ICS-Pcaps)

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/automayt-ics-pcap/POWERLINK/epl/epl.pcap' --overview
```

**2. Deep-dive with Pcapper (--overview)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/automayt-ics-pcap/POWERLINK/epl/epl.pcap' --overview --ot-commands
```

**3. Sweep the whole library**

```bash
pcapper data/automayt-ics-pcap/ --overview --ot-commands
```

**4. Every control and write, normalized**

--ot-commands lists every OT control/write command across protocols; --threats consolidates Pcapper's detections.

```bash
pcapper 'data/automayt-ics-pcap/POWERLINK/epl/epl.pcap' --ot-commands --threats
```

**5. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/automayt-ics-pcap/POWERLINK/epl/epl.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/automayt-ics-pcap/POWERLINK/epl/epl.pcap'
tshark -r 'data/automayt-ics-pcap/POWERLINK/epl/epl.pcap' -q -z io,phs | head -40
```

**2. Map the POWERLINK conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/automayt-ics-pcap/POWERLINK/epl/epl.pcap' -Y epl -T fields -e eth.src -e eth.dst -e epl.mtyp | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag the managing node's SoC/PReq/PRes/SoA cycle is deterministic — anything off-cycle or a second managing node is an anomaly.

```bash
tshark -r 'data/automayt-ics-pcap/POWERLINK/epl/epl.pcap' -Y 'epl' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Sweep the whole library**

```bash
for f in 'data/automayt-ics-pcap/POWERLINK/epl/epl.pcap' 'data/emreekin-ics-pcaps/PowerlinkEPL/epl.pcap' 'data/emreekin-ics-pcaps/PowerlinkEPL/epl_v1.pcap'; do echo "== $f"; tshark -r "$f" -Y 'epl' 2>/dev/null | head -3; done
```

## Hints

<details><summary>Hint 1</summary>

Wireshark display filter for the protocol: epl

</details>

<details><summary>Hint 2</summary>

Dangerous-operation filter: epl

</details>

<details><summary>Hint 3</summary>

Many library files are tiny protocol samples — read them packet by packet in Wireshark.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

A library, not a single puzzle: the deliverable is a per-capture table of roles and operations, with the dangerous ones flagged (the managing node's SoC/PReq/PRes/SoA cycle is deterministic — anything off-cycle or a second managing node is an anomaly). ATT&amp;CK for ICS: T0814 Denial of Service. Sources are credited per collection in each folder's PROVENANCE.md.

**Computed evidence (auto-extracted with tshark — verify it yourself):** POWERLINK packets matching `epl`: 1,065 (basis: 3 of 3 capture file(s), first 300,000 packets each)

_Captures credited to: ICS-pcap collection (automayt / Jason Smith) — Jason Smith (automayt) · ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset — Emre Ekin (ICS Defense, icsdefense.net)._

</details>

## Dataset & credit

**ICS-pcap collection (automayt / Jason Smith) — Jason Smith (automayt) · ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset — Emre Ekin (ICS Defense, icsdefense.net)** — license: varies by collection — see each folder's PROVENANCE.md

- [Dataset source — ICS-pcap collection (automayt / Jason Smith)](https://github.com/automayt/ICS-pcap)
- [Dataset source — ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset](https://github.com/EmreEkin/ICS-Pcaps)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (3)</summary>

- `data/automayt-ics-pcap/POWERLINK/epl/epl.pcap`
- `data/emreekin-ics-pcaps/PowerlinkEPL/epl.pcap`
- `data/emreekin-ics-pcaps/PowerlinkEPL/epl_v1.pcap`

</details>
