#!/usr/bin/env bash
# ==============================================================================
# GDG-Deploy — deploy OpenCyberRange to Google Compute Engine
# ==============================================================================
#
# This is a small, explicit wrapper around the existing installer. It creates a
# billable Ubuntu VM, opens the required ports, clones the repository, and runs
# the normal server setup non-interactively.
#
# Usage:
#   bash scripts/GDG-Deploy.sh --dry-run     # print the plan only
#   bash scripts/GDG-Deploy.sh               # create/update the VM and install
#   bash scripts/GDG-Deploy.sh --skip-install
#   bash scripts/GDG-Deploy.sh --delete      # remove the VM and firewall rules
#
# Required:
#   gcloud auth login
#   gcloud config set project YOUR_PROJECT
#   Compute Engine API enabled and billing active
#
# Common overrides:
#   GCP_PROJECT, GCP_ZONE, GCP_INSTANCE, GCP_MACHINE_TYPE, GCP_DISK_SIZE,
#   GCP_IMAGE_FAMILY, GCP_REPO_URL, GCP_REPO_REF, GCP_SSH_SOURCE,
#   GCP_NESTED_VIRT=1, GCP_STATIC_IP=NAME
#
# ==============================================================================

set -euo pipefail

PROJECT="${GCP_PROJECT:-$(gcloud config get-value project 2>/dev/null || true)}"
ZONE="${GCP_ZONE:-us-central1-a}"
INSTANCE="${GCP_INSTANCE:-ocr-gdg}"
MACHINE_TYPE="${GCP_MACHINE_TYPE:-e2-standard-4}"
IMAGE_FAMILY="${GCP_IMAGE_FAMILY:-ubuntu-2404-lts-amd64}"
IMAGE_PROJECT="${GCP_IMAGE_PROJECT:-ubuntu-os-cloud}"
DISK_SIZE="${GCP_DISK_SIZE:-100GB}"
DISK_TYPE="${GCP_DISK_TYPE:-pd-balanced}"
NETWORK="${GCP_NETWORK:-default}"
TAG="${GCP_TAG:-ocr-gdg}"
SSH_SOURCE="${GCP_SSH_SOURCE:-0.0.0.0/0}"
REPO_URL="${GCP_REPO_URL:-https://github.com/RobChaykoski/opencyberrange.git}"
REPO_REF="${GCP_REPO_REF:-main}"
STATIC_IP="${GCP_STATIC_IP:-}"
NESTED="${GCP_NESTED_VIRT:-0}"

FW_WEB="${GCP_FW_WEB:-ocr-gdg-web}"
FW_SSH="${GCP_FW_SSH:-ocr-gdg-ssh}"
FW_VPN="${GCP_FW_VPN:-ocr-gdg-vpn}"

REMOTE_SRC="/opt/opencyberrange-src"
REMOTE_PLATFORM="/opt/opencyberrange"

DRY_RUN=0
SKIP_INSTALL=0
DELETE=0

usage() {
    sed -n '2,26p' "$0" | sed 's/^# \{0,1\}//'
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)       DRY_RUN=1; shift ;;
        --skip-install)  SKIP_INSTALL=1; shift ;;
        --delete)        DELETE=1; shift ;;
        --help|-h)       usage; exit 0 ;;
        *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
    esac
done

say() {
    printf '\n== %s ==\n' "$*"
}

run() {
    if [[ "$DRY_RUN" == "1" ]]; then
        printf '[dry-run]'
        printf ' %q' "$@"
        printf '\n'
    else
        "$@"
    fi
}

if ! command -v gcloud >/dev/null 2>&1; then
    echo "ERROR: gcloud is not installed. Install the Google Cloud CLI first." >&2
    exit 1
fi

if [[ -z "$PROJECT" ]]; then
    echo "ERROR: no GCP project selected." >&2
    echo "Run: gcloud config set project YOUR_PROJECT" >&2
    echo "Or:  GCP_PROJECT=YOUR_PROJECT bash scripts/GDG-Deploy.sh" >&2
    exit 1
fi

if ! gcloud auth list --filter=status:ACTIVE --format='value(account)' | grep -q .; then
    echo "ERROR: no active gcloud account. Run: gcloud auth login" >&2
    exit 1
fi

say "GCP GDG deployment plan"
cat <<EOF
Project:        $PROJECT
Zone:           $ZONE
Instance:       $INSTANCE
Machine type:   $MACHINE_TYPE
Boot disk:      $DISK_SIZE ($DISK_TYPE)
Image:          $IMAGE_PROJECT/$IMAGE_FAMILY
Network/tag:    $NETWORK / $TAG
SSH source:     $SSH_SOURCE
Repository:     $REPO_URL ($REPO_REF)
Install path:   $REMOTE_PLATFORM
Nested virt:    $NESTED
Static IP:      ${STATIC_IP:-ephemeral}
EOF

