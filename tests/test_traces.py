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
        "episode_type",
        "model",
        "provider",
        "timestamp",
        "user_task",
        "retrieved_documents",
        "tool_calls",
        "final_answer",
        "execution_status",
        "error",
    ):
        assert key in trace
    assert trace["episode_type"] == "attack"
    assert trace["split"] == "attack"
    assert trace["retrieved_documents"][0]["doc_id"]
    assert "attack_success" not in trace
    assert "utility_success" not in trace


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
