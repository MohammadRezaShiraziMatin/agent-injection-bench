# Agent instructions

## OpenClaw — گذاشتن API Key (ساده)

**روش پیشنهادی (فقط یک فایل محلی، داخل Git نمی‌رود):**

```bash
cp .env.openclaw.local.example .env.openclaw.local
```

فایل **`.env.openclaw.local`** را باز کنید؛ بعد از `=` کلید OpenRouter را paste کنید، ذخیره کنید، بعد:

```bash
bash scripts/apply_openrouter_key.sh
```

همین. Bootstrap و Cloud Agent بعداً همان فایل را می‌خوانند (اگر روی همان ماشین باشد).

**روش دوم — پنجره مرورگر:** Task **`OpenClaw: Enter OpenRouter API Key`** یا `python3 scripts/openrouter_key_ui.py`

### Terminal (Windows)

پروفایل **OpenClaw (WSL login shell)** — `openclaw --version`

### Cloud Agent

`.cursor/environment.json` — Gateway روی `:18789`. Secret در Dashboard **اختیاری** است؛ ترجیحاً همان `.env.openclaw.local` در WSL.

### Verify

```bash
./scripts/verify_openclaw_cursor.sh
```

مدل پیش‌فرض: `openrouter/auto`. کانال‌های WhatsApp/Telegram را reset نکنید.
