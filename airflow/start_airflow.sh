#!/bin/bash
set -e

# ─────────────────────────────────────────────
# Start Airflow in server mode (background)
# Runs: api-server, scheduler, dag-processor
#
# Usage:
#   bash airflow/start_airflow.sh         # local (SQLite)
#   bash airflow/start_airflow.sh cloud   # cloud (PostgreSQL, reads .env)
#
# Stop: bash airflow/stop_airflow.sh
# ─────────────────────────────────────────────

ENV=${1:-local}

if [ "$ENV" != "local" ] && [ "$ENV" != "cloud" ]; then
  echo "ERROR: env must be 'local' or 'cloud'"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/airflow_adtech_env"
LOGS_DIR="$SCRIPT_DIR/logs/services"

export AIRFLOW_HOME="$SCRIPT_DIR"
export AIRFLOW__CORE__LOAD_EXAMPLES=False

# Load .env (Airflow Variables + optional DB connection override)
if [ -f "$SCRIPT_DIR/.env" ]; then
  set -a
  source "$SCRIPT_DIR/.env"
  set +a
else
  echo "WARNING: $SCRIPT_DIR/.env not found"
fi

if [ "$ENV" = "cloud" ]; then
  if [ -z "$AIRFLOW__DATABASE__SQL_ALCHEMY_CONN" ]; then
    echo "ERROR: cloud mode requires AIRFLOW__DATABASE__SQL_ALCHEMY_CONN in .env"
    exit 1
  fi
  if [ -z "$AIRFLOW_VAR_DB_USER" ] || [ -z "$AIRFLOW_VAR_DB_PASS" ] || [ -z "$AIRFLOW_VAR_DB_HOST" ] || [ -z "$AIRFLOW_VAR_DB_NAME" ]; then
    echo "ERROR: cloud mode requires AIRFLOW_VAR_DB_USER, AIRFLOW_VAR_DB_PASS, AIRFLOW_VAR_DB_HOST, AIRFLOW_VAR_DB_NAME in .env"
    exit 1
  fi
  export AIRFLOW__CORE__PARALLELISM=2
  echo "Modo cloud (metadata DB: $AIRFLOW__DATABASE__SQL_ALCHEMY_CONN)"
else
  echo "Modo local (SQLite)"
fi

# Activate virtualenv
source "$VENV_DIR/bin/activate"

mkdir -p "$LOGS_DIR"

echo "Ejecutando db migrate..."
airflow db migrate

echo ""
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
