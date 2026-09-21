# AIB P4.3 — Gap Analysis (external evidence → AIB)

**Date:** 2026-09-21 (UTC)  
**P4.2 digest (immutable):** `4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee`

## Gap register

| gap_id | Class | Description | Evidence | AIB dimension | Priority | Proposed solution | Status |
|--------|-------|-------------|----------|---------------|----------|-------------------|--------|
| G5-001 | G5 | No attack episodes with `success_criterion=S1` | P4.2 stats; Tensor Trust hijack; HouYi output append | horizon/impact | **P1** | 4 synthetic pairs `instruction_deviation` → `user_response` | **Implemented in P4.3 candidate** |
| G9-001 | G9 | No dynamic multi-suite agent environment | AgentDojo 97 tasks / 629 tests | evaluation | P2 | External eval harness; not JSON episodes | Deferred |
| G6-001 | G6 | Only `search_docs` + `send_email` tools | InjecAgent 62 attacker tools | executability | P2 | Harness expansion first | Deferred |
| G6-002 | G6 | 12 DNE + 16 PARTIAL harness episodes | `measure_p4_2_harness_coverage.py` | executability | P2 | Adapter work (P4.2.4 partial) | Documented |
| G4-001 | G4 | `data_exfiltration` n=1 | P4.2 distribution | objective | P3 | Add only if new mechanism | Deferred |
| G8-001 | G8 | Episode `review_status` vs HR trail drift | P4.2 audit | provenance | P1 | Overlay metadata; **do not rewrite frozen bytes** | Deferred |
| G1-001 | G1 | UNVERIFIED benchmarks (Task Shield, Spotlighting, VIGIL, IterInject) | Not primary-sourced here | taxonomy | — | Literature pass later | Open |

## Missing-case design (implemented)

### G5-001 — S1 instruction deviation (4 pairs)

| pair | family | source | gap closure |
|------|--------|--------|-------------|
| p43_001 | direct_prompt_injection | user_message | Output hijack in user tail |
| p43_002 | rag_document_injection | retrieved_document | Policy doc operator |
| p43_003 | web_retrieved_content_injection | web_snippet | Footer injection |
| p43_004 | indirect_prompt_injection | retrieved_document | HTML comment smuggling |

**Reason-not-duplicate:** P4.2 attacks are 100% S2 / `send_email` target; ACF checked in `qc_p4_3.py`.

**Executability:** EXECUTABLE (same harness surfaces as P4.2 RAG/direct paths).

**Realism:** `synthetic=true`; external inspiration **conceptual only** (no imported text).

## DO NOT CREATE (duplicate / wrong layer)

| Item | Reason |
|------|--------|
| More `send_email` S2 RAG variants | P4.2 already n=16 rag family |
| Raw InjecAgent JSONL rows | License + schema mismatch + duplicate mechanism |
| AgentDojo task clones | Environment benchmark, not episode JSON |
| Tensor Trust attack strings | DO_NOT_IMPORT; would duplicate hijack without provenance chain |

## P4.3 candidate summary

| Field | Value |
|-------|-------|
| Path | `data/episodes_p4_3/` |
| Schema | `schema/episode.p43.v1.json` |
| Episodes | 8 (4 attack + 4 benign) |
| Pairs | 4 |
| Seed | `43020260921` |
| Digest | `e60969bee257ec3111febf215fb5f7079edb79ed050dae300e549336184ab53d` (post–HR v1.0.1) |
| Human review | **COMPLETE** — `artifacts/p4_3_hr_audit_trail.json` (8× ACCEPT) |
| Freeze | **NOT READY** (see `docs/AIB_P4_3_COMPLETION_REPORT.md`) |

## Scientific quality gate (P4.3 candidate)

| Gate | Status |
|------|--------|
| Schema | PASS (`qc_p4_3.py`) |
| Taxonomy | PASS |
| Coverage | PASS for scoped G5-001 only |
| Pairing | PASS |
| Dedup vs P4.2 | PASS (ACF) |
| Leakage | PASS (manual ACF cross-check) |
| Provenance | PASS (synthetic, generator recorded) |
| Executability | PASS (labeled EXECUTABLE) |
| Benign controls | PASS |
| Human adjudication | **PASS** |
| Reproducibility | PASS (byte-identical regen, generator 1.0.1) |
| Scientific justification | PASS for G5-001 only |

**Overall:** **PASS WITH CONDITIONS** for scientific gate (`docs/AIB_P4_3_COMPLETION_REPORT.md`); **not** released/frozen.
