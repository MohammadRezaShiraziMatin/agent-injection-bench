"""Structured evaluation result payload for a harness run (P4.2.4)."""

from __future__ import annotations

from typing import Any

from agent.harness_meta import HARNESS_VERSION


def build_evaluation_result(
    *,
    episode: dict[str, Any],
    trace: dict[str, Any],
    dataset_digest: str | None = None,
) -> dict[str, Any]:
    harness_exec = trace.get("harness_execution") or {}
    return {
        "episode_id": episode.get("id"),
        "dataset_version": episode.get("dataset_version"),
        "dataset_digest": dataset_digest,
        "harness_version": HARNESS_VERSION,
        "execution_mode": harness_exec.get("execution_mode"),
        "surface_provenance": harness_exec.get("surface_provenance", []),
        "executability_authored": (episode.get("execution") or {}).get("executability"),
        "executability_harness": harness_exec.get("executability_harness"),
        "target_model": trace.get("model"),
        "target_snapshot": trace.get("provider"),
        "observed_response": trace.get("final_answer"),
        "tool_proposal": [
            {"tool": tc.get("tool"), "arguments": tc.get("arguments")}
            for tc in trace.get("tool_calls") or []
        ],
        "tool_execution": trace.get("tool_calls"),
        "side_effect": "none_mock_tools_only",
        "status": trace.get("status"),
        "failure_reason": trace.get("error"),
    }
