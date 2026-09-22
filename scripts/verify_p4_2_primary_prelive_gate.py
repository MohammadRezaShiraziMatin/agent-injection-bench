#!/usr/bin/env python3
"""Offline PRELIVE readiness for frozen P4.2 primary descriptive protocol (not live execution)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FREEZE_PATH = ROOT / "config" / "p4_2_primary_research_protocol_freeze.v1.json"
PRIMARY_MANIFEST = ROOT / "artifacts" / "p4_2_primary_d0_d2_experiment" / "MANIFEST.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.verify_model_lock import verify_model_lock  # noqa: E402


def verify_p4_2_primary_prelive_gate() -> dict:
    issues: list[str] = []
    if not FREEZE_PATH.is_file():
        issues.append("protocol_freeze_missing")
        freeze = {}
    else:
        freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
        if freeze.get("status") != "FROZEN":
            issues.append("protocol_not_frozen")
        if freeze.get("study_type") != "CONTROLLED_PAIRED_DESCRIPTIVE_EVALUATION":
            issues.append("study_type_mismatch")

    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "verify_p4_2_freeze.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    p42 = json.loads(proc.stdout or "{}") if proc.returncode == 0 else {"ok": False}
    if not p42.get("ok"):
        issues.append("p4_2_freeze_fail")

    lock = verify_model_lock()
    if lock.get("MODEL_LOCK_STATUS") != "LOCKED":
        issues.append("model_lock_not_locked")

    if PRIMARY_MANIFEST.is_file() and freeze:
        design = json.loads(PRIMARY_MANIFEST.read_text(encoding="utf-8"))
        expected_digest = freeze.get("primary_population", {}).get("dataset_digest_sha256")
        if design.get("dataset", {}).get("digest_sha256") != expected_digest:
            issues.append("primary_manifest_digest_mismatch")
        if design.get("live_execution") is True:
            issues.append("primary_manifest_live_execution_true")

    ok = not issues
    return {
        "PRELIVE_GATE": "PASS" if ok else "FAIL",
        "ok": ok,
        "issues": issues,
        "protocol_freeze": str(FREEZE_PATH.relative_to(ROOT)),
        "study_type": freeze.get("study_type"),
        "live_execution_authorized_by_this_gate": False,
        "note": "PASS means frozen descriptive protocol + integrity checks only; live still requires separate approval gates.",
    }


def main() -> int:
    report = verify_p4_2_primary_prelive_gate()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
