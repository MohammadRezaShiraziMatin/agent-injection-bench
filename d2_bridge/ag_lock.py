"""Verify installed AdaptiGuard core modules against PHASE1 detector lock hashes."""

from __future__ import annotations

import hashlib
import importlib.util
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from d2_bridge.config import ADAPTI_GUARD_COMMIT_PIN, DETECTOR_LOCK_ID

# SHA-256 from adapti-guard `configs/phase1_detector_lock.json` at pin c096b87.
LOCKED_SHA256: dict[str, str] = {
    "detector": "4c4484db45861681a4f9bc073437034c571a5c544f575ee8b798204fba9f9459",
    "risk": "ef7d0eada9f7c1cd5069825ce65a9879d847f4bfde2c901107a0e4854f0252f2",
    "policy": "1543179aaf45af66c4a04b8fb6cbf370c307f62a23edff37aa1215c5937838f3",
}

_MODULE_IMPORTS: dict[str, str] = {
    "detector": "adapti_guard.detector.prompt_injection_detector_phase1",
    "risk": "adapti_guard.risk.risk_engine_core",
    "policy": "adapti_guard.policy.core_policy",
}


class DetectorLockError(RuntimeError):
    """Installed AdaptiGuard modules do not match the pinned detector lock."""


@dataclass(frozen=True)
class LockVerificationResult:
    lock_id: str
    adaptiguard_commit: str
    components: dict[str, dict[str, str]]
    ok: bool

    def manifest_fragment(self) -> dict[str, Any]:
        return {
            "detector_lock_id": self.lock_id,
            "detector_lock_sha256": {k: v["sha256"] for k, v in self.components.items()},
            "detector_lock_verified": self.ok,
            "adaptiguard_commit": self.adaptiguard_commit,
        }


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _module_source_path(module_name: str) -> Path:
    spec = importlib.util.find_spec(module_name)
    if spec is None or not spec.origin or spec.origin.endswith("__init__.py"):
        raise DetectorLockError(f"cannot resolve source path for {module_name}")
    return Path(spec.origin)


def verify_detector_lock(
    *,
    adaptiguard_commit: str = ADAPTI_GUARD_COMMIT_PIN,
    lock_id: str = DETECTOR_LOCK_ID,
    raise_on_mismatch: bool = True,
) -> LockVerificationResult:
    """Hash installed AG detector/risk/policy modules vs the pinned lock file."""
    components: dict[str, dict[str, str]] = {}
    ok = True
    for key, expected in LOCKED_SHA256.items():
        mod = _MODULE_IMPORTS[key]
        path = _module_source_path(mod)
        actual = _sha256_file(path)
        match = actual == expected
        components[key] = {
            "module": mod,
            "path": str(path),
            "sha256": actual,
            "expected_sha256": expected,
            "match": str(match),
        }
        if not match:
            ok = False
    result = LockVerificationResult(
        lock_id=lock_id,
        adaptiguard_commit=adaptiguard_commit,
        components=components,
        ok=ok,
    )
    if raise_on_mismatch and not ok:
        mismatches = [k for k, v in components.items() if v["expected_sha256"] != v["sha256"]]
        raise DetectorLockError(
            f"AdaptiGuard detector lock mismatch for {mismatches}; "
            f"expected pin {adaptiguard_commit} ({lock_id})"
        )
    return result


def make_core_pipeline(defense_config: Any) -> Any:
    """Construct CoreDefensePipeline after lock verification."""
    from adapti_guard.core.core_pipeline import CoreDefensePipeline

    verify_detector_lock(adaptiguard_commit=defense_config.adaptiguard_commit)
    return CoreDefensePipeline(defense_level=defense_config.defense_level)
