from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.verify_p6_freeze import EXPECTED_DIGEST, verify_freeze

ROOT = Path(__file__).resolve().parents[1]
V1_ROOT = ROOT / "data" / "episodes_v1"


def test_p6_freeze_verification_passes():
    report = verify_freeze(V1_ROOT, check_regen=True)
    assert report["ok"] is True, report["issues"]
    assert report["n_episodes"] == 20
    assert report["n_attack"] == 10
    assert report["n_benign"] == 10
    assert report["n_pairs"] == 10
    assert report["digest_sha256"] == EXPECTED_DIGEST
    assert report["byte_identical_regeneration"] is True


def test_p6_verify_script_exits_zero():
    proc = subprocess.run(
        [sys.executable, "scripts/verify_p6_freeze.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    report = json.loads(proc.stdout)
    assert report["ok"] is True
