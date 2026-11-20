# Protocol deep-dive — LonTalk (2 unique captures)

**Protocol library** · **Easy** · 0.0 MB · 0 capture file(s)

> A deduplicated library of 2 LonTalk captures from 1 public collections. Learn the protocol's grammar, then hunt its dangerous operations.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Every public LonTalk sample in this range, deduplicated by SHA-256 across emreekin-ics-pcaps. Use it to learn what the protocol looks like on the wire — roles, operations, normal cadence — and to practice spotting the operations attackers abuse: LonWorks over IP (CNIP) — network-variable updates control building equipment directly.

## Objectives

- Identify clients/masters and servers/outstations across the samples.
- Enumerate the LonTalk operations present.
- Flag every dangerous operation and its source.
- Map findings to ATT&amp;CK for ICS (T0836 Modify Parameter).

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py emreekin-ics-pcaps
```

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
pcapper 'data/emreekin-ics-pcaps/EtherCat/valve.pcap' --overview
```

**2. Deep-dive with Pcapper (--overview)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/emreekin-ics-pcaps/EtherCat/valve.pcap' --overview --ot-commands
```

**3. Sweep the whole library**

```bash
pcapper data/emreekin-ics-pcaps/ --overview --ot-commands
```

**4. Every control and write, normalized**

--ot-commands lists every OT control/write command across protocols; --threats consolidates Pcapper's detections.

```bash
pcapper 'data/emreekin-ics-pcaps/EtherCat/valve.pcap' --ot-commands --threats
```

**5. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/emreekin-ics-pcaps/EtherCat/valve.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/emreekin-ics-pcaps/EtherCat/valve.pcap'
tshark -r 'data/emreekin-ics-pcaps/EtherCat/valve.pcap' -q -z io,phs | head -40
```

**2. Map the LonTalk conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/emreekin-ics-pcaps/EtherCat/valve.pcap' -Y 'cnip || lon' -T fields -e ip.src -e ip.dst | sort | uniq -c | sort -rn | head
```

**3. Hunt the dangerous operations**

Flag LonWorks over IP (CNIP) — network-variable updates control building equipment directly.

```bash
tshark -r 'data/emreekin-ics-pcaps/EtherCat/valve.pcap' -Y 'cnip || lon' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Sweep the whole library**

```bash
for f in 'data/emreekin-ics-pcaps/EtherCat/valve.pcap' 'data/emreekin-ics-pcaps/LonTalk/Lon.pcap'; do echo "== $f"; tshark -r "$f" -Y 'cnip || lon' 2>/dev/null | head -3; done
```

## Hints

<details><summary>Hint 1</summary>

Wireshark display filter for the protocol: cnip || lon

</details>

<details><summary>Hint 2</summary>

Dangerous-operation filter: cnip || lon

</details>

<details><summary>Hint 3</summary>

Many library files are tiny protocol samples — read them packet by packet in Wireshark.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

A library, not a single puzzle: the deliverable is a per-capture table of roles and operations, with the dangerous ones flagged (LonWorks over IP (CNIP) — network-variable updates control building equipment directly). ATT&amp;CK for ICS: T0836 Modify Parameter. Sources are credited per collection in each folder's PROVENANCE.md.

**Computed evidence (auto-extracted with tshark — verify it yourself):** LonTalk packets matching `cnip || lon`: 12,029; top conversations in valve.pcap: 204.63.214.0↔82.94.213.34 (2,196 pkts), 204.63.214.36↔82.94.213.34 (388 pkts), 204.63.214.52↔82.94.213.34 (386 pkts) (basis: 2 of 2 capture file(s), first 300,000 packets each)

_Captures credited to: ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset — Emre Ekin (ICS Defense, icsdefense.net)._

</details>

## Dataset & credit

**ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset — Emre Ekin (ICS Defense, icsdefense.net)** — license: varies by collection — see each folder's PROVENANCE.md

- [Dataset source — ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset](https://github.com/EmreEkin/ICS-Pcaps)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (2)</summary>

- `data/emreekin-ics-pcaps/EtherCat/valve.pcap`
- `data/emreekin-ics-pcaps/LonTalk/Lon.pcap`

</details>
