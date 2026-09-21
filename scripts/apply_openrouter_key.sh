#!/usr/bin/env bash
# Apply OPENROUTER_API_KEY from .env.openclaw.local → OpenClaw auth store.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck disable=SC1091
source "${repo_root}/scripts/load_openclaw_env.sh"

if [[ -z "${OPENROUTER_API_KEY:-}" ]]; then
  cat >&2 <<EOF
کلید پیدا نشد.

۱) cp .env.openclaw.local.example .env.openclaw.local
۲) فایل .env.openclaw.local را باز کنید و بعد از = کلید OpenRouter را بچسبانید
۳) دوباره: bash scripts/apply_openrouter_key.sh

یا Task: OpenClaw: Enter OpenRouter API Key (فرم مرورگر)
EOF
  exit 1
fi

export OPENROUTER_API_KEY
bash "${repo_root}/scripts/set_openrouter_api_key.sh" --force
