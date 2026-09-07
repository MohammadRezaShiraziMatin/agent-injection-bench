"""D0 prompt + reproducibility hooks."""

from __future__ import annotations

from pathlib import Path

from agent.config import config_from_env
from agent.llm import LLMResponse, ScriptedLLM
from agent.load import load_episode
from agent.loop import SYSTEM_PROMPT, load_system_prompt, run_episode
from agent.traces import empty_trace, make_run_id, write_manifest
from scripts._common import load_json

ROOT = Path(__file__).resolve().parents[1]


def test_d0_prompt_has_no_protective_defense_wording() -> None:
    text = load_system_prompt("d0").lower()
    assert "search_docs" in text
    assert "send_email" in text
    banned = [
        "ignore",
        "untrusted",
        "prompt injection",
        "do not follow",
        "disregard",
        "jailbreak",
        "adversarial",
        "guardrail",
        "safety policy",
        "refuse",
    ]
    for word in banned:
        assert word not in text, f"D0 must not contain protective wording {word!r}"
    assert SYSTEM_PROMPT.strip() == load_system_prompt("d0").strip()


def test_run_episode_attaches_run_id_and_d0(attack_example: Path) -> None:
    episode = load_episode(attack_example)
    client = ScriptedLLM([LLMResponse(content="ok")])
    from agent.config import LLMConfig

    config = LLMConfig(
        api_key="x",
        base_url="https://llm.test/v1",
        model="scripted",
        temperature=0.0,
        seed=7,
    )
    run_id = make_run_id(model="scripted", episode_id="atk_001")
    trace = run_episode(episode, client=client, config=config, run_id=run_id)
    assert trace["run_id"] == run_id
    assert trace["prompt_id"] == "d0"
    assert trace["defense_condition"] == "d0"
    assert trace["temperature"] == 0.0
    assert trace["seed"] == 7


def test_write_manifest(tmp_path: Path) -> None:
    path = write_manifest(
        "test-run-id",
        episode_ids=["atk_002", "ben_002"],
        model="m",
        temperature=0.0,
        seed=1,
        out_dir=tmp_path,
    )
    payload = load_json(path)
    assert payload["run_id"] == "test-run-id"
    assert payload["episode_ids"] == ["atk_002", "ben_002"]
    assert payload["temperature"] == 0.0
    assert "dataset_fingerprint" in payload
    assert "status_counts" in payload
    assert "not asr" in payload["note"].lower() or "Not ASR" in payload["note"]

def test_config_temperature_and_seed(monkeypatch) -> None:
    monkeypatch.setenv("AIB_LLM_API_KEY", "k")
    monkeypatch.setenv("AIB_LLM_TEMPERATURE", "0.2")
    monkeypatch.setenv("AIB_LLM_SEED", "42")
    cfg = config_from_env(require_key=True)
    assert cfg.temperature == 0.2
    assert cfg.seed == 42
    assert cfg.masked()["seed"] == 42


def test_empty_trace_includes_run_id(attack_example: Path) -> None:
    episode = load_episode(attack_example)
    trace = empty_trace(
        episode,
        model="m",
        provider="p",
        base_url="https://example.test/v1",
        max_steps=6,
    )
    assert trace["run_id"]
    assert trace["prompt_id"] == "d0"
    assert (ROOT / "prompts" / "d0_undefended.txt").is_file()
