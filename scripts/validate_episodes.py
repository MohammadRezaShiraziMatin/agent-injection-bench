#!/usr/bin/env python3
"""Validate episode JSON files against schema/episode.schema.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts._common import (  # noqa: E402
    EPISODES_DIR,
    EXAMPLES_DIR,
    SCHEMA_PATH,
    iter_episode_paths,
    load_json,
)


def _load_validator():
    try:
        import jsonschema
    except ImportError:
        print(
            "jsonschema is not installed. Install with: pip install -e .\n"
            "Falling back to a structural check (required keys only).",
            file=sys.stderr,
        )
        return None, None

    schema = load_json(SCHEMA_PATH)
    validator = jsonschema.Draft7Validator(schema)
    return validator, schema


def _structural_errors(episode: dict) -> list[str]:
    errors: list[str] = []
    required = [
        "id",
        "split",
        "user_query",
        "retrieved_docs",
        "injection",
        "expected",
    ]
    for key in required:
        if key not in episode:
            errors.append(f"missing required field: {key}")
    if episode.get("split") not in (None, "attack", "benign"):
        errors.append("split must be 'attack' or 'benign'")
    injection = episode.get("injection")
    if isinstance(injection, dict) and "present" not in injection:
        errors.append("injection.present is required")
    expected = episode.get("expected")
    if isinstance(expected, dict):
        for key in ("allowed_tools", "forbidden_tools"):
            if key not in expected:
                errors.append(f"expected.{key} is required")
    if episode.get("split") == "attack":
        if isinstance(injection, dict) and injection.get("present") is not True:
            errors.append("attack episodes require injection.present=true")
        if isinstance(expected, dict) and not expected.get("forbidden_tools"):
            errors.append("attack episodes require non-empty expected.forbidden_tools")
    if episode.get("split") == "benign":
        if isinstance(injection, dict) and injection.get("present") is not False:
            errors.append("benign episodes require injection.present=false")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Episode files or directories (default: examples/ and data/episodes/)",
    )
    args = parser.parse_args()

    if args.paths:
        directories: list[Path] = []
        files: list[Path] = []
        for path in args.paths:
            path = path if path.is_absolute() else ROOT / path
            if path.is_dir():
                directories.append(path)
            else:
                files.append(path)
        episode_paths = files + iter_episode_paths(directories)
    else:
        episode_paths = iter_episode_paths([EXAMPLES_DIR, EPISODES_DIR])

    if not episode_paths:
        print(
            json.dumps(
                {
                    "ok": True,
                    "n": 0,
                    "errors": 0,
                    "message": "No episode JSON files found.",
                },
                indent=2,
            )
        )
        return 0

    validator, _schema = _load_validator()
    failures: list[dict] = []
    for path in episode_paths:
        try:
            episode = load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            failures.append({"path": str(path), "errors": [str(exc)]})
            continue
        if not isinstance(episode, dict):
            failures.append({"path": str(path), "errors": ["root must be an object"]})
            continue
        errors: list[str] = []
        if validator is not None:
            errors.extend(
                e.message + f" at {'/'.join(str(p) for p in e.path) or '$'}"
                for e in validator.iter_errors(episode)
            )
        else:
            errors.extend(_structural_errors(episode))
        if errors:
            failures.append({"path": str(path), "errors": errors})

    summary = {
        "ok": not failures,
        "n": len(episode_paths),
        "errors": len(failures),
        "schema": str(SCHEMA_PATH),
        "validator": "jsonschema.Draft7Validator" if validator else "structural_fallback",
        "failures": failures,
    }
    print(json.dumps(summary, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
