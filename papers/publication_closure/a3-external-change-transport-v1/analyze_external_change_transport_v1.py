#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tier_a_analysis_common_v1 import (  # noqa: E402
    bootstrap_mean_interval,
    charged_saving,
    finite_float,
    mean,
    require_disjoint,
)

STRATA = (
    "representation_schema",
    "responsibility_output_contract",
    "objective_acceptance_criterion",
    "evidence_dependency",
)
GOLD = ("REUSE", "REOPEN", "CANNOT_CHECK")
PRED = ("REUSE", "REOPEN", "CANNOT_CHECK")
BASELINES = (
    "ALWAYS_REUSE",
    "ALWAYS_REOPEN",
    "VERSION_PROVENANCE_ONLY",
    "SEMANTIC_DIFF_ONLY",
    "CONFIDENCE_ONLY",
)


def _validate_row(row: dict[str, Any]) -> None:
    required = (
        "cluster_id", "split", "stratum", "source_family_id",
        "normalized_organization_lineage", "artifact_lineage_id", "gold",
        "candidate_prediction", "strongest_baseline_prediction",
        "candidate_downstream_valid", "always_reopen_downstream_valid",
        "candidate_charged_cost", "always_reopen_charged_cost",
        "common_visible_packet_hash", "candidate_visible_packet_hash",
        "baseline_visible_packet_hash", "prediction_sealed_before_gold",
    )
    missing = [k for k in required if k not in row]
    if missing:
        raise ValueError(f"missing fields: {missing}")
    if row["split"] not in ("primary", "replication"):
        raise ValueError("split must be primary or replication")
    if row["stratum"] not in STRATA:
        raise ValueError("unknown stratum")
    if row["gold"] not in GOLD:
        raise ValueError("unknown gold terminal")
    if row["candidate_prediction"] not in PRED or row["strongest_baseline_prediction"] not in PRED:
        raise ValueError("unknown prediction terminal")
    if row["prediction_sealed_before_gold"] is not True:
        raise ValueError("prediction was not sealed before gold")
    visible = row["common_visible_packet_hash"]
    if not isinstance(visible, str) or not visible:
        raise ValueError("common visible packet hash missing")
    if row["candidate_visible_packet_hash"] != visible or row["baseline_visible_packet_hash"] != visible:
        raise ValueError("information parity violation")
    for key in ("cluster_id", "source_family_id", "normalized_organization_lineage", "artifact_lineage_id"):
        if not isinstance(row[key], str) or not row[key]:
            raise ValueError(f"{key} missing")
    if row["gold"] == "CANNOT_CHECK":
        if row["candidate_downstream_valid"] is not None or row["always_reopen_downstream_valid"] is not None:
            raise ValueError("CANNOT_CHECK gold requires null downstream validity")
    else:
        if not isinstance(row["candidate_downstream_valid"], bool) or not isinstance(row["always_reopen_downstream_valid"], bool):
            raise ValueError("adjudicable rows require boolean downstream validity")
    c = finite_float(row["candidate_charged_cost"], "candidate_charged_cost")
    a = finite_float(row["always_reopen_charged_cost"], "always_reopen_charged_cost")
    if c < 0 or a <= 0:
        raise ValueError("costs must satisfy candidate>=0 and always_reopen>0")
    row["candidate_charged_cost"] = c
    row["always_reopen_charged_cost"] = a


def _unsound(pred: str, gold: str) -> int:
    return int(gold == "REOPEN" and pred == "REUSE")


def _paired_improvement(row: dict[str, Any]) -> float:
    return float(_unsound(row["strongest_baseline_prediction"], row["gold"]) - _unsound(row["candidate_prediction"], row["gold"]))


