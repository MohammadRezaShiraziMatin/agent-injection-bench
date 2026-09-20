from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from jsonschema import Draft7Validator

from scripts.qc_p4_1 import run_qc

ROOT = Path(__file__).resolve().parents[1]
V0_HASHES = json.loads((ROOT / "tests" / "fixtures" / "v0_episode_sha256.json").read_text(encoding="utf-8"))
V1_ROOT = ROOT / "data" / "episodes_v1"
SCHEMA = json.loads((ROOT / "schema" / "episode.v1.json").read_text(encoding="utf-8"))


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v0_episode_files_byte_stable():
    for rel, expected in V0_HASHES.items():
        path = ROOT / rel
        assert path.is_file(), rel
        assert _sha256_file(path) == expected, rel


def test_v0_validation_still_passes():
    proc = subprocess.run(
        [sys.executable, "scripts/validate_episodes.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    report = json.loads(proc.stdout)
    assert report["ok"] is True
    assert report["n"] == 42
    assert report["errors"] == 0


def test_p4_1_episodes_present_and_schema_valid():
    paths = sorted((V1_ROOT / "attack").glob("*.json")) + sorted((V1_ROOT / "benign").glob("*.json"))
    assert len(paths) == 20
    validator = Draft7Validator(SCHEMA)
    for path in paths:
        ep = json.loads(path.read_text(encoding="utf-8"))
        errors = list(validator.iter_errors(ep))
        assert not errors, f"{path.name}: {errors}"


def test_p4_1_qc_passes():
    report = run_qc(V1_ROOT, check_repro=True)
    assert report["ok"] is True
    assert report["byte_identical_regeneration"] is True
    assert report["semantic_near_duplicate"] == "NOT_VERIFIED"


def test_p4_1_generator_deterministic_in_temp():
    with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
        for td in (a, b):
            subprocess.run(
                [sys.executable, "scripts/gen_p4_1_dataset.py", "--out", td],
                cwd=ROOT,
                check=True,
            )
        files_a = sorted(Path(a).rglob("*.json"))
        files_b = sorted(Path(b).rglob("*.json"))
        assert [p.name for p in files_a] == [p.name for p in files_b]
        for pa, pb in zip(files_a, files_b, strict=True):
            assert pa.read_bytes() == pb.read_bytes()


def test_qc_detects_corrupted_fixture():
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(
            [sys.executable, "scripts/gen_p4_1_dataset.py", "--out", td],
            cwd=ROOT,
            check=True,
        )
        bad = Path(td) / "attack" / "atk_p41_01.json"
        ep = json.loads(bad.read_text(encoding="utf-8"))
        ep["injection"]["present"] = False
        bad.write_text(json.dumps(ep, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        report = run_qc(Path(td), check_repro=False)
        assert report["ok"] is False
        assert report["issues"]
