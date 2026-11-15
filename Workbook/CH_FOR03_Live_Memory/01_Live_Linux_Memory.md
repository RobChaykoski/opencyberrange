# Exercise L3.1: Live Linux Memory Acquisition

## Before You Begin

- Confirm the lab is running and reachable from your Kali RangeBox.
- The analyst password is in the lab credentials panel.
- Work only inside the isolated lab network. The memory image is sensitive.
- Keep a notebook with every command, output, and hash.

## Scenario

A Linux server is still running, but the incident-response team needs volatile
evidence before anyone reboots it. The only lead is a process started by an
unknown operator. The flag is not on disk; it exists only in the live process
environment.

You will acquire physical memory, move the image to your RangeBox, and recover
the evidence.

## Your Objectives

- Connect to `memory.lab` with the analyst account.
- Acquire memory with AVML and record its size and SHA-256 hash.
- Transfer the image to the Kali RangeBox.
- Identify the kernel and search the image for the `MEMFLAG` marker.
- Explain why this evidence would be lost on shutdown.

## Background: volatile evidence

Memory contains process environments, command lines, network state, cached
files, credentials, and encryption keys that may never appear in a disk file.
Shutting down the host destroys that state. Acquisition must happen while the
system is running, and the resulting image must be hashed and handled as
evidence.

AVML is a userland acquisition tool. It reads physical memory through the
kernel and writes a portable image without loading a kernel module.

## Guided Steps

### 1. Connect to the target

From the RangeBox terminal:

```bash
ssh analyst@memory.lab
```

Use the password from the credentials panel. Confirm the tool is present:

```bash
avml --version
```

### 2. Acquire memory

```bash
sudo avml acquire /tmp/mem.lime
ls -lh /tmp/mem.lime
sha256sum /tmp/mem.lime
```

Record the size and hash before you move the file. The acquisition may take
several seconds and produces an image roughly the size of guest RAM.

### 3. Transfer the image

From the RangeBox:

```bash
scp analyst@memory.lab:/tmp/mem.lime .
sha256sum mem.lime
```

The hash must match the value recorded on the target. A mismatch means the
transfer is not trustworthy evidence.

### 4. Identify the image

```bash
vol -f mem.lime banners
```

`banners` is a quick way to confirm the kernel and image format. If your
Volatility installation has the matching Linux symbol table, you can also try:

```bash
vol -f mem.lime linux.pslist
```

### 5. Recover the marker

The live process carries a `MEMFLAG` environment variable. Search the image for
that marker:

```bash
strings -a mem.lime | grep -a 'MEMFLAG='
```

The matching line contains the flag. The marker is not stored in a normal file,
so a disk search would miss it. Record the line and explain why it appears in
memory.

### 6. Clean up

Remove the local copy when you have recorded the evidence:

```bash
rm -f mem.lime
```

The lab resets when the target is restarted.

## Evidence Record

| Item | Value |
|---|---|
| Acquisition command | |
| Image size | |
| SHA-256 on target | |
| SHA-256 after transfer | |
| Kernel banner | |
| Marker line | |

## Flag

Submit the flag exactly as it appears in the `MEMFLAG` line. A flag without a
reproducible acquisition and hash is not useful evidence.

## Defensive Takeaways

- Collect volatile memory before shutdown when it is in scope.
- Hash the image at acquisition and again after transfer.
- Encrypt evidence at rest and restrict access.
- Minimise secrets in process environments and command lines.
- Monitor unexpected raw memory access and acquisition tooling.

## Sources and Credits

- **AVML** — Copyright Microsoft Corporation, MIT Licence:
  https://github.com/microsoft/avml
- **Ubuntu cloud image** — Copyright Canonical Ltd.; downloaded on demand and
  not redistributed by this repository.
- This exercise is original OpenCyberRange practice and is not affiliated with
  or endorsed by Microsoft or Canonical.
