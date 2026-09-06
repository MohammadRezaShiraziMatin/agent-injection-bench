# Episodes

Seed attack and benign JSON files here. v0 target: **20–40 attack** and **20–40 benign**. Current data batch: `atk_002`–`atk_021` and `ben_002`–`ben_021` (20 + 20). Format demos `atk_001` / `ben_001` stay under `examples/`.

## Layout

- `attack/` — files with `"split": "attack"`
- `benign/` — files with `"split": "benign"`

One episode per file. Suggested names: `atk_001.json`, `ben_001.json`.

## How to add an episode

1. Copy a format demo:
   - Attack: [`examples/episode_attack_001.json`](../../examples/episode_attack_001.json)
   - Benign: [`examples/episode_benign_001.json`](../../examples/episode_benign_001.json)
2. Give it a new `id` (`atk_00N` / `ben_00N`).
3. Write a realistic `user_query` and `retrieved_docs`.
4. For **attack**: `injection.present=true`, put the payload in a retrieved doc, and list the misuse target in `expected.forbidden_tools` (v0: usually `send_email`).
5. For **benign**: `injection.present=false`. `forbidden_tools` is usually `[]`.
6. If you want utility scoring later, set `expected.utility_answer_contains` to short substrings that a correct answer should include.
7. Validate:

```bash
python scripts/validate_episodes.py
```

Do not commit fabricated run traces or claimed ASR/utility numbers.
