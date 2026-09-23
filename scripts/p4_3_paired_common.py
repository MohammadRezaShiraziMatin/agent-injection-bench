"""Shared helpers for P4.3 paired D0/D2 evaluation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
P43_ROOT = ROOT / "data" / "episodes_p4_3"
P42_ROOT = ROOT / "data" / "episodes_p4_2"
P42_PRIMARY_DESIGN_MANIFEST = ROOT / "artifacts" / "p4_2_primary_d0_d2_experiment" / "MANIFEST.json"
P42_ELIGIBILITY_PATH = ROOT / "artifacts" / "p4_2_coverage_eligibility" / "ELIGIBILITY.json"
P42_PAIRED_OUT_BASE = ROOT / "results" / "p4_2_paired"
P3_PAIRED_OUT_BASE = ROOT / "results" / "p3_paired"
P3_COV_B_EXTENSION_MANIFEST = ROOT / "artifacts" / "p3_cov_b_extension" / "MANIFEST.json"
LEVEL_B_PRIMARY_MANIFEST = ROOT / "artifacts" / "level_b_primary_d0_d2_experiment" / "MANIFEST.json"
LEVEL_B_PAIRED_OUT_BASE = ROOT / "results" / "level_b_paired"
LEVEL_B_MODEL_MATRIX = ROOT / "config" / "level_b_model_matrix.v1.json"
P42_FROZEN_DIGEST = "4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee"


def sha256_text(t: str) -> str:
    return hashlib.sha256(t.encode()).hexdigest()


def input_hash(episode: dict[str, Any]) -> str:
    payload = {
        "id": episode.get("id"),
        "user_query": episode.get("user_query"),
        "retrieved_docs": episode.get("retrieved_docs"),
        "split": episode.get("split"),
    }
    return sha256_text(json.dumps(payload, sort_keys=True, ensure_ascii=False))


def dataset_manifest_digest(dataset_root: Path) -> str:
    manifest_path = dataset_root / "MANIFEST.json"
    doc = json.loads(manifest_path.read_text(encoding="utf-8"))
    return str(doc["digest_sha256"])


def load_episode_by_id(dataset_root: Path, episode_id: str) -> dict[str, Any]:
    split = "attack" if episode_id.startswith("atk_") else "benign"
    path = dataset_root / split / f"{episode_id}.json"
    if not path.is_file():
        raise FileNotFoundError(f"episode not found: {episode_id} under {dataset_root}")
    return json.loads(path.read_text(encoding="utf-8"))


def iter_episodes(
    *,
    dataset_root: Path | None = None,
    episode_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    root = dataset_root or P43_ROOT
    if episode_ids:
        return [load_episode_by_id(root, eid) for eid in sorted(episode_ids)]
    paths = sorted((root / "attack").glob("*.json")) + sorted((root / "benign").glob("*.json"))
    return [json.loads(p.read_text(encoding="utf-8")) for p in paths]


def resolve_benign_pair_refs(
    dataset_root: Path,
    attack_episodes: list[dict[str, Any]],
) -> list[dict[str, str]]:
    """Outcome-independent benign pairing via episode.pair_id (dataset MANIFEST contract)."""
    manifest = json.loads((dataset_root / "MANIFEST.json").read_text(encoding="utf-8"))
    benign_by_pair = {
        row["pair_id"]: row["episode_id"]
        for row in manifest["episodes"]
        if row.get("role") == "benign"
    }
    refs: list[dict[str, str]] = []
    for atk in attack_episodes:
        pair_id = atk.get("pair_id")
        if not pair_id:
            raise ValueError(f"missing pair_id on {atk.get('id')}")
        ben_id = benign_by_pair.get(pair_id)
        if not ben_id:
            raise KeyError(f"no benign episode for pair_id={pair_id}")
        refs.append(
            {
                "pair_id": pair_id,
                "attack_episode_id": atk["id"],
                "benign_episode_id": ben_id,
            }
        )
    return refs


def load_p42_primary_run_config() -> dict[str, Any]:
    """Design-time P4.2 primary pool (9 attacks) from immutable experiment manifest."""
    if not P42_PRIMARY_DESIGN_MANIFEST.is_file():
        raise FileNotFoundError(P42_PRIMARY_DESIGN_MANIFEST)
    design = json.loads(P42_PRIMARY_DESIGN_MANIFEST.read_text(encoding="utf-8"))
    pool = design["primary_attack_pool"]
    primary_attack_ids = [row["episode_id"] for row in pool["episodes"]]
    if len(primary_attack_ids) != 9:
        raise ValueError(f"primary pool must have 9 episodes, got {len(primary_attack_ids)}")
    benign_scope = (design.get("benign_controls") or {}).get("utility_fpr_benign_scope")
    if not isinstance(benign_scope, dict) or not benign_scope.get("benign_episode_ids"):
        raise ValueError("utility_fpr_benign_scope.benign_episode_ids required in design manifest")
    utility_fpr_benign_ids = sorted(benign_scope["benign_episode_ids"])
    if len(utility_fpr_benign_ids) != 9:
        raise ValueError("utility_fpr_benign_scope must list 9 benign episode ids")
    for row in pool["episodes"]:
        if row.get("benign_pair_episode_id") not in utility_fpr_benign_ids:
            raise ValueError(f"benign scope mismatch for {row['episode_id']}")
    # P4.3 paired runner order: attacks then benign (see iter_episodes default).
    episode_ids = sorted(primary_attack_ids) + utility_fpr_benign_ids
    digest = design["dataset"]["digest_sha256"]
    if digest != P42_FROZEN_DIGEST:
        raise ValueError("P4.2 digest mismatch in design manifest")
    coverage_map: dict[str, dict[str, str]] = {}
    if P42_ELIGIBILITY_PATH.is_file():
        elig = json.loads(P42_ELIGIBILITY_PATH.read_text(encoding="utf-8"))
        for row in elig.get("attacks") or []:
            if row.get("episode_id") in primary_attack_ids:
                coverage_map[row["episode_id"]] = {
                    "coverage_class": row.get("coverage_class") or pool["coverage_class"],
                    "eligibility": row.get("eligibility") or pool["eligibility_class"],
                }
    for eid in primary_attack_ids:
        if eid not in coverage_map:
            coverage_map[eid] = {
                "coverage_class": pool["coverage_class"],
                "eligibility": pool["eligibility_class"],
            }
    return {
        "dataset_root": P42_ROOT,
        "dataset_version": "P4.2",
        "dataset_digest": digest,
        "episode_ids": episode_ids,
        "primary_attack_ids": primary_attack_ids,
        "utility_fpr_benign_episode_ids": utility_fpr_benign_ids,
        "out_base": P42_PAIRED_OUT_BASE,
        "design_manifest": str(P42_PRIMARY_DESIGN_MANIFEST.relative_to(ROOT)),
        "coverage_by_episode": coverage_map,
        "protocol_version": "P4.2-PRIMARY-PAIRED-1",
        "utility_fpr_benign_scope": benign_scope,
    }


def load_level_b_primary_run_config() -> dict[str, Any]:
    """Frozen Level B expanded COV-A population (23+23) from Phase 4 manifest."""
    if not LEVEL_B_PRIMARY_MANIFEST.is_file():
        raise FileNotFoundError(LEVEL_B_PRIMARY_MANIFEST)
    design = json.loads(LEVEL_B_PRIMARY_MANIFEST.read_text(encoding="utf-8"))
    if design.get("status") != "FROZEN":
        raise ValueError("Level B population manifest must be FROZEN")
    pool = design["primary_attack_pool"]
    primary_attack_ids = sorted(pool.get("attack_episode_ids") or [])
    utility_fpr_benign_ids = sorted(pool.get("benign_episode_ids") or [])
    if len(primary_attack_ids) != len(utility_fpr_benign_ids):
        raise ValueError("Level B attack/benign pool sizes must match")
    digest = design["dataset"]["digest_sha256"]
    if digest != P42_FROZEN_DIGEST:
        raise ValueError("P4.2 digest mismatch in Level B manifest")
    coverage_map: dict[str, dict[str, str]] = {}
    for row in pool.get("episodes") or []:
        eid = row.get("episode_id")
        if eid in primary_attack_ids:
            coverage_map[eid] = {
                "coverage_class": row.get("coverage_class", "COV-A"),
                "eligibility": row.get("eligibility", "PRIMARY_ELIGIBLE"),
            }
    for eid in primary_attack_ids:
        if eid not in coverage_map:
            coverage_map[eid] = {"coverage_class": "COV-A", "eligibility": "PRIMARY_ELIGIBLE"}
    episode_ids = sorted(primary_attack_ids) + utility_fpr_benign_ids
    return {
        "dataset_root": P42_ROOT,
        "dataset_version": "P4.2",
        "dataset_digest": digest,
        "episode_ids": episode_ids,
        "primary_attack_ids": primary_attack_ids,
        "utility_fpr_benign_episode_ids": utility_fpr_benign_ids,
        "out_base": LEVEL_B_PAIRED_OUT_BASE,
        "design_manifest": str(LEVEL_B_PRIMARY_MANIFEST.relative_to(ROOT)),
        "coverage_by_episode": coverage_map,
        "protocol_version": "LEVEL-B-PRIMARY-PAIRED-1",
        "utility_fpr_benign_scope": {
            "benign_episode_ids": utility_fpr_benign_ids,
            "scope_note": "pair-matched benign controls for Level B frozen population",
        },
        "population_label": design.get("population_label"),
    }


def load_level_b_matrix_target_row(row_id: str) -> dict[str, Any]:
    """Resolve a Level B matrix target row for OpenRouter env wiring."""
    if not LEVEL_B_MODEL_MATRIX.is_file():
        raise FileNotFoundError(LEVEL_B_MODEL_MATRIX)
    matrix = json.loads(LEVEL_B_MODEL_MATRIX.read_text(encoding="utf-8"))
    for row in matrix.get("rows") or []:
        if row.get("row_id") == row_id and row.get("role") == "target":
            return row
    raise KeyError(f"matrix target row not found: {row_id}")


def load_p3_cov_b_extension_run_config() -> dict[str, Any]:
    """P3 extension pool (COV-B secondary) — separate from frozen COV-A primary."""
    if not P3_COV_B_EXTENSION_MANIFEST.is_file():
        raise FileNotFoundError(P3_COV_B_EXTENSION_MANIFEST)
    design = json.loads(P3_COV_B_EXTENSION_MANIFEST.read_text(encoding="utf-8"))
    pool = design["extension_attack_pool"]
    primary_attack_ids = [row["episode_id"] for row in pool["episodes"]]
    benign_scope = (design.get("benign_controls") or {}).get("utility_fpr_benign_scope")
    if not isinstance(benign_scope, dict) or not benign_scope.get("benign_episode_ids"):
        raise ValueError("utility_fpr_benign_scope.benign_episode_ids required in P3 manifest")
    utility_fpr_benign_ids = sorted(benign_scope["benign_episode_ids"])
    if len(utility_fpr_benign_ids) != len(primary_attack_ids):
        raise ValueError("P3 benign scope must match attack pool size")
    digest = design["dataset"]["digest_sha256"]
    if digest != P42_FROZEN_DIGEST:
        raise ValueError("P4.2 digest mismatch in P3 manifest")
    coverage_map: dict[str, dict[str, str]] = {}
    if P42_ELIGIBILITY_PATH.is_file():
        elig = json.loads(P42_ELIGIBILITY_PATH.read_text(encoding="utf-8"))
        for row in elig.get("attacks") or []:
            if row.get("episode_id") in primary_attack_ids:
                coverage_map[row["episode_id"]] = {
                    "coverage_class": row.get("coverage_class") or design.get("coverage_class"),
                    "eligibility": row.get("eligibility") or design.get("eligibility"),
                }
    for eid in primary_attack_ids:
        if eid not in coverage_map:
            coverage_map[eid] = {
                "coverage_class": design.get("coverage_class", "COV-B"),
                "eligibility": design.get("eligibility", "SECONDARY_ELIGIBLE"),
            }
    episode_ids = sorted(primary_attack_ids) + utility_fpr_benign_ids
    return {
        "dataset_root": P42_ROOT,
        "dataset_version": "P4.2",
        "dataset_digest": digest,
        "episode_ids": episode_ids,
        "primary_attack_ids": primary_attack_ids,
        "utility_fpr_benign_episode_ids": utility_fpr_benign_ids,
        "out_base": P3_PAIRED_OUT_BASE,
        "design_manifest": str(P3_COV_B_EXTENSION_MANIFEST.relative_to(ROOT)),
        "coverage_by_episode": coverage_map,
        "protocol_version": "P3-COV-B-EXT-PAIRED-1",
        "utility_fpr_benign_scope": benign_scope,
        "population_label": design.get("population_label", "P3-EXT"),
    }


def build_result_record(
    *,
    ep: dict[str, Any],
    run_id: str,
    digest: str,
    condition: str,
    target_cfg: Any,
    judge_cfg: Any,
    trace: dict[str, Any],
    mapped: dict[str, Any],
    judge_status: str,
    defense_event: dict[str, Any] | None,
    latency_ms: int,
    protocol_version: str = "P4.3-PAIRED-1",
    dataset_version: str = "P4.3",
) -> dict[str, Any]:
    forbidden = set((ep.get("expected") or {}).get("forbidden_tools") or [])
    proposed = trace.get("tool_proposals") or []
    tool_executed = any(ev.get("execution_completed") for ev in trace.get("execution_trace") or [])
    expected_crit = (ep.get("expected") or {}).get("success_criterion", "S0")
    error_status = "completed" if judge_status == "ok" else "JUDGE_FAILURE"
    if judge_status == "SKIPPED":
        error_status = "DEFENSE_OR_MODEL_FAILURE"

    return {
        "schema_version": "p43.v1",
        "protocol_version": protocol_version,
        "dataset_version": dataset_version,
        "dataset_digest": digest,
        "episode_id": ep["id"],
        "pair_id": ep.get("pair_id"),
        "split": ep.get("split"),
        "condition": condition,
        "run_id": run_id,
        "input_hash_sha256": input_hash(ep),
        "target_model": target_cfg.model,
        "judge_model": judge_cfg.model,
        "target_provider": getattr(target_cfg, "provider", None),
        "judge_provider": getattr(judge_cfg, "provider", None),
        "expected_success_criterion": expected_crit,
        "observed_success_level": mapped.get("observed_success_level"),
        "harness_observed_success_level": mapped.get("harness_observed_success_level"),
        "judge_observed_success_level": mapped.get("judge_observed_success_level"),
        "attack_success": mapped.get("attack_success"),
        "utility_success": mapped.get("utility_success"),
        "tool_proposed": bool(proposed),
        "forbidden_tool_proposed": mapped.get("forbidden_tool_proposed"),
        "tool_executed": tool_executed,
        "forbidden_tools": list(forbidden),
        "forbidden_tool_executed": mapped.get("forbidden_tool_executed"),
        "external_side_effect_observed": mapped.get("external_side_effect_observed"),
        "s4_status": mapped.get("s4_status"),
        "mapper_policy": mapped.get("mapper_policy"),
        "judge_status": judge_status,
        "error_status": error_status,
        "evaluation_mode": trace.get("harness_execution", {}).get("execution_mode", "LIVE"),
        "execution_trace": trace.get("execution_trace"),
        "defense_event": defense_event,
        "latency_ms": latency_ms,
    }
