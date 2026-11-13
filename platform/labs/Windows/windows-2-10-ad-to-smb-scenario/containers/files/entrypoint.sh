#!/bin/bash
set -euo pipefail
if ! id svc-backup >/dev/null 2>&1; then
  useradd -M -s /usr/sbin/nologin svc-backup
  echo 'svc-backup:S3rv1ce!Pass' | chpasswd
  (echo 'S3rv1ce!Pass'; echo 'S3rv1ce!Pass') | smbpasswd -s -a svc-backup
fi
mkdir -p /srv/evidence
printf 'OCR{ad_t0_smb_p4th}\n' > /srv/evidence/flag.txt
chown -R svc-backup:svc-backup /srv/evidence
cat > /etc/samba/smb.conf <<'EOF'
[global]
workgroup = LAB
server string = LAB Evidence
security = user
map to guest = never
server role = standalone server
[evidence]
path = /srv/evidence
read only = yes
valid users = svc-backup
EOF
exec smbd -F --no-process-group
