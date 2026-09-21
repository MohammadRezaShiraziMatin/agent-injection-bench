"""D2 / paired evaluation infrastructure (offline)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_d2_integration_blocked_without_package(monkeypatch):
    from scripts.verify_d2_integration import verify_d2_integration

    monkeypatch.setattr(
        "agent.defense.adaptiguard_bridge._package_importable",
        lambda: False,
    )
    report = verify_d2_integration()
    assert report["D2_INTEGRATION"] == "BLOCKED"
    assert report["integration"]["integrated"] is False


def test_paired_dry_run_comparability():
    from scripts.run_p4_3_paired_benchmark import run_paired
    from scripts.audit_paired_comparability import audit_run

    report = run_paired(run_id="test-paired-dry-unit", dry_run=True)
    assert report["ok"] is True
    run_dir = ROOT / report["out_dir"]
    audit = audit_run(run_dir)
    assert audit["comparability_status"] == "PASS"
    d0 = json.loads((run_dir / "D0" / "RESULTS.json").read_text(encoding="utf-8"))
    d2 = json.loads((run_dir / "D2" / "RESULTS.json").read_text(encoding="utf-8"))
    assert len(d0) == 8 and len(d2) == 8
    assert all(r["condition"] == "D0" for r in d0)
    assert all(r["condition"] == "D2" for r in d2)
    assert all(r["defense_event"]["defense_enabled"] is False for r in d0)
    assert all(r["defense_event"]["defense_enabled"] is True for r in d2)
    from agent.defense.adaptiguard_bridge import integration_status

    if integration_status().get("integrated"):
        assert all(r["defense_event"].get("detector_invoked") for r in d2)


def test_live_paired_blocked_without_d2():
    from scripts.run_p4_3_paired_benchmark import run_paired

    report = run_paired(run_id="test-paired-live-blocked", dry_run=False)
    assert report["ok"] is False
    assert report["paired_run"] == "BLOCKED"


def test_paired_contract_defense_rate_documented():
    contract = json.loads(
        (ROOT / "config" / "p4_3_paired_eval_contract.v1.json").read_text(encoding="utf-8")
    )
    assert "paired_operational_definition" in contract["defense_rate"]
    assert contract["historical_d0_run_id"] == "p43-live-20260921-controlled"
