"""Auditable trace writer for episode runs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TRACES_DIR = ROOT / "results" / "traces"


def ensure_traces_dir() -> Path:
    TRACES_DIR.mkdir(parents=True, exist_ok=True)
    return TRACES_DIR


def build_trace(
    *,
    episode: dict[str, Any],
    model: str,
    provider: str,
    user_task: str,
    tool_calls: list[dict[str, Any]],
    final_answer: str | None,
    status: str,
    error: str | None = None,
    harness_execution: dict[str, Any] | None = None,
    initial_messages: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "episode_id": episode.get("id"),
        "episode_type": episode.get("split"),
        "model": model,
        "provider": provider,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_task": user_task,
        "retrieved_docs": [
            {"doc_id": d.get("doc_id"), "text_len": len(d.get("text", ""))}
            for d in episode.get("retrieved_docs", [])
        ],
        "harness_execution": harness_execution,
        "initial_messages_digest": [
            {"role": m.get("role"), "content_len": len(str(m.get("content", "")))}
            for m in (initial_messages or [])
        ],
        "tool_calls": tool_calls,
        "final_answer": final_answer,
        "status": status,
        "error": error,
    }


def write_trace(trace: dict[str, Any], *, write: bool = True) -> Path | None:
    if not write:
        return None
    ensure_traces_dir()
    episode_id = trace.get("episode_id") or "unknown"
    path = TRACES_DIR / f"{episode_id}.json"
    path.write_text(json.dumps(trace, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
