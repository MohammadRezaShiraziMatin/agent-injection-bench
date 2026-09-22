#!/usr/bin/env python3
"""Audit D0/D2 paired run comparability (same episode, model, digest; defense-only delta)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def audit_run(run_dir: Path) -> dict:
    d0 = json.loads((run_dir / "D0" / "RESULTS.json").read_text(encoding="utf-8"))
    d2 = json.loads((run_dir / "D2" / "RESULTS.json").read_text(encoding="utf-8"))
    manifest = json.loads((run_dir / "RUN_MANIFEST.json").read_text(encoding="utf-8"))
    by_id_d0 = {r["episode_id"]: r for r in d0}
    by_id_d2 = {r["episode_id"]: r for r in d2}
    mismatches: list[dict] = []

    for eid, r0 in by_id_d0.items():
        r2 = by_id_d2.get(eid)
        if not r2:
            mismatches.append({"episode_id": eid, "type": "MISSING_D2"})
            continue
        checks = [
            ("episode_id", r0.get("episode_id"), r2.get("episode_id")),
            ("pair_id", r0.get("pair_id"), r2.get("pair_id")),
            ("input_hash_sha256", r0.get("input_hash_sha256"), r2.get("input_hash_sha256")),
            ("target_model", r0.get("target_model"), r2.get("target_model")),
            ("judge_model", r0.get("judge_model"), r2.get("judge_model")),
            ("dataset_digest", r0.get("dataset_digest"), r2.get("dataset_digest")),
        ]
        for field, a, b in checks:
            if a != b:
                mismatches.append(
                    {"episode_id": eid, "type": "COMPARABILITY_FAILURE", "field": field, "d0": a, "d2": b}
                )
        if r0.get("condition") != "D0" or r2.get("condition") != "D2":
            mismatches.append({"episode_id": eid, "type": "CONDITION_LABEL_MISMATCH"})
        de0 = (r0.get("defense_event") or {}).get("defense_enabled")
        de2 = (r2.get("defense_event") or {}).get("defense_enabled")
        if de0 is not False or de2 is not True:
            mismatches.append(
                {
                    "episode_id": eid,
                    "type": "DEFENSE_FLAG_MISMATCH",
                    "d0_enabled": de0,
                    "d2_enabled": de2,
                }
            )

    status = "PASS" if not mismatches else "FAIL"
    return {
        "comparability_status": status,
        "run_id": manifest.get("run_id"),
        "mode": manifest.get("mode"),
        "n_episodes": len(by_id_d0),
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "dataset_digest": manifest.get("dataset_digest"),
        "target_model": manifest.get("target_model"),
        "judge_model": manifest.get("judge_model"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    report = audit_run(args.run_dir.resolve())
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["comparability_status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
