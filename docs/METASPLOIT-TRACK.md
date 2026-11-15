# Metasploit Operations track

Status: **original OpenCyberRange content; live student walkthrough pending.**

This track teaches the Metasploit Framework through eight isolated exercises:
workspace discipline, service discovery, validation, exploitation, Meterpreter,
database access, pivoting, persistence, and cleanup.

## What it is not

This is **not** a copy, adaptation, or derivative of OffSec's *Metasploit
Unleashed* course. The exercises, scenarios, flags, hints, workbooks, and target
setup are original. OffSec's course is free to read, but OffSec's terms reserve
all rights and prohibit copying, changing, or creating derivative works from its
materials. This track does not reproduce its text, screenshots, diagrams, or lab
steps, and it does not use OffSec logos or imply endorsement.

For a free structured course on the Metasploit Framework, see
[Metasploit Unleashed](https://www.offsec.com/metasploit-unleashed/).

## Support Hackers For Charity

OffSec provides Metasploit Unleashed free of charge to raise awareness for
underprivileged children in East Africa. If you use that course, please support
**Hackers For Charity**, a 501(c)(3) nonprofit. A **$9 donation feeds a child for
a month**.

- [Donate via OffSec](https://www.offsec.com/metasploit-unleashed/donate/)
- [Hackers For Charity](https://www.hackersforcharity.org/donate/)

## Environment

- **Attacker:** Kali RangeBox supplied by the platform.
- **Target:** Metasploitable 2, packaged as `ocr-metasploitable2:latest`.
- **Virtualization:** KVM is strongly recommended. On hosts without
  `/dev/kvm`, the target falls back to QEMU TCG software emulation. Boot is
  slower and the practical concurrency is much lower, but the labs can still
  run.
- **Network:** the target uses QEMU user networking with egress restricted. The
  guest cannot reach the Internet. Service ports are exposed to the lab network
  through a userspace proxy, including FTP control (21), SSH (22), HTTP (80),
  SMB (139/445), MySQL (3306), PostgreSQL (5432), the vsftpd backdoor shell
  (6200), and Tomcat (8180).
- **Reset:** the qcow2 is mounted read-only and QEMU uses `-snapshot`. A restart
  returns the guest to its clean state.

## Host readiness

The development and production hosts both expose `/dev/kvm` and run the target
with hardware acceleration. Production was initially presented with a
`QEMU Virtual CPU version 2.5+` model that hid `vmx`; setting the VM CPU type to
`host` and cold-starting the VM exposed the flag and `/dev/kvm`.

To check a host:

```bash
grep -m1 -oE 'vmx|svm' /proc/cpuinfo
ls -l /dev/kvm
```

If the flags are missing, set the VM CPU type to `host` / `host-passthrough`
(or a model that includes `vmx`/`svm`) and **stop and start** the VM. A guest
reboot does not change the CPU model. After `/dev/kvm` appears, restart the
backend so its one-time KVM probe re-runs; the platform then injects
`/dev/kvm` into the target container.

The target still falls back to TCG if a host genuinely has no `/dev/kvm`, but
that path is now a compatibility fallback rather than the production default.

## Provisioning

The VM image is not committed to the repository. On each KVM-capable host:

```bash
bash scripts/provision-metasploitable2.sh
```

The script downloads the Metasploitable 2 archive, verifies its SHA-256,
converts the VMDK to qcow2, and builds `ocr-metasploitable2:latest`. Review
Rapid7's distribution terms before redistributing the image or shipping it
inside a published container.

## Lab map

| Exercise | Focus | Target profile |
|---|---|---|
| 1.1 Workspace and Module Discipline | Workspaces, database, module metadata | `web` |
| 1.2 Auxiliary Service Discovery | Port, SSH, FTP, HTTP, and MySQL scanners | `web` |
| 1.3 Validate Before You Exploit | vsftpd validation and controlled exploitation | `root` |
| 1.4 Samba Exploitation and First Session | usermap_script, reverse payload, session lifecycle | `root` |
| 2.1 Meterpreter Session | Java RMI, Meterpreter, system evidence | `root` |
| 2.2 Database Credentials and Data Access | MySQL authentication and read-only SQL | `mysql` |
| 2.3 Pivot to a Local-Only Service | Meterpreter `portfwd` to a loopback service | `pivot` |
| 2.4 Persistence, Evidence, and Cleanup | Scheduled-task marker, evidence, cleanup | `root` |

## Flag placement

The target image injects the flag after the guest SSH service is ready. The
profile decides where it lands:

| Profile | Flag location |
|---|---|
| `web` | `/var/www/flag.txt`, served at `http://target/flag.txt` |
| `ssh` | `/home/msfadmin/flag.txt` |
| `mysql` | `msf_lab.flags` table in MySQL |
| `pivot` | `/root/pivot/flag.txt`, served only on the guest's `127.0.0.1:9000` |
| `root` | `/root/flag.txt` |

## Safety

Metasploitable 2 is intentionally vulnerable. Run it only inside the isolated
lab network. Never expose the target to an untrusted network, and never reuse
the exercise commands against systems you do not own or have explicit permission
to test.

The labs are marked `x-ocr-kvm-preferred: true` in their compose files. KVM is
used automatically when `/dev/kvm` is available. Otherwise the target uses TCG,
which keeps the labs usable on production but is not suitable for a large class
at once.
