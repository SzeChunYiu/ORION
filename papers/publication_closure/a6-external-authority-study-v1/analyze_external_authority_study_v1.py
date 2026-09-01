#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tier_a_analysis_common_v1 import bootstrap_mean_interval, charged_saving, finite_float, mean, require_disjoint  # noqa: E402

STRATA = (
    "scientific_software_release_provenance_attestation",
    "workflowhub_rocrate_versioned_workflow",
    "scientific_record_transition",
)
ARMS = (
    "AUTHORIZATION_ONLY",
    "PROVENANCE_ONLY",
    "VERIFICATION_ONLY",
    "STRONGEST_COMBINED_DONOR_WITHOUT_SCIENTIFIC_DISCHARGE",
    "MERGED_CANDIDATE",
    "INFORMATION_EQUIVALENT_TYPED_DONOR",
)
INCOMPLETE_DONORS = ARMS[:4]
TERMINALS = ("ADMIT", "DENY", "CANNOT_CHECK")


def validate_row(row: dict[str, Any]) -> None:
    required = (
        "packet_id", "split", "stratum", "source_family_id", "normalized_organization_lineage",
        "artifact_lineage_id", "gold_local_action_release_authority", "gold_scientific_discharge_authority",
        "predictions", "candidate_post_revalidation_valid", "global_recheck_valid",
        "candidate_recheck_work", "global_recheck_work", "common_visible_packet_hash",
        "arm_visible_packet_hashes", "prediction_sealed_before_gold",
    )
    missing = [k for k in required if k not in row]
    if missing:
        raise ValueError(f"missing fields: {missing}")
    if row["split"] not in ("primary", "replication") or row["stratum"] not in STRATA:
        raise ValueError("bad split/stratum")
    if row["gold_local_action_release_authority"] not in (True, False, "CANNOT_CHECK"):
        raise ValueError("bad local authority gold")
    if row["gold_scientific_discharge_authority"] not in TERMINALS:
        raise ValueError("bad scientific authority gold")
    preds = row["predictions"]
    if not isinstance(preds, dict) or set(preds) != set(ARMS):
        raise ValueError("predictions must contain exactly the six frozen arms")
    if any(preds[a] not in TERMINALS for a in ARMS):
        raise ValueError("bad prediction terminal")
    if preds["MERGED_CANDIDATE"] != preds["INFORMATION_EQUIVALENT_TYPED_DONOR"]:
        raise ValueError("information-equivalent typed donor mismatch")
    if row["prediction_sealed_before_gold"] is not True:
        raise ValueError("prediction not sealed before gold")
    common = row["common_visible_packet_hash"]
    hashes = row["arm_visible_packet_hashes"]
    if not isinstance(common, str) or not common or not isinstance(hashes, dict):
        raise ValueError("visible packet hashes missing")
    for arm in ARMS:
        if hashes.get(arm) != common:
            raise ValueError(f"information parity violation for {arm}")
    cw = finite_float(row["candidate_recheck_work"], "candidate_recheck_work")
    gw = finite_float(row["global_recheck_work"], "global_recheck_work")
    if cw < 0 or gw <= 0:
        raise ValueError("recheck work must satisfy candidate>=0 and global>0")
    row["candidate_recheck_work"] = cw
    row["global_recheck_work"] = gw
    if row["gold_scientific_discharge_authority"] == "CANNOT_CHECK":
        if row["candidate_post_revalidation_valid"] is not None or row["global_recheck_valid"] is not None:
            raise ValueError("CANNOT_CHECK scientific gold requires null validity")
    else:
        if not isinstance(row["candidate_post_revalidation_valid"], bool) or not isinstance(row["global_recheck_valid"], bool):
            raise ValueError("adjudicable row requires boolean validity")


