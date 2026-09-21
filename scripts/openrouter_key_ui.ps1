# Opens the local browser form (via WSL) to enter OpenRouter API key.
$Repo = Split-Path -Parent $PSScriptRoot
wsl.exe -e bash -lc "cd \"$(wslpath '$Repo')\" && python3 scripts/openrouter_key_ui.py"
