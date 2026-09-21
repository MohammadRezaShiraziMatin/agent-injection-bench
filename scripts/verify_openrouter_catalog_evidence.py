#!/usr/bin/env python3
"""Re-fetch OpenRouter catalog and verify locked entry fingerprints (no API key)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = ROOT / "artifacts" / "openrouter_model_lock_evidence.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.fetch_openrouter_catalog_evidence import build_evidence  # noqa: E402


def main() -> int:
    if not EVIDENCE_PATH.is_file():
        print(json.dumps({"ok": False, "error": "evidence_missing"}, indent=2))
        return 1
    stored = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    ids = list(stored.get("models", {}).keys())
    if len(ids) < 2:
        print(json.dumps({"ok": False, "error": "insufficient_models"}, indent=2))
        return 1
    live = build_evidence(ids)
    mismatches: list[str] = []
    for mid in ids:
        old_h = stored["models"][mid]["catalog_entry_sha256"]
        new_h = live["models"][mid]["catalog_entry_sha256"]
        if old_h != new_h:
            mismatches.append(f"{mid}: stored={old_h} live={new_h}")
    ok = not mismatches
    print(
        json.dumps(
            {
                "ok": ok,
                "models_checked": ids,
                "mismatches": mismatches,
                "live_catalog_fetched_at": live["catalog_fetched_at"],
            },
            indent=2,
        )
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