def _eligible(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [r for r in rows if r["gold"] != "CANNOT_CHECK"]


def _direction(rows: list[dict[str, Any]]) -> float:
    e = _eligible(rows)
    return mean(_paired_improvement(r) for r in e) if e else 0.0


def analyze(payload: dict[str, Any], *, resamples: int = 10_000) -> dict[str, Any]:
    if payload.get("schema") != "ORION.A3.ExternalChangeTransportResultInput.v1":
        raise ValueError("wrong input schema")
    baseline = payload.get("strongest_noncandidate_baseline_id")
    if baseline not in BASELINES:
        raise ValueError("strongest baseline was not frozen to an allowed non-candidate id")
    rows = payload.get("rows")
    if not isinstance(rows, list):
        raise ValueError("rows must be a list")
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("row must be object")
        _validate_row(row)
        if row["cluster_id"] in seen:
            raise ValueError(f"duplicate cluster_id: {row['cluster_id']}")
        seen.add(row["cluster_id"])

    primary = [r for r in rows if r["split"] == "primary"]
    repl = [r for r in rows if r["split"] == "replication"]
    p_counts = Counter(r["stratum"] for r in primary)
    r_counts = Counter(r["stratum"] for r in repl)
    quota_ok = len(primary) == 96 and len(repl) == 32 and all(p_counts[s] == 24 and r_counts[s] == 8 for s in STRATA)

    for field in ("source_family_id", "normalized_organization_lineage", "artifact_lineage_id"):
        require_disjoint((r[field] for r in primary), (r[field] for r in repl), field)

    p_eligible = _eligible(primary)
    r_eligible = _eligible(repl)
    cannot_reasons = Counter(
        payload_row.get("cannot_check_reason", "UNSPECIFIED")
        for payload_row in rows if payload_row["gold"] == "CANNOT_CHECK"
    )
    if not quota_ok or not p_eligible or not r_eligible:
        terminal = "CANNOT_CHECK_QUOTA_OR_CUSTODY"
        result_core = {}
    else:
        paired = [_paired_improvement(r) for r in p_eligible]
        lo, hi = bootstrap_mean_interval(paired, "A3|primary|paired-unsound", resamples)
        validity_diff = mean(float(r["candidate_downstream_valid"]) - float(r["always_reopen_downstream_valid"]) for r in p_eligible)
        saving = charged_saving(
            (r["candidate_charged_cost"] for r in p_eligible),
            (r["always_reopen_charged_cost"] for r in p_eligible),
        )
        stratum_dir = {s: _direction([r for r in primary if r["stratum"] == s]) for s in STRATA}
        positive_strata = sum(v > 0 for v in stratum_dir.values())
        loo = {}
        for held in STRATA:
            kept = [r for r in primary if r["stratum"] != held]
            loo[held] = _direction(kept)
        repl_dir = _direction(repl)
        if lo <= 0:
            terminal = "NOT_SUPPORTED_UNSOUND_REUSE"
        elif validity_diff < -0.01:
            terminal = "NOT_SUPPORTED_DOWNSTREAM_VALIDITY"
        elif saving < 0.25:
            terminal = "NOT_SUPPORTED_RECOMPUTE_SAVING"
        elif positive_strata < 3 or any(v <= 0 for v in loo.values()):
            terminal = "HETEROGENEOUS_STRATUM_FAILURE"
        elif repl_dir <= 0:
            terminal = "REPLICATION_DIRECTION_FAILURE"
        else:
            terminal = "SUPPORTED_FROZEN_A3_GATE"
        result_core = {
            "primary_paired_unsound_reuse_improvement_mean": mean(paired),
            "primary_paired_unsound_reuse_improvement_ci95": [lo, hi],
            "candidate_minus_always_reopen_downstream_validity": validity_diff,
            "charged_recompute_saving_vs_always_reopen": saving,
            "stratum_direction": stratum_dir,
            "positive_strata": positive_strata,
            "leave_one_stratum_out_direction": loo,
            "replication_direction": repl_dir,
        }

    return {
        "schema": "ORION.A3.ExternalChangeTransportAnalysisResult.v1",
        "strongest_noncandidate_baseline_id": baseline,
        "quota_ok": quota_ok,
        "primary_counts": {s: p_counts[s] for s in STRATA},
        "replication_counts": {s: r_counts[s] for s in STRATA},
        "primary_eligible_n": len(p_eligible),
        "replication_eligible_n": len(r_eligible),
        "cannot_check_reasons": dict(sorted(cannot_reasons.items())),
        "terminal": terminal,
        **result_core,
    }


def _fixture() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    counter = 0
    for split, per in (("primary", 24), ("replication", 8)):
        for stratum in STRATA:
            for _ in range(per):
                cid = f"{split}-{counter}"
                rows.append({
                    "cluster_id": cid,
                    "split": split,
                    "stratum": stratum,
                    "source_family_id": f"sf-{cid}",
                    "normalized_organization_lineage": f"org-{cid}",
                    "artifact_lineage_id": f"art-{cid}",
                    "gold": "REOPEN",
                    "candidate_prediction": "REOPEN",
                    "strongest_baseline_prediction": "REUSE",
                    "candidate_downstream_valid": True,
                    "always_reopen_downstream_valid": True,
                    "candidate_charged_cost": 0.5,
                    "always_reopen_charged_cost": 1.0,
                    "common_visible_packet_hash": f"packet-{cid}",
                    "candidate_visible_packet_hash": f"packet-{cid}",
                    "baseline_visible_packet_hash": f"packet-{cid}",
                    "prediction_sealed_before_gold": True,
                })
                counter += 1
    return {
        "schema": "ORION.A3.ExternalChangeTransportResultInput.v1",
        "strongest_noncandidate_baseline_id": "VERSION_PROVENANCE_ONLY",
        "rows": rows,
    }


def self_test() -> dict[str, Any]:
    payload = _fixture()
    result = analyze(payload, resamples=256)
    assert result["terminal"] == "SUPPORTED_FROZEN_A3_GATE"
    bad = _fixture()
    bad["rows"][-1]["source_family_id"] = bad["rows"][0]["source_family_id"]
    try:
        analyze(bad, resamples=32)
    except ValueError as exc:
        assert "overlap" in str(exc)
    else:
        raise AssertionError("source-disjointness mutant was not rejected")
    return {"decision": "GREEN", "terminal": result["terminal"], "rows": len(payload["rows"])}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
        return 0
    if args.input is None:
        parser.error("input JSON required unless --self-test")
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    result = analyze(payload)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
