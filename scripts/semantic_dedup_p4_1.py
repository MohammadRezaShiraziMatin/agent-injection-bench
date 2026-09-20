#!/usr/bin/env python3
"""Offline semantic-near-duplicate screening for P4.1 (no network, no LLM).

Method: Attack Content Fingerprint (ACF) — deterministic normalization, structural
signatures, and character n-gram Jaccard on fused attack-relevant text surfaces.

See docs/AIB_P5_3_SEMANTIC_DEDUP_REPORT.md for thresholds and limitations.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.load import EPISODES_DIR, EXAMPLES_DIR, load_episode
from scripts.qc_p4_1 import jaccard, load_episode as load_v1, normalize_text

V1_ROOT = ROOT / "data" / "episodes_v1"
NGRAM_N = 5
# High overlap on fused surfaces → flag for human review (not auto-delete).
# Rationale: 5-gram Jaccard ≥0.88 implies ≥88% overlap of character 5-grams,
# stricter than word-level Jaccard on queries alone (QC uses 0.92 on queries only).
THRESHOLD_POSSIBLE = 0.88
# Payload skeleton overlap (attack episodes).
THRESHOLD_PAYLOAD_POSSIBLE = 0.85


EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
NUM_RE = re.compile(r"\b\d+(?:\.\d+)?\b")
PUNCT_RE = re.compile(r"[^\w\s]+", re.UNICODE)


def normalize_surface(text: str) -> str:
    t = text.lower()
    t = EMAIL_RE.sub("<email>", t)
    t = NUM_RE.sub("<num>", t)
    t = PUNCT_RE.sub(" ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def payload_skeleton(payload: str) -> str:
    return normalize_surface(payload)


def char_ngrams(text: str, n: int) -> set[str]:
    if len(text) < n:
        return {text} if text else set()
    return {text[i : i + n] for i in range(len(text) - n + 1)}


def ngram_jaccard(a: str, b: str, n: int = NGRAM_N) -> float:
    na, nb = char_ngrams(a, n), char_ngrams(b, n)
    if not na and not nb:
        return 1.0
    if not na or not nb:
        return 0.0
    return len(na & nb) / len(na | nb)


def extract_surfaces(ep: dict[str, Any]) -> dict[str, str]:
    parts: list[str] = []
    out: dict[str, str] = {}
    if ep.get("user_query"):
        out["user_query"] = ep["user_query"]
        parts.append(ep["user_query"])
    doc_texts = [d.get("text", "") for d in ep.get("retrieved_docs", [])]
    if doc_texts:
        out["retrieved_docs"] = "\n".join(doc_texts)
        parts.extend(doc_texts)
    for tr in ep.get("tool_results", []):
        parts.append(tr.get("output", ""))
    if ep.get("tool_results"):
        out["tool_results"] = "\n".join(tr.get("output", "") for tr in ep["tool_results"])
    for turn in ep.get("conversation", []):
        parts.append(turn.get("content", ""))
    if ep.get("conversation"):
        out["conversation"] = "\n".join(t.get("content", "") for t in ep["conversation"])
    for m in ep.get("memory_store", []):
        parts.append(m.get("value", ""))
    if ep.get("memory_store"):
        out["memory_store"] = "\n".join(m.get("value", "") for m in ep["memory_store"])
    for cx in ep.get("cross_context", []):
        parts.append(cx.get("text", ""))
    if ep.get("cross_context"):
        out["cross_context"] = "\n".join(c.get("text", "") for c in ep["cross_context"])
    inj = ep.get("injection") or {}
    if inj.get("payload"):
        out["injection.payload"] = inj["payload"]
        parts.append(inj["payload"])
    out["_fused"] = "\n".join(p for p in parts if p)
    return out


def content_fingerprint(ep: dict[str, Any]) -> str:
    fused = normalize_surface(extract_surfaces(ep)["_fused"])
    return hashlib.sha256(fused.encode("utf-8")).hexdigest()


def attack_signature(ep: dict[str, Any]) -> tuple[str, ...] | None:
    if ep.get("split") != "attack":
        return None
    tax = ep.get("taxonomy") or {}
    inj = ep.get("injection") or {}
    payload = payload_skeleton(inj.get("payload", ""))
    return (
        tax.get("family", ""),
        tax.get("source", ""),
        inj.get("locus", ""),
        inj.get("target_tool", ""),
        payload,
    )


@dataclass
class Flag:
    id_a: str
    id_b: str
    corpus: str
    classification: str
    metric: str
    score: float
    fields: str
    reason: str


def compare_pair(
    ep_a: dict[str, Any],
    ep_b: dict[str, Any],
    *,
    corpus: str,
    skip_twin: bool = False,
) -> list[Flag]:
    if skip_twin and ep_a.get("pair_id") and ep_a.get("pair_id") == ep_b.get("pair_id"):
        return []
    flags: list[Flag] = []
    id_a, id_b = ep_a["id"], ep_b["id"]

    fp_a, fp_b = content_fingerprint(ep_a), content_fingerprint(ep_b)
    if fp_a == fp_b:
        flags.append(
            Flag(id_a, id_b, corpus, "DUPLICATE", "content_sha256", 1.0, "_fused", "Identical normalized fused surfaces")
        )
        return flags

    sig_a, sig_b = attack_signature(ep_a), attack_signature(ep_b)
    if sig_a and sig_b and sig_a == sig_b:
        flags.append(
            Flag(
                id_a,
                id_b,
                corpus,
                "DUPLICATE",
                "attack_signature",
                1.0,
                "taxonomy+payload_skeleton",
                "Identical attack structural signature",
            )
        )

    surf_a = normalize_surface(extract_surfaces(ep_a)["_fused"])
    surf_b = normalize_surface(extract_surfaces(ep_b)["_fused"])
    ng = ngram_jaccard(surf_a, surf_b)
    if ng >= THRESHOLD_POSSIBLE:
        flags.append(
            Flag(
                id_a,
                id_b,
                corpus,
                "POSSIBLE_NEAR_DUPLICATE",
                f"char_{NGRAM_N}gram_jaccard",
                round(ng, 4),
                "_fused",
                "High character n-gram overlap on fused attack-relevant surfaces",
            )
        )

    if ep_a.get("split") == "attack" and ep_b.get("split") == "attack":
        pa = payload_skeleton((ep_a.get("injection") or {}).get("payload", ""))
        pb = payload_skeleton((ep_b.get("injection") or {}).get("payload", ""))
        if pa and pb:
            pj = ngram_jaccard(pa, pb, n=4)
            if pj >= THRESHOLD_PAYLOAD_POSSIBLE and not any(
                f.metric == "attack_signature" and f.classification == "DUPLICATE" for f in flags
            ):
                flags.append(
                    Flag(
                        id_a,
                        id_b,
                        corpus,
                        "POSSIBLE_NEAR_DUPLICATE",
                        "payload_4gram_jaccard",
                        round(pj, 4),
                        "injection.payload",
                        "High payload skeleton overlap",
                    )
                )

    return flags


def load_v1_episodes() -> list[dict[str, Any]]:
    eps = []
    for split in ("attack", "benign"):
        for p in sorted((V1_ROOT / split).glob("*.json")):
            eps.append(load_v1(p))
    return eps


def load_v0_episodes() -> list[dict[str, Any]]:
    paths: list[Path] = []
    for split in ("attack", "benign"):
        paths.extend(sorted((EPISODES_DIR / split).glob("*.json")))
    paths.extend(sorted(EXAMPLES_DIR.glob("episode_*.json")))
    return [load_episode(p) for p in paths]


def pairwise_flags(eps: list[dict[str, Any]], *, corpus: str, skip_twins: bool) -> list[Flag]:
    flags: list[Flag] = []
    for i, a in enumerate(eps):
        for b in eps[i + 1 :]:
            flags.extend(compare_pair(a, b, corpus=corpus, skip_twin=skip_twins))
    return flags


def cross_corpus_flags(v1: list[dict[str, Any]], v0: list[dict[str, Any]]) -> list[Flag]:
    flags: list[Flag] = []
    for a in v1:
        for b in v0:
            # v0 ids differ; never twins
            flags.extend(compare_pair(a, b, corpus="P4.1_vs_v0", skip_twin=False))
    return flags


def summarize(flags: list[Flag]) -> dict[str, Any]:
    by_class: dict[str, int] = {}
    for f in flags:
        by_class[f.classification] = by_class.get(f.classification, 0) + 1
    return {
        "n_flags": len(flags),
        "by_classification": by_class,
        "flags": [f.__dict__ for f in flags],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="P4.1 offline semantic dedup (ACF method)")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    args = parser.parse_args()

    v1 = load_v1_episodes()
    v0 = load_v0_episodes()
    if len(v1) != 20:
        print(f"expected 20 P4.1 episodes, got {len(v1)}", file=sys.stderr)
        return 2

    intra = pairwise_flags(v1, corpus="P4.1_vs_P4.1", skip_twins=True)
    cross = cross_corpus_flags(v1, v0)

    # Reuse QC lexical on queries for baseline line in report
    qc_query_warnings = []
    for i, ep_i in enumerate(v1):
        for j in range(i + 1, len(v1)):
            if ep_i.get("pair_id") == v1[j].get("pair_id"):
                continue
            sim = jaccard(ep_i["user_query"], v1[j]["user_query"])
            if sim >= 0.92:
                qc_query_warnings.append((ep_i["id"], v1[j]["id"], sim))

    report = {
        "method": "Attack Content Fingerprint (ACF)",
        "dependencies": ["Python stdlib", "scripts/qc_p4_1.jaccard (query baseline only)"],
        "ngram_n": NGRAM_N,
        "threshold_possible_ngram": THRESHOLD_POSSIBLE,
        "threshold_possible_payload": THRESHOLD_PAYLOAD_POSSIBLE,
        "p41_intra": summarize(intra),
        "p41_vs_v0": summarize(cross),
        "qc_query_jaccard_warnings_ge_0.92": qc_query_warnings,
        "semantic_near_duplicate_status": "VERIFIED_BY_ACF"
        if not any(f.classification == "DUPLICATE" for f in intra + cross)
        else "VERIFIED_WITH_DUPLICATE_FLAGS",
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
