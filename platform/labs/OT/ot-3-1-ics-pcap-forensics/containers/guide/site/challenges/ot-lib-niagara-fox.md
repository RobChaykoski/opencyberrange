# Protocol deep-dive — Niagara Fox (1 unique captures)

**Protocol library** · **Easy** · 0.0 MB · 0 capture file(s)

> A deduplicated library of 1 Niagara Fox captures from 1 public collections. Learn the protocol's grammar, then hunt its dangerous operations.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Every public Niagara Fox sample in this range, deduplicated by SHA-256 across iti-ics-security-tools-pcaps. Use it to learn what the protocol looks like on the wire — roles, operations, normal cadence — and to practice spotting the operations attackers abuse: the Fox 'hello' exchange leaks station name, host OS and Niagara version; credentials and write actions follow.

## Objectives

- Identify clients/masters and servers/outstations across the samples.
- Enumerate the Niagara Fox operations present.
- Flag every dangerous operation and its source.
- Map findings to ATT&amp;CK for ICS (T0888 Remote System Information Discovery · T0859 Valid Accounts).

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
pcapper 'data/iti-ics-security-tools-pcaps/pcaps/fox/fox_info.pcap' --overview
```

**2. Deep-dive with Pcapper (--niagara)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/iti-ics-security-tools-pcaps/pcaps/fox/fox_info.pcap' --niagara --ot-commands
```

**3. Sweep the whole library**

```bash
pcapper data/iti-ics-security-tools-pcaps/ --niagara --ot-commands
```

**4. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/iti-ics-security-tools-pcaps/pcaps/fox/fox_info.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/iti-ics-security-tools-pcaps/pcaps/fox/fox_info.pcap'
tshark -r 'data/iti-ics-security-tools-pcaps/pcaps/fox/fox_info.pcap' -q -z io,phs | head -40
```

**2. Map the Niagara Fox conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/iti-ics-security-tools-pcaps/pcaps/fox/fox_info.pcap' -Y 'tcp.port in {1911, 4911}' -q -z conv,tcp
```

**3. Hunt the dangerous operations**

Flag the Fox 'hello' exchange leaks station name, host OS and Niagara version; credentials and write actions follow.

```bash
tshark -r 'data/iti-ics-security-tools-pcaps/pcaps/fox/fox_info.pcap' -Y 'tcp.port in {1911, 4911}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Sweep the whole library**

```bash
for f in 'data/iti-ics-security-tools-pcaps/pcaps/fox/fox_info.pcap'; do echo "== $f"; tshark -r "$f" -Y 'tcp.port in {1911, 4911}' 2>/dev/null | head -3; done
```

## Hints

<details><summary>Hint 1</summary>

Wireshark display filter for the protocol: tcp.port in {1911, 4911}

</details>

<details><summary>Hint 2</summary>

Dangerous-operation filter: tcp.port in {1911, 4911}

</details>

<details><summary>Hint 3</summary>

Many library files are tiny protocol samples — read them packet by packet in Wireshark.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

A library, not a single puzzle: the deliverable is a per-capture table of roles and operations, with the dangerous ones flagged (the Fox 'hello' exchange leaks station name, host OS and Niagara version; credentials and write actions follow). ATT&amp;CK for ICS: T0888 Remote System Information Discovery · T0859 Valid Accounts. Sources are credited per collection in each folder's PROVENANCE.md.

**Computed evidence (auto-extracted with tshark — verify it yourself):** Niagara Fox packets matching `tcp.port in {1911, 4911}`: 10; dangerous-operation matches: 10 (top sources: 10.1.3.4 ×6, 106.68.88.119 ×4); top conversations in fox_info.pcap: 10.1.3.4↔106.68.88.119 (10 pkts) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Captures credited to: ITI ICS-Security-Tools — sample ICS protocol captures — Information Trust Institute (ITI), University of Illinois Urbana-Champaign._

</details>

## Dataset & credit

**ITI ICS-Security-Tools — sample ICS protocol captures — Information Trust Institute (ITI), University of Illinois Urbana-Champaign** — license: varies by collection — see each folder's PROVENANCE.md

- [Dataset source — ITI ICS-Security-Tools — sample ICS protocol captures](https://github.com/ITI/ICS-Security-Tools/tree/master/pcaps)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/iti-ics-security-tools-pcaps/pcaps/fox/fox_info.pcap`

</details>
