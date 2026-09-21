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

### Verify

```bash
./scripts/verify_openclaw_cursor.sh
```

Default model should be `openrouter/auto`. Do not reset WhatsApp/Telegram/Gateway channel config when adjusting models.
