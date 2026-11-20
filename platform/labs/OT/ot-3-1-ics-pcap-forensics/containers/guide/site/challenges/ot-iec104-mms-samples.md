# IEC-104 &amp; IEC 61850 MMS sample exchanges

**Power grid &amp; substations** · **Medium** · 0.0 MB · 0 capture file(s)

> A collection of IEC-104 and MMS client/server exchanges — learn the substation protocols' normal grammar.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

A collection of IEC-104 and MMS client/server exchanges — learn the substation protocols' normal grammar.

A protocol sample collection weighted toward IEC 60870-5-104 and IEC 61850 MMS client/server exchanges.

## Objectives

- Identify devices and protocol roles.
- Find and characterize the malicious activity.
- Use the dataset's labels/companion files to check yourself.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py ics-pcaps-haolipeng
```

- **[ICS protocol sample captures (IEC-104, MMS and more)](../DATASETS.md#ics-pcaps-haolipeng)** (`ics-pcaps-haolipeng`), ~4.2 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/haolipeng/ics-pcaps](https://github.com/haolipeng/ics-pcaps)

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/ics-pcaps-haolipeng/IEC104.pcap' --overview
```

**2. Deep-dive with Pcapper (--mms)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/ics-pcaps-haolipeng/IEC104.pcap' --mms --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/ics-pcaps-haolipeng/IEC104.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/ics-pcaps-haolipeng/IEC104.pcap'
tshark -r 'data/ics-pcaps-haolipeng/IEC104.pcap' -q -z io,phs | head -40
```

**2. Map the IEC 61850 MMS conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/ics-pcaps-haolipeng/IEC104.pcap' -Y mms -T fields -e ip.src -e ip.dst -e mms.confirmedServiceRequest | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag write (service 5) changes IED settings or operates controls; getNameList (1) and getVariableAccessAttributes (6) map the IED data model; file services (fileOpen/fileRead/obtainFile) move configuration in and out.

```bash
tshark -r 'data/ics-pcaps-haolipeng/IEC104.pcap' -Y 'mms.confirmedServiceRequest == 5' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

## Hints

<details><summary>Hint 1</summary>

Look for label files (CSV/JSON/logs) next to the captures — they are the answer key.

</details>

<details><summary>Hint 2</summary>

Compare attack captures against the clean/normal ones.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

The dataset's bundled labels and companion files are the authoritative answer key; the computed evidence below summarizes what the packets show.

**Computed evidence (auto-extracted with tshark — verify it yourself):** IEC 61850 MMS packets matching `mms`: 6; dangerous-operation matches: 0 for the IEC 61850 MMS filter (6 IEC 61850 MMS packets present, so the zero is real); top conversations in mms_top_level_remaining.pcap: 10.0.0.1↔10.0.0.2 (5 pkts) (basis: 3 of 88 capture file(s), first 300,000 packets each, smallest files carrying IEC 61850 MMS chosen)

_Dataset credit: haolipeng (GitHub) · License: No license stated in repo — credit the author._

</details>

## Dataset & credit

**haolipeng (GitHub)** — license: No license stated in repo — credit the author

