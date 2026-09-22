"""Offline mock email sender — sandbox execution with explicit side-effect metadata."""

from __future__ import annotations

from typing import Any

from tools.execution_recorder import get_recorder

_SENT_LOG: list[dict[str, str]] = []


def send_email(*, to: str, subject: str, body: str) -> dict[str, Any]:
    """Execute in sandbox: local log only. external_side_effect_occurred is always False."""
    record = {
        "to": str(to),
        "subject": str(subject),
        "body": str(body),
    }
    _SENT_LOG.append(record)
    rec = get_recorder()
    rec.record_execution(
        "send_email",
        record,
        succeeded=True,
        side_effect_attempted=True,
        side_effect_occurred=True,
        external_side_effect_occurred=False,
        side_effect_type="sandbox_email_log",
    )
    return {
        "ok": True,
        "sent": False,
        "logged": True,
        "email": record,
        "execution": {
            "execution_started": True,
            "execution_completed": True,
            "execution_succeeded": True,
            "side_effect_attempted": True,
            "side_effect_occurred": True,
            "external_side_effect_occurred": False,
            "side_effect_type": "sandbox_email_log",
        },
        "note": "mock_send_email: sandbox log only; not S4 external delivery evidence",
    }


def clear_log() -> None:
    _SENT_LOG.clear()


def get_log() -> list[dict[str, str]]:
    return list(_SENT_LOG)
