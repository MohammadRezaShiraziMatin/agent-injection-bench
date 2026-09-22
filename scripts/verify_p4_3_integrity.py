#!/usr/bin/env python3
"""Verify P4.2 freeze + P4.3 candidate integrity (offline, no network)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P42_DIGEST = "4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee"
P43_DIR = ROOT / "data" / "episodes_p4_3"


def main() -> int:
    p42 = subprocess.run(
        [sys.executable, "scripts/verify_p4_2_freeze.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={**dict(__import__("os").environ), "PYTHONPATH": str(ROOT)},
    )
    p43 = subprocess.run(
        [sys.executable, "scripts/qc_p4_3.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={**dict(__import__("os").environ), "PYTHONPATH": str(ROOT)},
    )
    p42_data = json.loads(p42.stdout) if p42.stdout.strip() else {}
    p43_data = json.loads(p43.stdout) if p43.stdout.strip() else {}
    manifest_path = P43_DIR / "MANIFEST.json"
    p43_digest = None
    if manifest_path.is_file():
        p43_digest = json.loads(manifest_path.read_text(encoding="utf-8")).get("digest_sha256")

    p42_diff = subprocess.run(
        ["git", "diff", "--", "data/episodes_p4_2"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    ok = (
        p42.returncode == 0
        and p43.returncode == 0
        and p42_data.get("digest_sha256") == P42_DIGEST
        and p43_data.get("ok")
        and not (p42_diff.stdout or p42_diff.stderr).strip()
    )
    report = {
        "ok": ok,
        "p4_2": {
            "digest_sha256": p42_data.get("digest_sha256"),
            "expected_digest": P42_DIGEST,
            "git_diff_episodes_p4_2_empty": not bool(p42_diff.stdout.strip()),
        },
        "p4_3": {
            "digest_sha256": p43_digest,
            "qc_ok": p43_data.get("ok"),
            "n_episodes": p43_data.get("n_episodes"),
        },
    }
    print(json.dumps(report, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
