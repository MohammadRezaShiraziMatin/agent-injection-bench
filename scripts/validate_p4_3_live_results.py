#!/usr/bin/env python3
"""Validate P4.3 live result records against schema."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema" / "evaluation_result.p43.v1.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path)
    args = parser.parse_args()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = Draft7Validator(schema)
    rows = json.loads(args.results.read_text(encoding="utf-8"))
    issues = []
    for row in rows:
        for err in validator.iter_errors(row):
            issues.append(f"{row.get('episode_id')}: {list(err.path)}: {err.message}")
    print(json.dumps({"ok": not issues, "n": len(rows), "issues": issues}, indent=2))
    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(main())
