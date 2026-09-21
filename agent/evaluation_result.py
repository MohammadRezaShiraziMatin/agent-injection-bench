"""Structured evaluation result payload for a harness run (P4.2.4)."""

from __future__ import annotations

from typing import Any

from agent.execution_evidence import analyze_execution_evidence
from agent.harness_meta import HARNESS_VERSION


def build_evaluation_result(
    *,
    episode: dict[str, Any],
    trace: dict[str, Any],
    dataset_digest: str | None = None,
) -> dict[str, Any]:
    harness_exec = trace.get("harness_execution") or {}
    expected = episode.get("expected") or {}
    execution_trace = trace.get("execution_trace") or []
    tool_proposals = trace.get("tool_proposals") or [
        {"tool": tc.get("tool"), "arguments": tc.get("arguments")}
        for tc in trace.get("tool_calls") or []
    ]
    evidence = analyze_execution_evidence(
        tool_proposals=tool_proposals,
        execution_trace=execution_trace,
        final_answer=trace.get("final_answer"),
        forbidden_tools=expected.get("forbidden_tools"),
        allowed_tools=expected.get("allowed_tools"),
    )
    external = any(ev.get("external_side_effect_occurred") for ev in execution_trace)
    side_effect_summary = {
        "external_side_effect_occurred": external,
        "sandbox_side_effect_only": evidence.get("sandbox_side_effect_only", False),
        "s4_external_claimable": evidence.get("s4_external_claimable", False),
        "note": (
            "external_delivery_not_observed_in_sandbox"
            if not external
            else "external_side_effect_recorded"
        ),
    }
    return {
        "episode_id": episode.get("id"),
        "dataset_version": episode.get("dataset_version"),
        "dataset_digest": dataset_digest,
        "harness_version": HARNESS_VERSION,
        "evaluation_mode": harness_exec.get("evaluation_mode") or harness_exec.get("execution_mode"),
        "execution_mode": harness_exec.get("execution_mode"),
        "surface_provenance": harness_exec.get("surface_provenance", []),
        "executability_authored": (episode.get("execution") or {}).get("executability"),
        "executability_harness": harness_exec.get("executability_harness"),
        "target_model": trace.get("model"),
        "target_snapshot": trace.get("provider"),
        "observed_response": trace.get("final_answer"),
        "tool_proposal": tool_proposals,
        "tool_execution": trace.get("tool_calls"),
        "execution_trace": execution_trace,
        "observed_success_level": evidence.get("observed_success_level"),
        "side_effect": side_effect_summary,
        "status": trace.get("status"),
        "failure_reason": trace.get("error"),
    }
