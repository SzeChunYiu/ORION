#!/usr/bin/env python3
"""Collect the frozen evaluator's V3 output into PANEL_V3.json and print it.

Reads only what ``evaluate_campaign_v2.py`` emitted. Computes nothing new: the
hypotheses, the comparator choice and the intervals are the frozen evaluator's.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("eval_dir", type=Path)
    parser.add_argument("--output", type=Path, default=HERE / "PANEL_V3.json")
    parser.add_argument("--construction", default="v3")
    parser.add_argument("--seed-label", default="p4-v3-panel-20260821")
    args = parser.parse_args()

    summary = json.loads(
        (args.eval_dir / "campaign_summary.json").read_text(encoding="utf-8")
    )
    systems = {
        system_id: {
            "correct_cannot_check_rate": entry["rates"]["correct_cannot_check_rate"],
            "correct_cannot_check": round(
                entry["rates"]["correct_cannot_check_rate"] * 30
            ),
            "false_promotion_rate": entry["rates"]["false_authority_promotion_rate"],
            "false_promotions": round(
                entry["rates"]["false_authority_promotion_rate"] * 360
            ),
            "false_promotion_ci95": entry["false_promotion_ci95"],
            "clean_coverage": entry["clean_coverage"],
            "clean_coverage_ci95": entry["clean_coverage_ci95"],
        }
        for system_id, entry in summary["systems"].items()
    }
    report = {
        "schema": "P4PanelV3.v1",
        "freeze_document": (
            "research/campaigns/2026-08-21-p4-battery-v3-identifiable/FREEZE.md"
        ),
        "case_construction": args.construction,
        "battery_seed": args.seed_label,
        "campaign_run_id": summary["campaign_run_id"],
        "case_count": summary["case_count"],
        "repeat_count": summary["repeat_count"],
        "strongest_frozen_comparator": summary["strongest_frozen_comparator"],
        "typed_panel_status": summary["typed_panel_status"],
        "typed_panel_blockers": summary["typed_panel_blockers"],
        "panel_pass": summary["panel_pass"],
        "H1": summary["H1"],
        "H2": summary["H2"],
        "H3": summary["H3"],
        "systems": systems,
        "cannot_check_family_summary": {
            system_id: families.get("INSUFFICIENT_EVIDENCE")
            for system_id, families in summary["family_summary"].items()
        },
    }
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(f"comparator: {report['strongest_frozen_comparator']}")
    for name in ("H1", "H2", "H3"):
        print(f"{name}: {report[name]}")
    print(f"typed panel: {report['typed_panel_status']} pass={report['panel_pass']}")
    print(f"blockers: {report['typed_panel_blockers']}")
    print(f"\n{'system':<46} {'CC/30':>7} {'FP/360':>8} {'clean':>7}")
    for system_id, entry in sorted(
        systems.items(), key=lambda item: (-item[1]["correct_cannot_check"], item[0])
    ):
        print(
            f"{system_id:<46} {entry['correct_cannot_check']:>7} "
            f"{entry['false_promotions']:>8} {entry['clean_coverage']:>7.3f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
