#!/usr/bin/env python3
"""P4.2.1 near-duplicate flag adjudication (offline, deterministic)."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.qc_p4_2 import acf_fingerprint, load_episode, iter_paths
from scripts.semantic_dedup_p4_1 import (
    extract_surfaces,
    ngram_jaccard,
    normalize_surface,
    payload_skeleton,
)
from scripts.semantic_dedup_p4_2 import THRESHOLD, load_attacks, screen_pairs

TAXONOMY_KEYS = [
    "family",
    "technique",
    "objective",
    "source",
    "target",
    "path",
    "interaction_type",
    "horizon",
    "context_type",
    "tool",
    "memory_state",
]


def episode_index(root: Path) -> dict[str, dict[str, Any]]:
    idx: dict[str, dict[str, Any]] = {}
    for p in iter_paths(root):
        ep = load_episode(p)
        idx[ep["id"]] = ep
    return idx


def taxonomy_signature(ep: dict[str, Any]) -> dict[str, str]:
    tax = ep.get("taxonomy", {})
    return {k: str(tax.get(k, "")) for k in TAXONOMY_KEYS}


def content_blob(ep: dict[str, Any]) -> str:
    return json.dumps(ep, sort_keys=True, ensure_ascii=False)


def mechanism_evidence(ep: dict[str, Any]) -> dict[str, Any]:
    return {
        "user_query": ep.get("user_query", ""),
        "injection_payload": (ep.get("injection") or {}).get("payload", ""),
        "injection_locus": (ep.get("injection") or {}).get("locus", ""),
        "retrieved_docs": [d.get("text", "") for d in ep.get("retrieved_docs", [])],
        "tool_results": [t.get("output", "") for t in ep.get("tool_results", [])],
        "conversation": [t.get("content", "") for t in ep.get("conversation", [])],
        "memory_store": [m.get("value", "") for m in ep.get("memory_store", [])],
        "cross_context": ep.get("cross_context", []),
        "inter_agent_messages": ep.get("inter_agent_messages", []),
        "adaptive_trace": ep.get("adaptive_trace", []),
        "session_state": ep.get("session_state", {}),
    }


def distinguishing_variables(a: dict[str, Any], b: dict[str, Any]) -> list[str]:
    vars_found: list[str] = []
    ev_a, ev_b = mechanism_evidence(a), mechanism_evidence(b)
    for key in ev_a:
        if ev_a[key] != ev_b[key]:
            vars_found.append(key)
    tax_a, tax_b = taxonomy_signature(a), taxonomy_signature(b)
    for key in TAXONOMY_KEYS:
        if tax_a[key] != tax_b[key]:
            vars_found.append(f"taxonomy.{key}")
    return sorted(set(vars_found))


def classify_pair(ea: dict[str, Any], eb: dict[str, Any], ngram_score: float) -> tuple[str, str, str]:
    """Return adjudication, action, rationale."""
    if content_blob(ea) == content_blob(eb):
        return (
            "TRUE_DUPLICATE",
            "REPLACE_OR_REMOVE",
            "Byte-identical episode JSON (exact duplicate).",
        )

    acf_a, acf_b = acf_fingerprint(ea), acf_fingerprint(eb)
    if acf_a == acf_b:
        return (
            "POSSIBLE_DUPLICATE_REQUIRES_HUMAN",
            "KEEP_BOTH",
            "ACF collision without byte identity; requires human disambiguation.",
        )

    dist = distinguishing_variables(ea, eb)
    tax_a, tax_b = taxonomy_signature(ea), taxonomy_signature(eb)
    same_family = tax_a["family"] == tax_b["family"]

    payload_a = payload_skeleton((ea.get("injection") or {}).get("payload", ""))
    payload_b = payload_skeleton((eb.get("injection") or {}).get("payload", ""))

    meaningful = [
        d
        for d in dist
        if d
        not in (
            "retrieved_docs",  # may share template; checked via raw inequality above
        )
    ]

    # Cross-family: document mechanism differences
    if not same_family:
        return (
            "FALSE_POSITIVE",
            "KEEP_BOTH",
            f"N-gram flag with different families ({tax_a['family']} vs {tax_b['family']}); "
            f"distinguishing fields: {', '.join(dist[:8])}.",
        )

    # Same family: scientific variant if any mechanism/content channel differs
    if meaningful:
        if len(meaningful) >= 2 or any(
            m.startswith("taxonomy.") or m in ("cross_context", "inter_agent_messages", "adaptive_trace", "conversation", "injection_payload", "user_query", "tool_results", "memory_store", "session_state")
            for m in meaningful
        ):
            return (
                "VALID_VARIANT",
                "KEEP_BOTH",
                f"Same family with meaningful experimental differences: {', '.join(meaningful[:12])}.",
            )
        return (
            "VALID_VARIANT",
            "KEEP_BOTH",
            f"Controlled variant within {tax_a['family']}; differences: {', '.join(meaningful)}.",
        )

    if payload_a == payload_b and ngram_score >= THRESHOLD:
        return (
            "POSSIBLE_DUPLICATE_REQUIRES_HUMAN",
            "KEEP_BOTH",
            "High n-gram similarity with identical payload skeleton and taxonomy; human review required.",
        )

    return (
        "FALSE_POSITIVE",
        "KEEP_BOTH",
        "N-gram similarity driven by shared normalization template; no distinguishing-variable collapse.",
    )


def reconstruct_flags(root: Path) -> list[dict[str, Any]]:
    attacks = load_attacks(root)
    raw = screen_pairs(attacks, attacks, "P4.2↔P4.2")
    # Canonicalize unordered pair order for stable artifact
    out: list[dict[str, Any]] = []
    for row in raw:
        a, b = row["a"], row["b"]
        if a > b:
            a, b = b, a
        out.append({**row, "a": a, "b": b})
    out.sort(key=lambda r: (r["a"], r["b"]))
    return out


def run_adjudication(root: Path) -> dict[str, Any]:
    idx = episode_index(root)
    flags = reconstruct_flags(root)
    records: list[dict[str, Any]] = []
    counts: dict[str, int] = {}

    for row in flags:
        ea, eb = idx[row["a"]], idx[row["b"]]
        adj, action, rationale = classify_pair(ea, eb, row["ngram_jaccard"])
        counts[adj] = counts.get(adj, 0) + 1
        fused_a = normalize_surface(extract_surfaces(ea).get("_fused", ""))
        fused_b = normalize_surface(extract_surfaces(eb).get("_fused", ""))
        records.append(
            {
                "episode_a": row["a"],
                "episode_b": row["b"],
                "family_a": ea["taxonomy"]["family"],
                "family_b": eb["taxonomy"]["family"],
                "pair_id_a": ea["pair_id"],
                "pair_id_b": eb["pair_id"],
                "similarity_metric": "char_5gram_jaccard_on_normalized_fused_surfaces",
                "similarity_value": row["ngram_jaccard"],
                "threshold": THRESHOLD,
                "acf_status": {
                    "episode_a": acf_fingerprint(ea),
                    "episode_b": acf_fingerprint(eb),
                    "exact_match": acf_fingerprint(ea) == acf_fingerprint(eb),
                },
                "payload_similarity": {
                    "skeleton_a": payload_skeleton((ea.get("injection") or {}).get("payload", "")),
                    "skeleton_b": payload_skeleton((eb.get("injection") or {}).get("payload", "")),
                    "skeleton_equal": payload_skeleton((ea.get("injection") or {}).get("payload", ""))
                    == payload_skeleton((eb.get("injection") or {}).get("payload", "")),
                },
                "taxonomy_comparison": {
                    "a": taxonomy_signature(ea),
                    "b": taxonomy_signature(eb),
                    "equal": taxonomy_signature(ea) == taxonomy_signature(eb),
                },
                "mechanism_comparison": {
                    "distinguishing_variables": distinguishing_variables(ea, eb),
                    "fused_surface_equal_after_normalization": fused_a == fused_b,
                },
                "context_comparison": {
                    "dataset_partition_a": ea.get("dataset_partition"),
                    "dataset_partition_b": eb.get("dataset_partition"),
                },
                "adjudication": adj,
                "action": action,
                "rationale": rationale,
            }
        )

    replacements = sum(1 for r in records if r["action"] not in ("KEEP_BOTH",))

    return {
        "dataset_version": "P4.2",
        "phase": "P4.2.1",
        "flag_count": len(records),
        "threshold_ngram_jaccard": THRESHOLD,
        "embedding_semantic_dedup": "not_performed",
        "adjudication_counts": counts,
        "replacements_required": replacements,
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT / "data" / "episodes_p4_2")
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "artifacts" / "p4_2_1_near_duplicate_adjudication.json",
    )
    args = parser.parse_args()
    report = run_adjudication(args.root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    digest = hashlib.sha256(args.out.read_bytes()).hexdigest()
    print(json.dumps({"ok": True, "flags": report["flag_count"], "out": str(args.out), "sha256": digest, "counts": report["adjudication_counts"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
