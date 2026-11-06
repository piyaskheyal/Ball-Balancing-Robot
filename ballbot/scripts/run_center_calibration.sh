#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -x ".venv/bin/python" ]]; then
  echo "Virtual environment not found at: $ROOT/.venv"
  exit 1
fi

export PYTHONPATH="$ROOT/src:${PYTHONPATH:-}"
exec "$ROOT/.venv/bin/python" "$ROOT/scripts/calibrate_camera_center.py" "$@"
