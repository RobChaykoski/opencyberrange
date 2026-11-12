#!/bin/sh
set -eu

# A short, fixed interval keeps the capture window small for students while
# still looking like a real implant check-in.
while true; do
    curl -fsS --max-time 8 \
        -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36' \
        -H 'Accept: application/json' \
        http://127.0.0.1:9000/tasking.json >/dev/null 2>&1 || true
    sleep 4
done
