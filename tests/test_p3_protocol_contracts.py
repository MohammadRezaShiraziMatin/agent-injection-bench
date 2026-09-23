"""P3 protocol freeze and extension manifest contracts (offline)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
P3_FREEZE = ROOT / "config" / "p3_experimental_protocol_freeze.v1.json"
P3_MANIFEST = ROOT / "artifacts" / "p3_cov_b_extension" / "MANIFEST.json"


@pytest.mark.skipif(not P3_FREEZE.is_file(), reason="P3 freeze not in tree")
def test_p3_freeze_descriptive_extension():
    doc = json.loads(P3_FREEZE.read_text(encoding="utf-8"))
    assert doc.get("status") == "FROZEN"
    assert doc.get("statistics") == "DESCRIPTIVE_ONLY"
    assert doc.get("primary_endpoint") == "ASR"
    assert doc["extension_population"]["label"] == "P3-EXT"
    assert doc["live_execution"]["live_d2_inference_allowed"] is True
    hist = doc.get("historical_evidence_immutable", "")
    assert "173736" in hist


@pytest.mark.skipif(not P3_MANIFEST.is_file(), reason="P3 manifest not in tree")
def test_p3_cov_b_manifest_loads_via_runner_helper():
    from scripts.p4_3_paired_common import load_p3_cov_b_extension_run_config

    cfg = load_p3_cov_b_extension_run_config()
    assert len(cfg["primary_attack_ids"]) == 42
    assert len(cfg["utility_fpr_benign_episode_ids"]) == 42
    assert cfg["out_base"].name == "p3_paired"
    assert cfg["protocol_version"] == "P3-COV-B-EXT-PAIRED-1"


@pytest.mark.skipif(not P3_FREEZE.is_file(), reason="P3 freeze not in tree")
def test_p3_safety_gate_passes_offline():
    from scripts.verify_p3_scientific_safety_gate import verify_p3_scientific_safety_gate

    report = verify_p3_scientific_safety_gate()
    assert report.get("checks", {}).get("historical_run_protected") == "PASS"
    assert report.get("checks", {}).get("protocol_frozen") == "PASS"
    assert report.get("checks", {}).get("p3_approval_artifact") == "PRESENT"
    assert report.get("ok") is True


@pytest.mark.skipif(
    not (ROOT / "artifacts" / "p3_live_execution_approval.json").is_file(),
    reason="P3 approval not in tree",
)
def test_p3_live_execution_approval_ok():
    from scripts.verify_p3_live_execution_approval import verify_p3_live_execution_approval

    report = verify_p3_live_execution_approval()
    assert report.get("ok") is True
    assert report.get("scope_ok") is True
