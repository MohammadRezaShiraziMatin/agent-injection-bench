# Future experiment protocol draft (NOT AUTHORIZED — NOT EXECUTED)

Pre-specification only for gaps that **cannot** be closed by documentation (e.g. G1-N9 powered inference).  
Does not modify frozen P4.2 primary run or P5 decisions.

---

## Scope trigger

Authorize only if reviewers require population-level or confirmatory claims beyond the frozen descriptive P4.2 primary (9 attack pairs, COV-A).

---

## Protocol skeleton

| Field | Draft value (to be frozen before run) |
|-------|--------------------------------------|
| RQ | Does D2 vs D0 change ASR on an expanded COV-A (or pre-registered) pool? |
| Hypothesis | Confirmatory testing **deferred** until this protocol is approved |
| Population | Pre-register coverage class and episode IDs (manifest hash) |
| Sampling | Paired attack/benign; no post-hoc pool expansion |
| N | TBD by power analysis **before** execution |
| Primary endpoint | ASR (attack), same scorer contract |
| Secondary | S2, S3, S4, Utility, FPR, paired transitions |
| Comparison | D0 vs D2 |
| Target model | Per `config/p4_3_live_eval_gate.v1.json` unless new lock |
| Judge model | Per gate unless new lock |
| Seed | Record; policy per provider |
| Statistics | Pre-register (e.g. exact paired test if binary endpoint) |
| Acceptance criteria | Pre-register; separate from descriptive P4.2 |
| Stopping rule | Fixed N; no optional stopping on interim ASR |

---

## Exclusions

- No rerun of frozen `p42-primary-d0-d2-20260921T173736Z-controlled` for “better” outcomes.
- No synthetic episodes without dataset contract amendment.
- No live execution without explicit approval artifacts and gate flags per existing scripts.

---

## Human judge (optional extension)

If G1-JUDGE is to be addressed: separate protocol for annotators, IAA, and adjudication **before** labeling.
