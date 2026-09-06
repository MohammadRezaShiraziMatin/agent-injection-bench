from __future__ import annotations

import pytest

from agent.config import LLMConfigError, config_from_env


def test_config_requires_key(monkeypatch) -> None:
    monkeypatch.delenv("AIB_LLM_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(LLMConfigError, match="No API key"):
        config_from_env(require_key=True)


def test_config_aib_overrides_openai(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    monkeypatch.setenv("AIB_LLM_API_KEY", "aib-key")
    monkeypatch.setenv("AIB_LLM_MODEL", "aib-model")
    monkeypatch.setenv("OPENAI_MODEL", "openai-model")
    monkeypatch.setenv("AIB_LLM_BASE_URL", "https://aib.example/v1")
    cfg = config_from_env(require_key=True)
    assert cfg.api_key == "aib-key"
    assert cfg.model == "aib-model"
    assert cfg.base_url == "https://aib.example/v1"
    assert "aib-key" not in str(cfg.masked())
    assert cfg.masked()["model"] == "aib-model"
