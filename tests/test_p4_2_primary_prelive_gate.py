"""P4.2 primary descriptive protocol PRELIVE gate (offline)."""

from __future__ import annotations


def test_p42_primary_prelive_gate_passes():
    from scripts.verify_p4_2_primary_prelive_gate import verify_p4_2_primary_prelive_gate

    report = verify_p4_2_primary_prelive_gate()
    assert report["PRELIVE_GATE"] == "PASS"
    assert report["ok"] is True
    assert report["live_execution_authorized_by_this_gate"] is False
