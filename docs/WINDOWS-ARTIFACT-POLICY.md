# Windows artifact policy

Status: **enforced by `scripts/check-windows-artifacts.py` and the Quality
workflow.**

The repository contains deployment code, lab definitions, documentation, and
automation scripts. It does not contain Windows operating-system media, product
keys, or activation material.

## Never commit

- Windows ISOs, evaluation ISOs, or downloaded media;
- VHD, VHDX, VMDK, QCOW2, OVA, OVF, WIM, ESD, or VDI files;
- Azure Marketplace images or exported marketplace disks;
- licensed institutional images or sysprep'd images;
- product keys, MAK keys, KMS keys, or activation secrets;
- `slmgr /ipk`, `ospp /inpkey`, `changepk /ProductKey`, or DISM product-key
  injection in source, scripts, unattend files, or configuration;
- non-empty `product_key` or `windows_license_key` assignments.

## Allowed

- Terraform and OpenTofu modules;
- Packer templates that take the media URL, media checksum, and license details
  as variables with no committed defaults;
- Ansible, PowerShell DSC, and PowerShell automation that reads secrets from a
  secret store at runtime;
- lab definitions, Compose files, documentation, and verification scripts;
- references to a marketplace image in deployment code, without vendoring the
  image.

## Institution-supplied media

The institution supplies Microsoft evaluation media or licensed media from its
own artifact store. The repository may document the expected path and checksum,
but not the media itself.

```text
WINDOWS_MEDIA_PATH=/srv/artifacts/windows-eval.iso
WINDOWS_MEDIA_SHA256=<sha256>
WINDOWS_LICENSE_SOURCE=evaluation
```

`WINDOWS_LICENSE_SOURCE` is one of `existing`, `kms`, `mak`, `azure`, or
`evaluation`. KMS may also record a non-secret host. MAK and product keys are
entered in the protected deployment process and never written to this file.

## Packer pattern

```hcl
variable "windows_iso_url" {
  type        = string
  description = "Institution-supplied Microsoft evaluation media."
}

variable "windows_iso_checksum" {
  type        = string
  description = "SHA-256 of the institution-supplied media."
}

variable "windows_license_source" {
  type    = string
  default = "evaluation"
  validation {
    condition     = contains(["existing", "kms", "mak", "azure", "evaluation"], var.windows_license_source)
    error_message = "Choose a supported license source."
  }
}
```

Do not put a real ISO URL, product key, or MAK in the template. Pass a private
var-file outside the repository.

## Terraform pattern

```hcl
variable "windows_admin_password" {
  type      = string
  sensitive = true
}

variable "windows_product_key" {
  type      = string
  sensitive = true
  default   = null
}
```

No secret default. The operator supplies the value from a secret manager or a
protected `-var-file`. An Azure marketplace image reference is deployment code;
the image itself is not vendored.

## Enforcement

```bash
python scripts/check-windows-artifacts.py
python scripts/check-windows-artifacts.py --json
```

The audit checks tracked and untracked files, extensions, magic bytes, product
key shapes, and activation-key injection. The Quality workflow runs it on every
push and pull request.

`.gitignore` excludes the media extensions. `.gitattributes` marks them binary
if they are ever force-added, but the audit is the gate.

## Review checklist

- [ ] No ISO, VHD/VHDX, VMDK, QCOW2, OVA/OVF, WIM/ESD, or VDI file.
- [ ] No product key, MAK, KMS key, or activation secret.
- [ ] No `slmgr /ipk` or equivalent activation-key injection.
- [ ] Packer media and license values are variables with no defaults.
- [ ] Terraform secrets are sensitive and have no committed defaults.
- [ ] The institution supplies evaluation or licensed media from a private store.
- [ ] `python scripts/check-windows-artifacts.py` returns zero findings.

## If a value is already published

Remove it, rotate the key, review the Microsoft licensing position, and treat
the history as disclosed. Rewrite history only after explicit approval, and
move the media to a private artifact store.
