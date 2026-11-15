# Metasploit Operations

This track is original OpenCyberRange practice for using the Metasploit
Framework in an authorised, isolated lab. It covers workspace discipline,
module selection, service validation, exploitation, Meterpreter, database
access, pivoting, and cleanup.

## Environment

- **Attacker:** Kali RangeBox supplied by the platform.
- **Target:** a deliberately vulnerable Metasploitable 2 guest, packaged as
  `ocr-metasploitable2:latest` and started with a read-only disk overlay.
- **KVM:** required. The target runs under QEMU/KVM and is refused on hosts
  without `/dev/kvm`.
- **Network:** the target has no outbound Internet access. It is reachable only
  from the lab network.

## Safety and scope

Use these exercises only on the lab target. Do not reuse the commands against
systems you do not own or have explicit permission to test. The target is
intentionally vulnerable; never expose it to an untrusted network.

## Track map

| Exercise | Focus |
|---|---|
| 1.1 | Workspace and module discipline |
| 1.2 | Auxiliary service discovery |
| 1.3 | Validate before exploit |
| 1.4 | Samba exploitation and first session |
| 2.1 | Meterpreter session |
| 2.2 | Database credentials and data access |
| 2.3 | Pivot to a local-only service |
| 2.4 | Persistence, evidence, and cleanup |

## Further learning and credits

This exercise is original OpenCyberRange practice. It is **not affiliated with,
endorsed by, or derived from OffSec course materials**.

For a free structured course on the Metasploit Framework, see
[Metasploit Unleashed](https://www.offsec.com/metasploit-unleashed/) by OffSec.
If you use that course, please support **Hackers For Charity**, a 501(c)(3)
nonprofit. A **$9 donation feeds a child for a month**.

- [Donate via OffSec](https://www.offsec.com/metasploit-unleashed/donate/)
- [Hackers For Charity](https://www.hackersforcharity.org/donate/)
