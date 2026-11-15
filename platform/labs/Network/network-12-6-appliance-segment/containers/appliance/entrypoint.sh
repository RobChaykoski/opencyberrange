#!/bin/sh
# OpenWrt appliance startup for the segmentation lab.
#
# The rootfs image is a container-sized OpenWrt userland, not a VM. Start the
# pieces the exercise needs and leave procd out of the picture.
set -e

ip link set lo up

# Demo credential hash for the learner login. The cleartext password is in
# lab.yaml; this file only carries the SHA-512 crypt hash.
cp /lab/shadow /etc/shadow
chmod 600 /etc/shadow

mkdir -p /etc/dropbear
dropbear -R -F -E -p 22 &

# Default-deny forwarding between the training and control segments. The
# appliance still terminates SSH and can reach both segments itself.
nft -f - <<'NFT'
table inet labfw {
  chain forward {
    type filter hook forward priority 0; policy drop;
    ct state established,related accept
  }
}
NFT

# Keep PID 1 alive; dropbear is a background child.
exec sleep 100000
