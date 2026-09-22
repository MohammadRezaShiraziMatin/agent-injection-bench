# P4.2.2-HR — Human Scientific Adjudication Workflow

> **Status:** Review package **READY**. **Actual human adjudication has not been performed.** The benchmark agent does not record `human_decision` values.

## Purpose

Convert P4.2.2 automated pre-review into an auditable workflow for a **real** researcher to adjudicate all 200 P4.2 candidate episodes before harness/adapter work (P4.2.3).

## Immutability

- **P4.1** frozen (`aib-p4.1-frozen-v1.0`) — do not modify.
- **v0** — do not modify.
- **P4.2 episode JSON** — no content edits in this phase unless a future revision gate applies a documented human `REVISE` outcome.

## Artifacts

| Artifact | Role |
|----------|------|
| `artifacts/p4_2_2_human_review_matrix.json` | Automated pre-review (200 rows); human fields **null** |
| `artifacts/p4_2_2_hr_review_queue.json` | Batch-ordered review cards + evidence pointers |
| `artifacts/p4_2_2_hr_episode_evidence.json` | Full content/taxonomy excerpts per episode |
| `artifacts/p4_2_2_hr_audit_trail.json` | Append-only log for human decisions (`decisions: []` until review) |
| `artifacts/p4_2_1_near_duplicate_adjudication.json` | 114 VALID_VARIANT flags (do not auto-reverse) |

Regenerate HR artifacts (deterministic, no network):

```bash
python scripts/build_p4_2_2_hr_package.py
```

## Human decision vocabulary

| Decision | Meaning |
|----------|---------|
| `ACCEPT` | Scientifically valid for the candidate benchmark |
| `REVISE` | Specific correction required (defer edits to revision phase) |
| `REJECT` | Should not remain in benchmark |
| `UNCERTAIN` | Insufficient evidence; needs further review |

## Decision guide (consistency)

- **ACCEPT:** Mechanism matches taxonomy; trust boundary clear; success criterion (S0–S4) honest; pair valid.
- **REVISE:** Metadata wrong, weak control, or mechanism not supported by episode fields.
- **REJECT:** Not injection, broken pair, or fundamentally unsuitable (use conservatively).
- **UNCERTAIN:** Ambiguous multi-turn dependence, adaptive trace, or similarity cluster without consensus.

Principle: **proposal ≠ execution ≠ external side effect.**

## Review batches (recommended order)

1. **batch_1_uncertain** — 16 episodes (`UNCERTAIN_HUMAN_REQUIRED`; multi-agent + adaptive pairs).
2. **batch_2_complex_families** — 96 episodes (partial/non-executable surfaces, complex families).
3. **batch_3_similarity_confirmation** — 20 episodes (cross-context pairs `p42_083`–`p42_092`; P4.2.1 VALID_VARIANT confirmation).
4. **batch_4_remaining_p1** — (empty if all P1 covered above).
5. **batch_5_p2_p3** — 68 lower-risk executable episodes.

**Note:** Similarity cluster pairs `p42_093`–`p42_100` appear in **batch_1** (uncertain) — total **36** episodes across pairs `p42_083`–`p42_100` require human confirmation per P4.2.1.

## Recording a human decision (audit trail)

Append one object per episode to `artifacts/p4_2_2_hr_audit_trail.json` → `decisions`:

```json
{
  "episode_id": "atk_p42_093",
  "previous_automated_status": "UNCERTAIN_HUMAN_REQUIRED",
  "human_decision": "ACCEPT",
  "human_reviewer": "<real name or id>",
  "review_date": "2026-09-21",
  "human_notes": "Inter-agent path documented; non-executable acknowledged."
}
```

Do **not** set `review_status=human_reviewed` on episode files until a project policy explicitly links audit trail → dataset metadata.

## Per-episode review checklist

See P4.2.2-HR prompt sections 9–19 (attack mechanism, S0–S4, multi-turn, memory, cross-context, multi-agent, adaptive, tool-output, RAG/web, benign controls, pairs).

## Prohibited

- Fabricated reviewer name/date/signature
- Auto-filling `human_decision` from `ACCEPT_CANDIDATE`
- Content paraphrase to reduce n-gram similarity
- Live LLM / AdaptiGuard / D0–D2 evaluation in this phase
- Git push / freeze tag

## Next gate

After real human decisions are recorded: **P4.2.3 Harness/Adapter Coverage**.
