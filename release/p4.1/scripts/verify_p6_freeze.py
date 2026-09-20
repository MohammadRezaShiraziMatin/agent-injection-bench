#!/usr/bin/env python3
"""Offline P6 freeze verification for the P4.1 dataset (no network, no LLM)."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = ROOT / "data" / "episodes_v1"
SCHEMA_PATH = ROOT / "schema" / "episode.v1.json"
GEN_SCRIPT = ROOT / "scripts" / "gen_p4_1_dataset.py"
EXPECTED_DIGEST = "717458789217d4fd29c655e40018471fdaf16b061ff5481cfdc48f7812437ac3"
EXPECTED_SEED = 41020260920
EXPECTED_FREEZE_ID = "aib-p4.1-frozen-v1.0"
EXPECTED_COUNTS = {"episodes": 20, "attack": 10, "benign": 10, "pairs": 10}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(issues: list[str], extra: dict[str, Any] | None = None) -> dict[str, Any]:
    report: dict[str, Any] = {"ok": False, "issues": issues}
    if extra:
        report.update(extra)
    return report


def verify_freeze(root: Path, *, check_regen: bool = True) -> dict[str, Any]:
    issues: list[str] = []
    manifest_path = root / "MANIFEST.json"
    if not manifest_path.is_file():
        return fail(["MANIFEST.json missing"])

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("dataset_version") != "P4.1":
        issues.append(f"dataset_version={manifest.get('dataset_version')!r}")
    if manifest.get("seed") != EXPECTED_SEED:
        issues.append(f"seed mismatch: {manifest.get('seed')}")
    if manifest.get("generator") != "scripts/gen_p4_1_dataset.py":
        issues.append(f"generator mismatch: {manifest.get('generator')}")
    if manifest.get("schema") != "schema/episode.v1.json":
        issues.append(f"schema mismatch: {manifest.get('schema')}")
    if manifest.get("freeze_id") != EXPECTED_FREEZE_ID:
        issues.append(f"freeze_id mismatch: {manifest.get('freeze_id')}")
    if manifest.get("digest_sha256") != EXPECTED_DIGEST:
        issues.append(
            f"digest_sha256 mismatch: got {manifest.get('digest_sha256')} expected {EXPECTED_DIGEST}"
        )

    records = manifest.get("episodes")
    files = manifest.get("files")
    if not isinstance(records, list) or len(records) != EXPECTED_COUNTS["episodes"]:
        issues.append(f"episodes records count {0 if not isinstance(records, list) else len(records)}")
        records = records if isinstance(records, list) else []
    if not isinstance(files, list) or len(files) != EXPECTED_COUNTS["episodes"]:
        issues.append(f"files list count {0 if not isinstance(files, list) else len(files)}")
        files = files if isinstance(files, list) else []

    missing = [rel for rel in files if not (root / rel).is_file()]
    if missing:
        issues.append(f"missing files: {missing}")

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft7Validator(schema)
    ids: list[str] = []
    pair_map: dict[str, dict[str, str]] = defaultdict(dict)
    n_attack = n_benign = 0

    for rec in records:
        rel = rec.get("filename")
        if not rel:
            issues.append(f"record missing filename: {rec}")
            continue
        path = root / rel
        if not path.is_file():
            issues.append(f"manifest file missing: {rel}")
            continue
        digest = sha256_file(path)
        size = path.stat().st_size
        if digest != rec.get("sha256"):
            issues.append(f"{rel}: sha256 mismatch")
        if size != rec.get("byte_size"):
            issues.append(f"{rel}: byte_size mismatch ({size} != {rec.get('byte_size')})")
        ep = json.loads(path.read_text(encoding="utf-8"))
        schema_errs = [e.message for e in validator.iter_errors(ep)]
        if schema_errs:
            issues.append(f"{rel}: schema {schema_errs[:3]}")
        eid = ep.get("id")
        ids.append(eid)
        if eid != rec.get("episode_id"):
            issues.append(f"{rel}: episode_id {eid!r} != {rec.get('episode_id')!r}")
        split = ep.get("split")
        if split != rec.get("role"):
            issues.append(f"{rel}: role {rec.get('role')!r} != split {split!r}")
        pid = ep.get("pair_id")
        if pid != rec.get("pair_id"):
            issues.append(f"{rel}: pair_id mismatch")
        if split == "attack":
            n_attack += 1
        elif split == "benign":
            n_benign += 1
        if pid:
            pair_map[pid][split] = eid

    if len(ids) != len(set(ids)):
        issues.append("duplicate episode IDs")
    if n_attack != EXPECTED_COUNTS["attack"] or n_benign != EXPECTED_COUNTS["benign"]:
        issues.append(f"composition attack={n_attack} benign={n_benign}")
    if len(pair_map) != EXPECTED_COUNTS["pairs"]:
        issues.append(f"pair_count={len(pair_map)}")
    unmatched = [pid for pid, parts in pair_map.items() if set(parts) != {"attack", "benign"}]
    if unmatched:
        issues.append(f"incomplete pairs: {unmatched}")

    regen_ok = None
    if check_regen and GEN_SCRIPT.is_file():
        with tempfile.TemporaryDirectory() as td:
            proc = subprocess.run(
                [sys.executable, str(GEN_SCRIPT), "--out", td],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            if proc.returncode != 0:
                issues.append(f"regeneration failed: {proc.stderr[-400:]}")
                regen_ok = False
            else:
                frozen_eps = sorted((root / "attack").glob("*.json")) + sorted((root / "benign").glob("*.json"))
                regen_ok = True
                for frozen in frozen_eps:
                    other = Path(td) / frozen.parent.name / frozen.name
                    if not other.is_file():
                        issues.append(f"regen missing {frozen.name}")
                        regen_ok = False
                    elif other.read_bytes() != frozen.read_bytes():
                        issues.append(f"regen byte mismatch: {frozen.name}")
                        regen_ok = False
                        break
                man_other = Path(td) / "MANIFEST.json"
                if man_other.is_file() and man_other.read_bytes() != manifest_path.read_bytes():
                    issues.append("regen MANIFEST.json byte mismatch vs frozen")
                    regen_ok = False

    report = {
        "ok": len(issues) == 0,
        "dataset_version": "P4.1",
        "freeze_id": manifest.get("freeze_id"),
        "digest_sha256": manifest.get("digest_sha256"),
        "n_episodes": len(ids),
        "n_attack": n_attack,
        "n_benign": n_benign,
        "n_pairs": len(pair_map),
        "schema_validation": "PASS" if not any("schema" in i for i in issues) else "FAIL",
        "episode_hashes": "PASS" if not any("sha256" in i for i in issues) else "FAIL",
        "byte_identical_regeneration": regen_ok,
        "issues": issues,
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify P4.1 P6 freeze integrity (offline).")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--no-regen", action="store_true")
    args = parser.parse_args()
    report = verify_freeze(args.root, check_regen=not args.no_regen)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
