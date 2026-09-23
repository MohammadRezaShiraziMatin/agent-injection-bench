#!/usr/bin/env python3
"""Verify Target/Judge model lock evidence (offline; no chat inference)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE_PATH = ROOT / "config" / "p4_3_live_eval_gate.v1.json"
LEVEL_B_GATE_PATH = ROOT / "config" / "level_b_live_eval_gate.v1.json"
EVIDENCE_PATH = ROOT / "artifacts" / "openrouter_model_lock_evidence.json"
LEVEL_B_EVIDENCE_PATH = ROOT / "artifacts" / "level_b_openrouter_model_lock_evidence.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.config import describe_openrouter_config  # noqa: E402


def _gate() -> dict:
    return json.loads(GATE_PATH.read_text(encoding="utf-8"))


def _evidence() -> dict | None:
    if not EVIDENCE_PATH.is_file():
        return None
    return json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))


def _snapshot_ok(role_block: dict, evidence: dict | None) -> bool:
    snap = role_block.get("immutable_snapshot") or {}
    mid = role_block.get("exact_model_id")
    if not mid or not snap.get("catalog_entry_sha256"):
        return False
    if snap.get("catalog_entry_sha256") != (role_block.get("immutable_snapshot") or {}).get(
        "catalog_entry_sha256"
    ):
        return False
    if not evidence:
        return False
    ev = (evidence.get("models") or {}).get(mid)
    if not ev:
        return False
    return ev.get("catalog_entry_sha256") == snap.get("catalog_entry_sha256")


def _routing_ok(role_block: dict) -> bool:
    pol = role_block.get("routing_policy") or {}
    return bool(pol.get("provider_order")) and pol.get("allow_fallbacks") is False


def _lock_report(
    *,
    target: dict,
    judge: dict,
    target_evidence: dict | None,
    judge_evidence: dict | None,
    catalog_evidence_path: Path,
    live_inference_allowed: bool,
    extra: dict | None = None,
) -> dict:
    env = describe_openrouter_config()
    target_id = target.get("exact_model_id")
    judge_id = judge.get("exact_model_id")
    distinct = bool(target_id and judge_id and target_id != judge_id)

    env_target = env.get("target_model")
    env_judge = env.get("judge_model")
    api_ok = env.get("api_key") == "present"

    target_locked = target.get("status") == "LOCKED"
    g2 = bool(target_id and target_locked)
    if env_target and env_target != target_id:
        g2 = False

    judge_locked = judge.get("status") == "LOCKED"
    g3 = bool(judge_id and judge_locked)
    if env_judge and env_judge != judge_id:
        g3 = False

    fallbacks_ok = env.get("allow_fallbacks") is False
    g4 = (
        distinct
        and _snapshot_ok(target, target_evidence)
        and _snapshot_ok(judge, judge_evidence)
        and fallbacks_ok
        and _routing_ok(target)
        and _routing_ok(judge)
    )

    env_matches = (
        env_target == target_id
        and env_judge == judge_id
        and bool(env_target)
        and bool(env_judge)
    )
    g10 = g2 and g3 and g4 and api_ok and env_matches

    if g2 and g3 and g4 and g10:
        status = "LOCKED"
    elif g2 and g3 and distinct:
        status = "PARTIALLY_LOCKED"
    else:
        status = "BLOCKED"

    report = {
        "MODEL_LOCK_STATUS": status,
        "gates": {
            "G2_target_identity": "PASS" if g2 else "FAIL",
            "G3_judge_identity": "PASS" if g3 else "FAIL",
            "G4_immutable_catalog_snapshot": "PASS" if g4 else "FAIL",
            "G10_live_eval_readiness": "PASS" if g10 else "FAIL",
        },
        "target_model_id": target_id,
        "judge_model_id": judge_id,
        "env_target_model_id": env_target,
        "env_judge_model_id": env_judge,
        "target_ne_judge": distinct,
        "allow_fallbacks": env.get("allow_fallbacks"),
        "provider_routing_env": env.get("provider_routing"),
        "api_key_present": api_ok,
        "catalog_evidence_path": str(catalog_evidence_path.relative_to(ROOT)),
        "upstream_weight_revision": "UNVERIFIED",
        "live_inference_allowed": status == "LOCKED" and live_inference_allowed,
    }
    if extra:
        report.update(extra)
    return report


def _load_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def verify_level_b_model_lock(matrix_row_id: str) -> dict:
    """Matrix-aware model lock for Level B descriptive live (offline; no inference)."""
    from scripts.p4_3_paired_common import load_level_b_matrix_target_row

    row = load_level_b_matrix_target_row(matrix_row_id)
    lock_status = row.get("lock_status")
    extra = {
        "level_b_matrix_row_id": matrix_row_id,
        "level_b_lock_mode": lock_status,
    }

    if lock_status == "INHERITS_LEVEL_A":
        report = verify_model_lock()
        report.update(extra)
        return report

    if lock_status != "LOCKED":
        return {
            "MODEL_LOCK_STATUS": "BLOCKED",
            "gates": {
                "G2_target_identity": "FAIL",
                "G3_judge_identity": "FAIL",
                "G4_immutable_catalog_snapshot": "FAIL",
                "G10_live_eval_readiness": "FAIL",
            },
            "target_model_id": row.get("model_id"),
            "judge_model_id": None,
            "env_target_model_id": describe_openrouter_config().get("target_model"),
            "env_judge_model_id": describe_openrouter_config().get("judge_model"),
            "level_b_matrix_row_id": matrix_row_id,
            "level_b_lock_mode": lock_status,
            "live_inference_allowed": False,
        }

    lb_gate = _load_json(LEVEL_B_GATE_PATH) or {}
    p43_gate = _gate()
    second = (lb_gate.get("target_models") or {}).get("second_family_locked") or {}
    target_id = row.get("model_id")
    if not target_id or second.get("exact_model_id") != target_id:
        extra["level_b_gate_target_mismatch"] = True
        return _lock_report(
            target={"exact_model_id": target_id, "status": "LOCKED"},
            judge=p43_gate.get("judge_model") or {},
            target_evidence=None,
            judge_evidence=_evidence(),
            catalog_evidence_path=LEVEL_B_EVIDENCE_PATH,
            live_inference_allowed=False,
            extra=extra,
        )

    evidence_ref = row.get("catalog_lock_evidence") or lb_gate.get("catalog_evidence")
    evidence_path = ROOT / str(evidence_ref) if evidence_ref else LEVEL_B_EVIDENCE_PATH
    target_evidence = _load_json(evidence_path)
    judge_evidence = _evidence()

    target_block = {
        "exact_model_id": target_id,
        "status": "LOCKED",
        "immutable_snapshot": second.get("immutable_snapshot") or {},
        "routing_policy": second.get("routing_policy") or {},
    }
    judge_block = p43_gate.get("judge_model") or {}
    live_ok = bool((lb_gate.get("preflight") or {}).get("live_inference_allowed", False))

    report = _lock_report(
        target=target_block,
        judge=judge_block,
        target_evidence=target_evidence,
        judge_evidence=judge_evidence,
        catalog_evidence_path=evidence_path,
        live_inference_allowed=live_ok,
        extra=extra,
    )
    report["judge_catalog_evidence_path"] = str(EVIDENCE_PATH.relative_to(ROOT))
    return report


def verify_model_lock() -> dict:
    gate = _gate()
    evidence = _evidence()
    target = gate.get("target_model") or {}
    judge = gate.get("judge_model") or {}
    live_ok = bool((gate.get("preflight") or {}).get("live_inference_allowed", False))
    return _lock_report(
        target=target,
        judge=judge,
        target_evidence=evidence,
        judge_evidence=evidence,
        catalog_evidence_path=EVIDENCE_PATH,
        live_inference_allowed=live_ok,
    )


def main() -> int:
    report = verify_model_lock()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["MODEL_LOCK_STATUS"] == "LOCKED" else 1


if __name__ == "__main__":
    sys.exit(main())
