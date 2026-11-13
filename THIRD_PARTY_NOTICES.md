# Third-Party Notices

This file is the third-party attribution inventory for OpenCyberRange. It is
**not legal advice**. Confirm the exact licence for the versions you distribute
and include the full licence text and copyright notice for each component.

This updated build is based on the upstream OpenCyberRange/OCR-Lite build by
Lewis Heuermann. Keep the upstream `LICENSE`, `NOTICE`, and
[`BUILD_NOTICE.md`](BUILD_NOTICE.md) with any distribution.

## Attribution checklist

Before publishing a source archive, container image, or hosted deployment:

1. Keep the project `LICENSE`, `NOTICE`, `LICENSING.md`, and `BUILD_NOTICE.md`.
2. Keep the licence text for every third-party component you distribute.
3. Preserve copyright lines and any `NOTICE` files required by Apache-2.0
   components.
4. Include the licence text for MPL-2.0 and LGPL components listed below.
5. Audit the packages installed inside each lab container, not only the
   backend and frontend.
6. Generate an SBOM for each release and store it with the build artifacts.

Possible SBOM commands:

```bash
cd platform/backend
pip-audit -r requirements.txt
# or generate a CycloneDX SBOM with your preferred tool

cd ../frontend
npm sbom --sbom-format=cyclonedx > ../../sbom-frontend.cdx.json
```

## Project licence

The project source and its original content are licensed under the
**PolyForm Noncommercial License 1.0.0**. See [`LICENSE`](LICENSE),
[`NOTICE`](NOTICE), [`LICENSING.md`](LICENSING.md), and
[`BUILD_NOTICE.md`](BUILD_NOTICE.md). Third-party components remain under
their own licences; the project licence does not override them.

## Release 4 update

- Backend adds `ldap3==2.9.1` (LGPL-3.0-only), `python3-saml==1.16.0` (MIT),
  `lxml` (BSD-3-Clause), and `xmlsec` (MIT) for enterprise directory and SAML
  sign-in. Licence texts are in `THIRD_PARTY_LICENSES/LGPL-3.0.txt`,
  `MIT.txt`, and `BSD-3-Clause.txt`.
- The optional SSO test stack adds Dex (`ghcr.io/dexidp/dex:v2.42.0`,
  Apache-2.0) and osixia/openldap 1.5.0 (MIT image, OpenLDAP Public License 2.8
  server). The OpenLDAP text is `THIRD_PARTY_LICENSES/OpenLDAP-2.8.txt`.
- The topology node image (`ocr-lab/topology-node:latest`) is built locally from
  `platform/topology-node`. It contains Alpine packages, OpenSSH (BSD), iproute2
  (GPL-2.0), nftables (GPL-2.0), and Python (PSF). The licence texts already in
  this directory cover GPL-2.0 and BSD-3-Clause. A CycloneDX SBOM is committed at
  `platform/backend/app/data/about/sbom/topology-node.cdx.json`; the image build
  context is covered by `supply-chain.lock.json`.
- Workbook PDF export vendors `html2pdf.js` 0.10.2 at
  `Workbook/javascripts/html2pdf.bundle.min.js` (MIT, Copyright Erik Koopmans).
  The licence text is `Workbook/javascripts/html2pdf.LICENSE.txt`; the source is
  pinned from the 0.10.2 release and its SHA256 is recorded in the workbook
  vendor note.
- Both SSO images are profile-gated (`--profile sso`). They are pulled, not
  redistributed, and are not started on a normal install.
- Release 4 changes are recorded in `CHANGELOG.md`, `versions.yaml`, and the
  About inventory (`platform/backend/app/data/about/about.json`).

## 2.7.0 update

- No new third-party runtime dependencies are shipped in 2.7.0. Level quizzes
  reuse the existing backend stack.
- `scripts/check-licences.py` reports **OK** for the 2.7.0 tree.
- Valkey (`valkey/valkey:9.1.3-alpine`, BSD-3-Clause) replaces Redis 7.2 as the
  rate-limit store. The client is RESP-compatible, so the `redis://` URI and
  `redis-py` dependency are unchanged.
