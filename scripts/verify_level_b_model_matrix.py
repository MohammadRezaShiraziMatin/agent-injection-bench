#!/usr/bin/env python3
"""Offline Level B model matrix verifier (structure, lock invariants; no API calls)."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "config" / "level_b_model_matrix.v1.json"
LEVEL_A_GATE_PATH = ROOT / "config" / "p4_3_live_eval_gate.v1.json"
PROTOCOL_FREEZE_PATH = ROOT / "config" / "level_b_protocol_freeze.v1.json"
LEVEL_B_GATE_PATH = ROOT / "config" / "level_b_live_eval_gate.v1.json"
LEVEL_B_CATALOG_EVIDENCE_PATH = ROOT / "artifacts" / "level_b_openrouter_model_lock_evidence.json"

ROW_REQUIRED = (
    "role",
    "family",
    "model_id",
    "provider",
    "temperature",
    "max_tokens",
    "cache_policy",
    "notes",
    "lock_status",
)

ROLES = {"target", "judge"}
LOCK_STATUSES = {"CANDIDATE_NOT_LOCKED", "INHERITS_LEVEL_A", "LOCKED"}
EXECUTION_STATUSES = {"LOCKED", "FROZEN", "AUTHORIZED", "AUTHORIZED_FOR_EXECUTION"}
APPROVAL_FIELDS = (
    "researcher_sign_off",
    "approved_at_utc",
    "authorization_artifact",
)


def _canonical_fingerprint(doc: dict[str, Any]) -> str:
    payload = {k: v for k, v in doc.items() if k != "content_fingerprint_sha256"}
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def verify_level_b_model_matrix(
    matrix_path: Path = MATRIX_PATH,
    gate_path: Path = LEVEL_A_GATE_PATH,
    protocol_freeze_path: Path = PROTOCOL_FREEZE_PATH,
) -> dict[str, Any]:
    issues: list[str] = []

    if not matrix_path.is_file():
        return {"ok": False, "issues": ["matrix config missing"], "MATRIX_VERIFY_STATUS": "FAIL"}

    doc = json.loads(matrix_path.read_text(encoding="utf-8"))
    status = doc.get("status")
    authorization = doc.get("authorization")

    for key in ("matrix_id", "status", "authorization", "protocol_doc", "rows"):
        if key not in doc:
            issues.append(f"missing top-level field: {key}")

    rows = doc.get("rows")
    if not isinstance(rows, list) or not rows:
        issues.append("rows must be a non-empty list")
        rows = []

    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            issues.append(f"rows[{i}] must be object")
            continue
        for field in ROW_REQUIRED:
            if field not in row:
                issues.append(f"rows[{i}] missing {field}")
        role = row.get("role")
        if role not in ROLES:
            issues.append(f"rows[{i}] invalid role: {role!r}")
        lock_status = row.get("lock_status")
        if lock_status not in LOCK_STATUSES:
            issues.append(f"rows[{i}] invalid lock_status: {lock_status!r}")

    fp = doc.get("content_fingerprint_sha256")
    computed = _canonical_fingerprint(doc)
    if not fp:
        issues.append("content_fingerprint_sha256 missing")
    elif fp != computed:
        issues.append(
            f"content_fingerprint_sha256 drift: expected {computed} got {fp}"
        )

    status_upper = str(status or "").upper()
    auth_upper = str(authorization or "").upper()
    claims_execution = status_upper in EXECUTION_STATUSES or auth_upper in {
        "AUTHORIZED",
        "AUTHORIZED_FOR_EXECUTION",
        "LOCKED",
        "FROZEN",
    }
    if claims_execution:
        missing_approval = [f for f in APPROVAL_FIELDS if not doc.get(f)]
        if missing_approval:
            issues.append(
                "status/authorization claims lock or execution without approval fields: "
                + ", ".join(missing_approval)
            )

    target_families = {
        r.get("family")
        for r in rows
        if isinstance(r, dict)
        and r.get("role") == "target"
        and r.get("lock_status") != "CANDIDATE_NOT_LOCKED"
    }
    target_families.discard(None)

    if status_upper in {"LOCKED", "FROZEN"}:
        if len(target_families) < 2:
            issues.append(
                f"LOCKED/FROZEN matrix requires >=2 non-candidate target families; got {len(target_families)}"
            )

    if gate_path.is_file():
        gate = json.loads(gate_path.read_text(encoding="utf-8"))
        target_id = (gate.get("target_model") or {}).get("exact_model_id")
        judge_id = (gate.get("judge_model") or {}).get("exact_model_id")
        for row in rows:
            if not isinstance(row, dict):
                continue
            if row.get("lock_status") != "INHERITS_LEVEL_A":
                continue
            mid = row.get("model_id")
            role = row.get("role")
            if role == "target" and target_id and mid != target_id:
                issues.append(
                    f"Level A target drift: matrix {mid!r} != gate {target_id!r}"
                )
            if role == "judge" and judge_id and mid != judge_id:
                issues.append(
                    f"Level A judge drift: matrix {mid!r} != gate {judge_id!r}"
                )
    else:
        issues.append("Level A gate missing for inheritance cross-check")

    if protocol_freeze_path.is_file():
        freeze = json.loads(protocol_freeze_path.read_text(encoding="utf-8"))
        inherited = (freeze.get("inherits_read_only") or {}).get("level_b_model_matrix")
        if inherited != str(matrix_path.relative_to(ROOT)).replace("\\", "/"):
            issues.append(
                "level_b_protocol_freeze inherits_read_only.level_b_model_matrix mismatch"
            )
        freeze_status = (freeze.get("status") or "").upper()
        if freeze_status in {"FROZEN", "LOCKED"}:
            claim = (freeze.get("claim_class") or freeze.get("statistics") or "").upper()
            if claim != "DESCRIPTIVE_ONLY":
                issues.append("protocol freeze FROZEN requires claim_class/statistics DESCRIPTIVE_ONLY")
        elif freeze_status not in {"DESIGN_NOT_FROZEN", ""}:
            issues.append(f"unexpected protocol freeze status: {freeze.get('status')!r}")

    if LEVEL_B_GATE_PATH.is_file():
        lb_gate = json.loads(LEVEL_B_GATE_PATH.read_text(encoding="utf-8"))
        second = (lb_gate.get("target_models") or {}).get("second_family_locked") or {}
        locked_rows = [
            r
            for r in rows
            if isinstance(r, dict)
            and r.get("role") == "target"
            and r.get("lock_status") == "LOCKED"
        ]
        for row in locked_rows:
            mid = row.get("model_id")
            if second.get("exact_model_id") and mid != second.get("exact_model_id"):
                issues.append(
                    f"Level B gate second target drift: matrix {mid!r} != gate {second.get('exact_model_id')!r}"
                )
            evidence_ref = row.get("catalog_lock_evidence") or lb_gate.get("catalog_evidence")
            if evidence_ref and evidence_ref != lb_gate.get("catalog_evidence"):
                issues.append("locked target catalog_lock_evidence != level_b gate catalog_evidence")
            if LEVEL_B_CATALOG_EVIDENCE_PATH.is_file() and evidence_ref:
                rel = str(LEVEL_B_CATALOG_EVIDENCE_PATH.relative_to(ROOT)).replace("\\", "/")
                if evidence_ref != rel:
                    issues.append("catalog_lock_evidence path must match artifacts file")
                evidence = json.loads(LEVEL_B_CATALOG_EVIDENCE_PATH.read_text(encoding="utf-8"))
                entry = (evidence.get("models") or {}).get(mid or "") or {}
                snap = second.get("immutable_snapshot") or {}
                if snap.get("catalog_entry_sha256") and entry.get("catalog_entry_sha256"):
                    if snap["catalog_entry_sha256"] != entry["catalog_entry_sha256"]:
                        issues.append("gate catalog fingerprint != level_b catalog evidence")

    matrix_ok = len(issues) == 0
    return {
        "ok": matrix_ok,
        "issues": issues,
        "MATRIX_VERIFY_STATUS": "PASS" if matrix_ok else "FAIL",
        "matrix_id": doc.get("matrix_id"),
        "status": status,
        "authorization": authorization,
        "n_rows": len(rows),
        "target_families_non_candidate": sorted(target_families),
        "content_fingerprint_sha256": computed,
        "live_execution_authorized": (
            str(authorization or "").upper() == "AUTHORIZED_FOR_DESCRIPTIVE_LIVE"
            and protocol_freeze_path.is_file()
            and (json.loads(protocol_freeze_path.read_text(encoding="utf-8")).get("status") or "").upper()
            == "FROZEN"
        ),
    }


def main() -> int:
    report = verify_level_b_model_matrix()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
