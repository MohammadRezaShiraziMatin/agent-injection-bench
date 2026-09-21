from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _lock_env(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key-placeholder")
    monkeypatch.setenv("OPENROUTER_TARGET_MODEL", "openai/gpt-4o-mini-2024-07-18")
    monkeypatch.setenv("OPENROUTER_JUDGE_MODEL", "meta-llama/llama-3.3-70b-instruct")
    monkeypatch.setenv("OPENROUTER_ALLOW_FALLBACKS", "false")
    monkeypatch.setenv("OPENROUTER_TARGET_PROVIDER_ORDER", "OpenAI")
    monkeypatch.setenv("OPENROUTER_JUDGE_PROVIDER_ORDER", "Groq")


def test_verify_model_lock_locked_with_gate_and_env(monkeypatch):
    _lock_env(monkeypatch)
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
    assert data["gates"]["G2_target_identity"] == "PASS"
    assert data["gates"]["G3_judge_identity"] == "PASS"
    assert data["gates"]["G4_immutable_catalog_snapshot"] == "PASS"
    assert data["gates"]["G10_live_eval_readiness"] == "PASS"
    assert proc.returncode == 0


def test_llm_openrouter_extra_body_from_gate(monkeypatch):
    _lock_env(monkeypatch)
    from agent.config import load_openrouter_config_for_role
    from agent.llm import LLMClient

    cfg = load_openrouter_config_for_role("target")
    client = LLMClient(cfg)
    captured = {}

    def fake_create(**kwargs):
        captured.update(kwargs)
        return None

    client._client.chat.completions.create = fake_create  # type: ignore[method-assign]
    client.chat([{"role": "user", "content": "hi"}])
    assert captured["extra_body"]["provider"]["allow_fallbacks"] is False
    assert captured["extra_body"]["provider"]["order"] == ["OpenAI"]
