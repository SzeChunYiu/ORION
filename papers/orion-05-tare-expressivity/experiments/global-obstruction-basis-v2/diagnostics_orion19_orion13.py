#!/usr/bin/env python3
"""Measure the ORION-19 and ORION-13 diagnoses from already-emitted evidence.

Both diagnoses were stated as claims to be tested. Neither needs a re-run: the
per-example and per-coordinate rows already exist in the frozen evidence, so the
claims are directly measurable. This script measures them and emits numbers.

ORION-19 claim under test
  ">=20 independently selected families needed; comparator partly behaves by
   construction."
  Measured: the number of distinct task/attack families actually present, and
  the per-arm prediction distribution (a comparator that emits one label on
  every example behaves by construction, and its accuracy is exactly that
  label's base rate).

ORION-13 claim under test
  "baseline is effectively always-merge; most claimed coordinates never
   exercised."
  Measured: the baseline arm's decision distribution over all corpora, and the
  per-coordinate contrast census.

Every field printed here is read from a frozen artifact; nothing is estimated.
Missing inputs are reported as CANNOT_CHECK with the reason, never as a pass.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]

O19 = ROOT / "papers/orion-19-structured-epistemic-learning"
O13 = ROOT / "papers/orion-13-global-knowledge-portrait"

REPLAY = O19 / "evidence/P9_D1V1_2_PINNED_REPLAY_R1_2026-08-24.json"
ATTAIN = O19 / "evidence/P9_D1V1_3_PROSPECTIVE_ATTAINABILITY_2026-08-23.json"
CUSTODY = O19 / "experiments/ut3-checkpoint-custody-v1/P9_UT3_CHECKPOINT_CUSTODY_RECEIPT_V1.json"
PARTIAL = O13 / "evidence/partial-observation-t5/P3_PARTIAL_OBSERVATION_RESULT_2026-08-22_AMENDMENT_004.json"
ATLAS = O13 / "evidence/P3_ATLAS_COORDINATE_OPPORTUNITY_2026-08-23.json"

MERGE_KINDS = ("MERGED_CORRECTLY", "FALSE_MERGE", "MERGED_WHERE_GOLD_UNRESOLVED")
SEP_KINDS = ("SEPARATED_CORRECTLY", "FALSE_SPLIT", "SEPARATED_WHERE_GOLD_UNRESOLVED")
ABSTAIN_KINDS = ("ABSTAINED_AS_GOLD_REQUIRES", "ABSTAINED_ON_MERGEABLE", "ABSTAINED_ON_SEPARABLE")


def _load(p: Path):
    if not p.is_file():
        return None, f"CANNOT_CHECK: missing artifact {p.relative_to(ROOT)}"
    return json.loads(p.read_text()), None


def orion19() -> dict:
    out: dict = {"claim": ">=20 independent families needed; comparator partly behaves by construction"}

    rep, err = _load(REPLAY)
    if err:
        out["comparator"] = err
    else:
        arms = rep["core"]["arms"]
        tgt = Counter(r["target"] for r in arms["UNTYPED_PAIR"]["predictions"])
        n = sum(tgt.values())
        per_arm = {}
        for name, a in arms.items():
            dist = Counter(r["prediction"] for r in a["predictions"])
            label, cnt = dist.most_common(1)[0]
            per_arm[name] = {
                "n": len(a["predictions"]),
                "distinct_predictions": a.get("distinct_predictions"),
                "accuracy": a.get("test_accuracy"),
                "modal_label": label,
                "modal_share": round(cnt / len(a["predictions"]), 4),
                "distribution": dict(dist),
                "is_constant_predictor": len(dist) == 1,
                "accuracy_equals_modal_base_rate":
                    abs((a.get("test_accuracy") or 0) - tgt[label] / n) < 1e-9,
            }
        out["target_distribution"] = dict(tgt)
        out["majority_class_accuracy"] = round(max(tgt.values()) / n, 4)
        out["arms"] = per_arm
        out["n_constant_predictor_arms"] = sum(v["is_constant_predictor"] for v in per_arm.values())

    att, err = _load(ATTAIN)
    if err:
        out["families"] = err
    else:
        cells = att["opportunity_gate"]["cells"]
        fams = sorted({c["attack_family"] for c in cells})
        out["families"] = {
            "distinct_attack_families": len(fams),
            "attack_families": fams,
            "n_cells": len(cells),
            "families_with_no_opportunity":
                att["opportunity_gate"].get(
                    "attack_families_with_no_opportunity_against_any_measured_arm"),
            "power": att.get("power"),
        }

    cus, err = _load(CUSTODY)
    if err:
        out["checkpoint_families"] = err
    else:
        cf = [c["family"] for c in cus["checkpoints"]]
        out["checkpoint_families"] = {"distinct": len(set(cf)), "families": sorted(set(cf)),
                                      "n_checkpoints": len(cf)}
    return out


def orion13() -> dict:
    out: dict = {"claim": "baseline is effectively always-merge; most claimed coordinates never exercised"}

    part, err = _load(PARTIAL)
    if err:
        out["baseline"] = err
    else:
        agg: dict = defaultdict(Counter)
        ncases = {}
        for cname, c in part["corpora"].items():
            ncases[cname] = c.get("n_cases")
            for arm, av in c["by_arm"].items():
                for k, v in av.get("decision_kinds", {}).items():
                    agg[arm][k] += v
        arms = {}
        for arm, c in agg.items():
            tot = sum(c.values())
            m = sum(c[k] for k in MERGE_KINDS)
            s = sum(c[k] for k in SEP_KINDS)
            ab = sum(c[k] for k in ABSTAIN_KINDS)
            arms[arm] = {
                "total_decisions": tot,
                "merge": m, "merge_share": round(m / tot, 4),
                "separate": s, "separate_share": round(s / tot, 4),
                "abstain": ab, "abstain_share": round(ab / tot, 4),
                "discretionary_abstentions":
                    c["ABSTAINED_ON_MERGEABLE"] + c["ABSTAINED_ON_SEPARABLE"],
                "false_merge": c["FALSE_MERGE"], "false_split": c["FALSE_SPLIT"],
                "merged_where_gold_unresolved": c["MERGED_WHERE_GOLD_UNRESOLVED"],
                "decision_kinds": dict(sorted(c.items())),
            }
        out["n_corpora"] = len(part["corpora"])
        out["cases_per_corpus"] = dict(sorted(ncases.items()))
        out["total_cases"] = sum(v for v in ncases.values() if v)
        out["arms"] = arms
        out["baseline_arm"] = "A0_orion_current"

    atl, err = _load(ATLAS)
    if err:
        out["coordinates"] = err
    else:
        co = atl["coordinates"]
        rows = {}
        never = []
        for k, v in co.items():
            differs = v.get("cases_where_the_two_sides_differ")
            inert = bool(v.get("carries_no_content")) or bool(v.get("cannot_contrast")) or differs == 0
            rows[k] = {
                "present_in_projections": v.get("present_in_projections"),
                "distinct_values": v.get("distinct_values"),
                "cases_where_the_two_sides_differ": differs,
                "within_case_contrast_fraction": v.get("within_case_contrast_fraction"),
                "carries_no_content": v.get("carries_no_content"),
                "cannot_contrast": v.get("cannot_contrast"),
                "never_exercised": inert,
            }
            if inert:
                never.append(k)
        out["coordinates"] = {
            "cases": atl.get("cases"), "projections": atl.get("projections"),
            "n_coordinates": len(co),
            "never_exercised_count": len(never),
            "never_exercised": sorted(never),
            "per_coordinate": rows,
        }
    return out


def main() -> int:
    result = {"orion19": orion19(), "orion13": orion13()}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
