# Live memory forensics

The Forensics track now includes **Level 3: Live Memory Forensics**. The first
exercise, `forensics-3-1-live-linux-memory`, teaches live acquisition rather
than analysis of a pre-captured image.

## What the student does

1. Connects to an Ubuntu 22.04 guest with the analyst account.
2. Runs `avml acquire` to capture physical memory.
3. Hashes the image and transfers it to the Kali RangeBox.
4. Uses Volatility `banners` and `strings` to recover a marker from a live
   process environment.
5. Submits the flag and records the acquisition evidence.

## Why KVM

The target is a real Linux guest, so the acquisition exercises the guest kernel
and `/proc/kcore` rather than a container namespace. The lab prefers KVM and
falls back to QEMU TCG when `/dev/kvm` is absent. KVM is strongly recommended;
TCG is substantially slower.

## Sources and licences

- **Ubuntu 22.04 cloud image** — Copyright Canonical Ltd. The image is
  downloaded on demand by the provisioning process and is not committed to the
  repository.
- **AVML 0.21.0** — Copyright Microsoft Corporation, MIT Licence.
  `https://github.com/microsoft/avml`
- The exercise scenario, workbook, hints, and flag are original OpenCyberRange
  content. They are not affiliated with or endorsed by Microsoft or Canonical.

## Provisioning

See
[`platform/labs/Forensics/_ubuntu-memory/README.md`](../platform/labs/Forensics/_ubuntu-memory/README.md)
and run:

```bash
QCOW=/path/to/ubuntu-memory.qcow2 \
  bash scripts/provision-ubuntu-memory-vm.sh
```

The guest image, Ubuntu cloud image, and AVML binary stay outside Git.
