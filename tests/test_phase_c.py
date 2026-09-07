"""Phase C: D1 prompt load + Wilson helper."""

from __future__ import annotations

from pathlib import Path

from agent.loop import DEFAULT_PROMPT_ID, load_system_prompt
from scripts.aggregate_phase_c import wilson_interval

ROOT = Path(__file__).resolve().parents[1]


def test_d1_prompt_loads_and_differs_from_d0() -> None:
    assert DEFAULT_PROMPT_ID == "d0"
    d0 = load_system_prompt("d0")
    d1 = load_system_prompt("d1")
    assert (ROOT / "prompts" / "d1_prompt_defense.txt").is_file()
    assert "untrusted" in d1.lower()
    assert "do not follow instructions" in d1.lower()
    assert d0.strip() != d1.strip()
    assert "untrusted" not in d0.lower()


def test_wilson_interval_empty_and_nonzero() -> None:
    empty = wilson_interval(0, 0)
    assert empty["low"] is None and empty["high"] is None
    ci = wilson_interval(1, 2)
    assert ci["n"] == 2
    assert 0.0 <= float(ci["low"]) <= float(ci["high"]) <= 1.0
