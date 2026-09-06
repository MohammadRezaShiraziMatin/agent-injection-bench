"""Shared path and I/O helpers for v0 stubs. Not an evaluation library."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "episode.schema.json"
EXAMPLES_DIR = ROOT / "examples"
EPISODES_DIR = ROOT / "data" / "episodes"
TRACES_DIR = ROOT / "data" / "traces"


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def dump_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def iter_episode_paths(directories: list[Path]) -> list[Path]:
    paths: list[Path] = []
    for directory in directories:
        if not directory.is_dir():
            continue
        paths.extend(sorted(directory.rglob("*.json")))
    return paths


def load_episodes(directories: list[Path]) -> list[dict[str, Any]]:
    episodes: list[dict[str, Any]] = []
    for path in iter_episode_paths(directories):
        episode = load_json(path)
        if isinstance(episode, dict):
            episode["_path"] = str(path)
            episodes.append(episode)
    return episodes


def load_traces(directory: Path) -> list[dict[str, Any]]:
    """Load trace JSON objects from a directory (non-recursive)."""
    if not directory.is_dir():
        return []
    traces: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json")):
        payload = load_json(path)
        if isinstance(payload, dict):
            payload["_path"] = str(path)
            traces.append(payload)
        elif isinstance(payload, list):
            for item in payload:
                if isinstance(item, dict):
                    item["_path"] = str(path)
                    traces.append(item)
    return traces


def index_episodes_by_id(episodes: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for episode in episodes:
        episode_id = episode.get("id")
        if isinstance(episode_id, str) and episode_id:
            by_id[episode_id] = episode
    return by_id


def tool_call_names(trace: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for call in trace.get("tool_calls") or []:
        if isinstance(call, dict) and isinstance(call.get("name"), str):
            names.append(call["name"])
    return names
