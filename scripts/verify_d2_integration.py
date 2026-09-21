#!/usr/bin/env python3
"""Gate 3: AdaptiGuard / D2 integration status (offline)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE_PATH = ROOT / "config" / "p4_3_d2_eval_gate.v1.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.defense.adaptiguard_bridge import integration_status  # noqa: E402


def verify_d2_integration() -> dict:
    gate = json.loads(GATE_PATH.read_text(encoding="utf-8")) if GATE_PATH.is_file() else {}
    status = integration_status()
    integrated = bool(status.get("integrated"))
    live_allowed = gate.get("preflight", {}).get("live_d2_inference_allowed", False)
    ok = integrated and live_allowed
    return {
        "D2_INTEGRATION": "PASS" if integrated else "BLOCKED",
        "LIVE_D2_ALLOWED_IN_GATE": live_allowed,
        "ok": ok,
        "integration": status,
        "gate_id": gate.get("gate_id"),
    }


def main() -> int:
    report = verify_d2_integration()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report.get("integration", {}).get("integrated") else 1


if __name__ == "__main__":
    sys.exit(main())