def eligible(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [r for r in rows if r["gold_scientific_discharge_authority"] != "CANNOT_CHECK"]


def false_promotion(row: dict[str, Any], arm: str) -> int:
    return int(row["gold_scientific_discharge_authority"] == "DENY" and row["predictions"][arm] == "ADMIT")


def valid_admission(row: dict[str, Any], arm: str) -> int | None:
    if row["gold_scientific_discharge_authority"] != "ADMIT":
        return None
    return int(row["predictions"][arm] == "ADMIT")


def direction(rows: list[dict[str, Any]], donor: str) -> float:
    e = eligible(rows)
    if not e:
        return 0.0
    return mean(false_promotion(r, donor) - false_promotion(r, "MERGED_CANDIDATE") for r in e)


def admission_rate(rows: list[dict[str, Any]], arm: str) -> float | None:
    vals = [v for r in rows if (v := valid_admission(r, arm)) is not None]
    return mean(vals) if vals else None


def analyze(payload: dict[str, Any], *, resamples: int = 10_000) -> dict[str, Any]:
    if payload.get("schema") != "ORION.A6.ExternalAuthorityResultInput.v1":
        raise ValueError("wrong schema")
    strongest = payload.get("strongest_incomplete_donor_id")
    if strongest not in INCOMPLETE_DONORS:
        raise ValueError("strongest incomplete donor id was not frozen to an allowed donor")
    rows = payload.get("rows")
    if not isinstance(rows, list):
        raise ValueError("rows must be list")
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("row must be object")
        validate_row(row)
        if row["packet_id"] in seen:
            raise ValueError(f"duplicate packet: {row['packet_id']}")
        seen.add(row["packet_id"])
    primary = [r for r in rows if r["split"] == "primary"]
    repl = [r for r in rows if r["split"] == "replication"]
    counts = Counter(r["stratum"] for r in primary)
    quota_ok = len(primary) == 60 and all(counts[s] == 20 for s in STRATA)
    replication_present = len(repl) > 0
    for field in ("source_family_id", "normalized_organization_lineage", "artifact_lineage_id"):
        require_disjoint((r[field] for r in primary), (r[field] for r in repl), field)
    pe = eligible(primary)
    re = eligible(repl)

    if not quota_ok or not replication_present or not pe or not re:
        terminal = "CANNOT_CHECK_PRIMARY_OR_REPLICATION_CUSTODY"
        metrics: dict[str, Any] = {}
    else:
        paired = [float(false_promotion(r, strongest) - false_promotion(r, "MERGED_CANDIDATE")) for r in pe]
        lo, hi = bootstrap_mean_interval(paired, "A6|primary|false-promotion", resamples)
        safe = []
        for arm in INCOMPLETE_DONORS:
            if sum(false_promotion(r, arm) for r in pe) == 0:
                rate = admission_rate(pe, arm)
                safe.append(((-1.0 if rate is None else rate), INCOMPLETE_DONORS.index(arm), arm))
        safe.sort(key=lambda x: (-x[0], x[1]))
        best_safe_arm = safe[0][2] if safe else None
        best_safe_rate = admission_rate(pe, best_safe_arm) if best_safe_arm else None
        cand_admit = admission_rate(pe, "MERGED_CANDIDATE")
        admission_gap = None if best_safe_rate is None or cand_admit is None else cand_admit - best_safe_rate
        saving = charged_saving((r["candidate_recheck_work"] for r in pe), (r["global_recheck_work"] for r in pe))
        cand_valid = mean(float(r["candidate_post_revalidation_valid"]) for r in pe)
        global_valid = mean(float(r["global_recheck_valid"]) for r in pe)
        stratum_dir = {s: direction([r for r in primary if r["stratum"] == s], strongest) for s in STRATA}
        repl_dir = direction(repl, strongest)

        if lo <= 0:
            terminal = "NOT_SUPPORTED_FALSE_PROMOTION"
        elif best_safe_arm is None or admission_gap is None:
            terminal = "CANNOT_CHECK_PRIMARY_OR_REPLICATION_CUSTODY"
        elif admission_gap < -0.02:
            terminal = "NOT_SUPPORTED_VALID_ADMISSION"
        elif saving < 0.25 or cand_valid < global_valid:
            terminal = "NOT_SUPPORTED_SELECTIVE_REVALIDATION"
        elif any(v <= 0 for v in stratum_dir.values()):
            terminal = "HETEROGENEOUS_STRATUM_FAILURE"
        elif repl_dir <= 0:
            terminal = "REPLICATION_DIRECTION_FAILURE"
        else:
            terminal = "SUPPORTED_FROZEN_A6_EXTERNAL_GATE"
        metrics = {
            "paired_false_promotion_improvement_mean": mean(paired),
            "paired_false_promotion_improvement_ci95": [lo, hi],
            "best_safe_comparator": best_safe_arm,
            "best_safe_valid_admission_rate": best_safe_rate,
            "candidate_valid_admission_rate": cand_admit,
            "candidate_minus_best_safe_admission_rate": admission_gap,
            "selective_recheck_saving": saving,
            "candidate_post_revalidation_validity_rate": cand_valid,
            "global_recheck_validity_rate": global_valid,
            "stratum_direction": stratum_dir,
            "replication_direction": repl_dir,
        }

    return {
        "schema": "ORION.A6.ExternalAuthorityAnalysisResult.v1",
        "strongest_incomplete_donor_id": strongest,
        "primary_quota_ok": quota_ok,
        "primary_counts": {s: counts[s] for s in STRATA},
        "replication_present": replication_present,
        "replication_n": len(repl),
        "primary_adjudicable_n": len(pe),
        "replication_adjudicable_n": len(re),
        "typed_donor_exact_tie": True,
        "terminal": terminal,
        **metrics,
    }


def _fixture() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    n = 0
    for split, per in (("primary", 20), ("replication", 4)):
        for stratum in STRATA:
            for i in range(per):
                pid = f"{split}-{n}"
                gold = "DENY" if i % 2 == 0 else "ADMIT"
                candidate = gold
                predictions = {
                    "AUTHORIZATION_ONLY": "ADMIT",
                    "PROVENANCE_ONLY": "ADMIT",
                    "VERIFICATION_ONLY": "DENY",
                    "STRONGEST_COMBINED_DONOR_WITHOUT_SCIENTIFIC_DISCHARGE": "ADMIT",
                    "MERGED_CANDIDATE": candidate,
                    "INFORMATION_EQUIVALENT_TYPED_DONOR": candidate,
                }
                common = f"packet-{pid}"
                rows.append({
                    "packet_id": pid,
                    "split": split,
                    "stratum": stratum,
                    "source_family_id": f"source-{pid}",
                    "normalized_organization_lineage": f"org-{pid}",
                    "artifact_lineage_id": f"art-{pid}",
                    "gold_local_action_release_authority": True,
                    "gold_scientific_discharge_authority": gold,
                    "predictions": predictions,
                    "candidate_post_revalidation_valid": True,
                    "global_recheck_valid": True,
                    "candidate_recheck_work": 0.5,
                    "global_recheck_work": 1.0,
                    "common_visible_packet_hash": common,
                    "arm_visible_packet_hashes": {arm: common for arm in ARMS},
                    "prediction_sealed_before_gold": True,
                })
                n += 1
    return {
        "schema": "ORION.A6.ExternalAuthorityResultInput.v1",
        "strongest_incomplete_donor_id": "STRONGEST_COMBINED_DONOR_WITHOUT_SCIENTIFIC_DISCHARGE",
        "rows": rows,
    }


def self_test() -> dict[str, Any]:
    payload = _fixture()
    result = analyze(payload, resamples=128)
    assert result["terminal"] == "SUPPORTED_FROZEN_A6_EXTERNAL_GATE"
    bad = _fixture()
    bad["rows"][0]["predictions"]["INFORMATION_EQUIVALENT_TYPED_DONOR"] = "ADMIT" if bad["rows"][0]["predictions"]["MERGED_CANDIDATE"] != "ADMIT" else "DENY"
    try:
        analyze(bad, resamples=16)
    except ValueError as exc:
        assert "typed donor" in str(exc)
    else:
        raise AssertionError("typed-donor mismatch mutant was not rejected")
    return {"decision": "GREEN", "rows": len(payload["rows"]), "terminal": result["terminal"]}


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
    result = analyze(json.loads(args.input.read_text(encoding="utf-8")))
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
