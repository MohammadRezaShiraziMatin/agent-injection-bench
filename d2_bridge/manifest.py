"""D2 batch manifest helpers (extends AIB manifest with bridge provenance)."""

from __future__ import annotations

import hashlib
from collections import Counter
from pathlib import Path
from typing import Any

from agent.traces import (
    MANIFESTS_DIR,
    TraceExistsError,
    dataset_fingerprint,
    dataset_version,
    git_head,
    safe_run_id,
    utc_timestamp,
)
from d2_bridge.ag_lock import verify_detector_lock
from d2_bridge.config import D2DefenseConfig, TRACE_SCHEMA_VERSION
from scripts._common import dump_json


def _prompt_sha256(prompt_path: Path) -> str | None:
    if not prompt_path.is_file():
        return None
    return hashlib.sha256(prompt_path.read_bytes()).hexdigest()


def write_d2_manifest(
    run_id: str,
    *,
    episode_ids: list[str],
    model: str,
    temperature: float | None,
    seed: int | None,
    provider: str | None,
    base_url: str | None,
    statuses: list[str],
    traces_dir: str,
    defense_config: D2DefenseConfig,
    prompt_path: Path,
    timestamp: str | None = None,
    out_dir: Path | None = None,
    force: bool = False,
    repeat: int | None = None,
) -> Path:
    directory = out_dir or MANIFESTS_DIR
    directory.mkdir(parents=True, exist_ok=True)
    safe = safe_run_id(run_id)
    path = directory / f"{safe}.json"
    if path.exists() and not force:
        raise TraceExistsError(
            f"manifest already exists: {path} (pass force=True / --force to overwrite)"
        )

    lock = verify_detector_lock(adaptiguard_commit=defense_config.adaptiguard_commit)
    status_list = list(statuses or [])
    bridge = {
        "bridge_name": "aib-adaptiguard-d2",
        "bridge_version": defense_config.manifest_fragment(),
        "adaptiguard_commit": defense_config.adaptiguard_commit,
        "adaptiguard_baseline": defense_config.baseline_key,
        "defense_level": defense_config.defense_level,
        "defense_level_provisional": defense_config.defense_level_provisional,
        "detector_lock_id": defense_config.detector_lock_id,
        "detector_lock_sha256": {k: v["sha256"] for k, v in lock.components.items()},
        "base_prompt_id": defense_config.base_prompt_id,
        "base_prompt_sha256": _prompt_sha256(prompt_path),
        "tool_deny_message_mode": defense_config.deny_message_mode,
        "action_cost_source": "not_emitted_by_core_pipeline",
        "aib_git_head": git_head(),
        "scorer_pin": git_head(),
        "cache_policy": "operator_defined_per_run",
    }
    payload: dict[str, Any] = {
        "run_id": run_id,
        "model": model,
        "provider": provider,
        "base_url": base_url,
        "temperature": temperature,
        "seed": seed,
        "prompt_id": "d2",
        "defense_condition": "d2",
        "trace_schema_version": TRACE_SCHEMA_VERSION,
        "repeat": repeat,
        "dataset_fingerprint": dataset_fingerprint(episode_ids),
        "dataset_version": dataset_version(),
        "timestamp": timestamp or utc_timestamp(),
        "episode_ids": episode_ids,
        "status_counts": dict(Counter(status_list)),
        "statuses": status_list,
        "traces_dir": traces_dir,
        "git_head": git_head(),
        "bridge": bridge,
        "note": (
            "D2 manifest with AdaptiGuard bridge provenance. Not ASR/utility. "
            "defense_level may be provisional — see bridge.defense_level_provisional."
        ),
    }
    dump_json(path, payload)
    return path
