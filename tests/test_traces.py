from __future__ import annotations

from pathlib import Path

from agent.config import LLMConfig
from agent.llm import LLMResponse, ScriptedLLM
from agent.load import load_episode
from agent.loop import run_episode
from agent.traces import (
    TRACE_KEY_ORDER,
    default_trace_path,
    empty_trace,
    order_trace,
    write_trace,
)
from scripts._common import load_json


def test_empty_trace_has_required_keys(attack_example: Path) -> None:
    episode = load_episode(attack_example)
    trace = empty_trace(
        episode,
        model="m",
        provider="p",
        base_url="https://example.test/v1",
        max_steps=6,
        timestamp="2026-01-01T00:00:00Z",
    )
    for key in (
        "episode_id",
        "episode",
        "episode_type",
        "model",
        "provider",
        "timestamp",
        "git_head",
        "user_task",
        "retrieved_documents",
        "tool_calls",
        "final_answer",
        "execution_status",
        "status",
        "error",
        "prompt_id",
        "temperature",
        "seed",
        "latency_ms",
        "tokens",
        "run_id",
    ):
        assert key in trace
    assert trace["episode_type"] == "attack"
    assert trace["split"] == "attack"
    assert trace["status"] == trace["execution_status"]
    assert trace["latency_ms"] is None
    assert trace["tokens"] is None
    assert trace["retrieved_documents"][0]["doc_id"]
    assert "attack_success" not in trace
    assert "utility_success" not in trace


def test_live_scripted_trace_records_latency_and_null_tokens_without_usage(
    attack_example: Path,
) -> None:
    episode = load_episode(attack_example)
    client = ScriptedLLM([LLMResponse(content="ok")])
    config = LLMConfig(api_key="x", base_url="https://llm.test/v1", model="scripted")
    trace = run_episode(episode, client=client, config=config)
    assert trace["execution_status"] == "ok"
    assert trace["status"] == "ok"
    assert isinstance(trace["latency_ms"], (int, float))
    assert trace["latency_ms"] >= 0
    # ScriptedLLM has no provider usage → tokens must remain null (not estimated).
    assert trace["tokens"] is None
    assert "git_head" in trace


def test_extract_usage_only_when_present() -> None:
    from agent.llm import extract_usage, parse_chat_completion

    assert extract_usage(None) is None
    assert extract_usage({"usage": {}}) is None
    usage = extract_usage(
        {"usage": {"prompt_tokens": 3, "completion_tokens": 2, "total_tokens": 5}}
    )
    assert usage == {"prompt_tokens": 3, "completion_tokens": 2, "total_tokens": 5}
    parsed = parse_chat_completion(
        {
            "choices": [{"message": {"content": "hi", "tool_calls": []}}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        }
    )
    assert parsed.usage == {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}


def test_write_trace_roundtrip(attack_example: Path, tmp_path: Path) -> None:
    episode = load_episode(attack_example)
    client = ScriptedLLM([LLMResponse(content="Tuesday 14:00")])
    config = LLMConfig(
        api_key="x",
        base_url="https://llm.test/v1",
        model="scripted-model",
    )
    trace = run_episode(episode, client=client, config=config)
    path = default_trace_path("atk_001", tmp_path)
    write_trace(trace, path)
    loaded = load_json(path)
    assert loaded["episode_id"] == "atk_001"
    assert loaded["final_answer"] == "Tuesday 14:00"
    assert loaded["execution_status"] == "ok"
    assert "run_id" in loaded
    assert loaded["prompt_id"] == "d0"
    assert list(order_trace(loaded).keys())[:5] == list(TRACE_KEY_ORDER[:5])
