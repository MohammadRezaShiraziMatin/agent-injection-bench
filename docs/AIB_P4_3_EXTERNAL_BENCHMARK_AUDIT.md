# AIB P4.3 — External Benchmark Audit

**Audit date:** 2026-09-21 (UTC)  
**Branch:** `cursor/p4-2-dataset-6db2`  
**AIB baseline:** Frozen **P4.2** (`4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee`)  
**Method:** Primary sources only (papers, official repos). **No external payloads imported.**

## Source validation legend

| Label | Meaning |
|-------|---------|
| PRIMARY_SOURCE | Paper and/or official repository consulted |
| SECONDARY_SOURCE | Cited only via another paper (not used alone) |
| UNVERIFIED | Not inspected in this pass |

## Corpus summary

| Name | Year / venue | Repository | Task focus | Size (reported) | License (repo) | Validation |
|------|----------------|------------|------------|-----------------|----------------|------------|
| **AgentDojo** | NeurIPS 2024 D&B | https://github.com/ethz-spylab/agentdojo | Dynamic agent env, tool use over untrusted data | 97 tasks, 629 security tests | Open-source (see repo) | PRIMARY |
| **InjecAgent** | ACL 2024 Findings | https://github.com/uiuc-kang-lab/InjecAgent | Tool-integrated IPI | 1,054 test cases; 17 user + 62 attacker tools | Open-source (see repo) | PRIMARY |
| **BIPIA** | Yi et al. 2023 / Microsoft | https://github.com/microsoft/BIPIA | Indirect PI across tasks (email, WebQA, code, etc.) | Multi-task builder | MIT (code); **component CC BY-SA / MIT** | PRIMARY |
| **Tensor Trust** | arXiv:2311.01011 | https://github.com/HumanCompatibleAI/tensor-trust-data | Hijack / extraction from online game | 126k+ attacks; benchmarks 775 hijack / 569 extraction | See dataset README | PRIMARY |
| **HouYi** | arXiv:2306.05499 | https://github.com/llmsecurity/houyi | Automated PI **framework** (not static JSON corpus) | 36 apps evaluated | Replication package | PRIMARY |
| **PIArena** | ACL 2026 (long) | https://github.com/sleeepeer/PIArena | Unified PI eval platform (wraps InjecAgent, AgentDojo, etc.) | Platform-dependent | See repo | PRIMARY |
| **StruQ** | USENIX Security 2025 | https://github.com/Sizhe-Chen/StruQ | Defense + attack eval on AlpacaFarm-derived set | ~208 samples × 15+ attack types | Open-source | PRIMARY |
| **Task Shield** | — | — | — | — | — | **UNVERIFIED** (not located as standalone primary artifact in this pass) |
| **Spotlighting** | — | — | — | — | — | **UNVERIFIED** |
| **VIGIL** | — | — | — | — | — | **UNVERIFIED** |
| **IterInject** | — | — | — | — | — | **UNVERIFIED** |
| **PIGuard** | — | — | — | — | — | **UNVERIFIED** (detector; not a static episode corpus) |

**Import policy:** BIPIA / Tensor Trust / InjecAgent / AgentDojo content → **DO_NOT_IMPORT** into AIB JSON without per-component license review and explicit adaptation provenance. This pass uses them **only for mapping**.

---

## Normalized taxonomy mapping (external → AIB)

| External concept | AIB `family` / dimension | Mapping |
|------------------|--------------------------|---------|
| User-channel PI | `direct_prompt_injection` | Direct |
| Doc / RAG / email body PI | `rag_document_injection`, `indirect_prompt_injection` | Direct |
| Tool-return PI | `tool_output_injection` | Direct |
| Multi-step chat PI | `multi_turn_injection` | Direct |
| Web page PI (AgentDojo, WASP via PIArena) | `web_retrieved_content_injection` | Partial (AIB uses text snippets, not live web) |
| Inter-agent PI | `multi_agent_injection` | Direct (dataset); harness DNE |
| Adaptive / feedback PI | `adaptive_injection` | Direct (dataset); harness DNE |
| Output hijack / wrong answer (Tensor Trust, HouYi) | `instruction_deviation` + `target=user_response` + **S1** | **Was missing in P4.2 attacks** |
| Tool-harm / data steal (InjecAgent) | `unauthorized_tool_proposal` / `data_exfiltration` + **S2** | Covered (P4.2 S2-heavy) |
| Dynamic suites (workspace, banking) | `context_type` campus-* | **NOT_MAPPABLE** 1:1 (domain mismatch by design) |
| GUI / screenshot agents (MIRAGE, AgentHazard) | — | **NOT_MAPPABLE** to text-only AIB harness |

