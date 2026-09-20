"""D2 bridge configuration and AdaptiGuard pin metadata."""

from __future__ import annotations

from dataclasses import dataclass

# Pinned AdaptiGuard commit (external package; not vendored in AIB).
ADAPTI_GUARD_COMMIT_PIN = "c096b878e0733fda27150d0fb13d579e95579e5b"

D2_BRIDGE_VERSION = "0.1.0"

DETECTOR_LOCK_ID = "PHASE1-DETECTOR-LOCK-0.1"

# Matches make_core_defense() / get_defense_fn("PHASE1-CORE") default.
# PROVISIONAL: must be set explicitly per run; not a confirmed scientific baseline for papers.
DEFAULT_BASELINE_KEY = "PHASE1-CORE"
DEFAULT_DEFENSE_LEVEL_PROVISIONAL = 0

DEFAULT_DENY_MESSAGE_MODE = "tool_denied_literal"
DEFAULT_BASE_PROMPT_ID = "d0"
D2_PROMPT_ID = "d2"
TRACE_SCHEMA_VERSION = "aib-d2-bridge-1"


@dataclass(frozen=True)
class D2DefenseConfig:
    """Explicit defense configuration for D2 (no silent baseline choice)."""

    baseline_key: str = DEFAULT_BASELINE_KEY
    # PROVISIONAL default — override via env/CLI for experiments; record in manifest.
    defense_level: int = DEFAULT_DEFENSE_LEVEL_PROVISIONAL
    defense_level_provisional: bool = True
    adaptiguard_commit: str = ADAPTI_GUARD_COMMIT_PIN
    base_prompt_id: str = DEFAULT_BASE_PROMPT_ID
    deny_message_mode: str = DEFAULT_DENY_MESSAGE_MODE
    detector_lock_id: str = DETECTOR_LOCK_ID

    def manifest_fragment(self) -> dict[str, object]:
        return {
            "baseline_key": self.baseline_key,
            "defense_level": self.defense_level,
            "defense_level_provisional": self.defense_level_provisional,
            "adaptiguard_commit": self.adaptiguard_commit,
            "base_prompt_id": self.base_prompt_id,
            "deny_message_mode": self.deny_message_mode,
            "detector_lock_id": self.detector_lock_id,
            "action_cost_source": "not_emitted_by_core_pipeline",
        }
