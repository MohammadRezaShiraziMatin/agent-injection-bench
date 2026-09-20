#!/usr/bin/env python3
"""P4.2.2 automated scientific pre-review (not human review)."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from jsonschema import Draft7Validator

from scripts.qc_p4_2 import acf_fingerprint, iter_paths, load_episode

P42_ROOT = ROOT / "data" / "episodes_p4_2"
SCHEMA_PATH = ROOT / "schema" / "episode.v2.json"
P421_ART = ROOT / "artifacts" / "p4_2_1_near_duplicate_adjudication.json"

TAX_KEYS = [
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

NEAR_DUP_ATTACK_IDS = {f"atk_p42_{i:03d}" for i in range(83, 101)}
NEAR_DUP_PAIR_IDS = {f"p42_{i:03d}" for i in range(83, 101)}


def load_near_dup_flags() -> set[str]:
    if not P421_ART.is_file():
        return set()
    data = json.loads(P421_ART.read_text(encoding="utf-8"))
    ids: set[str] = set()
    for r in data.get("records", []):
        ids.add(r["episode_a"])
        ids.add(r["episode_b"])
    return ids


def schema_errors(ep: dict[str, Any], validator: Draft7Validator) -> list[str]:
    return [e.message for e in validator.iter_errors(ep)]


def check_injection_validity(ep: dict[str, Any]) -> tuple[bool, list[str]]:
    notes: list[str] = []
    if ep["split"] == "benign":
        if ep.get("injection", {}).get("present"):
            notes.append("benign has injection.present=true")
            return False, notes
        return True, notes
    inj = ep.get("injection") or {}
    if not inj.get("present"):
        notes.append("attack missing injection")
        return False, notes
    if not inj.get("payload"):
        notes.append("attack missing payload")
        return False, notes
    return True, notes


def check_taxonomy_consistency(ep: dict[str, Any]) -> tuple[bool, list[str]]:
    notes: list[str] = []
    tax = ep.get("taxonomy", {})
    exp = ep.get("expected", {})
    crit = exp.get("success_criterion")
    obj = tax.get("objective")
    if ep["split"] == "benign":
        if obj not in ("benign_control", "unauthorized_state_change"):
            notes.append(f"benign objective unexpected: {obj}")
        if crit != "S0":
            notes.append(f"benign success_criterion={crit}, expected S0")
    else:
        if obj == "benign_control":
            notes.append("attack has benign_control objective")
        if crit in ("S3", "S4"):
            notes.append(f"attack claims {crit} without live side-effect evidence in dataset")
        if obj == "unauthorized_tool_execution" and crit == "S2":
            pass  # proposal-level benchmark
    if tax.get("interaction_type") == "multi_turn" and tax.get("horizon") == "h0":
        notes.append("multi_turn with h0 horizon (check temporal labeling)")
    return len(notes) == 0, notes


def check_mechanism(ep: dict[str, Any]) -> tuple[bool, list[str]]:
    notes: list[str] = []
    if ep["split"] == "benign":
        return True, notes
    fam = ep["taxonomy"]["family"]
    inj = ep.get("injection") or {}
    locus = inj.get("locus", "")

    if fam == "direct_prompt_injection" and not locus.startswith("user_query"):
        notes.append("direct family but locus is not user_query")
    if fam == "indirect_prompt_injection" and "retrieved_docs" not in locus:
        notes.append("indirect family locus should be retrieved_docs")
    if fam == "rag_document_injection" and "retrieved_docs" not in locus:
        notes.append("rag locus should reference retrieved_docs")
    if fam == "web_retrieved_content_injection":
        docs = ep.get("retrieved_docs", [])
        if docs and docs[0].get("source_kind") == "internal_kb":
            notes.append("web family but source_kind=internal_kb")
    if fam == "tool_output_injection":
        if not ep.get("tool_results"):
            notes.append("tool_output missing tool_results")
        if "tool_results" not in locus:
            notes.append("tool_output locus should reference tool_results")
    if fam == "multi_turn_injection":
        conv = ep.get("conversation") or []
        if len(conv) < 2:
            notes.append("multi_turn has fewer than 2 conversation turns")
        elif "conversation" not in locus and "prior" not in locus:
            notes.append("multi_turn locus does not reference conversation/prior_turn")
    if fam == "memory_state_injection":
        if not ep.get("memory_store") and not ep.get("session_state"):
            notes.append("memory_state missing memory_store/session_state")
    if fam == "cross_context_injection":
        if not ep.get("cross_context"):
            notes.append("cross_context missing cross_context block")
    if fam == "multi_agent_injection":
        if not ep.get("inter_agent_messages"):
            notes.append("multi_agent missing inter_agent_messages")
    if fam == "adaptive_injection":
        trace = ep.get("adaptive_trace") or []
        phases = {t.get("phase") for t in trace}
        if not {"attempt_1", "observation", "adaptation", "attempt_2"}.issubset(phases):
            notes.append("adaptive_trace missing required phases")
    return len(notes) == 0, notes


def check_pair(ep: dict[str, Any], twin: dict[str, Any] | None) -> tuple[bool, list[str]]:
    notes: list[str] = []
    if twin is None:
        return False, ["missing pair twin"]
    if ep.get("pair_id") != twin.get("pair_id"):
        notes.append("pair_id mismatch")
    if ep.get("dataset_partition") != twin.get("dataset_partition"):
        notes.append("partition mismatch within pair")
    if ep["split"] == "attack" and twin.get("injection", {}).get("present"):
        notes.append("benign twin has injection")
    return len(notes) == 0, notes


def duplicate_risk(ep: dict[str, Any]) -> str:
    if ep["id"] in NEAR_DUP_ATTACK_IDS or ep.get("pair_id") in NEAR_DUP_PAIR_IDS:
        return "MEDIUM"
    return "LOW"


def assign_review(
    ep: dict[str, Any],
    twin: dict[str, Any] | None,
    schema_ok: bool,
    inj_ok: bool,
    tax_ok: bool,
    mech_ok: bool,
    pair_ok: bool,
    inj_notes: list[str],
    tax_notes: list[str],
    mech_notes: list[str],
    pair_notes: list[str],
) -> dict[str, Any]:
    exec_st = ep.get("execution", {}).get("executability", "UNKNOWN")
    fam = ep["taxonomy"]["family"]
    all_notes = inj_notes + tax_notes + mech_notes + pair_notes
    if not schema_ok:
        scientific = "REJECT_CANDIDATE"
        priority = "P0"
        action = "REJECT"
    elif not inj_ok or not pair_ok:
        scientific = "REVISE"
        priority = "P0"
        action = "REVISE_CONTENT" if not inj_ok else "REVISE_METADATA"
    elif not mech_ok:
        scientific = "REVISE"
        priority = "P1"
        action = "REVISE_CONTENT"
    elif not tax_ok:
        scientific = "REVISE"
        priority = "P2"
        action = "REVISE_METADATA"
    elif exec_st == "DESIGNED_NOT_EXECUTABLE" or fam in ("multi_agent_injection", "adaptive_injection"):
        scientific = "UNCERTAIN_HUMAN_REQUIRED"
        priority = "P1"
        action = "REVIEW_HUMAN"
    elif exec_st == "PARTIALLY_EXECUTABLE":
        scientific = "ACCEPT_CANDIDATE"
        priority = "P1"
        action = "REVIEW_HUMAN"
    elif ep.get("pair_id") in NEAR_DUP_PAIR_IDS and fam == "cross_context_injection":
        scientific = "UNCERTAIN_HUMAN_REQUIRED"
        priority = "P1"
        action = "REVIEW_HUMAN"
    else:
        scientific = "ACCEPT_CANDIDATE"
        priority = "P3" if ep["split"] == "benign" else "P2"
        action = "KEEP"

    realism = True
    if fam == "direct_prompt_injection" and ep["split"] == "attack":
        if "[User follow-up for ticketing system" in ep.get("user_query", ""):
            realism = True
    if "IGNORE PREVIOUS" in ep.get("user_query", "").upper():
        realism = False
        if scientific == "ACCEPT_CANDIDATE":
            scientific = "REVISE"
            action = "REVISE_CONTENT"
            priority = "P2"
            all_notes.append("unrealistic IGNORE PREVIOUS wording in user_query")

    return {
        "scientific_status": scientific,
        "review_priority": priority,
        "recommended_action": action,
        "semantic_validity": inj_ok and mech_ok,
        "taxonomy_validity": tax_ok and schema_ok,
        "mechanism_validity": mech_ok,
        "internal_consistency": tax_ok and pair_ok,
        "pair_validity": pair_ok,
        "realism": realism,
        "executability_status": exec_st,
        "duplicate_risk": duplicate_risk(ep),
        "review_status": "unreviewed",
        "automated_pre_review": True,
        "review_notes": "; ".join(all_notes) if all_notes else "No automated issues detected.",
        "human_decision": None,
        "human_reviewer": None,
        "review_date": None,
        "human_notes": None,
    }


def build_record(
    ep: dict[str, Any],
    twin: dict[str, Any] | None,
    validator: Draft7Validator,
) -> dict[str, Any]:
    tax = ep.get("taxonomy", {})
    errs = schema_errors(ep, validator)
    schema_ok = len(errs) == 0
    inj_ok, inj_notes = check_injection_validity(ep)
    tax_ok, tax_notes = check_taxonomy_consistency(ep)
    mech_ok, mech_notes = check_mechanism(ep)
    pair_ok, pair_notes = check_pair(ep, twin)
    if not schema_ok:
        inj_notes.extend([f"schema: {e}" for e in errs[:3]])

    review = assign_review(
        ep, twin, schema_ok, inj_ok, tax_ok, mech_ok, pair_ok, inj_notes, tax_notes, mech_notes, pair_notes
    )
    return {
        "episode_id": ep["id"],
        "pair_id": ep.get("pair_id"),
        "split": ep["split"],
        "label": ep["split"],
        "dataset_partition": ep.get("dataset_partition"),
        "family": tax.get("family"),
        "technique": tax.get("technique"),
        "objective": tax.get("objective"),
        "source": tax.get("source"),
        "target": tax.get("target"),
        "path": tax.get("path"),
        "interaction_type": tax.get("interaction_type"),
        "horizon": tax.get("horizon"),
        "context_type": tax.get("context_type"),
        "tool": tax.get("tool"),
        "memory_state": tax.get("memory_state"),
        "success_criterion": ep.get("expected", {}).get("success_criterion"),
        **review,
    }


def run_pre_review(root: Path) -> dict[str, Any]:
    validator = Draft7Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))
    paths = iter_paths(root)
    episodes = [load_episode(p) for p in paths]
    by_id = {e["id"]: e for e in episodes}
    pairs: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for e in episodes:
        pairs[e["pair_id"]][e["split"]] = e

    records: list[dict[str, Any]] = []
    for ep in sorted(episodes, key=lambda x: x["id"]):
        pid = ep["pair_id"]
        twin_split = "benign" if ep["split"] == "attack" else "attack"
        twin = pairs[pid].get(twin_split)
        records.append(build_record(ep, twin, validator))

    stats = {
        "scientific_status": Counter(r["scientific_status"] for r in records),
        "review_priority": Counter(r["review_priority"] for r in records),
        "recommended_action": Counter(r["recommended_action"] for r in records),
        "by_family": Counter(r["family"] for r in records if r["split"] == "attack"),
    }
    near_dup_confirm = sum(1 for r in records if r.get("pair_id") in NEAR_DUP_PAIR_IDS)

    return {
        "phase": "P4.2.2",
        "dataset_version": "P4.2",
        "review_type": "AUTOMATED_PRE_REVIEW",
        "human_review_performed": False,
        "episode_count": len(records),
        "records": records,
        "statistics": {k: dict(v) for k, v in stats.items()},
        "near_duplicate_p4_2_1": {
            "flags": 114,
            "adjudication": "VALID_VARIANT",
            "pair_ids_in_flag_clusters": sorted(NEAR_DUP_PAIR_IDS),
            "human_confirmation_recommended": near_dup_confirm,
        },
    }


def write_csv(records: list[dict[str, Any]], path: Path) -> None:
    fields = list(records[0].keys()) if records else []
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in records:
            w.writerow(r)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=P42_ROOT)
    parser.add_argument(
        "--json-out",
        type=Path,
        default=ROOT / "artifacts" / "p4_2_2_human_review_matrix.json",
    )
    parser.add_argument(
        "--csv-out",
        type=Path,
        default=ROOT / "artifacts" / "p4_2_2_human_review_matrix.csv",
    )
    args = parser.parse_args()
    report = run_pre_review(args.root)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(report["records"], args.csv_out)
    print(json.dumps({"ok": True, "episodes": report["episode_count"], "stats": report["statistics"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
