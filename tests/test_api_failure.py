from __future__ import annotations

import io
import json
from pathlib import Path
from urllib.error import HTTPError, URLError

from agent.config import LLMConfig
from agent.errors import LLMError
from agent.llm import FailingLLM, OpenAICompatibleClient, parse_chat_completion
from agent.load import load_episode
from agent.loop import run_episode


def _cfg() -> LLMConfig:
    return LLMConfig(
        api_key="test-key",
        base_url="https://llm.test/v1",
        model="fail-model",
    )


def test_failing_client_recorded_on_trace(attack_example: Path) -> None:
    episode = load_episode(attack_example)
    trace = run_episode(episode, client=FailingLLM("simulated API failure"), config=_cfg())
    assert trace["execution_status"] == "error"
    assert trace["error"]["type"] == "LLMError"
    assert "simulated API failure" in trace["error"]["message"]
    assert trace["tool_calls"] == []
    assert "attack_success" not in trace


def test_parse_bad_completion() -> None:
    try:
        parse_chat_completion({"choices": []})
    except LLMError as exc:
        assert "choices[0].message" in str(exc)
    else:
        raise AssertionError("expected LLMError")


def test_http_error_from_provider() -> None:
    def opener(_request, timeout=None):
        raise HTTPError(
            "https://llm.test/v1/chat/completions",
            401,
            "Unauthorized",
            hdrs={},
            fp=io.BytesIO(b'{"error":"nope"}'),
        )

    client = OpenAICompatibleClient(_cfg(), opener=opener)
    try:
        client.complete([{"role": "user", "content": "hi"}], tools=[])
    except LLMError as exc:
        assert "401" in str(exc)
    else:
        raise AssertionError("expected LLMError")


def test_url_error_from_provider() -> None:
    def opener(_request, timeout=None):
        raise URLError("dns fail")

    client = OpenAICompatibleClient(_cfg(), opener=opener)
    try:
        client.complete([{"role": "user", "content": "hi"}], tools=[])
    except LLMError as exc:
        assert "failed" in str(exc).lower()
    else:
        raise AssertionError("expected LLMError")


def test_http_success_parses_tool_call() -> None:
    payload = {
        "choices": [
            {
                "message": {
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "c1",
                            "type": "function",
                            "function": {
                                "name": "search_docs",
                                "arguments": json.dumps({"query": "hours"}),
                            },
                        }
                    ],
                }
            }
        ]
    }

    class _Resp:
        def read(self):
            return json.dumps(payload).encode("utf-8")

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    client = OpenAICompatibleClient(_cfg(), opener=lambda *_a, **_k: _Resp())
    response = client.complete([{"role": "user", "content": "hi"}], tools=[])
    assert response.tool_calls[0].name == "search_docs"
    assert response.tool_calls[0].arguments["query"] == "hours"
