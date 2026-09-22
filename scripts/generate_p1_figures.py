#!/usr/bin/env python3
"""P1 evidence figures: descriptive plots from verified P4.2 paired run (no new experiments)."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.score_p4_3_paired_metrics import score_paired  # noqa: E402

PRIMARY_RUN_ID = "p42-primary-d0-d2-20260921T173736Z-controlled"
FORBIDDEN_RUN_IDS = (
    "p42-primary-d0-d2-20260922T130300Z-controlled",
    "p42-primary-d0-d2-20260922T122759Z",
    "p42-primary-d0-d2-20260922T122759Z-controlled",
)

D0_LABEL = "D0 — No defense"
D2_LABEL = "D2 — AdaptiGuard defense"

UTILITY_PROVENANCE = (
    "D0/RESULTS.json and D2/RESULTS.json via scripts/score_p4_3_live_metrics.score_run "
    "(utility_success on judge_status==ok benign rows; paired pipeline / result_mapper)"
)


def _default_run_dir() -> Path:
    freeze = ROOT / "config" / "p4_2_primary_research_protocol_freeze.v1.json"
    if freeze.is_file():
        rel = json.loads(freeze.read_text(encoding="utf-8")).get("historical_run_immutable")
        if rel:
            return (ROOT / rel).resolve()
    return (ROOT / "results" / "p4_2_paired" / PRIMARY_RUN_ID).resolve()


def _assert_run_allowed(run_dir: Path) -> None:
    manifest = run_dir / "RUN_MANIFEST.json"
    if not manifest.is_file():
        raise SystemExit(f"RUN_MANIFEST missing: {run_dir}")
    run_id = json.loads(manifest.read_text(encoding="utf-8")).get("run_id", "")
    if run_id in FORBIDDEN_RUN_IDS or any(bad in run_id for bad in ("130300", "122759")):
        raise SystemExit(f"Refusing forbidden or non-primary run_id: {run_id}")
    if PRIMARY_RUN_ID not in run_id:
        raise SystemExit(f"Expected primary run {PRIMARY_RUN_ID}, got {run_id}")


def collect_p1_figure_data(run_dir: Path) -> dict:
    _assert_run_allowed(run_dir)
    summary = score_paired(run_dir)
    if summary.get("mode") != "live":
        raise SystemExit(f"Unexpected run mode: {summary.get('mode')}")

    d0, d2 = summary["D0"], summary["D2"]
    for side, metrics in ("D0", d0), ("D2", d2):
        if metrics.get("invalid_or_judge_failure", 0) != 0:
            raise SystemExit(f"{side}: judge failures present")
        if metrics.get("valid_judged_episodes") != 18:
            raise SystemExit(f"{side}: expected 18 judged episodes")

    transitions = Counter()
    for row in summary.get("paired_attack_transitions") or []:
        a, b = row.get("d0_attack_success"), row.get("d2_attack_success")
        if a is True and b is True:
            transitions["success_to_success"] += 1
        elif a is True and b is False:
            transitions["success_to_failure"] += 1
        elif a is False and b is True:
            transitions["failure_to_success"] += 1
        elif a is False and b is False:
            transitions["failure_to_failure"] += 1

    expected = {
        "success_to_success": 1,
        "success_to_failure": 0,
        "failure_to_success": 0,
        "failure_to_failure": 8,
    }
    normalized = {k: transitions.get(k, 0) for k in expected}
    if normalized != expected:
        raise SystemExit(f"Paired transition mismatch: {normalized} != {expected}")

    data = {
        "descriptive_only": True,
        "run_id": PRIMARY_RUN_ID,
        "run_dir": str(run_dir.relative_to(ROOT)) if run_dir.is_relative_to(ROOT) else str(run_dir),
        "metrics_source": "scripts/score_p4_3_paired_metrics.score_paired",
        "utility_provenance": UTILITY_PROVENANCE,
        "population": {"attack_n": 9, "benign_n": 9},
        "ASR": {
            D0_LABEL: d0["ASR"],
            D2_LABEL: d2["ASR"],
        },
        "Utility": {
            D0_LABEL: d0["Utility"],
            D2_LABEL: d2["Utility"],
        },
        "FPR": {
            D0_LABEL: d0["FPR"],
            D2_LABEL: d2["FPR"],
        },
        "paired_transitions": normalized,
    }
    return data


def _pct(num: int, den: int) -> float:
    return (100.0 * num / den) if den else 0.0


def _annotate_bar(ax, bar, num: int, den: int) -> None:
    pct = _pct(num, den)
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        f"{num}/{den}\n({pct:.1f}%)",
        ha="center",
        va="bottom",
        fontsize=9,
    )


def render_figures(data: dict, out_dir: Path) -> list[Path]:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise SystemExit("matplotlib required for figure render: pip install matplotlib") from exc

    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    def save(fig, stem: str) -> None:
        for ext in (".png", ".pdf"):
            path = out_dir / f"{stem}{ext}"
            fig.savefig(path, bbox_inches="tight", dpi=150 if ext == ".png" else None)
            written.append(path)
        plt.close(fig)

    # Figure 1 — ASR
    fig, ax = plt.subplots(figsize=(5, 4))
    labels = [D0_LABEL, D2_LABEL]
    nums = [data["ASR"][lb]["numerator"] for lb in labels]
    dens = [data["ASR"][lb]["denominator"] for lb in labels]
    bars = ax.bar(range(2), [_pct(n, d) for n, d in zip(nums, dens)], color=["#4c72b0", "#55a868"])
    ax.set_xticks(range(2), labels, rotation=15, ha="right")
    ax.set_ylabel("Attack success rate (%)")
    ax.set_ylim(0, max(15, max(_pct(n, d) for n, d in zip(nums, dens)) * 1.35))
    ax.set_title("Primary ASR (COV-A attacks, n = 9)")
    for bar, n, d in zip(bars, nums, dens):
        _annotate_bar(ax, bar, n, d)
    save(fig, "fig_p1_primary_asr_d0_d2")

    # Figure 2 — Utility and FPR (grouped)
    fig, ax = plt.subplots(figsize=(6, 4))
    x = [0, 1]
    util = [data["Utility"][lb] for lb in labels]
    fpr = [data["FPR"][lb] for lb in labels]
    w = 0.35
    b1 = ax.bar([i - w / 2 for i in x], [_pct(u["numerator"], u["denominator"]) for u in util], w, label="Utility", color="#4c72b0")
    b2 = ax.bar([i + w / 2 for i in x], [_pct(f["numerator"], f["denominator"]) for f in fpr], w, label="FPR", color="#c44e52")
    ax.set_xticks(x, labels, rotation=15, ha="right")
    ax.set_ylabel("Rate (%)")
    ax.set_ylim(0, 110)
    ax.set_title("Benign utility and FPR (n = 9 benign)")
    ax.legend(loc="upper right")
    for bars, series in ((b1, util), (b2, fpr)):
        for bar, m in zip(bars, series):
            _annotate_bar(ax, bar, m["numerator"], m["denominator"])
    save(fig, "fig_p1_utility_fpr_d0_d2")

    # Figure 3 — paired transitions
    fig, ax = plt.subplots(figsize=(7, 4))
    t_labels = [
        "success → success",
        "success → failure",
        "failure → success",
        "failure → failure",
    ]
    t_keys = [
        "success_to_success",
        "success_to_failure",
        "failure_to_success",
        "failure_to_failure",
    ]
    counts = [data["paired_transitions"][k] for k in t_keys]
    bars = ax.bar(range(4), counts, color="#8172b3")
    ax.set_xticks(range(4), t_labels, rotation=20, ha="right")
    ax.set_ylabel("Episode count")
    ax.set_title("D0 → D2 paired outcomes (observed transitions)")
    ymax = max(counts) if counts else 1
    ax.set_ylim(0, ymax + max(1, ymax * 0.2))
    for bar, c in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(c), ha="center", va="bottom")
    save(fig, "fig_p1_paired_transitions_d0_d2")

    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate P1 manuscript figures from verified P4.2 run.")
    parser.add_argument("--run-dir", type=Path, default=None, help="Paired run directory (default: freeze historical_run_immutable)")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "docs" / "manuscript" / "figures",
        help="Output directory for figures and figure data JSON",
    )
    parser.add_argument("--data-only", action="store_true", help="Write p1_figure_data.json only (no plots)")
    args = parser.parse_args()

    run_dir = (args.run_dir or _default_run_dir()).resolve()
    out_dir = args.out_dir.resolve()
    data = collect_p1_figure_data(run_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    data_path = out_dir / "p1_figure_data.json"
    data_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if not args.data_only:
        render_figures(data, out_dir)

    print(json.dumps({"figure_data": str(data_path.relative_to(ROOT)), "run_dir": data["run_dir"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
