"""Thin OpenAI-compatible chat client."""

from __future__ import annotations

from typing import Any

from openai import OpenAI

from agent.config import LLMConfig


class LLMClient:
    def __init__(self, config: LLMConfig) -> None:
        if not config.configured:
            raise RuntimeError(
                "LLM API key missing. Set AIB_LLM_API_KEY (or OPENAI_API_KEY) in .env."
            )
        self.config = config
        self._client = OpenAI(api_key=config.api_key, base_url=config.base_url)

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        *,
        tool_choice: str | dict[str, Any] | None = "auto",
        temperature: float | None = 0,
        top_p: float | None = None,
    ) -> Any:
        kwargs: dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
        }
        if temperature is not None:
            kwargs["temperature"] = temperature
        if top_p is not None:
            kwargs["top_p"] = top_p
        if tools:
            kwargs["tools"] = tools
            if tool_choice is not None:
                kwargs["tool_choice"] = tool_choice
        if self.config.provider == "openrouter":
            extra: dict[str, Any] = {}
            order = list(self.config.provider_order)
            if order:
                extra["provider"] = {
                    "order": order,
                    "allow_fallbacks": self.config.allow_fallbacks,
                }
            elif self.config.openrouter_role:
                from agent.model_lock import openrouter_provider_extra

                extra.update(openrouter_provider_extra(self.config.openrouter_role))
            if extra:
                kwargs["extra_body"] = extra
        return self._client.chat.completions.create(**kwargs)
