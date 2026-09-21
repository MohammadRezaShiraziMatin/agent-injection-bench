"""Optional external AdaptiGuard package bridge (not vendored in AIB)."""

from __future__ import annotations

import importlib.util
import os
import time
from pathlib import Path
from typing import Any

from agent.defense.types import DefenseAction, DefenseApplyResult, DefenseEvent

_ADAPTIGUARD_MODULE_NAMES = ("adaptiguard", "adapti_guard", "adapti_guard.middleware")


def _module_available(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ModuleNotFoundError, ValueError, ImportError):
        return False


def _find_adaptiguard_module() -> str | None:
    for name in _ADAPTIGUARD_MODULE_NAMES:
        if _module_available(name):
            return name
    extra = os.environ.get("AIB_ADAPTIGUARD_MODULE")
    if extra and _module_available(extra):
        return extra
    return None


def integration_status() -> dict[str, Any]:
    mod = _find_adaptiguard_module()
    repo_path = os.environ.get("AIB_ADAPTIGUARD_REPO")
    if mod:
        return {
            "status": "INTEGRATED",
            "integrated": True,
            "module": mod,
            "repo_path": repo_path or None,
            "version": None,
            "commit": os.environ.get("AIB_ADAPTIGUARD_COMMIT"),
        }
    return {
        "status": "NOT_INTEGRATED",
        "integrated": False,
        "module": None,
        "repo_path": repo_path if repo_path and Path(repo_path).is_dir() else None,
        "reason": "No AdaptiGuard Python module on PYTHONPATH (see docs/ADAPTI_GUARD_BRIDGE.md)",
        "bridge_doc": "docs/ADAPTI_GUARD_BRIDGE.md",
    }


def apply_adaptiguard(
    *,
    episode: dict[str, Any],
    messages: list[dict[str, Any]],
    dry_run: bool,
    t0: float,
) -> DefenseApplyResult:
    """Invoke external AdaptiGuard when installed; otherwise unreachable (middleware guards)."""
    mod_name = _find_adaptiguard_module()
    if not mod_name:
        raise RuntimeError("apply_adaptiguard called without integration")

    mod = importlib.import_module(mod_name)
    if not hasattr(mod, "guard_messages"):
        ms = int((time.perf_counter() - t0) * 1000)
        event = DefenseEvent(
            defense_enabled=True,
            defense_backend="adaptiguard",
            detector_invoked=False,
            detector_result=None,
            risk_score=None,
            risk_level=None,
            decision=DefenseAction.ERROR.value,
            block=False,
            transform_applied=False,
            reason="module_missing_guard_messages_entrypoint",
            category="integration",
            latency_ms=ms,
            defense_error=True,
            integration_status="INTEGRATED_INCOMPLETE",
        )
        return DefenseApplyResult(messages=messages, event=event, skip_target_model=True)

    out = mod.guard_messages(episode=episode, messages=messages, dry_run=dry_run)
    ms = int((time.perf_counter() - t0) * 1000)
    decision = str(out.get("decision", DefenseAction.ALLOW.value))
    block = decision == DefenseAction.BLOCK.value
    transform = decision == DefenseAction.TRANSFORM.value
    event = DefenseEvent(
        defense_enabled=True,
        defense_backend="adaptiguard",
        detector_invoked=bool(out.get("detector_invoked", True)),
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
        extra={k: v for k, v in out.items() if k not in {"messages", "decision"}},
    )
    new_messages = out.get("messages", messages)
    skip = block or bool(out.get("skip_target_model"))
    synthetic = out.get("synthetic_final_answer")
    if block and not synthetic:
        synthetic = "[defense-blocked]"
    return DefenseApplyResult(
        messages=new_messages,
        event=event,
        skip_target_model=skip,
        synthetic_final_answer=synthetic,
    )
