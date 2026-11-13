# Licensing

OpenCyberRange is source-available software with a free noncommercial edition
and paid commercial tiers.

The source of the free edition, OCR-Lite, is published in full under the
PolyForm Noncommercial License 1.0.0. Source-available is not the same as open
source: PolyForm Noncommercial is not an OSI-approved license, because it
withholds commercial use. Read it before you build on it.

Development happens in a separate private repository. What is published here is
the Lite release: the platform, the installer, and the lab tracks that edition
ships. Content packs and the Enterprise tier are not in this repository and are
not covered by the license in it.

## The two grants

**OCR-Lite (free).** The source in this repository, and every artifact built
from it, is licensed under the PolyForm Noncommercial License 1.0.0 (the
`LICENSE` file). In plain terms: schools, instructors, students, researchers,
and hobbyists may install, run, modify and study OCR-Lite at no cost for any
noncommercial purpose. Commercial use of any kind, including resale,
rebranding, paid hosting, or bundling into a paid offering, is not licensed.

**Content packs and OCR-Enterprise (commercial).** Paid content packs and the
Enterprise bundle are licensed per customer under a commercial agreement.
Nothing in the PolyForm grant extends to them. Contact the owner for
commercial terms.

## 4 release status

- Platform source and content: **PolyForm Noncommercial License 1.0.0**.
- Release artefact: `v4` is a **signed** annotated tag. The supply-chain lock is
  signed by the release key and verified with
  `scripts/supply_chain.py --check --signature supply-chain.lock.json.asc`.
  This supersedes the unsigned-tag notes in the older release sections below.
- Third-party inventory: `scripts/check-licences.py` reports **OK** for the
  Release 4 tree.
- The frontend runtime image is `nginx:alpine`, pinned by digest in
  `platform/frontend/Dockerfile` so a base-image refresh cannot change it
  silently.
- Workbook diagrams and PDF export vendor **Mermaid 11.17.2** and
  **html2pdf.js 0.10.2** (both MIT) under `Workbook/javascripts/`, with their
  licence texts. They are served from the wiki origin rather than a CDN.
- CyberChef remains a pinned static build in the frontend image
  (`/tools/cyberchef/`, Apache-2.0).
- Valkey **9.1.3** (BSD-3-Clause) is the rate-limit store in the Release 4
  compose files.

## 2.7.0 release status

- Platform source and content: **PolyForm Noncommercial License 1.0.0**.
- Release artefact: `v2.7.0` is an annotated tag. The supply-chain lock is
  signed by the release key; the tag itself is unsigned and should be signed on
  the release workstation if a signed tag is required.
- Third-party inventory: `scripts/check-licences.py` reports **OK** for the
  2.7.0 tree.
- No new third-party runtime dependencies ship in 2.7.0. Level quizzes reuse
  the existing backend models and routers.
- Valkey is not bundled in 2.7.0. It remains under evaluation as a BSD-3-Clause
  replacement for the Redis 7.2 rate-limit store.
- GitHub Actions workflows use third-party actions; their licences remain with
  the action authors.

## 2.6.0 release status

- Platform source and content: **PolyForm Noncommercial License 1.0.0**.
- Release artefact: `v2.6.0` is an annotated tag. The supply-chain lock is
  signed by the release key; the tag itself is unsigned and should be signed on
  the release workstation if a signed tag is required.
- Third-party inventory: `scripts/check-licences.py` reports **OK** for the
  2.6.0 tree.
- No new third-party runtime dependencies ship in 2.6.0. Event certificates
  reuse the existing `fpdf2`, Pillow, and `qrcode` packages.
- CyberChef ships as a pinned static build in the frontend image
  (`/tools/cyberchef/`, Apache-2.0) so the student Tools panel works without
  internet access. Its notice and licence text are included here.
- Valkey is not bundled in 2.6.0. It is under evaluation as a BSD-3-Clause
  replacement for the Redis 7.2 rate-limit store; if adopted, its notice and
  pin will be added to this file and the supply-chain lock.
