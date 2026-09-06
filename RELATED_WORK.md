# Related work mapping (base papers)

Pointers only. Citations do **not** claim that this scaffold reproduces their coverage, numbers, or threat models. This repo publishes **no** ASR/utility rates.

## 1. Greshake et al. 2023 — indirect prompt injection threat model

[arXiv:2302.12173](https://arxiv.org/abs/2302.12173) (*Not what you've signed up for*) frames **indirect prompt injection (IPI)**: malicious instructions arrive through untrusted content that an LLM-integrated application retrieves or otherwise ingests, rather than through the user’s explicit prompt alone. That threat model is the conceptual starting point for agent-injection-bench. Our episodes place the injection in `retrieved_docs` text while keeping `user_query` as an honest user request. Attack/benign **twins** share the same query so that the difference is contamination of retrieved context, not a changed user goal. Success is defined in terms of **tool misuse** (calling a forbidden tool such as `send_email`), which is a concrete agent-facing failure mode under that IPI framing.

- **Difference from this repo:** Greshake et al. analyze and demonstrate IPI against real integrated applications at threat-model breadth; we ship only a tiny fixed seed set, mock tools, and an undefended harness—no application-security case studies and no measured attack rates.

## 2. Yi et al. 2023 — IPI benchmark and defense

[arXiv:2312.14197](https://arxiv.org/abs/2312.14197) (*Benchmarking and Defending Against Indirect Prompt Injection Attacks on Large Language Models*) combines **benchmarking** of IPI with **defense** proposals. Conceptually we reuse the idea that IPI should be measured under controlled retrieval/context contamination and that attack success should be separated from ordinary task utility. We do **not** port their defense stack, training recipes, or full evaluation suite into this repository. Runtime mitigation is intentionally left to the separate **ADAPTI-GUARD** line of work (see [`ADAPTI_GUARD_BRIDGE.md`](ADAPTI_GUARD_BRIDGE.md)), so this artifact stays measurement-first.

- **Difference from this repo:** Yi et al. contribute both a broader IPI evaluation story and defenses; agent-injection-bench is attack data + undefended eval stubs only and must not be cited for defense results.

## 3. InjecAgent / Zhan et al. 2024 — tool-agent IPI benchmark

[arXiv:2403.02691](https://arxiv.org/abs/2403.02691) (*InjecAgent*) benchmarks indirect prompt injections against **tool-integrated** LLM agents at substantial scale (the paper reports on the order of **1054** cases). Their setting is closer to ours in that agents call tools and injections aim at agent behavior. Our v0 seed is deliberately tiny: **20 attack + 20 benign** episodes, **two mock tools** (`search_docs`, `send_email`), and **no defense** in-tree. Episode `source_paper` may cite InjecAgent for inspiration; that does not mean we reproduce their suite or claim comparable coverage.

- **Difference from this repo:** InjecAgent is a large tool-agent IPI benchmark; we are a small academic seed with mock tools and no published ASR from this artifact.

## 4. AgentDojo / Debenedetti et al. 2024 — dynamic agent environment

[arXiv:2406.13352](https://arxiv.org/abs/2406.13352) (*AgentDojo*) provides a **dynamic environment** for evaluating prompt injection attacks and defenses on LLM agents, with richer stateful tasks than a static JSON seed. Our harness instead loads **fixed** episode files, returns episode-bound documents from `search_docs`, and logs auditable traces for offline scoring stubs. That keeps packaging and researcher-run evaluation simple, at the cost of not modeling AgentDojo’s full environment dynamics or defense-evaluation surface.

- **Difference from this repo:** AgentDojo is a dynamic attack/defense evaluation environment; we offer a fixed 20+20 seed, a simple undefended loop, and no defense implementation.

## Paste-ready Related Work paragraph

Prior work establishes indirect prompt injection as a threat when untrusted retrieved or otherwise ingested content steers LLM-integrated systems (Greshake et al., 2023) and develops both benchmarks and defenses for that setting (Yi et al., 2023). Tool-using agents are a particularly relevant target: InjecAgent evaluates IPI at large scale over tool-integrated agents (Zhan et al., 2024), while AgentDojo provides a dynamic environment for attack and defense evaluation (Debenedetti et al., 2024). agent-injection-bench is a complementary **small** measurement artifact: fixed attack/benign twin episodes with injection in retrieved documents, two mock tools, an undefended harness, and offline ASR/utility stubs under a shared schema. We do not reproduce those suites’ scale or environments, implement defenses (including ADAPTI-GUARD) in this repository, or publish ASR/utility numbers until researchers obtain live non-error traces.
