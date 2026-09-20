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


def test_hr_audit_trail_empty():
    audit = json.loads((ROOT / "artifacts" / "p4_2_2_hr_audit_trail.json").read_text(encoding="utf-8"))
    assert audit["human_review_performed"] is False
    assert audit["decisions"] == []
