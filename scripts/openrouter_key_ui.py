#!/usr/bin/env python3
"""Local-only browser form to set OpenRouter API key for OpenClaw (127.0.0.1)."""

from __future__ import annotations

import html
import os
import subprocess
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

HOST = "127.0.0.1"
PORT = 8765
REPO_ROOT = Path(__file__).resolve().parents[1]
SET_KEY_SCRIPT = REPO_ROOT / "scripts" / "set_openrouter_api_key.sh"


def _run_set_key(api_key: str) -> tuple[bool, str]:
    env = os.environ.copy()
    env["OPENROUTER_API_KEY"] = api_key
    env["PATH"] = f"{REPO_ROOT / '.bin'}:{Path.home() / '.openclaw' / 'bin'}:{env.get('PATH', '')}"
    try:
        proc = subprocess.run(
            ["bash", str(SET_KEY_SCRIPT), "--force"],
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return False, "Timed out while saving the key."
    out = (proc.stdout or "") + (proc.stderr or "")
    safe = "\n".join(line for line in out.splitlines() if "sk-or-" not in line.lower())
    if proc.returncode != 0:
        return False, safe.strip() or "Failed to save API key."
    return True, safe.strip() or "OpenRouter API key saved."


PAGE = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>OpenClaw — OpenRouter API Key</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 32rem; margin: 3rem auto; padding: 0 1rem; }}
    h1 {{ font-size: 1.25rem; }}
    label {{ display: block; margin: 1rem 0 0.35rem; }}
    input[type=password], input[type=text] {{ width: 100%; padding: 0.65rem; font-size: 1rem; box-sizing: border-box; }}
    button {{ margin-top: 1rem; padding: 0.5rem 1rem; }}
    .msg {{ margin-top: 1rem; padding: 0.75rem; border-radius: 6px; }}
    .ok {{ background: #e8f5e9; }}
    .err {{ background: #ffebee; }}
    .hint {{ color: #555; font-size: 0.9rem; margin-top: 0.5rem; }}
  </style>
</head>
<body>
  <h1>کلید OpenRouter</h1>
  <p class="hint">کلید را paste کنید و ذخیره بزنید. (یا فایل <code>.env.openclaw.local</code> + Task «Apply API key»)</p>
  {message}
  <form method="POST" action="/">
    <label for="api_key">API Key</label>
    <input id="api_key" name="api_key" type="text" autocomplete="off" required autofocus placeholder="sk-or-..." />
    <button type="submit">ذخیره در OpenClaw</button>
  </form>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    server_version = "OpenClawKeyUI/1.0"

    def log_message(self, fmt: str, *args) -> None:
        # Never log POST bodies (may contain keys).
        if self.command == "POST":
            sys.stderr.write(f"{self.address_string()} - POST / [redacted]\n")
            return
        super().log_message(fmt, *args)

    def do_GET(self) -> None:
        if self.path not in ("/", ""):
            self.send_error(404)
            return
        body = PAGE.format(message="").encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        if self.path not in ("/", ""):
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        if length > 65536:
            self.send_error(413)
            return
        raw = self.rfile.read(length).decode("utf-8", errors="replace")
        fields = parse_qs(raw, keep_blank_values=False)
        api_key = (fields.get("api_key") or [""])[0].strip()
        if not api_key:
            msg = '<div class="msg err">کلید خالی است.</div>'
            self._html(PAGE.format(message=msg))
            return
        ok, text = _run_set_key(api_key)
        del api_key
        cls = "ok" if ok else "err"
        msg = f'<div class="msg {cls}">{html.escape(text)}</div>'
        self._html(PAGE.format(message=msg))

    def _html(self, page: str) -> None:
        body = page.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> int:
    if not SET_KEY_SCRIPT.is_file():
        print(f"Missing {SET_KEY_SCRIPT}", file=sys.stderr)
        return 1
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}/"
    print(f"OpenClaw OpenRouter key UI: {url}")
    print("Press Ctrl+C to stop.")
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
