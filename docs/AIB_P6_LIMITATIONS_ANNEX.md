# AIB P6 Limitations Annex

**Freeze ID:** `aib-p4.1-frozen-v1.0`  
**Source:** P5.5 final scientific closure (`docs/AIB_P5_5_FINAL_SCIENTIFIC_CLOSURE_REPORT.md` §9)  
**Status:** Frozen documentation. These bounds are **not** closed by P6.

P6 is an immutability operation. It does **not** extend the harness, run embeddings, update `review_status`, or recover historical P4.

---

## L1 — Runtime harness coverage

The current default harness (`agent/loop.py`) loads only:

```text
user_query
retrieved_docs
```

It does **not** load:

```text
tool_results
conversation
cross_context
memory_store
session_state
```

Therefore P4.1’s richer surfaces are **not yet fully exercised** by the default runtime evaluator. Episodes that place the injection outside `retrieved_docs` remain scientifically specified in the dataset; default-loop E2E coverage is incomplete until a future harness loader (out of P6 scope).

This does **not** invalidate the frozen JSON. It limits **runtime evaluation fidelity**.

---

## L2 — Semantic paraphrase detection

P5.3 Attack Content Fingerprint (ACF) screening (`scripts/semantic_dedup_p4_1.py`):

```text
P4.1 ↔ P4.1: 0 DUPLICATE, 0 POSSIBLE_NEAR_DUPLICATE
P4.1 ↔ v0:   0 DUPLICATE, 0 POSSIBLE_NEAR_DUPLICATE
```

ACF uses normalized fused text and character n-gram similarity.

**Embedding-based semantic paraphrase detection was not performed.**

Do not claim that all semantic duplicates were eliminated or that semantic equivalence was completely verified.

---

## L3 — Human review metadata

Every P4.1 episode records:

```text
provenance.review_status = unreviewed
provenance.reviewed = false
```

These fields are **schema-locked** (`schema/episode.v1.json` consts). They remain **truthful** for the JSON objects: the generator is synthetic; episode-level review flags were never flipped.

P5.4 human-style adjudication is documented in `docs/AIB_P5_4_HUMAN_ADJUDICATION_REPORT.md` and closed in `docs/AIB_P5_4_1_METADATA_CLOSURE_REPORT.md`. That process is **report-level governance**, not a change to episode `review_status`.

P6 does **not** relabel `unreviewed` merely because adjudication reports exist.

---

## L4 — Benign taxonomy

After P5.4.1:

- Nine benign episodes use `taxonomy.objective = benign_control` with `objective_note` stating that `taxonomy.family` names the **paired evaluation surface**, not an injection claim.
- `ben_p41_08` keeps `family=memory_poisoning`, which the schema `allOf` requires to use `objective=unauthorized_state_change` plus `objective_note`. The control is still `split=benign`, `injection.present=false`, `expected.success_criterion=S0`.
- Frozen `family` enums still contain `*_injection` / `memory_poisoning` names on benign rows. That is a **schema channel label**, not a claim that the benign file contains an injection.

Do not expand the frozen taxonomy in P6 to invent a separate benign family enum.

---

## L5 — Historical P4

P4.1 is a **new controlled reconstruction**.

Historical P4 artifacts were **not recovered** (git history, remotes, and the historical package archive). P4.1 is **not**:

- recovered P4
- reconstructed historical P4
- restored P4
- the original P4 dataset

---

## Non-blocking for freeze

These limitations were accepted at P5.5 as **documentation conditions** for freeze authorization. They remain open **operational/scientific bounds**, not P6 hash/integrity failures.
