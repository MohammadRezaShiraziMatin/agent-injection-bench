#!/usr/bin/env python3
"""Offline P4.2 primary D0↔D2 effectiveness eligibility audit (no dataset/detector changes)."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
P42 = ROOT / "data" / "episodes_p4_2"
LABEL_DIR = ROOT / "artifacts" / "p4_2_coverage_labeling"
OUT = ROOT / "artifacts" / "p4_2_coverage_eligibility"
PIN_SHA = "30ddc756a07e3eae1f9afd5a3e9b9c68a7017f64"
P42_DIGEST = "4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee"
PROTOCOL = "coverage_eligibility_audit_v1"
PRIMARY_MIN_RECOMMENDED = 30  # reporting threshold only; no promotion

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.defense.adaptiguard_adapter import episode_input_from_aib  # noqa: E402

BRIDGE_LOCI_OK = ("user_query",)
BRIDGE_LOCI_PREFIX = ("retrieved_docs",)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _locus_on_bridge(locus: str | None) -> bool:
    if not locus:
        return False
    if locus in BRIDGE_LOCI_OK:
        return True
    return locus.startswith(BRIDGE_LOCI_PREFIX)


def _payload_on_bridge(episode: dict[str, Any]) -> bool:
    inj = episode.get("injection") or {}
    payload = str(inj.get("payload") or "")
    if not payload:
        return False
    inp = episode_input_from_aib(episode, [])
    return payload in inp.prompt or payload in (inp.context or "")


def _episode_path(episode_id: str) -> Path:
    return P42 / "attack" / f"{episode_id}.json"


def _cov_a_eligibility(
    lb: dict[str, Any],
    episode: dict[str, Any],
    cal: dict[str, Any] | None,
) -> dict[str, Any]:
    locus = lb.get("injection_locus")
    family = lb.get("family")
    exec_meta = episode.get("execution") or {}
    executability = exec_meta.get("executability")
    inp = episode_input_from_aib(episode, [])
    mapping = {
        "prompt_source": "episode.user_query",
        "context_source": "episode.retrieved_docs[].text|content",
        "adapter": "agent/defense/adaptiguard_adapter.py:episode_input_from_aib",
        "bridge": "agent/defense/adaptiguard_bridge.py:run_core_pipeline",
    }
    payload_ok = _payload_on_bridge(episode)
    locus_ok = _locus_on_bridge(locus)
    diag = (cal or {}).get("diagnostic")
    c1 = (cal or {}).get("c1") or {}
    indicators = c1.get("indicator_ids") or []
    if isinstance(lb.get("matched_feature"), str) and not indicators:
        indicators = [x for x in lb["matched_feature"].split(",") if x]

    base_audit = {
        "episode_id": lb["episode_id"],
        "family": family,
        "locus": locus,
        "episode_input_mapping": mapping,
        "detector_evidence": {
            "coverage_class": "COV-A",
            "evidence_type": lb.get("evidence_type"),
            "c1_is_injection": c1.get("is_injection"),
            "indicator_ids": indicators,
            "calibration_diagnostic": diag,
        },
        "evidence_reference": lb.get("evidence_reference"),
        "matched_detector_feature": lb.get("matched_feature"),
    }

    ambiguity: list[str] = []
    if not locus_ok:
        ambiguity.append("injection_locus_not_mapped_to_bridge_EpisodeInput")
    if not payload_ok:
        ambiguity.append("injection_payload_not_present_on_bridge_surface")
    if executability in ("PARTIALLY_EXECUTABLE", "DESIGNED_NOT_EXECUTABLE"):
        ambiguity.append(f"harness_executability={executability}")
    if exec_meta.get("missing_adapter_note"):
        ambiguity.append("missing_adapter_note_present")

    spurious_hit = (
        c1.get("is_injection")
        and not payload_ok
        and indicators == ["forced_identifier"]
    )
    if spurious_hit:
        ambiguity.append("detector_hit_without_attack_payload_on_bridge")

    if (
        locus_ok
        and payload_ok
        and diag == "D2"
        and c1.get("is_injection")
        and not ambiguity
    ):
        return {
            **base_audit,
            "eligibility": "PRIMARY_ELIGIBLE",
            "reason": (
                "COV-A with D2 calibration; attack payload on bridge EpisodeInput; "
                "documented detector hit with traceable indicators."
            ),
        }

    reasons = []
    if not (locus_ok and payload_ok and diag == "D2"):
        reasons.append("missing_direct_D2_bridge-aligned detector evidence chain")
    if ambiguity:
        reasons.extend(ambiguity)
    return {
        **base_audit,
        "eligibility": "SECONDARY_ELIGIBLE",
        "reason": "; ".join(reasons) or "COV-A without full primary criteria",
    }


def _cov_b_row(lb: dict[str, Any], episode: dict[str, Any]) -> dict[str, Any]:
    exec_meta = episode.get("execution") or {}
    return {
        "episode_id": lb["episode_id"],
        "family": lb.get("family"),
        "locus": lb.get("injection_locus"),
        "why_semantic_overlap": lb.get("rationale"),
        "why_direct_evidence_insufficient": lb.get("evidence_type"),
        "bridge_input_ambiguity": (
            "Adapter maps user_query+retrieved_docs only; "
            f"injection locus={lb.get('injection_locus')!r} "
            f"executability={exec_meta.get('executability')}"
        ),
        "eligibility": "SECONDARY_ELIGIBLE",
        "coverage_class": "COV-B",
        "evidence_reference": lb.get("evidence_reference"),
    }


def _cov_c_row(lb: dict[str, Any]) -> dict[str, Any]:
    gap = (
        "detector_coverage_gap_v1 D1 pattern (C1 no_hit, documented F1/F2 scaffold C2 hit)"
        if lb.get("evidence_type") == "detector_coverage_gap_v1_D1"
        else lb.get("rationale")
    )
    return {
        "episode_id": lb["episode_id"],
        "family": lb.get("family"),
        "gap_evidence": gap,
        "eligibility": "DIAGNOSTIC_ONLY",
        "coverage_class": "COV-C",
        "evidence_reference": lb.get("evidence_reference"),
    }


def main() -> int:
    if OUT.exists() and any(OUT.glob("*.json")):
        print(json.dumps({"ok": False, "error": "EXISTING_ELIGIBILITY_ARTIFACT", "path": str(OUT)}))
        return 1
    if not (LABEL_DIR / "LABELS.json").is_file():
        print(json.dumps({"ok": False, "error": "MISSING_COVERAGE_LABELING"}))
        return 1

    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT / "external" / "adapti-guard",
        capture_output=True,
        text=True,
        check=False,
    )
    if (proc.stdout or "").strip() != PIN_SHA:
        print(json.dumps({"ok": False, "error": "ADAPTIGUARD_SHA_MISMATCH"}))
        return 1

    label_manifest = _load_json(LABEL_DIR / "MANIFEST.json")
    if label_manifest.get("p4_2_digest_sha256") != P42_DIGEST:
        print(json.dumps({"ok": False, "error": "P42_DIGEST_MISMATCH"}))
        return 1

    labels_doc = _load_json(LABEL_DIR / "LABELS.json")
    cal_detail = labels_doc.get("calibration_detail") or {}
    attacks = [lb for lb in labels_doc["labels"] if lb.get("attack_benign") == "attack"]
    if len(attacks) != 100:
        print(json.dumps({"ok": False, "error": "ATTACK_COUNT", "n": len(attacks)}))
        return 1

    rows: list[dict[str, Any]] = []
    cov_a_audits: list[dict[str, Any]] = []

    for lb in attacks:
        ep = json.loads(_episode_path(lb["episode_id"]).read_text(encoding="utf-8"))
        cov = lb["coverage_class"]
        if cov == "COV-A":
            audit = _cov_a_eligibility(lb, ep, cal_detail.get(lb["episode_id"]))
            cov_a_audits.append(audit)
            rows.append({**lb, **audit})
        elif cov == "COV-B":
            rows.append(_cov_b_row(lb, ep))
        elif cov == "COV-C":
            rows.append(_cov_c_row(lb))
        else:
            rows.append(
                {
                    "episode_id": lb["episode_id"],
                    "coverage_class": cov,
                    "eligibility": "EXCLUDED",
                    "reason": "unexpected_coverage_class_for_attack",
                }
            )

    dist = {
        "PRIMARY_ELIGIBLE": 0,
        "SECONDARY_ELIGIBLE": 0,
        "DIAGNOSTIC_ONLY": 0,
        "EXCLUDED": 0,
    }
    families: dict[str, dict[str, list[str]]] = {
        k: {} for k in dist
    }
    for r in rows:
        el = r["eligibility"]
        dist[el] = dist.get(el, 0) + 1
        fam = r.get("family") or "unknown"
        families[el].setdefault(fam, []).append(r["episode_id"])

    primary_n = dist["PRIMARY_ELIGIBLE"]
    flags: list[str] = []
    if primary_n < PRIMARY_MIN_RECOMMENDED:
        flags.append("PRIMARY_SAMPLE_INSUFFICIENT")

    unresolved = [r["episode_id"] for r in rows if r["eligibility"] == "EXCLUDED"]

    finished = datetime.now(timezone.utc).isoformat()
    manifest = {
        "artifact_id": "p4_2_coverage_eligibility",
        "protocol_version": PROTOCOL,
        "protocol_doc": "docs/AIB_RESEARCH_CONTROLLED_DEFENSE_EXPERIMENT_SPEC.md",
        "coverage_protocol_doc": "docs/AIB_COVERAGE_AWARE_EVALUATION_PROTOCOL.md",
        "coverage_labeling_reference": "artifacts/p4_2_coverage_labeling/MANIFEST.json",
        "p4_2_digest_sha256": P42_DIGEST,
        "adaptiguard_commit_sha": PIN_SHA,
        "detector_contract": "adapti_guard.detector.prompt_injection_detector_phase1.PromptInjectionDetectorPhase1",
        "mode": "offline_audit_only",
        "live_d2_inference_allowed": False,
        "finished_at": finished,
    }
    summary = {
        "distribution": dist,
        "primary_sample_size": primary_n,
        "secondary_sample_size": dist["SECONDARY_ELIGIBLE"],
        "diagnostic_sample_size": dist["DIAGNOSTIC_ONLY"],
        "excluded_sample_size": dist["EXCLUDED"],
        "flags": flags,
        "primary_insufficient_criteria": (
            "Expand COV-A with additional episodes where injection payload is on bridge "
            "EpisodeInput and offline calibration shows D2 (C1+C2 documented scaffold hit); "
            "requires new labeling evidence only — no dataset/detector mutation in this audit."
            if flags
            else None
        ),
        "primary_attack_families": {k: sorted(v) for k, v in sorted(families["PRIMARY_ELIGIBLE"].items())},
        "secondary_attack_families": {k: sorted(v) for k, v in sorted(families["SECONDARY_ELIGIBLE"].items())},
        "diagnostic_attack_families": {k: sorted(v) for k, v in sorted(families["DIAGNOSTIC_ONLY"].items())},
        "unresolved_cases": unresolved,
        "cov_a_audit_count": len(cov_a_audits),
        "cov_a_primary_count": sum(1 for a in cov_a_audits if a["eligibility"] == "PRIMARY_ELIGIBLE"),
        "cov_a_downgraded_to_secondary": sum(
            1 for a in cov_a_audits if a["eligibility"] == "SECONDARY_ELIGIBLE"
        ),
    }

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (OUT / "ELIGIBILITY.json").write_text(
        json.dumps(
            {
                "protocol_version": PROTOCOL,
                "attacks": rows,
                "cov_a_detailed_audit": cov_a_audits,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (OUT / "SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "summary": summary}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
