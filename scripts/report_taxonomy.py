#!/usr/bin/env python3
"""Print attack pattern-family taxonomy distribution (no metrics invention)."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts._common import EPISODES_DIR, load_episodes  # noqa: E402

FAMILIES = (
    "instruction_override",
    "tool_hijack",
    "data_disclosure",
    "workflow_hijack",
    "fake_authorization",
    "urgency_social",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--episodes-dir",
        type=Path,
        default=EPISODES_DIR / "attack",
        help="Attack episodes directory (default: data/episodes/attack)",
    )
    args = parser.parse_args()
    directory = args.episodes_dir if args.episodes_dir.is_absolute() else ROOT / args.episodes_dir
    episodes = load_episodes([directory])
    counts: Counter[str] = Counter()
    missing: list[str] = []
    multi: list[str] = []
    for ep in episodes:
        if ep.get("split") not in (None, "attack"):
            # if loading mixed dirs, only count attack
            if ep.get("split") != "attack":
                continue
        tags = set(ep.get("tags") or [])
        families = [f for f in FAMILIES if f in tags]
        if not families:
            missing.append(str(ep.get("id")))
        elif len(families) > 1:
            multi.append(str(ep.get("id")))
            for f in families:
                counts[f] += 1
        else:
            counts[families[0]] += 1
    summary = {
        "n_attack": len(episodes),
        "families": {f: counts.get(f, 0) for f in FAMILIES},
        "missing_family_tags": missing,
        "multiple_family_tags": multi,
        "note": "Distribution only. Not ASR. See docs/TAXONOMY.md.",
    }
    print(json.dumps(summary, indent=2))
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
