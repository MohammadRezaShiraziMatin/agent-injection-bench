#!/usr/bin/env python3
"""Offline Level B Phase 4 prelive gate (lock/freeze; live fail-closed)."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GATE_PATH = ROOT / "config" / "level_b_live_eval_gate.v1.json"
APPROVAL_PATH = ROOT / "artifacts" / "level_b_phase4_execution_approval.json"
MANIFEST_PATH = ROOT / "artifacts" / "level_b_primary_d0_d2_experiment" / "MANIFEST.json"
PROTOCOL_FREEZE_PATH = ROOT / "config" / "level_b_protocol_freeze.v1.json"
MODEL_MATRIX_PATH = ROOT / "config" / "level_b_model_matrix.v1.json"
LEVEL_B_CATALOG_EVIDENCE_PATH = ROOT / "artifacts" / "level_b_openrouter_model_lock_evidence.json"
ADAPTIGUARD_PIN_PATH = ROOT / "config" / "adaptiguard_version_pin.v1.json"

P42_DIGEST = "4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee"
AG_SHA = "30ddc756a07e3eae1f9afd5a3e9b9c68a7017f64"

PRELIVE_STATUSES = {"AWAITING_KEY", "NOT_AUTHORIZED", "KEY_RECEIVED_PENDING_AUTH"}
LIVE_STATUSES = {"EXPLICIT", "AUTHORIZED", "AUTHORIZED_FOR_EXECUTION"}
PRELIVE_MANIFEST_STATUSES = {"DRAFT_NOT_FROZEN", "FROZEN"}


def _manifest_list_hash(manifest: dict[str, Any]) -> str:
    pool = manifest.get("primary_attack_pool") or {}
    payload = {
        "attack_episode_ids": sorted(pool.get("attack_episode_ids") or []),
        "benign_episode_ids": sorted(pool.get("benign_episode_ids") or []),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _second_target_locked(matrix: dict[str, Any]) -> bool:
    for row in matrix.get("rows") or []:
        if row.get("role") == "target" and row.get("lock_status") == "LOCKED":
            return True
    return False


def _validate_level_b_catalog_chain(gate: dict[str, Any], matrix: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    catalog_ref = gate.get("catalog_evidence")
    if catalog_ref != "artifacts/level_b_openrouter_model_lock_evidence.json":
        issues.append("gate_level_b_catalog_evidence_path_missing_or_wrong")
    second = (gate.get("target_models") or {}).get("second_family_locked") or {}
    if second.get("exact_model_id") != "google/gemini-2.5-flash":
        issues.append("gate_second_target_model_id_mismatch")
    if second.get("status") != "LOCKED":
        issues.append("gate_second_target_not_locked")
    snap = second.get("immutable_snapshot") or {}
    if not snap.get("catalog_entry_sha256"):
        issues.append("gate_second_target_catalog_fingerprint_missing")

    locked_row = None
    for row in matrix.get("rows") or []:
        if row.get("row_id") == "target-candidate-family-b":
            locked_row = row
            break
    if not locked_row or locked_row.get("lock_status") != "LOCKED":
        issues.append("matrix_second_target_not_locked")
    elif locked_row.get("model_id") != "google/gemini-2.5-flash":
        issues.append("matrix_second_target_model_id_mismatch")
    elif locked_row.get("catalog_lock_evidence") != catalog_ref:
        issues.append("matrix_catalog_lock_evidence_mismatch")

    if not LEVEL_B_CATALOG_EVIDENCE_PATH.is_file():
        issues.append("level_b_catalog_evidence_missing")
        return issues

    evidence = json.loads(LEVEL_B_CATALOG_EVIDENCE_PATH.read_text(encoding="utf-8"))
    mid = "google/gemini-2.5-flash"
    entry = (evidence.get("models") or {}).get(mid) or {}
    if entry.get("catalog_entry_sha256") != snap.get("catalog_entry_sha256"):
        issues.append("gate_catalog_fingerprint_not_in_evidence_file")
    if entry.get("tool_calling_supported") is not True:
        issues.append("second_target_tool_calling_not_supported_in_evidence")
    return issues


def verify_level_b_phase4_prelive_gate(
    gate_path: Path = GATE_PATH,
    approval_path: Path = APPROVAL_PATH,
    manifest_path: Path = MANIFEST_PATH,
    protocol_freeze_path: Path = PROTOCOL_FREEZE_PATH,
    model_matrix_path: Path = MODEL_MATRIX_PATH,
) -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = []

    if not gate_path.is_file():
        issues.append("level_b_live_gate_missing")
        gate: dict[str, Any] = {}
    else:
        gate = json.loads(gate_path.read_text(encoding="utf-8"))
        preflight = gate.get("preflight") or {}
        if preflight.get("live_inference_allowed") is True:
            issues.append("gate_live_inference_allowed_true_without_prep_complete")
        gate_ref = preflight.get("live_approval_artifact")
        if gate_ref and gate_ref != "artifacts/level_b_phase4_execution_approval.json":
            issues.append("gate_approval_artifact_mismatch")

    if not approval_path.is_file():
        issues.append("level_b_approval_missing")
        approval: dict[str, Any] = {}
    else:
        approval = json.loads(approval_path.read_text(encoding="utf-8"))
        if approval.get("authorized") is True:
            issues.append("approval_authorized_true")
        status = approval.get("status")
        if status in LIVE_STATUSES:
            issues.extend(_validate_claimed_live_authorization(approval, gate))
        elif status not in PRELIVE_STATUSES:
            issues.append(f"approval_status_unexpected:{status!r}")

    if not manifest_path.is_file():
        issues.append("population_manifest_missing")
        manifest: dict[str, Any] = {}
    else:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_status = manifest.get("status")
        if manifest_status not in PRELIVE_MANIFEST_STATUSES:
            if (approval.get("status") or "") not in LIVE_STATUSES:
                issues.append(f"manifest_status_unexpected_in_prelive:{manifest_status!r}")
        if manifest.get("live_execution") is True:
            issues.append("manifest_live_execution_true")
        pool = manifest.get("primary_attack_pool") or {}
        n_atk = len(pool.get("attack_episode_ids") or [])
        if n_atk <= 9:
            issues.append("candidate_attack_count_not_gt_9")
        recorded = manifest.get("draft_list_content_sha256")
        computed = _manifest_list_hash(manifest)
        if recorded != computed:
            issues.append("manifest_draft_list_hash_mismatch")
        scope = approval.get("scope") or {}
        if scope.get("draft_list_content_sha256") and scope["draft_list_content_sha256"] != computed:
            issues.append("approval_manifest_hash_mismatch")

    if protocol_freeze_path.is_file():
        freeze = json.loads(protocol_freeze_path.read_text(encoding="utf-8"))
        if freeze.get("status") != "DESIGN_NOT_FROZEN":
            if (approval.get("status") or "") not in LIVE_STATUSES:
                issues.append("protocol_freeze_not_design_in_prelive")
    else:
        issues.append("level_b_protocol_freeze_missing")

    matrix: dict[str, Any] = {}
    if model_matrix_path.is_file():
        matrix = json.loads(model_matrix_path.read_text(encoding="utf-8"))
        if matrix.get("authorization") != "NOT_AUTHORIZED":
            issues.append("model_matrix_must_remain_not_authorized_in_prelive")
        for row in matrix.get("rows") or []:
            if row.get("lock_status") == "CANDIDATE_NOT_LOCKED" and row.get("role") == "target":
                warnings.append("second_target_family_still_candidate")
        if manifest.get("status") == "FROZEN" and not _second_target_locked(matrix):
            issues.append("frozen_manifest_requires_second_target_locked")
        if _second_target_locked(matrix) and gate:
            issues.extend(_validate_level_b_catalog_chain(gate, matrix))
    else:
        issues.append("level_b_model_matrix_missing")

    if ADAPTIGUARD_PIN_PATH.is_file():
        pin = json.loads(ADAPTIGUARD_PIN_PATH.read_text(encoding="utf-8"))
        if pin.get("commit_sha") != AG_SHA:
            issues.append("adaptiguard_pin_sha_mismatch")
    else:
        issues.append("adaptiguard_pin_missing")

    prelive_ok = not issues
    live_would_run = _would_allow_live_inference(approval, gate, manifest, os.environ)
    mode = "PRELIVE_DRAFT_AWAITING_KEY"
    if manifest.get("status") == "FROZEN" and _second_target_locked(matrix):
        mode = "PRELIVE_LOCKED_FROZEN_AWAITING_LIVE_APPROVAL"

    return {
        "LEVEL_B_PHASE4_PRELIVE_GATE": "PASS" if prelive_ok else "FAIL",
        "ok": prelive_ok,
        "mode": mode,
        "live_inference_allowed": False,
        "live_would_run_if_invoked_now": live_would_run,
        "issues": issues,
        "warnings": warnings,
        "approval_status": approval.get("status"),
        "manifest_status": manifest.get("status"),
        "candidate_attack_count": len((manifest.get("primary_attack_pool") or {}).get("attack_episode_ids") or []),
        "dataset_digest_p4_2": P42_DIGEST,
        "note": "PASS means offline prep scaffolding only; do not execute live Level B runs.",
    }


def _validate_claimed_live_authorization(approval: dict[str, Any], gate: dict[str, Any]) -> list[str]:
    """Fail closed when approval claims live-ready status without a complete chain."""
    issues: list[str] = []
    req = approval.get("required_fields_for_authorization") or {}
    for field in ("operator", "approved_at_utc", "git_commit"):
        key = "approver" if field == "operator" else "approved_at" if field == "approved_at_utc" else "git_commit_at_authorization"
        if not approval.get(key):
            issues.append(f"missing_{key}_for_live_status")

    preflight = gate.get("preflight") or {}
    if preflight.get("live_inference_allowed") is not True:
        issues.append("gate_live_inference_not_enabled_for_claimed_authorization")

    scope = approval.get("scope") or {}
    if scope.get("dataset_manifest_hash") and scope["dataset_manifest_hash"] != P42_DIGEST:
        issues.append("dataset_digest_not_p42")
    if scope.get("adaptiguard_pin") and AG_SHA not in str(scope.get("adaptiguard_pin")):
        issues.append("adaptiguard_pin_not_recorded_in_scope")

    manifest_path = ROOT / "artifacts" / "level_b_primary_d0_d2_experiment" / "MANIFEST.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("status") != "FROZEN":
            issues.append("population_manifest_not_frozen_for_live_status")

    if MODEL_MATRIX_PATH.is_file():
        matrix = json.loads(MODEL_MATRIX_PATH.read_text(encoding="utf-8"))
        for row in matrix.get("rows") or []:
            if row.get("role") == "target" and row.get("lock_status") == "CANDIDATE_NOT_LOCKED":
                issues.append("model_matrix_second_target_still_candidate")

    if not req:
        issues.append("required_fields_for_authorization_block_missing")
    return issues


def _would_allow_live_inference(
    approval: dict[str, Any],
    gate: dict[str, Any],
    manifest: dict[str, Any],
    environ: dict[str, str],
) -> bool:
    preflight = gate.get("preflight") or {}
    if not preflight.get("live_inference_allowed"):
        return False
    if approval.get("authorized") is not True:
        return False
    if approval.get("status") not in LIVE_STATUSES:
        return False
    if manifest.get("status") != "FROZEN":
        return False
    for flag in preflight.get("required_env_flags_for_live") or []:
        if "=" in flag:
            name, value = flag.split("=", 1)
            if environ.get(name) != value:
                return False
        elif not environ.get(flag):
            return False
    return True


def main() -> int:
    report = verify_level_b_phase4_prelive_gate()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
