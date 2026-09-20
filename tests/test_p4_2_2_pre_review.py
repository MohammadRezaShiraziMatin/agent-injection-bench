from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "artifacts" / "p4_2_2_human_review_matrix.json"


def test_p4_2_2_review_matrix_complete():
    data = json.loads(MATRIX.read_text(encoding="utf-8"))
    assert data["episode_count"] == 200
    assert len(data["records"]) == 200
    assert data["human_review_performed"] is False
    for rec in data["records"]:
        assert rec["review_status"] == "unreviewed"
        assert rec["human_decision"] is None
        assert rec.get("automated_pre_review") is True
