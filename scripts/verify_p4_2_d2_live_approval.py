#!/usr/bin/env python3
"""Verify explicit P4.2 primary D2 live-eval approval artifact and gate wiring (offline)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPROVAL_PATH = ROOT / "artifacts" / "p4_2_d2_live_approval.json"
P43_APPROVAL = ROOT / "artifacts" / "p4_3_d2_live_approval.json"
GATE_PATH = ROOT / "config" / "p4_3_d2_eval_gate.v1.json"
P42_DIGEST = "4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee"
AG_SHA = "30ddc756a07e3eae1f9afd5a3e9b9c68a7017f64"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.p4_3_paired_common import load_p42_primary_run_config  # noqa: E402


def _load_gate() -> dict:
    if not GATE_PATH.is_file():
        return {}
    return json.loads(GATE_PATH.read_text(encoding="utf-8"))


def _p42_preflight(gate: dict) -> dict:
    return gate.get("p4_2_primary_preflight") or {}


def _validate_scope(doc: dict) -> tuple[bool, list[str]]:
    scope = doc.get("scope") or {}
    issues: list[str] = []
    if doc.get("status") != "EXPLICIT":
        issues.append("status_not_explicit")
    try:
        cfg = load_p42_primary_run_config()
    except (FileNotFoundError, ValueError, KeyError) as exc:
        issues.append(f"primary_config:{exc}")
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
    if scope.get("output_root") != "results/p4_2_paired/":
        issues.append("output_root")
    p43_digest = "e60969bee257ec3111febf215fb5f7079edb79ed050dae300e549336184ab53d"
    if scope.get("dataset_digest") == p43_digest:
        issues.append("p4_3_digest_in_scope")
    if P43_APPROVAL.is_file():
        p43 = json.loads(P43_APPROVAL.read_text(encoding="utf-8"))
        if doc.get("approval_id") == p43.get("approval_id"):
            issues.append("reused_p4_3_approval_id")
    return not issues, issues


def verify_p4_2_d2_live_approval() -> dict:
    gate = _load_gate()
    p42_pf = _p42_preflight(gate)
    gate_allowed = bool(p42_pf.get("live_d2_inference_allowed", False))
    gate_ref = p42_pf.get("live_d2_approval_artifact")

    if not APPROVAL_PATH.is_file():
        return {
            "P4_2_D2_LIVE_APPROVAL": "MISSING",
            "ok": False,
            "scope_ok": False,
            "live_d2_inference_allowed_in_p42_gate": gate_allowed,
            "gate_approval_artifact": gate_ref,
        }

    doc = json.loads(APPROVAL_PATH.read_text(encoding="utf-8"))
    scope_ok, issues = _validate_scope(doc)
    path_ok = gate_ref is None or gate_ref == str(APPROVAL_PATH.relative_to(ROOT))
    ok = scope_ok and path_ok and gate_allowed
    return {
        "P4_2_D2_LIVE_APPROVAL": "EXPLICIT" if ok else "BLOCKED",
        "ok": ok,
        "scope_ok": scope_ok,
        "path_ok": path_ok,
        "approval_id": doc.get("approval_id"),
        "approved_at": doc.get("approved_at"),
        "issues": issues,
        "live_d2_inference_allowed_in_p42_gate": gate_allowed,
        "gate_approval_artifact": gate_ref,
        "p4_3_global_gate_unchanged": gate.get("preflight", {}).get("live_d2_inference_allowed"),
    }


def main() -> int:
    report = verify_p4_2_d2_live_approval()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report.get("scope_ok") else 1


if __name__ == "__main__":
    sys.exit(main())
