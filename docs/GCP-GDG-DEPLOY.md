# GDG-Deploy: Google Cloud deployment

`scripts/GDG-Deploy.sh` is a small wrapper around the normal single-host
installer. It creates a billable Ubuntu 24.04 Compute Engine VM, opens the
required ports, clones OpenCyberRange, and runs the existing setup script.

This is a demo/GDG convenience path, not a new supported production topology.

## Prerequisites

- Google Cloud CLI installed and authenticated:
  ```bash
  gcloud auth login
  gcloud config set project YOUR_PROJECT
  ```
- Billing enabled and the Compute Engine API available.
- Permission to create Compute Engine instances, firewall rules, and disks.

## Deploy

```bash
# Show the plan without creating anything
bash scripts/GDG-Deploy.sh --dry-run

# Create or reuse the VM and install OpenCyberRange
bash scripts/GDG-Deploy.sh
```

The script prints the VM's public IP and sets up a self-signed HTTPS
certificate. The first boot can take several minutes.

## Common overrides

| Variable | Default | Purpose |
|---|---|---|
| `GCP_PROJECT` | active `gcloud` project | Target project |
| `GCP_ZONE` | `us-central1-a` | Compute zone |
| `GCP_INSTANCE` | `ocr-gdg` | VM name |
| `GCP_MACHINE_TYPE` | `e2-standard-4` | VM size |
| `GCP_DISK_SIZE` | `100GB` | Boot disk |
| `GCP_REPO_REF` | `main` | OpenCyberRange branch/tag |
| `GCP_SSH_SOURCE` | `0.0.0.0/0` | CIDR allowed to SSH |
| `GCP_NESTED_VIRT` | `0` | `1` enables nested virtualization for Windows labs |
| `GCP_STATIC_IP` | empty | Reserved static address name/IP |

Example:

```bash
GCP_PROJECT=my-project \
GCP_ZONE=northamerica-northeast1-a \
GCP_SSH_SOURCE=203.0.113.0/24 \
GCP_NESTED_VIRT=1 \
bash scripts/GDG-Deploy.sh
```

## Security notes

- The default opens SSH to the internet. Set `GCP_SSH_SOURCE` to a trusted CIDR
  for anything longer than a short demo.
- The default HTTPS certificate is self-signed. Use a real domain and
  Cloudflare/OPNsense or a managed certificate for a public deployment.
- The generated `.env`, WireGuard keys, and database password stay on the VM.
  Do not commit them.
- The VM is billable until deleted.

## Remove

```bash
bash scripts/GDG-Deploy.sh --delete
```

This deletes the VM and the three firewall rules created by the script. It does
not delete a separately reserved static IP or a manually attached disk.

## Limitations

- Single-host Docker Compose only.
- No automatic DNS, managed TLS, or Cloud Armor/WAF.
- Nested virtualization must be enabled explicitly and is machine-type
  dependent.
- The script has not replaced the certified Ubuntu 24.04 host validation or the
  real-host KVM, WireGuard, firewall-persistence, and restore gates.
