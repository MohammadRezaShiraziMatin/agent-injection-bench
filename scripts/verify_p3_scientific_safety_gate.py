#!/usr/bin/env python3
"""Offline P3 scientific safety gate (no live API)."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P3_FREEZE = ROOT / "config" / "p3_experimental_protocol_freeze.v1.json"
P42_FREEZE = ROOT / "config" / "p4_2_primary_research_protocol_freeze.v1.json"
HIST_MANIFEST_SHA = "bd3881779266ed84f186715f0ff64236facc99600bef22bb1958896e91f4fa68"
HIST_RESULTS_SHA = "f7078bf0af7b8294f25c5bc546ce7c554557e9bc08d28d4df3fde1a18772c549"
P3_MANIFEST = ROOT / "artifacts" / "p3_cov_b_extension" / "MANIFEST.json"
D2_GATE = ROOT / "config" / "p4_3_d2_eval_gate.v1.json"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_p3_scientific_safety_gate() -> dict:
    issues: list[str] = []
    checks: dict[str, str] = {}

    if not P3_FREEZE.is_file():
        issues.append("p3_freeze_missing")
    else:
        p3 = json.loads(P3_FREEZE.read_text(encoding="utf-8"))
        checks["protocol_frozen"] = "PASS" if p3.get("status") == "FROZEN" else "FAIL"
        if checks["protocol_frozen"] == "FAIL":
            issues.append("p3_not_frozen")

    if not P3_MANIFEST.is_file():
        issues.append("p3_manifest_missing")
        checks["population_frozen"] = "FAIL"
    else:
        doc = json.loads(P3_MANIFEST.read_text(encoding="utf-8"))
        n = len((doc.get("extension_attack_pool") or {}).get("episodes") or [])
        checks["population_frozen"] = "PASS" if n == 42 else "FAIL"
        if n != 42:
            issues.append(f"p3_population_n={n}")

    if P42_FREEZE.is_file():
        p42 = json.loads(P42_FREEZE.read_text(encoding="utf-8"))
        rel = p42.get("historical_run_immutable")
        run_dir = ROOT / rel if rel else None
        if run_dir and run_dir.is_dir():
            m = run_dir / "RUN_MANIFEST.json"
            r = run_dir / "RESULTS.json"
            if _sha256_file(m) != HIST_MANIFEST_SHA:
                issues.append("historical_manifest_mutated")
                checks["historical_run_protected"] = "FAIL"
            elif _sha256_file(r) != HIST_RESULTS_SHA:
                issues.append("historical_results_mutated")
                checks["historical_run_protected"] = "FAIL"
            else:
                checks["historical_run_protected"] = "PASS"
        else:
            issues.append("historical_run_missing")
            checks["historical_run_protected"] = "FAIL"
    else:
        issues.append("p42_freeze_missing")
        checks["historical_run_protected"] = "UNKNOWN"

    if D2_GATE.is_file():
        gate = json.loads(D2_GATE.read_text(encoding="utf-8"))
        pf = gate.get("preflight") or {}
        p42_pf = gate.get("p4_2_primary_preflight") or {}
        live_off = not pf.get("live_d2_inference_allowed") and not p42_pf.get("live_d2_inference_allowed")
        checks["live_authorization_default_safe"] = "PASS" if live_off else "FAIL"
        if not live_off:
            issues.append("live_d2_gate_not_safe_default")
    else:
        checks["live_authorization_default_safe"] = "UNKNOWN"

    if P3_FREEZE.is_file():
        live = json.loads(P3_FREEZE.read_text(encoding="utf-8")).get("live_execution") or {}
        p3_live_off = not live.get("live_inference_allowed") and not live.get("live_d2_inference_allowed")
        checks["p3_live_flags"] = "PASS" if p3_live_off else "FAIL"
        approval = ROOT / str(live.get("approval_artifact", ""))
        checks["p3_approval_artifact"] = "MISSING" if not approval.is_file() else "PRESENT"
        if not p3_live_off:
            issues.append("p3_live_flags_enabled")

    ok = not issues
    return {
        "P3_SCIENTIFIC_SAFETY_GATE": "PASS" if ok else "BLOCKED",
        "ok": ok,
        "issues": issues,
        "checks": checks,
        "note": "PASS permits dry-run preflight only; live requires separate P3 approval + gate flip.",
    }


def main() -> int:
    report = verify_p3_scientific_safety_gate()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
