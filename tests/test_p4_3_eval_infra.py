from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_model_lock_g10_fails_without_env_models(monkeypatch, tmp_path):
    empty = tmp_path / ".env"
    empty.write_text("")
    for name in (
        "OPENROUTER_API_KEY",
        "OPENROUTER_TARGET_MODEL",
        "OPENROUTER_JUDGE_MODEL",
        "AIB_LLM_API_KEY",
        "OPENAI_API_KEY",
    ):
        monkeypatch.delenv(name, raising=False)
    from scripts.verify_model_lock import verify_model_lock

    monkeypatch.setattr(
        "agent.config.load_dotenv",
        lambda *a, **k: None,
    )
    data = verify_model_lock()
    assert data["gates"]["G10_live_eval_readiness"] == "FAIL"


def test_preflight_dry_run_no_live(monkeypatch):
    monkeypatch.delenv("OPENROUTER_TARGET_MODEL", raising=False)
    monkeypatch.delenv("OPENROUTER_JUDGE_MODEL", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    from scripts.live_eval_preflight import run_preflight

    monkeypatch.setattr(
        "agent.config.load_dotenv",
        lambda *a, **k: None,
    )
    data = run_preflight()
    assert data["dry_run"] is True
    assert data["live_inference_executed"] is False
    assert data["preflight_ok"] is False
