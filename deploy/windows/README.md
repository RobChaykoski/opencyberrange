# Windows deployment inputs

The repository contains deployment code only. Microsoft products, Windows
media, and activation material are not included.

**Microsoft products referenced by this project are not included.**

Users are responsible for ensuring they possess the necessary Microsoft
licenses for all deployed software.

OpenCyberRange does not distribute, resell, sublicense, or provide Microsoft
software, activation keys, or licenses.

## Media

Supply Microsoft evaluation media, or licensed media from the institution's
private artifact store. Do not place the ISO in this repository.

```text
WINDOWS_MEDIA_PATH=/srv/artifacts/windows-eval.iso
WINDOWS_MEDIA_SHA256=<sha256>
```

Verify the SHA-256 before every build. Use evaluation media for non-production
labs and testing where possible.

## License source

Choose one. The administrator supplies the organization-owned details at
deploy time, never in git.

- [ ] Existing activation
- [ ] KMS
- [ ] MAK
- [ ] Azure
- [ ] Evaluation (default for non-production labs)

`WINDOWS_LICENSE_SOURCE` records the choice. `WINDOWS_KMS_HOST` may record a
non-secret KMS host. Do not add a product key, MAK key, or KMS key to this file
or to any script.

## Boundary

OpenCyberRange may deploy, automate, configure, destroy, and assess Windows. It
does not distribute Windows, include Windows images or licenses, provide
activation keys, or circumvent activation.

See [`../../docs/MICROSOFT-LEGAL-NOTICE.md`](../../docs/MICROSOFT-LEGAL-NOTICE.md)
and [`../../docs/WINDOWS-ARTIFACT-POLICY.md`](../../docs/WINDOWS-ARTIFACT-POLICY.md).
