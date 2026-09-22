#!/usr/bin/env python3
"""Build P4.2.2-HR human adjudication workflow artifacts (no human decisions)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.qc_p4_2 import load_episode, iter_paths

MATRIX_PATH = ROOT / "artifacts" / "p4_2_2_human_review_matrix.json"
P421_PATH = ROOT / "artifacts" / "p4_2_1_near_duplicate_adjudication.json"
P42_ROOT = ROOT / "data" / "episodes_p4_2"

SIMILARITY_PAIR_IDS = {f"p42_{i:03d}" for i in range(83, 101)}
COMPLEX_FAMILIES = {
    "multi_turn_injection",
    "memory_state_injection",
    "cross_context_injection",
    "multi_agent_injection",
    "adaptive_injection",
    "tool_output_injection",
}


def episode_evidence(ep: dict[str, Any]) -> dict[str, Any]:
    inj = ep.get("injection") or {}
    exp = ep.get("expected", {})
    tax = ep.get("taxonomy", {})
    return {
        "episode_id": ep["id"],
        "pair_id": ep.get("pair_id"),
        "split": ep["split"],
        "dataset_partition": ep.get("dataset_partition"),
        "taxonomy": {k: tax.get(k) for k in (
            "family", "technique", "objective", "source", "target", "path",
            "interaction_type", "horizon", "context_type", "tool", "memory_state",
        )},
        "content": {
            "user_query": ep.get("user_query", ""),
            "retrieved_docs": ep.get("retrieved_docs", []),
            "tool_results": ep.get("tool_results", []),
            "conversation": ep.get("conversation", []),
            "memory_store": ep.get("memory_store", []),
            "cross_context": ep.get("cross_context", []),
            "inter_agent_messages": ep.get("inter_agent_messages", []),
            "adaptive_trace": ep.get("adaptive_trace", []),
            "session_state": ep.get("session_state", {}),
            "injection": {
                "present": inj.get("present"),
                "payload": inj.get("payload"),
                "locus": inj.get("locus"),
                "target_tool": inj.get("target_tool"),
            },
        },
        "expected": {
            "success_criterion": exp.get("success_criterion"),
            "success_observable": exp.get("success_observable"),
            "not_success": exp.get("not_success"),
            "forbidden_tools": exp.get("forbidden_tools"),
        },
        "execution": ep.get("execution", {}),
        "notes": ep.get("notes", ""),
    }


def similarity_context(episode_id: str, pair_id: str | None) -> dict[str, Any]:
    out: dict[str, Any] = {
        "in_p4_2_1_cluster": pair_id in SIMILARITY_PAIR_IDS if pair_id else False,
        "human_confirmation_recommended": pair_id in SIMILARITY_PAIR_IDS if pair_id else False,
        "p4_2_1_adjudication": "VALID_VARIANT",
        "related_flags": [],
    }
    if not P421_PATH.is_file() or not episode_id.startswith("atk_"):
        return out
    data = json.loads(P421_PATH.read_text(encoding="utf-8"))
    for rec in data.get("records", []):
        if rec["episode_a"] == episode_id or rec["episode_b"] == episode_id:
            other = rec["episode_b"] if rec["episode_a"] == episode_id else rec["episode_a"]
            out["related_flags"].append(
                {
                    "other_episode": other,
                    "ngram_jaccard": rec["similarity_value"],
                    "adjudication": rec["adjudication"],
                    "rationale": rec.get("rationale", ""),
                }
            )
    return out


def assign_batch(rec: dict[str, Any]) -> str:
    if rec["scientific_status"] == "UNCERTAIN_HUMAN_REQUIRED":
        return "batch_1_uncertain"
    if rec.get("pair_id") in SIMILARITY_PAIR_IDS:
        return "batch_3_similarity_confirmation"
    fam = rec.get("family")
    pri = rec.get("review_priority")
    exec_st = rec.get("executability_status")
    if fam in COMPLEX_FAMILIES or exec_st in ("PARTIALLY_EXECUTABLE", "DESIGNED_NOT_EXECUTABLE"):
        return "batch_2_complex_families"
    if pri == "P1":
        return "batch_4_remaining_p1"
    return "batch_5_p2_p3"


def build_queue(matrix: dict[str, Any], evidence_by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    records = matrix["records"]
    batches: dict[str, list[str]] = {
        "batch_1_uncertain": [],
        "batch_2_complex_families": [],
        "batch_3_similarity_confirmation": [],
        "batch_4_remaining_p1": [],
        "batch_5_p2_p3": [],
    }
    assignments: dict[str, str] = {}
    for rec in records:
        eid = rec["episode_id"]
        batch = assign_batch(rec)
        assignments[eid] = batch
        batches[batch].append(eid)

    for k in batches:
        batches[k] = sorted(set(batches[k]))

    batch_meta = [
        {
            "batch_id": "batch_1_uncertain",
            "title": "UNCERTAIN_HUMAN_REQUIRED (review first)",
            "episode_count": len(batches["batch_1_uncertain"]),
        },
        {
            "batch_id": "batch_2_complex_families",
            "title": "Complex families / partial or non-executable",
            "episode_count": len(batches["batch_2_complex_families"]),
        },
        {
            "batch_id": "batch_3_similarity_confirmation",
            "title": "P4.2.1 similarity cluster confirmation (pairs p42_083–p42_100)",
            "episode_count": len(batches["batch_3_similarity_confirmation"]),
        },
        {
            "batch_id": "batch_4_remaining_p1",
            "title": "Remaining P1",
            "episode_count": len(batches["batch_4_remaining_p1"]),
        },
        {
            "batch_id": "batch_5_p2_p3",
            "title": "P2 / P3 lower-risk",
            "episode_count": len(batches["batch_5_p2_p3"]),
        },
    ]

    cards: list[dict[str, Any]] = []
    for rec in sorted(records, key=lambda r: (assignments[r["episode_id"]], r["episode_id"])):
        eid = rec["episode_id"]
        cards.append(
            {
                "episode_id": eid,
                "pair_id": rec.get("pair_id"),
                "review_batch": assignments[eid],
                "automated_status": rec.get("scientific_status"),
                "priority": rec.get("review_priority"),
                "recommended_action": rec.get("recommended_action"),
                "duplicate_risk": rec.get("duplicate_risk"),
                "executability_status": rec.get("executability_status"),
                "evidence": evidence_by_id[eid],
                "similarity": similarity_context(eid, rec.get("pair_id")),
                "human_decision": None,
                "human_reviewer": None,
                "review_date": None,
                "human_notes": None,
                "review_status": "unreviewed",
            }
        )

    return {
        "phase": "P4.2.2-HR",
        "human_review_performed": False,
        "episode_count": len(cards),
        "batches": batch_meta,
        "batch_assignments": assignments,
        "review_cards": cards,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", type=Path, default=MATRIX_PATH)
    parser.add_argument("--episodes-root", type=Path, default=P42_ROOT)
    parser.add_argument("--out-queue", type=Path, default=ROOT / "artifacts" / "p4_2_2_hr_review_queue.json")
    parser.add_argument("--out-evidence", type=Path, default=ROOT / "artifacts" / "p4_2_2_hr_episode_evidence.json")
    parser.add_argument("--out-audit", type=Path, default=ROOT / "artifacts" / "p4_2_2_hr_audit_trail.json")
    args = parser.parse_args()

    matrix = json.loads(args.matrix.read_text(encoding="utf-8"))
    evidence_list: list[dict[str, Any]] = []
    evidence_by_id: dict[str, dict[str, Any]] = {}
    for path in iter_paths(args.episodes_root):
        ep = load_episode(path)
        ev = episode_evidence(ep)
        evidence_list.append(ev)
        evidence_by_id[ep["id"]] = ev

    queue = build_queue(matrix, evidence_by_id)
    audit = {
        "schema_version": "1.0",
        "phase": "P4.2.2-HR",
        "human_review_performed": False,
        "decisions": [],
        "decision_schema": {
            "episode_id": "string",
            "previous_automated_status": "string",
            "human_decision": "ACCEPT | REVISE | REJECT | UNCERTAIN",
            "human_reviewer": "string",
            "review_date": "ISO-8601 date",
            "human_notes": "string",
            "content_mutation": "optional before/after if episode edited in later phase",
        },
    }

    for out_path, payload in (
        (args.out_queue, queue),
        (args.out_evidence, {"episode_count": len(evidence_list), "episodes": evidence_list}),
        (args.out_audit, audit),
    ):
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "ok": True,
                "queue_episodes": queue["episode_count"],
                "batches": queue["batches"],
                "audit_decisions": len(audit["decisions"]),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
