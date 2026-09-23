from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_verify_level_b_phase4_prelive_gate_passes_offline():
    proc = subprocess.run(
        [sys.executable, "scripts/verify_level_b_phase4_prelive_gate.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={**dict(__import__("os").environ), "PYTHONPATH": str(ROOT)},
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    data = json.loads(proc.stdout)
    assert data["LEVEL_B_PHASE4_PRELIVE_GATE"] == "PASS"
    assert data["live_inference_allowed"] is False
    assert data["candidate_attack_count"] > 9


def test_prelive_gate_fails_on_false_authorization(tmp_path: Path):
    from scripts.verify_level_b_phase4_prelive_gate import verify_level_b_phase4_prelive_gate

    approval = json.loads(
        (ROOT / "artifacts" / "level_b_phase4_execution_approval.json").read_text(encoding="utf-8")
    )
    approval["status"] = "EXPLICIT"
    approval["authorized"] = True
    approval["approver"] = "fake_without_full_chain"
    approval["approved_at"] = "2026-09-23T00:00:00Z"
    bad_approval = tmp_path / "approval.json"
    bad_approval.write_text(json.dumps(approval, indent=2), encoding="utf-8")

    report = verify_level_b_phase4_prelive_gate(approval_path=bad_approval)
    assert report["ok"] is False
    assert report["LEVEL_B_PHASE4_PRELIVE_GATE"] == "FAIL"
    assert any("gate_live_inference_not_enabled" in i or "population_manifest_not_frozen" in i for i in report["issues"])


def test_prelive_gate_fails_when_authorized_true_awaiting_key(tmp_path: Path):
    from scripts.verify_level_b_phase4_prelive_gate import verify_level_b_phase4_prelive_gate

    approval = json.loads(
        (ROOT / "artifacts" / "level_b_phase4_execution_approval.json").read_text(encoding="utf-8")
    )
    approval["authorized"] = True
    bad_approval = tmp_path / "approval.json"
    bad_approval.write_text(json.dumps(approval, indent=2), encoding="utf-8")

    report = verify_level_b_phase4_prelive_gate(approval_path=bad_approval)
    assert report["ok"] is False
    assert "approval_authorized_true" in report["issues"]
