# AIB P4.2.2 Human Scientific Review Report

## 1. Executive summary

Automated pre-review was performed by the benchmark agent on all **200** P4.2 candidate episodes. **Actual human scientific adjudication has not yet occurred.** No episode bytes were modified; manifest digest unchanged. Gate: **PASS WITH CONDITIONS**.

## 2. Scope

P4.2.2 scientific review package generation: structured pre-review, issue identification, human-review queue, integrity verification. No freeze, no live LLM, no dataset expansion.

## 3. Baseline dataset

| Field | Value |
|-------|-------|
| Episodes | 200 (100 attack / 100 benign / 100 pairs) |
| Manifest digest | `416264027c5e1f57a2a77f8ca31009f1b6ce399eddc1792a3dc8737ec75e74b3` |
| Schema | `episode.v2.json` (2.0) |
| Generator | `gen_p4_2_dataset.py@1.0.0` |
| Seed | `42020260920` |
| Taxonomy | V2 (`docs/AIB_P4_2_TAXONOMY_V2.md`) |
| Branch / HEAD | `cursor/p4-2-dataset-6db2` / `859574d` (+ local P4.2.2 artifacts) |

## 4. P4.1 integrity

`verify_p6_freeze.py`: **PASS**. Digest `717458789217d4fd29c655e40018471fdaf16b061ff5481cfdc48f7812437ac3`. `git diff data/episodes_v1/`: empty.

## 5. v0 integrity

42 episodes; validation **PASS**; `git diff data/episodes/`: empty.

## 6. Git state

Local branch ahead of `origin/cursor/p4-2-dataset-6db2` by P4.2.1 commit; P4.2.2 changes local only. **No push** in this phase. Draft PR #2 not modified.

## 7. Review methodology

Deterministic rules in `scripts/pre_review_p4_2_2.py`: schema validity, injection presence, taxonomy/success-criterion consistency, family-specific mechanism checks, pair integrity, executability metadata, P4.2.1 near-duplicate cluster tagging. Output: `artifacts/p4_2_2_human_review_matrix.json`.

## 8. Review categories

`AUTOMATED_PRE_REVIEW` only — not `human_reviewed`.

## 9. Attack review statistics

| scientific_status | Count |
|-------------------|------:|
| ACCEPT_CANDIDATE | 92 |
| UNCERTAIN_HUMAN_REQUIRED | 8 |
| REVISE | 0 |
| REJECT_CANDIDATE | 0 |

## 10. Benign review statistics

| scientific_status | Count |
|-------------------|------:|
| ACCEPT_CANDIDATE | 92 |
| UNCERTAIN_HUMAN_REQUIRED | 8 |

Benign controls: `injection.present=false`, `success_criterion=S0`, `objective=benign_control` (memory-family exception documented in schema).

## 11. Pair review statistics

100 pairs; automated `pair_validity=true` for all 200 records. Pairing QC: **PASS**.

## 12. Taxonomy findings

No schema-invalid taxonomy values detected. Success semantics: attacks use **S2** proposal-level criteria with explicit `not_success` text; no inappropriate S4 claims on mock tools.

## 13. Multi-turn findings

12 attack `multi_turn_injection` episodes include ≥2 conversation turns and conversation/prior-turn locus. Harness v0 does not replay conversation — **PARTIALLY_EXECUTABLE**; flagged **REVIEW_HUMAN** (P1).

## 14. Memory/state findings

12 episodes include `memory_store` and/or `session_state` with state-gated loci. Harness does not load state — partial execution documented.

## 15. Cross-context findings

10 episodes include explicit `cross_context` blocks and `cross_boundary` path. Near-duplicate n-gram cluster (pairs 083–092): P4.2.1 **VALID_VARIANT**; automated **ACCEPT_CANDIDATE** with **REVIEW_HUMAN** and duplicate_risk **MEDIUM** (human confirmation of channel diversity recommended).

## 16. Multi-agent findings

4 episodes include `inter_agent_messages`; **DESIGNED_NOT_EXECUTABLE**. Automated status: **UNCERTAIN_HUMAN_REQUIRED** (P1).

## 17. Adaptive findings

4 episodes include full `adaptive_trace` phases; **DESIGNED_NOT_EXECUTABLE**. **UNCERTAIN_HUMAN_REQUIRED**.

## 18. Executability findings

| Status | Attack count |
|--------|-------------:|
| EXECUTABLE | 34 |
| PARTIALLY_EXECUTABLE | 58 |
| DESIGNED_NOT_EXECUTABLE | 8 |

Dataset capability ≠ harness v0 capability (conversation, tool_results, memory, cross_context, multi-agent, adaptive not consumed in `agent/loop.py`).

## 19. Near-duplicate review findings

114 flags (P4.2.1) adjudicated VALID_VARIANT; not reversed. **36 episodes** (pairs `p42_083`–`p42_100`) flagged for human confirmation of distinct mechanisms despite normalized n-gram collision.

## 20. P0/P1 issues

| Priority | Count |
|----------|------:|
| P0 | 0 |
| P1 | 132 |
| P2 | 34 |
| P3 | 34 |

No P0 integrity failures.

## 21. Human-review queue

132 episodes with `recommended_action=REVIEW_HUMAN` (partial/non-executable surfaces, near-dup clusters, multi-agent/adaptive families). See `docs/AIB_P4_2_2_HUMAN_REVIEW_PACKAGE.md` Section 5.

## 22. Recommended actions

| Action | Count |
|--------|------:|
| KEEP | 68 |
| REVIEW_HUMAN | 132 |
| REVISE_METADATA | 0 |
| REVISE_CONTENT | 0 |
| REJECT | 0 |

## 23. Dataset limitations

- Automated pre-review only; embedding dedup not performed.
- Small families: multi-agent (4), adaptive (4).
- Residual n-gram flags after P4.2.1.

## 24. Freeze readiness assessment

**Not ready for freeze.** Human adjudication and harness adapter coverage (P4.2.3) remain open.

## 25. Next gate

**Actual human adjudication** → **P4.2.3 harness/adapter coverage**.

---

> Automated pre-review was performed by the benchmark agent. Actual human scientific adjudication has not yet occurred.
