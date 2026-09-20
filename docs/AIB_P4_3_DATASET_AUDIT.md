# AIB P4.3 — Complete Dataset Audit (P4.2 baseline)

**Audit date:** 2026-09-20 (UTC)  
**Branch:** `cursor/p4-2-dataset-6db2`  
**Baseline HEAD:** `95295684b558d6e2d59161a64ab4e7f10f1ee0fe`  
**Dataset under audit:** `data/episodes_p4_2/` (frozen **P4.2**, immutable)  
**Schema:** `schema/episode.v2.json`

## Repository evidence (source of truth)

| Check | Result |
|-------|--------|
| `scripts/verify_p4_2_freeze.py` | PASS |
| Digest | `4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee` |
| Episodes | 200 (100 attack / 100 benign / 100 pairs) |
| Freeze tag | `aib-p4.2-frozen-v1.0` |
| `scripts/qc_p4_2.py` | PASS (issues=[], leakage_ok=true, byte_identical_regeneration=true) |

---

## Phase 1 — Coverage distributions

Counts below are **attack episodes** unless noted. All 10 required families present (10 attack / 10 benign pairs each, except families with 12 or 14 attack episodes as listed).

### Taxonomy (attack)

| Dimension | Distribution |
|-----------|--------------|
| **family** | `rag_document_injection` 16; `tool_output_injection` 14; `multi_turn_injection` 12; `memory_state_injection` 12; `direct_prompt_injection` 10; `web_retrieved_content_injection` 10; `cross_context_injection` 10; `indirect_prompt_injection` 8; `adaptive_injection` 4; `multi_agent_injection` 4 |
| **objective** | `unauthorized_tool_proposal` 87; `unauthorized_state_change` 12; `data_exfiltration` 1 |
| **source** | `retrieved_document` 24; `tool_output` 14; `prior_turn` 12; `user_message` 10; `web_retrieved_content` 10; `auxiliary_context` 10; `memory_store` 6; `session_state` 6; `attacker_observation` 4; `inter_agent_message` 4 |
| **target** | `send_email` 90; `agent_memory` 6; `peer_agent` 4 |
| **path** | `indirect` 50; `direct_tool_channel` 14; `state_gated` 12; `direct` 10; `cross_boundary` 10; `multi_agent_channel` 4 |
| **interaction_type** | `single_turn` 88; `multi_turn` 12 |
| **horizon** | `h0` 80; `h1` 10; `h2` 6; `ha` 4 |
| **context_type** | campus_hr 17; campus_facilities 16; campus_finance 15; campus_it 15; campus_compliance 11; campus_research 9; campus_security 9; campus_health 8 |

### Low-sample cells (scientific note, not QC failure)

| Cell | Count | Note |
|------|------:|------|
| `data_exfiltration` objective | 1 | Rare objective by design |
| `multi_agent_injection` family | 4 pairs | Surface not live-executable |
| `adaptive_injection` family | 4 pairs | Surface not live-executable |
| `peer_agent` target | 4 | Tied to multi-agent family |
| `ha` horizon | 4 | Adaptive horizon only |

### Structural surface presence (attack / benign)

| Surface | Attack | Benign |
|---------|-------:|-------:|
| `conversation` | 12 | 12 |
| `tool_results` | 14 | 14 |
| `memory_store` | 12 | 12 |
| `session_state` | 6 | 6 |
| `cross_context` | 10 | 10 |

### Success criteria (impact horizon labeling)

| Split | success_criterion |
|-------|-------------------|
| Attack (100) | **S2** only |
| Benign (100) | **S0** only |

**S3 / S4:** Not represented as primary success labels. Mock harness cannot observe real external side effects (`docs/AIB_P7_EVALUATION_PROTOCOL.md`, `tools/mock_send_email.py`). This is an **environment limitation**, not missing JSON fields to fabricate.

### Partitions

