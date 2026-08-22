"""Audit P11G's survived hostile attack for a defeat the protocol could have produced.

Reproduces the committed scientific payload digest, runs P11G's four scientific
gates against the worlds its freeze admits, asks separately whether the arm
responds at all in worlds it does not, transplants P11C's frozen best-of-arms
rule onto P11G's own frozen data, and asks whether the record declares the arm
axis that transplant exposes.

Two of those readings roll up. The attainability verdict does, because a
survived attack with no reachable win is not evidence. The disclosure verdict
does, because a receipt that carries a verdict-changing axis with one value
reads as a claim about the decoder family when it is a claim about the arm
placed in the gate. The transplanted rule does **not**: P11C ran to completion
and applied its own rule to its own data, and
:func:`orion.study.p11.decoder_attack_reach.rule_binding` reads the two freezes
against each other and finds a different gate, a different ladder and a
different claim. A rule from one protocol does not bind another, so the reading
is reported as the measurement of the arm axis that it is.

Exits ``3`` when anything blocks, so it fails a pipeline rather than printing a
table nobody reads::

    python -m orion.study.p11.attack_audit
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Sequence

from orion.programme.records import Outcome
from orion.study.p11 import decoder_attack_reach as p11


def audit_p11g_attack_terminal() -> dict[str, Any]:
    """Measure the survived attack, and roll the verdicts up without compensation."""

    digest = p11.require_fidelity()
    terminal = p11.terminal_reach()
    responsiveness = p11.attack_responsiveness()
    axis = p11.arm_axis()
    binding = p11.rule_binding()

    # The transplanted rule is a reading, not a verdict on P11G. It is retained
    # verbatim -- nothing here drops an arm or moves a threshold -- and what
    # changed is which protocol it is read against. `binding` carries the freeze
    # text that decides that, and raises if either freeze stops saying it.
    transplanted_gate = p11.best_of_arms_gate()

    # What does roll up is the axis that reading exposes. A verdict-changing
    # axis carried in the receipt with one value owes the record a declaration
    # of every registered value; `arm_disclosure_gaps` is empty only when it has
    # one, and it is non-empty again the moment a future receipt publishes
    # another such axis.
    gaps = p11.arm_disclosure_gaps()
    disclosure_outcome = Outcome.FAIL if gaps else Outcome.PASS

    # Responsiveness is reported and does not roll up: it is the half that
    # clears the arm, and letting a PASS there offset an unreachable defeat
    # would be the compensation `worst_outcome` exists to refuse.
    outcome = Outcome.PASS
    for other in (terminal.outcome, disclosure_outcome):
        if other.blocks and not outcome.blocks:
            outcome = other

    return {
        "scientific_sha256": digest,
        "curves_reproduced": p11.shipped_curves_match(),
        "terminal_reach": terminal,
        "responsiveness": responsiveness,
        "arm_axis": axis,
        "rule_binding": binding,
        "best_of_arms_thresholds": p11.best_of_arms_thresholds(),
        "transplanted_rule_gate": transplanted_gate,
        "terminal_under_arm": {
            arm: p11.terminal_under_arm(arm) for arm in p11.REGISTERED_UNIVERSAL_ARMS
        },
        "one_value_decision_axes": p11.one_value_decision_axes(),
        "arm_disclosure_gaps": gaps,
        "disclosure_outcome": disclosure_outcome,
        "decoder_family_share": p11.decoder_family_share(),
        "outcome": outcome,
    }


def report_as_json(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "scientific_sha256": report["scientific_sha256"],
        "curves_reproduced": report["curves_reproduced"],
        "terminal_reach": report["terminal_reach"].as_json(),
        "responsiveness": report["responsiveness"].as_json(),
        "arm_axis": report["arm_axis"].as_json(),
        "rule_binding": report["rule_binding"].as_json(),
        "best_of_arms_thresholds": list(report["best_of_arms_thresholds"]),
        "transplanted_rule_gate": report["transplanted_rule_gate"],
        "terminal_under_arm": report["terminal_under_arm"],
        "one_value_decision_axes": [dict(row) for row in report["one_value_decision_axes"]],
        "arm_disclosure_gaps": list(report["arm_disclosure_gaps"]),
        "disclosure_outcome": report["disclosure_outcome"].value,
        "decoder_family_share": [dict(row) for row in report["decoder_family_share"]],
        "outcome": report["outcome"].value,
    }


def _render(report: dict[str, Any]) -> str:
    terminal = report["terminal_reach"]
    responsiveness = report["responsiveness"]
    axis = report["arm_axis"]
    binding = report["rule_binding"]
    lines = [
        f"P11G hostile tree decoder ({p11.SHIPPED_TERMINAL})",
        "",
        f"  shipped scientific payload sha256: {report['scientific_sha256']}",
        f"  published curve values reproduced: {report['curves_reproduced']}",
        "",
        f"  {terminal.label}",
        f"    admissible worlds registered: {len(terminal.world_ids)}",
        f"    worlds clearing every gate: {len(terminal.clearing)}",
        f"    reachable terminals: {terminal.distinct_terminals}",
        f"    no admissible world satisfies: {', '.join(terminal.unattainable) or 'none'}",
        f"    every admissible world satisfies: {', '.join(terminal.unconditional) or 'none'}",
        "",
        "    gate                              nearest refutation   outcome",
    ]
    for reach in terminal.reaches:
        lines.append(
            f"    {reach.gate.gate_id:<32} {p11.closest_refuting_margin(reach):+18.6f}   "
            f"{reach.outcome.value}"
        )
    lines += [
        "",
        f"  {responsiveness.label} (banks the protocol does not admit)",
        f"    baseline verdict: {responsiveness.baseline_verdict}",
        f"    distinct verdicts over the register: {len(responsiveness.verdicts_observed)}",
        f"    cases the verdict ignored: "
        f"{len(responsiveness.unmoved)}/{responsiveness.exercise.opportunities}",
        f"    outcome: {responsiveness.outcome.value} ({responsiveness.assessment.reason.value})",
        "",
        "  the pool P11C froze, transplanted onto P11G's own frozen data",
        f"    best-of-arms thresholds per cell: {list(report['best_of_arms_thresholds'])} "
        f"(P11G's gate wants >= {p11.GATE_THRESHOLD_SIZE})",
    ]
    for arm, value in report["terminal_under_arm"].items():
        lines.append(f"    {arm:<24} -> {value}")
    lines += [
        f"    decoder_arm axis: {axis.values} values, {axis.comparable_pairs} comparable pairs, "
        f"{axis.verdict_changing_pairs} verdict-changing, inert: {axis.inert}",
        f"    transplanted rule leaves P11G's gate standing: {report['transplanted_rule_gate']}",
        "",
        f"  {binding.label}",
        f"    P11C applied it to its own frozen data: {binding.applied_to_its_own_data} "
        f"-> thresholds {list(binding.p11c_best_of_arms_thresholds)}, "
        f"gate {binding.p11c_gate}, {binding.p11c_terminal}",
    ]
    for divergence in binding.divergences:
        lines += [
            f"    {divergence.aspect}",
            f"      P11C: {divergence.p11c.text}",
            f"      P11G: {divergence.p11g.text}",
        ]
    lines.append("    the programme's own non-crossing rule")
    for quote in binding.non_crossing:
        lines.append(f"      {quote.source}: {quote.text}")
    lines += [
        "",
        "  decision axes the terminal depends on, carried in the receipt with one value",
    ]
    if report["one_value_decision_axes"]:
        for entry in report["one_value_decision_axes"]:
            lines.append(
                f"    {entry['axis']}: registered {entry['registered_values']}, "
                f"published {entry['values_in_receipt']}"
            )
    else:
        lines.append("    none")
    lines += [
        f"    declared in {p11.ARM_PLACEMENT_ADJUDICATION.name}: "
        f"{not report['arm_disclosure_gaps']}",
    ]
    for gap in report["arm_disclosure_gaps"]:
        lines.append(f"      undeclared: {gap}")
    lines += [
        f"    disclosure outcome: {report['disclosure_outcome'].value}",
        "",
        "  decoder-family share of the published n=64 gap",
    ]
    for row in report["decoder_family_share"]:
        share = row["decoder_family_share"]
        lines.append(
            f"    {row['cell']}: published {row['published_gap_at_64']:.4f} = decoder "
            f"{row['decoder_family_gap_at_64']:.4f} + state {row['representation_gap_at_64']:.4f}"
            + (f"  ({share:.1%} decoder / {1 - share:.1%} state)" if share is not None else "")
        )
    lines += ["", f"  outcome: {report['outcome'].value}"]
    return "\n".join(lines)


def main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit the audit as JSON")
    args = parser.parse_args(argv)

    report = audit_p11g_attack_terminal()
    payload = report_as_json(report)
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else _render(report))
    return 3 if Outcome(payload["outcome"]).blocks else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
