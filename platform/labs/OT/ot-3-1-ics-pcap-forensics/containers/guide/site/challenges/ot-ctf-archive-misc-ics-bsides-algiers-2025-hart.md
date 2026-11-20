# BSides Algiers 2025 — Hart

**CTF &amp; conference labs** · **Medium** · 0.0 MB · 0 capture file(s)

> CTF: BSides Algiers 2025 — Hart (HART-IP).

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

A capture-the-flag challenge from ICS challenges from public CTF archives (sajjadium/ctf-archives). Industrial sensor network over HART-IP (UDP 5094).

ICS CTF flags usually hide in protocol fields — register values, write payloads, function codes or timing — rather than in plain text. Work it like an analyst: map the protocol, find the operations that don't belong, then decode.

## Objectives

- Identify the protocol(s), roles and endpoints.
- Find the anomalous operations or payloads.
- Extract and decode the flag.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py ctf-archive-misc-ics
```

- **[ICS challenges from public CTF archives (sajjadium/ctf-archives)](../DATASETS.md#ctf-archive-misc-ics)** (`ctf-archive-misc-ics`), ~9.5 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/sajjadium/ctf-archives](https://github.com/sajjadium/ctf-archives)

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Let Pcapper hunt the flag**

--ctf runs Pcapper's flag finder and decoders; --overview runs the right OT analyzer.

```bash
pcapper 'data/ctf-archive-misc-ics/bsides-algiers-2025-hart/chall.pcap' --ctf --overview
```

**2. Let Pcapper hunt for the flag**

--ctf runs Pcapper's flag finder and decoders; --strings surfaces cleartext that a flag may hide in.

```bash
pcapper 'data/ctf-archive-misc-ics/bsides-algiers-2025-hart/chall.pcap' --ctf --strings
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/ctf-archive-misc-ics/bsides-algiers-2025-hart/chall.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Let Pcapper hunt the flag**

```bash
capinfos 'data/ctf-archive-misc-ics/bsides-algiers-2025-hart/chall.pcap'
tshark -r 'data/ctf-archive-misc-ics/bsides-algiers-2025-hart/chall.pcap' -q -z io,phs | head -40
```

**2. Map the HART-IP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/ctf-archive-misc-ics/bsides-algiers-2025-hart/chall.pcap' -Y hart_ip -T fields -e ip.src -e ip.dst -e hart_ip.message_id | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag HART-IP tunnels HART commands to field instruments — command 0 (read unique ID) is recon; write commands change instrument configuration.

```bash
tshark -r 'data/ctf-archive-misc-ics/bsides-algiers-2025-hart/chall.pcap' -Y 'hart_ip' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Decode the protocol fields**

Register values, write payloads and odd function codes are the usual hiding places — try ASCII.

```bash
tshark -r 'data/ctf-archive-misc-ics/bsides-algiers-2025-hart/chall.pcap' -Y 'data.data' -T fields -e data.data | head -60
strings -n 6 'data/ctf-archive-misc-ics/bsides-algiers-2025-hart/chall.pcap' | grep -iE 'flag|ctf|\{' | head
```

## Hints

<details><summary>Hint 1</summary>

Pcapper --ctf tries common encodings automatically.

</details>

<details><summary>Hint 2</summary>

Read writes, not just reads — the flag is often written.

</details>

<details><summary>Hint 3</summary>

Concatenate register values in order and decode the 16-bit words as ASCII.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

No public write-up was located for this one — the computed evidence below lists any flag-like strings found automatically; confirm them by finding the packets that carry them.

**Computed evidence (auto-extracted with tshark — verify it yourself):** HART-IP packets matching `hart_ip`: 80; top conversations in chall.pcap: 192.168.10.1↔192.168.10.13 (782 pkts), 192.168.10.1↔192.168.10.11 (732 pkts), 192.168.10.1↔192.168.10.10 (728 pkts); flag-like strings found by `strings`: none in plain text (decode protocol fields) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: Event organisers; archived by sajjadium/ctf-archives · License: Archive repository MIT (challenge files not separately licensed) — credit each event._

</details>

## Dataset & credit

**Event organisers; archived by sajjadium/ctf-archives** — license: Archive repository MIT (challenge files not separately licensed) — credit each event

- [Dataset source — ICS challenges from public CTF archives (sajjadium/ctf-archi](https://github.com/sajjadium/ctf-archives)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/ctf-archive-misc-ics/bsides-algiers-2025-hart/chall.pcap`

</details>
