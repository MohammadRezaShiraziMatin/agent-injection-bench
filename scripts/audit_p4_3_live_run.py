#!/usr/bin/env python3
"""Post-live scientific audit (read-only on raw run; corrected analysis separate)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.result_mapper import map_live_result  # noqa: E402
from scripts.score_p4_3_live_metrics import score_run  # noqa: E402

DEFAULT_RUN = ROOT / "results" / "p4_3_live" / "p43-live-20260921-controlled"
P43 = ROOT / "data" / "episodes_p4_3"


def _load_episode(episode_id: str, split: str) -> dict[str, Any]:
    return json.loads((P43 / split / f"{episode_id}.json").read_text(encoding="utf-8"))


def audit_run(run_dir: Path) -> dict[str, Any]:
    results_path = run_dir / "RESULTS.json"
    stored = json.loads(results_path.read_text(encoding="utf-8"))
    disagreements: list[dict[str, Any]] = []
    corrected_rows: list[dict[str, Any]] = []

    for row in stored:
        eid = row["episode_id"]
        split = row["split"]
        ep = _load_episode(eid, split)
        trace = json.loads((run_dir / "target_traces" / f"{eid}.json").read_text(encoding="utf-8"))
        judge = json.loads((run_dir / "judge_outputs" / f"{eid}.json").read_text(encoding="utf-8"))
        parsed = judge.get("parsed") or {}
        mapped = map_live_result(ep, trace, parsed, judge_status=judge.get("status", "JUDGE_FAILURE"))

        corrected = {**row}
        corrected.update(
            {
                "corrected_observed_success_level": mapped["observed_success_level"],
                "corrected_attack_success": mapped["attack_success"],
                "corrected_utility_success": mapped["utility_success"],
                "stored_attack_success": row.get("attack_success"),
                "judge_attack_success": parsed.get("attack_success"),
                "judge_observed_level": parsed.get("observed_success_level"),
            }
        )
        corrected_rows.append(corrected)

        if row.get("expected_success_criterion") == "S1" and row.get("observed_success_level") != "S1":
            disagreements.append(
                {
                    "episode_id": eid,
                    "category": "S1_vs_label",
                    "expected_level": "S1",
                    "stored_observed": row.get("observed_success_level"),
                    "corrected_observed": mapped["observed_success_level"],
                    "root_cause": [],
                }
            )
            causes = disagreements[-1]["root_cause"]
            if row.get("attack_success") != parsed.get("attack_success"):
                causes.append("MAPPER_ignored_judge_attack_success")
            if row.get("observed_success_level") == "S3":
                causes.append("HARNESS_or_JUDGE_treated_allowed_tool_execution_as_S3")
            if mapped["attack_success"] != row.get("attack_success"):
                causes.append("MAPPER_ordinal_attack_success")

    # Write corrected analysis (does not overwrite RESULTS.json)
    corrected_path = ROOT / "artifacts" / "p4_3_live_corrected_analysis.json"
    corrected_path.write_text(
        json.dumps(
            {"run_id": stored[0].get("run_id"), "episodes": corrected_rows, "disagreements": disagreements},
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    # Independent metrics on corrected attack_success
    tmp_results = ROOT / "artifacts" / "_tmp_corrected_results.json"
    for r in corrected_rows:
        r["attack_success"] = r["corrected_attack_success"]
        r["observed_success_level"] = r["corrected_observed_success_level"]
        r["utility_success"] = r.get("corrected_utility_success")
    tmp_results.write_text(json.dumps(corrected_rows, indent=2) + "\n", encoding="utf-8")
    metrics_original = score_run(results_path)
    metrics_corrected = score_run(tmp_results)
    tmp_results.unlink(missing_ok=True)

    return {
        "run_id": stored[0].get("run_id"),
        "n_episodes": len(stored),
        "s1_s3_disagreements": len(disagreements),
        "disagreements": disagreements,
        "metrics_original_stored": metrics_original,
        "metrics_corrected_mapper": metrics_corrected,
        "corrected_analysis_path": str(corrected_path.relative_to(ROOT)),
        "live_rerun_required": False,
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN)
    args = parser.parse_args()
    if not args.run_dir.is_dir():
        print(json.dumps({"ok": False, "error": "run_dir_missing"}, indent=2))
        return 1
    report = audit_run(args.run_dir)
    print(json.dumps({"ok": True, **report}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
