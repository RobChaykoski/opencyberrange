#!/bin/sh
# Protected service startup.
#
# The protected host has no address on the training network. Point its default
# route at the appliance so replies to a routed client return through the
# segmentation point, then serve the flag.
set -e

ip link set lo up

appliance_ip=""
for _ in 1 2 3 4 5 6 7 8 9 10; do
    appliance_ip=$(nslookup appliance | awk '/^Address:/{value=$2} END{print value}')
    [ -n "$appliance_ip" ] && break
    sleep 1
done
if [ -z "$appliance_ip" ]; then
    echo "cannot resolve the appliance on the control segment" >&2
    exit 1
fi

ip route replace default via "$appliance_ip"
echo "protected segment default route via $appliance_ip"

exec nginx -g 'daemon off;'
