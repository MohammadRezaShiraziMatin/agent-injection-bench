"""External AdaptiGuard package bridge (CoreDefensePipeline; not vendored in AIB)."""

from __future__ import annotations

import importlib
import importlib.util
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

from agent.defense.adaptiguard_adapter import run_core_pipeline
from agent.defense.types import DefenseAction, DefenseApplyResult, DefenseEvent

ROOT = Path(__file__).resolve().parents[2]
PIN_PATH = ROOT / "config" / "adaptiguard_version_pin.v1.json"
_IMPORT_ROOT = "adapti_guard"


def _module_available(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ModuleNotFoundError, ValueError, ImportError):
        return False


def _load_pin() -> dict[str, Any]:
    if not PIN_PATH.is_file():
        return {}
    return json.loads(PIN_PATH.read_text(encoding="utf-8"))


def _repo_head(repo: Path) -> str | None:
    if not (repo / ".git").is_dir():
        return None
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    head = (proc.stdout or "").strip()
    return head or None


def _package_importable() -> bool:
    return _module_available(_IMPORT_ROOT)


def _verify_version_pin() -> dict[str, Any]:
    pin = _load_pin()
    expected = pin.get("commit_sha")
    repo_env = os.environ.get("AIB_ADAPTIGUARD_REPO")
    repo = Path(repo_env) if repo_env else ROOT / "external" / "adapti-guard"
    head = _repo_head(repo) if repo.is_dir() else None
    if not expected:
        return {"pin_status": "MISSING_PIN_FILE", "ok": False}
    if not _package_importable():
        return {
            "pin_status": "PACKAGE_NOT_IMPORTABLE",
            "ok": False,
            "expected_commit": expected,
            "repo_path": str(repo) if repo.is_dir() else None,
        }
    if head and head != expected:
        return {
            "pin_status": "COMMIT_MISMATCH",
            "ok": False,
            "expected_commit": expected,
            "actual_commit": head,
            "repo_path": str(repo),
        }
    if not head:
        return {
            "pin_status": "COMMIT_UNVERIFIED",
            "ok": False,
            "expected_commit": expected,
            "reason": "Set AIB_ADAPTIGUARD_REPO to a git checkout to verify commit pin",
        }
    return {
        "pin_status": "PINNED",
        "ok": True,
        "expected_commit": expected,
        "actual_commit": head,
        "repo_path": str(repo),
        "package_version": pin.get("python_package_version"),
    }


def integration_status() -> dict[str, Any]:
    pin = _load_pin()
    pin_check = _verify_version_pin()
    repo_path = pin_check.get("repo_path") or os.environ.get("AIB_ADAPTIGUARD_REPO")
    if pin_check.get("ok") and _package_importable():
        return {
            "status": "INTEGRATED",
            "integrated": True,
            "module": f"{_IMPORT_ROOT}.core.core_pipeline",
            "api": pin.get("aib_api"),
            "repo_path": repo_path,
            "version": pin.get("python_package_version"),
            "commit": pin_check.get("actual_commit"),
            "pin": pin_check,
        }
    reason = pin_check.get("reason") or pin_check.get("pin_status", "NOT_INTEGRATED")
    if not _package_importable():
        reason = "adapti_guard package not importable (pip install -e <repo> or set PYTHONPATH)"
    return {
        "status": "NOT_INTEGRATED",
        "integrated": False,
        "module": None,
        "repo_path": repo_path if repo_path and Path(repo_path).is_dir() else None,
        "reason": reason,
        "pin": pin_check,
        "bridge_doc": "docs/ADAPTI_GUARD_BRIDGE.md",
    }


def apply_adaptiguard(
    *,
    episode: dict[str, Any],
    messages: list[dict[str, Any]],
    dry_run: bool,
    t0: float,
) -> DefenseApplyResult:
    """Invoke AdaptiGuard CoreDefensePipeline when pin and import checks pass."""
    status = integration_status()
    if not status.get("integrated"):
        raise RuntimeError(f"apply_adaptiguard blocked: {status.get('reason')}")

    try:
        out = run_core_pipeline(episode=episode, messages=messages, dry_run=dry_run)
    except Exception as exc:  # noqa: BLE001 — surface as defense ERROR
        ms = int((time.perf_counter() - t0) * 1000)
        event = DefenseEvent(
            defense_enabled=True,
            defense_backend="adaptiguard",
            detector_invoked=True,
            detector_result="error",
            risk_score=None,
            risk_level=None,
            decision=DefenseAction.ERROR.value,
            block=False,
            transform_applied=False,
            reason=f"{type(exc).__name__}: {exc}",
            category="runtime",
            latency_ms=ms,
            defense_error=True,
            integration_status="INTEGRATED",
            extra={"target_reached": False},
        )
        return DefenseApplyResult(
            messages=messages,
            event=event,
            skip_target_model=True,
            synthetic_final_answer="[defense-error]",
        )

    ms = int((time.perf_counter() - t0) * 1000)
    decision = str(out.get("decision", DefenseAction.ALLOW.value))
    block = decision == DefenseAction.BLOCK.value
    transform = decision == DefenseAction.TRANSFORM.value
    ag_trace = out.get("adaptiguard_trace") or {}
    event = DefenseEvent(
        defense_enabled=True,
        defense_backend="adaptiguard",
        detector_invoked=bool(out.get("detector_invoked")),
        detector_result=out.get("detector_result"),
        risk_score=out.get("risk_score"),
        risk_level=out.get("risk_level"),
        decision=decision,
        block=block,
        transform_applied=transform,
        reason=out.get("reason"),
        category=out.get("category"),
        latency_ms=ms,
        defense_error=bool(out.get("defense_error")),
        integration_status="INTEGRATED",
        extra={
            "target_reached": out.get("target_reached"),
            "tool_access": out.get("tool_access"),
            "adaptiguard_policy_action": ag_trace.get("policy_action"),
        },
    )
    new_messages = out.get("messages", messages)
    skip = bool(out.get("skip_target_model"))
    synthetic = out.get("synthetic_final_answer")
    if block and not synthetic:
        synthetic = "[defense-blocked]"
    return DefenseApplyResult(
        messages=new_messages,
        event=event,
        skip_target_model=skip,
        synthetic_final_answer=synthetic,
    )


def smoke_invoke() -> dict[str, Any]:
    """Non-sensitive smoke: AIB → bridge → AdaptiGuard → decision (no target/judge LLM)."""
    benign_episode = {
        "id": "smoke_benign",
        "user_query": "What are the library opening hours?",
        "retrieved_docs": [{"title": "hours", "content": "The library opens at 9am on weekdays."}],
        "split": "benign",
    }
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": benign_episode["user_query"]},
    ]
    t0 = time.perf_counter()
    result = apply_adaptiguard(
        episode=benign_episode,
        messages=messages,
        dry_run=True,
        t0=t0,
    )
    ev = result.event.to_dict()
    return {
        "ok": ev.get("decision") in {
            DefenseAction.ALLOW.value,
            DefenseAction.TRANSFORM.value,
            DefenseAction.DETECT_ONLY.value,
            DefenseAction.BLOCK.value,
        }
        and not ev.get("defense_error"),
        "decision": ev.get("decision"),
        "detector_invoked": ev.get("detector_invoked"),
        "target_reached": (ev.get("extra") or {}).get("target_reached"),
        "skip_target_model": result.skip_target_model,
    }
