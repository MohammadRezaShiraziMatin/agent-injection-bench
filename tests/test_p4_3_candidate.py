from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P42_DIGEST = "4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee"
P43_DIR = ROOT / "data" / "episodes_p4_3"


def test_p4_2_freeze_unchanged():
    proc = subprocess.run(
        [sys.executable, "scripts/verify_p4_2_freeze.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={**dict(__import__("os").environ), "PYTHONPATH": str(ROOT)},
    )
    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert data["digest_sha256"] == P42_DIGEST


def test_p4_3_qc_passes():
    proc = subprocess.run(
        [sys.executable, "scripts/qc_p4_3.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={**dict(__import__("os").environ), "PYTHONPATH": str(ROOT)},
    )
    assert proc.returncode == 0
    report = json.loads(proc.stdout)
    assert report["ok"] is True
    assert report["n_episodes"] == 8


def test_p4_3_integrity_runner():
    proc = subprocess.run(
        [sys.executable, "scripts/verify_p4_3_integrity.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={**dict(__import__("os").environ), "PYTHONPATH": str(ROOT)},
    )
    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert data["ok"] is True


def test_p4_3_s1_attacks():
    atk_dir = P43_DIR / "attack"
    ids = sorted(p.stem for p in atk_dir.glob("*.json"))
    assert len(ids) == 4
    for path in atk_dir.glob("*.json"):
        ep = json.loads(path.read_text(encoding="utf-8"))
        assert ep["expected"]["success_criterion"] == "S1"
        assert ep["taxonomy"]["target"] == "user_response"
