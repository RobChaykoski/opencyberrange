# Zhejiang 2026 — easy_MMS

**CTF &amp; conference labs** · **Medium** · 0.0 MB · 0 capture file(s)

> CTF: Zhejiang 2026 — easy_MMS (IEC 61850 MMS).

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller. This capture carries executable files (Windows PE / Linux ELF) inside the traffic, and some may be malware: work offline, hash anything you extract and never run it.

## Scenario

A capture-the-flag challenge from Chinese ICS competition challenges (CISCN, Fujian, Panda Cup, Qiangwang, Zhejiang, VCTF). 

ICS CTF flags usually hide in protocol fields — register values, write payloads, function codes or timing — rather than in plain text. Work it like an analyst: map the protocol, find the operations that don't belong, then decode.

## Objectives

- Identify the protocol(s), roles and endpoints.
- Find the anomalous operations or payloads.
- Extract and decode the flag.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py ctf-cn-competitions-misc
```

- **[Chinese ICS competition challenges (CISCN, Fujian, Panda Cup, Qiangwang, Zhejiang, VCTF)](../DATASETS.md#ctf-cn-competitions-misc)** (`ctf-cn-competitions-misc`), ~24.4 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/CTF-Archives](https://github.com/CTF-Archives)

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Let Pcapper hunt the flag**

--ctf runs Pcapper's flag finder and decoders; --overview runs the right OT analyzer.

```bash
pcapper 'data/ctf-cn-competitions-misc/zhejiang-2026-easy-mms/easymms.pcap' --ctf --overview
```

**2. Let Pcapper hunt for the flag**

--ctf runs Pcapper's flag finder and decoders; --strings surfaces cleartext that a flag may hide in.

```bash
pcapper 'data/ctf-cn-competitions-misc/zhejiang-2026-easy-mms/easymms.pcap' --ctf --strings
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/ctf-cn-competitions-misc/zhejiang-2026-easy-mms/easymms.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Let Pcapper hunt the flag**

```bash
capinfos 'data/ctf-cn-competitions-misc/zhejiang-2026-easy-mms/easymms.pcap'
tshark -r 'data/ctf-cn-competitions-misc/zhejiang-2026-easy-mms/easymms.pcap' -q -z io,phs | head -40
```

**2. Map the IEC 61850 MMS conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/ctf-cn-competitions-misc/zhejiang-2026-easy-mms/easymms.pcap' -Y mms -T fields -e ip.src -e ip.dst -e mms.confirmedServiceRequest | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag write (service 5) changes IED settings or operates controls; getNameList (1) and getVariableAccessAttributes (6) map the IED data model; file services (fileOpen/fileRead/obtainFile) move configuration in and out.

```bash
tshark -r 'data/ctf-cn-competitions-misc/zhejiang-2026-easy-mms/easymms.pcap' -Y 'mms.confirmedServiceRequest == 5' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Decode the protocol fields**

Register values, write payloads and odd function codes are the usual hiding places — try ASCII.

```bash
tshark -r 'data/ctf-cn-competitions-misc/zhejiang-2026-easy-mms/easymms.pcap' -Y 'mms.data.visible-string' -T fields -e mms.data.visible-string | head -60
strings -n 6 'data/ctf-cn-competitions-misc/zhejiang-2026-easy-mms/easymms.pcap' | grep -iE 'flag|ctf|\{' | head
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

A public write-up exists — work it yourself first, then compare: https://github.com/yomymy/industrial-internet-security-2026-writeup

**Computed evidence (auto-extracted with tshark — verify it yourself):** IEC 61850 MMS operations — getNameList ×351, getVariableAccessAttributes ×211, fileOpen ×72, fileRead ×44, write ×32, 12 ×26, read ×17, fileClose ×9; dangerous-operation matches: 32 (top sources: 192.168.2.112 ×32); top conversations in easymms.pcap: 192.168.2.112↔192.168.2.53 (8,518 pkts); flag-like strings found by `strings`: none in plain text (decode protocol fields) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: Competition organisers; archived by CTF-Archives, C1oudfL0w0, TajangSec, ChaMd5 · License: None stated — credit each competition._

</details>

## Dataset & credit

**Competition organisers; archived by CTF-Archives, C1oudfL0w0, TajangSec, ChaMd5** — license: None stated — credit each competition

- [Dataset source — Chinese ICS competition challenges (CISCN, Fujian, Panda Cup](https://github.com/CTF-Archives)
- [Write-up / solution](https://github.com/yomymy/industrial-internet-security-2026-writeup)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/ctf-cn-competitions-misc/zhejiang-2026-easy-mms/easymms.pcap`

</details>
