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
    provider_order: tuple[str, ...] = ()
    allow_fallbacks: bool = False
    openrouter_role: OpenRouterRole | None = None

    @property
    def configured(self) -> bool:
        return bool(self.api_key.strip())


def _env_strip(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _openrouter_api_key() -> str:
    return _env_strip("OPENROUTER_API_KEY") or _env_strip("AIB_LLM_API_KEY") or _env_strip(
        "OPENAI_API_KEY"
    )


def _provider_order_for_role(role: OpenRouterRole) -> tuple[str, ...]:
    env_key = (
        "OPENROUTER_TARGET_PROVIDER_ORDER"
        if role == "target"
        else "OPENROUTER_JUDGE_PROVIDER_ORDER"
    )
    raw = _env_strip(env_key) or _env_strip("OPENROUTER_PROVIDER_ORDER")
    if raw:
        return tuple(p.strip() for p in raw.split(",") if p.strip())
    try:
        from agent.model_lock import role_block

        pol = role_block(role).get("routing_policy") or {}
        return tuple(pol.get("provider_order") or [])
    except OSError:
        return ()


def load_openrouter_config_for_role(
    role: OpenRouterRole,
    *,
    dotenv_path: str | None = None,
) -> LLMConfig:
    load_dotenv(dotenv_path=dotenv_path, override=False)
    env_model = _env_strip("OPENROUTER_TARGET_MODEL") if role == "target" else _env_strip(
        "OPENROUTER_JUDGE_MODEL"
    )
    gate_model = ""
    try:
        from agent.model_lock import role_block

        gate_model = str(role_block(role).get("exact_model_id") or "")
    except OSError:
        gate_model = ""
    model = env_model or gate_model
    allow_fb = _env_strip("OPENROUTER_ALLOW_FALLBACKS", "false").lower() == "true"
    return LLMConfig(
        api_key=_openrouter_api_key(),
        base_url=_env_strip("OPENROUTER_BASE_URL", OPENROUTER_DEFAULT_BASE_URL),
        model=model,
        provider=OPENROUTER_PROVIDER,
        provider_order=_provider_order_for_role(role),
        allow_fallbacks=allow_fb,
        openrouter_role=role,
    )


def describe_openrouter_config(*, dotenv_path: str | None = None) -> dict[str, Any]:
    """Offline summary (never includes secret values)."""
    load_dotenv(dotenv_path=dotenv_path, override=False)
    target = _env_strip("OPENROUTER_TARGET_MODEL")
    judge = _env_strip("OPENROUTER_JUDGE_MODEL")
    gate_target = ""
    gate_judge = ""
    try:
        from agent.model_lock import role_block

        gate_target = str(role_block("target").get("exact_model_id") or "")
        gate_judge = str(role_block("judge").get("exact_model_id") or "")
    except OSError:
        pass
    resolved_target = target or gate_target or None
    resolved_judge = judge or gate_judge or None
    return {
        "provider": OPENROUTER_PROVIDER,
        "base_url": _env_strip("OPENROUTER_BASE_URL", OPENROUTER_DEFAULT_BASE_URL),
        "target_model": resolved_target,
        "judge_model": resolved_judge,
        "env_target_model": target or None,
        "env_judge_model": judge or None,
        "api_key": "present" if _openrouter_api_key() else "not present",
        "allow_fallbacks": _env_strip("OPENROUTER_ALLOW_FALLBACKS", "false").lower() == "true",
        "provider_routing": _env_strip("OPENROUTER_PROVIDER_ORDER") or None,
        "target_provider_order": list(_provider_order_for_role("target")),
        "judge_provider_order": list(_provider_order_for_role("judge")),
    }


def load_config(*, dotenv_path: str | None = None) -> LLMConfig:
    """Load LLM settings from environment (.env optional)."""
    load_dotenv(dotenv_path=dotenv_path, override=False)
    provider = _env_strip("AIB_LLM_PROVIDER").lower()
    if provider == OPENROUTER_PROVIDER:
        return load_openrouter_config_for_role("target", dotenv_path=dotenv_path)

    api_key = _env_strip("AIB_LLM_API_KEY") or _env_strip("OPENAI_API_KEY")
    base_url = _env_strip("AIB_LLM_BASE_URL", "https://api.openai.com/v1")
    model = _env_strip("AIB_LLM_MODEL", "gpt-4o-mini")
    return LLMConfig(api_key=api_key, base_url=base_url, model=model)
