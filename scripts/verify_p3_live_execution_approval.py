#!/usr/bin/env python3
"""Verify explicit P3-EXT COV-B live-eval approval artifact and gate wiring (offline)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPROVAL_PATH = ROOT / "artifacts" / "p3_live_execution_approval.json"
GATE_PATH = ROOT / "config" / "p4_3_d2_eval_gate.v1.json"
P42_DIGEST = "4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee"
AG_SHA = "30ddc756a07e3eae1f9afd5a3e9b9c68a7017f64"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.p4_3_paired_common import load_p3_cov_b_extension_run_config  # noqa: E402


def _p3_preflight(gate: dict) -> dict:
    return gate.get("p3_ext_preflight") or {}


def _validate_scope(doc: dict) -> tuple[bool, list[str]]:
    scope = doc.get("scope") or {}
    issues: list[str] = []
    if doc.get("status") != "EXPLICIT":
        issues.append("status_not_explicit")
    try:
        cfg = load_p3_cov_b_extension_run_config()
    except (FileNotFoundError, ValueError, KeyError) as exc:
        issues.append(f"p3_config:{exc}")
        return False, issues
    if scope.get("dataset_digest") != P42_DIGEST:
        issues.append("digest_mismatch")
    if sorted(scope.get("primary_attack_ids") or []) != sorted(cfg["primary_attack_ids"]):
        issues.append("attack_ids_mismatch")
    if sorted(scope.get("benign_episode_ids") or []) != sorted(cfg["utility_fpr_benign_episode_ids"]):
        issues.append("benign_ids_mismatch")
    if scope.get("adaptiguard_commit") != AG_SHA:
        issues.append("adaptiguard_sha_mismatch")
    if scope.get("dataset_version") != "P4.2":
        issues.append("dataset_version")
    if scope.get("output_root") != "results/p3_paired/":
        issues.append("output_root")
    if scope.get("coverage_class_attacks") != "COV-B":
        issues.append("coverage_class")
    if scope.get("population_label") != "P3-EXT":
        issues.append("population_label")
    if scope.get("episode_count") != 84:
        issues.append("episode_count")
    return not issues, issues


def verify_p3_live_execution_approval() -> dict:
    gate = json.loads(GATE_PATH.read_text(encoding="utf-8")) if GATE_PATH.is_file() else {}
    p3_pf = _p3_preflight(gate)
    gate_allowed = bool(p3_pf.get("live_d2_inference_allowed", False))
    gate_ref = p3_pf.get("live_d2_approval_artifact")

    if not APPROVAL_PATH.is_file():
        return {
            "P3_LIVE_EXECUTION_APPROVAL": "MISSING",
            "ok": False,
            "scope_ok": False,
            "live_d2_inference_allowed_in_p3_gate": gate_allowed,
            "gate_approval_artifact": gate_ref,
        }

    doc = json.loads(APPROVAL_PATH.read_text(encoding="utf-8"))
    scope_ok, issues = _validate_scope(doc)
    path_ok = gate_ref is None or gate_ref == str(APPROVAL_PATH.relative_to(ROOT))
    ok = scope_ok and path_ok and gate_allowed
    return {
        "P3_LIVE_EXECUTION_APPROVAL": "EXPLICIT" if ok else "BLOCKED",
        "ok": ok,
        "scope_ok": scope_ok,
        "path_ok": path_ok,
        "approval_id": doc.get("approval_id"),
        "approved_at": doc.get("approved_at"),
        "issues": issues,
        "live_d2_inference_allowed_in_p3_gate": gate_allowed,
        "gate_approval_artifact": gate_ref,
    }


def main() -> int:
    report = verify_p3_live_execution_approval()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
