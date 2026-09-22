# AIB P4.4 Independent Validation Dataset Freeze

**Freeze ID:** `aib-p4.4-validation-v1.0`  
**Status:** byte-frozen, `review_status=unreviewed` (no human adjudication pass yet).

| Field | Value |
|-------|-------|
| Path | `data/episodes_p4_4/` |
| Schema | `schema/episode.p44.v1.json` (sibling of `episode.v2.json`; v2 was not edited) |
| Episodes | 200 (100 attack / 100 benign / 100 pairs) |
| Digest | `d5132fb3a4897684e1cb8a6f38f7cd367ee2a928bcd351743f73f13c326d796f` |
| Seed | `44020260922` |
| Generator | `gen_p4_4_dataset.py@1.0.0` |
| Timestamp | `2026-09-22T00:00:00Z` |

`episode.v2.json` cannot represent this corpus: `dataset_version` is const `P4.2` and ids must match `p42_`. The sibling schema changes only those identity consts.

Difficulty is not a new enum. Strata `low` / `mid` / `high` are recorded from existing `executability`, `path`, and `horizon`. Success criteria stay `S1` (8 instruction-deviation attacks) and `S2` (92 tool-proposal attacks). Non-executable families are labeled `PARTIALLY_EXECUTABLE` or `DESIGNED_NOT_EXECUTABLE`.

Benign episodes quote the attack line as a prohibited training example and ask for the published rule. They are hard negatives, not relabeled attacks.

Leakage against P4.2 and P4.3 attacks: exact payload 0, normalized query 0, ACF 0, ngram Jaccard below 0.88 (max observed 0.5).

Parent digests unchanged: P4.2 `4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee`, P4.3 `e60969bee257ec3111febf215fb5f7079edb79ed050dae300e549336184ab53d`.
