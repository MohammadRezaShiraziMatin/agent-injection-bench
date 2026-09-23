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
        if (freeze.get("status") or "").upper() in {"FROZEN", "LOCKED"}:
            issues.append("protocol freeze must remain DESIGN_NOT_FROZEN in Phase 2")

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
        "live_execution_authorized": False,
    }


def main() -> int:
    report = verify_level_b_model_matrix()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
