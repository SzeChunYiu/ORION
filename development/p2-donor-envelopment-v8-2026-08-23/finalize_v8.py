#!/usr/bin/env python3
"""Derive the V8 scientific adjudication and human-readable receipts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parent
ADJUDICATED_TERMINAL = (
    "P2_V8_DONOR_ENVELOPMENT_CROSSFIT_FAILS_CRE20_WSS95_AND_HARM__"
    "NO_RESIDUAL_ADMITTED__EXACT_U4_FALLBACK"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(name: str, value: Any) -> None:
    (ROOT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def fmt(value: float) -> str:
    return f"{value:+.12f}"


def main() -> None:
    result = json.loads((ROOT / "RESULT_V8.json").read_text())
    reviews = tuple(result["nested_loro_by_held_out_review"])
    configs = tuple(result["configuration_meta"])
    grid = result["complete_development_grid"]
    aggregate = result["cross_fitted_aggregate"]

    config_summary: dict[str, Any] = {}
    for config in configs:
        deltas = [grid[review][config]["delta_vs_u4"] for review in reviews]
        config_summary[config] = {
            "mean_delta_cre20": float(np.mean([item["cre20"] for item in deltas])),
            "mean_delta_r10": float(np.mean([item["recall_at_010"] for item in deltas])),
            "mean_delta_wss95": float(np.mean([item["wss_at_95"] for item in deltas])),
            "worst_review_delta_r10": min(item["recall_at_010"] for item in deltas),
            "full_fourteen_support_passed": (
                float(np.mean([item["cre20"] for item in deltas])) > 0
                and float(np.mean([item["wss_at_95"] for item in deltas])) >= 0
                and min(item["recall_at_010"] for item in deltas) >= -0.05
            ),
        }

    support_fold_counts = {config: 0 for config in configs}
    for receipt in result["nested_loro_by_held_out_review"].values():
        for config, support in receipt["support_by_configuration"].items():
            support_fold_counts[config] += int(support["passed"])

    selected_harm = {
        review: {
            "selected": receipt["selected"],
            "delta_cre20": receipt["held_out_delta_vs_u4"]["cre20"],
            "delta_r10": receipt["held_out_delta_vs_u4"]["recall_at_010"],
            "delta_wss95": receipt["held_out_delta_vs_u4"]["wss_at_95"],
        }
        for review, receipt in result["nested_loro_by_held_out_review"].items()
        if not receipt["exact_u4_fallback"]
    }

    adjudication = {
        "identity": "P2_KIFMS_V8_POST_EXECUTION_SCIENTIFIC_ADJUDICATION",
        "status": "POST_EXECUTION_CLASSIFICATION__NOT_A_RETROACTIVE_PROTOCOL_FREEZE",
        "execution_terminal": result["terminal"],
        "adjudicated_terminal": ADJUDICATED_TERMINAL,
        "result_sha256": sha256(ROOT / "RESULT_V8.json"),
        "binding_passed": result["binding_receipt"]["passed"],
        "u4_identity_passed_all_reviews": result["u4_identity_passed_all_reviews"],
        "cross_fitted_aggregate": aggregate,
        "full_grid_configuration_summary": config_summary,
        "support_fold_counts": support_fold_counts,
        "nonfallback_held_out_failures": selected_harm,
        "interpretation": {
            "selector_activation": "A residual passed the other-thirteen rule in two of fourteen outer folds.",
            "exclusion_fragility": "In both activations, the held-out review was itself adverse for the selected residual; removing the harmed unit made the residual appear supported.",
            "admission": "No residual is admitted. The exact u4 fallback is the only V8 output eligible to be frozen while a source-disjoint discriminator is acquired.",
            "positive_diagnostic": "Title emphasis improved full-grid mean CRE20 and WSS95, but its -0.0625 worst-review R@10 violated the unchanged -0.05 harm floor.",
        },
        "claims_not_authorized": [
            "KIFMS confirmation or independent custody",
            "a safe or superior donor-envelopment controller",
            "source-general residual benefit",
            "relaxation of the V7 harm floor",
        ],
    }
    write_json("SCIENTIFIC_ADJUDICATION_V8.json", adjudication)

    negatives = {
        "identity": "P2_KIFMS_V8_NEGATIVE_RESULT_LEDGER",
        "terminal": ADJUDICATED_TERMINAL,
        "entries": [
            {
                "id": "V8-N1",
                "finding": "Nested-LORO cross-fitted mean CRE20 did not improve on exact u4.",
                "value": aggregate["mean_delta_vs_u4"]["cre20"],
                "next_discriminator": "Test the single strongest bounded residual on a source-disjoint family without KIFMS retuning.",
            },
            {
                "id": "V8-N2",
                "finding": "Nested-LORO cross-fitted relative WSS95 was negative.",
                "value": aggregate["mean_delta_vs_u4"]["wss_at_95"],
                "next_discriminator": "Retain WSS95 as noncompensatory; no CRE20 gain may pay for extra screening work.",
            },
            {
                "id": "V8-N3",
                "finding": "Worst held-out R@10 harm was far below the unchanged -0.05 floor.",
                "value": aggregate["worst_review_delta_r10"],
                "review": "Shoulderdystocia_positioning",
                "selected": "F1_WORD_PRUNED_A100",
                "next_discriminator": "Require source-disjoint worst-review harm and retain exact u4 fallback.",
            },
            {
                "id": "V8-N4",
                "finding": "The selector fell back to exact u4 in twelve of fourteen folds; both nonfallback selections were adverse on their held-out review.",
                "fallback_count": aggregate["fallback_count"],
                "fallback_fraction": aggregate["fallback_fraction"],
                "nonfallback_failures": selected_harm,
                "next_discriminator": "Treat exclusion-sensitive support as a target, not as positive selection evidence.",
            },
            {
                "id": "V8-N5",
                "finding": "None of the six configurations passed CRE20, WSS95, and worst-review R@10 support jointly over all fourteen development reviews.",
                "configuration_summary": config_summary,
                "next_discriminator": "Carry only the most scientifically informative title-emphasis configuration as a diagnostic into a source-disjoint family.",
            },
            {
                "id": "V8-N6",
                "finding": "KIFMS is open same-workspace development data and cannot provide confirmation or independent custody.",
                "next_discriminator": "Acquire and freeze a lawful source-disjoint family before its labels or comparative outcomes are opened.",
            },
        ],
    }
    write_json("NEGATIVE_RESULT_LEDGER_V8.json", negatives)

    next_discriminator = {
        "identity": "P2_V9_SOURCE_DISJOINT_TITLE_RESIDUAL_STABILITY_DISCRIMINATOR",
        "parent_terminal": ADJUDICATED_TERMINAL,
        "scientific_question": "Does the bounded title-emphasis residual transport without the exclusion-sensitive R@10 harm seen on KIFMS?",
        "source": {
            "requirement": "A lawful public review family disjoint in named review identity and normalized title-abstract content from SWIFT, SYNERGY V5, and KIFMS V7.",
            "unit_rule": "Predeclare every available eligible review; no outcome-based unit deletion.",
            "status": "SOURCE_IDENTITY_AND_OUTCOME_CUSTODY_NOT_YET_BOUND"
        },
        "frozen_development_choice": {
            "controller": "unchanged u4 plus F2_TITLE_EMPHASIS at alpha=0.25",
            "why_this_one": "It had the largest full-grid mean CRE20 delta (+0.010693125060) while retaining positive mean WSS95 (+0.002042792819); its -0.0625 KIFMS harm is the explicit falsifier, not hidden.",
            "comparators": [
                "unchanged exact u4",
                "F2 title-emphasis representation alone with the same u4 learner/balancer",
                "u4 plus the frozen alpha=0.25 residual"
            ],
            "fallback": "Exact u4 whenever source binding, both-class execution, or the frozen controller cannot be reproduced."
        },
        "unchanged_gates": {
            "mean_delta_CRE20": ">= 0.010858985820770889",
            "mean_delta_R10": ">= 0.010858985820770889",
            "positive_sign_fraction_each_coprimary": ">= 6/7 of all predeclared review units, the unchanged 12/14 fraction",
            "mean_delta_WSS95": ">= 0",
            "worst_review_delta_R10": ">= -0.05",
            "absolute_work_saving": "controller WSS95 > 0 in every review"
        },
        "interpretation": {
            "all_gates_pass": "Source-disjoint development transport of this one residual only; KIFMS remains adverse and independent confirmation remains required.",
            "any_gate_fails": "Discard title emphasis as a donor-envelopment residual and retain exact u4; recurse on a new mechanism rather than relax thresholds.",
            "mixed_family_result": "A positive new family cannot overwrite the KIFMS harm; it identifies review-family heterogeneity requiring a separately frozen gate."
        },
        "forbidden": [
            "KIFMS retuning after the source-disjoint outcomes",
            "review deletion",
            "threshold relaxation",
            "claiming independent confirmation from same-workspace execution",
            "averaging away a worst-review harm failure"
        ]
    }
    write_json("NEXT_DISCRIMINATOR_V9.json", next_discriminator)

    report_lines = [
        "# P2 V8 donor-envelopment nested-LORO development study",
        "",
        "## Exact adjudicated terminal",
        "",
        f"`{ADJUDICATED_TERMINAL}`",
        "",
        "The execution-level terminal records that a residual activated in at least one outer fold. "
        "Post-execution scientific adjudication is adverse: the cross-fitted controller failed CRE20, "
        "relative WSS95, and worst-review R@10. This classification is not represented as a retroactive protocol freeze.",
        "",
        "## Design",
        "",
        "The exact V7 `R1_L1` u4 arm was reconstructed with identical metrics and order hashes in all 14 reviews. "
        "Three representation-only residual families, each at alpha 0.10 and 0.25, were evaluated. For each held-out "
        "review, only the other 13 reviews could support a configuration; otherwise the emitted order was exact u4.",
        "",
        "## Cross-fitted result",
        "",
        "| Quantity | Result |",
        "|---|---:|",
        f"| Mean delta CRE20 | {fmt(aggregate['mean_delta_vs_u4']['cre20'])} |",
        f"| Mean delta R@10 | {fmt(aggregate['mean_delta_vs_u4']['recall_at_010'])} |",
        f"| Mean delta WSS95 | {fmt(aggregate['mean_delta_vs_u4']['wss_at_95'])} |",
        f"| Worst-review delta R@10 | {fmt(aggregate['worst_review_delta_r10'])} |",
        f"| Exact-u4 fallbacks | {aggregate['fallback_count']}/14 ({aggregate['fallback_fraction']:.1%}) |",
        "",
        "No held-out review had a strictly positive CRE20 or R@10 delta after nested selection. The two nonfallback "
        "activations were precisely exclusion-fragile: removing a harmed review made the residual pass on the remaining 13, "
        "then the residual harmed that held-out review.",
        "",
        "| Held-out review | Selected residual | Delta CRE20 | Delta R@10 | Delta WSS95 |",
        "|---|---|---:|---:|---:|",
    ]
    for review, values in selected_harm.items():
        report_lines.append(
            f"| {review} | `{values['selected']}` | {fmt(values['delta_cre20'])} | "
            f"{fmt(values['delta_r10'])} | {fmt(values['delta_wss95'])} |"
        )
    report_lines.extend(
        [
            "",
            "## Residual diagnosis",
            "",
            "| Configuration | Mean delta CRE20 | Mean delta R@10 | Mean delta WSS95 | Worst delta R@10 | Full support |",
            "|---|---:|---:|---:|---:|---|",
        ]
    )
    for config, values in config_summary.items():
        report_lines.append(
            f"| `{config}` | {fmt(values['mean_delta_cre20'])} | {fmt(values['mean_delta_r10'])} | "
            f"{fmt(values['mean_delta_wss95'])} | {fmt(values['worst_review_delta_r10'])} | "
            f"{str(values['full_fourteen_support_passed']).lower()} |"
        )
    report_lines.extend(
        [
            "",
            "Title emphasis is the only family with positive full-grid mean CRE20 and WSS95 at both strengths, but its "
            "worst-review R@10 delta is -0.0625, below the unchanged -0.05 floor. Character morphology at alpha 0.10 "
            "has nonnegative worst-review R@10 but loses CRE20 and WSS95. No configuration jointly closes the frontier.",
            "",
            "## Boundary and next discriminator",
            "",
            "KIFMS is open same-workspace development data, not confirmation or independent custody. No residual is "
            "admitted and no V7 threshold is relaxed. `NEXT_DISCRIMINATOR_V9.json` carries exactly one bounded diagnostic, "
            "title emphasis at alpha 0.25, to a lawful source-disjoint family with unchanged coprimary, work-saving, harm, "
            "and absolute-efficiency gates. A positive new-family result cannot overwrite KIFMS harm; a failure retires this residual.",
            "",
        ]
    )
    (ROOT / "RESULT_REPORT_V8.md").write_text("\n".join(report_lines))

    ledger_lines = [
        "# P2 V8 negative-result ledger",
        "",
        f"Terminal: `{ADJUDICATED_TERMINAL}`",
        "",
    ]
    for entry in negatives["entries"]:
        ledger_lines.extend(
            [
                f"## {entry['id']}",
                "",
                entry["finding"],
                "",
                f"**Next discriminator:** {entry['next_discriminator']}",
                "",
            ]
        )
    (ROOT / "NEGATIVE_RESULT_LEDGER_V8.md").write_text("\n".join(ledger_lines))


if __name__ == "__main__":
    main()