- Release signing uses GnuPG; it is not redistributed with the platform.

## 2.6.0 update

- No new third-party runtime dependencies are shipped in 2.6.0. Event
  certificates reuse the existing `fpdf2`, Pillow, and `qrcode` packages.
- `scripts/check-licences.py` reports **OK** for the 2.6.0 tree.
- CyberChef ships as a pinned static build in the frontend image
  (`/tools/cyberchef/`, Apache-2.0) so the student Tools panel works without
  internet access. Its notice and licence text are included here.
- Valkey is not bundled in 2.6.0. It is under evaluation as a BSD-3-Clause
  replacement for the Redis 7.2 rate-limit store; if adopted, its notice and pin
  will be added here and to the supply-chain lock.
- `scripts/GDG-Deploy.sh` uses the operator's Google Cloud CLI; the CLI is not
  redistributed with OpenCyberRange.
- GitHub Actions workflows use third-party actions; their licence terms remain
  with the action authors.
- Release signing uses GnuPG; it is not redistributed with the platform.
- The active release key fingerprint is
  `8E81 B5F3 FDC5 F5A6 2B0C 2587 91FD 6FBC 4ADA FDA2`.

## Brand assets

The **SWOCTS** name and logo/crest are owned by **SWOCTS** and were created and
designed by **Avery Chaykoski**. They are brand assets, not software, and are
not licensed under the PolyForm Noncommercial License 1.0.0. See
[`BRANDING.md`](BRANDING.md). The OpenCyberRange name and shield are upstream
marks; keep their attribution.

## Backend runtime dependencies

These are the direct production dependencies from
`platform/backend/requirements.txt`. Transitive dependencies add more MIT, BSD,
Apache-2.0, ISC, PSF, and MPL-2.0 components; an SBOM is the reliable inventory.

| Package | Licence family | Notes |
|---------|----------------|-------|
| fastapi | MIT | Include copyright notice |
| uvicorn | BSD-3-Clause | Include copyright notice |
| sqlalchemy | MIT | Include copyright notice |
| psycopg (v3) | LGPL-3.0-only | Notice-sensitive; include licence and source/relink information |
| PyJWT | MIT | Include copyright notice |
| pwdlib | MIT | Include copyright notice |
| argon2-cffi | MIT | Include copyright notice |
| bcrypt | Apache-2.0 | Include licence and any NOTICE |
| python-multipart | Apache-2.0 | Include licence |
| pydantic | MIT | Include copyright notice |
| pydantic-settings | MIT | Include copyright notice |
| email-validator | Unlicense / CC0-1.0 | Public-domain dedication |
| PyYAML | MIT | Include copyright notice |
| docker (Python SDK) | Apache-2.0 | Include licence and any NOTICE |
| APScheduler | MIT | Include copyright notice |
| cryptography | Apache-2.0 OR BSD-3-Clause | Include the chosen licence text |
| requests | Apache-2.0 | Include licence |
| slowapi | MIT | Include copyright notice |
| fpdf2 | LGPL-3.0-only | Notice-sensitive; include licence and relinking/source information |
| matplotlib | PSF-based | Include licence |
| aiohttp | Apache-2.0 | Include licence |
| websocket-client | Apache-2.0 | Include licence |
| pywinrm | MIT | Include copyright notice |
| alembic | MIT | Include copyright notice |
| pyotp | MIT | Include copyright notice |
| redis (Python client) | MIT | Include copyright notice |
| qrcode | BSD | Include copyright notice |
| Pillow | HPND | Include copyright and licence notice |
| ldap3 | LGPL-3.0-only | Include `LGPL-3.0.txt` and relinking/source information |
| python3-saml | MIT | Include copyright notice |
| lxml | BSD-3-Clause | Include copyright notice |
| xmlsec (python-xmlsec) | MIT | Include copyright notice |