| Partition | Episodes |
|-----------|----------|
| development | 120 |
| validation | 40 |
| test | 40 |

---

## Phase 2 — Attack taxonomy audit (10 families)

| Family | Atk | Ben | Pairs | Primary source | Primary target | Executability (post P4.2.4 harness) |
|--------|----:|----:|------:|----------------|----------------|-------------------------------------|
| direct_prompt_injection | 10 | 10 | 10 | user_message | send_email | EXECUTABLE |
| indirect_prompt_injection | 8 | 8 | 8 | retrieved_document | send_email | EXECUTABLE |
| rag_document_injection | 16 | 16 | 16 | retrieved_document | send_email | EXECUTABLE |
| web_retrieved_content_injection | 10 | 10 | 10 | web_retrieved_content | send_email | EXECUTABLE |
| tool_output_injection | 14 | 14 | 14 | tool_output | send_email | EXECUTABLE |
| multi_turn_injection | 12 | 12 | 12 | prior_turn | send_email | EXECUTABLE |
| memory_state_injection | 12 | 12 | 12 | memory_store / session_state | send_email / agent_memory | 12 EXEC + 12 PARTIAL (session_state gating) |
| cross_context_injection | 10 | 10 | 10 | auxiliary_context | send_email | EXECUTABLE |
| multi_agent_injection | 4 | 4 | 4 | inter_agent_message | peer_agent | DESIGNED_NOT_EXECUTABLE |
| adaptive_injection | 4 | 4 | 4 | attacker_observation | send_email | 4 PARTIAL + 4 DNE (adaptive_loop) |

**coverage_gap:** Families with DNE/PARTIAL are **represented in the dataset** for taxonomy completeness; gaps are **harness/runtime**, not missing JSON episodes.

---

## Phase 3 — Attack surface completeness

| Surface | Dataset | Harness (P4.2.4) | Live model |
|---------|---------|------------------|------------|
| user input | covered | supported | not evaluated here |
| retrieved documents / RAG | covered | supported | not evaluated here |
| web content (as doc snippet) | covered | partial (no crawler) | not evaluated here |
| tool output | covered | supported (adapters) | not evaluated here |
| conversation history | covered | supported (replay) | not evaluated here |
| memory_store | covered | supported (adapter) | not evaluated here |
| session_state | covered | partial (gated paths) | not evaluated here |
| cross_context | covered | supported | not evaluated here |
| inter-agent messages | covered | **unsupported** (DNE) | not evaluated here |
| adaptive traces | covered | **unsupported** (DNE) | not evaluated here |
| tool selection / arguments | covered via S2 tool schema | supported | not evaluated here |
| external action / S4 | **not claimable** | mock only | not evaluated here |

---

## Phase 4 — Horizon / impact (S0–S4)

| Level | In dataset | Executable observation |
|-------|------------|------------------------|
| S0 | 100 benign | utility substring checks |
| S1 | (not primary label) | — |
| S2 | 100 attack | structured forbidden tool proposal |
| S3 | not primary | mock logs proposal vs execution; not SMTP |
| S4 | not represented | **by design** in mock environment |

Escalation path in data: taxonomy `horizon` (`h0`–`ha`) varies; **labeled success remains S2/S0**.

---

## Phase 5 — Benign control quality

| Metric | Value |
|--------|------:|
| Pairs with benign `injection.present=false` | 100/100 (QC enforced) |
| Mean user_query Jaccard (attack vs benign) | 0.934 |
| Pairs with Jaccard > 0.85 | 90/100 |

**objective_mismatch (attack vs benign):** 94/100 pairs — **expected**: attacks use `unauthorized_tool_proposal` / `unauthorized_state_change` while benign twins use `legitimate_completion` (or equivalent) per generator design. Not flagged as unfair control.

**HR scientific review:** `artifacts/p4_2_2_hr_audit_trail.json` — 200 decisions (192 ACCEPT, 8 REVISE metadata-only). Episode field `provenance.review_status` remains `unreviewed` for all 200 (**metadata drift vs HR artifact**; see gaps).

