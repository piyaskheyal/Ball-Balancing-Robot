#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -x ".venv/bin/python" ]]; then
  echo "Venv not found at: $ROOT/.venv"
  echo "Run: bash scripts/Install.sh"
  exit 1
fi

export PYTHONPATH="$ROOT/src"
exec "$ROOT/.venv/bin/python" -m ballbot.runtime.main "$@"
