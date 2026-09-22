# AIB P4.4 v2 Freeze

**Freeze ID:** `aib-p4.4-validation-v2.0`  
**Parent freeze:** `aib-p4.4-validation-v1.0`

| Field | Value |
|-------|-------|
| Path | `data/episodes_p4_4_v2/` |
| Schema | `schema/episode.p44.v1.json` |
| Episode `dataset_version` | `P4.4` (schema const) |
| Corpus `dataset_version` | `P4.4-v2` |
| Parent version | `P4.4` |
| Parent digest | `d5132fb3a4897684e1cb8a6f38f7cd367ee2a928bcd351743f73f13c326d796f` |
| Digest | `8dcf0664729ed4b8f7e0e445180979c2929efc305e9c08787886e738b43ee531` |
| Revision source | `artifacts/p4_4_hr_audit_trail.json` |
| Revision count | 96 attack rows |
| Revision scope | REVISE attacks only |
| Seed | `44020260922` |

v1 under `data/episodes_p4_4/` is not overwritten. The 4 ACCEPT attacks and all 100 benign episodes are byte-identical to v1. Payloads were not rewritten.

Corrections, and only these:

- S1 observable no longer calls an imperative a false claim.
- `retrieved_docs` no longer repeats the payload when `injection.locus` is another channel.
- Non-email lures are S1 instruction deviation with `forbidden_tools` empty and target `user_response`, not an S2 `send_email` proposal.
- Unsupported `taxonomy.technique` values on the defer-until-side-effect template are `workflow_hijack`, the audit rule that requires that template.

`taxonomy.objective` and `taxonomy.tool` were not audit fields and were not edited. Family counts, strata, and executability are unchanged: 44 `EXECUTABLE`, 42 `PARTIALLY_EXECUTABLE`, 14 `DESIGNED_NOT_EXECUTABLE`.
