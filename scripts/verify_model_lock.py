#!/usr/bin/env python3
"""Verify Target/Judge model lock evidence (offline; no chat inference)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE_PATH = ROOT / "config" / "p4_3_live_eval_gate.v1.json"
EVIDENCE_PATH = ROOT / "artifacts" / "openrouter_model_lock_evidence.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.config import describe_openrouter_config  # noqa: E402


def _gate() -> dict:
    return json.loads(GATE_PATH.read_text(encoding="utf-8"))


def _evidence() -> dict | None:
    if not EVIDENCE_PATH.is_file():
        return None
    return json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))


def _snapshot_ok(role_block: dict, evidence: dict | None) -> bool:
    snap = role_block.get("immutable_snapshot") or {}
    mid = role_block.get("exact_model_id")
    if not mid or not snap.get("catalog_entry_sha256"):
        return False
    if snap.get("catalog_entry_sha256") != (role_block.get("immutable_snapshot") or {}).get(
        "catalog_entry_sha256"
    ):
        return False
    if not evidence:
        return False
    ev = (evidence.get("models") or {}).get(mid)
    if not ev:
        return False
    return ev.get("catalog_entry_sha256") == snap.get("catalog_entry_sha256")


def _routing_ok(role_block: dict) -> bool:
    pol = role_block.get("routing_policy") or {}
    return bool(pol.get("provider_order")) and pol.get("allow_fallbacks") is False


def verify_model_lock() -> dict:
    gate = _gate()
    env = describe_openrouter_config()
    evidence = _evidence()

    target = gate.get("target_model") or {}
    judge = gate.get("judge_model") or {}
    target_id = target.get("exact_model_id")
    judge_id = judge.get("exact_model_id")
    distinct = bool(target_id and judge_id and target_id != judge_id)

    env_target = env.get("target_model")
    env_judge = env.get("judge_model")
    api_ok = env.get("api_key") == "present"

    g2 = bool(target_id and target.get("status") == "LOCKED")
    if env_target and env_target != target_id:
        g2 = False

    g3 = bool(judge_id and judge.get("status") == "LOCKED")
    if env_judge and env_judge != judge_id:
        g3 = False

    fallbacks_ok = env.get("allow_fallbacks") is False
    g4 = (
        distinct
        and _snapshot_ok(target, evidence)
        and _snapshot_ok(judge, evidence)
        and fallbacks_ok
        and _routing_ok(target)
        and _routing_ok(judge)
    )

    env_matches = (
        env_target == target_id
        and env_judge == judge_id
        and bool(env_target)
        and bool(env_judge)
    )
    g10 = g2 and g3 and g4 and api_ok and env_matches

    if g2 and g3 and g4 and g10:
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
            "G4_immutable_catalog_snapshot": "PASS" if g4 else "FAIL",
            "G10_live_eval_readiness": "PASS" if g10 else "FAIL",
        },
        "target_model_id": target_id,
        "judge_model_id": judge_id,
        "env_target_model_id": env_target,
        "env_judge_model_id": env_judge,
        "target_ne_judge": distinct,
        "allow_fallbacks": env.get("allow_fallbacks"),
        "provider_routing_env": env.get("provider_routing"),
        "api_key_present": api_ok,
        "catalog_evidence_path": str(EVIDENCE_PATH.relative_to(ROOT)),
        "upstream_weight_revision": "UNVERIFIED",
        "live_inference_allowed": status == "LOCKED"
        and gate.get("preflight", {}).get("live_inference_allowed", False),
    }


def main() -> int:
    report = verify_model_lock()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["MODEL_LOCK_STATUS"] == "LOCKED" else 1


if __name__ == "__main__":
    sys.exit(main())
