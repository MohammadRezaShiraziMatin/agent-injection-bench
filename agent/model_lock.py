"""P4.3 live-eval gate + OpenRouter lock helpers (offline)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GATE_PATH = ROOT / "config" / "p4_3_live_eval_gate.v1.json"


@lru_cache(maxsize=1)
def load_live_eval_gate() -> dict[str, Any]:
    return json.loads(GATE_PATH.read_text(encoding="utf-8"))


def role_block(role: str) -> dict[str, Any]:
    gate = load_live_eval_gate()
    if role == "target":
        return gate.get("target_model") or {}
    if role == "judge":
        return gate.get("judge_model") or {}
    raise ValueError(f"unknown role: {role}")


def openrouter_provider_extra(role: str) -> dict[str, Any]:
    """OpenRouter `provider` routing object for chat.completions extra_body."""
    pol = role_block(role).get("routing_policy") or {}
    order = pol.get("provider_order") or []
    return {
        "provider": {
            "order": list(order),
            "allow_fallbacks": bool(pol.get("allow_fallbacks", True)),
        }
    }
