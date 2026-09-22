#!/usr/bin/env python3
"""Write P4.4 v2 by revising frozen v1 in memory. Does not write v1, P4.2, or P4.3."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.gen_p4_2_dataset import dataset_digest, episode_records, serialize_episode  # noqa: E402
from scripts.gen_p4_4_dataset import (  # noqa: E402
    FORBIDDEN_OUT,
    GENERATOR_SEED,
    SCHEMA_RELPATH,
    episode_specs,
)
from scripts.p4_4_v2_revision import (  # noqa: E402
    DATASET_VERSION,
    PARENT_DIGEST,
    PARENT_VERSION,
    REVISION_SOURCE,
    V1_DIR,
    apply_decision,
    consistency_errors,
    load_trail,
)
from scripts.qc_p4_4 import _paths  # noqa: E402

DEFAULT_OUT = ROOT / "data" / "episodes_p4_4_v2"
GENERATOR_VERSION = "gen_p4_4_v2_dataset.py@1.0.0"


def _refuse(out_dir: Path) -> None:
    resolved = out_dir.resolve()
    blocked = set(FORBIDDEN_OUT)
    blocked.add(V1_DIR.resolve())
    if resolved in blocked:
        raise SystemExit(f"refusing to write frozen tree {out_dir}")


def _v1_bytes() -> dict[str, bytes]:
    found: dict[str, bytes] = {}
    for path in _paths(V1_DIR):
        found[path.name] = path.read_bytes()
    return found


def assert_v1_reproducible() -> None:
    digest = dataset_digest(_paths(V1_DIR))
    if digest != PARENT_DIGEST:
        raise SystemExit("STOP — IMMUTABLE DATA INTEGRITY FAILURE")
    on_disk = _v1_bytes()
    for episode in episode_specs():
        rendered = serialize_episode(episode).encode("utf-8")
        if on_disk.get(f"{episode['id']}.json") != rendered:
            raise SystemExit("STOP — IMMUTABLE DATA INTEGRITY FAILURE")


def build_v2_episodes() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    assert_v1_reproducible()
    trail = load_trail()
    by_id = {row["episode_id"]: row for row in trail["decisions"]}
    if sum(1 for row in by_id.values() if row["human_decision"] == "REVISE") != 96:
        raise SystemExit("STOP — REVISION AMBIGUITY")
    revised: list[dict[str, Any]] = []
    log: list[dict[str, Any]] = []
    for episode in episode_specs():
        decision = by_id.get(episode["id"])
        if decision is None:
            raise SystemExit("STOP — REVISION AMBIGUITY")
        if episode["split"] == "benign" and decision["human_decision"] != "ACCEPT":
            raise SystemExit("STOP — REVISION AMBIGUITY")
        updated = apply_decision(episode, decision)
        if episode["split"] == "attack":
            errors = consistency_errors(updated)
            if errors:
                raise SystemExit("STOP — REVISION AMBIGUITY")
        revised.append(updated)
        if decision["human_decision"] == "REVISE":
            log.append(
                {
                    "episode_id": episode["id"],
                    "pair_id": episode["pair_id"],
                    "affected_fields": list(decision["affected_fields"]),
                }
            )
    if len(log) != 96:
        raise SystemExit("STOP — REVISION AMBIGUITY")
    return revised, log


def write_dataset(out_dir: Path) -> tuple[list[Path], list[dict[str, Any]]]:
    _refuse(out_dir)
    episodes, log = build_v2_episodes()
    attack_dir = out_dir / "attack"
    benign_dir = out_dir / "benign"
    attack_dir.mkdir(parents=True, exist_ok=True)
    benign_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for episode in episodes:
        folder = attack_dir if episode["split"] == "attack" else benign_dir
        path = folder / f"{episode['id']}.json"
        path.write_text(serialize_episode(episode), encoding="utf-8")
        paths.append(path)
    return sorted(paths), log


def build_manifest(out_dir: Path, paths: list[Path], log: list[dict[str, Any]]) -> dict[str, Any]:
    records = episode_records(out_dir, paths)
    return {
        "attack_count": sum(1 for row in records if row["role"] == "attack"),
        "benign_count": sum(1 for row in records if row["role"] == "benign"),
        "corpus_revision": "v2",
        "dataset_version": DATASET_VERSION,
        "digest_sha256": dataset_digest(paths),
        "episode_count": len(records),
        "episode_schema_dataset_version": PARENT_VERSION,
        "episodes": records,
        "files": [row["filename"] for row in records],
        "freeze_id": "aib-p4.4-validation-v2.0",
        "generator": "scripts/gen_p4_4_v2_dataset.py",
        "generator_version": GENERATOR_VERSION,
        "identity": "P4.4 v2 revision of frozen v1",
        "n_files": len(paths),
        "pair_count": len({row["pair_id"] for row in records}),
        "parent_corpora_not_mutated": [
            "data/episodes_p4_2",
            "data/episodes_p4_3",
            "data/episodes_p4_4",
        ],
        "parent_digest": PARENT_DIGEST,
        "parent_freeze_id": "aib-p4.4-validation-v1.0",
        "parent_version": PARENT_VERSION,
        "revision_count": len(log),
        "revision_scope": "96 attack REVISE rows only; benign and ACCEPT attacks are byte-identical to v1",
        "revision_source": REVISION_SOURCE,
        "revisions": log,
        "schema": SCHEMA_RELPATH,
        "seed": GENERATOR_SEED,
        "status": "frozen",
    }


def write_manifest(out_dir: Path, paths: list[Path], log: list[dict[str, Any]]) -> dict[str, Any]:
    manifest = build_manifest(out_dir, paths, log)
    (out_dir / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the P4.4 v2 revised dataset.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    paths, log = write_dataset(args.out)
    manifest = write_manifest(args.out, paths, log)
    print(
        json.dumps(
            {
                "ok": True,
                "out": str(args.out),
                "n": len(paths),
                "digest": manifest["digest_sha256"],
                "revision_count": manifest["revision_count"],
                "parent_digest": manifest["parent_digest"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
