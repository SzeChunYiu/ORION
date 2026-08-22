"""Audit P9's shipped D1 transfer margins for a comparator that answered the cases.

Scores the three published differences against the arms they name, re-scores the
frozen predictions on re-composed protected splits, measures how many protected
cases each view can still tell apart once its vocabulary is fixed, and asks
whether the ``D1_EVALUATOR_FAILURE`` branch could ever be taken.

Two of those measurements report a *number that has more than one cause*, and
this audit exists to say which cause, because the number alone reads as a result
either way.

``N of M protected feature keys survive the fitted vocabulary`` is the first. A
key can be missing because the vocabulary was fitted on other domains --- which
more or better training data fixes --- or because the key space is minted per
instance, which no corpus could ever have covered. The two are told apart by
refitting the vocabulary on a same-size corpus the same generator draws from the
protected split's *own* domain, and the audit reports how many keys that
restores rather than leaving the reader to guess.

``points N, divergent 0`` between the exact typed relational comparator and
evaluator gold is the second, and it has three causes: the comparator is gold,
it reads gold, or it is being asked on a space where nothing could differ. It is
the first. The comparator is
:func:`orion.study.p9.d1.classify_methods` re-expressed through the typed
projection --- same eight coordinates, same precedence --- so the audit reports
it as an identity and reports ``D1_EVALUATOR_FAILURE`` as unreachable for the
artifact as run, instead of printing an agreement it could not have failed to
find. That the branch would still reject six declared-wrong comparators is
reported beside it, because "the check is vacuous" and "the check was pointed at
its own reference" are different repairs.

Reporting the identity does not answer the branch's question, so the audit then
asks it. ``orion.study.p9.transfer_margins.protocol_declared_comparator`` decides
the same pairs from D1's *declared* surface --- the comparison coordinates and
labels of ``D1_PROTOCOL_V1.json``, the per-coordinate comparison semantics of
``D1_PROTOCOL_V1_1.json``, the ``P9.D1Typed.v1`` payload --- without calling the
evaluator's rule, and it disagrees with the shipped comparator on 384 of the
1,280 pairs the D1 generator never builds. Because it *can* disagree, its
agreement with gold on all 512 frozen and all 128 protected cases is a
measurement: the branch is reachable for a conforming comparator and does not
fire. The 384 are printed with the shape that causes them, because they are a
finding about D1's evaluator --- it grades a coordinate carrying no value as a
decided obstruction --- and not a defect in the second implementation.

Exits ``3`` when anything blocks, so it fails a pipeline rather than printing a
table nobody reads::

    python -m orion.study.p9.transfer_audit
"""

from __future__ import annotations

import argparse
import json
from typing import Any, Sequence

from orion.programme.guard_exercise import worst_outcome
from orion.programme.records import Outcome
from orion.study.p9 import transfer_margins as p9


def audit_p9_transfer_margins() -> dict[str, Any]:
    """Measure every published D1 margin, and roll the verdicts up without compensation."""

    result = p9.load_shipped_d1_result()
    # First, because every number below is about a regenerated corpus and this is
    # the only thing that says it is the corpus the result was produced on.
    provenance = p9.d1_dataset_provenance()
    margins = p9.d1_contrast_margins(result)
    sensitivity = p9.d1_composition_sensitivity(result)
    collapse = p9.d1_view_collapse_report()
    reproduction = p9.d1_reproduction_report(result)
    oracle = p9.d1_oracle_identity()
    independence = p9.d1_independent_oracle()

    # Four verdicts that must stay separable, because they have four different
    # repairs: a margin taken against an arm that never answered, a view whose
    # protected design matrix has one row, a terminal branch whose trigger
    # recomputes the gold it grades, and the claim that branch would have made if
    # a comparator able to deny it had been the one grading.
    oracle_outcome = oracle.outcome
    independence_outcome = independence.outcome
    outcome = worst_outcome(tuple(item.assessment for item in margins))
    others = (
        *(item.outcome for item in margins),
        *(item.outcome for item in collapse.values()),
        *(item.outcome for item in reproduction.values()),
        oracle_outcome,
        independence_outcome,
    )
    for other in others:
        if other is Outcome.FAIL:
            outcome = other
            break
        if other.blocks and not outcome.blocks:
            outcome = other

    return {
        "result_digest": result["result_digest"],
        "terminal": result["terminal"],
        "dataset_provenance": provenance,
        "reproduction": reproduction,
        "margins": margins,
        "sensitivity": sensitivity,
        "view_collapse": collapse,
        "oracle": oracle,
        "oracle_outcome": oracle_outcome,
        "independence": independence,
        "independence_outcome": independence_outcome,
        "outcome": outcome,
    }


