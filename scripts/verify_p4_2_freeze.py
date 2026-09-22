#!/usr/bin/env python3
"""Offline P4.2 dataset freeze verification (episode bytes + MANIFEST digest; no network)."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = ROOT / "data" / "episodes_p4_2"
SCHEMA_PATH = ROOT / "schema" / "episode.v2.json"
EXPECTED_DIGEST = "4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee"
EXPECTED_SEED = 42020260920
EXPECTED_FREEZE_ID = "aib-p4.2-frozen-v1.0"
EXPECTED_COUNTS = {"episodes": 200, "attack": 100, "benign": 100, "pairs": 100}


def fail(issues: list[str], extra: dict[str, Any] | None = None) -> dict[str, Any]:
    report: dict[str, Any] = {"ok": False, "issues": issues}
    if extra:
        report.update(extra)
    return report


def dataset_digest(paths: list[Path]) -> str:
    h = hashlib.sha256()
    for path in sorted(paths, key=lambda p: p.name):
        h.update(path.name.encode("utf-8"))
        h.update(b"\0")
        h.update(path.read_bytes())
    return h.hexdigest()


def verify_freeze(root: Path) -> dict[str, Any]:
    issues: list[str] = []
    manifest_path = root / "MANIFEST.json"
    if not manifest_path.is_file():
        return fail(["MANIFEST.json missing"])

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("dataset_version") != "P4.2":
        issues.append(f"dataset_version={manifest.get('dataset_version')!r}")
    if manifest.get("seed") != EXPECTED_SEED:
        issues.append(f"seed mismatch: {manifest.get('seed')}")
    if manifest.get("digest_sha256") != EXPECTED_DIGEST:
        issues.append(
            f"digest_sha256 mismatch: got {manifest.get('digest_sha256')} expected {EXPECTED_DIGEST}"
        )

    ep_paths = sorted(
        [p for p in root.rglob("*.json") if p.name != "MANIFEST.json"],
        key=lambda p: p.name,
    )
    if len(ep_paths) != EXPECTED_COUNTS["episodes"]:
        issues.append(f"episode file count {len(ep_paths)}")
    computed = dataset_digest(ep_paths)
    if computed != EXPECTED_DIGEST:
        issues.append(f"computed digest mismatch: {computed}")

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft7Validator(schema)
    pair_map: dict[str, dict[str, str]] = defaultdict(dict)
    n_attack = n_benign = 0

    for path in ep_paths:
        ep = json.loads(path.read_text(encoding="utf-8"))
        errs = [e.message for e in validator.iter_errors(ep)]
        if errs:
            issues.append(f"{path.name}: schema: {errs[0]}")
        eid = ep.get("id", path.stem)
        ids_role = ep.get("split", path.parent.name)
        if ids_role == "attack":
            n_attack += 1
        else:
            n_benign += 1
        pid = ep.get("pair_id")
        if pid:
            pair_map[pid][ids_role] = eid

    if n_attack != EXPECTED_COUNTS["attack"]:
        issues.append(f"attack count {n_attack}")
    if n_benign != EXPECTED_COUNTS["benign"]:
        issues.append(f"benign count {n_benign}")
    if len(pair_map) != EXPECTED_COUNTS["pairs"]:
        issues.append(f"pair count {len(pair_map)}")

    return {
        "ok": len(issues) == 0,
        "issues": issues,
        "freeze_id": EXPECTED_FREEZE_ID,
        "dataset_version": "P4.2",
        "digest_sha256": EXPECTED_DIGEST,
        "n_episodes": len(ep_paths),
        "n_attack": n_attack,
        "n_benign": n_benign,
        "n_pairs": len(pair_map),
        "schema_validation": "PASS" if not any("schema" in i for i in issues) else "FAIL",
        "episode_hashes": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()
    report = verify_freeze(args.root)
    print(json.dumps(report, indent=2))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
