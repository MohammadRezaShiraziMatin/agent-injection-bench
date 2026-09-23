#!/usr/bin/env python3
"""P3-EXT COV-B figures from completed live run (no new experiments)."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.generate_p1_figures import (  # noqa: E402
    D0_LABEL,
    D2_LABEL,
    UTILITY_PROVENANCE,
    render_figures,
)
from scripts.score_p4_3_paired_metrics import score_paired  # noqa: E402

P3_RUN_ID = "p3-cov-b-ext-20260923T112900Z-controlled"


def _default_run_dir() -> Path:
    return (ROOT / "results" / "p3_paired" / P3_RUN_ID).resolve()


def collect_p3_figure_data(run_dir: Path) -> dict:
    manifest = run_dir / "RUN_MANIFEST.json"
    if not manifest.is_file():
        raise SystemExit(f"RUN_MANIFEST missing: {run_dir}")
    run_id = json.loads(manifest.read_text(encoding="utf-8")).get("run_id", "")
    if run_id != P3_RUN_ID:
        raise SystemExit(f"Expected P3 run {P3_RUN_ID}, got {run_id}")

    summary = score_paired(run_dir, append_audit=False)
    if summary.get("mode") != "live":
        raise SystemExit(f"Unexpected run mode: {summary.get('mode')}")

    d0, d2 = summary["D0"], summary["D2"]
    transitions = Counter()
    for row in summary.get("paired_attack_transitions") or []:
        a, b = row.get("d0_attack_success"), row.get("d2_attack_success")
        eid = row.get("episode_id")
        if a is True and b is True:
            transitions["success_to_success"] += 1
        elif a is True and b is False:
            transitions["success_to_failure"] += 1
        elif a is False and b is True:
            transitions["failure_to_success"] += 1
        elif a is False and b is False:
            transitions["failure_to_failure"] += 1
        elif a is None and b is False:
            # D0 judge failure (e.g. atk_p42_045): D2 judged failure → descriptive FF bucket
            transitions["failure_to_failure"] += 1
        else:
            raise SystemExit(f"Unhandled paired transition for {eid}: d0={a!r} d2={b!r}")

    keys = (
        "success_to_success",
        "success_to_failure",
        "failure_to_success",
        "failure_to_failure",
    )
    normalized = {k: transitions.get(k, 0) for k in keys}
    if sum(normalized.values()) != 42:
        raise SystemExit(f"Expected 42 attack transitions, got {sum(normalized.values())}: {normalized}")

    return {
        "descriptive_only": True,
        "population_label": "P3-EXT",
        "coverage_class": "COV-B",
        "run_id": run_id,
        "run_dir": str(run_dir.relative_to(ROOT)) if run_dir.is_relative_to(ROOT) else str(run_dir),
        "metrics_source": "scripts/score_p4_3_paired_metrics.score_paired",
        "utility_provenance": UTILITY_PROVENANCE,
        "population": {
            "attack_episodes_executed": 42,
            "benign_episodes_executed": 42,
            "d0_judge_failures": d0.get("invalid_or_judge_failure", 0),
            "d2_judge_failures": d2.get("invalid_or_judge_failure", 0),
        },
        "ASR": {D0_LABEL: d0["ASR"], D2_LABEL: d2["ASR"]},
        "Utility": {D0_LABEL: d0["Utility"], D2_LABEL: d2["Utility"]},
        "FPR": {D0_LABEL: d0["FPR"], D2_LABEL: d2["FPR"]},
        "paired_transitions": normalized,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate P3-EXT manuscript figures from live run.")
    parser.add_argument("--run-dir", type=Path, default=None)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "docs" / "manuscript" / "figures",
    )
    parser.add_argument("--data-only", action="store_true")
    args = parser.parse_args()

    run_dir = (args.run_dir or _default_run_dir()).resolve()
    out_dir = args.out_dir.resolve()
    data = collect_p3_figure_data(run_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    data_path = out_dir / "p3_figure_data.json"
    data_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if not args.data_only:
        render_figures(
            data,
            out_dir,
            stem_asr="fig_p3_ext_asr_d0_d2",
            stem_util_fpr="fig_p3_ext_utility_fpr_d0_d2",
            stem_transitions="fig_p3_ext_paired_transitions_d0_d2",
            title_asr="P3-EXT ASR (COV-B attacks; valid judged denominators)",
            title_util_fpr="P3-EXT benign utility and FPR (n = 42 benign)",
            title_transitions="P3-EXT D0 → D2 paired outcomes (observed transitions)",
        )

    print(json.dumps({"figure_data": str(data_path.relative_to(ROOT)), "run_dir": data["run_dir"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
