# Agent instructions

## OpenClaw + Cursor

This repo is wired for **OpenClaw in WSL/Linux**, not a duplicate Windows global install.

### Terminal (local Windows)

- Integrated terminal default profile: **OpenClaw (WSL login shell)** (see `.vscode/settings.json`).
- From PowerShell without WSL profile: `.\scripts\openclaw.ps1 --version`

### Cloud Agent

- `.cursor/environment.json` runs `pip install -e '.[dev]'`, `scripts/bootstrap_openclaw.sh`, and starts the **OpenClaw Gateway** terminal (`ws://127.0.0.1:18789`).
- MCP bridge: `.cursor/mcp.json` → `openclaw mcp serve` (enable in Cursor **Settings → MCP**).
- **OpenRouter API key (optional in Cloud Secrets):** if you skip dashboard secrets, set the key on the machine that runs OpenClaw:
  - Task **OpenClaw: Enter OpenRouter API Key**, or `python3 scripts/openrouter_key_ui.py` → http://127.0.0.1:8765/
  - WSL: `./scripts/set_openrouter_api_key.sh --force`
- Optional Cloud Secret **`OPENROUTER_API_KEY`**: bootstrap imports it when present; use **`OPENROUTER_API_KEY_ROTATE=1`** once to replace an existing profile.

### Verify

```bash
./scripts/verify_openclaw_cursor.sh
```

Default model should be `openrouter/auto`. Do not reset WhatsApp/Telegram/Gateway channel config when adjusting models.
