#!/bin/sh
set -eu

# The A records must point at this container's address, which the platform
# assigns per student. Resolve it at startup instead of hard-coding an IP.
SELF_IP="$(hostname -i | awk '{print $1}')"
if [ -z "$SELF_IP" ]; then
  echo "could not determine container IP" >&2
  exit 1
fi

sed "s/__SELF_IP__/$SELF_IP/g" /etc/dnsmasq.conf > /tmp/dnsmasq.conf
exec dnsmasq -k --conf-file=/tmp/dnsmasq.conf
