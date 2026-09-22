#!/usr/bin/env python3
"""Emit CSV summary from P4.2.1 adjudication artifact."""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
art = ROOT / "artifacts" / "p4_2_1_near_duplicate_adjudication.json"
out = ROOT / "artifacts" / "p4_2_1_near_duplicate_summary.csv"

def main() -> int:
    data = json.loads(art.read_text(encoding="utf-8"))
    fields = [
        "episode_a",
        "episode_b",
        "family_a",
        "family_b",
        "similarity_value",
        "threshold",
        "acf_exact_match",
        "taxonomy_equal",
        "fused_surface_equal_after_normalization",
        "adjudication",
        "action",
    ]
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in data["records"]:
            w.writerow(
                {
                    "episode_a": r["episode_a"],
                    "episode_b": r["episode_b"],
                    "family_a": r["family_a"],
                    "family_b": r["family_b"],
                    "similarity_value": r["similarity_value"],
                    "threshold": r["threshold"],
                    "acf_exact_match": r["acf_status"]["exact_match"],
                    "taxonomy_equal": r["taxonomy_comparison"]["equal"],
                    "fused_surface_equal_after_normalization": r["mechanism_comparison"][
                        "fused_surface_equal_after_normalization"
                    ],
                    "adjudication": r["adjudication"],
                    "action": r["action"],
                }
            )
    print(out)
    return 0

if __name__ == "__main__":
    sys.exit(main())
