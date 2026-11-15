# Persistence, Evidence, and Cleanup

## Lab overview

Collect system evidence, demonstrate a reversible persistence check, remove the artifact, and document the session.

- **Level:** 2
- **Estimated time:** 120 minutes
- **Target:** `ocr-metasploitable2:latest` with `LAB_PROFILE=root`
- **Flag:** stored at the location defined by the target profile
- **KVM:** required. The platform refuses to spawn this lab without `/dev/kvm`.

## Instructor notes

1. Provision the target image with `scripts/provision-metasploitable2.sh` on a
   KVM-capable host.
2. Confirm the lab workspace is isolated from untrusted networks.
3. The target boots from a read-only qcow2 with a temporary overlay. A restart
   resets the guest to its clean state.
4. The flag is injected after the guest SSH service is ready. Allow up to three
   minutes for the first boot before troubleshooting.
5. Students use the Kali RangeBox supplied by the platform. The target is
   reachable by the service name `target` on the lab network.

## Safety

Metasploitable 2 is intentionally vulnerable. Run it only inside the isolated
lab network, never on a shared or Internet-facing network. The target image is
downloaded separately and is not redistributed by this repository.

## Credits

This is original OpenCyberRange practice. It is not affiliated with, endorsed by,
or derived from OffSec course materials. Metasploit Unleashed is a free course
by OffSec; if you use it, please support Hackers For Charity.
