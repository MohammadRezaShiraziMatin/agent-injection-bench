"""P3-EXT figure data must match verified COV-B live run (no matplotlib required)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

P3_RUN = ROOT / "results" / "p3_paired" / "p3-cov-b-ext-20260923T112900Z-controlled"


@pytest.mark.skipif(not P3_RUN.is_dir(), reason="P3 live run not in tree")
def test_p3_figure_data_matches_live_evidence():
    from scripts.generate_p3_figures import collect_p3_figure_data

    data = collect_p3_figure_data(P3_RUN)
    assert data["run_id"] == "p3-cov-b-ext-20260923T112900Z-controlled"
    assert data["coverage_class"] == "COV-B"
    assert data["population"]["attack_episodes_executed"] == 42
    assert data["population"]["d0_judge_failures"] == 1
    assert data["population"]["d2_judge_failures"] == 0
    assert data["ASR"][list(data["ASR"])[0]]["numerator"] == 11
    assert data["ASR"][list(data["ASR"])[0]]["denominator"] == 41
    assert data["ASR"][list(data["ASR"])[1]]["denominator"] == 42
    assert data["Utility"][list(data["Utility"])[0]]["numerator"] == 35
    assert data["FPR"][list(data["FPR"])[0]]["numerator"] == 0
    assert data["paired_transitions"] == {
        "success_to_success": 11,
        "success_to_failure": 0,
        "failure_to_success": 0,
        "failure_to_failure": 31,
    }


@pytest.mark.skipif(not P3_RUN.is_dir(), reason="P3 live run not in tree")
def test_p3_figure_data_json_committed_when_present():
    path = ROOT / "docs" / "manuscript" / "figures" / "p3_figure_data.json"
    if not path.is_file():
        pytest.skip("p3_figure_data.json not generated yet")
    from scripts.generate_p3_figures import collect_p3_figure_data

    on_disk = json.loads(path.read_text(encoding="utf-8"))
    live = collect_p3_figure_data(P3_RUN)
    assert on_disk["ASR"] == live["ASR"]
    assert on_disk["Utility"] == live["Utility"]
    assert on_disk["FPR"] == live["FPR"]
    assert on_disk["paired_transitions"] == live["paired_transitions"]
