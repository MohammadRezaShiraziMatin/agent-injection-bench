"""LLM settings from the environment. Never hard-code secrets."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_MAX_STEPS = 6
DEFAULT_TIMEOUT_SEC = 60.0


def _first_env(*names: str) -> str | None:
    for name in names:
        value = os.environ.get(name)
        if value is not None and value.strip():
            return value.strip()
    return None


def load_dotenv(path: Path | None = None) -> None:
    """Load KEY=VALUE lines from a .env file if present.

    Existing environment variables win. This is a tiny local helper — not a
    secret store and not required for the harness.
    """
    env_path = path or (ROOT / ".env")
    if not env_path.is_file():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = value


@dataclass(frozen=True)
class LLMConfig:
    api_key: str
    base_url: str
    model: str
    max_steps: int = DEFAULT_MAX_STEPS
    timeout_sec: float = DEFAULT_TIMEOUT_SEC
    provider: str = "openai_compatible"

    @property
    def chat_completions_url(self) -> str:
        return self.base_url.rstrip("/") + "/chat/completions"

    def masked(self) -> dict[str, str | int | float]:
        """Public metadata safe to write into a trace (no API key)."""
        return {
            "provider": self.provider,
            "model": self.model,
            "base_url": self.base_url,
            "max_steps": self.max_steps,
        }


def config_from_env(*, require_key: bool = True) -> LLMConfig:
    """Read AIB_LLM_* first, then OPENAI_* fallbacks."""
    load_dotenv()
    api_key = _first_env("AIB_LLM_API_KEY", "OPENAI_API_KEY") or ""
    if require_key and not api_key:
        raise LLMConfigError(
            "No API key. Set AIB_LLM_API_KEY or OPENAI_API_KEY "
            "(see .env.example). Dry-run does not need a key."
        )
    base_url = _first_env("AIB_LLM_BASE_URL", "OPENAI_BASE_URL") or DEFAULT_BASE_URL
    model = _first_env("AIB_LLM_MODEL", "OPENAI_MODEL") or DEFAULT_MODEL
    max_steps_raw = _first_env("AIB_LLM_MAX_STEPS")
    timeout_raw = _first_env("AIB_LLM_TIMEOUT_SEC")
    max_steps = int(max_steps_raw) if max_steps_raw else DEFAULT_MAX_STEPS
    timeout_sec = float(timeout_raw) if timeout_raw else DEFAULT_TIMEOUT_SEC
    return LLMConfig(
        api_key=api_key,
        base_url=base_url.rstrip("/"),
        model=model,
        max_steps=max(1, max_steps),
        timeout_sec=timeout_sec,
    )


class LLMConfigError(RuntimeError):
    """Missing or invalid harness configuration."""
