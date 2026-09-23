#!/usr/bin/env python3
"""Level B paired D0/D2 runner (dry-run default; live gated by Phase 4 approval chain)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.p4_3_paired_common import (  # noqa: E402
    load_level_b_matrix_target_row,
    load_level_b_primary_run_config,
)
from scripts.run_p4_3_paired_benchmark import run_paired  # noqa: E402
from scripts.verify_level_b_phase4_prelive_gate import (  # noqa: E402
    MODE_LIVE_AUTHORIZED,
    verify_level_b_phase4_prelive_gate,
)

TARGET_ROW_IDS = ("target-level-a-primary", "target-candidate-family-b")


def _apply_matrix_row_env(row: dict[str, Any]) -> None:
    os.environ["OPENROUTER_TARGET_MODEL"] = str(row["model_id"])
    routing = row.get("routing_notes")
    if isinstance(routing, dict):
        order = routing.get("provider_order") or []
        if order:
            os.environ["OPENROUTER_TARGET_PROVIDER_ORDER"] = ",".join(order)
        if routing.get("allow_fallbacks") is False:
            os.environ["OPENROUTER_ALLOW_FALLBACKS"] = "false"


def _row_slug(row_id: str) -> str:
    return row_id.replace("target-", "").replace("-", "_")


def main() -> int:
    parser = argparse.ArgumentParser(description="Level B frozen population paired benchmark")
    parser.add_argument("--run-id", default=None)
    parser.add_argument(
        "--live",
        action="store_true",
        help="Live inference (requires AIB_LEVEL_B_LIVE_EXECUTION=1 and OPENROUTER_API_KEY)",
    )
    parser.add_argument(
        "--matrix-row",
        choices=[*TARGET_ROW_IDS, "both"],
        default="both",
        help="Which matrix target row(s) to evaluate (default: both families)",
    )
    args = parser.parse_args()

    gate_report = verify_level_b_phase4_prelive_gate()
    if args.live:
        if os.environ.get("AIB_LEVEL_B_LIVE_EXECUTION") != "1":
            print(
                json.dumps(
                    {
                        "ok": False,
                        "error": "AIB_LEVEL_B_LIVE_EXECUTION must be 1 for live Level B runs",
                        "level_b_gate": gate_report,
                    },
                    indent=2,
                )
            )
            return 1
        if gate_report.get("mode") != MODE_LIVE_AUTHORIZED or not gate_report.get("ok"):
            print(json.dumps({"ok": False, "level_b_gate": gate_report}, indent=2))
            return 1

    cfg = load_level_b_primary_run_config()
    row_ids = list(TARGET_ROW_IDS) if args.matrix_row == "both" else [args.matrix_row]
    summaries: list[dict[str, Any]] = []

    for row_id in row_ids:
        row = load_level_b_matrix_target_row(row_id)
        _apply_matrix_row_env(row)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        run_id = args.run_id
        if run_id is None:
            suffix = "dry" if not args.live else "controlled"
            run_id = f"level-b-primary-d0-d2-{ts}-{suffix}-{_row_slug(row_id)}"
        elif len(row_ids) > 1:
            run_id = f"{run_id}-{_row_slug(row_id)}"

        report = run_paired(
            run_id=run_id,
            dry_run=not args.live,
            dataset_root=cfg["dataset_root"],
            dataset_digest=cfg["dataset_digest"],
            episode_ids=cfg["episode_ids"],
            out_base=cfg["out_base"],
            dataset_version=cfg["dataset_version"],
            design_manifest=cfg["design_manifest"],
            coverage_by_episode=cfg["coverage_by_episode"],
            protocol_version=cfg["protocol_version"],
            utility_fpr_benign_scope=cfg["utility_fpr_benign_scope"],
            primary_attack_ids=cfg["primary_attack_ids"],
            utility_fpr_benign_episode_ids=cfg["utility_fpr_benign_episode_ids"],
            level_b=True,
        )
        report["matrix_row_id"] = row_id
        report["target_model"] = row.get("model_id")
        summaries.append(report)
        if not report.get("ok"):
            print(json.dumps({"ok": False, "runs": summaries}, indent=2, sort_keys=True))
            return 1

    print(json.dumps({"ok": True, "runs": summaries}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
