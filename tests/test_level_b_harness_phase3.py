"""Offline Phase 3 harness: D0 passthrough, D2 hook indices, sandbox permissions."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from agent.defense.hook_trace import HOOK_PRE_TARGET, HOOK_PRE_TOOL_CALL, TRACE_SCHEMA_VERSION
from agent.defense.middleware import apply_defense_at_hook
from agent.defense.types import DefenseAction, DefenseApplyResult, DefenseCondition, DefenseEvent
from agent.load import load_episode_by_id
from agent.loop import run_episode
from agent.tools import call_tool
from tools.execution_recorder import clear_recorder, get_recorder
from tools.tool_sandbox import get_sandbox, reset_sandbox


def _fake_adaptiguard(**kwargs: object) -> DefenseApplyResult:
    ev = DefenseEvent(
        defense_enabled=True,
        defense_backend="adaptiguard",
        detector_invoked=True,
        detector_result="clean",
        risk_score=0.0,
        risk_level="low",
        decision=DefenseAction.ALLOW.value,
        block=False,
        transform_applied=False,
        reason="test_stub",
        category=None,
        latency_ms=0,
        defense_error=False,
        integration_status="INTEGRATED",
    )
    return DefenseApplyResult(messages=list(kwargs["messages"]), event=ev)  # type: ignore[arg-type]


def test_d0_passthrough_at_pre_target():
    ep = {"user_query": "hi", "retrieved_docs": [], "expected": {}}
    res = apply_defense_at_hook(
        condition=DefenseCondition.D0,
        episode=ep,
        messages=[{"role": "user", "content": "hi"}],
        hook_point=HOOK_PRE_TARGET,
        tool_step_index=-1,
        dry_run=True,
    )
    ev = res.event.to_dict()
    assert ev["defense_enabled"] is False
    assert ev["decision"] == "allow"
    assert ev["extra"]["hook_point"] == HOOK_PRE_TARGET
    assert ev["extra"]["tool_step_index"] == -1


def test_d2_dry_run_records_pre_target_hook_trace():
    ep = load_episode_by_id("atk_002")
    out = run_episode(ep, dry_run=True, write=False, defense_condition=DefenseCondition.D2)
    hx = out["trace"]["harness_execution"]
    assert hx["trace_schema_version"] == TRACE_SCHEMA_VERSION
    assert hx["hook_coverage_map"]["pre_target"]["covered"] is True
    assert hx["hook_coverage_map"]["pre_target"]["tool_step_indices"] == [-1]
    assert len(hx["defense_trace"]) >= 1
    assert hx["defense_trace"][0]["tool_step_index"] == -1


def test_sandbox_blocks_forbidden_send_email():
    ep = load_episode_by_id("atk_002")
    clear_recorder()
    reset_sandbox(ep)
    out = call_tool(
        "send_email",
        {"to": "x@example.invalid", "subject": "s", "body": "b"},
        docs=ep.get("retrieved_docs", []),
    )
    assert out["ok"] is False
    assert "forbidden" in out["error"]
    sb = get_sandbox()
    assert sb.call_log[-1]["executed"] is False
    trace = get_recorder().to_trace()
    assert trace[-1]["blocked"] is True


def test_d2_tool_loop_records_pre_tool_step_indices():
    ep = load_episode_by_id("ben_002")
    reset_sandbox(ep)

    mock_tool_call = MagicMock()
    mock_tool_call.id = "call_1"
    mock_tool_call.function.name = "search_docs"
    mock_tool_call.function.arguments = '{"query": "policy"}'

    msg_no_tools = MagicMock()
    msg_no_tools.content = "done"
    msg_no_tools.tool_calls = None

    msg_with_tool = MagicMock()
    msg_with_tool.content = ""
    msg_with_tool.tool_calls = [mock_tool_call]

    choice_final = MagicMock()
    choice_final.message = msg_no_tools
    choice_tool = MagicMock()
    choice_tool.message = msg_with_tool

    resp_tool = MagicMock()
    resp_tool.choices = [choice_tool]
    resp_final = MagicMock()
    resp_final.choices = [choice_final]

    cfg = MagicMock()
    cfg.configured = True
    cfg.model = "test-model"
    cfg.base_url = "http://offline.test"

    with (
        patch("agent.defense.middleware.integration_status", return_value={"integrated": True}),
        patch("agent.defense.middleware.apply_adaptiguard", side_effect=_fake_adaptiguard),
        patch("agent.loop.LLMClient") as client_cls,
    ):
        client = client_cls.return_value
        client.chat.side_effect = [resp_tool, resp_final]
        out = run_episode(
            ep,
            config=cfg,
            dry_run=False,
            write=False,
            defense_condition=DefenseCondition.D2,
        )

    hx = out["trace"]["harness_execution"]
    pre_tool = hx["hook_coverage_map"]["pre_tool_call"]
    assert pre_tool["covered"] is True
    assert pre_tool["tool_step_indices"] == [1]
    step_events = [r for r in hx["defense_trace"] if r["hook_point"] == HOOK_PRE_TOOL_CALL]
    assert len(step_events) == 1
    assert step_events[0]["tool_step_index"] == 1
    assert step_events[0]["defense_event"]["extra"]["tool_step_index"] == 1
    assert hx["tool_sandbox"]["call_log"]


def test_verify_level_b_harness_phase3_script():
    from scripts.verify_level_b_harness_phase3 import verify_level_b_harness_phase3

    report = verify_level_b_harness_phase3()
    assert report["ok"] is True
