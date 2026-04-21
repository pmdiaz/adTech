#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/airflow_adtech_env"
LOGS_DIR="$SCRIPT_DIR/logs/services"

export AIRFLOW_HOME="$SCRIPT_DIR"
export AIRFLOW__CORE__LOAD_EXAMPLES=False

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
echo "Password: $(python3 -c "import json; print(json.load(open('$SCRIPT_DIR/simple_auth_manager_passwords.json.generated'))['admin'])" 2>/dev/null || echo 'check $AIRFLOW_HOME/simple_auth_manager_passwords.json.generated')"
echo ""
echo "Logs: $LOGS_DIR"
echo "Stop: bash $SCRIPT_DIR/stop_airflow.sh"
