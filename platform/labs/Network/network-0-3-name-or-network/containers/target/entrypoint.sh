#!/bin/sh
set -eu

# Start the authoritative DNS server in the background, then keep the HTTP
# service in the foreground so the container lifecycle follows the web service.
dnsmasq -k --conf-file=/etc/dnsmasq.conf &

cd /srv
exec python3 -m http.server 80 --bind 0.0.0.0
