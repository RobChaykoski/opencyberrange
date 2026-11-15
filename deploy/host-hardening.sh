#!/usr/bin/env bash
# Apply the low-risk host hardening items that Lynis reports as suggestions.
#
# Covered:
#   AUTH-9328  stricter default umask (027) for interactive logins
#   KRNL-5820  disable core dumps for local service accounts
#
# Deliberately not covered (see docs/SECURITY-SCANNING.md):
#   GRUB passwords, PAM password-quality modules, separate /home, /tmp, /var
#   partitions, USB storage disablement.
#
# Usage: sudo bash deploy/host-hardening.sh [--dry-run]
set -euo pipefail

DRY_RUN=0
case "${1:-}" in
    --dry-run) DRY_RUN=1 ;;
    "") ;;
    *) echo "usage: sudo bash $0 [--dry-run]" >&2; exit 2 ;;
esac

if [ "$(id -u)" -ne 0 ] && [ "$DRY_RUN" -eq 0 ]; then
    echo "error: run as root (or use --dry-run to preview)" >&2
    exit 1
fi

STAMP=$(date -u +%Y%m%dT%H%M%SZ)

backup() {
    local path=$1
    if [ -f "$path" ] && [ ! -f "$path.ocr-bak-$STAMP" ]; then
        cp -a "$path" "$path.ocr-bak-$STAMP"
        echo "backup: $path.ocr-bak-$STAMP"
    fi
}

apply_umask() {
    local path=/etc/login.defs
    if grep -Eq '^[[:space:]]*UMASK[[:space:]]+027[[:space:]]*$' "$path"; then
        echo "ok: UMASK is already 027 in $path"
        return 0
    fi
    echo "change: set UMASK 027 in $path"
    if [ "$DRY_RUN" -eq 1 ]; then
        return 0
    fi
    backup "$path"
    if grep -Eq '^[[:space:]]*UMASK[[:space:]]+' "$path"; then
        sed -i -E 's/^[[:space:]]*UMASK[[:space:]]+.*/UMASK\t\t027/' "$path"
    else
        printf '\n# OpenCyberRange: restrict default permissions for new files\nUMASK\t\t027\n' >> "$path"
    fi
    grep -E '^UMASK' "$path"
}

apply_core_dumps() {
    local path=/etc/security/limits.conf
    local missing=()
    local entry
    for entry in '* hard core 0' 'root hard core 0'; do
        if grep -Eq "^[[:space:]]*${entry//\*/\\*}[[:space:]]*$" "$path"; then
            echo "ok: '$entry' is already present in $path"
        else
            missing+=("$entry")
        fi
    done
    if [ "${#missing[@]}" -eq 0 ]; then
        return 0
    fi
    echo "change: add ${#missing[@]} core-dump limit(s) to $path"
    if [ "$DRY_RUN" -eq 1 ]; then
        return 0
    fi
    backup "$path"
    printf '%s\n' "${missing[@]}" >> "$path"
    tail -n 4 "$path"
}

echo "== OpenCyberRange host hardening =="
if [ "$DRY_RUN" -eq 1 ]; then
    echo "mode: dry run (no files written)"
fi
apply_umask
apply_core_dumps
if [ "$DRY_RUN" -eq 0 ]; then
    echo "done. Re-run Lynis to confirm AUTH-9328 and KRNL-5820 clear."
fi
