# Reading notes — base IPI papers

Structured notes for researchers packaging agent-injection-bench. Academic tone; **no** ASR/utility numbers from this repository. See also [`RELATED_WORK.md`](RELATED_WORK.md).

---

## Greshake et al. 2023

- **Citation + arXiv:** Kai Greshake, Sahar Abdelnabi, Shailesh Mishra, Christoph Endres, Thorsten Holz, and Mario Fritz. *Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection*. [arXiv:2302.12173](https://arxiv.org/abs/2302.12173).
- **Core claim:** LLM-integrated applications are vulnerable when untrusted content is ingested into the model context, allowing **indirect prompt injection (IPI)** that is not typed by the user as an adversarial prompt. The paper establishes the threat model and demonstrates how such injections can compromise real integrated systems.
- **Reading questions:**
  - *Where does the malicious instruction enter?* Through retrieved or otherwise ingested application data (e.g., documents, web content), not primarily through an overt adversarial user prompt.
  - *What fails if injection succeeds?* Application behavior can diverge from the user’s intent, including actions mediated by the integrated system’s capabilities.
  - *What does “indirect” exclude?* Direct jailbreak-style user prompting as the sole attack channel; the distinctive path is untrusted context the system chooses to include.
- **Mapping to agent-injection-bench:**
  - Injection lives in `retrieved_docs`; `user_query` remains an honest task.
  - Attack/benign twins isolate contamination of retrieval context.
  - Attack success is framed as forbidden **tool misuse** (`send_email`), a concrete agent-side failure mode under IPI.
- **What NOT to claim from our repo:** Do not claim to reproduce Greshake et al.’s real-application case studies, threat coverage, or any attack-success rates; this artifact has no published IPI measurements.
- **Paste-ready Related Work sentence:** Greshake et al. (2023) introduce indirect prompt injection as a threat arising from untrusted content ingested by LLM-integrated applications. Our seed episodes adopt that threat framing by placing injections in retrieved documents while holding the user query fixed.

---

## Yi et al. 2023

- **Citation + arXiv:** Jingwei Yi, Yueqi Xie, Bin Zhu, Keegan Hines, Emre Kiciman, Guangzhong Sun, Xing Xie, and Fangzhao Wu. *Benchmarking and Defending Against Indirect Prompt Injection Attacks on Large Language Models*. [arXiv:2312.14197](https://arxiv.org/abs/2312.14197).
- **Core claim:** IPI should be evaluated systematically under controlled settings that expose models to contaminated external content, and defenses should be studied alongside that evaluation. The work couples a benchmarking perspective with defense proposals rather than threat description alone.
- **Reading questions:**
  - *What is being measured?* Susceptibility of LLMs to instructions embedded in untrusted context, under a structured evaluation design.
  - *How do attack and utility relate?* Robustness claims are incomplete without checking that ordinary task behavior remains usable; defense work must confront that trade-off.
  - *Where do defenses belong in our stack?* Outside this measurement repo—aligned with ADAPTI-GUARD, not with episode JSON or scorers here.
- **Mapping to agent-injection-bench:**
  - Reuses the conceptual split between measuring IPI under contaminated retrieval and tracking task utility.
  - Offline ASR/utility stubs mirror that separation at a minimal scale.
  - Explicitly does **not** import Yi et al.’s defense methods into this tree ([`ADAPTI_GUARD_BRIDGE.md`](ADAPTI_GUARD_BRIDGE.md)).
- **What NOT to claim from our repo:** Do not claim we implement, evaluate, or match their defenses, dataset scale, or reported mitigation results; cite this repo only as a small undefended measurement scaffold.
- **Paste-ready Related Work sentence:** Yi et al. (2023) benchmark indirect prompt injection and study defenses in tandem. agent-injection-bench borrows only the measurement orientation (contaminated context vs. utility) and leaves defense evaluation to separate work such as ADAPTI-GUARD.

---

## InjecAgent / Zhan et al. 2024

- **Citation + arXiv:** Qiusi Zhan, Zhixiang Liang, Zifan Ying, and Daniel Kang. *InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents*. [arXiv:2403.02691](https://arxiv.org/abs/2403.02691).
- **Core claim:** Tool-integrated LLM agents are a distinct IPI evaluation surface because success often means inducing unintended **tool use**, not only corrupted text generation. InjecAgent provides a large-scale benchmark (on the order of **1054** cases in the paper) for that setting.
- **Reading questions:**
  - *Why tools matter?* Agents can act; injection that triggers a harmful or out-of-scope tool call is a security-relevant success criterion.
  - *What scale do they target?* A broad case suite far larger than our v0 seed; we must not imply parity of coverage.
  - *What can we cite honestly?* Conceptual kinship (tool-agent IPI) and optional `source_paper` inspiration—not reproduction of their suite or numbers.
- **Mapping to agent-injection-bench:**
  - Same broad class: tool-using agent, injection aiming at tool behavior.
  - Ours: **20+20** twins, **two mock tools** (`search_docs`, `send_email`), undefended harness, offline stubs.
  - Scorable success = forbidden tool name appearing in the trace—not a claim of InjecAgent-comparable ASR.
- **What NOT to claim from our repo:** Do not claim coverage comparable to InjecAgent’s ~1054 cases, their tool ecosystem, their empirical ASR figures, or any defense results; our package publishes no evaluation rates.
- **Paste-ready Related Work sentence:** InjecAgent (Zhan et al., 2024) benchmarks indirect prompt injection against tool-integrated agents at large scale. Our artifact is a complementary tiny seed (20 attack / 20 benign episodes, two mock tools) and does not reproduce that suite or report ASR from this repository alone.

---

## AgentDojo / Debenedetti et al. 2024

- **Citation + arXiv:** Edoardo Debenedetti, Jie Zhang, Mislav Balunović, Luca Beurer-Kellner, Marc Fischer, and Florian Tramèr. *AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents*. [arXiv:2406.13352](https://arxiv.org/abs/2406.13352).
- **Core claim:** Evaluating agent prompt injection (and defenses) benefits from a **dynamic environment** with stateful tasks, rather than static prompts alone. AgentDojo supplies such an environment for attack and defense experimentation.
- **Reading questions:**
  - *What does “dynamic” buy?* Stateful interactions and richer task structure than a single fixed context dump.
  - *What do we intentionally simplify?* Fixed episode JSON, episode-bound `search_docs`, and a short tool loop with auditable traces.
  - *Can we host defenses here?* No—AgentDojo’s defense-evaluation role is out of scope; our bridge points to a separate defended runner later.
- **Mapping to agent-injection-bench:**
  - Shared interest: agents, injection, measurable outcomes.
  - Ours: static seed files + simple harness + offline scorers; no AgentDojo environment.
  - Trace schema is for researcher-run comparison under a fixed format, not a dynamic sandbox.
- **What NOT to claim from our repo:** Do not claim we provide AgentDojo’s environment, task suite, defense benchmarks, or any environment-level attack/defense rates.
- **Paste-ready Related Work sentence:** AgentDojo (Debenedetti et al., 2024) evaluates prompt injection attacks and defenses for LLM agents in a dynamic environment. agent-injection-bench instead offers a fixed small seed and an undefended harness for offline scoring under a shared episode/trace schema, without implementing that environment or any defense.
