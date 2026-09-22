"""CI contract guards: live-gate safety, frozen protocol, immutable historical evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FREEZE_PATH = ROOT / "config" / "p4_2_primary_research_protocol_freeze.v1.json"
D2_GATE_PATH = ROOT / "config" / "p4_3_d2_eval_gate.v1.json"
P42_DIGEST = "4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee"

# Pinned from tracked artifacts (mutation detection only; not a scientific threshold).
HISTORICAL_RUN_MANIFEST_SHA256 = (
    "bd3881779266ed84f186715f0ff64236facc99600bef22bb1958896e91f4fa68"
)
HISTORICAL_RUN_RESULTS_SHA256 = (
    "f7078bf0af7b8294f25c5bc546ce7c554557e9bc08d28d4df3fde1a18772c549"
)

P6_VALID_RUN_ID = "p42-primary-d0-d2-20260922T130300Z-controlled"
P6_VALID_RESULTS_SHA256 = (
    "f292c5355908e87d0195fe075a34c3245a8d04c169b1bfc6b1473d36053c254c"
)
P6_INVALID_RUN_ID = "p42-primary-d0-d2-20260922T122759Z-controlled"
P6_INVALID_RESULTS_SHA256 = (
    "1e1f8422721b8569152e894ea0d6af60b74f5eb22f3baa623371ad9957bebcd4"
)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_research_ci_workflow_present():
    wf = ROOT / ".github/workflows/research-ci.yml"
    assert wf.is_file()
    text = wf.read_text(encoding="utf-8")
    assert "permissions:" in text
    assert "contents: read" in text


@pytest.mark.skipif(not FREEZE_PATH.is_file(), reason="P4.2 protocol freeze not in tree")
def test_p5_protocol_freeze_status():
    freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    assert freeze.get("status") == "FROZEN"
    assert freeze.get("study_type") == "CONTROLLED_PAIRED_DESCRIPTIVE_EVALUATION"
    assert freeze.get("primary_endpoint") == "ASR"
    assert freeze.get("statistics") == "DESCRIPTIVE_ONLY"
    pop = freeze.get("primary_population") or {}
    assert pop.get("coverage_class") == "COV-A"
    assert pop.get("attack_episodes") == 9
    assert pop.get("benign_episodes") == 9
    assert pop.get("dataset_digest_sha256") == P42_DIGEST
    assert freeze.get("live_execution_in_this_freeze") is False


@pytest.mark.skipif(not D2_GATE_PATH.is_file(), reason="P4.3 D2 eval gate not in tree")
def test_live_d2_gate_safely_disabled():
    gate = json.loads(D2_GATE_PATH.read_text(encoding="utf-8"))
    assert gate.get("preflight", {}).get("live_d2_inference_allowed") is False
    assert gate.get("p4_2_primary_preflight", {}).get("live_d2_inference_allowed") is False


@pytest.mark.skipif(not FREEZE_PATH.is_file(), reason="P4.2 protocol freeze not in tree")
def test_historical_p42_run_immutable_per_freeze():
    freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    rel = freeze.get("historical_run_immutable")
    assert rel
    run_dir = ROOT / rel
    manifest = run_dir / "RUN_MANIFEST.json"
    results = run_dir / "RESULTS.json"
    assert manifest.is_file(), "historical RUN_MANIFEST missing"
    assert results.is_file(), "historical RESULTS missing"
    assert _sha256_file(manifest) == HISTORICAL_RUN_MANIFEST_SHA256
    assert _sha256_file(results) == HISTORICAL_RUN_RESULTS_SHA256
    doc = json.loads(manifest.read_text(encoding="utf-8"))
    assert doc.get("dataset_digest") == P42_DIGEST
    assert doc.get("n_episodes") == 18


@pytest.mark.skipif(
    not (ROOT / "results" / "p4_2_paired" / P6_VALID_RUN_ID / "RESULTS.json").is_file(),
    reason="P6 valid run not present in workspace",
)
def test_p6_valid_run_results_immutable_when_tracked():
    results = ROOT / "results" / "p4_2_paired" / P6_VALID_RUN_ID / "RESULTS.json"
    assert _sha256_file(results) == P6_VALID_RESULTS_SHA256
    rows = json.loads(results.read_text(encoding="utf-8"))
    assert len(rows) == 36
    assert sum(1 for r in rows if r.get("judge_status") != "ok") == 0


@pytest.mark.skipif(
    not (ROOT / "results" / "p4_2_paired" / P6_INVALID_RUN_ID / "RESULTS.json").is_file(),
    reason="invalid P6 run not present",
)
def test_p6_invalid_run_excluded_from_primary_evidence_contract():
    """Invalid judge-failure run remains detectable; not used as primary scorer input in CI."""
    results = ROOT / "results" / "p4_2_paired" / P6_INVALID_RUN_ID / "RESULTS.json"
    assert _sha256_file(results) == P6_INVALID_RESULTS_SHA256
    rows = json.loads(results.read_text(encoding="utf-8"))
    assert all(r.get("judge_status") == "JUDGE_FAILURE" for r in rows)