Notable transitive components include `certifi` (MPL-2.0), `pathspec`
(MPL-2.0), `python-dateutil` (dual BSD/Apache-2.0), `pywin32` (PSF), `numpy`
(BSD), `starlette` (BSD), `uvloop` (MIT), `httptools` (MIT), `watchfiles`
(MIT), `websockets` (BSD), `python-dotenv` (BSD), and `mergedeep` (MIT,
metadata may report the licence as unknown).

**Do not add PyMuPDF (`fitz`/`pymupdf`) to the runtime.** It is dual-licensed
AGPL-3.0 or Artifex Commercial and is not part of the shipped requirements.

## Frontend runtime dependencies

From `platform/frontend/package.json`. The generated `dist/` bundles these into
the frontend image.

| Package | Licence family | Notes |
|---------|----------------|-------|
| vue | MIT | Include copyright notice |
| vue-router | MIT | Include copyright notice |
| axios | MIT | Include copyright notice |
| chart.js | MIT | Include copyright notice |
| vue-chartjs | MIT | Include copyright notice |
| marked | MIT | Include copyright notice |
| dompurify | MPL-2.0 OR Apache-2.0 | This build uses the Apache-2.0 option |
| sortablejs | MIT | Include copyright notice |
| @novnc/novnc | MPL-2.0 | Include licence; disclose modifications to MPL files |

`vue-eslint-parser` is a development/lint tool; it is not part of the runtime
bundle. Development-only packages (Vite, ESLint, plugins, `lightningcss`) are
not part of the shipped runtime, but their licences should still be retained if
you distribute the build toolchain or source archive. `lightningcss` is
MPL-2.0.

## Documentation and workbook tooling

The workbook is built with MkDocs and shipped as static HTML into the
`wiki_data` volume.

| Component | Licence family | Notes |
|-----------|----------------|-------|
| MkDocs | BSD | Include copyright notice |
| MkDocs Material | MIT | Include copyright notice |
| PyMdown Extensions | MIT | Include copyright notice |
| mkdocs-material-extensions | MIT | Include copyright notice |
| mergedeep | MIT | Transitive MkDocs dependency |
| Lunr | MIT | Bundled in the search index assets |
| Mermaid | MIT | If diagrams are rendered with Mermaid |
| html2pdf.js | MIT | If workbook PDF export is enabled |
| Pygments | BSD-2-Clause | Syntax highlighting |

MkDocs Material also bundles icon sets. If a built wiki includes them, retain
the notices for Material Design Icons (Apache-2.0), Font Awesome Free (icons
CC BY 4.0, fonts OFL-1.1, code MIT), Octicons (MIT), and Simple Icons (CC0-1.0).

## Fonts and icons

The MkDocs configurations request **Inter** and **JetBrains Mono**. If the
build bundles the font files, include the **SIL Open Font License 1.1** text and
the font copyright notices. Do not sell the fonts on their own. The frontend
CSS only names the fonts; it does not bundle them.

The inline SVG icons in `platform/frontend/src/components/icons/` include paths
adapted from:

- **Lucide** — ISC Licence.
- **Feather** — MIT Licence.

Other icons are original project artwork. See `THIRD_PARTY_LICENSES/` for the
licence texts.

## Container base images

Container images include their own licences and package notices. The current
image set is:

