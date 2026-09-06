from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent.errors import EpisodeLoadError
from agent.load import load_episode, load_episode_by_id


def test_load_example_attack(attack_example: Path) -> None:
    episode = load_episode(attack_example)
    assert episode["id"] == "atk_001"
    assert episode["split"] == "attack"
    assert episode["injection"]["present"] is True
    assert episode["user_query"]


def test_load_example_benign(benign_example: Path) -> None:
    episode = load_episode(benign_example)
    assert episode["id"] == "ben_001"
    assert episode["split"] == "benign"
    assert episode["injection"]["present"] is False


def test_load_seed_by_id() -> None:
    episode = load_episode_by_id("atk_002")
    assert episode["id"] == "atk_002"
    assert episode["split"] == "attack"


def test_load_missing_file(tmp_path: Path) -> None:
    with pytest.raises(EpisodeLoadError, match="not found"):
        load_episode(tmp_path / "nope.json")


def test_load_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(EpisodeLoadError, match="invalid JSON"):
        load_episode(path)


def test_load_missing_required_field(tmp_path: Path) -> None:
    path = tmp_path / "partial.json"
    path.write_text(json.dumps({"id": "x", "split": "benign"}), encoding="utf-8")
    with pytest.raises(EpisodeLoadError, match="failed validation"):
        load_episode(path)


def test_load_unknown_id() -> None:
    with pytest.raises(EpisodeLoadError, match="no episode"):
        load_episode_by_id("atk_999")
