# VulnHub VM sourcing and licence alignment

Status: **licence review completed 2026-11-15. No VulnHub images are committed
to this repository.**

This note records how OpenCyberRange can use VulnHub images without
misrepresenting their licence or shipping third-party virtual machines in the
repository. It is an engineering review, not legal advice; confirm disputed
terms with the institution's counsel.

## What VulnHub says

- The VulnHub site and its own content are copyright VulnHub.
- VulnHub's contributor terms state that a submitter grants everybody who
  accesses a submitted VM a **permanent, global and free right to use, copy,
  amend and share the VM without restriction**. Submitters must have permission
  for any third-party material they include.
- VulnHub does not verify the images. Its own FAQ warns that the VMs are
  untrusted, may attack the host or network, and must be run in an isolated
  lab.
- VulnHub was acquired by OffSec; that does not make every image open source.

## Rules for this platform

1. **Download on demand.** Never commit an OVA, VMDK, VDI, qcow2 or archive to
   the repository. Provision it on the host and add the image directory to
   `.gitignore`.
2. **Verify the published checksum** before conversion or first boot.
3. **Credit the VM.** Show the VM name, author, VulnHub entry link, and the
   original README/licence text in the lab README and workbook.
4. **Do not use VulnHub or OffSec logos** or imply endorsement.
5. **Isolate the VM.** No Internet egress, no production network, no shared
   bridge. Use QEMU user networking with restricted egress and an explicit
   port allow-list.
6. **Audit third-party software.** A VM may bundle Windows, SCADA applications,
   proprietary tools, or an end-of-life operating system. Record the licence
   and support status before using it in a graded lab.
7. **Treat VulnHub images as legacy.** Do not make an EOL guest the core of a
   new track without a time-boxed support and security review.

## Candidate review

| VM | Fit | Size | Notes |
|---|---|---|---|
| **Bizarre Adventure: Joestar** | OT/SCADA CTF | 924 MB | Ubuntu 17.04 (EOL), VirtualBox VDI. Booted under QEMU/KVM, but the original network configuration did not come up automatically; it needs disk-level customisation before it can be a per-lab target. No README/licence file in the archive. |
| **NETinVM** | Network-in-a-VM | 4.7 GB current KVM image | Debian 13 base with nested KVM guests, firewall, DMZ and internal/external networks. Strong teaching fit, but heavy and not designed for per-student spawn. Upstream is an academic project; confirm terms with the authors before redistribution. |
| **HA: Forensics** | Forensic analysis CTF | 845 MB | Linux, four forensic flags. Useful as a forensic-analysis supplement, but it is not a live-memory acquisition lab. |
| **Metasploit 2** | Already used | 865 MB | Already provisioned for the Metasploit track; original Rapid7 image, not bundled. |

## Recommendation

- **Live Linux memory forensics:** no suitable VulnHub live-acquisition VM was
  found. Use a small Ubuntu 22.04 cloud image with AVML, booted under KVM, with
  a per-lab flag injected into a process environment. This is the lab already
  being prepared; it is not a VulnHub derivative.
- **Network appliances:** prefer a maintained OpenWrt/pfSense/VyOS image or the
  existing Docker topology for core teaching. Use NETinVM only as an optional
  legacy "network in a box" lab if its size, age and academic licence are
  acceptable.
- **OT/ICS:** prefer a maintained OpenPLC container or appliance. Use Joestar
  only as an optional legacy CTF, after documenting its EOL base and auditing
  the bundled SCADA software.
- **Windows:** deferred as agreed; Windows images add licensing and patching
  obligations.

## Implementation pattern when a VulnHub VM is used

- Per-lab QEMU target, KVM when available and TCG fallback otherwise.
- Read-only qcow2 with `-snapshot`; a restart returns to the clean state.
- Restricted user networking; only the required service ports are proxied to
  the lab network.
- Flag injection only after the guest is ready; do not bake flags into the
  shared image.
- Provisioning script downloads, verifies, extracts and converts on the host.
  The image and archive stay outside Git.