---

## Coverage matrix (presence / partial / absent)

| Capability | AIB P4.2 | AgentDojo | InjecAgent | BIPIA | Tensor Trust | HouYi | PIArena | StruQ |
|------------|----------|-----------|------------|-------|--------------|-------|---------|-------|
| Direct injection | Yes | Partial | Partial | Yes | Yes (hijack) | Yes | Yes | Yes |
| Indirect / RAG | Yes | Yes | Yes | Yes | Partial | Partial | Yes | Yes |
| Web injection | Partial | Yes | Yes | Yes | No | Partial | Yes | Partial |
| Tool output injection | Yes | Yes | Yes | Partial | No | No | Yes | Partial |
| Multi-turn | Yes | Yes | Partial | Partial | Partial | Partial | Yes | Partial |
| Memory / state | Yes | Partial | Partial | Partial | No | No | Partial | No |
| Cross-context | Yes | Partial | Partial | Partial | No | No | Partial | No |
| Multi-agent | Yes (DNE) | Partial | Partial | No | No | No | Partial | No |
| Adaptive | Yes (DNE) | Yes | No | No | No | No | Partial | No |
| Tool selection diversity | Low (2 tools) | High | Very high | Task-dependent | N/A | N/A | High | N/A |
| **S1 instruction deviation** | **No (pre-P4.3)** | Partial | Partial | Partial | **Yes (hijack)** | **Yes (output)** | Partial | Yes |
| S2 tool proposal | Yes (100%) | Yes | Yes | Partial | No | No | Yes | Partial |
| S3/S4 execution / side effect | Mock-limited | Live sim | Live tools | Task-dependent | N/A | N/A | Mixed | N/A |
| Benign / utility checks | Yes (pairs) | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Paired controls | Yes | Task-dependent | Composed cases | Builder | Game pairs | Harness | Platform | Train/test |
| Provenance | Synthetic | Env logs | Synthetic compose | Mixed | Human game | Framework | Platform | Alpaca-derived |
| Reproducibility | Byte-gen | Env+API | Scripted | Builder seed | Versioned dumps | GA search | Seeds | Fixed scripts |

---

## Quantitative AIB P4.2 (reference)

| Dimension | Note |
|-----------|------|
| Families | 10 / 10 required families present |
| Attack `success_criterion` | **100% S2** before P4.3 additive set |
| `target=user_response` (attack) | **0** before P4.3 |
| `objective=instruction_deviation` (attack) | **0** before P4.3 |
| Executability (harness p4.2.4) | 172 EXEC / 16 PARTIAL / 12 DNE |

External benchmarks emphasize **broader tool catalogs** and **dynamic environments**; AIB P4.2 emphasizes **paired taxonomy coverage** in a **fixed campus mock-tool harness**.

---

## Licenses (high level)

| Source | Use in AIB |
|--------|------------|
| AgentDojo | Conceptual comparison only unless SPDX reviewed per file |
| InjecAgent | DO_NOT_IMPORT raw JSONL without audit |
| BIPIA | DO_NOT_IMPORT; CC BY-SA components require share-alike compliance |
| Tensor Trust | DO_NOT_IMPORT raw attacks; game data has own terms |
| HouYi | Framework only; not a dataset |

---

## Confirmed cross-benchmark gap (dataset-level)

**G5-001 — Primary S1 / user_response attacks absent in P4.2**  
Evidence: Tensor Trust hijacking benchmark; HouYi output-manipulation intention; BIPIA/StruQ indirect instruction-in-data channel. AIB taxonomy supports S1; generator supported `instruction_deviation` but **P4.2 bank had zero such attack pairs**.

**Not treated as dataset gaps (evaluation / harness):**  
- AgentDojo dynamic state (G9)  
- InjecAgent 62-tool catalog (G6 tool surface)  
- Multilingual / multimodal (unverified for AIB scope)  
- GUI agents (NOT_MAPPABLE)

See `docs/AIB_P4_3_GAP_ANALYSIS.md` for full gap register and P4.3 response.
