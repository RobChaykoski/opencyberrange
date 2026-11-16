# External open datasets for lab building

This page is the operator and lab-author guide for the external datasets
registered in
`platform/backend/app/data/external-datasets.yaml`. The registry is a
provenance and handling record. It is not a copy of the datasets, and the
public repository does not vendor raw third-party telemetry.

## Why a registry instead of a data dump

A link is not a licence. The sources below have different terms:

| Source | Licence | Redistribution | Access | Pin |
|---|---|---|---|---|
| [**Security Datasets**](https://securitydatasets.com/introduction.html) | MIT | Allowed with the MIT notice | Public download | Commit `d9d40ef1` |
| [**Canadian Institute for Cybersecurity datasets**](https://www.unb.ca/cic/datasets/index.html) | CIC dataset terms | Allowed with the dataset and paper citation | Public download or request | Dataset page |
| [**Splunk attack_data**](https://github.com/splunk/attack_data) | Apache-2.0 | Allowed with the Apache-2.0 notice | Public download, Git LFS | Commit `eb3ab742` |
| [**theZoo**](https://github.com/ytisf/theZoo) | GPL-3.0-or-later for tooling; samples excluded | Samples forbidden | Reference only | Repository |
| [**vx-underground malware repository**](https://vx-underground.org/) | No licence declared; live malware | Forbidden | Reference only | Repository |
| [**PCAP-ATTACK**](https://github.com/sbousseaden/PCAP-ATTACK) | No licence declared | Forbidden | Reference only | Commit `9ef5476d` |
| [**Aman Hardikar Forensics Practice Lab mind map**](https://www.amanhardikar.com/mindmaps/ForensicChallenges.html) | Free to use and share; attribution requested | Allowed with attribution | Reference only | Page |
| [**OWASP Juice Shop**](https://juice-shop.github.io/) | MIT | Allowed with the MIT notice | Pinned container image | `v20.4.0@sha256:9bba…` |

If a source has no declared licence, the default is **reference only**. Public
visibility does not grant permission to copy, mirror, or serve the material.

## Selected datasets

The registry records the exact file paths, sizes, SHA-256 values, ATT&CK
mappings, and pathway modules for fetchable entries. The main selections are:

### Security Datasets

- **Arp Cache Discovery** (`SDLIN-201110074812`) for Linux discovery.
- **DD Binary Padding Hash Change** (`SDLIN-201110081941`) for hash-independent
  detection.
- **Lsass Memory Dump via Comsvcs.dll** (`SDWIN-201018195009`) and **Empire
  Mimikatz LogonPasswords** (`SDWIN-190518202151`) for credential-access
  evidence.
- **Empire Invoke PsExec** (`SDWIN-190518210652`) for lateral movement.
- **Log4Shell** for a multi-source web-exploit hunt.
- **Golden SAML AD FS Mail Access** for cloud identity evidence.
- **LSASS Memory - Procdump campaign** and **APT29 Day 2** for capstone hunts.

Security Datasets is by Roberto Rodriguez (@Cyb3rWard0g), Jose Luis Rodriguez
(@Cyb3rPandaH), and the Open Threat Research community. It is MIT-licensed;
keep `THIRD_PARTY_LICENSES/Security-Datasets-MIT.txt` with any copy. Some
metadata and telemetry include simulated credentials; review and redact before
learner use.

### Canadian Institute for Cybersecurity (UNB)

- **CIC-IDS2017** and **CSE-CIC-IDS2018** for intrusion-detection baselines.
- **CIC-DDoS2019** for denial-of-service triage.
- **CIC-MalMem-2022** for memory-forensics and obfuscated-malware features.
- **CIC-Bell-DNS-EXF-2021** and **CIRA-CIC-DoHBrw-2020** for DNS evidence.
- **CCCS-CIC-AndMal-2020** for Android malware-family comparison.
- **CIC-IoT-Attack-2023** for IoT/OT flow enrichment.
- **CIC-Trap4Phish-2025** for phishing and quishing triage.
- **CIC-UNSW-NB15-2024** for adversarial-ML evaluation.

CIC permits redistribution and mirroring when the dataset and paper are cited.
The required citation for each selected dataset is in the registry entry and
must appear in the lab handout, the workbook, or the derived chart caption.
Cite the dataset and the paper, not only the CIC home page. The source page is
the authority if the terms change.

### Splunk attack_data

Splunk attack_data is an Apache-2.0 collection of curated attack telemetry. It
uses Git LFS; the small YAML descriptor is not the data. Fetch the media URL,
verify the SHA-256 in the registry, and keep the Apache-2.0 notice. Selected
techniques cover LSASS access, encoded PowerShell, SMB/Windows Admin Shares,
DNS exfiltration, long DNS queries, macro delivery, encoded HTTP POST,
scheduled tasks, and ProxyShell.

### Reference-only sources

- **theZoo** is a live-malware reference collection. Its GPL-3.0 licence covers
  the tooling, and the licence text expressly excludes the malware samples.
  This project does not copy, download, execute, or serve a sample.
- **vx-underground malware repository** is a public malware and source-code
  archive with no declared licence. Treat every item as live malware. It is a
  reading reference for an approved, isolated environment only.
- **PCAP-ATTACK** is a public PCAP collection with no licence file. Do not
  vendor a capture, bundle it in a container, or serve it from the platform
  until the author grants permission.
- The **Aman Hardikar Forensics Practice Lab mind map** is an index of
  challenges, CTFs, sample images, and tools. It is free to use and share, and
  we attribute it. Each linked resource keeps its own terms; verify it before
  use.

### Lab applications

**OWASP Juice Shop** is an MIT-licensed intentionally insecure web application
by Bjoern Kimminich and the OWASP Juice Shop contributors. It is registered as
a pinned lab application, not a dataset:

- image: `bkimminich/juice-shop:v20.4.0`
- digest: `sha256:9bbaecc41791f00b002bc65931cc5ff355fbdb941fa72b06558c18dace43197b`
- access: container image
- handling: isolated lab network, no egress, disposable storage, reset between
  learners, no real user data, no public exposure

See [`JUICE-SHOP-LABS.md`](JUICE-SHOP-LABS.md) for the lab blueprint, safety
rules, and evidence expectations. Juice Shop is not affiliated with or endorsed
by OpenCyberRange.

## Fetching a dataset

Security Datasets and Splunk attack_data can be fetched into a local,
gitignored cache:

```bash
python scripts/fetch-external-datasets.py --list
python scripts/fetch-external-datasets.py --dataset SDLIN-201110074812
python scripts/fetch-external-datasets.py --source security-datasets --all
python scripts/fetch-external-datasets.py --verify
```

The fetch script refuses reference-only and no-licence sources. It writes to
`platform/backend/app/data/external-datasets/cache/`, which is not committed.
It checks the size and SHA-256 recorded in the registry before reporting
success.

For CIC, download from the dataset page and record the citation in the lab
metadata. Do not add the full archive to the repository.

## Handling rules

- **No real learner or institutional data.** These are external teaching
  datasets, not production telemetry.
- **No live malware.** A malware sample is never copied into the public repo,
  a public lab image, or a served evidence directory.
- **Credential-bearing telemetry needs review.** Security Datasets and Splunk
  content can include simulated passwords, hashes, or tokens. Trim or redact
  before a learner sees it.
- **Keep the citation with the derivative.** A chart, query result, or model
  trained on a CIC dataset still needs the dataset and paper citation.
- **Do not widen the licence.** A MIT or Apache-2.0 file keeps its notice; a
  no-licence file keeps its reference-only status.
- **No egress from a lab.** Fetching is an author/operator action on the host,
  not a runtime action inside a learner lab.

## Validation

```bash
python scripts/check-external-datasets.py
python scripts/check-external-datasets.py --json
```

The check verifies source fields, https links, commit pins, hashes, pathway
references, reference-only handling, attribution in `THIRD_PARTY_NOTICES.md`,
and the absence of tracked cache files. It runs in CI with the other
governance checks.

## Attribution

See [`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md). The licence texts and
source notices are in `THIRD_PARTY_LICENSES/`.
