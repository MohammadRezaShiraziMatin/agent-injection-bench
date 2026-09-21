#!/usr/bin/env python3
"""QC for P4.3 additive candidate (offline)."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "episode.p43.v1.json"
DEFAULT_DIR = ROOT / "data" / "episodes_p4_3"
P42_DIR = ROOT / "data" / "episodes_p4_2"
GEN_SCRIPT = ROOT / "scripts" / "gen_p4_3_dataset.py"
N_EXPECTED = 8
N_PAIRS = 4
P42_DIGEST = "4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee"


def iter_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    for split in ("attack", "benign"):
        d = root / split
        if d.is_dir():
            paths.extend(sorted(d.glob("*.json")))
    return paths


def load_episode(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_qc(root: Path) -> dict[str, Any]:
    from scripts.qc_p4_2 import acf_fingerprint

    validator = Draft7Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))
    issues: list[str] = []
    paths = iter_paths(root)
    if len(paths) != N_EXPECTED:
        issues.append(f"expected {N_EXPECTED} episode files, found {len(paths)}")

    episodes = [load_episode(p) for p in paths]
    attacks = [e for e in episodes if e["split"] == "attack"]
    if len(attacks) != N_PAIRS:
        issues.append(f"expected {N_PAIRS} attack episodes")

    for path, ep in zip(paths, episodes, strict=True):
        for err in sorted(validator.iter_errors(ep), key=lambda x: list(x.path)):
            loc = "/".join(map(str, err.path)) or "<root>"
            issues.append(f"{path.name}: {loc}: {err.message}")

    s1 = [e for e in attacks if e["expected"]["success_criterion"] == "S1"]
    if len(s1) != N_PAIRS:
        issues.append(f"expected all {N_PAIRS} attacks to be S1, found {len(s1)}")

    p42_paths = iter_paths(P42_DIR) if P42_DIR.is_dir() else []
    p42_atk = [load_episode(p) for p in p42_paths if p.parent.name == "attack"]
    p42_acf = {acf_fingerprint(e) for e in p42_atk}
    for e in attacks:
        if acf_fingerprint(e) in p42_acf:
            issues.append(f"ACF collision with P4.2: {e['id']}")

    byte_identical = None
    if GEN_SCRIPT.is_file():
        with tempfile.TemporaryDirectory() as td1, tempfile.TemporaryDirectory() as td2:
            for td in (td1, td2):
                subprocess.run(
                    [sys.executable, str(GEN_SCRIPT), "--out", td],
                    check=True,
                    cwd=ROOT,
                    capture_output=True,
                    env={**os.environ, "PYTHONPATH": str(ROOT)},
                )
            f1 = sorted(Path(td1).rglob("*.json"))
            f2 = sorted(Path(td2).rglob("*.json"))
            ep1 = sorted(p for p in f1 if p.name != "MANIFEST.json")
            ep2 = sorted(p for p in f2 if p.name != "MANIFEST.json")
            byte_identical = (
                [str(p.relative_to(td1)) for p in ep1]
                == [str(p.relative_to(td2)) for p in ep2]
                and all(
                    p.read_bytes() == (Path(td2) / p.relative_to(td1)).read_bytes() for p in ep1
                )
            )
            if not byte_identical:
                issues.append("reproducibility: byte-identical regen failed")

    p42_freeze = subprocess.run(
        [sys.executable, "scripts/verify_p4_2_freeze.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    p42_ok = False
    if p42_freeze.returncode == 0:
        data = json.loads(p42_freeze.stdout)
        p42_ok = data.get("digest_sha256") == P42_DIGEST and data.get("ok")

    return {
        "ok": len(issues) == 0 and p42_ok,
        "issues": issues,
        "n_episodes": len(episodes),
        "n_attack": len(attacks),
        "n_benign": len(episodes) - len(attacks),
        "byte_identical_regeneration": byte_identical,
        "p4_2_frozen_digest_ok": p42_ok,
        "p4_2_digest": P42_DIGEST,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_DIR)
    args = parser.parse_args()
    report = run_qc(args.root)
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
