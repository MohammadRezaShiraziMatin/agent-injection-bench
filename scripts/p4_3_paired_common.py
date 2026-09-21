"""Shared helpers for P4.3 paired D0/D2 evaluation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
P43_ROOT = ROOT / "data" / "episodes_p4_3"


def sha256_text(t: str) -> str:
    return hashlib.sha256(t.encode()).hexdigest()


def input_hash(episode: dict[str, Any]) -> str:
    payload = {
        "id": episode.get("id"),
        "user_query": episode.get("user_query"),
        "retrieved_docs": episode.get("retrieved_docs"),
        "split": episode.get("split"),
    }
    return sha256_text(json.dumps(payload, sort_keys=True, ensure_ascii=False))


def iter_episodes() -> list[dict[str, Any]]:
    paths = sorted((P43_ROOT / "attack").glob("*.json")) + sorted(
        (P43_ROOT / "benign").glob("*.json")
    )
    return [json.loads(p.read_text(encoding="utf-8")) for p in paths]


def build_result_record(
    *,
    ep: dict[str, Any],
    run_id: str,
    digest: str,
    condition: str,
    target_cfg: Any,
    judge_cfg: Any,
    trace: dict[str, Any],
    mapped: dict[str, Any],
    judge_status: str,
    defense_event: dict[str, Any] | None,
    latency_ms: int,
    protocol_version: str = "P4.3-PAIRED-1",
) -> dict[str, Any]:
    forbidden = set((ep.get("expected") or {}).get("forbidden_tools") or [])
    proposed = trace.get("tool_proposals") or []
    tool_executed = any(ev.get("execution_completed") for ev in trace.get("execution_trace") or [])
    expected_crit = (ep.get("expected") or {}).get("success_criterion", "S0")
    error_status = "completed" if judge_status == "ok" else "JUDGE_FAILURE"
    if judge_status == "SKIPPED":
        error_status = "DEFENSE_OR_MODEL_FAILURE"

    return {
        "schema_version": "p43.v1",
        "protocol_version": protocol_version,
        "dataset_version": "P4.3",
        "dataset_digest": digest,
        "episode_id": ep["id"],
        "pair_id": ep.get("pair_id"),
        "split": ep.get("split"),
        "condition": condition,
        "run_id": run_id,
        "input_hash_sha256": input_hash(ep),
        "target_model": target_cfg.model,
        "judge_model": judge_cfg.model,
        "target_provider": getattr(target_cfg, "provider", None),
        "judge_provider": getattr(judge_cfg, "provider", None),
        "expected_success_criterion": expected_crit,
        "observed_success_level": mapped.get("observed_success_level"),
        "harness_observed_success_level": mapped.get("harness_observed_success_level"),
        "judge_observed_success_level": mapped.get("judge_observed_success_level"),
        "attack_success": mapped.get("attack_success"),
        "utility_success": mapped.get("utility_success"),
        "tool_proposed": bool(proposed),
        "forbidden_tool_proposed": mapped.get("forbidden_tool_proposed"),
        "tool_executed": tool_executed,
        "forbidden_tools": list(forbidden),
        "forbidden_tool_executed": mapped.get("forbidden_tool_executed"),
        "external_side_effect_observed": mapped.get("external_side_effect_observed"),
        "s4_status": mapped.get("s4_status"),
        "mapper_policy": mapped.get("mapper_policy"),
        "judge_status": judge_status,
        "error_status": error_status,
        "evaluation_mode": trace.get("harness_execution", {}).get("execution_mode", "LIVE"),
        "execution_trace": trace.get("execution_trace"),
        "defense_event": defense_event,
        "latency_ms": latency_ms,
    }
