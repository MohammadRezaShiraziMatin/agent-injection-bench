"""Auditable execution traces. Observed facts only — no eval labels."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts._common import RESULTS_TRACES_DIR, dump_json

TRACE_KEY_ORDER = (
    "episode_id",
    "episode_type",
    "split",
    "model",
    "provider",
    "base_url",
    "timestamp",
    "user_task",
    "retrieved_documents",
    "tool_calls",
    "final_answer",
    "execution_status",
    "error",
    "steps",
    "max_steps",
    "dry_run",
)


def utc_timestamp(now: datetime | None = None) -> str:
    moment = now or datetime.now(timezone.utc)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def document_refs(episode: dict[str, Any]) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for doc in episode.get("retrieved_docs") or []:
        if not isinstance(doc, dict):
            continue
        refs.append(
            {
                "doc_id": str(doc.get("doc_id", "")),
                "text": str(doc.get("text", "")),
            }
        )
    return refs


def empty_trace(
    episode: dict[str, Any],
    *,
    model: str,
    provider: str,
    base_url: str,
    max_steps: int,
    timestamp: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    split = str(episode.get("split") or "")
    return {
        "episode_id": episode.get("id"),
        "episode_type": split,
        "split": split,
        "model": model,
        "provider": provider,
        "base_url": base_url,
        "timestamp": timestamp or utc_timestamp(),
        "user_task": episode.get("user_query"),
        "retrieved_documents": document_refs(episode),
        "tool_calls": [],
        "final_answer": "",
        "execution_status": "ok",
        "error": None,
        "steps": 0,
        "max_steps": max_steps,
        "dry_run": dry_run,
    }


def order_trace(trace: dict[str, Any]) -> dict[str, Any]:
    ordered: dict[str, Any] = {key: trace.get(key) for key in TRACE_KEY_ORDER}
    for key, value in trace.items():
        if key not in ordered and not str(key).startswith("_"):
            ordered[key] = value
    return ordered


def write_trace(trace: dict[str, Any], path: Path) -> Path:
    payload = order_trace(trace)
    dump_json(path, payload)
    return path


def default_trace_path(episode_id: str, out_dir: Path | None = None) -> Path:
    directory = out_dir or RESULTS_TRACES_DIR
    return directory / f"{episode_id}.json"
