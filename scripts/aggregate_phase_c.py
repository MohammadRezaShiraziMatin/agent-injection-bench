#!/usr/bin/env python3
"""Aggregate Phase C matrix runs: ASR L0/L1 + utility + Wilson 95% CI.

Reads results/manifests/*.json (or a plan file listing run_ids). Never invents successes.
rate=null when n=0.
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts._common import load_json  # noqa: E402


def wilson_interval(successes: int, n: int, z: float = 1.96) -> dict[str, float | None]:
    """Wilson score interval for a binomial proportion."""
    if n <= 0:
        return {"low": None, "high": None, "n": 0}
    p = successes / n
    denom = 1.0 + (z * z) / n
    center = (p + (z * z) / (2.0 * n)) / denom
    margin = (z * math.sqrt((p * (1.0 - p) / n) + (z * z) / (4.0 * n * n))) / denom
    return {
        "low": max(0.0, center - margin),
        "high": min(1.0, center + margin),
        "n": n,
    }


def _score(level: int | None, traces_dir: Path) -> dict[str, Any]:
    if level is None:
        cmd = [
            sys.executable,
            str(ROOT / "scripts" / "score_utility.py"),
            "--traces-dir",
            str(traces_dir),
        ]
    else:
        cmd = [
            sys.executable,
            str(ROOT / "scripts" / "score_asr.py"),
            "--level",
            str(level),
            "--traces-dir",
            str(traces_dir),
        ]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return {
            "error": proc.stderr.strip() or proc.stdout.strip() or f"rc={proc.returncode}",
            "n": 0,
            "successes": 0,
            "rate": None,
            "skipped": {},
        }
    return json.loads(proc.stdout)


def _metric_block(raw: dict[str, Any]) -> dict[str, Any]:
    n = int(raw.get("n") or 0)
    successes = int(raw.get("successes") or 0)
    rate = raw.get("rate")
    block = {
        "n": n,
        "successes": successes,
        "rate": rate,
        "skipped": raw.get("skipped") or {},
        "wilson95": wilson_interval(successes, n) if n > 0 else {"low": None, "high": None, "n": 0},
        "message": raw.get("message"),
    }
    if raw.get("error"):
        block["error"] = raw["error"]
    return block


def aggregate_run(manifest: dict[str, Any]) -> dict[str, Any]:
    run_id = str(manifest.get("run_id") or "")
    traces_dir = manifest.get("traces_dir")
    if traces_dir:
        tdir = Path(str(traces_dir))
        if not tdir.is_absolute():
            tdir = ROOT / tdir
    else:
        tdir = ROOT / "results" / "traces" / run_id
    asr0 = _metric_block(_score(0, tdir))
    asr1 = _metric_block(_score(1, tdir))
    util = _metric_block(_score(None, tdir))
    return {
        "run_id": run_id,
        "model": manifest.get("model"),
        "prompt_id": manifest.get("prompt_id") or manifest.get("defense_condition"),
        "defense_condition": manifest.get("defense_condition"),
        "temperature": manifest.get("temperature"),
        "seed": manifest.get("seed"),
        "repeat": manifest.get("repeat"),
        "traces_dir": str(tdir),
        "status_counts": manifest.get("status_counts"),
        "dataset_version": manifest.get("dataset_version"),
        "asr_l0": asr0,
        "asr_l1": asr1,
        "utility": util,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--plan",
        type=Path,
        default=ROOT / "results" / "phase_c_plan.json",
        help="Phase C plan JSON (lists cells with run_id after execution).",
    )
    parser.add_argument(
        "--manifests-dir",
        type=Path,
        default=ROOT / "results" / "manifests",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "results" / "phase_c_summary.json",
    )
    parser.add_argument(
        "--run-ids",
        nargs="*",
        default=None,
        help="Optional explicit run_ids (overrides plan completed cells).",
    )
    args = parser.parse_args()

    manifests_dir = (
        args.manifests_dir if args.manifests_dir.is_absolute() else ROOT / args.manifests_dir
    )
    plan_path = args.plan if args.plan.is_absolute() else ROOT / args.plan
    out_path = args.out if args.out.is_absolute() else ROOT / args.out

    run_ids: list[str] = []
    plan: dict[str, Any] | None = None
    if args.run_ids:
        run_ids = list(args.run_ids)
    elif plan_path.is_file():
        plan = load_json(plan_path)
        for cell in plan.get("cells") or []:
            rid = cell.get("run_id")
            if rid:
                run_ids.append(str(rid))
    else:
        # Fall back: all manifests on disk
        if manifests_dir.is_dir():
            run_ids = [p.stem for p in sorted(manifests_dir.glob("*.json"))]

    cells_out: list[dict[str, Any]] = []
    for run_id in run_ids:
        safe = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in run_id)
        path = manifests_dir / f"{safe}.json"
        if not path.is_file():
            cells_out.append(
                {
                    "run_id": run_id,
                    "error": f"missing manifest: {path}",
                    "asr_l0": {"n": 0, "successes": 0, "rate": None},
                    "asr_l1": {"n": 0, "successes": 0, "rate": None},
                    "utility": {"n": 0, "successes": 0, "rate": None},
                }
            )
            continue
        manifest = load_json(path)
        cells_out.append(aggregate_run(manifest))

    summary = {
        "phase": "C",
        "pilot": True,
        "publication_ready": False,
        "temperature": 0,
        "baselines_in_repo": ["d0", "d1"],
        "d2": "external_only",
        "plan": str(plan_path) if plan_path.is_file() else None,
        "n_cells": len(cells_out),
        "cells": cells_out,
        "message": (
            "Phase C aggregate from disk scorers only. "
            "Wilson 95% CI present only when n>0. "
            "rate=null means undefined, not a measured zero. "
            "Not a published benchmark. No ADAPTI/D2 results invented here."
        ),
    }
    if plan is not None:
        summary["models"] = plan.get("models")
        summary["baselines"] = plan.get("baselines")
        summary["k"] = plan.get("k")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
