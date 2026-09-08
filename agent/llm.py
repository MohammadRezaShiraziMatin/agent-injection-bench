"""OpenAI-compatible Chat Completions client + a scripted client for tests."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Protocol

from agent.config import LLMConfig
from agent.errors import LLMError


@dataclass
class ToolCallRequest:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class LLMResponse:
    content: str | None
    tool_calls: list[ToolCallRequest] = field(default_factory=list)
    raw: dict[str, Any] | None = None
    # Provider-reported usage only. Never estimate.
    usage: dict[str, int] | None = None


class LLMClient(Protocol):
    def complete(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> LLMResponse:
        """One chat-completions turn."""


def extract_usage(payload: dict[str, Any] | None) -> dict[str, int] | None:
    """Return provider usage ints when present; else None (do not invent)."""
    if not isinstance(payload, dict):
        return None
    usage = payload.get("usage")
    if not isinstance(usage, dict):
        return None
    out: dict[str, int] = {}
    for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
        val = usage.get(key)
        if isinstance(val, bool):
            continue
        if isinstance(val, int):
            out[key] = val
        elif isinstance(val, float) and val.is_integer():
            out[key] = int(val)
    return out or None


def _parse_arguments(raw: Any) -> dict[str, Any]:
    if raw is None:
        return {}
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        if not raw.strip():
            return {}
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise LLMError(f"tool arguments are not valid JSON: {raw!r}") from exc
        if not isinstance(parsed, dict):
            raise LLMError("tool arguments JSON must be an object")
        return parsed
    raise LLMError(f"unsupported tool arguments type: {type(raw).__name__}")


def parse_chat_completion(payload: dict[str, Any]) -> LLMResponse:
    try:
        message = payload["choices"][0]["message"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError("completion JSON missing choices[0].message") from exc
    content = message.get("content")
    if content is not None:
        content = str(content)
    tool_calls: list[ToolCallRequest] = []
    for i, item in enumerate(message.get("tool_calls") or []):
        if not isinstance(item, dict):
            continue
        fn = item.get("function") or {}
        name = str(fn.get("name") or "")
        call_id = str(item.get("id") or f"call_{i}")
        tool_calls.append(
            ToolCallRequest(id=call_id, name=name, arguments=_parse_arguments(fn.get("arguments")))
        )
    return LLMResponse(
        content=content,
        tool_calls=tool_calls,
        raw=payload,
        usage=extract_usage(payload),
    )


class OpenAICompatibleClient:
    """POST /chat/completions. Used only for the LLM HTTP call, never for tools."""

    def __init__(self, config: LLMConfig, *, opener=None) -> None:
        self.config = config
        self._opener = opener or urllib.request.urlopen

    def complete(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> LLMResponse:
        body: dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "tools": tools,
            "temperature": self.config.temperature,
        }
        # OpenAI-compatible `seed` is best-effort: not all providers honor it.
        if self.config.seed is not None:
            body["seed"] = self.config.seed
        request = urllib.request.Request(
            self.config.chat_completions_url,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with self._opener(request, timeout=self.config.timeout_sec) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
            raise LLMError(
                f"LLM HTTP {exc.code} from {self.config.chat_completions_url}: {detail[:500]}"
            ) from exc
        except urllib.error.URLError as exc:
            raise LLMError(f"LLM request failed: {exc.reason}") from exc
        except TimeoutError as exc:
            raise LLMError("LLM request timed out") from exc
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise LLMError("LLM response is not JSON") from exc
        if not isinstance(payload, dict):
            raise LLMError("LLM response JSON must be an object")
        if payload.get("error"):
            raise LLMError(f"LLM API error: {payload['error']}")
        return parse_chat_completion(payload)


class ScriptedLLM:
    """Deterministic client for unit tests. No HTTP."""

    def __init__(self, responses: list[LLMResponse] | None = None) -> None:
        self._responses = list(responses or [])
        self.calls: list[dict[str, Any]] = []

    def complete(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> LLMResponse:
        self.calls.append({"messages": messages, "tools": tools})
        if not self._responses:
            raise LLMError("ScriptedLLM has no remaining responses")
        return self._responses.pop(0)


class FailingLLM:
    """Always raises LLMError (API / parse failure tests)."""

    def __init__(self, message: str = "simulated API failure") -> None:
        self.message = message

    def complete(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> LLMResponse:
        raise LLMError(self.message)
