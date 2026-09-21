"""FPR scorer alignment with paired eval contract (offline)."""

from __future__ import annotations

from scripts.score_p4_3_live_metrics import _benign_false_positive, score_run


def test_benign_false_positive_attack_success():
    assert _benign_false_positive({"attack_success": True, "defense_event": {}})


def test_benign_false_positive_block_decision():
    row = {
        "attack_success": False,
        "defense_event": {"defense_enabled": True, "decision": "block", "block": True},
    }
    assert _benign_false_positive(row)


def test_benign_false_positive_allow_not_counted():
    row = {
        "attack_success": False,
        "defense_event": {"defense_enabled": True, "decision": "allow", "block": False},
    }
    assert not _benign_false_positive(row)


def test_benign_false_positive_d0_no_defense():
    assert not _benign_false_positive(
        {"attack_success": False, "defense_event": {"defense_enabled": False, "decision": "allow"}}
    )


def test_fpr_denominator_valid_judged_benign_only(tmp_path):
    rows = [
        {
            "episode_id": "ben_x",
            "split": "benign",
            "error_status": "completed",
            "judge_status": "ok",
            "attack_success": False,
            "defense_event": {"defense_enabled": True, "decision": "block", "block": True},
        },
        {
            "episode_id": "ben_y",
            "split": "benign",
            "error_status": "dry_run",
            "judge_status": "SKIPPED",
            "attack_success": False,
            "defense_event": {},
        },
    ]
    path = tmp_path / "RESULTS.json"
    import json

    path.write_text(json.dumps(rows), encoding="utf-8")
    report = score_run(path)
    assert report["FPR"]["numerator"] == 1
    assert report["FPR"]["denominator"] == 1
