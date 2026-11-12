#!/bin/sh
# Toggle the development-only Advanced DNA Insights gate.
#
# Usage:
#   bash scripts/dev-insights.sh on
#   bash scripts/dev-insights.sh off
#
# Run from the repository root on the development host after the backend
# container is running. The setting is also available in
# Admin -> Settings -> Features.
set -e

VALUE=${1:-on}
case "$VALUE" in
  on|true|1) VALUE=true ;;
  off|false|0) VALUE=false ;;
  *)
    echo "Usage: $0 on|off" >&2
    exit 2
    ;;
esac

docker compose exec -T backend python -c "
from app.database import SessionLocal
from app.services.settings_service import set_setting

db = SessionLocal()
try:
    set_setting(db, 'advanced_dna_insights_enabled', '$VALUE')
finally:
    db.close()
print('advanced_dna_insights_enabled=$VALUE')
"
