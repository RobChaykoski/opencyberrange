# Protocol deep-dive — IEC 61850 MMS (76 unique captures)

**Protocol library** · **Medium** · 0.0 MB · 0 capture file(s)

> A deduplicated library of 76 IEC 61850 MMS captures from 4 public collections. Learn the protocol's grammar, then hunt its dangerous operations.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Every public IEC 61850 MMS sample in this range, deduplicated by SHA-256 across emreekin-ics-pcaps, ics-pcaps-haolipeng, inl-malcolm-ot-artifacts, iti-ics-security-tools-pcaps. Use it to learn what the protocol looks like on the wire — roles, operations, normal cadence — and to practice spotting the operations attackers abuse: write (service 5) changes IED settings or operates controls; getNameList (1) and getVariableAccessAttributes (6) map the IED data model; file services (fileOpen/fileRead/obtainFile) move configuration in and out.

## Objectives

- Identify clients/masters and servers/outstations across the samples.
- Enumerate the IEC 61850 MMS operations present.
- Flag every dangerous operation and its source.
- Map findings to ATT&amp;CK for ICS (T0855 Unauthorized Command Message · T0836 Modify Parameter · T0861 Point &amp; Tag Identification).

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch its 4 datasets first, from the repo root:

```bash
python3 scripts/fetch.py emreekin-ics-pcaps ics-pcaps-haolipeng inl-malcolm-ot-artifacts iti-ics-security-tools-pcaps
```

