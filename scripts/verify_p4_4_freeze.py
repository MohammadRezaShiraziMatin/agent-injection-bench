#!/usr/bin/env python3
"""Offline freeze check for the P4.4 independent validation dataset."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.gen_p4_2_dataset import dataset_digest  # noqa: E402
from scripts.qc_p4_4 import P42_DIGEST, P43_DIGEST, _paths  # noqa: E402

P44 = ROOT / "data" / "episodes_p4_4"
SCHEMA = ROOT / "schema" / "episode.p44.v1.json"
EXPECTED_DIGEST = "d5132fb3a4897684e1cb8a6f38f7cd367ee2a928bcd351743f73f13c326d796f"
EXPECTED_SEED = 44020260922


def main() -> int:
    issues: list[str] = []
    manifest = json.loads((P44 / "MANIFEST.json").read_text(encoding="utf-8"))
    paths = _paths(P44)
    digest = dataset_digest(paths)
    if digest != EXPECTED_DIGEST or manifest.get("digest_sha256") != EXPECTED_DIGEST:
        issues.append(f"digest {digest}")
    if manifest.get("attack_count") != 100 or manifest.get("benign_count") != 100:
        issues.append("counts")
    if manifest.get("pair_count") != 100:
        issues.append("pairs")
    if manifest.get("seed") != EXPECTED_SEED:
        issues.append("seed")
    if manifest.get("dataset_version") != "P4.4":
        issues.append("version")
    validator = Draft7Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))
    for path in paths:
        ep = json.loads(path.read_text(encoding="utf-8"))
        if any(validator.iter_errors(ep)):
            issues.append(f"schema {path.name}")
            break
    p42 = json.loads((ROOT / "data/episodes_p4_2/MANIFEST.json").read_text(encoding="utf-8"))
    p43 = json.loads((ROOT / "data/episodes_p4_3/MANIFEST.json").read_text(encoding="utf-8"))
    if p42.get("digest_sha256") != P42_DIGEST:
        issues.append("p42 mutated")
    if p43.get("digest_sha256") != P43_DIGEST:
        issues.append("p43 mutated")
    report = {
        "ok": not issues,
        "freeze_id": "aib-p4.4-validation-v1.0",
        "digest_sha256": digest,
        "attack_count": 100,
        "benign_count": 100,
        "pair_count": 100,
        "review_status": "unreviewed",
        "issues": issues,
    }
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