- The `GDG-Deploy` script uses the operator's Google Cloud CLI and does not
  redistribute it.
- GitHub Actions workflows use third-party actions; their licences remain with
  the action authors.

## What the noncommercial grant covers

Per PolyForm Noncommercial, permitted purposes include use by educational
institutions, charitable organizations, public research organizations, and
government institutions regardless of funding source, plus personal study
and hobby use. If your organization charges for access to a deployment, or
uses the software to deliver a paid service, you need a commercial license.

## Notices

Every copy of the software must carry the `Required Notice:` line found at
the end of `LICENSE`, per the Notices section of the license. Third-party
software bundled with the platform carries its own notices; see
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) and the licence texts in
[`THIRD_PARTY_LICENSES/`](THIRD_PARTY_LICENSES/).

CyberChef is bundled as a pinned static build served from the student Tools
menu and the active-lab panel at `/tools/cyberchef/`. It is licensed under
Apache-2.0, is redistributed unmodified, and is attributed in
`THIRD_PARTY_NOTICES.md` with the licence text in
`THIRD_PARTY_LICENSES/Apache-2.0.txt`. The build version and SHA256 are pinned
in `platform/frontend/Dockerfile`.

## Mixed-licence components

Most of the repository is PolyForm Noncommercial 1.0.0. A small number of
build-time lab generators are **GPL-2.0-only** because they import Scapy, which
is GPL-2.0-only. They carry an `SPDX-License-Identifier: GPL-2.0-only` header
and are listed in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md). Their
generated `.pcap` output is data and is not a derivative work of Scapy.

Third-party container images, lab tools, and development skills keep their own
licences. The PolyForm grant does not relicense them, and their notices must be
kept with any distribution. In particular:

- Redis is pinned to **7.2**, which is BSD-3-Clause. Redis 7.4 and later are
  RSALv2/SSPLv1 and must not be substituted without a licence review.
- Hydra and Masscan in the RangeBox image are **AGPL-3.0**; they are separate
  executables, not linked into the platform. Keep them unmodified and provide
  their source.
- Volatility 3 uses the **Volatility Software License 1.0**, not an OSI
  licence.
- `fpdf2` and `psycopg` are **LGPL-3.0-only**; their licence texts and source
  information are included.

## Branding

The upstream **OpenCyberRange** name, copyright notice, and `Required Notice:`
line must remain. **SWOCTS Cyber Range** is the name of this deployment and does
not replace the upstream mark.

The **SWOCTS** name and logo/crest are owned by **SWOCTS** and were created and
designed by **Avery Chaykoski**. They are brand assets, not software, and are not
licensed under the PolyForm Noncommercial License 1.0.0. The software licence
does not grant a trademark, brand, or logo licence. See
[`BRANDING.md`](BRANDING.md).

If you distribute this build under a different name or brand, confirm that you
have permission from the relevant rights holder.

## Trademarks

"OpenCyberRange" and the OCR content universes are trademarks and creative
works of the owner. No license to the marks is granted by the software
license. Copies of the software may not be distributed under a different
name or brand.

## Updated build

This repository is an updated build maintained by Robert Chaykoski. It is based
on the original OpenCyberRange/OCR-Lite build created by Lewis Heuermann and
published at <https://github.com/syntaxoverride/opencyberrange>. It is not an
official upstream release and is not affiliated with or endorsed by the original
author.

The original copyright and `Required Notice:` line remain in force. This
updated build does not transfer ownership of the original work or grant any
additional rights, and it remains subject to the PolyForm Noncommercial License
1.0.0 in [`LICENSE`](LICENSE). See [`BUILD_NOTICE.md`](BUILD_NOTICE.md) for the
build-specific attribution and change summary.

## History

An earlier repository held a placeholder MIT license naming "OpenCyberRange
Contributors". It was private, and this release is the first publication of
OpenCyberRange's source under any license.

That earlier repository accepted pull requests. If you contributed to it and
believe your work appears here, contact the copyright holder: the intent is to
credit or remove it, whichever you prefer.
