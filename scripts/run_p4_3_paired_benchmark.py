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
from agent.structured_run_log import (  # noqa: E402
    STAGE_AGGREGATION,
    STAGE_DATA_VALIDATION,
    STAGE_EPISODE_EXECUTION,
    STAGE_GATE,
    STAGE_INIT,
    STAGE_MODEL_VALIDATION,
    STAGE_PREFLIGHT,
    STAGE_RUN_START,
    STAGE_VALIDATION,
    StructuredRunLogger,
    sanitize_for_log,
)
from agent.harness_meta import EXECUTION_MODE_LIVE, HARNESS_VERSION  # noqa: E402
from agent.judge import run_judge  # noqa: E402
from agent.loop import SYSTEM_PROMPT, run_episode  # noqa: E402
from agent.model_lock import load_live_eval_gate  # noqa: E402
from agent.result_mapper import map_live_result  # noqa: E402
from scripts.live_eval_preflight import run_preflight  # noqa: E402
from scripts.p4_3_paired_common import (  # noqa: E402
    build_result_record,
    dataset_manifest_digest,
    iter_episodes,
    load_p42_primary_run_config,
    load_p3_cov_b_extension_run_config,
    resolve_benign_pair_refs,
    sha256_text,
)
from scripts.verify_d2_integration import verify_d2_integration  # noqa: E402
from scripts.verify_d2_live_approval import verify_d2_live_approval  # noqa: E402
from scripts.verify_p4_2_d2_live_approval import verify_p4_2_d2_live_approval  # noqa: E402
from scripts.verify_p3_live_execution_approval import verify_p3_live_execution_approval  # noqa: E402
from scripts.verify_live_approval import verify_live_approval  # noqa: E402
from scripts.verify_model_lock import verify_level_b_model_lock, verify_model_lock  # noqa: E402
from scripts.verify_level_b_phase4_prelive_gate import (  # noqa: E402
    MODE_LIVE_AUTHORIZED,
    verify_level_b_phase4_prelive_gate,
)


def _path_ref(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


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
        "live_path": "P4.3",
    }


def _live_gates_ok_p3_ext() -> tuple[bool, dict[str, Any]]:
    lock = verify_model_lock()
    pre = run_preflight()
    appr = verify_live_approval()
    d2 = verify_d2_integration()
    p3_appr = verify_p3_live_execution_approval()
    integrity = _integrity_ok()
    ok = (
        integrity.get("ok")
        and lock.get("MODEL_LOCK_STATUS") == "LOCKED"
        and pre.get("preflight_ok")
        and appr.get("ok")
        and d2.get("ok")
        and p3_appr.get("ok")
    )
    return ok, {
        "integrity": integrity,
        "model_lock": lock,
        "preflight": pre,
        "live_approval": appr,
        "d2_integration": d2,
        "p3_live_execution_approval": p3_appr,
        "live_path": "P3_EXT_COV_B",
    }


def _live_gates_ok_level_b(*, matrix_row_id: str | None = None) -> tuple[bool, dict[str, Any]]:
    if not matrix_row_id:
        return False, {"error": "level_b_matrix_row_id_required"}
    lock = verify_level_b_model_lock(matrix_row_id)
    pre = run_preflight(level_b_matrix_row_id=matrix_row_id)
    d2 = verify_d2_integration()
    integrity = _integrity_ok()
    lb_gate = verify_level_b_phase4_prelive_gate()
    ok = (
        integrity.get("ok")
        and lock.get("MODEL_LOCK_STATUS") == "LOCKED"
        and pre.get("preflight_ok")
        and d2.get("ok")
        and lb_gate.get("ok")
        and lb_gate.get("mode") == MODE_LIVE_AUTHORIZED
        and lb_gate.get("live_inference_allowed")
        and __import__("os").environ.get("AIB_LEVEL_B_LIVE_EXECUTION") == "1"
    )
    return ok, {
        "integrity": integrity,
        "model_lock": lock,
        "preflight": pre,
        "d2_integration": d2,
        "level_b_phase4_gate": lb_gate,
        "live_path": "LEVEL_B_DESCRIPTIVE",
    }


