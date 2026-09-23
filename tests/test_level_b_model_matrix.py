from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_verify_level_b_model_matrix_passes_offline():
    proc = subprocess.run(
        [sys.executable, "scripts/verify_level_b_model_matrix.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={**dict(__import__("os").environ), "PYTHONPATH": str(ROOT)},
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    data = json.loads(proc.stdout)
    assert data["MATRIX_VERIFY_STATUS"] == "PASS"
    assert data["status"] == "DESIGN"
    assert data["live_execution_authorized"] is False
    assert data["target_families_non_candidate"] == ["google_gemini_flash", "openai_gpt4o_mini"]


def test_verify_level_b_model_matrix_fails_on_false_lock(tmp_path: Path):
    from scripts.verify_level_b_model_matrix import verify_level_b_model_matrix

    src = ROOT / "config" / "level_b_model_matrix.v1.json"
    broken = json.loads(src.read_text(encoding="utf-8"))
    broken["status"] = "LOCKED"
    broken["researcher_sign_off"] = "missing rest of approval chain"
    dest = tmp_path / "matrix.json"
    dest.write_text(json.dumps(broken, indent=2), encoding="utf-8")
    report = verify_level_b_model_matrix(matrix_path=dest, protocol_freeze_path=tmp_path / "none.json")
    assert report["ok"] is False
    assert any("approval" in i.lower() or "LOCKED" in i for i in report["issues"])


@pytest.mark.skipif(
    not (ROOT / "config" / "level_b_protocol_freeze.v1.json").is_file(),
    reason="protocol freeze stub missing",
)
def test_protocol_freeze_points_at_matrix():
    freeze = json.loads(
        (ROOT / "config" / "level_b_protocol_freeze.v1.json").read_text(encoding="utf-8")
    )
    assert freeze.get("status") == "DESIGN_NOT_FROZEN"
    assert (
        freeze.get("inherits_read_only", {}).get("level_b_model_matrix")
        == "config/level_b_model_matrix.v1.json"
    )
