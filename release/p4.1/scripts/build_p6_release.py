#!/usr/bin/env python3
"""Build a deterministic P4.1 freeze release package (offline, no network)."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "release" / "p4.1"
FREEZE_ID = "aib-p4.1-frozen-v1.0"

# Repo-relative paths required to inspect/reproduce P4.1. Sorted for determinism.
PACKAGE_PATHS: tuple[str, ...] = (
    "data/episodes_v1/MANIFEST.json",
    "data/episodes_v1/attack/atk_p41_01.json",
    "data/episodes_v1/attack/atk_p41_02.json",
    "data/episodes_v1/attack/atk_p41_03.json",
    "data/episodes_v1/attack/atk_p41_04.json",
    "data/episodes_v1/attack/atk_p41_05.json",
    "data/episodes_v1/attack/atk_p41_06.json",
    "data/episodes_v1/attack/atk_p41_07.json",
    "data/episodes_v1/attack/atk_p41_08.json",
    "data/episodes_v1/attack/atk_p41_09.json",
    "data/episodes_v1/attack/atk_p41_10.json",
    "data/episodes_v1/benign/ben_p41_01.json",
    "data/episodes_v1/benign/ben_p41_02.json",
    "data/episodes_v1/benign/ben_p41_03.json",
    "data/episodes_v1/benign/ben_p41_04.json",
    "data/episodes_v1/benign/ben_p41_05.json",
    "data/episodes_v1/benign/ben_p41_06.json",
    "data/episodes_v1/benign/ben_p41_07.json",
    "data/episodes_v1/benign/ben_p41_08.json",
    "data/episodes_v1/benign/ben_p41_09.json",
    "data/episodes_v1/benign/ben_p41_10.json",
    "docs/AIB_P4_1_DATASET_PLAN.md",
    "docs/AIB_P4_1_DATASET_REPORT.md",
    "docs/AIB_P4_ARTIFACT_ARCHIVE_INSPECTION.md",
    "docs/AIB_P4_RECOVERY_REPORT.md",
    "docs/AIB_P5_1_TARGETED_REVISION_REPORT.md",
    "docs/AIB_P5_2_CONDITIONS_CLOSURE_AUDIT.md",
    "docs/AIB_P5_3_SEMANTIC_DEDUP_REPORT.md",
    "docs/AIB_P5_4_1_METADATA_CLOSURE_REPORT.md",
    "docs/AIB_P5_4_HUMAN_ADJUDICATION_REPORT.md",
    "docs/AIB_P5_5_FINAL_SCIENTIFIC_CLOSURE_REPORT.md",
    "docs/AIB_P5_DATASET_QA_REPORT.md",
    "docs/AIB_P6_DATASET_FREEZE_REPORT.md",
    "docs/AIB_P6_DATASET_FREEZE_SPEC.md",
    "docs/AIB_P6_LIMITATIONS_ANNEX.md",
    "schema/episode.v1.json",
    "scripts/build_p6_release.py",
    "scripts/gen_p4_1_dataset.py",
    "scripts/qc_p4_1.py",
    "scripts/semantic_dedup_p4_1.py",
    "scripts/validate_episodes.py",
    "scripts/verify_p6_freeze.py",
    "tests/fixtures/v0_episode_sha256.json",
    "tests/test_p4_1_dataset.py",
    "tests/test_p6_freeze.py",
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_release(out_dir: Path) -> dict[str, Any]:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    records: list[dict[str, Any]] = []
    for rel in PACKAGE_PATHS:
        src = ROOT / rel
        if not src.is_file():
            raise FileNotFoundError(rel)
        dest = out_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        if dest.read_bytes() != src.read_bytes():
            raise RuntimeError(f"copy mismatch: {rel}")
        records.append(
            {
                "byte_size": dest.stat().st_size,
                "path": rel,
                "sha256": sha256_file(dest),
            }
        )

    p41_manifest = json.loads((out_dir / "data" / "episodes_v1" / "MANIFEST.json").read_text(encoding="utf-8"))
    release_manifest = {
        "dataset_version": "P4.1",
        "digest_sha256": p41_manifest["digest_sha256"],
        "file_count": len(records),
        "files": records,
        "freeze_id": FREEZE_ID,
        "identity": "P4.1 controlled reconstruction (not historical P4 recovery)",
        "includes_v0_episodes": False,
        "package": "release/p4.1",
        "schema": "schema/episode.v1.json",
        "seed": p41_manifest["seed"],
    }
    man_path = out_dir / "RELEASE_MANIFEST.json"
    man_path.write_text(json.dumps(release_manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    return release_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build P4.1 P6 release package.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    manifest = build_release(args.out)
    print(
        json.dumps(
            {
                "ok": True,
                "out": "release/p4.1",
                "n": manifest["file_count"],
                "digest": manifest["digest_sha256"],
                "freeze_id": manifest["freeze_id"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
