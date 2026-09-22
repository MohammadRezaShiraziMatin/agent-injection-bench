#!/usr/bin/env python3
"""QC for P4.4 v2 using the P4.4 checker, plus a v2 byte-identical regen."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.p4_4_v2_revision import consistency_errors  # noqa: E402
from scripts.qc_p4_4 import _load, _paths, run_qc  # noqa: E402

V2 = ROOT / "data" / "episodes_p4_4_v2"


def _regen_identical() -> bool:
    with tempfile.TemporaryDirectory() as td1, tempfile.TemporaryDirectory() as td2:
        env = {**os.environ, "PYTHONPATH": str(ROOT)}
        for folder in (td1, td2):
            subprocess.run(
                [sys.executable, "scripts/gen_p4_4_v2_dataset.py", "--out", folder],
                check=True,
                cwd=ROOT,
                capture_output=True,
                env=env,
            )

        def files(folder: str) -> list[Path]:
            base = Path(folder)
            found = sorted((base / "attack").glob("*.json"))
            found += sorted((base / "benign").glob("*.json"))
            found.append(base / "MANIFEST.json")
            return found

        left, right = files(td1), files(td2)
        return len(left) == len(right) and all(
            a.read_bytes() == b.read_bytes() for a, b in zip(left, right)
        )


def main() -> int:
    report = run_qc(V2, check_repro=False)
    for path in _paths(V2):
        episode = _load(path)
        if episode["split"] == "attack":
            for error in consistency_errors(episode):
                report["issues"].append(f"{episode['id']}: {error}")
    report["issue_count"] = len(report["issues"])
    report["metadata_consistency"] = "PASS" if report["issue_count"] == 0 else "FAIL"
    report["reproducible"] = _regen_identical()
    if not report["reproducible"]:
        report["issues"].append("v2 regen not byte-identical")
        report["issue_count"] = len(report["issues"])
    report["ok"] = report["issue_count"] == 0 and report["reproducible"]
    out = ROOT / "artifacts" / "p4_4_v2_qc_report.json"
    payload = {key: value for key, value in report.items() if key != "issues"}
    payload["issues"] = report["issues"]
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in payload if key != "issues"}, indent=2))
    if report["issues"]:
        print("ISSUES")
        for item in report["issues"]:
            print(item)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
