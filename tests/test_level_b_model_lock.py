from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _p43_lock_env(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key-placeholder")
    monkeypatch.setenv("OPENROUTER_TARGET_MODEL", "openai/gpt-4o-mini-2024-07-18")
    monkeypatch.setenv("OPENROUTER_JUDGE_MODEL", "meta-llama/llama-3.3-70b-instruct")
    monkeypatch.setenv("OPENROUTER_ALLOW_FALLBACKS", "false")
    monkeypatch.setenv("OPENROUTER_TARGET_PROVIDER_ORDER", "OpenAI")
    monkeypatch.setenv("OPENROUTER_JUDGE_PROVIDER_ORDER", "Groq")


def _family_b_lock_env(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key-placeholder")
    monkeypatch.setenv("OPENROUTER_TARGET_MODEL", "google/gemini-2.5-flash")
    monkeypatch.setenv("OPENROUTER_JUDGE_MODEL", "meta-llama/llama-3.3-70b-instruct")
    monkeypatch.setenv("OPENROUTER_ALLOW_FALLBACKS", "false")
    monkeypatch.setenv("OPENROUTER_TARGET_PROVIDER_ORDER", "Google")
    monkeypatch.setenv("OPENROUTER_JUDGE_PROVIDER_ORDER", "Groq")


def test_level_b_primary_row_inherits_p43_lock(monkeypatch):
    _p43_lock_env(monkeypatch)
    from scripts.verify_model_lock import verify_level_b_model_lock

    report = verify_level_b_model_lock("target-level-a-primary")
    assert report["MODEL_LOCK_STATUS"] == "LOCKED"
    assert report["level_b_lock_mode"] == "INHERITS_LEVEL_A"
    assert report["gates"]["G2_target_identity"] == "PASS"


def test_level_b_family_b_locked_with_matrix_env(monkeypatch):
    _family_b_lock_env(monkeypatch)
    from scripts.verify_model_lock import verify_level_b_model_lock

    report = verify_level_b_model_lock("target-candidate-family-b")
    assert report["MODEL_LOCK_STATUS"] == "LOCKED"
    assert report["level_b_lock_mode"] == "LOCKED"
    assert report["gates"]["G2_target_identity"] == "PASS"
    assert report["target_model_id"] == "google/gemini-2.5-flash"
    assert report["env_target_model_id"] == "google/gemini-2.5-flash"


def test_level_b_family_b_wrong_env_target_fails(monkeypatch):
    _p43_lock_env(monkeypatch)
    from scripts.verify_model_lock import verify_level_b_model_lock

    report = verify_level_b_model_lock("target-candidate-family-b")
    assert report["MODEL_LOCK_STATUS"] == "BLOCKED"
    assert report["gates"]["G2_target_identity"] == "FAIL"


def test_p43_verify_model_lock_unchanged(monkeypatch):
    _p43_lock_env(monkeypatch)
    proc = subprocess.run(
        [sys.executable, "scripts/verify_model_lock.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={**dict(__import__("os").environ), "PYTHONPATH": str(ROOT)},
    )
    data = json.loads(proc.stdout)
    assert data["MODEL_LOCK_STATUS"] == "LOCKED"
    assert proc.returncode == 0


def test_level_b_dry_run_passes_model_lock_for_family_b(monkeypatch):
    _family_b_lock_env(monkeypatch)
    from scripts.run_p4_3_paired_benchmark import _dry_run_gates_ok

    ok, report = _dry_run_gates_ok(level_b=True, matrix_row_id="target-candidate-family-b")
    assert report["model_lock"]["MODEL_LOCK_STATUS"] == "LOCKED"
    assert report["model_lock"]["gates"]["G2_target_identity"] == "PASS"
    assert ok is True
