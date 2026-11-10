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

## 2.6.0 release status

- Platform source and content: **PolyForm Noncommercial License 1.0.0**.
- Release artefact: `v2.6.0` is a signed annotated tag; the supply-chain lock is
  signed by the same release key.
- Third-party inventory: `scripts/check-licences.py` reports **OK** for the
  2.6.0 tree.
- No new third-party runtime dependencies ship in 2.6.0. Event certificates
  reuse the existing `fpdf2`, Pillow, and `qrcode` packages.
- The Grade 10-12 CyberChef lab exercises link to CyberChef, an external
  Apache-2.0 browser tool, not bundled or redistributed by this repository.
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

CyberChef is linked as an external browser tool from the student Tools menu and
the three Grade 9 CyberChef labs. It is licensed under Apache-2.0, is not
bundled or redistributed by this repository, and is attributed in
`THIRD_PARTY_NOTICES.md` with the licence text in
`THIRD_PARTY_LICENSES/Apache-2.0.txt`.

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
