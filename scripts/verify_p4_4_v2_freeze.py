#!/usr/bin/env python3
"""Freeze check for P4.4 v2. Does not regenerate or modify v1."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.gen_p4_2_dataset import dataset_digest  # noqa: E402
from scripts.p4_4_v2_revision import PARENT_DIGEST, consistency_errors  # noqa: E402
from scripts.qc_p4_4 import P42_DIGEST, P43_DIGEST, _paths  # noqa: E402
from scripts.verify_p4_4_freeze import EXPECTED_DIGEST, EXPECTED_SEED  # noqa: E402

V2 = ROOT / "data" / "episodes_p4_4_v2"
V1 = ROOT / "data" / "episodes_p4_4"
EXPECTED_V2_DIGEST = "8dcf0664729ed4b8f7e0e445180979c2929efc305e9c08787886e738b43ee531"
EPISODE_V2_SCHEMA_SHA256 = "76ac66c72e1cce2c1415add76305c622c5f354e8f6487a82fbed6ade6dd0840d"


def main() -> int:
    issues: list[str] = []
    manifest = json.loads((V2 / "MANIFEST.json").read_text(encoding="utf-8"))
    paths = _paths(V2)
    digest = dataset_digest(paths)
    if digest != EXPECTED_V2_DIGEST or manifest.get("digest_sha256") != EXPECTED_V2_DIGEST:
        issues.append("v2 digest")
    if manifest.get("parent_digest") != PARENT_DIGEST or digest == PARENT_DIGEST:
        issues.append("parent digest")
    if manifest.get("revision_count") != 96 or len(manifest.get("revisions", [])) != 96:
        issues.append("revision count")
    if manifest.get("attack_count") != 100 or manifest.get("benign_count") != 100:
        issues.append("counts")
    if manifest.get("pair_count") != 100:
        issues.append("pairs")
    if manifest.get("seed") != EXPECTED_SEED:
        issues.append("seed")
    if dataset_digest(_paths(V1)) != EXPECTED_DIGEST:
        issues.append("v1 digest")
    schema_hash = hashlib.sha256((ROOT / "schema/episode.v2.json").read_bytes()).hexdigest()
    if schema_hash != EPISODE_V2_SCHEMA_SHA256:
        issues.append("episode.v2.json")
    p42 = json.loads((ROOT / "data/episodes_p4_2/MANIFEST.json").read_text(encoding="utf-8"))
    p43 = json.loads((ROOT / "data/episodes_p4_3/MANIFEST.json").read_text(encoding="utf-8"))
    if p42.get("digest_sha256") != P42_DIGEST or p43.get("digest_sha256") != P43_DIGEST:
        issues.append("parent corpora")
    trail = json.loads((ROOT / "artifacts/p4_4_hr_audit_trail.json").read_text(encoding="utf-8"))
    revise_ids = {row["episode_id"] for row in trail["decisions"] if row["human_decision"] == "REVISE"}
    logged = {row["episode_id"] for row in manifest["revisions"]}
    if revise_ids != logged:
        issues.append("revision ids")
    changed = 0
    for path in paths:
        v1_path = V1 / path.parent.name / path.name
        episode = json.loads(path.read_text(encoding="utf-8"))
        if path.read_bytes() == v1_path.read_bytes():
            if episode["id"] in revise_ids:
                issues.append(f"unchanged revise {episode['id']}")
            continue
        changed += 1
        if episode["id"] not in revise_ids:
            issues.append(f"unexpected edit {episode['id']}")
    for path in paths:
        episode = json.loads(path.read_text(encoding="utf-8"))
        if episode["split"] == "attack" and consistency_errors(episode):
            issues.append(f"consistency {episode['id']}")
    if changed != 96:
        issues.append(f"changed {changed}")
    report = {
        "ok": not issues,
        "freeze_id": "aib-p4.4-validation-v2.0",
        "digest_sha256": digest,
        "parent_digest": PARENT_DIGEST,
        "revision_count": 96,
        "issues": issues,
    }
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
