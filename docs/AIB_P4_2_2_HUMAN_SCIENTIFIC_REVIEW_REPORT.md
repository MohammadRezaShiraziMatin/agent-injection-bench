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

## 26. Taxonomy consistency audit — interaction_type × horizon (P4.2.2-HR follow-up)

**Audit question:** After Batch 1 REVISE resolution, are `taxonomy.interaction_type=single_turn` with `taxonomy.horizon=h1` (atk_p42_093–096) and `single_turn` with `horizon=ha` (atk_p42_097–100) schema-valid and scientifically coherent?

**Sources reviewed:** `docs/AIB_P4_2_TAXONOMY_V2.md`, `schema/episode.v2.json`, `data/episodes_p4_2/attack/atk_p42_093.json`–`atk_p42_100.json`, `data/episodes_p4_2/benign/ben_p42_093.json`–`ben_p42_100.json`, `scripts/p4_2_episode_bank.py` (generator encoding), `scripts/pre_review_p4_2_2.py`, `scripts/qc_p4_2.py`, `artifacts/p4_2_2_hr_audit_trail.json` (Batch 1 REVISE resolution), full P4.2 cross-tab of interaction_type × horizon (200 episodes).

### Taxonomy definitions (as written)

| Dimension | Documented definition | Schema constraint |
|-----------|----------------------|-------------------|
| `interaction_type` | Controlled values `single_turn`, `multi_turn` only (`AIB_P4_2_TAXONOMY_V2.md` §Dimensions). No prose definition of “turn” in V2. | Enum; no cross-field rules with `horizon`. |
| `horizon` | Controlled values `h0`, `h1`, `h2`, `ha`. Only **family-level** note: `adaptive_injection` → `horizon=ha` (static trace; not live adaptive). **No** prose definitions for `h0`/`h1`/`h2` in V2. | Enum; independent of `interaction_type`. |
| Cross-field | **Not specified** in V2 taxonomy doc or JSON Schema. | `pre_review_p4_2_2.py` flags only `multi_turn` + `h0` (not `single_turn` + `h1`). |

**Doc vs schema:** No conflict on allowed values. **Gap:** V2 does not define semantic meaning of `h0`/`h1`/`h2` or whether `h1` requires `multi_turn`.

**Implicit project convention (generator, not normative in V2):** In `scripts/p4_2_episode_bank.py`, `multi_turn_injection` uses `h1` vs `h2` to distinguish **conversation depth** (2 vs 4 `conversation[]` turns before the final user query). P4.1 plan table shows `h1` only on a `multi_turn` pair (`p41_04`).

### Batch 1 episodes (evidence)

| Episode | Turns (harness) | `conversation[]` | Injection | `interaction_type` | `horizon` | `family` | Executability |
|---------|-----------------|------------------|-----------|-------------------|-----------|----------|---------------|
| atk_p42_093–096 | 1 `user_query` | absent | `inter_agent_message[0]` | `single_turn` | `h1` | `multi_agent_injection` | `DESIGNED_NOT_EXECUTABLE` |
| atk_p42_097–100 | 1 `user_query` (narrative prior refusal in text only) | absent | `adaptive_trace.attempt_2` | `single_turn` | `ha` | `adaptive_injection` | `DESIGNED_NOT_EXECUTABLE` |

**Multi-agent (093–096):** One coordinator user message + one inter-agent message; S2 via `send_email` proposal; not reducible to `multi_turn_injection` (no `prior_turn` / conversation replay). **Horizon `h1` is not documented as “inter-agent hop” in V2**; it is only empirically reused from generator defaults for this family.

**Adaptive (097–100):** Full static `adaptive_trace` (attempt_1 → observation → adaptation → attempt_2); notes state non-live adaptive. **`single_turn` + `ha` aligns with V2 family note** (ha = adaptive design axis; harness presents one user turn).

**Benign twins (093–100):** Still `multi_turn` + `h1` (093–096) or `multi_turn` + `ha` (097–100) while attack twins were revised to `single_turn`. Pair-level taxonomy **asymmetry** on `interaction_type` (documented; no mutation in this audit).

### Consistency matrix (P4.2 corpus)

| interaction_type | horizon | Count | Schema-valid? | Evidence |
|------------------|---------|------:|---------------|----------|
| single_turn | h0 | 160 | Yes | Default for direct/indirect/RAG/etc. |
| single_turn | h1 | 4 | Yes | **Only** atk_p42_093–096 (`multi_agent_injection`) |
| single_turn | ha | 4 | Yes | atk_p42_097–100; matches V2 `adaptive_injection` + `ha` |
| multi_turn | h1 | 16 | Yes | atk_p42_059–064 + benign twins; `multi_turn_injection`, `conversation` len 2 |
| multi_turn | h2 | 12 | Yes | `multi_turn_injection`, deeper `conversation` |
| multi_turn | ha | 4 | Yes | ben_p42_097–100 only (benign adaptive controls) |

### Audit decision

| Outcome | Label |
|---------|--------|
| **Schema / enum** | **CONSISTENT** — all combinations validate; no schema rule forbids `single_turn` + `h1`. |
| **V2 prose** | **AMBIGUOUS** for `h0`/`h1`/`h2` meaning and for whether `h1` implies multi-turn user conversation. |
| **Dataset mutation** | **NONE** — no evidence-backed mandatory field change; changing `h1`→`h0` on multi-agent attacks would be interpretive without V2 normative definition. |

**Recommended interpretation (non-binding):** Treat `interaction_type` as **harness/user-dialogue turn model**; treat `horizon` as **temporal/design depth** where `ha` is reserved for adaptive trace designs per V2. Multi-agent `h1` is **conventionally overloaded** (generator default) but not schema-invalid.

### Validation (this audit)

| Check | Result |
|-------|--------|
| P4.2 digest | Unchanged: `4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee` |
| P4.1 / V0 | Unchanged (`verify_p6_freeze.py` PASS; no diff on `data/episodes/`, `data/episodes_v1/`) |
| `qc_p4_2.py` | PASS |
| `pytest` | 32 passed |

### Unresolved risks

1. V2 lacks normative definitions for `h0`/`h1`/`h2` (documentation gap).
2. Attack vs benign `interaction_type` mismatch on pairs p42_093–p42_100 (Batch 1 resolution applied to attack REVISE only).
3. Optional future human gate: align benign `interaction_type` with attack twins or document intentional pair asymmetry for controls.

### Next gate (Batch 2)

**READY** for Batch 2 Human Scientific Review (taxonomy audit does not block). Optional follow-up: metadata-only pair alignment or V2 horizon glossary (human-authored).

---

> Automated pre-review was performed by the benchmark agent. Actual human scientific adjudication has not yet occurred.
