#!/usr/bin/env python3
"""Verify Target/Judge model lock evidence (offline; no inference)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE_PATH = ROOT / "config" / "p4_3_live_eval_gate.v1.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.config import describe_openrouter_config  # noqa: E402


def _gate() -> dict:
    return json.loads(GATE_PATH.read_text(encoding="utf-8"))


def verify_model_lock() -> dict:
    gate = _gate()
    env = describe_openrouter_config()
    target_id = env.get("target_model")
    judge_id = env.get("judge_model")
    api_ok = env.get("api_key") == "present"
    distinct = bool(target_id and judge_id and target_id != judge_id)
    no_fallbacks = env.get("allow_fallbacks") is False
    routing = env.get("provider_routing")

    g2 = bool(target_id and api_ok)
    g3 = bool(judge_id and api_ok)
    g4 = distinct and no_fallbacks and bool(routing)

    snapshots_ok = bool(
        gate.get("target_model", {}).get("immutable_snapshot")
        and gate.get("judge_model", {}).get("immutable_snapshot")
    )

    if g2 and g3 and g4 and snapshots_ok:
        status = "LOCKED"
    elif g2 and g3 and distinct:
        status = "PARTIALLY_LOCKED"
    else:
        status = "BLOCKED"

    return {
        "MODEL_LOCK_STATUS": status,
        "gates": {
            "G2_target_identity": "PASS" if g2 else "FAIL",
            "G3_judge_identity": "PASS" if g3 else "FAIL",
            "G4_routing_and_distinct": "PASS" if g4 else "FAIL",
            "G10_immutable_snapshot": "PASS" if snapshots_ok else "FAIL",
        },
        "target_model_id": target_id,
        "judge_model_id": judge_id,
        "target_ne_judge": distinct,
        "allow_fallbacks": env.get("allow_fallbacks"),
        "provider_routing": routing,
        "api_key_present": api_ok,
        "live_inference_allowed": status == "LOCKED" and gate.get("preflight", {}).get(
            "live_inference_allowed", False
        ),
    }


def main() -> int:
    report = verify_model_lock()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["MODEL_LOCK_STATUS"] == "LOCKED" else 1


if __name__ == "__main__":
    sys.exit(main())
