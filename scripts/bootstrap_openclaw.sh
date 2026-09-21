#!/usr/bin/env bash
# Idempotent OpenClaw bootstrap for Cursor (Linux/WSL Cloud Agent). No secrets in repo.
set -euo pipefail

OPENCLAW_BIN="${HOME}/.openclaw/bin/openclaw"
export PATH="${HOME}/.openclaw/bin:${PATH}"

install_cli() {
  if [[ -x "${OPENCLAW_BIN}" ]]; then
    return 0
  fi
  curl -fsSL https://openclaw.ai/install-cli.sh | bash -s -- --no-onboard
}

ensure_path_in_bashrc() {
  local marker='# OpenClaw CLI (Cursor bootstrap)'
  if grep -qF "${marker}" "${HOME}/.bashrc" 2>/dev/null; then
    return 0
  fi
  cat >>"${HOME}/.bashrc" <<EOF

${marker}
if [ -d "\$HOME/.openclaw/bin" ]; then
  export PATH="\$HOME/.openclaw/bin:\$PATH"
fi
EOF
}

ensure_model_default() {
  command -v openclaw >/dev/null 2>&1 || return 0
  local current
  current="$(openclaw config get agents.defaults.model.primary 2>/dev/null || true)"
  if [[ "${current}" == *openrouter/auto* ]]; then
    return 0
  fi
  openclaw models set openrouter/auto
}

ensure_gateway_mode() {
  command -v openclaw >/dev/null 2>&1 || return 0
  local mode
  mode="$(openclaw config get gateway.mode 2>/dev/null || true)"
  if [[ "${mode}" == *local* ]]; then
    return 0
  fi
  openclaw config set gateway.mode local
}

write_gateway_token_file() {
  # Token lives in ~/.openclaw/openclaw.json (not in git). CLI redacts on read; parse file locally.
  local cfg="${HOME}/.openclaw/openclaw.json"
  if [[ ! -f "${cfg}" ]] || ! python3 -c "import json, pathlib; d=json.loads(pathlib.Path('${cfg}').read_text()); exit(0 if (d.get('gateway') or {}).get('auth', {}).get('token') else 1)" 2>/dev/null; then
    openclaw doctor --fix --generate-gateway-token >/dev/null 2>&1 || true
  fi
  [[ -f "${cfg}" ]] || return 0
  python3 - <<'PY' || return 0
import json, os, pathlib
cfg = pathlib.Path(os.environ["HOME"]) / ".openclaw" / "openclaw.json"
data = json.loads(cfg.read_text())
token = (data.get("gateway") or {}).get("auth", {}).get("token")
if not token or token in ("undefined", "null"):
    raise SystemExit(1)
out = pathlib.Path(os.environ["HOME"]) / ".openclaw" / "gateway.token"
out.write_text(str(token) + "\n", encoding="utf-8")
out.chmod(0o600)
PY
}

sync_openrouter_from_env() {
  if [[ -z "${OPENROUTER_API_KEY:-}" ]]; then
    return 0
  fi
  local rotate="${OPENROUTER_API_KEY_ROTATE:-0}"
  if [[ "${rotate}" == "1" || "${rotate}" == "true" || "${rotate}" == "yes" ]]; then
    bash "$(dirname "${BASH_SOURCE[0]}")/set_openrouter_api_key.sh" --force
    return 0
  fi
  if openclaw models auth list 2>/dev/null | grep -qi openrouter; then
    return 0
  fi
  printf '%s' "${OPENROUTER_API_KEY}" | openclaw models auth paste-api-key --provider openrouter >/dev/null 2>&1 || true
}

install_cli
ensure_path_in_bashrc
ensure_model_default
ensure_gateway_mode
openclaw config set env.shellEnv.enabled true >/dev/null 2>&1 || true
write_gateway_token_file
sync_openrouter_from_env

echo "OpenClaw bootstrap OK: $(openclaw --version 2>/dev/null || echo missing)"
