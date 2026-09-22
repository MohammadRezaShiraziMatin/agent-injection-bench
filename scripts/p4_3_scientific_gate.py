#!/usr/bin/env python3
"""Aggregate scientific gate for P4.3 evaluation readiness (offline)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.harness_meta import (  # noqa: E402
    ADAPTIVE_CAPABILITY_LIVE,
    ADAPTIVE_CAPABILITY_STATIC_ONLY,
    MULTI_AGENT_CAPABILITY,
)
from scripts.live_eval_preflight import run_preflight  # noqa: E402
from scripts.verify_model_lock import verify_model_lock  # noqa: E402

P42_DIGEST = "4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee"


def _run(cmd: list[str]) -> dict:
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={**dict(__import__("os").environ), "PYTHONPATH": str(ROOT)},
    )
    try:
        data = json.loads(proc.stdout) if proc.stdout.strip() else {}
    except json.JSONDecodeError:
        data = {"raw_stdout": proc.stdout, "stderr": proc.stderr}
    data["_exit_code"] = proc.returncode
    return data


def main() -> int:
    integrity = _run([sys.executable, "scripts/verify_p4_3_integrity.py"])
    qc = _run([sys.executable, "scripts/qc_p4_3.py"])
    lock = verify_model_lock()
    preflight = run_preflight()

    dataset_status = "PASS" if integrity.get("ok") and qc.get("ok") else "FAIL"
    harness_status = "PARTIALLY_CLOSED"
    eval_status = "PARTIALLY_CLOSED"
    live_status = "BLOCKED"
    model_lock_status = lock["MODEL_LOCK_STATUS"]

    if preflight.get("preflight_ok"):
        live_status = "READY"
    elif lock["MODEL_LOCK_STATUS"] == "BLOCKED":
        live_status = "BLOCKED"

    conditions = []
    if model_lock_status != "LOCKED":
        conditions.append("MODEL_LOCK")
    if not preflight.get("preflight_ok"):
        conditions.append("PREFLIGHT")
    conditions.append("S4_EXTERNAL_NOT_IN_SANDBOX")
    conditions.append("P4_3_S1_N_EQUALS_4_NO_BROAD_STATS")

    if dataset_status == "PASS" and model_lock_status == "LOCKED" and preflight.get("preflight_ok"):
        overall = "PASS"
    elif dataset_status == "PASS":
        overall = "PASS WITH CONDITIONS"
    else:
        overall = "BLOCKED"

    report = {
        "FINAL_GATE": overall,
        "DATASET_STATUS": dataset_status,
        "HARNESS_STATUS": harness_status,
        "EVALUATION_STATUS": eval_status,
        "LIVE_EVIDENCE_STATUS": live_status,
        "MODEL_LOCK_STATUS": model_lock_status,
        "conditions": conditions,
        "P4_2_digest": P42_DIGEST,
        "capabilities": {
            "S3_S4": "sandbox_execution_trace_supported_external_s4_not_claimable",
            "MULTI_AGENT": MULTI_AGENT_CAPABILITY,
            "ADAPTIVE_STATIC": ADAPTIVE_CAPABILITY_STATIC_ONLY,
            "ADAPTIVE_LIVE": ADAPTIVE_CAPABILITY_LIVE,
            "INTER_AGENT_EPISODE_SURFACE": "INTER_AGENT_REPLAY_ONLY",
        },
        "integrity": integrity,
        "qc_p4_3": qc,
        "preflight": preflight,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if overall in ("PASS", "PASS WITH CONDITIONS") else 1


if __name__ == "__main__":
    sys.exit(main())