- **[ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset](../DATASETS.md#emreekin-ics-pcaps)** (`emreekin-ics-pcaps`), ~0.26 GB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/EmreEkin/ICS-Pcaps](https://github.com/EmreEkin/ICS-Pcaps)
- **[ICS protocol sample captures (IEC-104, MMS and more)](../DATASETS.md#ics-pcaps-haolipeng)** (`ics-pcaps-haolipeng`), ~4.2 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/haolipeng/ics-pcaps](https://github.com/haolipeng/ics-pcaps)
- **[INL Malcolm test artifacts — OT protocol samples](../DATASETS.md#inl-malcolm-ot-artifacts)** (`inl-malcolm-ot-artifacts`), ~99.2 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/idaholab/Malcolm-Test-Artifacts](https://github.com/idaholab/Malcolm-Test-Artifacts)
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
pcapper 'data/iti-ics-security-tools-pcaps/pcaps/IEC61850/piccolo.pcap' --overview
```

**2. Deep-dive with Pcapper (--mms)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/iti-ics-security-tools-pcaps/pcaps/IEC61850/piccolo.pcap' --mms --ot-commands
```

**3. Sweep the whole library**

```bash
pcapper data/emreekin-ics-pcaps/ --mms --ot-commands
```

**4. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/iti-ics-security-tools-pcaps/pcaps/IEC61850/piccolo.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/iti-ics-security-tools-pcaps/pcaps/IEC61850/piccolo.pcap'
tshark -r 'data/iti-ics-security-tools-pcaps/pcaps/IEC61850/piccolo.pcap' -q -z io,phs | head -40
```

**2. Map the IEC 61850 MMS conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/iti-ics-security-tools-pcaps/pcaps/IEC61850/piccolo.pcap' -Y mms -T fields -e ip.src -e ip.dst -e mms.confirmedServiceRequest | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag write (service 5) changes IED settings or operates controls; getNameList (1) and getVariableAccessAttributes (6) map the IED data model; file services (fileOpen/fileRead/obtainFile) move configuration in and out.

```bash
tshark -r 'data/iti-ics-security-tools-pcaps/pcaps/IEC61850/piccolo.pcap' -Y 'mms.confirmedServiceRequest == 5' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Sweep the whole library**

```bash
for f in 'data/iti-ics-security-tools-pcaps/pcaps/IEC61850/piccolo.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/IEC61850/Sample_File_MMS_and_GOOSE.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/IEC61850/8d7c7db0-9804-012b-b2a6-0016cb8cea27.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/IEC61850/MMS - Specific Commands/mms-initiateDownloadSequence.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/IEC61850/MMS - Specific Commands/mms-startRequest.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/IEC61850/MMS - Specific Commands/mms-resumeRequest.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/IEC61850/MMS - Specific Commands/mms-getDomainAttributes.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/IEC61850/MMS - Specific Commands/mms-initiateUploadSequence.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/IEC61850/MMS - Specific Commands/mms-stopRequest.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/IEC61850/MMS - Specific Commands/iec61850_get_name_list.pcap'; do echo "== $f"; tshark -r "$f" -Y 'mms.confirmedServiceRequest == 5' 2>/dev/null | head -3; done
```

## Hints

<details><summary>Hint 1</summary>

Wireshark display filter for the protocol: mms

</details>

<details><summary>Hint 2</summary>

Dangerous-operation filter: mms.confirmedServiceRequest == 5

</details>

<details><summary>Hint 3</summary>

Many library files are tiny protocol samples — read them packet by packet in Wireshark.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

A library, not a single puzzle: the deliverable is a per-capture table of roles and operations, with the dangerous ones flagged (write (service 5) changes IED settings or operates controls; getNameList (1) and getVariableAccessAttributes (6) map the IED data model; file services (fileOpen/fileRead/obtainFile) move configuration in and out). ATT&amp;CK for ICS: T0855 Unauthorized Command Message · T0836 Modify Parameter · T0861 Point &amp; Tag Identification. Sources are credited per collection in each folder's PROVENANCE.md.

**Computed evidence (auto-extracted with tshark — verify it yourself):** IEC 61850 MMS operations — identify ×1, 0 ×1; dangerous-operation matches: 0 for the IEC 61850 MMS filter (8 IEC 61850 MMS packets present, so the zero is real); top conversations in mms_top_level_remaining.pcap: 10.0.0.1↔10.0.0.2 (5 pkts) (basis: 3 of 76 capture file(s), first 300,000 packets each, smallest files carrying IEC 61850 MMS chosen)

_Captures credited to: ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset — Emre Ekin (ICS Defense, icsdefense.net) · ICS protocol sample captures (IEC-104, MMS and more) — haolipeng (GitHub) · INL Malcolm test artifacts — OT protocol samples — Idaho National Laboratory (Malcolm) · ITI ICS-Security-Tools — sample ICS protocol captures — Information Trust Institute (ITI), University of Illinois Urbana-Champaign._

</details>

## Dataset & credit

**ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset — Emre Ekin (ICS Defense, icsdefense.net) · ICS protocol sample captures (IEC-104, MMS and more) — haolipeng (GitHub) · INL Malcolm test artifacts — OT protocol samples — Idaho National Laboratory (Malcolm) · ITI ICS-Security-Tools — sample ICS protocol captures — Information Trust Institute (ITI), University of Illinois Urbana-Champaign** — license: varies by collection — see each folder's PROVENANCE.md

- [Dataset source — ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset](https://github.com/EmreEkin/ICS-Pcaps)
- [Dataset source — ICS protocol sample captures (IEC-104, MMS and more)](https://github.com/haolipeng/ics-pcaps)
- [Dataset source — INL Malcolm test artifacts — OT protocol samples](https://github.com/idaholab/Malcolm-Test-Artifacts)
- [Dataset source — ITI ICS-Security-Tools — sample ICS protocol captures](https://github.com/ITI/ICS-Security-Tools/tree/master/pcaps)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (76)</summary>

- `data/iti-ics-security-tools-pcaps/pcaps/IEC61850/piccolo.pcap`
- `data/iti-ics-security-tools-pcaps/pcaps/IEC61850/Sample_File_MMS_and_GOOSE.pcap`
- `data/iti-ics-security-tools-pcaps/pcaps/IEC61850/8d7c7db0-9804-012b-b2a6-0016cb8cea27.pcap`
- `data/iti-ics-security-tools-pcaps/pcaps/IEC61850/MMS - Specific Commands/mms-initiateDownloadSequence.pcap`
- `data/iti-ics-security-tools-pcaps/pcaps/IEC61850/MMS - Specific Commands/mms-startRequest.pcap`
- `data/iti-ics-security-tools-pcaps/pcaps/IEC61850/MMS - Specific Commands/mms-resumeRequest.pcap`
- `data/iti-ics-security-tools-pcaps/pcaps/IEC61850/MMS - Specific Commands/mms-getDomainAttributes.pcap`
- `data/iti-ics-security-tools-pcaps/pcaps/IEC61850/MMS - Specific Commands/mms-initiateUploadSequence.pcap`
- `data/iti-ics-security-tools-pcaps/pcaps/IEC61850/MMS - Specific Commands/mms-stopRequest.pcap`
- `data/iti-ics-security-tools-pcaps/pcaps/IEC61850/MMS - Specific Commands/iec61850_get_name_list.pcap`
- `data/iti-ics-security-tools-pcaps/pcaps/IEC61850/MMS - Specific Commands/mms-readRequest.pcap`
- `data/iti-ics-security-tools-pcaps/pcaps/IEC61850/MMS - Specific Commands/mms-getAlarmSummary.pcap`
- `data/iti-ics-security-tools-pcaps/pcaps/IEC61850/MMS - Specific Commands/mms-confirmedRequestPDU.pcap`
- `data/iti-ics-security-tools-pcaps/pcaps/IEC61850/MMS - Specific Commands/iec61850_release.pcap`
- `data/iti-ics-security-tools-pcaps/pcaps/IEC61850/MMS - Specific Commands/iec61850_write.pcap`
- `data/iti-ics-security-tools-pcaps/pcaps/IEC61850/MMS - Specific Commands/iec61850_read.pcap`
- `data/iti-ics-security-tools-pcaps/pcaps/IEC61850/MMS - Specific Commands/iec61850_get_variable_access_attributes.pcap`
- `data/iti-ics-security-tools-pcaps/pcaps/IEC61850/MMS - Specific Commands/mms-deleteProgramInvocation.pcap`
- `data/iti-ics-security-tools-pcaps/pcaps/IEC61850/MMS - Specific Commands/mms-cancelRequest.pcap`
- `data/iti-ics-security-tools-pcaps/pcaps/IEC61850/MMS - Specific Commands/mms-takeControl.pcap`
- `data/iti-ics-security-tools-pcaps/pcaps/IEC61850/MMS - Specific Commands/mms-terminateUploadSequence.pcap`
- `data/iti-ics-security-tools-pcaps/pcaps/IEC61850/MMS - Specific Commands/mms-killRequest.pcap`
- `data/iti-ics-security-tools-pcaps/pcaps/IEC61850/MMS - Specific Commands/mms-relinquishControl.pcap`
- `data/iti-ics-security-tools-pcaps/pcaps/IEC61850/MMS - Specific Commands/mms-resetRequest.pcap`
- `data/emreekin-ics-pcaps/IEC61850/mms1.pcap`
- `data/emreekin-ics-pcaps/IEC61850/setvalue.pcap`
- `data/emreekin-ics-pcaps/IEC61850/mms2.pcap`
- `data/emreekin-ics-pcaps/IEC61850/mmsy1.pcap`
- `data/emreekin-ics-pcaps/IEC61850/mmsy.pcap`
- `data/emreekin-ics-pcaps/IEC61850/Substation/simens.pcap`
- `data/emreekin-ics-pcaps/IEC61850/Substation/circuit.pcap`
- `data/emreekin-ics-pcaps/IEC61850/Substation/ABB2.pcap`
- `data/emreekin-ics-pcaps/IEC61850/Substation/wamp.pcap`
- `data/emreekin-ics-pcaps/IEC61850/Substation/ABB3.pcap`
- `data/emreekin-ics-pcaps/IEC61850/Substation/ABB1.pcap`
- `data/emreekin-ics-pcaps/IEC61850/Substation/simens_merge.pcap`
- `data/ics-pcaps-haolipeng/iec61850_read_variable_list_name.pcap`
- `data/ics-pcaps-haolipeng/cancel_response.pcap`
- `data/ics-pcaps-haolipeng/unconfirmed_information_report.pcap`
- `data/ics-pcaps-haolipeng/client-server-mms.pcap`
- `data/ics-pcaps-haolipeng/mms_top_level_remaining.pcap`
- `data/ics-pcaps-haolipeng/iec61850_full_session.pcap`
- `data/ics-pcaps-haolipeng/get_name_list_full_response.pcap`
- `data/ics-pcaps-haolipeng/initiate_error.pcap`
- `data/ics-pcaps-haolipeng/mms-readRequest.pcap`
- `data/ics-pcaps-haolipeng/iec61850_get_named_variableList_attributes.pcap`
- `data/ics-pcaps-haolipeng/read_response_with_data.pcap`
- `data/ics-pcaps-haolipeng/client-server-mms-clean.pcap`
- `data/ics-pcaps-haolipeng/conclude_error.pcap`
- `data/ics-pcaps-haolipeng/mms.pcap`
- `data/ics-pcaps-haolipeng/mms_read_data_choice/iec61850_mms_read_data_octet_string.pcap`
- `data/ics-pcaps-haolipeng/mms_read_data_choice/iec61850_mms_read_data_array.pcap`
- `data/ics-pcaps-haolipeng/mms_read_data_choice/iec61850_mms_read_data_floating_point.pcap`
- `data/ics-pcaps-haolipeng/mms_read_data_choice/iec61850_mms_read_data_utc_time.pcap`
- `data/ics-pcaps-haolipeng/mms_read_data_choice/iec61850_mms_read_data_integer.pcap`
- `data/ics-pcaps-haolipeng/mms_read_data_choice/iec61850_mms_read_data_structure.pcap`
- `data/ics-pcaps-haolipeng/mms_read_data_choice/iec61850_mms_read_data_boolean_array.pcap`
- `data/ics-pcaps-haolipeng/mms_read_data_choice/iec61850_mms_read_data_mms_string.pcap`
- `data/ics-pcaps-haolipeng/mms_read_data_choice/iec61850_mms_read_data_bit_string.pcap`
- `data/ics-pcaps-haolipeng/mms_read_data_choice/iec61850_mms_read_data_boolean.pcap`
- `data/ics-pcaps-haolipeng/mms_read_data_choice/iec61850_mms_read_data_binary_time.pcap`
- `data/ics-pcaps-haolipeng/mms_read_data_choice/iec61850_mms_read_data_bcd.pcap`
- `data/ics-pcaps-haolipeng/mms_read_data_choice/iec61850_mms_read_data_unsigned.pcap`
- `data/ics-pcaps-haolipeng/mms_read_data_choice/iec61850_mms_read_data_visible_string.pcap`
- `data/ics-pcaps-haolipeng/mms_write/write_07_unknown_alternate_malformed_failure_response.pcap`
- `data/ics-pcaps-haolipeng/mms_write/write_03_multi_variable_struct_partial_failure.pcap`
- `data/ics-pcaps-haolipeng/mms_write/write_06_alternate_range_all_elements.pcap`
- `data/ics-pcaps-haolipeng/mms_write/write_05_alternate_component_index.pcap`
- `data/ics-pcaps-haolipeng/mms_write/write_02_domain_boolean_success_response.pcap`
- `data/ics-pcaps-haolipeng/mms_write/write_01_vmd_integer_invoke_only_response.pcap`
- `data/ics-pcaps-haolipeng/mms_write/write_04_variable_list_name_unsigned_success.pcap`
- `data/ics-pcaps-haolipeng/mms_firmware_write/iec61850_mms_firmware_segmented.pcap`
- `data/ics-pcaps-haolipeng/mms_firmware_write/iec61850_mms_firmware_segmented_multi.pcap`
- `data/ics-pcaps-haolipeng/mms_file_transfer/iec61850_mms_file_upload.pcap`
- `data/ics-pcaps-haolipeng/mms_file_transfer/iec61850_mms_file_download.pcap`
- `data/inl-malcolm-ot-artifacts/Malcolm-Test-Artifacts-main/pcap/protocols/S7comm.pcap`

</details>
