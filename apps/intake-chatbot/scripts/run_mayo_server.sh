#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"

credential_path="${AGIGEE_CREDENTIALS_PATH:-/home/m327768/my-codex/apis.jsonl}"
credential_alias="${LLM_CREDENTIAL_ALIAS:-key1}"
access_token_file="${APP_ACCESS_TOKEN_FILE:-$project_root/var/app_access_token}"

if [[ ! -r "$credential_path" ]]; then
  printf 'Credential file is not readable: %s\n' "$credential_path" >&2
  exit 2
fi

if ! CREDENTIAL_PATH="$credential_path" CREDENTIAL_ALIAS="$credential_alias" \
  .venv/bin/python - <<'PY'
import json
import os
from pathlib import Path

path = Path(os.environ["CREDENTIAL_PATH"])
alias = os.environ["CREDENTIAL_ALIAS"]
for line in path.read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    record = json.loads(line)
    if record.get("alias") == alias:
        if record.get("client_id") and record.get("client_secret"):
            raise SystemExit(0)
        break
raise SystemExit(1)
PY
then
  printf 'Credential alias %s is missing or incomplete in %s\n' \
    "$credential_alias" "$credential_path" >&2
  exit 2
fi

mkdir -p "$(dirname "$access_token_file")"
if [[ ! -s "$access_token_file" ]]; then
  umask 077
  .venv/bin/python - <<'PY' >"$access_token_file"
import secrets
print(secrets.token_urlsafe(32))
PY
fi
chmod 600 "$access_token_file"

export AGIGEE_CREDENTIALS_PATH="$credential_path"
export LLM_PROVIDER="${LLM_PROVIDER:-agigee_openai_compatible}"
export LLM_CREDENTIAL_ALIAS="$credential_alias"
export LLM_MODEL="${LLM_MODEL:-gpt-5.6-luna}"
export LLM_BASE_URL="${LLM_BASE_URL:-https://mcc.apix.mayo.edu}"
export LLM_TOKEN_URL="${LLM_TOKEN_URL:-https://mcc.apix.mayo.edu/oauth/token}"
export LLM_API_VERSION="${LLM_API_VERSION:-2025-04-01-preview}"
export APP_HOST="${APP_HOST:-0.0.0.0}"
export APP_PORT="${APP_PORT:-7860}"
export APP_ENV="${APP_ENV:-production}"
export APP_ACCESS_TOKEN="$(<"$access_token_file")"

if [[ ! -f frontend/dist/index.html ]]; then
  npm --prefix frontend run build
fi

printf 'Starting AGENT-O Intake on http://%s:%s\n' "$APP_HOST" "$APP_PORT"
public_url="${APP_PUBLIC_URL:-}"
if [[ -z "$public_url" ]]; then
  browser_host="$APP_HOST"
  if [[ "$browser_host" == "0.0.0.0" || "$browser_host" == "::" ]]; then
    browser_host="$(hostname -I 2>/dev/null | awk '{print $1}')"
    browser_host="${browser_host:-127.0.0.1}"
  fi
  public_url="http://$browser_host:$APP_PORT"
fi
printf 'Open this link to sign in automatically:\n%s/#access_token=%s\n' \
  "${public_url%/}" "$APP_ACCESS_TOKEN"
printf 'LLM credential alias: %s (OAuth tokens are obtained and refreshed automatically)\n' \
  "$LLM_CREDENTIAL_ALIAS"

exec ./scripts/start_server.sh
