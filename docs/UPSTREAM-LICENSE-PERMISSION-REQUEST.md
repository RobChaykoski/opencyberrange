# Upstream relicensing permission request

Status: **draft, not sent.** Review with counsel before sending. No licence
change will be made until a written response is on file.

## Why this exists

This repository is an independent updated build of OpenCyberRange. The committed
`LICENSE` names **Lewis Heuermann** as the copyright holder and carries a
`Required Notice` under the PolyForm Noncommercial License 1.0.0. A derivative
build cannot be relicensed to AGPL-3.0 (or any other licence) without the
copyright holder's permission.

## Draft message

> **Subject:** Permission to relicense the updated OpenCyberRange build
>
> Hi Lewis,
>
> I maintain the updated SWOCTS Cyber Range build of OpenCyberRange
> (`RobChaykoski/opencyberrange`), which keeps your copyright, the `Required
> Notice`, and the PolyForm Noncommercial terms.
>
> I am considering moving the code to **AGPL-3.0-or-later** and the curriculum
> text to **CC BY-SA 4.0**, so public institutions can audit and reuse it under
> a recognised open-source licence. That change needs your written permission for
> the parts you own. Attribution and the original notice would stay prominent.
>
> Could you confirm one of these, in writing?
>
> 1. You permit the combined build to be relicensed under AGPL-3.0-or-later
>    (code) and CC BY-SA 4.0 (curriculum), with attribution preserved.
> 2. You permit only my own contributions to be licensed that way, with your code
>    remaining under PolyForm Noncommercial.
> 3. You prefer to discuss a commercial or dual-licensing arrangement instead.
>
> Until I hear back, nothing changes: the repository stays on PolyForm
> Noncommercial 1.0.0 with your notice intact.
>
> Thanks for the original work — it is the reason this build exists.
>
> Robert Chaykoski

## Record

| Item | Value |
|---|---|
| Sent | _not sent_ |
| Recipient | Lewis Heuermann (upstream author) |
| Response | _pending_ |
| Decision | _pending_ |
| Licence after decision | PolyForm Noncommercial 1.0.0 (unchanged) |

## If permission is granted

1. Update `LICENSE`, `NOTICE`, `LICENSING.md`, and the README licence badge.
2. Add SPDX identifiers to source files and a licence section to
   `CONTRIBUTING.md`.
3. Apply CC BY-SA 4.0 to curriculum text and keep the attribution inventory in
   `THIRD_PARTY_NOTICES.md`.
4. Re-run the dependency and SBOM audit before publishing the change.

## If permission is declined

Keep the PolyForm licence. A commercial licence path and any dual licensing of
the maintainer's own contributions need counsel.
