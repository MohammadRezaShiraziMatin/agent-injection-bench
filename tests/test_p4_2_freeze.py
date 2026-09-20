from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.verify_p4_2_freeze import EXPECTED_DIGEST, verify_freeze

ROOT = Path(__file__).resolve().parents[1]
P42_ROOT = ROOT / "data" / "episodes_p4_2"


def test_p4_2_freeze_verification_passes():
    report = verify_freeze(P42_ROOT)
    assert report["ok"] is True, report["issues"]
    assert report["n_episodes"] == 200
    assert report["n_attack"] == 100
    assert report["n_benign"] == 100
    assert report["n_pairs"] == 100
    assert report["digest_sha256"] == EXPECTED_DIGEST


def test_p4_2_verify_script_exits_zero():
    proc = subprocess.run(
        [sys.executable, "scripts/verify_p4_2_freeze.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    report = json.loads(proc.stdout)
    assert report["ok"] is True
