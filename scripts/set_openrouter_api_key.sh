#!/usr/bin/env bash
# Replace OpenRouter API key in OpenClaw auth store (WSL/Linux). Never prints the key.
set -euo pipefail

export PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/.bin:${HOME}/.openclaw/bin:${PATH}"

usage() {
  cat <<'EOF'
Usage: set_openrouter_api_key.sh [--force]

Sets OpenRouter credentials for the default agent via OpenClaw auth store.

Sources (first match wins):
  1. OPENROUTER_API_KEY environment variable (e.g. Cursor Environment Secret)
  2. Hidden prompt on a TTY

Options:
  --force   Remove existing openrouter:* profiles before saving the new key

Does not write keys into the git repo or openclaw.json env.vars literals.
After saving, restarts the Gateway when it is reachable.
EOF
}

FORCE=0
if [[ "${1:-}" == "--force" ]]; then
  FORCE=1
elif [[ -n "${1:-}" ]]; then
  usage >&2
  exit 2
fi

if ! command -v openclaw >/dev/null 2>&1; then
  echo "openclaw not found. Use WSL terminal or run scripts/bootstrap_openclaw.sh first." >&2
  exit 1
fi

read_key() {
  if [[ -n "${OPENROUTER_API_KEY:-}" ]]; then
    printf '%s' "${OPENROUTER_API_KEY}"
    return 0
  fi
  if [[ ! -t 0 ]]; then
    echo "Provide OPENROUTER_API_KEY or run interactively on a TTY." >&2
    return 1
  fi
  local key
  read -rs -p "New OpenRouter API key (input hidden): " key >&2
  echo >&2
  printf '%s' "${key}"
}

remove_openrouter_profiles() {
  local ids
  ids="$(openclaw models auth list 2>/dev/null | awk '/^-/ {print $2}' | grep -E '^openrouter:' || true)"
  if [[ -z "${ids}" ]]; then
    return 0
  fi
  while IFS= read -r id; do
    [[ -z "${id}" ]] && continue
    openclaw models auth logout "${id}" --yes >/dev/null 2>&1 || true
  done <<<"${ids}"
}

# Drop legacy literal env overrides if present (prefer auth store + shell env).
openclaw config unset env.vars.OPENROUTER_API_KEY >/dev/null 2>&1 || true

key="$(read_key)" || exit 1
if [[ -z "${key}" ]]; then
  echo "Empty key; aborted." >&2
  exit 1
fi

if [[ "${FORCE}" -eq 1 ]]; then
  remove_openrouter_profiles
fi

printf '%s' "${key}" | openclaw models auth paste-api-key --provider openrouter >/dev/null

profile_id="openrouter:manual"
if openclaw models auth list 2>/dev/null | grep -q 'openrouter:default'; then
  profile_id="openrouter:default"
fi
openclaw models auth activate "${profile_id}" >/dev/null 2>&1 || true

if openclaw gateway status 2>&1 | grep -q 'Connectivity probe: ok'; then
  openclaw gateway restart >/dev/null 2>&1 || openclaw gateway stop >/dev/null 2>&1 || true
fi

echo "OpenRouter API key updated in auth store (profile ${profile_id})."
openclaw models status 2>&1 | grep -vE 'sk-or-|Bearer' | sed -n '1,20p'

unset key
