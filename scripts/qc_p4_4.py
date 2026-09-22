#!/usr/bin/env python3
"""QC, leakage, and reproducibility for the P4.4 independent validation dataset."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.gen_p4_2_dataset import dataset_digest  # noqa: E402
from scripts.qc_p4_2 import acf_fingerprint, normalize_text  # noqa: E402
from scripts.semantic_dedup_p4_1 import extract_surfaces, ngram_jaccard, normalize_surface  # noqa: E402

SCHEMA_PATH = ROOT / "schema" / "episode.p44.v1.json"
DEFAULT_DIR = ROOT / "data" / "episodes_p4_4"
P42_DIR = ROOT / "data" / "episodes_p4_2"
P43_DIR = ROOT / "data" / "episodes_p4_3"
P42_DIGEST = "4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee"
P43_DIGEST = "e60969bee257ec3111febf215fb5f7079edb79ed050dae300e549336184ab53d"
THRESHOLD = 0.88
FAMILIES = {
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


def _paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    for split in ("attack", "benign"):
        paths.extend(sorted((root / split).glob("*.json")))
    return paths


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _fused(ep: dict[str, Any]) -> str:
    return normalize_surface(extract_surfaces(ep).get("_fused", ""))


def run_qc(root: Path, *, check_repro: bool = True) -> dict[str, Any]:
    issues: list[str] = []
    validator = Draft7Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))
    paths = _paths(root)
    episodes = [_load(p) for p in paths]
    attacks = [e for e in episodes if e["split"] == "attack"]
    benigns = [e for e in episodes if e["split"] == "benign"]
    if len(attacks) < 100 or len(benigns) < 100:
        issues.append(f"counts attack={len(attacks)} benign={len(benigns)}")
    if len({e["id"] for e in episodes}) != len(episodes):
        issues.append("duplicate episode ids")
    pairs: dict[str, set[str]] = {}
    for e in episodes:
        pairs.setdefault(e["pair_id"], set()).add(e["split"])
    if len(pairs) < 100:
        issues.append(f"pair count {len(pairs)}")
    if any(v != {"attack", "benign"} for v in pairs.values()):
        issues.append("pair missing attack or benign")
    for path, ep in zip(paths, episodes, strict=True):
        for err in validator.iter_errors(ep):
            loc = "/".join(map(str, err.path)) or "<root>"
            issues.append(f"{path.name}: {loc}: {err.message}")
            break
    payloads = [e["injection"].get("payload", "") for e in attacks]
    if len(payloads) != len(set(payloads)):
        issues.append("duplicate payloads inside P4.4")
    queries = [e["user_query"].strip() for e in attacks]
    if len(queries) != len(set(queries)):
        issues.append("duplicate attack user_query inside P4.4")
    families = Counter(e["taxonomy"]["family"] for e in attacks)
    missing = sorted(FAMILIES - set(families))
    if missing:
        issues.append(f"missing families {missing}")
    criteria = Counter(e["expected"]["success_criterion"] for e in attacks)
    if criteria.get("S1", 0) < 1 or criteria.get("S2", 0) < 1:
        issues.append(f"criterion mix {dict(criteria)}")
    strata = Counter()
    for e in attacks:
        note = e.get("taxonomy", {}).get("objective_note", "")
        if "difficulty_stratum=low" in note:
            strata["low"] += 1
        elif "difficulty_stratum=mid" in note:
            strata["mid"] += 1
        elif "difficulty_stratum=high" in note:
            strata["high"] += 1
    if strata["low"] < 1 or strata["mid"] < 1 or strata["high"] < 1:
        issues.append(f"strata {dict(strata)}")
    hard = 0
    for e in benigns:
        if e["injection"].get("present") is not False:
            issues.append(f"benign injection present {e['id']}")
        if "Hard negative" not in e.get("notes", ""):
            issues.append(f"benign missing hard-negative note {e['id']}")
        else:
            hard += 1
        if e["user_query"].strip() == next(
            a["user_query"].strip() for a in attacks if a["pair_id"] == e["pair_id"]
        ):
            issues.append(f"benign query copies attack {e['id']}")

    prior_attacks: list[dict[str, Any]] = []
    for label, folder in (("P4.2", P42_DIR), ("P4.3", P43_DIR)):
        for p in _paths(folder):
            if p.parent.name == "attack":
                ep = _load(p)
                ep["_corpus"] = label
                prior_attacks.append(ep)
    prior_acf = {acf_fingerprint(e): e["id"] for e in prior_attacks}
    prior_payload = {e["injection"].get("payload", ""): e["id"] for e in prior_attacks}
    prior_query = {normalize_text(e["user_query"]): e["id"] for e in prior_attacks}
    exact_payload = 0
    exact_query = 0
    acf_hits = 0
    near = 0
    worst = 0.0
    for e in attacks:
        if acf_fingerprint(e) in prior_acf:
            acf_hits += 1
            issues.append(f"ACF collision {e['id']} vs {prior_acf[acf_fingerprint(e)]}")
        payload = e["injection"].get("payload", "")
        if payload in prior_payload:
            exact_payload += 1
            issues.append(f"payload collision {e['id']}")
        if normalize_text(e["user_query"]) in prior_query:
            exact_query += 1
            issues.append(f"normalized query collision {e['id']}")
        fused = _fused(e)
        for prior in prior_attacks:
            score = ngram_jaccard(fused, _fused(prior))
            worst = max(worst, score)
            if score >= THRESHOLD:
                near += 1
                issues.append(f"near-duplicate {e['id']} vs {prior['id']} {score:.3f}")
                break
    intra_near = 0
    fused_attacks = [(e["id"], _fused(e)) for e in attacks]
    for i, (ida, fa) in enumerate(fused_attacks):
        for idb, fb in fused_attacks[i + 1 :]:
            score = ngram_jaccard(fa, fb)
            worst = max(worst, score)
            if score >= THRESHOLD:
                intra_near += 1
                issues.append(f"intra near-duplicate {ida} vs {idb} {score:.3f}")
                if intra_near > 5:
                    break
        if intra_near > 5:
            break

    manifest_ok = False
    manifest_path = root / "MANIFEST.json"
    digest = dataset_digest(paths)
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_ok = manifest.get("digest_sha256") == digest
        if not manifest_ok:
            issues.append("manifest digest mismatch")
    else:
        issues.append("MANIFEST.json missing")

    p42_manifest = json.loads((P42_DIR / "MANIFEST.json").read_text(encoding="utf-8"))
    p43_manifest = json.loads((P43_DIR / "MANIFEST.json").read_text(encoding="utf-8"))
    if p42_manifest.get("digest_sha256") != P42_DIGEST:
        issues.append("P4.2 digest changed")
    if p43_manifest.get("digest_sha256") != P43_DIGEST:
        issues.append("P4.3 digest changed")

    byte_identical = None
    if check_repro:
        with tempfile.TemporaryDirectory() as td1, tempfile.TemporaryDirectory() as td2:
            for td in (td1, td2):
                subprocess.run(
                    [sys.executable, "scripts/gen_p4_4_dataset.py", "--out", td],
                    check=True,
                    cwd=ROOT,
                    capture_output=True,
                    env={**os.environ, "PYTHONPATH": str(ROOT)},
                )
            def eps(td: str) -> list[Path]:
                base = Path(td)
                files = sorted((base / "attack").glob("*.json")) + sorted((base / "benign").glob("*.json"))
                return files
            a, b = eps(td1), eps(td2)
            byte_identical = len(a) == len(b) and all(x.read_bytes() == y.read_bytes() for x, y in zip(a, b))
            if not byte_identical:
                issues.append("regen not byte-identical")

    report = {
        "ok": not issues,
        "attack_count": len(attacks),
        "benign_count": len(benigns),
        "pair_count": len(pairs),
        "schema_validation": "PASS" if not any(": " in x and x.endswith for x in []) else None,
        "families": dict(families),
        "criteria": dict(criteria),
        "strata": dict(strata),
        "hard_benign": hard,
        "leakage": {
            "prior_attacks_checked": len(prior_attacks),
            "p44_attacks_checked": len(attacks),
            "exact_payload_collisions": exact_payload,
            "normalized_query_collisions": exact_query,
            "acf_collisions": acf_hits,
            "near_duplicates_vs_prior": near,
            "intra_near_duplicates_capped": intra_near,
            "max_ngram_jaccard_observed": round(worst, 4),
            "threshold": THRESHOLD,
        },
        "digest": digest,
        "manifest_digest_ok": manifest_ok,
        "reproducible": byte_identical,
        "issues": issues[:30],
        "issue_count": len(issues),
    }
    schema_fail = any(p.name.endswith(".json") and ": " in msg for msg in issues for p in paths)
    report["schema_validation"] = "FAIL" if any("/" in msg or msg.endswith(tuple(e["id"]+".json") ) for e in [] ) else (
        "FAIL" if any(x.split(":")[0].endswith(".json") for x in issues) else "PASS"
    )
    if any(x.split(":")[0].endswith(".json") for x in issues):
        report["schema_validation"] = "FAIL"
    return report


def main() -> int:
    report = run_qc(DEFAULT_DIR)
    out = ROOT / "artifacts" / "p4_4_qc_report.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in report if k != "issues"}, indent=2))
    if report["issues"]:
        print("ISSUES")
        for item in report["issues"]:
            print(item)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