- [Dataset source — ICS protocol sample captures (IEC-104, MMS and more)](https://github.com/haolipeng/ics-pcaps)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (88)</summary>

- `data/ics-pcaps-haolipeng/IEC104.pcap`
- `data/ics-pcaps-haolipeng/cancel_response.pcap`
- `data/ics-pcaps-haolipeng/client-server-mms-clean.pcap`
- `data/ics-pcaps-haolipeng/client-server-mms.pcap`
- `data/ics-pcaps-haolipeng/conclude_error.pcap`
- `data/ics-pcaps-haolipeng/get_name_list_full_response.pcap`
- `data/ics-pcaps-haolipeng/iec60780-5-104.pcap`
- `data/ics-pcaps-haolipeng/iec61850-goose/GOOSE.pcap`
- `data/ics-pcaps-haolipeng/iec61850-goose/GOOSE_DEMO.pcap`
- `data/ics-pcaps-haolipeng/iec61850-goose/GOOSE_all_data_primitives_fallbacks.pcap`
- `data/ics-pcaps-haolipeng/iec61850-goose/GOOSE_array_depth_truncated_10nest.pcap`
- `data/ics-pcaps-haolipeng/iec61850-goose/GOOSE_array_structure.pcap`
- `data/ics-pcaps-haolipeng/iec61850-goose/GOOSE_array_truncated.pcap`
- `data/ics-pcaps-haolipeng/iec61850-goose/GOOSE_t_binary_time.pcap`
- `data/ics-pcaps-haolipeng/iec61850-goose/GOOSE_t_unsupported_time.pcap`
- `data/ics-pcaps-haolipeng/iec61850-goose/Sample_File_GOOSE.pcap`
- `data/ics-pcaps-haolipeng/iec61850_full_session.pcap`
- `data/ics-pcaps-haolipeng/iec61850_get_name_list.pcap`
- `data/ics-pcaps-haolipeng/iec61850_get_named_variableList_attributes.pcap`
- `data/ics-pcaps-haolipeng/iec61850_get_variable_access_attributes.pcap`
- `data/ics-pcaps-haolipeng/iec61850_read.pcap`
- `data/ics-pcaps-haolipeng/iec61850_read_variable_list_name.pcap`
- `data/ics-pcaps-haolipeng/iec61850_release.pcap`
- `data/ics-pcaps-haolipeng/iec61850_write.pcap`
- `data/ics-pcaps-haolipeng/initiate_error.pcap`
- `data/ics-pcaps-haolipeng/mms-readRequest.pcap`
- `data/ics-pcaps-haolipeng/mms.pcap`
- `data/ics-pcaps-haolipeng/mms_file_transfer/iec61850_mms_file_download.pcap`
- `data/ics-pcaps-haolipeng/mms_file_transfer/iec61850_mms_file_upload.pcap`
- `data/ics-pcaps-haolipeng/mms_firmware_write/iec61850_mms_firmware_segmented.pcap`
- `data/ics-pcaps-haolipeng/mms_firmware_write/iec61850_mms_firmware_segmented_multi.pcap`
- `data/ics-pcaps-haolipeng/mms_read_data_choice/iec61850_mms_read_data_array.pcap`
- `data/ics-pcaps-haolipeng/mms_read_data_choice/iec61850_mms_read_data_bcd.pcap`
- `data/ics-pcaps-haolipeng/mms_read_data_choice/iec61850_mms_read_data_binary_time.pcap`
- `data/ics-pcaps-haolipeng/mms_read_data_choice/iec61850_mms_read_data_bit_string.pcap`
- `data/ics-pcaps-haolipeng/mms_read_data_choice/iec61850_mms_read_data_boolean.pcap`
- `data/ics-pcaps-haolipeng/mms_read_data_choice/iec61850_mms_read_data_boolean_array.pcap`
- `data/ics-pcaps-haolipeng/mms_read_data_choice/iec61850_mms_read_data_floating_point.pcap`
- `data/ics-pcaps-haolipeng/mms_read_data_choice/iec61850_mms_read_data_integer.pcap`
- `data/ics-pcaps-haolipeng/mms_read_data_choice/iec61850_mms_read_data_mms_string.pcap`
- `data/ics-pcaps-haolipeng/mms_read_data_choice/iec61850_mms_read_data_octet_string.pcap`
- `data/ics-pcaps-haolipeng/mms_read_data_choice/iec61850_mms_read_data_structure.pcap`
- `data/ics-pcaps-haolipeng/mms_read_data_choice/iec61850_mms_read_data_unsigned.pcap`
- `data/ics-pcaps-haolipeng/mms_read_data_choice/iec61850_mms_read_data_utc_time.pcap`
- `data/ics-pcaps-haolipeng/mms_read_data_choice/iec61850_mms_read_data_visible_string.pcap`
- `data/ics-pcaps-haolipeng/mms_top_level_remaining.pcap`
- `data/ics-pcaps-haolipeng/mms_write/write_01_vmd_integer_invoke_only_response.pcap`
- `data/ics-pcaps-haolipeng/mms_write/write_02_domain_boolean_success_response.pcap`
- `data/ics-pcaps-haolipeng/mms_write/write_03_multi_variable_struct_partial_failure.pcap`
- `data/ics-pcaps-haolipeng/mms_write/write_04_variable_list_name_unsigned_success.pcap`
- `data/ics-pcaps-haolipeng/mms_write/write_05_alternate_component_index.pcap`
- `data/ics-pcaps-haolipeng/mms_write/write_06_alternate_range_all_elements.pcap`
- `data/ics-pcaps-haolipeng/mms_write/write_07_unknown_alternate_malformed_failure_response.pcap`
- `data/ics-pcaps-haolipeng/profinet/ChangeIPUsingPureDCP.pcap`
- `data/ics-pcaps-haolipeng/profinet/PN-DCP.pcap`
- `data/ics-pcaps-haolipeng/profinet/PNIO-CM-2.pcap`
- `data/ics-pcaps-haolipeng/profinet/PNIO-CM.pcap`
- `data/ics-pcaps-haolipeng/profinet/PROFINET-RT.pcap`
- `data/ics-pcaps-haolipeng/profinet/dcp-vlan.pcap`
- `data/ics-pcaps-haolipeng/profinet/profinet-vlan.pcap`
- `data/ics-pcaps-haolipeng/profinet/profinet_pure_dcp.pcap`
- `data/ics-pcaps-haolipeng/profinet_synthetic/synthetic-get-dcp.pcap`
- `data/ics-pcaps-haolipeng/profinet_synthetic/synthetic-hello-dcp.pcap`
- `data/ics-pcaps-haolipeng/profinet_synthetic/synthetic-malformed-dcp.pcap`
- `data/ics-pcaps-haolipeng/profinet_synthetic/synthetic-non-dcp.pcap`
- `data/ics-pcaps-haolipeng/read_response_with_data.pcap`
- `data/ics-pcaps-haolipeng/s7_common/s7comm_downloading_block_db1.pcap`
- `data/ics-pcaps-haolipeng/s7_common/s7comm_plc_control_full.pcap`
- `data/ics-pcaps-haolipeng/s7_common/s7comm_plc_stop_full.pcap`
- `data/ics-pcaps-haolipeng/s7_common/s7comm_program_blocklist_onlineview.pcap`
- `data/ics-pcaps-haolipeng/s7_common/s7comm_reading_plc_status.pcap`
- `data/ics-pcaps-haolipeng/s7_common/s7comm_reading_setting_plc_time.pcap`
- `data/ics-pcaps-haolipeng/s7_common/s7comm_varservice_libnodavedemo.pcap`
- `data/ics-pcaps-haolipeng/s7_common/s7comm_varservice_libnodavedemo_bench.pcap`
- `data/ics-pcaps-haolipeng/s7_common/snap7_s300_stop.pcap`
- `data/ics-pcaps-haolipeng/s7_common/step7_s300_stop.pcap`
- `data/ics-pcaps-haolipeng/software_version_test/ftp_banner.pcap`
- `data/ics-pcaps-haolipeng/software_version_test/ftp_proftpd.pcap`
- `data/ics-pcaps-haolipeng/software_version_test/http_apache.pcap`
- `data/ics-pcaps-haolipeng/software_version_test/http_nginx.pcap`
- `data/ics-pcaps-haolipeng/software_version_test/mysql_complete.pcap`
- `data/ics-pcaps-haolipeng/software_version_test/pgsql.pcap`
- `data/ics-pcaps-haolipeng/software_version_test/redis_hello.pcap`
- `data/ics-pcaps-haolipeng/software_version_test/redis_info.pcap`
- `data/ics-pcaps-haolipeng/software_version_test/ssh.pcap`
- `data/ics-pcaps-haolipeng/software_version_test/ssh_traffic.pcap`
- `data/ics-pcaps-haolipeng/software_version_test/telnet.pcap`
- `data/ics-pcaps-haolipeng/unconfirmed_information_report.pcap`

</details>
