"""P4.4 independent validation dataset stays schema-valid and disjoint from P4.2/P4.3."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.qc_p4_4 import run_qc
from scripts.verify_p4_4_freeze import main as freeze_main

ROOT = Path(__file__).resolve().parents[1]


def test_p44_qc_without_regen() -> None:
    report = run_qc(ROOT / "data" / "episodes_p4_4", check_repro=False)
    assert report["ok"], report["issues"]
    assert report["attack_count"] == 100
    assert report["benign_count"] == 100
    assert report["pair_count"] == 100
    assert report["leakage"]["acf_collisions"] == 0
    assert report["leakage"]["near_duplicates_vs_prior"] == 0
    assert set(report["families"]) >= {
        "direct_prompt_injection",
        "indirect_prompt_injection",
        "rag_document_injection",
        "web_retrieved_content_injection",
        "tool_output_injection",
        "multi_turn_injection",
        "memory_state_injection",
        "cross_context_injection",
        "multi_agent_injection",
        "adaptive_injection",
    }


def test_p44_freeze_and_parents() -> None:
    assert freeze_main() == 0
    p42 = json.loads((ROOT / "data/episodes_p4_2/MANIFEST.json").read_text(encoding="utf-8"))
    assert p42["digest_sha256"] == "4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee"