def report_as_json(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_digest": report["result_digest"],
        "terminal": report["terminal"],
        "margins": [item.as_json() for item in report["margins"]],
        "sensitivity": {
            arm: item.as_json() for arm, item in sorted(report["sensitivity"].items())
        },
        "view_collapse": {
            view: item.as_json() for view, item in sorted(report["view_collapse"].items())
        },
        "dataset_provenance": report["dataset_provenance"],
        "reproduction": {
            arm: item.as_json() for arm, item in sorted(report["reproduction"].items())
        },
        "oracle": report["oracle"].as_json(),
        "oracle_outcome": report["oracle_outcome"].value,
        "independence": report["independence"].as_json(),
        "independence_outcome": report["independence_outcome"].value,
        "outcome": report["outcome"].value,
    }


def _render(report: dict[str, Any]) -> str:
    lines = [
        "P9 D1 transfer margins",
        f"  archive {report['result_digest']} -> {report['terminal']}",
        f"  dataset {report['dataset_provenance']['measured_dataset_manifest_digest']}"
        f" (shipped digest reproduced:"
        f" {report['dataset_provenance']['measured_dataset_manifest_digest'] == report['dataset_provenance']['shipped_dataset_manifest_digest']})",
        "  protocol v1.2's generator correction is installed by an import, so this"
        " module installs it explicitly and fails closed on the digest;",
        "  it was not installed when this audit was entered:"
        f" {not report['dataset_provenance']['v12_generator_installed_before_this_call']}",
        "",
    ]
    for margin in report["margins"]:
        comparator = margin.comparator
        lines.extend(
            [
                f"  {margin.label}",
                f"    published margin: {margin.published_margin}"
                f"  earned: {margin.earned_margin}"
                f"  prior-supplied: {margin.prior_supplied}",
                f"    informedness margin: {margin.informedness_margin}",
                f"    {comparator.arm_id}: accuracy {comparator.accuracy}, "
                f"{comparator.distinct_predictions} distinct prediction(s), "
                f"informedness {comparator.informedness}",
                f"    departures from its own modal answer: "
                f"{comparator.departures}/{comparator.eval_cases}",
                f"    outcome: {margin.outcome.value} ({margin.reason.value})",
                "",
            ]
        )
    for arm, item in sorted(report["sensitivity"].items()):
        lines.append(
            f"  {arm} over {item.compositions} re-composed splits: "
            f"published margin [{item.published_margin_low}, {item.published_margin_high}], "
            f"informedness margin [{item.informedness_margin_low}, "
            f"{item.informedness_margin_high}]"
        )
    lines.append("")
    for view, item in sorted(report["view_collapse"].items()):
        lines.extend(
            [
                f"  {view}: {item.test_keys_in_train_vocabulary}/{item.test_keys} "
                f"protected feature keys survive the fitted vocabulary, leaving "
                f"{item.distinct_protected_rows} distinct protected row(s)",
                f"    in-domain refit ({item.in_domain_train_rows} rows of the protected "
                f"domain): {item.test_keys_in_in_domain_vocabulary}/{item.test_keys} keys, "
                f"{item.distinct_protected_rows_in_domain} distinct row(s), "
                f"{item.restored_by_in_domain_refit} key(s) restored",
                f"    outcome: {item.outcome.value} ({item.reason.value})",
                f"    {item.mechanism}",
            ]
        )
    lines.append("")
    lines.append("  re-running the frozen protocol and comparing to the archive")
    for arm, item in sorted(report["reproduction"].items()):
        lines.extend(
            [
                f"    {arm}: {item.outcome.value} ({item.reason.value})",
                f"      {item.detail}",
            ]
        )
    oracle = report["oracle"]
    capacity = oracle.capacity
    lines.extend(
        [
            "",
            f"  {oracle.comparator_id}",
            f"    frozen D1 space: {oracle.frozen_space.points} points, "
            f"{oracle.frozen_space.points_changed} divergent",
            f"    protected split: {oracle.protected_space.points} points, "
            f"{oracle.protected_space.points_changed} divergent",
            f"    pairs the D1 generator never builds: {oracle.widened_space.points} points "
            f"over {len(oracle.widened_gold_labels)} gold labels, "
            f"{oracle.widened_space.points_changed} divergent",
            f"    reads {len(oracle.comparator_read_coordinates)} of "
            f"{len(oracle.compared_coordinates)} coordinates the evaluator compares",
            f"    {oracle.branch} would still reject {len(capacity.refuted)}/"
            f"{len(capacity.refuted) + len(capacity.survivors)} declared wrong "
            f"comparators ({capacity.outcome.value})",
            f"    {oracle.branch} reachable for the artifact as run: "
            f"{oracle.branch_reachable}",
            f"    outcome: {report['oracle_outcome'].value} ({oracle.verdict.value})",
        ]
    )
    independence = report["independence"]
    witness = independence.witness
    lines.extend(
        [
            "",
            f"  {independence.comparator_id} vs D1 evaluator gold",
            f"    frozen D1 space: {independence.frozen_space.points} points, "
            f"{independence.frozen_space.points_changed} divergent",
            f"    protected split: {independence.protected_space.points} points, "
            f"{independence.protected_space.points_changed} divergent",
            f"    pairs the D1 generator never builds: "
            f"{independence.widened_space.points} points, "
            f"{independence.widened_space.points_changed} divergent",
            "    disagrees with the comparator the artifact ran on "
            f"{independence.against_shipped_comparator.points_changed} of "
            f"{independence.against_shipped_comparator.points} of those points, so it "
            "is a second implementation and not a second expression",
        ]
    )
    for pair, count in independence.divergent_label_pairs:
        lines.append(
            f"      evaluator {pair[0]} where the declaration reads {pair[1]}: "
            f"{count} point(s)"
        )
    if witness:
        lines.append(
            f"      witness {witness['instance_id']}: perturbed "
            f"{witness['perturbed_coordinates']}, evaluator "
            f"{witness['evaluator_gold']}, declaration {witness['protocol_declared']}"
        )
        for entry in witness["coordinates_carrying_no_value"]:
            lines.append(
                f"        {entry['side']}.{entry['coordinate']} carries no value and is "
                f"not marked unknown (marked_unknown={entry['marked_unknown']})"
            )
    capacity = independence.capacity
    lines.extend(
        [
            f"    {independence.branch} would still reject {len(capacity.refuted)}/"
            f"{len(capacity.refuted) + len(capacity.survivors)} declared wrong "
            f"comparators when graded against it ({capacity.outcome.value})",
            f"    {independence.branch} reachable for a conforming comparator: "
            f"{independence.branch_reachable}; fires on the shipped protected split: "
            f"{independence.branch_fires}",
            f"    outcome: {report['independence_outcome'].value} "
            f"({independence.verdict.value})",
            f"    {independence.divergence_shape}",
            "",
            f"  audit outcome: {report['outcome'].value}",
        ]
    )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit the audit as JSON")
    args = parser.parse_args(argv)

    report = audit_p9_transfer_margins()
    payload = report_as_json(report)
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else _render(report))
    return 3 if Outcome(payload["outcome"]).blocks else 0


if __name__ == "__main__":
    raise SystemExit(main())
