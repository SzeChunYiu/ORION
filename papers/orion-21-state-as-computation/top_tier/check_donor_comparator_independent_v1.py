#!/usr/bin/env python3
"""Independent re-derivation checker for P11 donor comparator V1.

Recomputes the placement verdicts, challenger dispositions, resource parity and
prediction outcomes from the run receipt's raw rows using statistics.fmean and
independently written aggregation — never numpy, never the runner's code path —
and cross-checks them against the receipt and the frozen gold file.
"""

from __future__ import annotations

from collections import defaultdict
import hashlib
import json
from pathlib import Path
import statistics

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "P11_DONOR_COMPILER_COMPARATOR_PROTOCOL_V1.md"
GOLD = HERE / "p11_donor_comparator_gold_v1.json"
RUN_RECEIPT = Path("p11_donor_comparator_v1.json")

ACC_TOLERANCE = 0.02
DIM_RATIO_MAX = 0.6
COEF_RATIO_MAX = 0.65
ACC_PARITY_THRESHOLD = 0.01
DATASET_ORDER = ("breast_cancer", "wine", "digits")
CHALLENGERS = {"donor_mi": "DONOR_MI_COMPILED_LINEAR", "random_k": "RANDOM_K_COMPILED_LINEAR"}
REGISTERED = {"COMPILED_LINEAR", "UNIVERSAL_LINEAR"}


def placement_positive(ul_mean: float, ch_mean: float, ch_dim: int, ul_dim: int,
                       ch_coef: float, ul_coef: float) -> bool:
    return (
        ch_mean >= ul_mean - ACC_TOLERANCE
        and ch_dim <= DIM_RATIO_MAX * ul_dim
        and ch_coef <= COEF_RATIO_MAX * ul_coef
    )


def disposition(ch_positive: bool, reg_positive: bool) -> str:
    if ch_positive and reg_positive:
        return "BOTH_PASS"
    if ch_positive:
        return "CHALLENGER_ABOVE"
    if reg_positive:
        return "CHALLENGER_BELOW"
    return "BOTH_FAIL"