| Image | Licence family | Notes |
|-------|----------------|-------|
| `python:3.11-slim` | PSF plus Debian packages | Backend runtime |
| `python:3.12-slim` | PSF plus Debian packages | Wiki builder |
| `node:22-alpine` | Node.js MIT plus Alpine packages | Frontend build stage |
| `nginx:alpine` | BSD-2-Clause plus Alpine packages | Frontend runtime |
| `nginxinc/nginx-unprivileged:alpine` | BSD-2-Clause plus Alpine packages | VoIP evidence lab |
| `postgres:15-alpine` | PostgreSQL Licence plus Alpine packages | Platform database |
| `valkey/valkey:9.1.3-alpine` | BSD-3-Clause plus Alpine packages | Rate-limit counters |
| `mysql:8.0` | GPL-2.0 | Web-lab database server |
| `php:8.1-apache` | PHP Licence 3.01 plus Apache-2.0 | Web-lab web server |
| `python:3.12-alpine` | PSF plus Alpine packages | Network lab target |
| `alpine:3.18` / `alpine:3.19` | Alpine package licences | Lab sidecars and builders |
| `ubuntu:22.04` / `ubuntu:24.04` | Ubuntu/Debian package licences | Desktop and lab targets |
| `kalilinux/kali-rolling` | Kali/Debian package licences | RangeBox and one lab target |
| `remnux/remnux-distro:noble` | REMnux/Debian package licences | RemnuxBox |
| `0x4d4c/inetsim@sha256:01fdf65489db7b9a77a33cc336ba1d5ddf23aded35eeb23f2c6455290ca595e8` | INetSim GPL-2.0 plus Debian packages | Third-party image; pinned to the reviewed digest |
| `axllent/mailpit` | MIT | Development mail catcher only |

**Valkey is BSD-3-Clause.** It is the Linux Foundation fork of Redis 7.2 and is
RESP-compatible with the `redis-py` client. The bundled service stores only
ephemeral rate-limit counters.

If you distribute built images, include the licences for the installed packages
or provide a clear source/notice path. Do not assume the base image's licence
covers every package inside it.

## Lab toolchains

Each lab may install its own packages. The main notice-sensitive toolchains are:

| Component | Licence family | Where |
|-----------|----------------|-------|
| Apache HTTP Server | Apache-2.0 | Web lab containers |
| PHP | PHP Licence 3.01 (BSD-3-Clause-like) | Web lab containers |
| MySQL Server | GPL-2.0 | Web lab database containers |
| PyMySQL | MIT | Web lab application connector |
| Flask | BSD-3-Clause | Web lab applications |
| pymodbus | BSD-3-Clause | OT Modbus lab |
| paramiko | LGPL-2.1 | SSH lab target |
| Scapy | GPL-2.0-only | Build-time PCAP generator scripts (see below) |
| Volatility 3 | Volatility Software License 1.0 (VSL-1.0) | Memory/forensics labs and RangeBox |
| PyCryptodome | Public domain / BSD-2-Clause | Memory lab |
| INetSim | GPL-2.0 | Malware labs |
| Nmap | GPL-2.0 / Nmap Public Source Licence terms | RangeBox and lab tooling |
| SQLMap | GPL-2.0 | RangeBox and lab tooling |
| Wireshark / tshark | GPL-2.0 | RangeBox and network labs |
| Suricata | GPL-2.0 | RangeBox and network labs |
| John the Ripper | GPL-2.0 | RangeBox |
| Hydra | AGPL-3.0 | RangeBox |
| Masscan | AGPL-3.0 | RangeBox |
| Metasploit Framework | BSD-3-Clause | RangeBox `full` image |
| Impacket | Apache-2.0 | RangeBox |
| Hashcat | MIT | RangeBox |
| SecLists | MIT | RangeBox wordlists |
| zsteg | MIT | RangeBox / RemnuxBox |
| Snap7 / `libsnap7` | LGPL-3.0 | Tester sidecar (compiled from source) |
| python-snap7 | MIT | Tester sidecar |
| pycomm3 | MIT | Tester sidecar |
| asyncua | LGPL-3.0-or-later | Tester sidecar |
| Firefox ESR / Firefox | MPL-2.0 | RangeBox, UbuntuBox, RemnuxBox |
| XFCE / Xfce terminal | GPL/LGPL family | Desktop boxes |
| CyberChef | Apache-2.0 | Pinned static build bundled in the frontend image and served at `/tools/cyberchef/` |

Apache, pymodbus, PyMySQL, Flask, and the Python standard library carry
permissive licences; the GPL/AGPL/LGPL/VSL components above need their licence
texts and, where applicable, a source offer.

