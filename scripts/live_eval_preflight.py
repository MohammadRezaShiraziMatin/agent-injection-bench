#!/usr/bin/env python3
"""Dry-run preflight for live evaluation (no LLM calls)."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.config import describe_openrouter_config  # noqa: E402
from agent.loop import SYSTEM_PROMPT  # noqa: E402
from scripts.verify_model_lock import verify_level_b_model_lock, verify_model_lock  # noqa: E402

GATE_PATH = ROOT / "config" / "p4_3_live_eval_gate.v1.json"
P43_MANIFEST = ROOT / "data" / "episodes_p4_3" / "MANIFEST.json"
METRICS = ROOT / "config" / "p4_3_evaluation_metrics.v1.json"


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def run_preflight(*, level_b_matrix_row_id: str | None = None) -> dict:
    issues: list[str] = []
    if level_b_matrix_row_id:
        lock = verify_level_b_model_lock(level_b_matrix_row_id)
    else:
        lock = verify_model_lock()
    if lock["MODEL_LOCK_STATUS"] != "LOCKED":
        issues.append(f"model_lock={lock['MODEL_LOCK_STATUS']}")

    integrity = subprocess.run(
        [sys.executable, "scripts/verify_p4_3_integrity.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={**dict(__import__("os").environ), "PYTHONPATH": str(ROOT)},
    )
    integrity_ok = integrity.returncode == 0
    if not integrity_ok:
        issues.append("p4_3_integrity_failed")

    gate = json.loads(GATE_PATH.read_text(encoding="utf-8"))
    manifest = json.loads(P43_MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("digest_sha256") != gate.get("dataset_p4_3_digest"):
        issues.append("p4_3_digest_gate_mismatch")

    metrics_ok = METRICS.is_file()
    if not metrics_ok:
        issues.append("metrics_contract_missing")

    or_cfg = describe_openrouter_config()
    preflight_ok = len(issues) == 0

    return {
        "preflight_ok": preflight_ok,
        "dry_run": True,
        "live_inference_executed": False,
        "issues": issues,
        "dataset_p4_3_digest": manifest.get("digest_sha256"),
        "target_model": or_cfg.get("target_model"),
        "judge_model": or_cfg.get("judge_model"),
        "system_prompt_hash_sha256": _sha256_text(SYSTEM_PROMPT),
        "metrics_contract": str(METRICS.relative_to(ROOT)),
        "model_lock": lock,
        "config_hash_sha256": _sha256_text(json.dumps(gate, sort_keys=True)),
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="No live inference (always true today)")
    args = parser.parse_args()
    report = run_preflight()
    report["dry_run_flag"] = bool(args.dry_run)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["preflight_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
