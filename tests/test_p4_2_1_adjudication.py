from __future__ import annotations

import json
from pathlib import Path

from scripts.adjudicate_p4_2_1 import run_adjudication

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts" / "p4_2_1_near_duplicate_adjudication.json"


def test_p4_2_1_adjudication_artifact_complete():
    assert ART.is_file()
    data = json.loads(ART.read_text(encoding="utf-8"))
    assert data["flag_count"] == 114
    assert len(data["records"]) == 114
    assert sum(data["adjudication_counts"].values()) == 114
    assert data["replacements_required"] == 0


def test_p4_2_1_reconstruct_matches_artifact_counts():
    live = run_adjudication(ROOT / "data" / "episodes_p4_2")
    assert live["flag_count"] == 114