The **AGPL-3.0** Hydra and Masscan binaries are separate executables, not
linked into the platform. Keep them unmodified and provide the corresponding
source (Kali/Debian source packages are sufficient). Do not describe the
platform as a single combined AGPL work.

## Mixed-licence build-time PCAP generators

The following scripts import **Scapy (GPL-2.0-only)** and are therefore
distributed under **GPL-2.0-only**, not the project's PolyForm licence:

- `platform/labs/Forensics/forensics-2-1-voip-call-reconstruction/containers/evidence/generate_pcap.py`
- `platform/labs/Linux/linux-5-7-black-box-ctf/containers/server-delta/generate-pcap.py`
- `platform/labs/Network/network-1-1-packet-capture-analysis/containers/analyst/generate-pcap.py`
- `platform/labs/Network/network-1-2-http-traffic-analysis/containers/target/pcap_generator.py`
- `platform/labs/Network/network-1-2-log-correlation/containers/analyst/generate-pcap.py`
- `platform/labs/Network/network-2-1-ftp-credential-extraction/containers/analyst-workstation/generate_ftp_pcap.py`
- `platform/labs/Network/network-2-2-smtp-email-analysis/containers/analyst-workstation/generate_smtp_pcap.py`
- `platform/labs/Network/network-2-3-http-session-hijacking/containers/analyst-workstation/generate_http_pcap.py`
- `platform/labs/Network/network-2-4-dns-exfiltration/generate_dns_pcap.py`
- `platform/labs/Network/network-2-5-attack-chain-analysis/generate_attack_pcap.py`

Each file carries an `SPDX-License-Identifier: GPL-2.0-only` header. The
generated `.pcap` output is data, not a derivative work of Scapy. The GPL-2.0
text is in `THIRD_PARTY_LICENSES/GPL-2.0.txt`.

## Vendored binaries and data

