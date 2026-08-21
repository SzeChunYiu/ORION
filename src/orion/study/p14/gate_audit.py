"""Audit P14A's published negative for a terminal the protocol could have moved.

Reproduces the committed result digest, measures how far the graded ORION arm
sits from the gold that grades it, runs all seven preregistered gates against
worlds the freeze admits, and asks separately whether the emitter responds at
all to worlds it does not.

Exits ``3`` when anything blocks, so it fails a pipeline rather than printing a
table nobody reads::

    python -m orion.study.p14.gate_audit
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Sequence

from orion.programme.records import Outcome
from orion.study.p14 import governance_gates as p14


def audit_p14a_governance_terminal() -> dict[str, Any]:
    """Measure the shipped negative, and roll the verdicts up without compensation."""

    terminal = p14.terminal_reach()
    responsiveness = p14.bench_responsiveness()
    divergence = p14.orion_arm_divergence()

    # The ORION arm's divergence is not a guard assessment: an arm that is the
    # answer key is the P4 failure --- a label recoverable from the construction
    # --- not a missing denominator.
    grading_outcome = Outcome.PASS if divergence.applied else Outcome.FAIL

    # Responsiveness is reported but does not roll up: it is the half that
    # clears the emitter, and letting a PASS there offset an unreachable
    # terminal would be the compensation `worst_outcome` exists to refuse.
    outcome = Outcome.PASS
    for other in (terminal.outcome, grading_outcome):
        if other.blocks and not outcome.blocks:
            outcome = other

    return {
        "digest_reproduced": p14.shipped_bench()["result_sha256"] == p14.SHIPPED_RESULT_DIGEST,
        "terminal_reach": terminal,
        "responsiveness": responsiveness,
        "orion_arm_divergence": divergence,
        "grading_outcome": grading_outcome,
        "discriminator_supremum": p14.discriminator_supremum(),
        "outcome": outcome,
    }


def report_as_json(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "digest_reproduced": report["digest_reproduced"],
        "terminal_reach": report["terminal_reach"].as_json(),
        "responsiveness": report["responsiveness"].as_json(),
        "orion_arm_divergence": report["orion_arm_divergence"].as_json(),
        "grading_outcome": report["grading_outcome"].value,
        "discriminator_supremum": report["discriminator_supremum"],
        "outcome": report["outcome"].value,
    }


def _render(report: dict[str, Any]) -> str:
    terminal = report["terminal_reach"]
    responsiveness = report["responsiveness"]
    divergence = report["orion_arm_divergence"]
    lines = [
        "P14A controlled governance terminal",
        "",
        f"  committed digest reproduced: {report['digest_reproduced']}",
        f"  graded ORION arm vs the gold that grades it: "
        f"{divergence.points_changed}/{divergence.points} points differ "
        f"({report['grading_outcome'].value})",
        f"  supremum of the discriminator over the declared support: "
        f"{report['discriminator_supremum']:.6f}",
        "",
        f"  {terminal.label}",
        f"    admissible worlds registered: {len(terminal.world_ids)}",
        f"    worlds clearing every gate: {len(terminal.clearing)}",
        f"    reachable terminals: {terminal.distinct_terminals}",
        f"    no admissible world satisfies: {', '.join(terminal.unattainable) or 'none'}",
        f"    every admissible world satisfies: {', '.join(terminal.unconditional) or 'none'}",
        "",
        "    gate                                         best     margin  outcome",
    ]
    for reach in terminal.reaches:
        lines.append(
            f"    {reach.gate.gate_id:<40} {reach.best_value:9.6f} "
            f"{reach.attainment_margin:+10.6f}  {reach.outcome.value}"
        )
    lines += [
        "",
        f"  {responsiveness.label} (worlds the protocol does not admit)",
        f"    baseline verdict: {responsiveness.baseline_verdict}",
        f"    distinct verdicts over the register: {len(responsiveness.verdicts_observed)}",
        f"    cases the verdict ignored: "
        f"{len(responsiveness.unmoved)}/{responsiveness.exercise.opportunities}",
        f"    outcome: {responsiveness.outcome.value} "
        f"({responsiveness.assessment.reason.value})",
        "",
        f"  outcome: {report['outcome'].value}",
    ]
    return "\n".join(lines)


def main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit the audit as JSON")
    args = parser.parse_args(argv)

    report = audit_p14a_governance_terminal()
    payload = report_as_json(report)
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else _render(report))
    return 3 if Outcome(payload["outcome"]).blocks else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
