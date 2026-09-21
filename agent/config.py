"""Environment-backed configuration for the agent harness."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Literal

from dotenv import load_dotenv

OPENROUTER_PROVIDER = "openrouter"
OPENROUTER_DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"

OpenRouterRole = Literal["target", "judge"]


@dataclass(frozen=True)
class LLMConfig:
    api_key: str
    base_url: str
    model: str
    provider: str | None = None

    @property
    def configured(self) -> bool:
        return bool(self.api_key.strip())


def _env_strip(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _openrouter_api_key() -> str:
    return _env_strip("OPENROUTER_API_KEY") or _env_strip("AIB_LLM_API_KEY") or _env_strip(
        "OPENAI_API_KEY"
    )


def load_openrouter_config_for_role(
    role: OpenRouterRole,
    *,
    dotenv_path: str | None = None,
) -> LLMConfig:
    load_dotenv(dotenv_path=dotenv_path, override=False)
    model = _env_strip("OPENROUTER_TARGET_MODEL") if role == "target" else _env_strip(
        "OPENROUTER_JUDGE_MODEL"
    )
    return LLMConfig(
        api_key=_openrouter_api_key(),
        base_url=_env_strip("OPENROUTER_BASE_URL", OPENROUTER_DEFAULT_BASE_URL),
        model=model,
        provider=OPENROUTER_PROVIDER,
    )


def describe_openrouter_config(*, dotenv_path: str | None = None) -> dict[str, Any]:
    """Offline summary (never includes secret values)."""
    load_dotenv(dotenv_path=dotenv_path, override=False)
    target = _env_strip("OPENROUTER_TARGET_MODEL")
    judge = _env_strip("OPENROUTER_JUDGE_MODEL")
    return {
        "provider": OPENROUTER_PROVIDER,
        "base_url": _env_strip("OPENROUTER_BASE_URL", OPENROUTER_DEFAULT_BASE_URL),
        "target_model": target or None,
        "judge_model": judge or None,
        "api_key": "present" if _openrouter_api_key() else "not present",
        "allow_fallbacks": _env_strip("OPENROUTER_ALLOW_FALLBACKS", "false").lower() == "true",
        "provider_routing": _env_strip("OPENROUTER_PROVIDER_ORDER") or None,
    }


def load_config(*, dotenv_path: str | None = None) -> LLMConfig:
    """Load LLM settings from environment (.env optional)."""
    load_dotenv(dotenv_path=dotenv_path, override=False)
    api_key = (
        os.getenv("AIB_LLM_API_KEY", "").strip()
        or os.getenv("OPENAI_API_KEY", "").strip()
    )
    base_url = os.getenv("AIB_LLM_BASE_URL", "https://api.openai.com/v1").strip()
    model = os.getenv("AIB_LLM_MODEL", "gpt-4o-mini").strip()
    return LLMConfig(api_key=api_key, base_url=base_url, model=model)
