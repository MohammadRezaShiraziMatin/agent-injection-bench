#!/usr/bin/env python3
"""Build archivable evidence bundle (no secrets, no raw traces by default)."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUNDLE_DIR = ROOT / "artifacts" / "p4_3_evidence_bundle"
RUN_DIR = ROOT / "results" / "p4_3_live" / "p43-live-20260921-controlled"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _scrub_scan(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace").lower()
    flags = []
    for token in ("sk-", "bearer ", "authorization:", "openrouter_api_key"):
        if token in text:
            flags.append(token)
    return flags


def main() -> int:
    BUNDLE_DIR.mkdir(parents=True, exist_ok=True)
    files_to_copy = [
        ROOT / "artifacts" / "p4_3_live_run_pointer.json",
        ROOT / "artifacts" / "p4_3_live_metrics_summary.json",
        ROOT / "artifacts" / "p4_3_live_corrected_analysis.json",
        ROOT / "artifacts" / "openrouter_model_lock_evidence.json",
        ROOT / "artifacts" / "p4_3_live_approval.json",
        ROOT / "config" / "p4_3_live_eval_gate.v1.json",
        ROOT / "config" / "p4_3_evaluation_metrics.v1.json",
        ROOT / "schema" / "evaluation_result.p43.v1.json",
        ROOT / "docs" / "AIB_P4_3_POST_LIVE_VALIDATION_REPORT.md",
    ]
    if RUN_DIR.is_dir():
        files_to_copy.append(RUN_DIR / "RUN_MANIFEST.json")

    hashes: dict[str, str] = {}
    secret_hits: dict[str, list[str]] = {}
    for src in files_to_copy:
        if not src.is_file():
            continue
        dst = BUNDLE_DIR / src.name
        dst.write_bytes(src.read_bytes())
        hashes[src.name] = _sha256_file(dst)
        secret_hits[src.name] = _scrub_scan(dst)

    if any(secret_hits.values()):
        print(json.dumps({"ok": False, "secret_scan_failed": secret_hits}, indent=2))
        return 1

    manifest = {
        "bundle_id": "p4_3_evidence_bundle_v1",
        "files": hashes,
        "raw_traces_included": False,
        "note": "Raw target/judge traces remain under results/p4_3_live/ (gitignored).",
    }
    (BUNDLE_DIR / "HASH_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "bundle_dir": str(BUNDLE_DIR.relative_to(ROOT)), "files": list(hashes)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
