#!/usr/bin/env python3
"""Replay all non-secret P4 publication artifacts from committed safe evidence."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "protected-campaign-31968809206"
FIGURE_DATA = ROOT / "figures" / "data" / "RESULTS_SUMMARY_V1.json"
RENDERER = ROOT / "figures" / "generate_protected_results.py"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    index = json.loads((EVIDENCE / "ARTIFACT_INDEX_V1.json").read_text(encoding="utf-8"))
    assert index["campaign_run_id"] == "31968809206"
    assert index["subject_commit"] == "46977ea104162c4cf64da8138a4c4759065fe6d4"
    assert index["host_custody"]["protected_manifest_sha256"] == "23c7732118bf750b4f5b927aab271cf1e7ee1068d8dc1838ca5119d7e436b102"

    for name, meta in index["safe_files"].items():
        if name == "ARTIFACT_INDEX_V1.json":
            continue
        path = EVIDENCE / name
        assert path.exists(), f"missing safe evidence file: {name}"
        assert path.stat().st_size == meta["bytes"], f"size drift: {name}"
        assert _sha(path) == meta["sha256"], f"hash drift: {name}"

    summary = json.loads((EVIDENCE / "CAMPAIGN_SUMMARY_V1.json").read_text(encoding="utf-8"))
    ablations = json.loads((EVIDENCE / "ABLATION_SUMMARY_V1.json").read_text(encoding="utf-8"))
    telemetry = json.loads((EVIDENCE / "ACCESS_TELEMETRY_SUMMARY_V1.json").read_text(encoding="utf-8"))
    reproduction = json.loads((EVIDENCE / "INDEPENDENT_REPRODUCTION_V1.json").read_text(encoding="utf-8"))
    panel = json.loads((EVIDENCE / "AUTHORITY_BENCHMARK_PANEL_V1.json").read_text(encoding="utf-8"))
    figure_data = json.loads(FIGURE_DATA.read_text(encoding="utf-8"))

    assert summary["typed_panel_status"] == "PASS"
    assert summary["panel_pass"] is True
    assert summary["H1"]["status"] == "PASS"
    assert summary["H1"]["orion_minus_baseline_false_promotion"] == -0.5
    assert summary["H2"]["status"] == "PASS"
    assert summary["H2"]["orion_minus_baseline_clean_coverage"] == 0.0
    assert summary["H3"]["status"] == "NOT_SUPPORTED"
    assert summary["systems"]["ORION"]["rates"]["false_authority_promotion_rate"] == 0.0
    assert summary["systems"]["ORION"]["clean_coverage"] == 1.0
    assert summary["systems"]["ORION"]["clean_false_negative_count"] == 0
    assert len(ablations["ablations"]) == 8
    assert all(item["clean_coverage"] == 1.0 for item in ablations["ablations"].values())
    assert reproduction["headline_reproduced"] is True
    assert reproduction["typed_panel_hash"] == summary["typed_panel_hash"]
    assert panel["artifact_hash"] == summary["typed_panel_hash"]
    assert telemetry["candidate_protected_identifier_hits"] == 0
    assert telemetry["comparator_protected_identifier_hits"] == 0
    assert telemetry["candidate_external_ip_connects"] == 0
    assert telemetry["comparator_external_ip_connects"] == 0
    assert figure_data["typed_panel_hash"] == summary["typed_panel_hash"]
    assert figure_data["H1"] == summary["H1"]
    assert figure_data["H2"] == summary["H2"]
    assert figure_data["H3"] == summary["H3"]

    subprocess.run([sys.executable, str(RENDERER)], check=True, cwd=ROOT)
    expected = [
        ROOT / "figures" / "p4_2_false_promotion.svg",
        ROOT / "figures" / "p4_3_coverage_frontier.svg",
        ROOT / "figures" / "p4_4_detection_by_attack.svg",
        ROOT / "figures" / "p4_5_attribution_vs_support.svg",
        ROOT / "figures" / "p4_6_cost_false_promotion.svg",
        ROOT / "tables" / "p4_t1_attack_custody.tex",
        ROOT / "tables" / "p4_t2_baseline_ablation_results.tex",
        ROOT / "tables" / "p4_t3_cannot_check_errors.tex",
    ]
    for path in expected:
        assert path.exists() and path.stat().st_size > 0, f"renderer did not create {path}"

    receipt = {
        "schema": "P4PublicReplayReceipt.v1",
        "campaign_run_id": "31968809206",
        "subject_commit": index["subject_commit"],
        "typed_panel_hash": summary["typed_panel_hash"],
        "headline_false_promotion_effect": summary["H1"]["orion_minus_baseline_false_promotion"],
        "headline_clean_coverage_effect": summary["H2"]["orion_minus_baseline_clean_coverage"],
        "H3_status": summary["H3"]["status"],
        "safe_file_hashes_verified": True,
        "public_figures_and_tables_regenerated": True,
        "protected_gold_required": False,
    }
    (ROOT / "reproducibility" / "PUBLIC_REPLAY_RECEIPT_V1.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
