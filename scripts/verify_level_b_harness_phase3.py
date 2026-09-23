#!/usr/bin/env python3
"""Offline Level B harness Phase 3 contract verifier (no network)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "config" / "level_b_harness_contract.v1.json"
DOC_PATH = ROOT / "docs" / "AIB_LEVEL_B_HARNESS_PHASE3.md"


def verify_level_b_harness_phase3(
    contract_path: Path = CONTRACT_PATH,
    doc_path: Path = DOC_PATH,
) -> dict:
    issues: list[str] = []
    if not contract_path.is_file():
        issues.append("missing harness contract config")
    if not doc_path.is_file():
        issues.append("missing Phase 3 harness doc")
    if issues:
        return {"ok": False, "issues": issues, "HARNESS_VERIFY_STATUS": "FAIL"}

    doc = json.loads(contract_path.read_text(encoding="utf-8"))
    if doc.get("status") != "DESIGN_NOT_FROZEN":
        issues.append("status must remain DESIGN_NOT_FROZEN until Phase 4 authorization")
    if doc.get("authorization") != "NOT_AUTHORIZED_FOR_EXECUTION":
        issues.append("authorization must remain NOT_AUTHORIZED_FOR_EXECUTION")
    if not doc.get("trace_schema_version"):
        issues.append("trace_schema_version required")
    paired = ROOT / doc.get("paired_eval_contract", "")
    if not paired.is_file():
        issues.append("paired_eval_contract path missing")

    hook = doc.get("hook_points") or {}
    if "pre_target" not in hook or "pre_tool_call" not in hook:
        issues.append("hook_points must define pre_target and pre_tool_call")

    return {
        "ok": not issues,
        "issues": issues,
        "HARNESS_VERIFY_STATUS": "PASS" if not issues else "FAIL",
        "contract_id": doc.get("contract_id"),
        "trace_schema_version": doc.get("trace_schema_version"),
    }


def main() -> int:
    report = verify_level_b_harness_phase3()
    print(json.dumps(report, indent=2))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
