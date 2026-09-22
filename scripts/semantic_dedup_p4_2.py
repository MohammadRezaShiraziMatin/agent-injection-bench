#!/usr/bin/env python3
"""ACF-based semantic near-duplicate screening for P4.2 (offline)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.qc_p4_2 import acf_fingerprint, load_episode, iter_paths
from scripts.semantic_dedup_p4_1 import ngram_jaccard, extract_surfaces, normalize_surface

P42_ROOT = ROOT / "data" / "episodes_p4_2"
V1_ROOT = ROOT / "data" / "episodes_v1"
V0_ROOT = ROOT / "data" / "episodes"
THRESHOLD = 0.88


def load_attacks(root: Path) -> list[dict]:
    return [load_episode(p) for p in iter_paths(root) if p.parent.name == "attack"]


def screen_pairs(a: list[dict], b: list[dict], label: str) -> list[dict]:
    flags: list[dict] = []
    for ea in a:
        sa = normalize_surface(extract_surfaces(ea).get("_fused", ""))
        for eb in b:
            if ea.get("id") == eb.get("id"):
                continue
            sb = normalize_surface(extract_surfaces(eb).get("_fused", ""))
            score = ngram_jaccard(sa, sb)
            if score >= THRESHOLD:
                flags.append(
                    {
                        "pair": label,
                        "a": ea["id"],
                        "b": eb["id"],
                        "ngram_jaccard": round(score, 4),
                    }
                )
    return flags


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=P42_ROOT)
    args = parser.parse_args()
    p42 = load_attacks(args.root)
    p41 = load_attacks(V1_ROOT) if V1_ROOT.is_dir() else []
    v0 = load_attacks(V0_ROOT) if V0_ROOT.is_dir() else []

    acf_self = {}
    acf_dupes = []
    for e in p42:
        fp = acf_fingerprint(e)
        if fp in acf_self:
            acf_dupes.append({"id": e["id"], "dup_of": acf_self[fp]})
        acf_self[fp] = e["id"]

    flags = []
    flags.extend(screen_pairs(p42, p42, "P4.2↔P4.2"))
    flags.extend(screen_pairs(p42, p41, "P4.2↔P4.1"))
    flags.extend(screen_pairs(p42, v0, "P4.2↔v0"))

    report = {
        "ok": len(acf_dupes) == 0,
        "acf_exact_duplicates": acf_dupes,
        "near_duplicate_flags": flags,
        "threshold_ngram_jaccard": THRESHOLD,
        "embedding_semantic_dedup": "not_performed",
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
