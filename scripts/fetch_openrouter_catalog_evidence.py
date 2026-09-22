#!/usr/bin/env python3
"""Fetch public OpenRouter /models catalog entries for lock evidence (no API key)."""

from __future__ import annotations

import hashlib
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_URL = "https://openrouter.ai/api/v1/models"
OUT = ROOT / "artifacts" / "openrouter_model_lock_evidence.json"


def _sha256_obj(obj: dict) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()


def fetch_catalog() -> list[dict]:
    with urllib.request.urlopen(CATALOG_URL, timeout=60) as resp:
        payload = json.loads(resp.read().decode())
    return payload.get("data") or []


def entry_for(catalog: list[dict], model_id: str) -> dict:
    for row in catalog:
        if row.get("id") == model_id:
            return row
    raise KeyError(f"model_id not in catalog: {model_id}")


def build_evidence(model_ids: list[str]) -> dict:
    catalog = fetch_catalog()
    fetched_at = datetime.now(timezone.utc).isoformat()
    catalog_blob_sha = hashlib.sha256(
        json.dumps(catalog, sort_keys=True).encode()
    ).hexdigest()
    models: dict[str, dict] = {}
    for mid in model_ids:
        row = entry_for(catalog, mid)
        models[mid] = {
            "exact_model_id": mid,
            "canonical_slug": row.get("canonical_slug"),
            "catalog_entry_sha256": _sha256_obj(row),
            "context_length": row.get("context_length"),
            "created_unix": row.get("created"),
            "hugging_face_id": row.get("hugging_face_id"),
            "supported_parameters": row.get("supported_parameters"),
            "tool_calling_supported": "tools" in (row.get("supported_parameters") or []),
            "weight_revision_provable": False,
            "snapshot_limitation": (
                "OpenRouter catalog row fingerprint only; upstream provider weight revision "
                "is not independently attested by this repository."
            ),
        }
    return {
        "catalog_url": CATALOG_URL,
        "catalog_fetched_at": fetched_at,
        "catalog_full_sha256": catalog_blob_sha,
        "models": models,
    }


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: fetch_openrouter_catalog_evidence.py <target_id> <judge_id>", file=sys.stderr)
        return 2
    target_id, judge_id = sys.argv[1], sys.argv[2]
    if target_id == judge_id:
        print("target and judge must differ", file=sys.stderr)
        return 2
    evidence = build_evidence([target_id, judge_id])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "out": str(OUT), "models": list(evidence["models"].keys())}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
