#!/usr/bin/env python3
"""P4.3 paired D0 vs D2 benchmark (dry-run default; live gated)."""

from __future__ import annotations

import argparse
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
OUT_BASE = ROOT / "results" / "p4_3_paired"
GATE_PATH = ROOT / "config" / "p4_3_live_eval_gate.v1.json"
D2_GATE_PATH = ROOT / "config" / "p4_3_d2_eval_gate.v1.json"
CONTRACT_PATH = ROOT / "config" / "p4_3_paired_eval_contract.v1.json"
METRICS_PATH = ROOT / "config" / "p4_3_evaluation_metrics.v1.json"
EVIDENCE_PATH = ROOT / "artifacts" / "openrouter_model_lock_evidence.json"

from agent.config import describe_openrouter_config, load_openrouter_config_for_role  # noqa: E402
from agent.defense.adaptiguard_bridge import integration_status  # noqa: E402
from agent.defense.types import DefenseCondition  # noqa: E402
from agent.harness_meta import EXECUTION_MODE_LIVE, HARNESS_VERSION  # noqa: E402
from agent.judge import run_judge  # noqa: E402
from agent.loop import SYSTEM_PROMPT, run_episode  # noqa: E402
from agent.model_lock import load_live_eval_gate  # noqa: E402
from agent.result_mapper import map_live_result  # noqa: E402
from scripts.live_eval_preflight import run_preflight  # noqa: E402
from scripts.p4_3_paired_common import build_result_record, iter_episodes, sha256_text  # noqa: E402
from scripts.verify_d2_integration import verify_d2_integration  # noqa: E402
from scripts.verify_d2_live_approval import verify_d2_live_approval  # noqa: E402
from scripts.verify_live_approval import verify_live_approval  # noqa: E402
from scripts.verify_model_lock import verify_model_lock  # noqa: E402


def _git_head() -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return (proc.stdout or "").strip() or "unknown"


def _integrity_ok() -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "verify_p4_3_integrity.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        return json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return {"ok": False, "parse_error": True, "stderr": proc.stderr}


def _live_gates_ok() -> tuple[bool, dict[str, Any]]:
    lock = verify_model_lock()
    pre = run_preflight()
    appr = verify_live_approval()
    d2 = verify_d2_integration()
    d2_appr = verify_d2_live_approval()
    integrity = _integrity_ok()
    ok = (
        integrity.get("ok")
        and lock.get("MODEL_LOCK_STATUS") == "LOCKED"
        and pre.get("preflight_ok")
        and appr.get("ok")
        and d2.get("ok")
        and d2_appr.get("ok")
    )
    return ok, {
        "integrity": integrity,
        "model_lock": lock,
        "preflight": pre,
        "live_approval": appr,
        "d2_integration": d2,
        "d2_live_approval": d2_appr,
    }


def _dry_run_gates_ok() -> tuple[bool, dict[str, Any]]:
    integrity = _integrity_ok()
    lock = verify_model_lock()
    ok = bool(integrity.get("ok")) and lock.get("MODEL_LOCK_STATUS") == "LOCKED"
    return ok, {"integrity": integrity, "model_lock": lock, "mode": "dry_run"}


