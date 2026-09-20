# Paper outline (draft)

Draft structure only — **no empirical ASR/utility claims** until live scorable traces are archived.

## 1. Introduction

- Problem: indirect prompt injection via untrusted retrieved content in tool-using agents
- Contribution: small twin episode benchmark + harness + offline scorers under shared schema
- Complement to ADAPTI-GUARD (external D2), not an in-repo defense evaluation
- Source text: intro bullets in prior `PAPER_INTRO_SNIPPET.md` (merged here conceptually)

## 2. Related work

- Greshake et al. — IPI threat model ([arXiv:2302.12173](https://arxiv.org/abs/2302.12173))
- Yi et al. — IPI benchmark/defense ([arXiv:2312.14197](https://arxiv.org/abs/2312.14197))
- InjecAgent — tool-agent IPI at scale ([arXiv:2403.02691](https://arxiv.org/abs/2403.02691))
- AgentDojo — dynamic agent eval ([arXiv:2406.13352](https://arxiv.org/abs/2406.13352))
- Positioning: complementary **small** measurement artifact; see [related_work.md](./related_work.md) and [reading_notes.md](./reading_notes.md); paste-ready prose in [draft_snippets.md](./draft_snippets.md)

## 3. Threat model

Canonical: [../docs/THREAT_MODEL.md](../docs/THREAT_MODEL.md)

## 4. Taxonomy

Canonical: [../docs/TAXONOMY.md](../docs/TAXONOMY.md)

## 5. Benchmark design

Canonical: [../docs/BENCHMARK.md](../docs/BENCHMARK.md)

## 6. Dataset

Canonical: [../docs/DATASET.md](../docs/DATASET.md)

## 7. Evaluation protocol

Canonical: [../docs/EVALUATION.md](../docs/EVALUATION.md), [../docs/EXPERIMENT_PROTOCOL.md](../docs/EXPERIMENT_PROTOCOL.md)

## 8. Experiments (to run)

- D0 full pilot on 40 episodes (required for any results section)
- Optional Phase C: D0 vs D1 matrix with documented N and Wilson CI
- Optional external D2 (ADAPTI-GUARD) case study — separate runner, same scorers

## 9. Results

*Pending live traces — store tables under `paper/tables/` when available; do not commit fabricated numbers.*

## 10. Limitations and reproducibility

Canonical: [../docs/LIMITATIONS.md](../docs/LIMITATIONS.md), [../docs/REPRODUCIBILITY.md](../docs/REPRODUCIBILITY.md)

## 11. Figures

Placeholders: `paper/figures/` (taxonomy distribution, twin schematic, trace flow)
