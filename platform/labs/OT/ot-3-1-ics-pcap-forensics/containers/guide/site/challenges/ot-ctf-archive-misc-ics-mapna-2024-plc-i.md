# MAPNA 2024 — PLC I

**CTF &amp; conference labs** · **Medium** · 0.0 MB · 0 capture file(s)

> CTF: MAPNA 2024 — PLC I (S7comm).

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

A capture-the-flag challenge from ICS challenges from public CTF archives (sajjadium/ctf-archives). S7comm on non-standard TCP 10203 — use Decode As → TPKT.

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
pcapper 'data/ctf-archive-misc-ics/mapna-2024-plc-i/plc.pcap' --ctf --overview
```

**2. Pcapper reports TCP/10203 as an unknown service**

Pcapper recognises OT protocols on their standard ports, so it lists TCP/10203 without decoding it. Identify the protocol with tshark's decode-as (see the tshark / Wireshark track), then continue here.

```bash
pcapper 'data/ctf-archive-misc-ics/mapna-2024-plc-i/plc.pcap' --services
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/ctf-archive-misc-ics/mapna-2024-plc-i/plc.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Let Pcapper hunt the flag**

```bash
capinfos 'data/ctf-archive-misc-ics/mapna-2024-plc-i/plc.pcap'
tshark -r 'data/ctf-archive-misc-ics/mapna-2024-plc-i/plc.pcap' -q -z io,phs | head -40
```

**2. Who talks on which port?**

Payload-carrying packets per conversation and server port: the busiest port carries the protocol you need to identify.

```bash
tshark -r 'data/ctf-archive-misc-ics/mapna-2024-plc-i/plc.pcap' -Y 'tcp.len > 0 || udp.length > 8' -T fields -e ip.src -e ip.dst -e tcp.dstport -e udp.dstport | sort | uniq -c | sort -rn | head -20
```

**3. Read the payloads**

Look for magic bytes, length fields, sequence counters and ASCII (device names, tags, flags).

```bash
tshark -r 'data/ctf-archive-misc-ics/mapna-2024-plc-i/plc.pcap' -qz follow,tcp,hex,0 | head -60
tshark -r 'data/ctf-archive-misc-ics/mapna-2024-plc-i/plc.pcap' -Y 'tcp.len > 0 || udp.length > 8' -T fields -e frame.number -e data.data | head -20
```

**4. Try the industrial dissectors on that port**

Replace &lt;port&gt; with the busiest server port from step 2. A clean decode (no malformed packets, length fields that match) identifies a standard protocol on a non-standard port.

```bash
for p in tpkt mbtcp dnp3 enip iec60870_104; do echo "== $p"; tshark -r 'data/ctf-archive-misc-ics/mapna-2024-plc-i/plc.pcap' -d tcp.port==<port>,$p 2>/dev/null | head -4; done
```

**5. Map the S7comm conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/ctf-archive-misc-ics/mapna-2024-plc-i/plc.pcap' -d tcp.port==10203,tpkt -Y s7comm -T fields -e ip.src -e ip.dst -e s7comm.header.rosctr -e s7comm.param.func -e s7comm.param.userdata.funcgroup -e s7comm.param.userdata.subfunc | sort | uniq -c | sort -rn | head -25
```

**6. Hunt the dangerous operations**

Flag write variable (0x05), program download (0x1A–0x1C), program upload (0x1D–0x1F — logic theft), PI-service (0x28 — start/restart/compress), PLC STOP (0x29) and security/password userdata (function group 5); SZL reads (function group 4) are device recon.

```bash
tshark -r 'data/ctf-archive-misc-ics/mapna-2024-plc-i/plc.pcap' -d tcp.port==10203,tpkt -Y 's7comm.param.func in {0x05, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 0x28, 0x29} || s7comm.param.userdata.funcgroup == 5' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**7. Decode the protocol fields**

Register values, write payloads and odd function codes are the usual hiding places — try ASCII.

```bash
tshark -r 'data/ctf-archive-misc-ics/mapna-2024-plc-i/plc.pcap' -d tcp.port==10203,tpkt -Y 's7comm.resp.data' -T fields -e s7comm.resp.data | head -60
strings -n 6 'data/ctf-archive-misc-ics/mapna-2024-plc-i/plc.pcap' | grep -iE 'flag|ctf|\{' | head
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

**Computed evidence (auto-extracted with tshark — verify it yourself):** S7comm operations — CPU services ×24, Setup Communication ×2; dangerous-operation matches: 0 for the S7comm filter (26 S7comm packets present, so the zero is real); top conversations in plc.pcap: 10.19.31.85↔192.168.110.40 (51 pkts); flag-like strings found by `strings`: none in plain text (decode protocol fields) (basis: 1 of 1 capture file(s), first 300,000 packets each; decoded with -d tcp.port==10203,tpkt)

_Dataset credit: Event organisers; archived by sajjadium/ctf-archives · License: Archive repository MIT (challenge files not separately licensed) — credit each event._

</details>

## Dataset & credit

**Event organisers; archived by sajjadium/ctf-archives** — license: Archive repository MIT (challenge files not separately licensed) — credit each event

- [Dataset source — ICS challenges from public CTF archives (sajjadium/ctf-archi](https://github.com/sajjadium/ctf-archives)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/ctf-archive-misc-ics/mapna-2024-plc-i/plc.pcap`

</details>
