#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"

host="${APP_HOST:-127.0.0.1}"
port="${APP_PORT:-7860}"

if [[ "$host" == "0.0.0.0" || "$host" == "::" ]]; then
  if [[ -z "${APP_ACCESS_TOKEN:-}" && "${ALLOW_INSECURE_BIND:-false}" != "true" ]]; then
    printf '%s\n' "APP_ACCESS_TOKEN is required for a remote bind." >&2
    exit 2
  fi
fi

.venv/bin/python scripts/inspect_ontology.py --check
exec .venv/bin/python -m uvicorn app.main:app --app-dir backend \
  --host "$host" --port "$port"
