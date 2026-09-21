from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_live_approval_explicit():
    proc = subprocess.run(
        [sys.executable, "scripts/verify_live_approval.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={**dict(__import__("os").environ), "PYTHONPATH": str(ROOT)},
    )
    data = json.loads(proc.stdout)
    assert data["ok"] is True
    assert data["LIVE_APPROVAL"] == "EXPLICIT"