if [[ "$SSH_SOURCE" == "0.0.0.0/0" ]]; then
    echo
    echo "WARNING: SSH will be open to the internet. Set GCP_SSH_SOURCE to a"
    echo "         trusted CIDR before using this outside a short demo."
fi

if [[ "$DELETE" == "1" ]]; then
    say "Deleting $INSTANCE and GDG firewall rules"
    run gcloud compute instances delete "$INSTANCE" \
        --project="$PROJECT" --zone="$ZONE" --quiet || true
    run gcloud compute firewall-rules delete "$FW_WEB" "$FW_SSH" "$FW_VPN" \
        --project="$PROJECT" --quiet || true
    echo "Deleted. Any external IP or disk not named by this script may remain."
    exit 0
fi

ensure_firewall() {
    local name="$1"; shift
    if gcloud compute firewall-rules describe "$name" --project="$PROJECT" >/dev/null 2>&1; then
        echo "Firewall rule exists: $name"
    else
        run gcloud compute firewall-rules create "$name" \
            --project="$PROJECT" \
            --network="$NETWORK" \
            --direction=INGRESS \
            --action=ALLOW \
            --target-tags="$TAG" \
            "$@"
    fi
}

say "Ensuring firewall rules"
ensure_firewall "$FW_WEB" \
    --allow=tcp:80,tcp:443 \
    --source-ranges=0.0.0.0/0 \
    --description="OpenCyberRange GDG web traffic"
ensure_firewall "$FW_SSH" \
    --allow=tcp:22 \
    --source-ranges="$SSH_SOURCE" \
    --description="OpenCyberRange GDG SSH management"
ensure_firewall "$FW_VPN" \
    --allow=udp:51820 \
    --source-ranges=0.0.0.0/0 \
    --description="OpenCyberRange GDG WireGuard VPN"

if gcloud compute instances describe "$INSTANCE" \
    --project="$PROJECT" --zone="$ZONE" >/dev/null 2>&1; then
    say "Instance already exists: $INSTANCE"
else
    say "Creating instance: $INSTANCE"
    CREATE_ARGS=(
        compute instances create "$INSTANCE"
        --project="$PROJECT"
        --zone="$ZONE"
        --machine-type="$MACHINE_TYPE"
        --image-family="$IMAGE_FAMILY"
        --image-project="$IMAGE_PROJECT"
        --boot-disk-size="$DISK_SIZE"
        --boot-disk-type="$DISK_TYPE"
        --network="$NETWORK"
        --tags="$TAG"
        --metadata=enable-oslogin=TRUE
        --scopes=cloud-platform
    )
    if [[ "$NESTED" == "1" ]]; then
        CREATE_ARGS+=(--enable-nested-virtualization)
    fi
    if [[ -n "$STATIC_IP" ]]; then
        CREATE_ARGS+=(--address="$STATIC_IP")
    fi
    run gcloud "${CREATE_ARGS[@]}"
fi

if [[ "$DRY_RUN" == "1" ]]; then
    say "Dry run complete"
    echo "No VM was created and no software was installed."
    exit 0
fi

say "Waiting for SSH"
SSH_READY=0
for _ in $(seq 1 60); do
    if gcloud compute ssh "$INSTANCE" \
        --project="$PROJECT" --zone="$ZONE" --quiet \
        --command="true" >/dev/null 2>&1; then
        SSH_READY=1
        break
    fi
    sleep 5
done
if [[ "$SSH_READY" != "1" ]]; then
    echo "ERROR: SSH did not become ready. Check the VM serial console." >&2
    exit 1
fi

if [[ "$SKIP_INSTALL" == "1" ]]; then
    say "Skipping platform install (--skip-install)"
else
    say "Installing OpenCyberRange on $INSTANCE"
    REMOTE_CMD="sudo apt-get update -y && sudo apt-get install -y git ca-certificates curl && sudo rm -rf '$REMOTE_SRC' && sudo git clone --branch '$REPO_REF' '$REPO_URL' '$REMOTE_SRC' && cd '$REMOTE_SRC' && yes '' | sudo env OCR_PLATFORM_DIR='$REMOTE_PLATFORM' DEPLOYMENT_MODE=internet GENERATE_SELF_SIGNED=true bash scripts/setup-range-server.sh --install"
    gcloud compute ssh "$INSTANCE" \
        --project="$PROJECT" --zone="$ZONE" --quiet \
        --command="$REMOTE_CMD"
fi

IP="$(gcloud compute instances describe "$INSTANCE" \
    --project="$PROJECT" --zone="$ZONE" \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)' 2>/dev/null || true)"

say "Deployment complete"
if [[ -n "$IP" ]]; then
    echo "HTTP:  http://$IP"
    echo "HTTPS: https://$IP  (self-signed certificate)"
else
    echo "No external IP. Use IAP or assign a static IP."
fi
echo "SSH:   gcloud compute ssh $INSTANCE --project=$PROJECT --zone=$ZONE"
echo
echo "This VM is billable. Remove it with:"
echo "  bash scripts/GDG-Deploy.sh --delete"
