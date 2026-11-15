# Ubuntu live-memory target

This directory builds `ocr-ubuntu-memory:latest`, the per-lab QEMU target for
the live Linux memory exercise.

## Sources and licences

- **Ubuntu 22.04 cloud image** — Copyright Canonical Ltd. Download it from
  `https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img`.
  The image is downloaded on demand and is **not** committed to this repository.
- **AVML 0.21.0** — Copyright Microsoft Corporation, MIT Licence.
  `https://github.com/microsoft/avml/releases/download/v0.21.0/avml`
  SHA-256: `e75597dcdcaaa8475fdc61643effb050f72aaa9cff677c7271386a9781bf4460`
- The lab content itself is original OpenCyberRange material.

## Prepare the base image

1. Download the Ubuntu cloud image and create a writable overlay:

   ```bash
   qemu-img create -f qcow2 -F qcow2 \
     -b jammy-server-cloudimg-amd64.img prepared.qcow2 10G
   ```

2. Create a NoCloud seed ISO labelled `CIDATA` with `user-data` and
   `meta-data`. The analyst account must have password login and passwordless
   sudo. The seed used on development sets:

   - user: `analyst`
   - password: `Analyst#2026`
   - hostname: `memory-lab`
   - `ssh_pwauth: true`

   A small `pycdlib` script or any ISO builder that preserves the lowercase
   files through Rock Ridge/Joliet works.

3. Boot the overlay with KVM and the seed ISO, attach user networking with
   `hostfwd=tcp:127.0.0.1:2222-:22`, and wait for SSH.

4. Install AVML:

   ```bash
   scp -P 2222 avml analyst@127.0.0.1:/tmp/avml
   ssh -p 2222 analyst@127.0.0.1 \
     'sudo install -m 755 /tmp/avml /usr/local/bin/avml; avml --version'
   ```

5. Remove test dumps, shell history, and logs, then shut down cleanly:

   ```bash
   sudo rm -rf /tmp/*
   sudo truncate -s 0 /var/log/auth.log /var/log/syslog
   rm -f ~/.bash_history
   sudo poweroff
   ```

6. Flatten and compress the overlay:

   ```bash
   qemu-img convert -c -O qcow2 prepared.qcow2 ubuntu-memory.qcow2
   ```

7. Build the Docker image:

   ```bash
   QCOW=/path/to/ubuntu-memory.qcow2 \
     bash scripts/provision-ubuntu-memory-vm.sh
   ```

## Runtime behaviour

- The qcow2 is read-only and QEMU runs with `-snapshot`.
- KVM is used when `/dev/kvm` is available; TCG is the fallback.
- The entrypoint starts a process whose environment contains `MEMFLAG` and
  waits until that flag is visible in `/proc/*/environ`.
- SSH is proxied to the lab network on port 22.
- The lab network has no guest Internet egress.

Do not commit the qcow2, the Ubuntu cloud image, or the AVML binary.
