"""Auditable execution traces. Observed facts only — no eval labels."""

from __future__ import annotations

import hashlib
import json
import subprocess
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts._common import RESULTS_TRACES_DIR, dump_json

MANIFESTS_DIR = Path(__file__).resolve().parents[1] / "results" / "manifests"

# Canonical execution_status values for v0 (see docs/BENCHMARK.md).
EXECUTION_STATUSES = frozenset({"ok", "max_steps", "error", "dry_run"})

TRACE_KEY_ORDER = (
    "run_id",
    "episode_id",
    "episode_type",
    "split",
    "episode",
    "prompt_id",
    "defense_condition",
    "model",
    "provider",
    "base_url",
    "temperature",
    "seed",
    "timestamp",
    "git_head",
    "user_task",
    "retrieved_documents",
    "tool_calls",
    "final_answer",
    "execution_status",
    "status",
    "error",
    "steps",
    "max_steps",
    "dry_run",
    "latency_ms",
    "tokens",
)


class TraceExistsError(FileExistsError):
    """Refuse to overwrite an existing trace unless force=True."""


def utc_timestamp(now: datetime | None = None) -> str:
    moment = now or datetime.now(timezone.utc)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def safe_run_id(run_id: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in run_id)


def make_run_id(*, model: str = "", episode_id: str = "") -> str:
    """Stable-enough run id: utc stamp + model + episode + short uuid."""
    stamp = utc_timestamp().replace(":", "").replace("-", "")
    model_slug = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in (model or "model"))[:40]
    ep = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in (episode_id or "ep"))[:40]
    short = uuid.uuid4().hex[:8]
    return f"{stamp}_{model_slug}_{ep}_{short}"


def git_head(repo_root: Path | None = None) -> str | None:
    root = repo_root or Path(__file__).resolve().parents[1]
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return out.strip() or None


def dataset_fingerprint(episode_ids: list[str]) -> dict[str, Any]:
    """Count + hash of sorted episode ids (+ git HEAD when available)."""
    ordered = sorted({eid for eid in episode_ids if eid})
    digest = hashlib.sha256("\n".join(ordered).encode("utf-8")).hexdigest()
    return {
        "n_episodes": len(ordered),
        "ids_sha256": digest,
        "git_head": git_head(),
    }


def dataset_version(episodes_dir: Path | None = None) -> dict[str, Any]:
    """Content hash over sorted episode JSON files (ids + file digests)."""
    root = Path(__file__).resolve().parents[1]
    directory = episodes_dir or (root / "data" / "episodes")
    files = sorted(directory.rglob("*.json")) if directory.is_dir() else []
    h = hashlib.sha256()
    ids: list[str] = []
    for path in files:
        raw = path.read_bytes()
        rel = str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(hashlib.sha256(raw).digest())
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            payload = None
        if isinstance(payload, dict) and isinstance(payload.get("id"), str):
            ids.append(payload["id"])
    return {
        "dataset_version": h.hexdigest(),
        "n_files": len(files),
        "n_ids": len(ids),
        "ids_sha256": hashlib.sha256("\n".join(sorted(set(ids))).encode("utf-8")).hexdigest(),
        "git_head": git_head(),
    }


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
    run_id: str | None = None,
    prompt_id: str = "d0",
    defense_condition: str = "d0",
    temperature: float | None = None,
    seed: int | None = None,
    git_head_value: str | None = None,
    latency_ms: float | None = None,
    tokens: dict[str, Any] | None = None,
) -> dict[str, Any]:
    split = str(episode.get("split") or "")
    episode_id = episode.get("id")
    status = "ok"
    return {
        "run_id": run_id
        or make_run_id(model=model, episode_id=str(episode_id or "unknown")),
        "episode_id": episode_id,
        "episode_type": split,
        "split": split,
        "episode": episode_id,
        "prompt_id": prompt_id,
        "defense_condition": defense_condition,
        "model": model,
        "provider": provider,
        "base_url": base_url,
        "temperature": temperature,
        "seed": seed,
        "timestamp": timestamp or utc_timestamp(),
        # Actual HEAD when available; never invent a commit.
        "git_head": git_head_value if git_head_value is not None else git_head(),
        "user_task": episode.get("user_query"),
        "retrieved_documents": document_refs(episode),
        "tool_calls": [],
        "final_answer": "",
        "execution_status": status,
        # Alias for consumers that expect `status` (mirrors execution_status).
        "status": status,
        "error": None,
        "steps": 0,
        "max_steps": max_steps,
        "dry_run": dry_run,
        # Measured wall time when observable; otherwise null (never estimate).
        "latency_ms": latency_ms,
        # Provider usage when observable; otherwise null (never estimate).
        "tokens": tokens,
    }


def order_trace(trace: dict[str, Any]) -> dict[str, Any]:
    ordered: dict[str, Any] = {key: trace.get(key) for key in TRACE_KEY_ORDER}
    for key, value in trace.items():
        if key not in ordered and not str(key).startswith("_"):
            ordered[key] = value
    return ordered


def write_trace(trace: dict[str, Any], path: Path, *, force: bool = False) -> Path:
    if path.exists() and not force:
        raise TraceExistsError(
            f"trace already exists: {path} (pass force=True / --force to overwrite)"
        )
    payload = order_trace(trace)
    dump_json(path, payload)
    return path


def default_trace_path(
    episode_id: str,
    out_dir: Path | None = None,
    *,
    run_id: str | None = None,
) -> Path:
    """Default: results/traces/<run_id>/<episode_id>.json when run_id is set."""
    directory = out_dir or RESULTS_TRACES_DIR
    if run_id:
        directory = directory / safe_run_id(run_id)
    return directory / f"{episode_id}.json"


def write_manifest(
    run_id: str,
    *,
    episode_ids: list[str],
    model: str,
    temperature: float | None,
    seed: int | None,
    prompt_id: str = "d0",
    defense_condition: str = "d0",
    provider: str | None = None,
    base_url: str | None = None,
    statuses: list[str] | None = None,
    traces_dir: str | None = None,
    timestamp: str | None = None,
    note: str | None = None,
    out_dir: Path | None = None,
    force: bool = False,
    repeat: int | None = None,
) -> Path:
    """Write results/manifests/<run_id>.json — run metadata only, not ASR."""
    directory = out_dir or MANIFESTS_DIR
    directory.mkdir(parents=True, exist_ok=True)
    safe = safe_run_id(run_id)
    path = directory / f"{safe}.json"
    if path.exists() and not force:
        raise TraceExistsError(
            f"manifest already exists: {path} (pass force=True / --force to overwrite)"
        )
    status_list = list(statuses or [])
    payload = {
        "run_id": run_id,
        "model": model,
        "provider": provider,
        "base_url": base_url,
        "temperature": temperature,
        "seed": seed,
        "prompt_id": prompt_id,
        "defense_condition": defense_condition,
        "repeat": repeat,
        "dataset_fingerprint": dataset_fingerprint(episode_ids),
        "dataset_version": dataset_version(),
        "timestamp": timestamp or utc_timestamp(),
        "episode_ids": episode_ids,
        "status_counts": dict(Counter(status_list)),
        "statuses": status_list,
        "traces_dir": traces_dir,
        "git_head": git_head(),
        "note": note
        or (
            "Manifest only. Not ASR/utility. D0 = undefended baseline. "
            "Do not treat execution_status=error as attack success."
        ),
    }
    dump_json(path, payload)
    return path
