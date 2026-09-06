"""Load and structurally validate episodes. Schema file is not modified."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent.errors import EpisodeLoadError
from scripts._common import (
    EPISODES_DIR,
    EXAMPLES_DIR,
    ROOT,
    SCHEMA_PATH,
    iter_episode_paths,
    load_json,
)

REQUIRED_TOP = (
    "id",
    "split",
    "user_query",
    "retrieved_docs",
    "injection",
    "expected",
)


def _schema_errors(episode: dict[str, Any]) -> list[str]:
    try:
        import jsonschema
    except ImportError:
        return _structural_errors(episode)
    schema = load_json(SCHEMA_PATH)
    validator = jsonschema.Draft7Validator(schema)
    return [
        e.message + f" at {'/'.join(str(p) for p in e.path) or '$'}"
        for e in validator.iter_errors(episode)
    ]


def _structural_errors(episode: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED_TOP:
        if key not in episode:
            errors.append(f"missing required field: {key}")
    if episode.get("split") not in (None, "attack", "benign"):
        errors.append("split must be 'attack' or 'benign'")
    return errors


def load_episode(path: Path | str) -> dict[str, Any]:
    """Load one episode JSON and reject malformed records."""
    file_path = Path(path)
    if not file_path.is_absolute():
        file_path = ROOT / file_path
    if not file_path.is_file():
        raise EpisodeLoadError(f"episode file not found: {file_path}")
    try:
        payload = load_json(file_path)
    except json.JSONDecodeError as exc:
        raise EpisodeLoadError(f"invalid JSON in {file_path}: {exc}") from exc
    except OSError as exc:
        raise EpisodeLoadError(f"cannot read {file_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise EpisodeLoadError(f"episode root must be an object: {file_path}")
    errors = _schema_errors(payload)
    if errors:
        raise EpisodeLoadError(
            f"episode failed validation ({file_path}): " + "; ".join(errors)
        )
    payload = dict(payload)
    payload["_path"] = str(file_path)
    return payload


def load_episode_by_id(
    episode_id: str,
    search_dirs: list[Path] | None = None,
) -> dict[str, Any]:
    directories = search_dirs or [EPISODES_DIR, EXAMPLES_DIR]
    for path in iter_episode_paths(directories):
        try:
            payload = load_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(payload, dict) and payload.get("id") == episode_id:
            return load_episode(path)
    raise EpisodeLoadError(f"no episode with id={episode_id!r} under {directories}")