---

## Phase 6 — Duplicate / semantic dedup

| Check | Result |
|-------|--------|
| ACF exact duplicates (attacks) | **0** (`qc_p4_2.py`) |
| Cross-version ACF leakage (v0, P4.1) | **0** |
| N-gram Jaccard ≥ 0.88 (`semantic_dedup_p4_2.py`) | **105** flagged pairs (mostly `adaptive_injection` cluster `atk_p42_083`–`092` and related batches) |
| Embedding semantic dedup | **not performed** (QC + contract document recommendation) |

**Interpretation:** High n-gram similarity within adaptive batches reflects **shared template surfaces** with distinct pair IDs; not ACF duplicates. **Human adjudication** required before treating as near-duplicate violations — do not auto-delete.

---

## Phase 7 — Executability audit

`scripts/measure_p4_2_harness_coverage.py` (harness **p4.2.4**):

| Label | Count |
|-------|------:|
| EXECUTABLE | 172 |
| PARTIALLY_EXECUTABLE | 16 |
| DESIGNED_NOT_EXECUTABLE | 12 |

| Missing surface (DNE) | Episodes |
|-----------------------|----------|
| multi_agent_channel | 8 |
| adaptive_loop | 4 |
| session_state (partial) | 12 |

**Replay observability ≠ live execution** for PARTIAL/DNE families.

---

## Phase 8 — Provenance

| Field | Finding |
|-------|---------|
| `provenance.synthetic` | **true** (200/200) |
| `provenance_type` | `programmatically_generated` |
| `generator_version` | `gen_p4_2_dataset.py@1.0.0` |
| `seed` | `42020260920` (constant in episodes) |
| Real-world claims | **None** in sampled episodes |
| `provenance.review_status` | `unreviewed` in all episode JSON (**does not reflect HR ACCEPT**) |

---

## Phase 9 — Quality contract

Machine-checkable contract: `config/p4_3_quality_contract.v1.json` (maps to `qc_p4_2.py`, `semantic_dedup_p4_2.py`, `verify_p4_2_freeze.py`, HR trail).

---

## Phase 10 — Gap analysis

| Gap | Evidence | Impact | Status | Proposed fix | Risk |
|-----|----------|--------|--------|--------------|------|
| P0 integrity | verify_p4_2_freeze PASS | baseline trust | **closed** | none | — |
| P1 HR vs episode review_status | HR 200 decisions; episode `unreviewed` | provenance UX | open | metadata sync in **future** candidate only | mutating frozen P4.2 |
| P1 objective pair mismatch semantics | 94/100 pairs | scientific clarity | documented | document in benchmark card | misread as bug |
| P2 S3/S4 not primary labels | 100% S2/S0 | impact breadth | open | document; optional future harness with real tools **outside** P4.2 | fake S4 |
| P2 DNE surfaces (8+4 ep) | harness coverage | live eval scope | open | harness extension, **not** more episodes | scope creep |
| P2 near-dup n-gram cluster | semantic_dedup flags | validity | open | human review of adaptive cluster | auto-dedup unsafe |
| P3 embedding dedup | not implemented | optional | open | design-only recommendation | heavy deps |
| P3 low-count objectives | data_exfiltration=1 | coverage | acceptable | only add with justification in P4.3+ | balance gaming |

---

## Phase 11–12 — P4.3 design decision

**DO NOT CREATE P4.3 dataset candidate at this time.**

Rationale:

1. P4.2 passes schema, pairing, dedup (ACF), leakage, and reproducibility gates.  
2. Identified gaps are **harness**, **labeling documentation**, and **optional dedup science** — not corrected by adding random episodes.  
3. Creating episodes without new harness surfaces would **inflate N without increasing live-mechanism coverage**.

See `docs/AIB_P4_3_DATASET_PLAN.md` for hardening-only roadmap.
