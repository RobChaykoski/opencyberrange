# Protocol deep-dive — Beckhoff ADS/AMS (10 unique captures)

**Protocol library** · **Medium** · 0.0 MB · 0 capture file(s)

> A deduplicated library of 10 Beckhoff ADS/AMS captures from 1 public collections. Learn the protocol's grammar, then hunt its dangerous operations.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Every public Beckhoff ADS/AMS sample in this range, deduplicated by SHA-256 across iti-ics-security-tools-pcaps. Use it to learn what the protocol looks like on the wire — roles, operations, normal cadence — and to practice spotting the operations attackers abuse: Write (3), WriteControl (5 — change the TwinCAT run state) and ReadWrite (9).

## Objectives

- Identify clients/masters and servers/outstations across the samples.
- Enumerate the Beckhoff ADS/AMS operations present.
- Flag every dangerous operation and its source.
- Map findings to ATT&amp;CK for ICS (T0858 Change Operating Mode · T0836 Modify Parameter).

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py iti-ics-security-tools-pcaps
```

- **[ITI ICS-Security-Tools — sample ICS protocol captures](../DATASETS.md#iti-ics-security-tools-pcaps)** (`iti-ics-security-tools-pcaps`), ~0.12 GB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/ITI/ICS-Security-Tools/tree/master/pcaps](https://github.com/ITI/ICS-Security-Tools/tree/master/pcaps)

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/iti-ics-security-tools-pcaps/pcaps/beckoff/beckoffiplink.pcapng' --overview
```

**2. Deep-dive with Pcapper (--overview)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/iti-ics-security-tools-pcaps/pcaps/beckoff/beckoffiplink.pcapng' --overview --ot-commands
```

**3. Sweep the whole library**

```bash
pcapper data/iti-ics-security-tools-pcaps/ --overview --ot-commands
```

**4. Every control and write, normalized**

--ot-commands lists every OT control/write command across protocols; --threats consolidates Pcapper's detections.

```bash
pcapper 'data/iti-ics-security-tools-pcaps/pcaps/beckoff/beckoffiplink.pcapng' --ot-commands --threats
```

**5. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/iti-ics-security-tools-pcaps/pcaps/beckoff/beckoffiplink.pcapng' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/iti-ics-security-tools-pcaps/pcaps/beckoff/beckoffiplink.pcapng'
tshark -r 'data/iti-ics-security-tools-pcaps/pcaps/beckoff/beckoffiplink.pcapng' -q -z io,phs | head -40
```

**2. Map the Beckhoff ADS/AMS conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/iti-ics-security-tools-pcaps/pcaps/beckoff/beckoffiplink.pcapng' -Y ams -T fields -e ip.src -e ip.dst -e ams.cmdid | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag Write (3), WriteControl (5 — change the TwinCAT run state) and ReadWrite (9).

```bash
tshark -r 'data/iti-ics-security-tools-pcaps/pcaps/beckoff/beckoffiplink.pcapng' -Y 'ams.cmdid in {3, 5, 9}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Sweep the whole library**

```bash
for f in 'data/iti-ics-security-tools-pcaps/pcaps/beckoff/beckoffiplink.pcapng' 'data/iti-ics-security-tools-pcaps/pcaps/beckoff/addroute.pcapng' 'data/iti-ics-security-tools-pcaps/pcaps/beckoff/beckoffaddroute.pcapng' 'data/iti-ics-security-tools-pcaps/pcaps/beckoff/addrouteuse444444444.pcapng' 'data/iti-ics-security-tools-pcaps/pcaps/beckoff/beckoffiplinktc3.pcapng' 'data/iti-ics-security-tools-pcaps/pcaps/beckoff/invokeid12.pcapng' 'data/iti-ics-security-tools-pcaps/pcaps/beckoff/beckoffiplinktc2.pcapng' 'data/iti-ics-security-tools-pcaps/pcaps/beckoff/addroute1.pcapng' 'data/iti-ics-security-tools-pcaps/pcaps/beckoff/beckofflink.pcapng' 'data/iti-ics-security-tools-pcaps/pcaps/beckoff/beckoffiplinktc.pcapng'; do echo "== $f"; tshark -r "$f" -Y 'ams.cmdid in {3, 5, 9}' 2>/dev/null | head -3; done
```

## Hints

<details><summary>Hint 1</summary>

Wireshark display filter for the protocol: ams

</details>

<details><summary>Hint 2</summary>

Dangerous-operation filter: ams.cmdid in {3, 5, 9}

</details>

<details><summary>Hint 3</summary>

Many library files are tiny protocol samples — read them packet by packet in Wireshark.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

A library, not a single puzzle: the deliverable is a per-capture table of roles and operations, with the dangerous ones flagged (Write (3), WriteControl (5 — change the TwinCAT run state) and ReadWrite (9)). ATT&amp;CK for ICS: T0858 Change Operating Mode · T0836 Modify Parameter. Sources are credited per collection in each folder's PROVENANCE.md.

**Computed evidence (auto-extracted with tshark — verify it yourself):** Beckhoff ADS/AMS operations — ReadState ×35, Read ×32, ReadWrite ×14, ReadDeviceInfo ×8, AddDeviceNotification ×4, DelDeviceNotification ×2; dangerous-operation matches: 14 (top sources: 192.168.1.99 ×7, 192.168.1.8 ×7); top conversations in invokeid12.pcapng: 192.168.1.177↔192.168.1.255 (27 pkts), 192.168.1.194↔192.168.255.255 (6 pkts), 192.168.1.177↔192.168.1.8 (5 pkts) (basis: 3 of 10 capture file(s), first 300,000 packets each, smallest files carrying Beckhoff ADS/AMS chosen)

_Captures credited to: ITI ICS-Security-Tools — sample ICS protocol captures — Information Trust Institute (ITI), University of Illinois Urbana-Champaign._

</details>

## Dataset & credit

**ITI ICS-Security-Tools — sample ICS protocol captures — Information Trust Institute (ITI), University of Illinois Urbana-Champaign** — license: varies by collection — see each folder's PROVENANCE.md

- [Dataset source — ITI ICS-Security-Tools — sample ICS protocol captures](https://github.com/ITI/ICS-Security-Tools/tree/master/pcaps)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (10)</summary>

- `data/iti-ics-security-tools-pcaps/pcaps/beckoff/beckoffiplink.pcapng`
- `data/iti-ics-security-tools-pcaps/pcaps/beckoff/addroute.pcapng`
- `data/iti-ics-security-tools-pcaps/pcaps/beckoff/beckoffaddroute.pcapng`
- `data/iti-ics-security-tools-pcaps/pcaps/beckoff/addrouteuse444444444.pcapng`
- `data/iti-ics-security-tools-pcaps/pcaps/beckoff/beckoffiplinktc3.pcapng`
- `data/iti-ics-security-tools-pcaps/pcaps/beckoff/invokeid12.pcapng`
- `data/iti-ics-security-tools-pcaps/pcaps/beckoff/beckoffiplinktc2.pcapng`
- `data/iti-ics-security-tools-pcaps/pcaps/beckoff/addroute1.pcapng`
- `data/iti-ics-security-tools-pcaps/pcaps/beckoff/beckofflink.pcapng`
- `data/iti-ics-security-tools-pcaps/pcaps/beckoff/beckoffiplinktc.pcapng`

</details>
