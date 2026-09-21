#!/usr/bin/env bash
# Load OPENROUTER_API_KEY from gitignored .env.openclaw.local (repo root).
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
local_env="${repo_root}/.env.openclaw.local"

if [[ ! -f "${local_env}" ]]; then
  return 0 2>/dev/null || exit 0
fi

set -a
# shellcheck disable=SC1090
source "${local_env}"
set +a
