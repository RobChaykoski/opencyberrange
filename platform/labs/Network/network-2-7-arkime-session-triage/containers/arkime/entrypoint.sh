#!/bin/bash
set -euo pipefail

ES="${ARKIME_OPENSEARCH_URL:-http://opensearch:9200}"
PASSWORD="${ARKIME_ADMIN_PASSWORD:?ARKIME_ADMIN_PASSWORD is required}"
ANALYST_PASSWORD="${ARKIME_ANALYST_PASSWORD:?ARKIME_ANALYST_PASSWORD is required}"
SEED="${ARKIME_SEED_PCAP:-/tmp/arkime-seed.pcap}"

echo "arkime: waiting for OpenSearch at ${ES}"
ready=0
for _ in $(seq 1 90); do
    if curl -fsS "${ES}/_cluster/health?wait_for_status=yellow&timeout=5s" >/dev/null; then
        ready=1
        break
    fi
    sleep 2
done

if [ "${ready}" -ne 1 ]; then
    echo "arkime: OpenSearch did not become ready" >&2
    exit 1
fi

/opt/arkime/db/db.pl "${ES}" init --ifneeded

# The viewer signs users with the passwordSecret in config.ini. The lab user is
# recreated only on a fresh index; an existing user is left alone.
/opt/arkime/bin/arkime_add_user.sh admin "Lab Admin" "${PASSWORD}" --admin >/dev/null 2>&1 || true
/opt/arkime/bin/arkime_add_user.sh analyst "SOC Analyst" "${ANALYST_PASSWORD}" --hidePcap >/dev/null 2>&1 || true

# Seed once. The marker lives in OpenSearch so a restart of this container does
# not create duplicate sessions, while a fresh index is seeded again.
if ! curl -fsS "${ES}/arkime-lab-seeded/_doc/1" >/dev/null 2>&1; then
    echo "arkime: importing the synthetic capture"
    python3 /opt/arkime/seed_pcap.py "${SEED}"
    /opt/arkime/bin/capture -r "${SEED}" --node arkime-lab
    curl -fsS -X PUT "${ES}/arkime-lab-seeded/_doc/1" \
        -H 'Content-Type: application/json' \
        -d '{"seeded":true}' >/dev/null
fi

cd /opt/arkime/viewer
exec /opt/arkime/bin/node viewer.js
