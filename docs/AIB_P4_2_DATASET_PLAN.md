# AIB P4.2 Dataset Plan

## Objective

Design and materialize an expanded, defense-agnostic benchmark dataset **P4.2** without modifying frozen **P4.1** (`data/episodes_v1/`, tag `aib-p4.1-frozen-v1.0`) or **v0** (`data/episodes/`).

## Forensic inventory (repository)

| Version | Path | Episodes | Attack | Benign | Pairs | Schema | Generator | Manifest |
|---------|------|----------|--------|--------|-------|--------|-----------|----------|
| v0 | `data/episodes/` | 42 | 21 | 21 | — | `schema/episode.schema.json` | legacy / static | none |
| P4.1 (frozen) | `data/episodes_v1/` | 20 | 10 | 10 | 10 | `schema/episode.v1.json` | `scripts/gen_p4_1_dataset.py` | yes (`digest_sha256` frozen) |
| P4.2 (candidate) | `data/episodes_p4_2/` | 200 | 100 | 100 | 100 | `schema/episode.v2.json` | `scripts/gen_p4_2_dataset.py` | yes (candidate, not frozen) |

P4.1 immutability verified via `scripts/verify_p6_freeze.py` (digest `717458789217d4fd29c655e40018471fdaf16b061ff5481cfdc48f7812437ac3`, seed `41020260920`).

## Size decision

| Target | Episodes | Rationale |
|--------|----------|-----------|
| Minimum (200) | **200** (chosen) | Meets minimum while preserving mechanism-level diversity across 10 families |
| Preferred (400) | not used | Would require repetitive templating across families already constrained by harness fidelity; quality prioritized over round count |

## Stratified coverage (100 attack pairs)

| Family | Attack pairs | Executability |
|--------|--------------|---------------|
| `direct_prompt_injection` | 10 | EXECUTABLE |
| `indirect_prompt_injection` | 8 | EXECUTABLE |
| `rag_document_injection` | 16 | EXECUTABLE |
| `web_retrieved_content_injection` | 10 | PARTIALLY_EXECUTABLE |
| `tool_output_injection` | 14 | PARTIALLY_EXECUTABLE |
| `multi_turn_injection` | 12 | PARTIALLY_EXECUTABLE |
| `memory_state_injection` | 12 | PARTIALLY_EXECUTABLE |
| `cross_context_injection` | 10 | PARTIALLY_EXECUTABLE |
| `multi_agent_injection` | 4 | DESIGNED_NOT_EXECUTABLE |
| `adaptive_injection` | 4 | DESIGNED_NOT_EXECUTABLE |

## Partitions

| Partition | Attack pairs | Episodes |
|-----------|--------------|----------|
| `development` | 60 | 120 |
| `validation` | 20 | 40 |
| `test` | 20 | 40 |

Field: `dataset_partition` (attack/benign role remains `split`).

## Architecture separation

Dataset episodes define surfaces and expected success semantics only. Execution adapters (`agent/loop.py` today) and evaluation (P7 protocol) are separate layers. No defense labels, model outcomes, or AdaptiGuard fields in episodes.

## Deliverables

- Schema: `schema/episode.v2.json`
- Generator: `scripts/gen_p4_2_dataset.py`, `scripts/p4_2_episode_bank.py`
- QC: `scripts/qc_p4_2.py`, `scripts/semantic_dedup_p4_2.py`
- Tests: `tests/test_p4_2_dataset.py`
- Documentation: taxonomy, executability matrix, quality report, dataset card, benchmark card

## Freeze policy

P4.2 is a **candidate** only. No `aib-p4.2-frozen-*` tag in this phase.
