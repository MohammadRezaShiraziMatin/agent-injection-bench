from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from jsonschema import Draft7Validator

from scripts.qc_p4_2 import run_qc

ROOT = Path(__file__).resolve().parents[1]
P42_ROOT = ROOT / "data" / "episodes_p4_2"
SCHEMA = json.loads((ROOT / "schema" / "episode.v2.json").read_text(encoding="utf-8"))


def test_p4_2_episodes_present_and_schema_valid():
    paths = sorted((P42_ROOT / "attack").glob("*.json")) + sorted((P42_ROOT / "benign").glob("*.json"))
    assert len(paths) == 200
    validator = Draft7Validator(SCHEMA)
    for path in paths:
        ep = json.loads(path.read_text(encoding="utf-8"))
        errors = list(validator.iter_errors(ep))
        assert not errors, f"{path.name}: {errors}"


def test_p4_2_qc_passes():
    report = run_qc(P42_ROOT, check_repro=True)
    assert report["ok"] is True
    assert report["byte_identical_regeneration"] is True
    assert report["leakage_ok"] is True
    assert report["embedding_semantic_dedup"] == "not_performed"


def test_p4_2_generator_deterministic_in_temp():
    with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
        for td in (a, b):
            subprocess.run(
                [sys.executable, "scripts/gen_p4_2_dataset.py", "--out", td],
                cwd=ROOT,
                check=True,
            )
        files_a = sorted(p for p in Path(a).rglob("*.json") if p.name != "MANIFEST.json")
        files_b = sorted(p for p in Path(b).rglob("*.json") if p.name != "MANIFEST.json")
        assert [p.name for p in files_a] == [p.name for p in files_b]
        for pa, pb in zip(files_a, files_b, strict=True):
            assert pa.read_bytes() == pb.read_bytes()


def test_p4_1_still_frozen_after_p4_2_artifacts():
    proc = subprocess.run(
        [sys.executable, "scripts/verify_p6_freeze.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    report = json.loads(proc.stdout)
    assert report["ok"] is True
    assert report["digest_sha256"] == "717458789217d4fd29c655e40018471fdaf16b061ff5481cfdc48f7812437ac3"