def _live_gates_ok_p42_primary() -> tuple[bool, dict[str, Any]]:
    lock = verify_model_lock()
    pre = run_preflight()
    appr = verify_live_approval()
    d2 = verify_d2_integration()
    p42_appr = verify_p4_2_d2_live_approval()
    integrity = _integrity_ok()
    ok = (
        integrity.get("ok")
        and lock.get("MODEL_LOCK_STATUS") == "LOCKED"
        and pre.get("preflight_ok")
        and appr.get("ok")
        and d2.get("ok")
        and p42_appr.get("ok")
    )
    return ok, {
        "integrity": integrity,
        "model_lock": lock,
        "preflight": pre,
        "live_approval": appr,
        "d2_integration": d2,
        "p4_2_d2_live_approval": p42_appr,
        "live_path": "P4.2_PRIMARY",
    }


def _dry_run_gates_ok(
    *,
    level_b: bool = False,
    matrix_row_id: str | None = None,
) -> tuple[bool, dict[str, Any]]:
    integrity = _integrity_ok()
    if level_b:
        if not matrix_row_id:
            return False, {
                "integrity": integrity,
                "error": "level_b_matrix_row_id_required",
                "mode": "dry_run",
            }
        lock = verify_level_b_model_lock(matrix_row_id)
    else:
        lock = verify_model_lock()
    ok = bool(integrity.get("ok")) and lock.get("MODEL_LOCK_STATUS") == "LOCKED"
    return ok, {"integrity": integrity, "model_lock": lock, "mode": "dry_run"}


