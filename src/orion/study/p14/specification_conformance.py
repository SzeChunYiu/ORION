"""P14C's published positive, asked the question that disqualified P14A's negative.

``research/failures/2026-08-unattainable-gate-predetermined-terminal/`` closes
with a residual it could not discharge: "P14C separates the specification and is
not audited here, and it should be --- by this instrument, before its numbers are
read as a superiority result." This module is that audit, and it also carries the
part the P14A record could not: P14A's two failing thresholds, unchanged, read on
a benchmark where they are inside reach.

The shipped runner and the frozen case table are loaded, never re-implemented.
:func:`bench` replays ``main()``'s aggregation with one thing lifted out as a
parameter --- which implementation sits in the graded ``ORION_RSE_FULL`` slot ---
and at the shipped subject it reproduces the committed canonical digest
``74032348de7e6508b6c1827aabcf1bf9d354d30b9c6f81c8259fdb3535f01a63`` byte for
byte.

Three questions, and the first is the one P14A's register could not ask.

**What coordinate does each gate's statistic vary over?** P14A's two failing
gates read a *benchmark* quantity --- how often the one disposition the strongest
baseline cannot make actually occurs --- so their reach is a property of the
sampling support, and the support's ceiling of ``0.042326`` sat below both
thresholds. P14C fixes the composition instead of sampling it: four cases per
semantic stratum makes that same quantity exactly ``4/28 = 0.142857`` in every
admissible table. What is left free is the *subject*: the protocol registers six
component ablations as implementations of the contract, and
:func:`subject_worlds` puts each of them in the graded slot in turn.

**Could the terminal have been the other word?** :func:`terminal_reach`
intersects the eight gates' readings across those seven subjects. The full
implementation clears all eight; every ablation fails at least one; the
conjunction prints two distinct terminals. That is the property P14A's
conjunction did not have.

**Do P14A's own thresholds pass here?** :func:`inherited_gate_reaches` registers
``strongest_baseline_false_promotion_ge_0_05`` and ``accuracy_gain_ge_0_08`` with
their frozen P14A thresholds untouched and reads them on P14C's summary. Both are
met at ``0.142857`` --- 2.9x and 1.8x their bars, against a P14A ceiling of
``0.042326`` that was below both. Nothing here edits, relabels or re-runs P14A;
its receipt and terminal stand verbatim. What is added is the measurement P14A's
own protocol could not take.

The boundary is P14C's, unchanged and inherited: the adjudication specification
is internally authored, so what is established is contract conformance, not
external scientific validity.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from functools import lru_cache
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Mapping, Sequence

from orion.programme.gate_attainability import (
    AdmissibleWorld,
    GateDirection,
    GateReach,
    GateReachReason,
    GateRole,
    PreregisteredGate,
    StatisticSupport,
    TerminalReach,
    ThresholdPanel,
    ThresholdReach,
    assess_threshold_panel,
    assess_threshold_support,
    measure_gate_attainability,
    measure_terminal_reach,
)
from orion.programme.records import Outcome
from orion.study.p14 import governance_gates as p14a

REPO_ROOT = Path(__file__).resolve().parents[4]
PAPER = REPO_ROOT / "papers/orion-24-orion-rse"
P14C_SCRIPT = PAPER / "run_p14c_specification_separated_governance_v1.py"
P14C_CASES = PAPER / "P14C_ADJUDICATION_CASES_V1.json"
P14C_RECEIPT = PAPER / "P14C_SPECIFICATION_SEPARATED_RESULT_RECEIPT_V1.json"
P14C_ADJUDICATION = PAPER / "P14C_PROTOCOL_ADJUDICATION_V2.json"

#: The terminal the shipped P14C receipt publishes.
SHIPPED_TERMINAL = "P14C_SPECIFICATION_SEPARATED_GOVERNANCE_CONFORMANCE_SUPPORTED"

#: The other word the runner's conjunction can print.
NEGATIVE_TERMINAL = "P14C_SPECIFICATION_SEPARATED_GOVERNANCE_CONFORMANCE_GATE_NOT_MET"

#: The committed canonical digest, adjudicated twice in
#: ``P14C_PROTOCOL_ADJUDICATION_V2.json``. The fidelity anchor.
SHIPPED_RESULT_DIGEST = "74032348de7e6508b6c1827aabcf1bf9d354d30b9c6f81c8259fdb3535f01a63"

#: The four partial-governance rule baselines, in the order the runner registers
#: them. The comparator is ``max`` over this tuple by disposition accuracy.
BASELINE_ARMS: tuple[str, ...] = (
    "RAW_POSITIVE",
    "REFLECTION_CHECKLIST",
    "DONOR_AWARE_REVIEW",
    "MULTI_REVIEW",
)

#: The six component ablations, and the fact each one stops reading. Registered
#: by the protocol as implementations of the contract, which is what makes them
#: admissible occupants of the graded slot.
ABLATED_FACT: Mapping[str, str] = {
    "ABLATE_EVIDENCE_INTEGRITY": "evidence_integrity",
    "ABLATE_FREEZE": "frozen_protocol",
    "ABLATE_IDENTIFIABILITY": "identifiable",
    "ABLATE_DONOR": "donor_owned",
    "ABLATE_INTERACTION": "interaction_only",
    "ABLATE_NEGATIVE_HISTORY": "live_negative_history",
}
ABLATION_ARMS: tuple[str, ...] = tuple(ABLATED_FACT)

#: The name of the graded slot. Which *implementation* occupies it is the
#: coordinate this module varies.
SUBJECT_SLOT = "ORION_RSE_FULL"

#: The implementations the frozen protocol admits in the graded slot: the full
#: contract it shipped, and the six ablations it registers as variants of the
#: same contract with one component removed.
SUBJECT_IMPLEMENTATIONS: tuple[str, ...] = (SUBJECT_SLOT,) + ABLATION_ARMS

#: The stratum whose disposition no partial-review contract can reach. Its size
#: in the frozen table is the whole separation, exactly as one fact state was the
#: whole of P14A's.
DISCRIMINATING_STRATUM = "RETAIN_NEGATIVE"


def _load(path: Path, module_name: str) -> ModuleType:
    """Import a shipped script by path without putting it on the import graph."""

    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(module_name, module)
    spec.loader.exec_module(module)
    return module


@lru_cache(maxsize=None)
def runner_module() -> ModuleType:
    """The shipped P14C runner.

    Loaded rather than copied so ``full_policy``, the four baselines,
    ``ablated``, ``facts_only`` and ``score`` below are the functions that
    produced the committed result. ``main()`` sits behind a ``__name__`` guard
    and would write into ``papers/`` if it were called.
    """

    return _load(P14C_SCRIPT, "orion_p14c_specification_separated")


@lru_cache(maxsize=None)
def frozen_cases() -> tuple[dict[str, Any], ...]:
    """The frozen adjudication specification, as the runner reads it."""

    payload = json.loads(P14C_CASES.read_text(encoding="utf-8"))
    return tuple(payload["cases"])


def shipped_receipt() -> dict[str, Any]:
    return json.loads(P14C_RECEIPT.read_text(encoding="utf-8"))


def shipped_adjudication() -> dict[str, Any]:
    return json.loads(P14C_ADJUDICATION.read_text(encoding="utf-8"))


def policies() -> dict[str, Callable[[dict[str, bool]], str]]:
    """Every registered arm's decision function, taken from the shipped runner."""

    module = runner_module()
    arms: dict[str, Callable[[dict[str, bool]], str]] = {
        "RAW_POSITIVE": module.raw_positive,
        "REFLECTION_CHECKLIST": module.reflection,
        "DONOR_AWARE_REVIEW": module.donor_aware,
        "MULTI_REVIEW": module.multi_review,
        SUBJECT_SLOT: module.full_policy,
    }
    for name, field in ABLATED_FACT.items():
        arms[name] = lambda case, field=field: module.ablated(case, field)
    return arms


