from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_model_lock_blocked_without_pinned_models(monkeypatch):
    monkeypatch.delenv("OPENROUTER_TARGET_MODEL", raising=False)
    monkeypatch.delenv("OPENROUTER_JUDGE_MODEL", raising=False)
    proc = subprocess.run(
        [sys.executable, "scripts/verify_model_lock.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={**dict(__import__("os").environ), "PYTHONPATH": str(ROOT)},
    )
    data = json.loads(proc.stdout)
    assert data["MODEL_LOCK_STATUS"] in ("BLOCKED", "PARTIALLY_LOCKED")
    assert proc.returncode != 0 or data["MODEL_LOCK_STATUS"] != "LOCKED"


def test_preflight_dry_run_no_live(monkeypatch):
    monkeypatch.delenv("OPENROUTER_TARGET_MODEL", raising=False)
    monkeypatch.delenv("OPENROUTER_JUDGE_MODEL", raising=False)
    proc = subprocess.run(
        [sys.executable, "scripts/live_eval_preflight.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={**dict(__import__("os").environ), "PYTHONPATH": str(ROOT)},
    )
    data = json.loads(proc.stdout)
    assert data["dry_run"] is True
    assert data["live_inference_executed"] is False
    assert data["preflight_ok"] is False
