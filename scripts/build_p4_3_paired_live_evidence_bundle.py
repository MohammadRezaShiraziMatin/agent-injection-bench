#!/usr/bin/env python3
"""Assemble evidence bundle for paired live D0/D2 run (no secrets)."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def build_bundle(run_dir: Path, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    copies = [
        (ROOT / "config" / "adaptiguard_version_pin.v1.json", "adaptiguard_version_pin.v1.json"),
        (ROOT / "config" / "p4_3_paired_eval_contract.v1.json", "paired_eval_contract.v1.json"),
        (ROOT / "config" / "p4_3_d2_eval_gate.v1.json", "d2_eval_gate.v1.json"),
        (ROOT / "config" / "p4_3_live_eval_gate.v1.json", "live_eval_gate.v1.json"),
        (ROOT / "config" / "p4_3_evaluation_metrics.v1.json", "evaluation_metrics.v1.json"),
        (ROOT / "artifacts" / "openrouter_model_lock_evidence.json", "model_lock_evidence.json"),
        (ROOT / "artifacts" / "p4_3_d2_live_approval.json", "d2_live_approval.json"),
        (ROOT / "artifacts" / "p4_3_live_approval.json", "p4_3_live_approval.json"),
        (ROOT / "artifacts" / "p4_3_paired_live_metrics_summary.json", "paired_live_metrics_summary.json"),
        (run_dir / "RUN_MANIFEST.json", "RUN_MANIFEST.json"),
        (run_dir / "paired" / "PAIRED_INDEX.json", "PAIRED_INDEX.json"),
        (run_dir / "D0" / "RESULTS.json", "D0_RESULTS.json"),
        (run_dir / "D2" / "RESULTS.json", "D2_RESULTS.json"),
    ]
    for src, name in copies:
        if src.is_file():
            shutil.copy2(src, out_dir / name)

    hashes = {p.name: _sha256_file(p) for p in sorted(out_dir.glob("*")) if p.is_file()}
    (out_dir / "HASH_MANIFEST.json").write_text(
        json.dumps(hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return {"ok": True, "bundle_dir": str(out_dir.relative_to(ROOT)), "n_files": len(hashes)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--out", type=Path, default=ROOT / "artifacts" / "p4_3_paired_evidence_bundle")
    args = parser.parse_args()
    print(json.dumps(build_bundle(args.run_dir.resolve(), args.out.resolve()), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