def _evaluate_episode(
    ep: dict[str, Any],
    *,
    condition: DefenseCondition,
    run_id: str,
    digest: str,
    dataset_version: str,
    protocol_version: str,
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
        protocol_version=protocol_version,
        dataset_version=dataset_version,
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


def run_paired(
    *,
    run_id: str | None = None,
    dry_run: bool = True,
    dataset_root: Path | None = None,
    dataset_digest: str | None = None,
    episode_ids: list[str] | None = None,
    out_base: Path | None = None,
    dataset_version: str | None = None,
    design_manifest: str | None = None,
    coverage_by_episode: dict[str, dict[str, str]] | None = None,
    protocol_version: str | None = None,
    utility_fpr_benign_scope: Any | None = None,
    primary_attack_ids: list[str] | None = None,
    utility_fpr_benign_episode_ids: list[str] | None = None,
    p42_primary: bool = False,
    p3_ext: bool = False,
    level_b: bool = False,
    matrix_row_id: str | None = None,
) -> dict[str, Any]:
    t_run = time.time()
    ds_root = dataset_root or P43_ROOT
    out_root = out_base or OUT_BASE
    manifest = json.loads((ds_root / "MANIFEST.json").read_text(encoding="utf-8"))
    digest = dataset_digest or manifest["digest_sha256"]
    ds_version = dataset_version or manifest.get("dataset_version", "P4.3")
    proto_version = protocol_version or "P4.3-PAIRED-1"
    run_id = run_id or (
        f"p43-d0-d2-dry-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        if dry_run and ds_root == P43_ROOT
        else (
            f"p42-primary-d0-d2-dry-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
            if dry_run
            else f"p42-primary-d0-d2-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-controlled"
        )
    )
    out_dir = out_root / run_id
    audit = StructuredRunLogger(run_id, out_dir / "AUDIT_TRAIL.jsonl")
    audit.emit(
        STAGE_INIT,
        status="OK",
        mode="dry_run" if dry_run else "live",
        p42_primary=p42_primary,
        p3_ext=p3_ext,
        level_b=level_b,
        matrix_row_id=matrix_row_id,
        dataset_root=str(ds_root.relative_to(ROOT)),
        git_commit=_git_head(),
    )

    if dry_run:
        ok, gate_report = _dry_run_gates_ok(level_b=level_b, matrix_row_id=matrix_row_id)
        audit.emit(STAGE_PREFLIGHT, status="OK" if ok else "FAIL", gates=sanitize_for_log(gate_report))
        if not ok:
            audit.finalize(
                ok=False,
                paired_run="BLOCKED",
                duration_ms=int((time.time() - t_run) * 1000),
                exit_status=1,
                error_taxonomy="PREFLIGHT_GATE_FAIL",
            )
            return {"ok": False, "paired_run": "BLOCKED", "mode": "dry_run", "gates": gate_report}
        if p42_primary:
            p42_appr = verify_p4_2_d2_live_approval()
            gate_report["p4_2_live_readiness"] = {
                "scope_ok": p42_appr.get("scope_ok"),
                "gate_authorized": p42_appr.get("ok"),
                "approval_id": p42_appr.get("approval_id"),
            }
    else:
        if level_b:
            ok, gate_report = _live_gates_ok_level_b(matrix_row_id=matrix_row_id)
        elif p3_ext:
            ok, gate_report = _live_gates_ok_p3_ext()
        elif p42_primary:
            ok, gate_report = _live_gates_ok_p42_primary()
        else:
            ok, gate_report = _live_gates_ok()
        audit.emit(STAGE_PREFLIGHT, status="OK" if ok else "FAIL", gates=sanitize_for_log(gate_report))
        if not ok:
            audit.finalize(
                ok=False,
                paired_run="BLOCKED",
                duration_ms=int((time.time() - t_run) * 1000),
                exit_status=1,
                error_taxonomy="LIVE_GATE_FAIL",
            )
            return {"ok": False, "paired_run": "BLOCKED", "mode": "live", "gates": gate_report}

    gate = load_live_eval_gate()
    d2_gate = json.loads(D2_GATE_PATH.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    manifest_digest = dataset_manifest_digest(ds_root)
    if digest != manifest_digest:
        audit.emit(
            STAGE_DATA_VALIDATION,
            status="FAIL",
            error_taxonomy="DATASET_DIGEST_MISMATCH",
            expected=digest,
            manifest_digest=manifest_digest,
        )
        audit.finalize(
            ok=False,
            paired_run="BLOCKED",
            duration_ms=int((time.time() - t_run) * 1000),
            exit_status=1,
            error_taxonomy="DATASET_DIGEST_MISMATCH",
        )
        return {
            "ok": False,
            "paired_run": "BLOCKED",
            "error": "DATASET_DIGEST_MISMATCH",
            "expected": digest,
            "manifest_digest": manifest_digest,
        }
    audit.emit(
        STAGE_DATA_VALIDATION,
        status="OK",
        dataset_digest=digest,
        dataset_version=ds_version,
    )
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
    gen = gate.get("generation") or {}
    audit.emit(
        STAGE_MODEL_VALIDATION,
        status="OK",
        target_model=target_cfg.model,
        target_provider=target_cfg.provider,
        judge_model=judge_cfg.model,
        judge_provider=judge_cfg.provider,
        seed=gen.get("seed"),
        seed_policy=gen.get("seed_policy"),
        temperature=gen.get("temperature"),
        top_p=gen.get("top_p"),
        secret_status=secret_status,
        upstream_weight_revision="UNVERIFIED",
    )
    audit.emit(
        STAGE_GATE,
        status="OK",
        live_path=(
            "LEVEL_B_DESCRIPTIVE"
            if level_b
            else (
                "P3_EXT_COV_B"
                if p3_ext
                else ("P4.2_PRIMARY" if p42_primary else "P4.3")
            )
        ),
        gates_at_start=sanitize_for_log(gate_report),
    )

    integ = integration_status()
    run_manifest: dict[str, Any] = {
        "run_id": run_id,
        "mode": "dry_run" if dry_run else "live",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "dataset_version": ds_version,
        "dataset_digest": digest,
        "dataset_root": str(ds_root.relative_to(ROOT)),
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
        "gates_at_start": sanitize_for_log(gate_report),
        "audit_trail": _path_ref(out_dir / "AUDIT_TRAIL.jsonl"),
    }
    if design_manifest:
        run_manifest["design_manifest"] = design_manifest
    if coverage_by_episode:
        run_manifest["coverage_by_episode"] = coverage_by_episode
    if utility_fpr_benign_scope is not None:
        run_manifest["utility_fpr_benign_scope"] = utility_fpr_benign_scope
    if primary_attack_ids:
        run_manifest["primary_attack_ids"] = primary_attack_ids
    if utility_fpr_benign_episode_ids:
        run_manifest["utility_fpr_benign_episode_ids"] = utility_fpr_benign_episode_ids
    if level_b:
        run_manifest["live_path"] = "LEVEL_B_DESCRIPTIVE"
        lb_gate = verify_level_b_phase4_prelive_gate()
        run_manifest["level_b_phase4_gate"] = {
            "mode": lb_gate.get("mode"),
            "gate_ok": lb_gate.get("ok"),
            "approval_status": lb_gate.get("approval_status"),
        }
    elif p42_primary:
        run_manifest["live_path"] = "P4.2_PRIMARY"
        p42_appr = verify_p4_2_d2_live_approval()
        run_manifest["p4_2_d2_live_approval"] = {
            "scope_ok": p42_appr.get("scope_ok"),
            "gate_authorized": p42_appr.get("ok"),
            "approval_id": p42_appr.get("approval_id"),
        }
    elif p3_ext:
        run_manifest["live_path"] = "P3_EXT_COV_B"
        p3_appr = verify_p3_live_execution_approval()
        run_manifest["p3_live_execution_approval"] = {
            "scope_ok": p3_appr.get("scope_ok"),
            "gate_authorized": p3_appr.get("ok"),
            "approval_id": p3_appr.get("approval_id"),
        }

    episodes = iter_episodes(dataset_root=ds_root, episode_ids=episode_ids)
    if episode_ids and len(episodes) != len(episode_ids):
        audit.emit(
            STAGE_DATA_VALIDATION,
            status="FAIL",
            error_taxonomy="EPISODE_SELECTION_MISMATCH",
            requested=episode_ids,
            loaded=[e["id"] for e in episodes],
        )
        audit.finalize(
            ok=False,
            paired_run="BLOCKED",
            duration_ms=int((time.time() - t_run) * 1000),
            exit_status=1,
            error_taxonomy="EPISODE_SELECTION_MISMATCH",
        )
        return {
            "ok": False,
            "paired_run": "BLOCKED",
            "error": "EPISODE_SELECTION_MISMATCH",
            "requested": episode_ids,
            "loaded": [e["id"] for e in episodes],
        }
    benign_pair_refs: list[dict[str, str]] = []
    attack_episodes = [e for e in episodes if e.get("split") == "attack"]
    if episode_ids and attack_episodes:
        benign_pair_refs = resolve_benign_pair_refs(ds_root, attack_episodes)
        run_manifest["benign_pair_refs"] = benign_pair_refs
    d0_results: list[dict[str, Any]] = []
    d2_results: list[dict[str, Any]] = []
    pairs: list[dict[str, Any]] = []
    target_api_calls = 0
    judge_api_calls = 0

    audit.emit(
        STAGE_RUN_START,
        status="OK",
        n_episodes=len(episodes),
        harness_version=HARNESS_VERSION,
        config_hash_sha256=sha256_text(json.dumps(gate, sort_keys=True)),
        paired_contract=str(CONTRACT_PATH.relative_to(ROOT)),
        metrics_contract=str(METRICS_PATH.relative_to(ROOT)),
    )

    for ep in episodes:
        ep_t0 = time.time()
        pair_id = ep.get("pair_id") or ep["id"]
        d0_eval = _evaluate_episode(
            ep,
            condition=DefenseCondition.D0,
            run_id=run_id,
            digest=digest,
            dataset_version=ds_version,
            protocol_version=proto_version,
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
            dataset_version=ds_version,
            protocol_version=proto_version,
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
        d0_es = d0_eval["record"].get("error_status")
        d2_es = d2_eval["record"].get("error_status")
        if dry_run:
            ep_status = "OK" if d0_es == d2_es == "dry_run" else "FAIL"
        else:
            ep_status = "OK" if d0_es == d2_es == "completed" else "FAIL"
        audit.emit(
            STAGE_EPISODE_EXECUTION,
            status=ep_status,
            duration_ms=int((time.time() - ep_t0) * 1000),
            episode_id=ep["id"],
            pair_id=pair_id,
            defense_conditions=["D0", "D2"],
            d0_error_status=d0_es,
            d2_error_status=d2_es,
            d0_judge_status=d0_eval["record"].get("judge_status"),
            d2_judge_status=d2_eval["record"].get("judge_status"),
            error_taxonomy="EPISODE_EXECUTION_ERROR" if ep_status == "FAIL" else None,
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

    from scripts.audit_paired_comparability import audit_run  # noqa: E402

    comparability = audit_run(out_dir)
    audit.emit(
        STAGE_VALIDATION,
        status="OK" if comparability.get("comparability_status") == "PASS" else "FAIL",
        comparability_status=comparability.get("comparability_status"),
        issues=comparability.get("issues"),
    )
    audit.emit(
        STAGE_AGGREGATION,
        status="OK",
        n_episodes=len(episodes),
        target_api_calls=target_api_calls,
        judge_api_calls=judge_api_calls,
    )
    duration_ms = int((time.time() - t_run) * 1000)
    audit.finalize(
        ok=True,
        paired_run="COMPLETED",
        duration_ms=duration_ms,
        exit_status=0,
        n_episodes=len(episodes),
    )

    return {
        "ok": True,
        "paired_run": "COMPLETED",
        "mode": "dry_run" if dry_run else "live",
        "run_id": run_id,
        "out_dir": _path_ref(out_dir),
        "n_episodes": len(episodes),
        "secret_status": secret_status,
        "d2_integration": integ.get("status"),
        "audit_trail": _path_ref(out_dir / "AUDIT_TRAIL.jsonl"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--live", action="store_true", help="Live inference (all gates required)")
    parser.add_argument("--dataset-root", type=Path, default=None)
    parser.add_argument("--dataset-digest", default=None)
    parser.add_argument("--episode-id", action="append", dest="episode_ids", default=None)
    parser.add_argument("--out-base", type=Path, default=None)
    parser.add_argument(
        "--p42-primary-config",
        action="store_true",
        help="Use artifacts/p4_2_primary_d0_d2_experiment/MANIFEST.json primary pool",
    )
    parser.add_argument(
        "--p3-cov-b-extension",
        action="store_true",
        help="Use artifacts/p3_cov_b_extension/MANIFEST.json (P3-EXT COV-B; output under results/p3_paired/)",
    )
    args = parser.parse_args()
    kwargs: dict[str, Any] = {
        "run_id": args.run_id,
        "dry_run": not args.live,
    }
    if args.p3_cov_b_extension and args.p42_primary_config:
        raise SystemExit("Use only one of --p42-primary-config or --p3-cov-b-extension")
    if args.p3_cov_b_extension:
        cfg = load_p3_cov_b_extension_run_config()
        kwargs.update(
            {
                "dataset_root": cfg["dataset_root"],
                "dataset_digest": cfg["dataset_digest"],
                "episode_ids": cfg["episode_ids"],
                "out_base": cfg["out_base"],
                "dataset_version": cfg["dataset_version"],
                "design_manifest": cfg["design_manifest"],
                "coverage_by_episode": cfg["coverage_by_episode"],
                "protocol_version": cfg["protocol_version"],
                "utility_fpr_benign_scope": cfg["utility_fpr_benign_scope"],
                "primary_attack_ids": cfg["primary_attack_ids"],
                "utility_fpr_benign_episode_ids": cfg["utility_fpr_benign_episode_ids"],
            }
        )
        if args.run_id is None and kwargs["dry_run"]:
            kwargs["run_id"] = "p3-cov-b-ext-dry-config-v1"
    elif args.p42_primary_config:
        cfg = load_p42_primary_run_config()
        kwargs.update(
            {
                "dataset_root": cfg["dataset_root"],
                "dataset_digest": cfg["dataset_digest"],
                "episode_ids": cfg["episode_ids"],
                "out_base": cfg["out_base"],
                "dataset_version": cfg["dataset_version"],
                "design_manifest": cfg["design_manifest"],
                "coverage_by_episode": cfg["coverage_by_episode"],
                "protocol_version": cfg["protocol_version"],
                "utility_fpr_benign_scope": cfg["utility_fpr_benign_scope"],
                "primary_attack_ids": cfg["primary_attack_ids"],
                "utility_fpr_benign_episode_ids": cfg["utility_fpr_benign_episode_ids"],
            }
        )
        if args.run_id is None and kwargs["dry_run"]:
            kwargs["run_id"] = "p42-primary-d0-d2-dry-config-v1"
    else:
        if args.dataset_root is not None:
            kwargs["dataset_root"] = args.dataset_root
        if args.dataset_digest is not None:
            kwargs["dataset_digest"] = args.dataset_digest
        if args.episode_ids:
            kwargs["episode_ids"] = args.episode_ids
        if args.out_base is not None:
            kwargs["out_base"] = args.out_base
    kwargs["p42_primary"] = bool(args.p42_primary_config)
    kwargs["p3_ext"] = bool(args.p3_cov_b_extension)
    report = run_paired(**kwargs)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
