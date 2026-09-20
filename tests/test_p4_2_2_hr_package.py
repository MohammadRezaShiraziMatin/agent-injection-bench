from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_hr_queue_covers_all_episodes_with_null_human_fields():
    queue = json.loads((ROOT / "artifacts" / "p4_2_2_hr_review_queue.json").read_text(encoding="utf-8"))
    matrix = json.loads((ROOT / "artifacts" / "p4_2_2_human_review_matrix.json").read_text(encoding="utf-8"))
    assert queue["episode_count"] == 200
    assert matrix["episode_count"] == 200
    assert queue["human_review_performed"] is False
    ids_q = {c["episode_id"] for c in queue["review_cards"]}
    ids_m = {r["episode_id"] for r in matrix["records"]}
    assert ids_q == ids_m
    for card in queue["review_cards"]:
        assert card["human_decision"] is None
        assert card["human_reviewer"] is None
        assert card["review_date"] is None
        assert card["review_status"] == "unreviewed"


def test_hr_uncertain_and_similarity_batches():
    queue = json.loads((ROOT / "artifacts" / "p4_2_2_hr_review_queue.json").read_text(encoding="utf-8"))
    by_batch = {b["batch_id"]: b["episode_count"] for b in queue["batches"]}
    assert by_batch["batch_1_uncertain"] == 16
    assert by_batch["batch_3_similarity_confirmation"] == 20
    assert sum(by_batch.values()) == 200


def test_hr_audit_trail_batch1_recorded():
    audit = json.loads((ROOT / "artifacts" / "p4_2_2_hr_audit_trail.json").read_text(encoding="utf-8"))
    assert audit["human_review_performed"] is True
    assert len(audit["decisions"]) >= 16
    by_id = {d["episode_id"]: d["human_decision"] for d in audit["decisions"]}
    expected = {
        "atk_p42_093": "REVISE",
        "ben_p42_093": "ACCEPT",
        "atk_p42_094": "REVISE",
        "ben_p42_094": "ACCEPT",
        "atk_p42_095": "REVISE",
        "ben_p42_095": "ACCEPT",
        "atk_p42_096": "REVISE",
        "ben_p42_096": "ACCEPT",
        "atk_p42_097": "REVISE",
        "ben_p42_097": "ACCEPT",
        "atk_p42_098": "REVISE",
        "ben_p42_098": "ACCEPT",
        "atk_p42_099": "REVISE",
        "ben_p42_099": "ACCEPT",
        "atk_p42_100": "REVISE",
        "ben_p42_100": "ACCEPT",
    }
    assert {k: by_id[k] for k in expected} == expected
    assert all(d.get("human_reviewer") is None for d in audit["decisions"])
    assert all(d.get("review_date") is None for d in audit["decisions"])
    revise = [d for d in audit["decisions"] if d["human_decision"] == "REVISE"]
    assert len(revise) == 8
    for d in revise:
        assert d.get("revision_resolution")
        assert d["revision_resolution"]["revision_type"] in {
            "METADATA_ONLY",
            "CONTENT_REVISION",
        }
        assert d.get("content_mutation")


def test_hr_audit_trail_batch2a_recorded():
    audit = json.loads((ROOT / "artifacts" / "p4_2_2_hr_audit_trail.json").read_text(encoding="utf-8"))
    by_id = {d["episode_id"]: d["human_decision"] for d in audit["decisions"]}
    for i in range(35, 45):
        assert by_id[f"atk_p42_{i:03d}"] == "ACCEPT"
        assert by_id[f"ben_p42_{i:03d}"] == "ACCEPT"
    batch2a = [
        d
        for d in audit["decisions"]
        if d["episode_id"].startswith(("atk_p42_0", "ben_p42_0"))
        and 35 <= int(d["episode_id"].split("_")[-1]) <= 44
    ]
    assert len(batch2a) == 20
    assert all(d.get("previous_automated_status") == "ACCEPT_CANDIDATE" for d in batch2a)
    assert all(d.get("human_reviewer") is None for d in batch2a)


def test_hr_audit_trail_batch2b_recorded():
    audit = json.loads((ROOT / "artifacts" / "p4_2_2_hr_audit_trail.json").read_text(encoding="utf-8"))
    by_id = {d["episode_id"]: d["human_decision"] for d in audit["decisions"]}
    for i in range(45, 59):
        assert by_id[f"atk_p42_{i:03d}"] == "ACCEPT"
        assert by_id[f"ben_p42_{i:03d}"] == "ACCEPT"
    batch2b = [
        d
        for d in audit["decisions"]
        if d["episode_id"].startswith(("atk_p42_0", "ben_p42_0"))
        and 45 <= int(d["episode_id"].split("_")[-1]) <= 58
    ]
    assert len(batch2b) == 28
    assert all(d.get("previous_automated_status") == "ACCEPT_CANDIDATE" for d in batch2b)
    assert all(d.get("human_reviewer") is None for d in batch2b)
    meta = audit.get("batch2b_human_decisions")
    assert meta is not None
    assert meta["episode_count"] == 28


def test_hr_audit_trail_batch2c_recorded():
    audit = json.loads((ROOT / "artifacts" / "p4_2_2_hr_audit_trail.json").read_text(encoding="utf-8"))
    by_id = {d["episode_id"]: d["human_decision"] for d in audit["decisions"]}
    for i in range(59, 71):
        assert by_id[f"atk_p42_{i:03d}"] == "ACCEPT"
        assert by_id[f"ben_p42_{i:03d}"] == "ACCEPT"
    batch2c = [
        d
        for d in audit["decisions"]
        if d["episode_id"].startswith(("atk_p42_0", "ben_p42_0"))
        and 59 <= int(d["episode_id"].split("_")[-1]) <= 70
    ]
    assert len(batch2c) == 24
    assert all(d.get("previous_automated_status") == "ACCEPT_CANDIDATE" for d in batch2c)
    assert all(d.get("human_reviewer") is None for d in batch2c)
    meta = audit.get("batch2c_human_decisions")
    assert meta is not None
    assert meta["episode_count"] == 24
    assert len(audit["decisions"]) == 88
