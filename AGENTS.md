# Agent instructions

## OpenClaw + Cursor

This repo is wired for **OpenClaw in WSL/Linux**, not a duplicate Windows global install.

### Terminal (local Windows)

- Integrated terminal default profile: **OpenClaw (WSL login shell)** (see `.vscode/settings.json`).
- From PowerShell without WSL profile: `.\scripts\openclaw.ps1 --version`

### Cloud Agent

- `.cursor/environment.json` runs `scripts/bootstrap_openclaw.sh` and starts the **OpenClaw Gateway** terminal (`ws://127.0.0.1:18789`).
- MCP bridge: `.cursor/mcp.json` → `openclaw mcp serve` (enable in Cursor **Settings → MCP**).
- Put **`OPENROUTER_API_KEY`** in the Cursor environment **Secrets** (never commit). Bootstrap imports it into the local auth store when present.
- **Rotate key:** update the secret, then either run `./scripts/set_openrouter_api_key.sh --force` (WSL) with `OPENROUTER_API_KEY` set, or set `OPENROUTER_API_KEY_ROTATE=1` and re-run bootstrap / restart Cloud Agent.
- **Browser form:** Run Task **OpenClaw: Enter OpenRouter API Key** (`.vscode/tasks.json`) or `python3 scripts/openrouter_key_ui.py` — opens `http://127.0.0.1:8765/` on this machine only.

### Verify

```bash
./scripts/verify_openclaw_cursor.sh
```

Default model should be `openrouter/auto`. Do not reset WhatsApp/Telegram/Gateway channel config when adjusting models.
