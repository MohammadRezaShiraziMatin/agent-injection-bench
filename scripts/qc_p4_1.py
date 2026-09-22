#!/usr/bin/env python3
"""Quality control for P4.1 candidate dataset (offline)."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "episode.v1.json"
DEFAULT_DIR = ROOT / "data" / "episodes_v1"
GEN_SCRIPT = ROOT / "scripts" / "gen_p4_1_dataset.py"

REQUIRED_FAMILIES = {
    "rag_document_injection",
    "tool_output_injection",
    "multi_turn_injection",
    "cross_context_injection",
    "state_dependent_injection",
    "memory_poisoning",
}


def load_schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def iter_v1_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    for split in ("attack", "benign"):
        d = root / split
        if d.is_dir():
            paths.extend(sorted(d.glob("*.json")))
    return paths


def load_episode(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_schema(episode: dict[str, Any], validator: Draft7Validator) -> list[str]:
    return [
        f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}"
        for e in sorted(validator.iter_errors(episode), key=lambda x: list(x.path))
    ]


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def jaccard(a: str, b: str) -> float:
    ta = set(normalize_text(a).split())
    tb = set(normalize_text(b).split())
    if not ta and not tb:
        return 1.0
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def load_v0_queries() -> set[str]:
    from agent.load import EPISODES_DIR, EXAMPLES_DIR, load_episode

    paths: list[Path] = []
    for split in ("attack", "benign"):
        paths.extend(sorted((EPISODES_DIR / split).glob("*.json")))
    paths.extend(sorted(EXAMPLES_DIR.glob("episode_*.json")))
    return {load_episode(p)["user_query"].strip() for p in paths}


def run_qc(root: Path, *, check_repro: bool = True) -> dict[str, Any]:
    validator = Draft7Validator(load_schema())
    issues: list[str] = []
    warnings: list[str] = []

    paths = iter_v1_paths(root)
    if len(paths) != 20:
        issues.append(f"expected 20 episode JSON files, found {len(paths)}")

    episodes = [load_episode(p) for p in paths]
    ids = [e.get("id") for e in episodes]
    if len(set(ids)) != len(ids):
        issues.append("duplicate episode IDs detected")

    attacks = [e for e in episodes if e.get("split") == "attack"]
    benigns = [e for e in episodes if e.get("split") == "benign"]
    if len(attacks) != 10 or len(benigns) != 10:
        issues.append(f"composition mismatch: attack={len(attacks)} benign={len(benigns)}")

    for path, ep in zip(paths, episodes, strict=True):
        issues.extend([f"{path.name}: {err}" for err in validate_schema(ep, validator)])

    for ep in attacks:
        if not ep.get("injection", {}).get("present"):
            issues.append(f"{ep['id']}: attack episode must have injection.present=true")
    for ep in benigns:
        if ep.get("injection", {}).get("present"):
            issues.append(f"{ep['id']}: benign episode must have injection.present=false")

    v0_queries = load_v0_queries()
    for ep in episodes:
        if ep["user_query"].strip() in v0_queries:
            issues.append(f"{ep['id']}: user_query duplicates v0 episode")

    payloads = [e["injection"].get("payload", "") for e in attacks if e["injection"].get("present")]
    if len(payloads) != len(set(payloads)):
        issues.append("duplicate attack payloads")

    exact_dupes: list[str] = []
    seen: dict[str, str] = {}
    for path, ep in zip(paths, episodes, strict=True):
        blob = json.dumps(ep, sort_keys=True)
        if blob in seen:
            exact_dupes.append(f"{path.name} duplicates {seen[blob]}")
        seen[blob] = path.name
    issues.extend(exact_dupes)

    lexical_pairs: list[str] = []
    for i, ep_i in enumerate(episodes):
        for j in range(i + 1, len(episodes)):
            if ep_i.get("pair_id") and ep_i.get("pair_id") == episodes[j].get("pair_id"):
                continue
            sim = jaccard(ep_i["user_query"], episodes[j]["user_query"])
            if sim >= 0.92:
                lexical_pairs.append(f"{ep_i['id']} vs {episodes[j]['id']} query_jaccard={sim:.2f}")
    if lexical_pairs:
        warnings.extend(lexical_pairs)

    template_counts = Counter()
    for ep in attacks:
        template_counts[ep["taxonomy"]["family"], ep["taxonomy"]["technique"]] += 1
    repeated = [f"{k} x{v}" for k, v in template_counts.items() if v > 2]
    if repeated:
        warnings.append(f"repeated attack templates: {repeated}")

    pair_map: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for ep in episodes:
        pid = ep.get("pair_id")
        if not pid:
            issues.append(f"{ep['id']}: missing pair_id")
            continue
        pair_map[pid][ep["split"]] = ep

    unmatched = [pid for pid, parts in pair_map.items() if set(parts) != {"attack", "benign"}]
    if unmatched:
        issues.append(f"incomplete pairs: {unmatched}")

    for pid, parts in pair_map.items():
        atk, ben = parts["attack"], parts["benign"]
        if atk["user_query"] != ben["user_query"]:
            issues.append(f"{pid}: attack/benign user_query mismatch")
        if atk.get("pair_id") != ben.get("pair_id"):
            issues.append(f"{pid}: pair_id mismatch between twins")
        if ben["injection"].get("present"):
            issues.append(f"{pid}: benign twin has injection.present=true")
        inj_words = normalize_text(atk["injection"].get("payload", ""))
        for doc in ben.get("retrieved_docs", []):
            if inj_words and inj_words in normalize_text(doc.get("text", "")):
                issues.append(f"{pid}: benign doc may contain attack payload text")

    families = {e["taxonomy"]["family"] for e in attacks}
    missing_families = REQUIRED_FAMILIES - families
    if missing_families:
        issues.append(f"missing attack families: {sorted(missing_families)}")

    byte_identical = None
    if check_repro and GEN_SCRIPT.is_file():
        with tempfile.TemporaryDirectory() as td1, tempfile.TemporaryDirectory() as td2:
            for td in (td1, td2):
                subprocess.run(
                    [sys.executable, str(GEN_SCRIPT), "--out", td],
                    check=True,
                    cwd=ROOT,
                    capture_output=True,
                )
            files1 = sorted(Path(td1).rglob("*.json"))
            files2 = sorted(Path(td2).rglob("*.json"))
            if [p.name for p in files1] != [p.name for p in files2]:
                issues.append("reproducibility: file list mismatch between generator runs")
            else:
                byte_identical = all(
                    p.read_bytes() == Path(td2, p.relative_to(td1)).read_bytes() for p in files1
                )
                if not byte_identical:
                    issues.append("reproducibility: byte-identical output = FALSE")

    report = {
        "ok": len(issues) == 0,
        "dataset_version": "P4.1",
        "root": str(root),
        "n_episodes": len(episodes),
        "n_attack": len(attacks),
        "n_benign": len(benigns),
        "families": sorted(families),
        "issues": issues,
        "warnings": warnings,
        "semantic_near_duplicate": "NOT_VERIFIED",
        "byte_identical_regeneration": byte_identical,
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_DIR)
    parser.add_argument("--no-repro", action="store_true")
    args = parser.parse_args()
    report = run_qc(args.root, check_repro=not args.no_repro)
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
