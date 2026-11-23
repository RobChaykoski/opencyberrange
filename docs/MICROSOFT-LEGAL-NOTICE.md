# Microsoft products and licensing notice

**Microsoft products referenced by this project are not included.**

Users are responsible for ensuring they possess the necessary Microsoft
licenses for all deployed software.

OpenCyberRange does not distribute, resell, sublicense, or provide Microsoft
software, activation keys, or licenses.

## What OpenCyberRange may do

OpenCyberRange **may**:

- deploy Windows;
- automate Windows;
- configure Windows;
- destroy Windows;
- assess Windows.

## What OpenCyberRange must not do

OpenCyberRange **must not**:

- distribute Windows;
- include Windows images;
- include Windows licenses;
- provide activation keys;
- circumvent activation.

## Media and evaluation use

Institutions supply the Windows media. Use Microsoft evaluation media for
non-production labs and testing where possible. Evaluation media is time
limited, non-production, and intended for testing; obtain it directly from
Microsoft.

Do not commit licensed institutional media, evaluation ISOs, VHD/VHDX files,
marketplace images, or sysprep'd images. Keep media in a private artifact store
or a local path outside the repository, and verify its SHA-256 before use.

## License source

When a Windows deployment needs activation, the administrator selects and
supplies the organization-owned source:

```text
License source:
  ( ) Existing activation
  ( ) KMS
  ( ) MAK
  ( ) Azure
```

The repository records only the choice and any non-secret endpoint, such as a
KMS host. It never stores a product key, MAK key, KMS key, or activation secret.
The administrator enters those details in the protected deployment console or
secret manager.

- **Existing activation:** the organization's existing licensed activation is
  used.
- **KMS:** use the organization's KMS infrastructure and DNS/AD configuration.
- **MAK:** the administrator supplies the organization-owned MAK through the
  protected deployment process.
- **Azure:** use the platform image and AVMA; no product key is placed in the
  repository.
- **Evaluation:** use Microsoft evaluation media for the time-limited lab.

## Deployment code

The project may contain Terraform/OpenTofu, Packer templates, Ansible,
PowerShell DSC, PowerShell, lab definitions, documentation, and automation
scripts. Packer templates must accept the media URL/checksum and any license
details as variables supplied outside the repository. Terraform variables for
administrator passwords or product keys must be marked sensitive and have no
committed defaults.

## Enforcement

- [`WINDOWS-ARTIFACT-POLICY.md`](WINDOWS-ARTIFACT-POLICY.md) defines the
  repository rules.
- `scripts/check-windows-artifacts.py` fails CI on media, product keys, or
  activation-key injection.
- `.gitignore` excludes Windows media extensions.
- The installer, README, deployment docs, and public website repeat this notice.

## If Windows material is found

Remove it from the working tree, rotate any exposed key, review the licensing
position, and treat the history as disclosed. A history rewrite and a private
artifact-store migration are required before the next publication.
