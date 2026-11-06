#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export TERM="${TERM:-xterm}"
export PYTHONPATH="$ROOT/src"

if [[ ! -x ".venv/bin/python" ]]; then
  echo "Virtualenv not found at: $ROOT/.venv"
  exit 1
fi

echo "[INFO] Launching Ballbot Real-Time Calibration..."
exec "$ROOT/.venv/bin/python" -m ballbot.runtime.calibration
