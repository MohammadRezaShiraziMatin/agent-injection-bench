#!/usr/bin/env bash
# Verify OpenClaw is reachable from a Cursor integrated terminal (WSL/Linux/macOS).
# Does not print API keys or read secret values from config.
set -euo pipefail

export PATH="${HOME}/.openclaw/bin:${PATH}"

echo "== Environment =="
echo "Host: $(uname -s)"
echo "Shell: ${SHELL:-unknown}"
echo "openclaw: $(command -v openclaw 2>/dev/null || echo 'NOT IN PATH')"

if ! command -v openclaw >/dev/null 2>&1; then
  echo "FAIL: openclaw not found. On Windows, use the WSL default terminal profile."
  exit 1
fi

echo ""
echo "== openclaw --version =="
openclaw --version

echo ""
echo "== openclaw models status =="
openclaw models status 2>&1 | grep -vE 'sk-or-|sk-ant-|Bearer|api[_-]?key' || true

echo ""
echo "== Default model check =="
if openclaw config get agents.defaults.model.primary 2>/dev/null | grep -q 'openrouter/auto'; then
  echo "OK: agents.defaults.model.primary is openrouter/auto"
else
  echo "WARN: set with: openclaw models set openrouter/auto"
fi

echo ""
echo "== Local agent smoke test (no secrets printed) =="
set +e
out="$(openclaw agent --local -m 'Reply with exactly: OK' --json 2>&1)"
code=$?
set -e
echo "$out" | grep -vE 'sk-or-|sk-ant-|Bearer' | tail -20
if echo "$out" | grep -q '"ok": true'; then
  echo "PASS: agent responded via configured provider"
  exit 0
fi
if echo "$out" | grep -qi 'openrouter'; then
  echo "PARTIAL: OpenRouter route configured; auth may need setup (see openclaw models auth login --provider openrouter)"
fi
exit "${code:-1}"
