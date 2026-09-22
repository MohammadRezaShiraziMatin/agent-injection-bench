"""Structured JSONL run audit trail."""

from __future__ import annotations

import json
from pathlib import Path

from agent.structured_run_log import (
    STAGE_INIT,
    sanitize_for_log,
    StructuredRunLogger,
)


def test_sanitize_for_log_redacts_secrets():
    raw = {
        "api_key": "sk-secret-value",
        "nested": {"authorization": "Bearer abc.def.ghi"},
        "ok_field": "visible",
    }
    clean = sanitize_for_log(raw)
    assert clean["api_key"] == "[REDACTED]"
    assert "REDACTED" in clean["nested"]["authorization"]
    assert clean["ok_field"] == "visible"


def test_audit_trail_written_on_paired_dry_run(tmp_path):
    from scripts.run_p4_3_paired_benchmark import run_paired

    out_base = tmp_path / "paired"
    report = run_paired(run_id="test-audit-trail-dry", dry_run=True, out_base=out_base)
    assert report["ok"] is True
    trail = out_base / "test-audit-trail-dry" / "AUDIT_TRAIL.jsonl"
    assert trail.is_file()
    lines = [json.loads(ln) for ln in trail.read_text(encoding="utf-8").splitlines() if ln.strip()]
    stages = [r["stage"] for r in lines]
    assert STAGE_INIT in stages
    assert "FINAL_STATUS" in stages
    for row in lines:
        blob = json.dumps(row)
        assert "sk-" not in blob or "[REDACTED]" in blob

    from scripts.score_p4_3_paired_metrics import score_paired

    score_paired(out_base / "test-audit-trail-dry")
    lines2 = [json.loads(ln) for ln in trail.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert any(r["stage"] == "SCORING" for r in lines2)
    assert sum(1 for r in lines2 if r["stage"] == "AGGREGATION") == 1
