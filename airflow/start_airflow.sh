#!/bin/bash
set -e

# ─────────────────────────────────────────────
# Start Airflow in server mode (background)
# Runs: api-server, scheduler, dag-processor
#
# Usage:
#   bash airflow/start_airflow.sh local
#   bash airflow/start_airflow.sh cloud <usuario> <password> <database_url>
#
# Stop: bash airflow/stop_airflow.sh
# ─────────────────────────────────────────────

ENV=${1:-local}

if [ "$ENV" = "cloud" ]; then
  if [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ]; then
    echo "ERROR: cloud mode requires: <usuario> <password> <database_url>"
    echo "Usage: bash airflow/start_airflow.sh cloud <usuario> <password> <database_url>"
    exit 1
  fi
  USUARIO=$2
  PASSWORD=$3
  DATABASE_URL=$4
elif [ "$ENV" != "local" ]; then
  echo "ERROR: env must be 'local' or 'cloud'"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/airflow_adtech_env"
LOGS_DIR="$SCRIPT_DIR/logs/services"

export AIRFLOW_HOME="$SCRIPT_DIR"
export AIRFLOW__CORE__LOAD_EXAMPLES=False

if [ "$ENV" = "cloud" ]; then
  export AIRFLOW__CORE__PARALLELISM=2
  export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="postgresql+psycopg2://$USUARIO:$PASSWORD@$DATABASE_URL"
  echo "Modo cloud (DB: $DATABASE_URL)"
else
  echo "Mode local (SQLite)"
fi

# Load DB credentials as Airflow Variables
if [ -f "$SCRIPT_DIR/.env" ]; then
  set -a
  source "$SCRIPT_DIR/.env"
  set +a
fi

# Activate virtualenv
source "$VENV_DIR/bin/activate"

mkdir -p "$LOGS_DIR"

echo "Arranca Airflow (AIRFLOW_HOME=$AIRFLOW_HOME)"
echo ""

# api-server
airflow api-server --port 8080 >> "$LOGS_DIR/api-server.log" 2>&1 &
echo $! > "$SCRIPT_DIR/api-server.pid"
echo "  api-server    started (pid $(cat $SCRIPT_DIR/api-server.pid))"

# scheduler
airflow scheduler >> "$LOGS_DIR/scheduler.log" 2>&1 &
echo $! > "$SCRIPT_DIR/scheduler.pid"
echo "  scheduler     started (pid $(cat $SCRIPT_DIR/scheduler.pid))"

# dag-processor
airflow dag-processor >> "$LOGS_DIR/dag-processor.log" 2>&1 &
echo $! > "$SCRIPT_DIR/dag-processor.pid"
echo "  dag-processor started (pid $(cat $SCRIPT_DIR/dag-processor.pid))"

echo ""
echo "Password check $SCRIPT_DIR/simple_auth_manager_passwords.json.generated')"
echo ""
echo "Logs: $LOGS_DIR"
echo "Stop: bash $SCRIPT_DIR/stop_airflow.sh"