def _evaluate_episode(
    ep: dict[str, Any],
    *,
    condition: DefenseCondition,
    run_id: str,
    digest: str,
    target_cfg: Any,
    judge_cfg: Any,
    dry_run: bool,
    out_cond_dir: Path,
) -> dict[str, Any]:
    ep_id = ep["id"]
    t0 = time.time()
    cond_label = condition.value
    try:
        target_out = run_episode(
            ep,
            config=target_cfg,
            write=False,
            dry_run=dry_run,
            defense_condition=condition,
        )
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "record": {
                "episode_id": ep_id,
                "pair_id": ep.get("pair_id"),
                "condition": cond_label,
                "run_id": run_id,
                "error_status": f"MODEL_OR_DEFENSE_FAILURE: {type(exc).__name__}",
                "judge_status": "SKIPPED",
            },
            "judge_called": False,
        }

    trace = target_out["trace"]
    defense_event = target_out.get("defense_event")
    if dry_run:
        parsed: dict[str, Any] = {}
        judge_status = "SKIPPED"
        mapped = map_live_result(ep, trace, parsed, judge_status="SKIPPED")
    else:
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
        (out_cond_dir / "target_traces" / f"{ep_id}.json").write_text(
            json.dumps(trace, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        (out_cond_dir / "judge_outputs" / f"{ep_id}.json").write_text(
            json.dumps(judge_out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        parsed = (judge_out.get("parsed") or {}) if judge_out.get("status") == "ok" else {}
        judge_status = judge_out.get("status", "JUDGE_FAILURE")
        mapped = map_live_result(ep, trace, parsed, judge_status=judge_status)

    record = build_result_record(
        ep=ep,
        run_id=run_id,
        digest=digest,
        condition=cond_label,
        target_cfg=target_cfg,
        judge_cfg=judge_cfg,
        trace=trace,
        mapped=mapped,
        judge_status=judge_status,
        defense_event=defense_event,
        latency_ms=int((time.time() - t0) * 1000),
    )
    if dry_run:
        record["error_status"] = "dry_run"
        record["judge_status"] = "SKIPPED"
    (out_cond_dir / "episodes" / f"{ep_id}.json").write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if defense_event and cond_label == "D2" and not dry_run:
        dtrace = {
            "episode_id": ep_id,
            "condition": cond_label,
            "defense_event": defense_event,
            "adaptiguard_trace": (defense_event.get("extra") or {}).get("adaptiguard_policy_action"),
        }
        trace_path = out_cond_dir / "defense_traces" / f"{ep_id}.json"
        trace_path.write_text(json.dumps(dtrace, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"ok": True, "record": record, "judge_called": judge_status != "SKIPPED"}


def run_paired(*, run_id: str | None = None, dry_run: bool = True) -> dict[str, Any]:
    if dry_run:
        ok, gate_report = _dry_run_gates_ok()
        if not ok:
            return {"ok": False, "paired_run": "BLOCKED", "mode": "dry_run", "gates": gate_report}
    else:
        ok, gate_report = _live_gates_ok()
        if not ok:
            return {"ok": False, "paired_run": "BLOCKED", "mode": "live", "gates": gate_report}

    gate = load_live_eval_gate()
    d2_gate = json.loads(D2_GATE_PATH.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    manifest = json.loads((P43_ROOT / "MANIFEST.json").read_text(encoding="utf-8"))
    digest = manifest["digest_sha256"]
    run_id = run_id or (
        f"p43-d0-d2-dry-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        if dry_run
        else f"p43-d0-d2-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-controlled"
    )
    out_dir = OUT_BASE / run_id
    d0_dir = out_dir / "D0"
    d2_dir = out_dir / "D2"
    paired_dir = out_dir / "paired"
    defense_traces_root = out_dir / "defense_traces"
    defense_traces_root.mkdir(parents=True, exist_ok=True)
    for base in (d0_dir, d2_dir, paired_dir):
        for sub in ("episodes", "target_traces", "judge_outputs", "defense_traces"):
            (base / sub).mkdir(parents=True, exist_ok=True)

    target_cfg = load_openrouter_config_for_role("target")
    judge_cfg = load_openrouter_config_for_role("judge")
    or_desc = describe_openrouter_config()
    secret_status = "AVAILABLE" if or_desc.get("api_key") == "present" else "MISSING"

    integ = integration_status()
    run_manifest: dict[str, Any] = {
        "run_id": run_id,
        "mode": "dry_run" if dry_run else "live",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "dataset_version": "P4.3",
        "dataset_digest": digest,
        "git_commit": _git_head(),
        "harness_version": HARNESS_VERSION,
        "evaluation_mode": "DRY_RUN" if dry_run else EXECUTION_MODE_LIVE,
        "target_model": target_cfg.model,
        "judge_model": judge_cfg.model,
        "target_provider": target_cfg.provider,
        "judge_provider": judge_cfg.provider,
        "secret_status": secret_status,
        "config_hash_sha256": sha256_text(json.dumps(gate, sort_keys=True)),
        "d2_gate_hash_sha256": sha256_text(json.dumps(d2_gate, sort_keys=True)),
        "paired_contract": str(CONTRACT_PATH.relative_to(ROOT)),
        "system_prompt_hash_sha256": sha256_text(SYSTEM_PROMPT),
        "metrics_contract": str(METRICS_PATH.relative_to(ROOT)),
        "catalog_evidence": str(EVIDENCE_PATH.relative_to(ROOT)),
        "seed": gate.get("generation", {}).get("seed"),
        "upstream_weight_revision": "UNVERIFIED",
        "defense_integration": integ,
        "episode_order_policy": contract.get("paired_protocol", {}).get("order_policy"),
        "gates_at_start": gate_report,
    }

    episodes = iter_episodes()
    d0_results: list[dict[str, Any]] = []
    d2_results: list[dict[str, Any]] = []
    pairs: list[dict[str, Any]] = []
    target_api_calls = 0
    judge_api_calls = 0

    for ep in episodes:
        pair_id = ep.get("pair_id") or ep["id"]
        d0_eval = _evaluate_episode(
            ep,
            condition=DefenseCondition.D0,
            run_id=run_id,
            digest=digest,
            target_cfg=target_cfg,
            judge_cfg=judge_cfg,
            dry_run=dry_run,
            out_cond_dir=d0_dir,
        )
        d2_eval = _evaluate_episode(
            ep,
            condition=DefenseCondition.D2,
            run_id=run_id,
            digest=digest,
            target_cfg=target_cfg,
            judge_cfg=judge_cfg,
            dry_run=dry_run,
            out_cond_dir=d2_dir,
        )
        d0_results.append(d0_eval["record"])
        d2_results.append(d2_eval["record"])
        for ev in (d0_eval, d2_eval):
            rec = ev.get("record") or {}
            de = rec.get("defense_event") or {}
            if rec.get("error_status") == "completed":
                if de.get("defense_enabled"):
                    if (de.get("extra") or {}).get("target_reached"):
                        target_api_calls += 1
                else:
                    target_api_calls += 1
            if ev.get("judge_called"):
                judge_api_calls += 1
        de2 = d2_eval["record"].get("defense_event") or {}
        if de2.get("defense_enabled") and not dry_run:
            (defense_traces_root / f"{ep['id']}.json").write_text(
                json.dumps(
                    {
                        "episode_id": ep["id"],
                        "defense_event": de2,
                        "target_reached": (de2.get("extra") or {}).get("target_reached"),
                    },
                    indent=2,
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
        pairs.append(
            {
                "pair_id": pair_id,
                "episode_id": ep["id"],
                "input_hash_sha256": d0_eval["record"].get("input_hash_sha256"),
                "d0_error_status": d0_eval["record"].get("error_status"),
                "d2_error_status": d2_eval["record"].get("error_status"),
                "d0_defense_event": d0_eval["record"].get("defense_event"),
                "d2_defense_event": d2_eval["record"].get("defense_event"),
            }
        )
        (paired_dir / "episodes" / f"{ep['id']}.json").write_text(
            json.dumps(pairs[-1], indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )

    run_manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
    run_manifest["n_episodes"] = len(episodes)
    run_manifest["episode_ids"] = [e["id"] for e in episodes]
    run_manifest["target_api_calls"] = target_api_calls
    run_manifest["judge_api_calls"] = judge_api_calls
    run_manifest["adaptiguard_commit"] = integ.get("commit")

    (out_dir / "RUN_MANIFEST.json").write_text(
        json.dumps(run_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (d0_dir / "RESULTS.json").write_text(
        json.dumps(d0_results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (d2_dir / "RESULTS.json").write_text(
        json.dumps(d2_results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (paired_dir / "PAIRED_INDEX.json").write_text(
        json.dumps(pairs, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    combined = d0_results + d2_results
    (out_dir / "RESULTS.json").write_text(
        json.dumps(combined, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    return {
        "ok": True,
        "paired_run": "COMPLETED",
        "mode": "dry_run" if dry_run else "live",
        "run_id": run_id,
        "out_dir": str(out_dir.relative_to(ROOT)),
        "n_episodes": len(episodes),
        "secret_status": secret_status,
        "d2_integration": integ.get("status"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--live", action="store_true", help="Live inference (all gates required)")
    args = parser.parse_args()
    report = run_paired(run_id=args.run_id, dry_run=not args.live)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
