#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"

APP_HOST=127.0.0.1 APP_PORT=7860 \
  .venv/bin/python -m uvicorn app.main:app --app-dir backend \
  --host 127.0.0.1 --port 7860 --reload &
backend_pid=$!
trap 'kill "$backend_pid" 2>/dev/null || true' EXIT INT TERM

npm --prefix frontend run dev
