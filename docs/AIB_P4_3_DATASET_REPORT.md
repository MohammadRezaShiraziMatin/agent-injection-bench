# AIB P4.3 — Dataset Report (external gap closure)

```text
P4.3 EXTERNAL BENCHMARK GAP ANALYSIS

Baseline HEAD:
3e37818cbd4b75b185217b7b75f14c27a628a9f1

Final HEAD:
c8f24c2e4524d6cbb068087a5d7b03908c7518ab

P4.2 digest:
4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee

P4.2 mutated: NO

External sources audited: 8 PRIMARY (+ 5 UNVERIFIED listed)
Licenses verified: high-level (BIPIA component SA; no imports performed)

AIB coverage (P4.2): 10 families; 100% S2 attacks; 0 S1 before P4.3 add-on

Confirmed gaps addressed in candidate:
G5-001: S1 / user_response attacks (4 pairs)

Confirmed gaps deferred:
G9-001, G6-001, G6-002, G8-001, G4-001

P4.3 created: YES

New attacks: 4
New benign: 4
New pairs: 4
New families: 0 (existing families reused)
New surfaces: 0 (same harness surfaces)
New objectives: instruction_deviation (attack primary)
New horizons: 0 (h0/h1 only)

External-derived: 0 (conceptual inspiration only)
Synthetic: 8
Adapted: 0
Real-world: 0

Exact duplicates vs P4.2: 0 (ACF)
Near duplicates: not auto-screened (n=8); human review required
Leakage vs P4.2: 0 (ACF cross-check)

Human review:
Accepted: 0
Revise: 0
Reject: 0
Uncertain: 8 (queue)

Reproducibility: PASS (byte-identical)
Digest (P4.3): 3dcd436bb098b6bab601450659227fc686d9457b5052c3bb59d57766ae55be47

Tests: pytest (includes test_p4_3_candidate.py)

P4.2 integrity: PASS (verify_p4_2_freeze.py)
Dataset mutation (P4.2): NO
Live LLM: NO
API key exposed: NO
Push / PR / Release: NO

Freeze readiness: NOT READY

Final status:
P4.3 ADDITIVE CANDIDATE — G5-001 ONLY — HR PENDING

Next required action:
Complete human adjudication; define S1 scoring in evaluation protocol before live use
```
