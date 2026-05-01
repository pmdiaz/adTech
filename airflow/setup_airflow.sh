#!/bin/bash
set -e


SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/airflow_adtech_env"

export AIRFLOW_HOME="$SCRIPT_DIR"

echo "AIRFLOW_HOME: $AIRFLOW_HOME"
echo "Virtualenv:   $VENV_DIR"



if [ ! -d "$VENV_DIR" ]; then
  python3.12 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

echo ""
echo "pip install apache-airflow==3.1.8 via constraint url"
pip install --quiet --upgrade pip
pip install "apache-airflow==3.1.8" \
  --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-3.1.8/constraints-3.12.txt"


echo "Instalo dependencias en requirements"
pip install --quiet -r "$SCRIPT_DIR/requirements.txt"


echo ""
echo "Done."
echo ""