def main() -> int:
    run = json.loads(RUN_RECEIPT.read_text())
    gold = json.loads(GOLD.read_text())

    assert run["protocol"] == "P11_DONOR_COMPILER_COMPARATOR_PROTOCOL_V1"
    assert run["protocol_sha256"] == hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    assert run["gold_sha256"] == hashlib.sha256(GOLD.read_bytes()).hexdigest()

    rows_by = defaultdict(list)
    for row in run["rows"]:
        rows_by[(row["dataset"], row["arm"])].append(row)
    for dataset in DATASET_ORDER:
        for arm in ("UNIVERSAL_LINEAR", "COMPILED_LINEAR", "UNIVERSAL_FOREST",
                    "COMPILED_FOREST", "DONOR_MI_COMPILED_LINEAR",
                    "RANDOM_K_COMPILED_LINEAR"):
            assert len(rows_by[(dataset, arm)]) == 5, (dataset, arm)

    derived = {}
    positive_datasets = []
    for dataset in DATASET_ORDER:
        ul = rows_by[(dataset, "UNIVERSAL_LINEAR")]
        reg = rows_by[(dataset, "COMPILED_LINEAR")]
        ul_mean = statistics.fmean(r["accuracy"] for r in ul)
        reg_mean = statistics.fmean(r["accuracy"] for r in reg)
        ul_dim = ul[0]["state_dimension"]
        reg_dim = reg[0]["state_dimension"]
        ul_coef = statistics.fmean(
            r["model_resource"]["coefficient_count"] for r in ul
        )
        reg_coef = statistics.fmean(
            r["model_resource"]["coefficient_count"] for r in reg
        )
        reg_positive = placement_positive(
            ul_mean, reg_mean, reg_dim, ul_dim, reg_coef, ul_coef
        )
        if reg_positive:
            positive_datasets.append(dataset)

        cell = {"registered": reg_positive}
        for key, arm in CHALLENGERS.items():
            ch = rows_by[(dataset, arm)]
            ch_mean = statistics.fmean(r["accuracy"] for r in ch)
            ch_dim = ch[0]["state_dimension"]
            ch_coef = statistics.fmean(
                r["model_resource"]["coefficient_count"] for r in ch
            )
            ch_positive = placement_positive(
                ul_mean, ch_mean, ch_dim, ul_dim, ch_coef, ul_coef
            )
            cell[key] = {
                "positive": ch_positive,
                "disposition": disposition(ch_positive, reg_positive),
                "accuracy_parity_within_threshold": bool(
                    abs(ch_mean - reg_mean) <= ACC_PARITY_THRESHOLD
                ),
            }
        derived[dataset] = cell

    # EP1 hard gate: registered result reproduced.
    ep1_expected = gold["ep1_reproduction"]["expected_positive_datasets"]
    assert positive_datasets == ep1_expected, positive_datasets
    assert run["positive_datasets"] == ep1_expected
    assert run["terminal"] == "P11_DONOR_COMPARATOR_V1_SUPPORTED"

    # Cross-check receipt dispositions against the independent derivation.
    for dataset in DATASET_ORDER:
        for key, arm in CHALLENGERS.items():
            receipt_disp = run["summaries"][dataset][f"{key}_disposition"]
            assert receipt_disp in gold["disposition_vocabulary"]
            assert receipt_disp == derived[dataset][key]["disposition"], (
                dataset, key, receipt_disp, derived[dataset][key]["disposition"]
            )
            assert (
                run["summaries"][dataset][f"{key}_placement_positive"]
                == derived[dataset][key]["positive"]
            )
            assert (
                run["summaries"][dataset][f"{key}_accuracy_parity_within_threshold"]
                == derived[dataset][key]["accuracy_parity_within_threshold"]
            )

    # EP4 resource parity, recomputed from the selections records.
    per_fold = defaultdict(dict)
    for entry in run["selections"]:
        per_fold[(entry["dataset"], entry["fold"])][entry["selector"]] = entry
    assert len(per_fold) == 15
    for (dataset, fold), selectors in sorted(per_fold.items()):
        assert set(selectors) == {"f_classif", "mutual_info", "random_k"}
        proxies = {e["compiler_fit_proxy"] for e in selectors.values()}
        assert len(proxies) == 1, (dataset, fold, proxies)
        mi = selectors["mutual_info"]
        assert mi["mi_estimator_calls"] >= 1
        assert mi["mi_nn_distance_evals_proxy"] >= mi["mi_estimator_calls"]
        assert sorted(mi["selected_features"]) == mi["selected_features"]

    # Prediction outcomes must be tracked against the frozen gold cells.
    for role, gold_key in (("donor_mi", "ep2_donor_predictions"),
                           ("random_k", "ep3_random_k_predictions")):
        for dataset in DATASET_ORDER:
            tracked = run["prediction_outcomes"][role][dataset]
            predicted = gold[gold_key][dataset]
            observed = run["summaries"][dataset][f"{role}_disposition"]
            expected_outcome = (
                "WITHHELD"
                if predicted == "CANNOT_CHECK_PREDICTION"
                else ("CONFIRMED" if observed == predicted else "CORRECTED")
            )
            assert tracked == {
                "predicted": predicted,
                "observed": observed,
                "outcome": expected_outcome,
            }, (role, dataset, tracked)

    payload = {
        "checker": "P11_DONOR_COMPARATOR_INDEPENDENT_V1",
        "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "run_receipt_sha256": run["receipt_sha256"],
        "positive_datasets": positive_datasets,
        "derived_dispositions": {
            dataset: {
                key: derived[dataset][key]["disposition"] for key in CHALLENGERS
            }
            for dataset in DATASET_ORDER
        },
        "prediction_outcomes": run["prediction_outcomes"],
        "terminal": "P11_DONOR_COMPARATOR_V1_INDEPENDENT_GREEN",
    }
    print(json.dumps(payload, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())