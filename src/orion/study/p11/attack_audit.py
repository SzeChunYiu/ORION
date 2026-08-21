"""Audit P11G's survived hostile attack for a defeat the protocol could have produced.

Reproduces the committed scientific payload digest, runs P11G's four scientific
gates against the worlds its freeze admits, asks separately whether the arm
responds at all in worlds it does not, and applies P11C's own frozen
best-of-arms rule to P11G's own frozen data.

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

    # The pool verdict is not a guard assessment. A protocol that froze three
    # arms and a combination rule, then gated on one arm, has an unapplied rule
    # rather than a missing denominator, so it is read as its own boolean:
    # P11C's rule on P11G's data either leaves the gate standing or does not.
    pool_outcome = Outcome.PASS if p11.best_of_arms_gate() else Outcome.FAIL

    # Responsiveness is reported and does not roll up: it is the half that
    # clears the arm, and letting a PASS there offset an unreachable defeat
    # would be the compensation `worst_outcome` exists to refuse.
    outcome = Outcome.PASS
    for other in (terminal.outcome, pool_outcome):
        if other.blocks and not outcome.blocks:
            outcome = other

    return {
        "scientific_sha256": digest,
        "curves_reproduced": p11.shipped_curves_match(),
        "terminal_reach": terminal,
        "responsiveness": responsiveness,
        "arm_axis": axis,
        "best_of_arms_thresholds": p11.best_of_arms_thresholds(),
        "pool_outcome": pool_outcome,
        "terminal_under_arm": {
            arm: p11.terminal_under_arm(arm) for arm in p11.REGISTERED_UNIVERSAL_ARMS
        },
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
        "best_of_arms_thresholds": list(report["best_of_arms_thresholds"]),
        "pool_outcome": report["pool_outcome"].value,
        "terminal_under_arm": report["terminal_under_arm"],
        "decoder_family_share": [dict(row) for row in report["decoder_family_share"]],
        "outcome": report["outcome"].value,
    }


def _render(report: dict[str, Any]) -> str:
    terminal = report["terminal_reach"]
    responsiveness = report["responsiveness"]
    axis = report["arm_axis"]
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
        "  the pool P11C froze, applied to P11G's own frozen data",
        f"    best-of-arms thresholds per cell: {list(report['best_of_arms_thresholds'])} "
        f"(gate wants >= {p11.GATE_THRESHOLD_SIZE})",
    ]
    for arm, value in report["terminal_under_arm"].items():
        lines.append(f"    {arm:<24} -> {value}")
    lines += [
        f"    decoder_arm axis: {axis.values} values, {axis.comparable_pairs} comparable pairs, "
        f"{axis.verdict_changing_pairs} verdict-changing, inert: {axis.inert}",
        f"    pool outcome: {report['pool_outcome'].value}",
        "",
        "  decoder-family share of the published n=64 gap",
    ]
    for row in report["decoder_family_share"]:
        share = row["decoder_family_share"]
        lines.append(
            f"    {row['cell']}: published {row['published_gap_at_64']:.4f} = decoder "
            f"{row['decoder_family_gap_at_64']:.4f} + state {row['representation_gap_at_64']:.4f}"
            + (f"  ({share:.1%} decoder)" if share is not None else "")
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
