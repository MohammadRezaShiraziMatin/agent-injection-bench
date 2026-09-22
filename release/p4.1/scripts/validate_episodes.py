#!/usr/bin/env python3
"""Validate all episode JSON files against the frozen schema."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.load import SCHEMA_PATH, iter_episode_paths, load_episode, make_validator, validate_episode


def main() -> int:
    validator = make_validator()
    paths = iter_episode_paths(include_examples=True)
    failures: list[dict[str, object]] = []
    for path in paths:
        ep = load_episode(path)
        errs = validate_episode(ep, validator)
        if errs:
            failures.append({"path": str(path.relative_to(ROOT)), "id": ep.get("id"), "errors": errs})
    report = {
        "ok": len(failures) == 0,
        "n": len(paths),
        "errors": len(failures),
        "schema": str(SCHEMA_PATH),
        "validator": "jsonschema.Draft7Validator",
        "failures": failures,
    }
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
