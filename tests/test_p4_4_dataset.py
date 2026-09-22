"""P4.4 independent validation dataset stays schema-valid and disjoint from P4.2/P4.3."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.qc_p4_4 import run_qc
from scripts.verify_p4_4_freeze import main as freeze_main

ROOT = Path(__file__).resolve().parents[1]


def test_p44_qc_without_regen() -> None:
    report = run_qc(ROOT / "data" / "episodes_p4_4", check_repro=False)
    assert report["ok"], report["issues"]
    assert report["attack_count"] == 100
    assert report["benign_count"] == 100
    assert report["pair_count"] == 100
    assert report["leakage"]["acf_collisions"] == 0
    assert report["leakage"]["near_duplicates_vs_prior"] == 0
    assert set(report["families"]) >= {
        "direct_prompt_injection",
        "indirect_prompt_injection",
        "rag_document_injection",
        "web_retrieved_content_injection",
        "tool_output_injection",
        "multi_turn_injection",
        "memory_state_injection",
        "cross_context_injection",
        "multi_agent_injection",
        "adaptive_injection",
    }


def test_p44_freeze_and_parents() -> None:
    assert freeze_main() == 0
    p42 = json.loads((ROOT / "data/episodes_p4_2/MANIFEST.json").read_text(encoding="utf-8"))
    assert p42["digest_sha256"] == "4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee"
    p43 = json.loads((ROOT / "data/episodes_p4_3/MANIFEST.json").read_text(encoding="utf-8"))
    assert p43["digest_sha256"] == "e60969bee257ec3111febf215fb5f7079edb79ed050dae300e549336184ab53d"


def test_p44_adjudication_trail_does_not_mutate_freeze() -> None:
    trail = json.loads((ROOT / "artifacts/p4_4_hr_audit_trail.json").read_text(encoding="utf-8"))
    decisions = trail["decisions"]
    assert len(decisions) == 200
    assert len({d["episode_id"] for d in decisions}) == 200
    labels = {"ACCEPT", "REVISE", "REJECT", "UNCERTAIN"}
    counts = {"attack": {k: 0 for k in labels}, "benign": {k: 0 for k in labels}}
    for row in decisions:
        assert row["human_decision"] in labels
        split = "attack" if row["episode_id"].startswith("atk_") else "benign"
        counts[split][row["human_decision"]] += 1
        if row["human_decision"] != "ACCEPT":
            assert row["reason"]
            assert row["affected_fields"]
        episode = next((ROOT / "data/episodes_p4_4").rglob(row["episode_id"] + ".json"))
        body = json.loads(episode.read_text(encoding="utf-8"))
        assert body["provenance"]["review_status"] == "unreviewed"
        assert body["pair_id"] == row["pair_id"]
    assert counts == trail["summary"]
    manifest = json.loads((ROOT / "data/episodes_p4_4/MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["digest_sha256"] == trail["dataset_digest_sha256"]
    assert trail["episode_bytes_changed"] is False


def test_p44_v2_freeze_keeps_v1() -> None:
    from scripts.verify_p4_4_v2_freeze import main as v2_freeze_main

    assert v2_freeze_main() == 0
    v2 = json.loads((ROOT / "data/episodes_p4_4_v2/MANIFEST.json").read_text(encoding="utf-8"))
    assert v2["digest_sha256"] == "8dcf0664729ed4b8f7e0e445180979c2929efc305e9c08787886e738b43ee531"
    assert v2["parent_digest"] == "d5132fb3a4897684e1cb8a6f38f7cd367ee2a928bcd351743f73f13c326d796f"
    assert v2["revision_count"] == 96
    assert v2["attack_count"] == 100
    assert v2["benign_count"] == 100
    assert v2["pair_count"] == 100
    assert v2["dataset_version"] == "P4.4-v2"
    assert v2["parent_version"] == "P4.4"
    assert v2["revision_source"] == "artifacts/p4_4_hr_audit_trail.json"
