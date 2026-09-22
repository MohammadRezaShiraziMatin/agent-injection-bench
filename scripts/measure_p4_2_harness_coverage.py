#!/usr/bin/env python3
"""Print before/after P4.2 harness executability coverage (no dataset mutation)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.harness_coverage import compare_before_after


def main() -> int:
    report = compare_before_after()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
