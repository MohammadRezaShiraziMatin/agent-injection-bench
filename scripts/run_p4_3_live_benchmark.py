#!/usr/bin/env python3
"""Controlled P4.3 live benchmark (Target then Judge; raw artifacts on disk)."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

P43_ROOT = ROOT / "data" / "episodes_p4_3"
OUT_BASE = ROOT / "results" / "p4_3_live"
GATE_PATH = ROOT / "config" / "p4_3_live_eval_gate.v1.json"
METRICS_PATH = ROOT / "config" / "p4_3_evaluation_metrics.v1.json"
EVIDENCE_PATH = ROOT / "artifacts" / "openrouter_model_lock_evidence.json"

from agent.config import describe_openrouter_config, load_openrouter_config_for_role  # noqa: E402
from agent.result_mapper import map_live_result  # noqa: E402
from agent.harness_meta import EXECUTION_MODE_LIVE, HARNESS_VERSION  # noqa: E402
from agent.judge import run_judge  # noqa: E402
from agent.loop import SYSTEM_PROMPT, run_episode  # noqa: E402
from agent.model_lock import load_live_eval_gate  # noqa: E402
from scripts.live_eval_preflight import run_preflight  # noqa: E402
from scripts.verify_live_approval import verify_live_approval  # noqa: E402
from scripts.verify_model_lock import verify_model_lock  # noqa: E402


def _sha256_text(t: str) -> str:
    return hashlib.sha256(t.encode()).hexdigest()


def _git_head() -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return (proc.stdout or "").strip() or "unknown"


def _iter_episodes() -> list[dict[str, Any]]:
    paths = sorted((P43_ROOT / "attack").glob("*.json")) + sorted(
        (P43_ROOT / "benign").glob("*.json")
    )
    return [json.loads(p.read_text(encoding="utf-8")) for p in paths]


def _gates_ok() -> tuple[bool, dict[str, Any]]:
    lock = verify_model_lock()
    pre = run_preflight()
    appr = verify_live_approval()
    ok = (
        lock.get("MODEL_LOCK_STATUS") == "LOCKED"
        and pre.get("preflight_ok")
        and appr.get("ok")
    )
    return ok, {"model_lock": lock, "preflight": pre, "approval": appr}


def run_benchmark(*, run_id: str | None = None) -> dict[str, Any]:
    ok, gate_report = _gates_ok()
    if not ok:
        return {"ok": False, "live_run": "BLOCKED", "gates": gate_report}

    gate = load_live_eval_gate()
    manifest = json.loads((P43_ROOT / "MANIFEST.json").read_text(encoding="utf-8"))
    digest = manifest["digest_sha256"]
    run_id = run_id or f"p43-live-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    out_dir = OUT_BASE / run_id
    for sub in ("episodes", "target_traces", "judge_outputs"):
        (out_dir / sub).mkdir(parents=True, exist_ok=True)

    target_cfg = load_openrouter_config_for_role("target")
    judge_cfg = load_openrouter_config_for_role("judge")
    or_desc = describe_openrouter_config()
    secret_status = "AVAILABLE" if or_desc.get("api_key") == "present" else "MISSING"

    run_manifest: dict[str, Any] = {
        "run_id": run_id,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "dataset_version": "P4.3",
        "dataset_digest": digest,
        "git_commit": _git_head(),
        "harness_version": HARNESS_VERSION,
        "evaluation_mode": EXECUTION_MODE_LIVE,
        "target_model": target_cfg.model,
        "judge_model": judge_cfg.model,
        "target_provider": target_cfg.provider,
        "judge_provider": judge_cfg.provider,
        "secret_status": secret_status,
        "config_hash_sha256": _sha256_text(json.dumps(gate, sort_keys=True)),
        "system_prompt_hash_sha256": _sha256_text(SYSTEM_PROMPT),
        "metrics_contract": str(METRICS_PATH.relative_to(ROOT)),
        "catalog_evidence": str(EVIDENCE_PATH.relative_to(ROOT)),
        "seed": gate.get("generation", {}).get("seed"),
        "upstream_weight_revision": "UNVERIFIED",
        "episode_ids": [],
        "gates_at_start": gate_report,
    }
    (out_dir / "RUN_MANIFEST.json").write_text(
        json.dumps(run_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    episodes = _iter_episodes()
    results: list[dict[str, Any]] = []
    for ep in episodes:
        ep_id = ep["id"]
        run_manifest["episode_ids"].append(ep_id)
        ep_dir = out_dir / "episodes"
        t0 = time.time()
        try:
            target_out = run_episode(ep, config=target_cfg, write=False)
        except Exception as exc:  # noqa: BLE001
            record = {
                "schema_version": "p43.v1",
                "protocol_version": "P4.3-LIVE-1",
                "dataset_version": "P4.3",
                "dataset_digest": digest,
                "episode_id": ep_id,
                "pair_id": ep.get("pair_id"),
                "split": ep.get("split"),
                "run_id": run_id,
                "target_model": target_cfg.model,
                "judge_model": judge_cfg.model,
                "expected_success_criterion": (ep.get("expected") or {}).get(
                    "success_criterion"
                ),
                "observed_success_level": None,
                "attack_success": None,
                "utility_success": None,
                "tool_proposed": False,
                "tool_executed": False,
                "external_side_effect_observed": False,
                "judge_status": "SKIPPED",
                "error_status": f"MODEL_FAILURE: {type(exc).__name__}",
                "evaluation_mode": EXECUTION_MODE_LIVE,
                "latency_ms": int((time.time() - t0) * 1000),
            }
            results.append(record)
            (ep_dir / f"{ep_id}.json").write_text(json.dumps(record, indent=2) + "\n")
            continue

        trace = target_out["trace"]
        eval_h = target_out.get("evaluation_result") or {}
        judge_out = run_judge(
            ep,
            target_final_answer=trace.get("final_answer"),
            tool_proposals=trace.get("tool_proposals") or [],
            execution_trace=trace.get("execution_trace") or [],
            harness_observed_level=(target_out.get("evaluation_result") or {}).get(
                "observed_success_level", "S0"
            ),
            config=judge_cfg,
        )
        (out_dir / "target_traces" / f"{ep_id}.json").write_text(
            json.dumps(trace, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        (out_dir / "judge_outputs" / f"{ep_id}.json").write_text(
            json.dumps(judge_out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )

        parsed = (judge_out.get("parsed") or {}) if judge_out.get("status") == "ok" else {}
        judge_status = judge_out.get("status", "JUDGE_FAILURE")
        error_status = "completed" if judge_status == "ok" else "JUDGE_FAILURE"
        mapped = map_live_result(ep, trace, parsed, judge_status=judge_status)
        forbidden = set((ep.get("expected") or {}).get("forbidden_tools") or [])
        proposed = trace.get("tool_proposals") or []
        tool_proposed = bool(proposed)
        tool_executed = any(ev.get("execution_completed") for ev in trace.get("execution_trace") or [])

        expected_crit = (ep.get("expected") or {}).get("success_criterion", "S0")

        record = {
            "schema_version": "p43.v1",
            "protocol_version": "P4.3-LIVE-1",
            "dataset_version": "P4.3",
            "dataset_digest": digest,
            "episode_id": ep_id,
            "pair_id": ep.get("pair_id"),
            "split": ep.get("split"),
            "run_id": run_id,
            "target_model": target_cfg.model,
            "judge_model": judge_cfg.model,
            "target_provider": target_cfg.provider,
            "judge_provider": judge_cfg.provider,
            "expected_success_criterion": expected_crit,
            "observed_success_level": mapped["observed_success_level"],
            "harness_observed_success_level": mapped["harness_observed_success_level"],
            "judge_observed_success_level": mapped.get("judge_observed_success_level"),
            "attack_success": mapped["attack_success"],
            "utility_success": mapped["utility_success"],
            "tool_proposed": tool_proposed,
            "forbidden_tool_proposed": mapped["forbidden_tool_proposed"],
            "tool_executed": tool_executed,
            "forbidden_tools": list(forbidden),
            "forbidden_tool_executed": mapped["forbidden_tool_executed"],
            "external_side_effect_observed": mapped["external_side_effect_observed"],
            "s4_status": mapped["s4_status"],
            "mapper_policy": mapped.get("mapper_policy"),
            "judge_status": judge_status,
            "error_status": error_status,
            "evaluation_mode": EXECUTION_MODE_LIVE,
            "execution_trace": trace.get("execution_trace"),
            "latency_ms": int((time.time() - t0) * 1000),
        }
        results.append(record)
        (ep_dir / f"{ep_id}.json").write_text(
            json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )

    run_manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
    run_manifest["n_episodes"] = len(results)
    (out_dir / "RUN_MANIFEST.json").write_text(
        json.dumps(run_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (out_dir / "RESULTS.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return {
        "ok": True,
        "live_run": "COMPLETED",
        "run_id": run_id,
        "out_dir": str(out_dir.relative_to(ROOT)),
        "n_episodes": len(results),
        "secret_status": secret_status,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()
    report = run_benchmark(run_id=args.run_id)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
