from __future__ import annotations

import json
from pathlib import Path

from agent.execution_context import EpisodeExecutionContext
from agent.harness_coverage import compare_before_after
from agent.harness_meta import (
    EXECUTION_MODE_EXPLICIT_UNSUPPORTED,
    EXECUTION_MODE_STATIC_REPLAY,
    HARNESS_VERSION,
)
from agent.load import load_episode
from agent.loop import run_episode
from agent.surface_adapters import (
    ADAPTIVE_HEADER,
    CROSS_CONTEXT_HEADER,
    TOOL_RESULTS_HEADER,
    build_initial_messages,
)

ROOT = Path(__file__).resolve().parents[1]
P42 = ROOT / "data" / "episodes_p4_2"


def _p42(episode_id: str) -> dict:
    for split in ("attack", "benign"):
        path = P42 / split / f"{episode_id}.json"
        if path.is_file():
            return load_episode(path)
    raise FileNotFoundError(episode_id)


def test_tool_results_not_merged_into_user_query():
    ep = _p42("atk_p42_055")
    ctx = EpisodeExecutionContext.from_episode(ep)
    messages = build_initial_messages(ep, ctx)
    assert len(messages) >= 1
    final = messages[-1]["content"]
    assert TOOL_RESULTS_HEADER in final
    assert "User request:" in final
    assert ep["injection"]["payload"] in final
    assert final.index(TOOL_RESULTS_HEADER) < final.index("User request:")


def test_conversation_replay_preserves_turn_order():
    ep = _p42("atk_p42_070")
    ctx = EpisodeExecutionContext.from_episode(ep)
    messages = build_initial_messages(ep, ctx)
    roles = [m["role"] for m in messages[:-1]]
    assert roles == ["user", "assistant", "user", "assistant"]
    assert messages[-1]["role"] == "user"
    rec = ctx.provenance_dict()
    assert any(r["surface"] == "conversation" and r["applied"] for r in rec)


def test_cross_context_distinct_from_user_query():
    ep = _p42("atk_p42_085")
    ctx = EpisodeExecutionContext.from_episode(ep)
    messages = build_initial_messages(ep, ctx)
    body = messages[-1]["content"]
    assert CROSS_CONTEXT_HEADER in body
    assert ep["user_query"] in body
    assert body.index(CROSS_CONTEXT_HEADER) < body.index("User request:")


def test_inter_agent_explicit_unsupported_mode():
    ep = _p42("atk_p42_093")
    ctx = EpisodeExecutionContext.from_episode(ep)
    build_initial_messages(ep, ctx)
    ia = [r for r in ctx.provenance_dict() if r["surface"] == "inter_agent_messages"][0]
    assert ia["execution_mode"] == EXECUTION_MODE_EXPLICIT_UNSUPPORTED


def test_adaptive_static_replay_header():
    ep = _p42("atk_p42_097")
    ctx = EpisodeExecutionContext.from_episode(ep)
    messages = build_initial_messages(ep, ctx)
    assert ADAPTIVE_HEADER in messages[-1]["content"]
    ad = [r for r in ctx.provenance_dict() if r["surface"] == "adaptive_trace"][0]
    assert ad["execution_mode"] == EXECUTION_MODE_STATIC_REPLAY


def test_episode_isolation_memory_store():
    a = _p42("atk_p42_076")
    b = _p42("ben_p42_076")
    ca = EpisodeExecutionContext.from_episode(a)
    cb = EpisodeExecutionContext.from_episode(b)
    assert ca.memory_store != cb.memory_store


def test_dry_run_includes_harness_metadata(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    ep = _p42("atk_p42_055")
    out = run_episode(ep, dry_run=True, write=False)
    trace = out["trace"]
    assert trace["harness_execution"]["harness_version"] == HARNESS_VERSION
    assert out["evaluation_result"]["episode_id"] == "atk_p42_055"
    side = out["evaluation_result"]["side_effect"]
    assert side["external_side_effect_occurred"] is False
    assert side["s4_external_claimable"] is False


def test_coverage_improves_without_dataset_edit():
    report = compare_before_after()
    before = report["before"]["executability"]
    after = report["after"]["executability"]
    assert before["EXECUTABLE"] == 68
    assert before["PARTIALLY_EXECUTABLE"] == 116
    assert before["DESIGNED_NOT_EXECUTABLE"] == 16
    assert after["EXECUTABLE"] == 172
    assert after["PARTIALLY_EXECUTABLE"] == 16
    assert after["DESIGNED_NOT_EXECUTABLE"] == 12


def test_p42_digest_unchanged():
    manifest = json.loads((P42 / "MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["digest_sha256"] == "4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee"