@lru_cache(maxsize=None)
def bench(subject: str = SUBJECT_SLOT) -> dict[str, Any]:
    """Replay ``main()``'s payload with the graded slot's implementation as a parameter.

    Every decision is delegated to the shipped module: ``facts_only`` strips the
    gold field, the registered policies answer, ``score`` tallies. Only the
    occupant of the graded slot is ours, and at :data:`SUBJECT_SLOT` the emitted
    payload hashes to :data:`SHIPPED_RESULT_DIGEST`.
    """

    if subject not in SUBJECT_IMPLEMENTATIONS:
        raise ValueError(f"{subject} is not a registered occupant of the graded slot")
    module = runner_module()
    cases = list(frozen_cases())
    arms = policies()
    arms[SUBJECT_SLOT] = policies()[subject]

    summary = {name: module.score(cases, fn) for name, fn in arms.items()}
    strongest = max(BASELINE_ARMS, key=lambda arm: float(summary[arm]["disposition_accuracy"]))
    gates = {gate.gate_id: gate.satisfied_by(READINGS[gate.gate_id](summary)) for gate in GATES}
    terminal = SHIPPED_TERMINAL if all(gates.values()) else NEGATIVE_TERMINAL
    result = {
        "schema": "ORION.P14C.SpecificationSeparatedGovernance.v1",
        "protocol": "P14C_SPECIFICATION_SEPARATED_GOVERNANCE_PROTOCOL_V1.md",
        "adjudication_spec": "P14C_ADJUDICATION_CASES_V1.json",
        "case_count": len(cases),
        "strongest_non_orion_baseline": strongest,
        "summary": summary,
        "gates": gates,
        "terminal": terminal,
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    return {**result, "result_sha256": hashlib.sha256(text.encode()).hexdigest()}


def shipped_bench() -> dict[str, Any]:
    return bench(SUBJECT_SLOT)


def _strongest(summary: Mapping[str, Any]) -> str:
    return max(BASELINE_ARMS, key=lambda arm: float(summary[arm]["disposition_accuracy"]))


def _ablations_worse(summary: Mapping[str, Any]) -> float:
    subject = summary[SUBJECT_SLOT]
    return float(
        sum(
            1
            for arm in ABLATION_ARMS
            if summary[arm]["disposition_accuracy"] < subject["disposition_accuracy"]
        )
    )


def _gold_stripped(_summary: Mapping[str, Any]) -> float:
    module = runner_module()
    return float(
        all("gold_disposition" not in module.facts_only(dict(case)) for case in frozen_cases())
    )


#: Each gate's statistic, read off a run's ``summary``. Counts and rates rather
#: than the runner's booleans, so an attainability verdict carries the distance
#: to the threshold and not only which side of it a subject landed.
READINGS: Mapping[str, Callable[[Mapping[str, Any]], float]] = {
    "full_accuracy_one": lambda s: s[SUBJECT_SLOT]["disposition_accuracy"],
    "full_zero_false_promotion": lambda s: s[SUBJECT_SLOT]["false_promotion_rate"],
    "full_discovery_recall_one": lambda s: s[SUBJECT_SLOT]["useful_discovery_recall"],
    "retain_and_reopen_exact": lambda s: min(
        s[SUBJECT_SLOT]["retain_negative_accuracy"], s[SUBJECT_SLOT]["supported_reopen_accuracy"]
    ),
    "strongest_baseline_false_promotion_ge_0_10": lambda s: s[_strongest(s)][
        "false_promotion_rate"
    ],
    "accuracy_advantage_ge_0_10": lambda s: s[SUBJECT_SLOT]["disposition_accuracy"]
    - s[_strongest(s)]["disposition_accuracy"],
    "every_ablation_worse": _ablations_worse,
    "gold_stripped_from_policy_input": _gold_stripped,
}

#: P14C's eight preregistered gates, transcribed from its protocol's positive
#: terminal. Thresholds are the frozen ones; nothing here is relaxed.
#:
#: Two are :data:`~orion.programme.gate_attainability.GateRole.PRECONDITION`
#: rather than hypotheses, and the distinction is the one P14A's receipt could
#: not draw. "The strongest partial contract false-promotes at least 10% of the
#: time" is a statement about the benchmark, settled before a subject is chosen;
#: it is *supposed* to hold in every admissible world, and P14A's corresponding
#: gate failing to hold in any is precisely why P14A measured nothing. So is
#: "no policy call saw the gold field": an input hygiene certificate, not a
#: finding about the contract.
GATES: tuple[PreregisteredGate, ...] = (
    PreregisteredGate(
        gate_id="full_accuracy_one",
        reads="graded implementation's disposition accuracy over the 28 frozen cases",
        threshold=1.0,
    ),
    PreregisteredGate(
        gate_id="full_zero_false_promotion",
        reads="graded implementation's false promotion rate",
        threshold=0.0,
        direction=GateDirection.AT_MOST,
    ),
    PreregisteredGate(
        gate_id="full_discovery_recall_one",
        reads="graded implementation's useful discovery recall",
        threshold=1.0,
    ),
    PreregisteredGate(
        gate_id="retain_and_reopen_exact",
        reads="the lower of the graded implementation's retained-negative and reopen accuracy",
        threshold=1.0,
    ),
    PreregisteredGate(
        gate_id="strongest_baseline_false_promotion_ge_0_10",
        reads="strongest non-ORION baseline false promotion rate over the frozen table",
        threshold=0.10,
        role=GateRole.PRECONDITION,
    ),
    PreregisteredGate(
        gate_id="accuracy_advantage_ge_0_10",
        reads="graded implementation's disposition accuracy minus the strongest baseline's",
        threshold=0.10,
    ),
    PreregisteredGate(
        gate_id="every_ablation_worse",
        reads="registered ablations scoring below the graded implementation",
        threshold=6.0,
    ),
    PreregisteredGate(
        gate_id="gold_stripped_from_policy_input",
        reads="1.0 when no policy call receives the gold field, 0.0 otherwise",
        threshold=1.0,
        role=GateRole.PRECONDITION,
    ),
)

#: P14A's two failing thresholds, verbatim. Same ids, same numbers, same
#: directions, same roles as :data:`orion.study.p14.governance_gates.GATES`
#: registers them --- read here on a benchmark that can produce values on both
#: sides of them. Nothing about P14A is edited by pointing its own bars at a
#: different instrument.
INHERITED_GATES: tuple[PreregisteredGate, ...] = tuple(
    gate for gate in p14a.GATES if gate.gate_id in set(p14a.SUPPORT_BOUNDED_GATES)
)

#: The inherited gates' statistics, expressed against P14C's summary. They are
#: the same two quantities P14A read: the strongest rule baseline's false
#: promotion rate, and the graded implementation's accuracy gain over it.
INHERITED_READINGS: Mapping[str, Callable[[Mapping[str, Any]], float]] = {
    "strongest_baseline_false_promotion_ge_0_05": READINGS[
        "strongest_baseline_false_promotion_ge_0_10"
    ],
    "accuracy_gain_ge_0_08": READINGS["accuracy_advantage_ge_0_10"],
}


def subject_worlds() -> tuple[AdmissibleWorld, ...]:
    """The implementations the frozen protocol admits in the graded slot.

    The register has to be defensible in both directions, and this one is short
    enough to audit line by line: the contract P14C shipped, and the six
    single-component ablations its own protocol section 'Policies' registers.
    Nothing outside that list is offered, because a world the protocol does not
    admit widens the gate instead of measuring it.
    """

    worlds = [
        AdmissibleWorld(
            world_id="full-contract",
            admits="the implementation the protocol names for the graded slot",
            payload=SUBJECT_SLOT,
        )
    ]
    worlds += [
        AdmissibleWorld(
            world_id=arm.lower().replace("_", "-"),
            admits=(
                f"the protocol registers {arm} as the contract with its {ABLATED_FACT[arm]} "
                "check removed and scores it on the same table; an implementation that "
                "silently lost that check is what the graded slot would then hold"
            ),
            payload=arm,
        )
        for arm in ABLATION_ARMS
    ]
    return tuple(worlds)


def _reaches(
    gates: Sequence[PreregisteredGate], readings: Mapping[str, Any]
) -> tuple[GateReach, ...]:
    worlds = subject_worlds()
    return tuple(
        measure_gate_attainability(
            lambda subject, gate_id=gate.gate_id: readings[gate_id](bench(subject)["summary"]),
            gate=gate,
            worlds=worlds,
        )
        for gate in gates
    )


def gate_reaches() -> tuple[GateReach, ...]:
    """Each of P14C's eight gates, measured across the seven admissible subjects."""

    return _reaches(GATES, READINGS)


def inherited_gate_reaches() -> tuple[GateReach, ...]:
    """P14A's two thresholds, unchanged, measured across the same seven subjects."""

    return _reaches(INHERITED_GATES, INHERITED_READINGS)


def terminal_reach() -> TerminalReach:
    """How many terminals P14C's conjunction could print over its subject register."""

    return measure_terminal_reach(
        gate_reaches(), label="P14C specification-separated conformance terminal"
    )


def inherited_reading() -> dict[str, float]:
    """P14A's two statistics as P14C's shipped run realizes them."""

    summary = shipped_bench()["summary"]
    return {gate_id: reader(summary) for gate_id, reader in INHERITED_READINGS.items()}


def inherited_gates_met() -> dict[str, bool]:
    """Whether P14A's own frozen bars are cleared on the successor's benchmark."""

    values = inherited_reading()
    return {gate.gate_id: gate.satisfied_by(values[gate.gate_id]) for gate in INHERITED_GATES}


def discriminating_stratum_share() -> float:
    """Fraction of the frozen table on which no partial-review contract can be right.

    The counterpart of P14A's ``discriminator_supremum``, and the reason the same
    thresholds are reachable here: P14C fixes the composition where P14A sampled
    it, so this is a count rather than a supremum over a box.
    """

    cases = frozen_cases()
    return sum(1 for case in cases if case["stratum"] == DISCRIMINATING_STRATUM) / len(cases)


def arm_error_counts() -> dict[str, int]:
    """Cases of the 28 on which each registered arm departs from the frozen gold."""

    module = runner_module()
    cases = frozen_cases()
    return {
        name: sum(
            1
            for case in cases
            if fn(module.facts_only(dict(case))) != str(case["gold_disposition"])
        )
        for name, fn in policies().items()
    }


def declared_supports() -> dict[str, StatisticSupport]:
    """The intervals P14C's own freeze puts each threshold-bearing statistic in.

    Available before the run, like P14A's --- and unlike P14A's, they contain the
    thresholds. Two coordinates, because the two gates vary over different things:
    the difficulty precondition over the tables the protocol admits, the
    superiority gate over the implementations it admits in the graded slot.
    """

    share = discriminating_stratum_share()
    counts = arm_error_counts()
    cases = len(frozen_cases())
    worst_subject = max(counts[arm] for arm in ABLATION_ARMS)
    strongest_errors = min(counts[arm] for arm in BASELINE_ARMS)

    difficulty = StatisticSupport(
        statistic=(
            "strongest partial-contract false promotion rate, over the case tables the "
            "frozen protocol admits"
        ),
        infimum=share,
        supremum=share,
        derivation=(
            f"the protocol declares four cases per semantic stratum over seven strata; the "
            f"strongest rule baseline MULTI_REVIEW is wrong exactly on the "
            f"{DISCRIMINATING_STRATUM} stratum and nowhere else ({strongest_errors} of "
            f"{cases} cases), so the statistic is that stratum's fixed share of the table "
            f"in every admissible table and equals {share}"
        ),
    )
    advantage = StatisticSupport(
        statistic=(
            "graded implementation's accuracy gain over the strongest partial contract, "
            "over the implementations the frozen protocol admits in the graded slot"
        ),
        infimum=(strongest_errors - worst_subject) / cases if worst_subject else share,
        supremum=share,
        derivation=(
            "the protocol registers six single-component ablations as implementations of "
            "the contract; dropping donor, interaction or negative-history handling costs "
            f"{worst_subject} of {cases} cases and lands the subject on the strongest "
            "baseline's own score for a gain of 0.0, while a fully conforming "
            f"implementation gains the {strongest_errors} cases the baseline cannot reach"
        ),
    )
    return {
        "strongest_baseline_false_promotion_ge_0_10": difficulty,
        "accuracy_advantage_ge_0_10": advantage,
        "strongest_baseline_false_promotion_ge_0_05": difficulty,
        "accuracy_gain_ge_0_08": advantage,
    }


def threshold_reaches() -> tuple[ThresholdReach, ...]:
    """P14C's own two numeric thresholds against the intervals its freeze declares."""

    supports = declared_supports()
    return tuple(
        assess_threshold_support(gate, support=supports[gate.gate_id])
        for gate in GATES
        if gate.gate_id in supports
    )


def inherited_threshold_reaches() -> tuple[ThresholdReach, ...]:
    """P14A's two thresholds against the intervals P14C's freeze declares.

    The comparison that resolves P14A's terminal: the same bars, ``0.05`` and
    ``0.08``, against a reachable interval that contains them instead of one
    whose ceiling was ``0.042326``.
    """

    supports = declared_supports()
    return tuple(
        assess_threshold_support(gate, support=supports[gate.gate_id]) for gate in INHERITED_GATES
    )


def threshold_panel() -> ThresholdPanel:
    """The pre-run verdict on P14C's own battery."""

    return assess_threshold_panel(
        threshold_reaches(), label="P14C specification-separated thresholds"
    )


def inherited_threshold_panel() -> ThresholdPanel:
    """The pre-run verdict on P14A's battery, had it been frozen against this benchmark."""

    return assess_threshold_panel(
        inherited_threshold_reaches(),
        label="P14A aggregate superiority thresholds on the P14C benchmark",
    )


def unexercised_hypothesis_gates() -> tuple[str, ...]:
    """Hypothesis gates every admissible subject satisfies, so their ``true`` says nothing.

    Reported by name rather than folded into the terminal's verdict, because the
    two facts are different and only one of them blocks. P14C's conjunction can
    print both its words, so its terminal is a function of the subject --- and
    ``full_discovery_recall_one`` is still a gate no registered implementation
    can fail, because every ablation removes a check and a policy that reads
    fewer facts promotes more rather than fewer. That gate's pass is a property
    of the ablation register, not evidence that the contract preserves valid
    discovery, and saying so is the same discipline P4's saturated
    ``clean_coverage`` gets in :mod:`orion.programme.panel_resolution`.
    """

    return tuple(
        reach.gate.gate_id
        for reach in gate_reaches()
        if reach.reason is GateReachReason.THRESHOLD_UNCONDITIONAL
        and reach.gate.role is GateRole.HYPOTHESIS
    )


def audit_p14c_conformance_terminal() -> dict[str, Any]:
    """Measure the shipped positive, and roll the verdicts up without compensation."""

    terminal = terminal_reach()
    panel = threshold_panel()
    inherited_panel = inherited_threshold_panel()
    inherited = inherited_gates_met()

    digest_reproduced = shipped_bench()["result_sha256"] == SHIPPED_RESULT_DIGEST
    fidelity = Outcome.PASS if digest_reproduced else Outcome.FAIL
    inherited_outcome = Outcome.PASS if all(inherited.values()) else Outcome.FAIL

    outcome = Outcome.PASS
    for other in (fidelity, terminal.outcome, panel.outcome, inherited_panel.outcome):
        if other.blocks and not outcome.blocks:
            outcome = other

    return {
        "digest_reproduced": digest_reproduced,
        "terminal_reach": terminal,
        "threshold_panel": panel,
        "inherited_threshold_panel": inherited_panel,
        "inherited_gates_met": inherited,
        "inherited_reading": inherited_reading(),
        "discriminating_stratum_share": discriminating_stratum_share(),
        "arm_error_counts": arm_error_counts(),
        "unexercised_hypothesis_gates": unexercised_hypothesis_gates(),
        "p14a_discriminator_supremum": p14a.discriminator_supremum(),
        "inherited_outcome": inherited_outcome,
        "outcome": outcome,
    }


def report_as_json(report: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "digest_reproduced": report["digest_reproduced"],
        "terminal_reach": report["terminal_reach"].as_json(),
        "threshold_panel": report["threshold_panel"].as_json(),
        "inherited_threshold_panel": report["inherited_threshold_panel"].as_json(),
        "inherited_gates_met": dict(report["inherited_gates_met"]),
        "inherited_reading": dict(report["inherited_reading"]),
        "discriminating_stratum_share": report["discriminating_stratum_share"],
        "arm_error_counts": dict(report["arm_error_counts"]),
        "unexercised_hypothesis_gates": list(report["unexercised_hypothesis_gates"]),
        "p14a_discriminator_supremum": report["p14a_discriminator_supremum"],
        "inherited_outcome": report["inherited_outcome"].value,
        "outcome": report["outcome"].value,
    }


def _render(report: Mapping[str, Any]) -> str:
    terminal = report["terminal_reach"]
    lines = [
        "P14C specification-separated conformance terminal",
        "",
        f"  committed canonical digest reproduced: {report['digest_reproduced']}",
        f"  share of the frozen table no partial contract can reach: "
        f"{report['discriminating_stratum_share']:.6f}",
        f"  the same quantity's ceiling under P14A's sampled benchmark: "
        f"{report['p14a_discriminator_supremum']:.6f}",
        "",
        f"  {terminal.label}",
        f"    admissible subject implementations registered: {len(terminal.world_ids)}",
        f"    subjects clearing every gate: {len(terminal.clearing)}",
        f"    reachable terminals: {terminal.distinct_terminals}",
        f"    no admissible subject satisfies: {', '.join(terminal.unattainable) or 'none'}",
        f"    every admissible subject satisfies: {', '.join(terminal.unconditional) or 'none'}",
        "",
        "    gate                                          best     margin  outcome",
    ]
    for reach in terminal.reaches:
        lines.append(
            f"    {reach.gate.gate_id:<40} {reach.best_value:9.6f} "
            f"{reach.attainment_margin:+10.6f}  {reach.outcome.value}"
        )
    for label, panel in (
        ("P14C thresholds, before the run", report["threshold_panel"]),
        ("P14A thresholds, unchanged, on this benchmark", report["inherited_threshold_panel"]),
    ):
        lines += ["", f"  {label}: {panel.outcome.value}"]
        for reach in panel.reaches:
            lines.append(
                f"    {reach.gate.gate_id:<40} reach "
                f"[{reach.support.infimum:.6f}, {reach.support.supremum:.6f}] "
                f"vs {reach.gate.threshold:<6} {reach.reason.value}"
            )
    values = report["inherited_reading"]
    lines += ["", "  P14A's two failing gates, read on the successor's benchmark"]
    for gate_id, met in report["inherited_gates_met"].items():
        lines.append(f"    {gate_id:<44} {values[gate_id]:9.6f}  {'MET' if met else 'NOT MET'}")
    lines += [
        "",
        "  hypothesis gates no registered subject can fail: "
        + (", ".join(report["unexercised_hypothesis_gates"]) or "none"),
        f"  outcome: {report['outcome'].value}",
    ]
    return "\n".join(lines)


def main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit the audit as JSON")
    args = parser.parse_args(argv)

    report = audit_p14c_conformance_terminal()
    payload = report_as_json(report)
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else _render(report))
    return 3 if Outcome(payload["outcome"]).blocks else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))


__all__ = [
    "ABLATED_FACT",
    "ABLATION_ARMS",
    "BASELINE_ARMS",
    "DISCRIMINATING_STRATUM",
    "GATES",
    "INHERITED_GATES",
    "INHERITED_READINGS",
    "NEGATIVE_TERMINAL",
    "READINGS",
    "SHIPPED_RESULT_DIGEST",
    "SHIPPED_TERMINAL",
    "SUBJECT_IMPLEMENTATIONS",
    "SUBJECT_SLOT",
    "arm_error_counts",
    "audit_p14c_conformance_terminal",
    "bench",
    "declared_supports",
    "discriminating_stratum_share",
    "frozen_cases",
    "gate_reaches",
    "inherited_gate_reaches",
    "inherited_gates_met",
    "inherited_reading",
    "inherited_threshold_panel",
    "inherited_threshold_reaches",
    "main",
    "policies",
    "report_as_json",
    "runner_module",
    "shipped_adjudication",
    "shipped_bench",
    "shipped_receipt",
    "subject_worlds",
    "terminal_reach",
    "threshold_panel",
    "threshold_reaches",
    "unexercised_hypothesis_gates",
]
