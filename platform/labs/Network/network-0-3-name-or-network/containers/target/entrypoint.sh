#!/bin/sh
set -eu

# The A record must point at this container's address, which the platform
# assigns per student. Resolve it at startup instead of hard-coding an IP.
SELF_IP="$(hostname -i | awk '{print $1}')"
if [ -z "$SELF_IP" ]; then
  echo "could not determine container IP" >&2
  exit 1
fi
sed "s/__SELF_IP__/$SELF_IP/g" /etc/dnsmasq.conf > /tmp/dnsmasq.conf

# Start the authoritative DNS server in the background, then keep the HTTP
# service in the foreground so the container lifecycle follows the web service.
dnsmasq -k --conf-file=/tmp/dnsmasq.conf &

cd /srv
exec python3 -m http.server 80 --bind 0.0.0.0
