"""P1 figure data must match verified primary run (no matplotlib required)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

PRIMARY = ROOT / "results" / "p4_2_paired" / "p42-primary-d0-d2-20260921T173736Z-controlled"


@pytest.mark.skipif(not PRIMARY.is_dir(), reason="primary P4.2 run not in tree")
def test_p1_figure_data_matches_primary_evidence():
    from scripts.generate_p1_figures import collect_p1_figure_data

    data = collect_p1_figure_data(PRIMARY)
    assert data["run_id"].endswith("173736Z-controlled")
    assert data["population"] == {"attack_n": 9, "benign_n": 9}
    for key in ("ASR", "Utility", "FPR"):
        for cond in data[key]:
            assert data[key][cond]["denominator"] == 9
    assert data["ASR"][list(data["ASR"])[0]]["numerator"] == 1
    assert data["Utility"][list(data["Utility"])[0]]["numerator"] == 9
    assert data["FPR"][list(data["FPR"])[0]]["numerator"] == 0
    assert data["paired_transitions"] == {
        "success_to_success": 1,
        "success_to_failure": 0,
        "failure_to_success": 0,
        "failure_to_failure": 8,
    }


@pytest.mark.skipif(not PRIMARY.is_dir(), reason="primary P4.2 run not in tree")
def test_p1_figure_data_json_committed_when_present():
    path = ROOT / "docs" / "manuscript" / "figures" / "p1_figure_data.json"
    if not path.is_file():
        pytest.skip("p1_figure_data.json not generated yet")
    from scripts.generate_p1_figures import collect_p1_figure_data

    on_disk = json.loads(path.read_text(encoding="utf-8"))
    live = collect_p1_figure_data(PRIMARY)
    assert on_disk["ASR"] == live["ASR"]
    assert on_disk["Utility"] == live["Utility"]
    assert on_disk["FPR"] == live["FPR"]
    assert on_disk["paired_transitions"] == live["paired_transitions"]