| Component | Source | Obligation / note |
|-----------|--------|-------------------|
| `wstunnel` 10.5.2 (`platform/frontend/binaries/*.tar.gz`) | Erèbe / Romain Gerard | BSD-3-Clause; the licence text is inside each tarball and in `THIRD_PARTY_LICENSES/wstunnel-BSD-3-Clause.txt`. Copied into the frontend image as `/downloads/`. |
| SecLists wordlists | Daniel Miessler / SecLists | MIT. Used in RangeBox. |
| `rockyou-75.txt` | Kali/SecLists local wordlist | Not downloaded or vendored by this project. If an operator uses a breach-derived wordlist supplied by Kali, review the privacy/legal basis before redistributing it; prefer a synthetic or clearly licensed list. |
| `memdump.7z` / `memdump.mem` | Sam Bowne, [samsclass.info](https://samsclass.info/121/proj/) | Windows Server 2008 memory-analysis training image. No explicit open-source licence was found at the source. It is downloaded at image-build time for isolated classroom use, not vendored in this repository. Treat it as all-rights-reserved third-party material and obtain permission before redistributing the image outside your course. |
| Microsoft Windows symbol table (`ntkrpamp.pdb`) | Microsoft public symbol server | Not vendored in this repository. The memory-lab Dockerfile generates the Volatility JSON at image-build time from Microsoft's symbol server. Microsoft's symbol terms do not grant redistribution rights; the operator building the image accepts those terms. Review the terms before publishing a prebuilt image. |
| VoIP lab capture and audio | Generated by `platform/labs/Forensics/forensics-2-1-voip-call-reconstruction/containers/evidence/generate_pcap.py` | Original synthetic training data created for this project. The transcript is an original accessibility aid for that audio. |
| Workbook PCAPs | Generated by the build-time PCAP generators listed above | Synthetic training data; the generators that use Scapy are GPL-2.0-only. |

The memory lab's `case_brief.txt` and the workbook page repeat the Samsclass
attribution so learners can see where the evidence came from.

## `.opencode/skills` (development tooling)

`.opencode/skills/` is repository tooling, not part of the runtime image.

| Skill | Licence / source |
|-------|------------------|
| `opencyberrange-*`, `education-support-technologist` | Original project content, PolyForm Noncommercial 1.0.0 |
| `banner-design`, `brand`, `design`, `design-system`, `slides` | MIT, Claudekit |
| `ui-styling` | Apache-2.0 per its `LICENSE.txt`; upstream Claudekit metadata also declares MIT. This build follows the `LICENSE.txt`. |
| `ui-ux-pro-max` | MIT, Copyright (c) 2024 Next Level Builder |

The Claudekit and Next Level Builder skills are third-party development tools.
Keep their notices if you redistribute the repository or the skills.

## Notice-sensitive components

Pay particular attention to these, because a permissive-licence checklist alone
will miss them:

- `psycopg` (v3) — LGPL-3.0-only. Include the licence and enough information to
  replace/relink the library.
- `fpdf2` — LGPL-3.0-only. Include the licence and enough information to
  replace/relink the library.
- `@novnc/novnc` — MPL-2.0. Include the licence; if you modify MPL-covered
  files, make those files available under MPL-2.0.
- `dompurify` — MPL-2.0 OR Apache-2.0. This build uses Apache-2.0.
- `certifi` and `pathspec` — MPL-2.0. Include the licence notice.
- `lightningcss` — MPL-2.0 (build tooling only).
- Scapy — GPL-2.0-only; the build-time generators are GPL-2.0-only.
- Hydra and Masscan — AGPL-3.0; keep unmodified and provide source.
- Volatility 3 — VSL-1.0; keep the licence and source-availability notice.
- Snap7 and asyncua — LGPL-3.0 family; include the licence and source path.

## Container source offers

For GPL/AGPL/LGPL components distributed in container images, the corresponding
source is available from the distribution used to build the image:

- Debian: <https://www.debian.org/source/>
- Ubuntu: <https://launchpad.net/ubuntu/+source>
- Kali: <https://www.kali.org/docs/policy/kali-linux-open-source-policy/> and
  <https://pkg.kali.org/>
- Alpine: <https://git.alpinelinux.org/>
- REMnux: <https://docs.remnux.org/>
- MySQL: <https://dev.mysql.com/downloads/mysql/>
- PHP: <https://www.php.net/downloads>
- Valkey 9.1: <https://github.com/valkey-io/valkey>
- INetSim: <https://www.inetsim.org/>
- Snap7: <https://snap7.sourceforge.net/>
- Volatility 3: <https://github.com/volatilityfoundation/volatility3>
- Hydra: <https://github.com/vanhauser-thc/thc-hydra>
- Masscan: <https://github.com/robertdavidgraham/masscan>

If you publish prebuilt images, include the licence texts and a written offer
to provide the corresponding source for the GPL/AGPL/LGPL components.

## Suggested repository layout

The notice-sensitive licence texts are included here:

```text
LICENSE
NOTICE
LICENSING.md
BUILD_NOTICE.md
THIRD_PARTY_NOTICES.md
THIRD_PARTY_LICENSES/
  fpdf2-LGPL-3.0.txt
  psycopg3-LGPL-3.0.txt
  novnc-MPL-2.0.txt
  dompurify-MPL-2.0-OR-Apache-2.0.txt
  certifi-MPL-2.0.txt
  pathspec-MPL-2.0.txt
  wstunnel-BSD-3-Clause.txt
  valkey-BSD-3-Clause.txt
  GPL-2.0.txt
  LGPL-2.1.txt
  LGPL-3.0.txt
  lucide-ISC.txt
  feather-MIT.txt
```

Add the full licence text for any additional component you distribute. A
source-only archive has a smaller obligation than a built container image that
bundles every dependency.

---

_This inventory was prepared with AI assistance and reviewed as part of the
updated build. It is not legal advice. Verify it against the exact versions you
ship._
