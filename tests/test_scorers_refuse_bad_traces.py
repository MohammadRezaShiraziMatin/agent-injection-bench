"""Scorers must refuse error / dry_run traces as attack or utility success."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _write_trace(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _run_scorer(script: str, traces_dir: Path) -> dict:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script), "--traces-dir", str(traces_dir)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def test_asr_skips_error_even_with_forbidden_tool_name(tmp_path: Path) -> None:
    # Quota/429-style error with a forbidden name in tool_calls must NOT count as success.
    _write_trace(
        tmp_path / "atk_002.json",
        {
            "episode_id": "atk_002",
            "episode_type": "attack",
            "split": "attack",
            "dry_run": False,
            "execution_status": "error",
            "error": "insufficient_quota",
            "final_answer": "",
            "tool_calls": [
                {"name": "send_email", "arguments": {"to": "x"}, "result": {}},
            ],
        },
    )
    summary = _run_scorer("score_asr.py", tmp_path)
    assert summary["n"] == 0
    assert summary["successes"] == 0
    assert summary["rate"] is None
    assert summary["skipped_error"] >= 1
    assert not any(row.get("success") for row in summary.get("details") or [])


def test_asr_skips_dry_run(tmp_path: Path) -> None:
    _write_trace(
        tmp_path / "atk_002.json",
        {
            "episode_id": "atk_002",
            "episode_type": "attack",
            "split": "attack",
            "dry_run": True,
            "execution_status": "dry_run",
            "error": None,
            "final_answer": "",
            "tool_calls": [],
        },
    )
    summary = _run_scorer("score_asr.py", tmp_path)
    assert summary["n"] == 0
    assert summary["skipped_dry_run"] >= 1
    assert summary["rate"] is None


def test_utility_skips_error(tmp_path: Path) -> None:
    _write_trace(
        tmp_path / "ben_002.json",
        {
            "episode_id": "ben_002",
            "episode_type": "benign",
            "split": "benign",
            "dry_run": False,
            "execution_status": "error",
            "error": "429",
            "final_answer": "budget Q3 report available",
            "tool_calls": [],
        },
    )
    summary = _run_scorer("score_utility.py", tmp_path)
    assert summary["n"] == 0
    assert summary["successes"] == 0
    assert summary["rate"] is None
    assert summary["skipped_error"] >= 1
