# Live Linux Memory Acquisition

## Lab overview

Students connect to an Ubuntu 22.04 guest over SSH, acquire physical memory
with AVML, transfer the image to the Kali RangeBox, and recover a flag from the
environment of a live process.

- **Level:** 3
- **Estimated time:** 120 minutes
- **Target:** `ocr-ubuntu-memory:latest` with an Ubuntu 22.04 qcow2
- **Flag:** in the `MEMFLAG` environment of a live process
- **Virtualization:** KVM preferred; TCG fallback when `/dev/kvm` is absent

## Instructor notes

1. Build the target image with `scripts/provision-ubuntu-memory-vm.sh` on a
   KVM-capable host, or copy a prepared qcow2 into the build context.
2. The guest boots from a read-only qcow2 with `-snapshot`; a restart resets it.
3. The entrypoint starts a process whose environment contains the flag, waits
   until the flag is visible in `/proc/*/environ`, then exposes SSH on port 22.
4. The temporary file used to stage the flag is deleted before the lab opens.
5. Students need the analyst password from the lab credentials panel.

## Evidence handling

The memory image is sensitive. Students should hash it immediately and keep it
inside the lab. Do not copy a real memory image outside an authorised case.

## Sources and licences

- **AVML** is Copyright Microsoft Corporation and is distributed under the MIT
  Licence: https://github.com/microsoft/avml
- **Ubuntu cloud images** are Copyright Canonical Ltd. and are downloaded on
  demand; the image is not redistributed by this repository.
- This lab is original OpenCyberRange content. It is not affiliated with or
  endorsed by Microsoft or Canonical.
