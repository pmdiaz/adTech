#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

stop_service() {
  local name=$1
  local pidfile="$SCRIPT_DIR/$name.pid"
  if [ -f "$pidfile" ]; then
    local pid=$(cat "$pidfile")
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid"
      echo "  $name stopped (pid $pid)"
    else
      echo "  $name was not running (pid $pid)"
    fi
    rm -f "$pidfile"
  else
    echo "  $name: no pid file found"
  fi
}

stop_service "dag-processor"
stop_service "scheduler"
stop_service "api-server"
echo ""
echo "Done."
