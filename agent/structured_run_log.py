"""Append-only JSONL audit trail for benchmark runs (no secrets in records)."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STAGE_INIT = "INIT"
STAGE_PREFLIGHT = "PREFLIGHT"
STAGE_DATA_VALIDATION = "DATA_VALIDATION"
STAGE_MODEL_VALIDATION = "MODEL_VALIDATION"
STAGE_RUN_START = "RUN_START"
STAGE_EPISODE_EXECUTION = "EPISODE_EXECUTION"
STAGE_SCORING = "SCORING"
STAGE_AGGREGATION = "AGGREGATION"
STAGE_VALIDATION = "VALIDATION"
STAGE_GATE = "GATE"
STAGE_FINAL_STATUS = "FINAL_STATUS"

LIFECYCLE_STAGES = (
    STAGE_INIT,
    STAGE_PREFLIGHT,
    STAGE_DATA_VALIDATION,
    STAGE_MODEL_VALIDATION,
    STAGE_RUN_START,
    STAGE_EPISODE_EXECUTION,
    STAGE_SCORING,
    STAGE_AGGREGATION,
    STAGE_VALIDATION,
    STAGE_GATE,
    STAGE_FINAL_STATUS,
)

_SENSITIVE_KEY_RE = re.compile(
    r"(api[_-]?key|authorization|bearer|token|secret|password|credential)",
    re.IGNORECASE,
)
_BEARER_RE = re.compile(r"Bearer\s+[A-Za-z0-9._\-]+", re.IGNORECASE)
_SK_REDACTED = "[REDACTED]"


def sanitize_for_log(value: Any) -> Any:
    """Recursively redact likely secrets; keep structure for audit."""
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for k, v in value.items():
            if _SENSITIVE_KEY_RE.search(str(k)):
                out[k] = _SK_REDACTED if v not in (None, "", False) else v
            else:
                out[k] = sanitize_for_log(v)
        return out
    if isinstance(value, list):
        return [sanitize_for_log(v) for v in value]
    if isinstance(value, str):
        if _BEARER_RE.search(value):
            return _BEARER_RE.sub(f"Bearer {_SK_REDACTED}", value)
        if value.startswith("sk-") and len(value) > 12:
            return _SK_REDACTED
    return value


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class StructuredRunLogger:
    """One JSON object per line under ``AUDIT_TRAIL.jsonl`` in the run directory."""

    def __init__(self, run_id: str, log_path: Path) -> None:
        self.run_id = run_id
        self.log_path = log_path
        self._opened = False
        self._run_started_at = _utc_now()

    @classmethod
    def open_append(cls, log_path: Path) -> StructuredRunLogger:
        run_id = log_path.parent.name
        return cls(run_id, log_path)

    def _ensure_parent(self) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._opened = True

    def emit(
        self,
        stage: str,
        *,
        status: str,
        duration_ms: int | None = None,
        exit_status: int | None = None,
        error_taxonomy: str | None = None,
        **fields: Any,
    ) -> None:
        if stage not in LIFECYCLE_STAGES:
            raise ValueError(f"unknown lifecycle stage: {stage}")
        self._ensure_parent()
        record: dict[str, Any] = {
            "schema": "aib-structured-run-log-v1",
            "run_id": self.run_id,
            "timestamp": _utc_now(),
            "stage": stage,
            "status": status,
        }
        if duration_ms is not None:
            record["duration_ms"] = duration_ms
        if exit_status is not None:
            record["exit_status"] = exit_status
        if error_taxonomy is not None:
            record["error_taxonomy"] = error_taxonomy
        if fields:
            record["details"] = sanitize_for_log(fields)
        line = json.dumps(record, ensure_ascii=False, sort_keys=True, default=str) + "\n"
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(line)
            fh.flush()

    def finalize(
        self,
        *,
        ok: bool,
        paired_run: str,
        duration_ms: int,
        exit_status: int,
        **fields: Any,
    ) -> None:
        self.emit(
            STAGE_FINAL_STATUS,
            status="OK" if ok else "FAIL",
            duration_ms=duration_ms,
            exit_status=exit_status,
            paired_run=paired_run,
            run_started_at=self._run_started_at,
            **fields,
        )
