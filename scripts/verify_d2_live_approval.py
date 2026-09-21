#!/usr/bin/env python3
"""Verify explicit D2 live-eval approval artifact (offline)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPROVAL_PATH = ROOT / "artifacts" / "p4_3_d2_live_approval.json"
GATE_PATH = ROOT / "config" / "p4_3_d2_eval_gate.v1.json"


def verify_d2_live_approval() -> dict:
    gate = json.loads(GATE_PATH.read_text(encoding="utf-8")) if GATE_PATH.is_file() else {}
    allowed = gate.get("preflight", {}).get("live_d2_inference_allowed", False)
    ref = gate.get("preflight", {}).get("live_d2_approval_artifact")
    if not APPROVAL_PATH.is_file():
        return {
            "D2_LIVE_APPROVAL": "MISSING",
            "ok": False,
            "live_d2_inference_allowed_in_gate": allowed,
        }
    doc = json.loads(APPROVAL_PATH.read_text(encoding="utf-8"))
    explicit = doc.get("status") == "EXPLICIT"
    path_ok = ref is None or ref == str(APPROVAL_PATH.relative_to(ROOT))
    ok = explicit and allowed and path_ok
    return {
        "D2_LIVE_APPROVAL": "EXPLICIT" if ok else "BLOCKED",
        "ok": ok,
        "approval_id": doc.get("approval_id"),
        "approved_at": doc.get("approved_at"),
        "live_d2_inference_allowed_in_gate": allowed,
        "gate_approval_artifact": ref,
    }


def main() -> int:
    print(json.dumps(verify_d2_live_approval(), indent=2, sort_keys=True))
    return 0 if verify_d2_live_approval()["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
