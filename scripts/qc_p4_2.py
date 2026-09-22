#!/usr/bin/env python3
"""Quality control for P4.2 candidate dataset (offline)."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "episode.v2.json"
DEFAULT_DIR = ROOT / "data" / "episodes_p4_2"
GEN_SCRIPT = ROOT / "scripts" / "gen_p4_2_dataset.py"
V1_ROOT = ROOT / "data" / "episodes_v1"
V0_ROOT = ROOT / "data" / "episodes"
N_EXPECTED = 200
N_PAIRS = 100

REQUIRED_FAMILIES = {
    "direct_prompt_injection",
    "indirect_prompt_injection",
    "multi_turn_injection",
    "rag_document_injection",
    "web_retrieved_content_injection",
    "tool_output_injection",
    "memory_state_injection",
    "cross_context_injection",
    "multi_agent_injection",
    "adaptive_injection",
}


def load_schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def iter_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    for split in ("attack", "benign"):
        d = root / split
        if d.is_dir():
            paths.extend(sorted(d.glob("*.json")))
    return paths


def load_episode(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def acf_fingerprint(ep: dict[str, Any]) -> str:
    """Attack Content Fingerprint (deterministic)."""
    parts: list[str] = []
    parts.append(ep.get("user_query", ""))
    for d in ep.get("retrieved_docs", []):
        parts.append(d.get("text", ""))
    inj = ep.get("injection") or {}
    if inj.get("payload"):
        parts.append(inj["payload"])
    for tr in ep.get("tool_results", []):
        parts.append(tr.get("output", ""))
    for t in ep.get("conversation", []):
        parts.append(t.get("content", ""))
    for m in ep.get("memory_store", []):
        parts.append(m.get("value", ""))
    for c in ep.get("cross_context", []):
        parts.append(c.get("text", ""))
    blob = normalize_text("\n".join(parts))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def load_prior_episodes(root: Path, pattern: str) -> list[dict[str, Any]]:
    eps: list[dict[str, Any]] = []
    for split in ("attack", "benign"):
        for path in sorted((root / split).glob(pattern)):
            eps.append(load_episode(path))
    return eps


def run_leakage(episodes: list[dict[str, Any]]) -> dict[str, Any]:
    issues: list[str] = []
    by_part: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for ep in episodes:
        by_part[ep["dataset_partition"]].append(ep)

    def check_pair(a_eps: list[dict[str, Any]], b_eps: list[dict[str, Any]], label: str) -> None:
        a_atk = [e for e in a_eps if e["split"] == "attack"]
        b_atk = [e for e in b_eps if e["split"] == "attack"]
        a_acf = {acf_fingerprint(e): e["id"] for e in a_atk}
        for e in b_atk:
            fp = acf_fingerprint(e)
            if fp in a_acf:
                issues.append(f"{label}: ACF collision {a_acf[fp]} vs {e['id']}")
        for ea in a_atk:
            for eb in b_atk:
                if ea["user_query"].strip() == eb["user_query"].strip():
                    issues.append(f"{label}: identical user_query {ea['id']} vs {eb['id']}")
                pa = ea.get("injection", {}).get("payload", "")
                pb = eb.get("injection", {}).get("payload", "")
                if pa and pa == pb:
                    issues.append(f"{label}: identical payload {ea['id']} vs {eb['id']}")

    check_pair(by_part["development"], by_part["validation"], "dev↔validation")
    check_pair(by_part["development"], by_part["test"], "dev↔test")
    check_pair(by_part["validation"], by_part["test"], "validation↔test")

    p42_atk = [e for e in episodes if e["split"] == "attack"]
    for prior_root, tag in ((V1_ROOT, "P4.1"), (V0_ROOT, "v0")):
        if not prior_root.is_dir():
            continue
        prior = load_prior_episodes(prior_root, "*.json")
        prior_q = {e["user_query"].strip() for e in prior}
        for e in p42_atk:
            if e["user_query"].strip() in prior_q:
                issues.append(f"{tag}↔P4.2: user_query overlap with prior dataset ({e['id']})")
        prior_acf = {acf_fingerprint(e) for e in prior if e.get("split") == "attack"}
        for e in p42_atk:
            if acf_fingerprint(e) in prior_acf:
                issues.append(f"{tag}↔P4.2: ACF overlap {e['id']}")

    return {"ok": len(issues) == 0, "issues": issues}


def run_qc(root: Path, *, check_repro: bool = True) -> dict[str, Any]:
    validator = Draft7Validator(load_schema())
    issues: list[str] = []
    warnings: list[str] = []

    paths = iter_paths(root)
    if len(paths) != N_EXPECTED:
        issues.append(f"expected {N_EXPECTED} episode JSON files, found {len(paths)}")

    episodes = [load_episode(p) for p in paths]
    if len({e.get("id") for e in episodes}) != len(episodes):
        issues.append("duplicate episode IDs")

    attacks = [e for e in episodes if e.get("split") == "attack"]
    benigns = [e for e in episodes if e.get("split") == "benign"]
    if len(attacks) != N_PAIRS or len(benigns) != N_PAIRS:
        issues.append(f"composition mismatch: attack={len(attacks)} benign={len(benigns)}")

    for path, ep in zip(paths, episodes, strict=True):
        for err in sorted(validator.iter_errors(ep), key=lambda x: list(x.path)):
            loc = "/".join(map(str, err.path)) or "<root>"
            issues.append(f"{path.name}: {loc}: {err.message}")

    payloads = [
        e["injection"].get("payload", "")
        for e in attacks
        if e.get("injection", {}).get("present")
    ]
    if len(payloads) != len(set(payloads)):
        dupes = [p for p, c in Counter(payloads).items() if c > 1]
        issues.append(f"duplicate attack payloads: {len(dupes)} duplicates")

    pair_map: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for ep in episodes:
        pid = ep.get("pair_id")
        if not pid:
            issues.append(f"{ep['id']}: missing pair_id")
            continue
        pair_map[pid][ep["split"]] = ep

    for pid, parts in pair_map.items():
        if set(parts) != {"attack", "benign"}:
            issues.append(f"incomplete pair {pid}")
            continue
        atk, ben = parts["attack"], parts["benign"]
        if atk["dataset_partition"] != ben["dataset_partition"]:
            issues.append(f"{pid}: partition mismatch")
        if ben["injection"].get("present"):
            issues.append(f"{pid}: benign has injection")

    families = {e["taxonomy"]["family"] for e in attacks}
    missing = REQUIRED_FAMILIES - families
    if missing:
        issues.append(f"missing attack families: {sorted(missing)}")

    acf_counts = Counter(acf_fingerprint(e) for e in attacks)
    acf_dupes = [fp for fp, c in acf_counts.items() if c > 1]
    if acf_dupes:
        issues.append(f"intra-P4.2 ACF duplicates among attacks: {len(acf_dupes)}")

    leakage = run_leakage(episodes)
    issues.extend(leakage["issues"])

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
            ep_files1 = [p for p in files1 if p.name != "MANIFEST.json"]
            ep_files2 = [p for p in files2 if p.name != "MANIFEST.json"]
            byte_identical = (
                [p.name for p in ep_files1] == [p.name for p in ep_files2]
                and all(
                    p.read_bytes() == Path(td2, p.relative_to(td1)).read_bytes() for p in ep_files1
                )
            )
            if not byte_identical:
                issues.append("reproducibility: byte-identical episode output = FALSE")

    manifest_path = root / "MANIFEST.json"
    manifest_ok = None
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        ep_paths = [p for p in paths]
        expected_digest = manifest.get("digest_sha256")
        h = hashlib.sha256()
        for path in sorted(ep_paths, key=lambda p: p.name):
            h.update(path.name.encode("utf-8"))
            h.update(b"\0")
            h.update(path.read_bytes())
        manifest_ok = h.hexdigest() == expected_digest
        if not manifest_ok:
            issues.append("MANIFEST digest_sha256 mismatch")

    return {
        "ok": len(issues) == 0,
        "n_episodes": len(episodes),
        "n_attack": len(attacks),
        "n_benign": len(benigns),
        "n_pairs": len(pair_map),
        "issues": issues,
        "warnings": warnings,
        "leakage_ok": leakage["ok"],
        "byte_identical_regeneration": byte_identical,
        "manifest_digest_ok": manifest_ok,
        "embedding_semantic_dedup": "not_performed",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_DIR)
    parser.add_argument("--no-repro", action="store_true")
    args = parser.parse_args()
    report = run_qc(args.root, check_repro=not args.no_repro)
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
