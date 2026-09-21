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


def test_p42_live_blocked_without_p42_gate():
    from scripts.run_p4_3_paired_benchmark import run_paired
    from scripts.p4_3_paired_common import load_p42_primary_run_config

    cfg = load_p42_primary_run_config()
    report = run_paired(
        run_id="test-p42-live-blocked",
        dry_run=False,
        p42_primary=True,
        **{k: cfg[k] for k in cfg if k != "utility_fpr_benign_scope"},
        utility_fpr_benign_scope=cfg["utility_fpr_benign_scope"],
    )
    assert report["ok"] is False
    assert report["gates"]["live_path"] == "P4.2_PRIMARY"
    assert report["gates"]["p4_2_d2_live_approval"]["scope_ok"] is True


def test_p42_dry_run_records_live_readiness():
    from scripts.run_p4_3_paired_benchmark import run_paired
    from scripts.p4_3_paired_common import load_p42_primary_run_config

    cfg = load_p42_primary_run_config()
    report = run_paired(
        run_id="test-p42-readiness-dry",
        dry_run=True,
        p42_primary=True,
        **{k: cfg[k] for k in cfg if k != "utility_fpr_benign_scope"},
        utility_fpr_benign_scope=cfg["utility_fpr_benign_scope"],
    )
    assert report["ok"] is True
    manifest = json.loads(
        (ROOT / report["out_dir"] / "RUN_MANIFEST.json").read_text(encoding="utf-8")
    )
    assert manifest["p4_2_d2_live_approval"]["scope_ok"] is True
    assert manifest["p4_2_d2_live_approval"]["gate_authorized"] is False


def test_p42_primary_config_dry_run():
    from scripts.run_p4_3_paired_benchmark import run_paired

    report = run_paired(
        run_id="test-p42-primary-dry-unit",
        dry_run=True,
        **{
            k: v
            for k, v in __import__(
                "scripts.p4_3_paired_common", fromlist=["load_p42_primary_run_config"]
            ).load_p42_primary_run_config().items()
            if k
            in (
                "dataset_root",
                "dataset_digest",
                "episode_ids",
                "out_base",
                "dataset_version",
                "design_manifest",
                "coverage_by_episode",
                "protocol_version",
                "utility_fpr_benign_scope",
                "primary_attack_ids",
                "utility_fpr_benign_episode_ids",
            )
        },
    )
    assert report["ok"] is True
    assert report["n_episodes"] == 18
    assert "p4_2_paired" in report["out_dir"]
    run_dir = ROOT / report["out_dir"]
    manifest = json.loads((run_dir / "RUN_MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["dataset_digest"] == "4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee"
    assert manifest["dataset_version"] == "P4.2"
    assert len(manifest["episode_ids"]) == 18
    assert len(manifest["primary_attack_ids"]) == 9
    assert len(manifest["utility_fpr_benign_episode_ids"]) == 9
    scope = manifest["utility_fpr_benign_scope"]
    assert scope["population"] == "pair_matched_benign_of_primary_attack_pool"
    cov = manifest["coverage_by_episode"]
    assert all(cov[eid]["coverage_class"] == "COV-A" for eid in manifest["primary_attack_ids"])
    assert all(cov[eid]["eligibility"] == "PRIMARY_ELIGIBLE" for eid in manifest["primary_attack_ids"])
    d0 = json.loads((run_dir / "D0" / "RESULTS.json").read_text(encoding="utf-8"))
    assert len(d0) == 18
    assert sum(1 for r in d0 if r.get("split") == "attack") == 9
    assert sum(1 for r in d0 if r.get("split") == "benign") == 9
    assert manifest["target_api_calls"] == 0
    assert manifest["judge_api_calls"] == 0


def test_paired_contract_defense_rate_documented():
    contract = json.loads(
        (ROOT / "config" / "p4_3_paired_eval_contract.v1.json").read_text(encoding="utf-8")
    )
    assert "paired_operational_definition" in contract["defense_rate"]
    assert contract["historical_d0_run_id"] == "p43-live-20260921-controlled"
