"""P11H's preregistered battery, asked for its reach before the campaign runs.

P11G froze a hostile attack, ran it, and reported that the defence survived.
:mod:`orion.study.p11.attack_audit` then established that the survival was
arithmetic: all four of P11G's scientific gates hold in every world its freeze
admits, so ``all(gates.values())`` was ``True`` before the seed was drawn. That
is ``UNWINNABLE_ATTACK_PREDETERMINED_SURVIVAL``, and the record says only a
successor protocol can retire it.

P11H is that successor. This module is the half of it that runs **before** the
result is read:

* it declares P11H's five gates with their roles, in
  :mod:`orion.programme.gate_attainability`'s vocabulary;
* it derives each gate statistic's support from the frozen protocol --- the
  ladder's per-rung readings plus an exact order statistic over the pair the
  fresh seed draws --- rather than guessing it;
* it runs :func:`~orion.programme.gate_attainability.assess_threshold_panel` and
  :func:`~orion.programme.gate_attainability.require_supported_thresholds` over
  that support, so a threshold outside its own statistic's reach is a raised
  exception at freeze time rather than a published number that has to be
  withdrawn; and
* it measures :func:`~orion.programme.gate_attainability.measure_terminal_reach`
  over every pair of rungs the draw can produce, so ``distinct_terminals`` is a
  fact about the protocol and not about the run.

Every number is taken at :data:`PREFLIGHT_SEED`, which is not the seed the
terminal is read at. The preflight bounds the reach of the bars; it never reads
the outcome.

The one thing P11H does **not** change is the bars themselves. ``0.95`` and
``0.20`` are P11G's own thresholds carried over verbatim, exactly as P14C
carried P14A's ``0.05`` and ``0.08`` onto a benchmark that could move them. What
changes is the support of the statistic they read.
"""

from __future__ import annotations

import importlib.util
import itertools
import json
import sys
from functools import lru_cache
from pathlib import Path
from types import ModuleType
from typing import Any, Sequence

from orion.programme.gate_attainability import (
    AdmissibleWorld,
    GateDirection,
    GateReach,
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
    require_reachable,
    require_supported_thresholds,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
PAPER_DIR = REPO_ROOT / "papers/paper-11-state-as-computation"
P11H_RUNNER = PAPER_DIR / "run_p11h_pooled_sparsity_ladder_v1.py"
P11H_PROTOCOL = PAPER_DIR / "P11H_POOLED_SPARSITY_LADDER_PROTOCOL_V1.md"
P11H_PREFLIGHT = PAPER_DIR / "P11H_PREFLIGHT_ATTAINABILITY_V1.json"
P11H_RESULT = PAPER_DIR / "P11H_POOLED_SPARSITY_LADDER_RESULT_V1.json"

PANEL_LABEL = "P11H pooled universal-decoder battery"
TERMINAL_LABEL = "P11H pooled sparsity-ladder terminal"


@lru_cache(maxsize=1)
def p11h_module() -> ModuleType:
    """Import the frozen runner under its own name, without executing its ``main``.

    The preflight measures the executable that will produce the result, not a
    local re-implementation of it. An instrument that only agrees with its own
    fixture is the defect ``2026-08-unfalsifiable-check-zero-refutation-capacity``
    records.
    """

    if not P11H_RUNNER.exists():  # pragma: no cover - a missing paper is a layout fault
        raise FileNotFoundError(f"P11H runner not found at {P11H_RUNNER}")
    spec = importlib.util.spec_from_file_location("orion_p11h_frozen_runner", P11H_RUNNER)
    if spec is None or spec.loader is None:  # pragma: no cover - importlib contract
        raise ImportError(f"cannot load {P11H_RUNNER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    previously = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previously
    return module


def _runner() -> ModuleType:
    return p11h_module()


PREFLIGHT_SEED = 2026082201


#: P11H's five gates. Two carry the claim; three certify the instrument.
#:
#: The roles are what make "this gate never fails" mean two different things.
#: ``attack_live_on_ladder`` is *supposed* to hold in every admissible world ---
#: it says the pooled attack is a measuring instrument that registers a win
#: somewhere on the frozen ladder, which is precisely the sentence P11G could
#: not write. A hypothesis gate that holds in every admissible world is the
#: P11G defect and :class:`~orion.programme.gate_attainability.ThresholdPanel`
#: refuses it.
def gates() -> tuple[PreregisteredGate, ...]:
    module = _runner()
    target = module.TARGET_ACCURACY
    return (
        PreregisteredGate(
            gate_id="no_answer_laundering",
            reads="active components equal to or negating the signed label on the "
            "protected test set, summed over the drawn regimes",
            threshold=0.0,
            direction=GateDirection.AT_MOST,
            role=GateRole.PRECONDITION,
        ),
        PreregisteredGate(
            gate_id="attack_live_on_ladder",
            reads="the pooled universal attack's best mean test accuracy at a registered "
            "size below n=256, maximised over every rung of the frozen ladder",
            threshold=target,
            direction=GateDirection.AT_LEAST,
            role=GateRole.PRECONDITION,
        ),
        PreregisteredGate(
            gate_id="compiled_by_64",
            reads="the compiled arm's smallest mean test accuracy at n=64 over the "
            "drawn regimes",
            threshold=target,
            direction=GateDirection.AT_LEAST,
            role=GateRole.PRECONDITION,
        ),
        PreregisteredGate(
            gate_id="pooled_universal_threshold_ge_256",
            reads="the pooled universal attack's best mean test accuracy at a registered "
            "size below n=256, over the drawn regimes",
            threshold=target,
            direction=GateDirection.AT_MOST,
            role=GateRole.HYPOTHESIS,
        ),
        PreregisteredGate(
            gate_id="delta64_ge_0_20",
            reads="the smallest compiled-minus-pooled mean accuracy at n=64 over the "
            "drawn regimes",
            threshold=module.DELTA64_THRESHOLD,
            direction=GateDirection.AT_LEAST,
            role=GateRole.HYPOTHESIS,
        ),
    )


#: How each gate's statistic is assembled from the ladder's per-rung readings.
#:
#: ``PAIR`` statistics read only the drawn regimes; ``LADDER`` statistics read
#: the whole frozen ladder and are therefore constant across the draw. The
#: distinction is what makes the support derivation exact: a ``PAIR`` statistic's
#: reach over the draw is an order statistic of the rung readings, and a
#: ``LADDER`` statistic's is a single value.
AGGREGATION: dict[str, tuple[str, str, str]] = {
    # gate_id -> (scope, reducer, per-rung field)
    "no_answer_laundering": ("PAIR", "sum", "laundering_count"),
    "attack_live_on_ladder": ("LADDER", "max", "pooled_best_below_gate"),
    "compiled_by_64": ("PAIR", "min", "compiled_at_64"),
    "pooled_universal_threshold_ge_256": ("PAIR", "max", "pooled_best_below_gate"),
    "delta64_ge_0_20": ("PAIR", "min", "delta64_vs_pool"),
}


@lru_cache(maxsize=8)
def ladder_readings(seed: int = PREFLIGHT_SEED) -> tuple[dict[str, float], ...]:
    """Each rung's gate-relevant quantities, measured by the frozen runner itself."""

    module = _runner()
    rows = []
    for rung in module.measure_ladder(seed):
        rows.append(
            {
                "rung": float(rung["rung"]),
                "laundering_count": float(len(rung["laundering_failures"])),
                "pooled_best_below_gate": float(rung["pooled_best_below_gate"]),
                "compiled_at_64": float(rung["compiled_at_64"]),
                "delta64_vs_pool": float(rung["delta64_vs_pool"]),
            }
        )
    return tuple(rows)


def statistic_of(gate_id: str, rungs: Sequence[dict[str, float]], drawn: Sequence[int]) -> float:
    """One gate's statistic, given the ladder's readings and the drawn regimes."""

    scope, reducer, field = AGGREGATION[gate_id]
    source = rungs if scope == "LADDER" else [rungs[index] for index in drawn]
    values = [row[field] for row in source]
    return {"sum": sum, "min": min, "max": max}[reducer](values)


def declared_supports(seed: int = PREFLIGHT_SEED) -> dict[str, StatisticSupport]:
    """Each gate statistic's closed interval over every draw the protocol admits.

    Exact rather than sampled. The protocol fixes the ladder and draws
    ``N_PROTECTED`` rungs from it without replacement, so a statistic that
    reduces the drawn rungs by ``max`` attains its infimum at the second-smallest
    rung reading and its supremum at the largest, and one that reduces by ``min``
    attains its infimum at the smallest and its supremum at the second-largest.
    Those are order statistics of a finite list, so the interval is computed, not
    estimated --- which is the property P14A's ``0.042326`` had and P11G's gates
    never had.
    """

    module = _runner()
    rungs = ladder_readings(seed)
    protected = module.N_PROTECTED
    supports: dict[str, StatisticSupport] = {}
    for gate in gates():
        scope, reducer, field = AGGREGATION[gate.gate_id]
        values = sorted(row[field] for row in rungs)
        if scope == "LADDER":
            point = {"sum": sum, "min": min, "max": max}[reducer](values)
            low = high = point
            how = (
                f"the statistic reduces the whole frozen ladder by {reducer}, so the draw "
                f"cannot move it: it is the single value {point!r} in every admissible world"
            )
        elif reducer == "max":
            low, high = values[protected - 1], values[-1]
            how = (
                f"the draw takes {protected} of {len(values)} rungs without replacement and the "
                f"statistic is their {reducer}; over all draws that is minimised on the "
                f"{protected} smallest rung readings and maximised on the largest, so the "
                f"interval is the ({protected})th and last order statistics of the rung readings"
            )
        elif reducer == "min":
            low, high = values[0], values[-protected]
            how = (
                f"the draw takes {protected} of {len(values)} rungs without replacement and the "
                f"statistic is their {reducer}; over all draws that is minimised on the smallest "
                f"rung reading and maximised on the {protected} largest, so the interval is the "
                f"first and ({len(values) - protected + 1})th order statistics of the rung readings"
            )
        else:
            low, high = sum(values[:protected]), sum(values[-protected:])
            how = (
                f"the draw takes {protected} of {len(values)} rungs and the statistic is their "
                f"sum, so the interval runs from the {protected} smallest rung readings to the "
                f"{protected} largest"
            )
        supports[gate.gate_id] = StatisticSupport(
            statistic=f"{gate.reads} (over every pair of rungs the frozen ladder admits)",
            infimum=float(low),
            supremum=float(high),
            derivation=(
                f"{how}; rung readings measured by the frozen runner at the preflight seed "
                f"{seed}, which is not the seed the terminal is read at"
            ),
        )
    return supports


def threshold_reaches(seed: int = PREFLIGHT_SEED) -> tuple[ThresholdReach, ...]:
    supports = declared_supports(seed)
    return tuple(assess_threshold_support(gate, support=supports[gate.gate_id]) for gate in gates())


def threshold_panel(seed: int = PREFLIGHT_SEED) -> ThresholdPanel:
    """P11H's whole battery, checked against its own declared support."""

    return assess_threshold_panel(threshold_reaches(seed), label=PANEL_LABEL)


def admissible_worlds(seed: int = PREFLIGHT_SEED) -> tuple[AdmissibleWorld, ...]:
    """Every pair of rungs the fresh seed can draw.

    The register is the protocol's own reachable set and nothing wider. P11H
    freezes the ladder and says the protected regimes are drawn from it without
    replacement, so each pair is an input a reader can read and agree the freeze
    permits --- which is what ``AdmissibleWorld.admits`` is required to state.
    Registering a regime that is not on the ladder would widen the protocol
    instead of measuring it, exactly as registering a different cell would have
    for P11G.
    """

    module = _runner()
    return tuple(
        AdmissibleWorld(
            world_id="regimes-" + "-".join(str(index) for index in drawn),
            admits="the frozen protocol draws its protected regimes from the frozen ladder "
            "without replacement; this is one of those draws, at cells "
            + " and ".join(str(list(module.LADDER[index])) for index in drawn),
            payload=drawn,
        )
        for drawn in itertools.combinations(range(len(module.LADDER)), module.N_PROTECTED)
    )


def gate_reaches(
    seed: int = PREFLIGHT_SEED, worlds: Sequence[AdmissibleWorld] | None = None
) -> tuple[GateReach, ...]:
    """Each gate, measured over every draw the frozen ladder admits."""

    rungs = ladder_readings(seed)
    register = tuple(admissible_worlds(seed) if worlds is None else worlds)
    return tuple(
        measure_gate_attainability(
            lambda drawn, gate_id=gate.gate_id: statistic_of(gate_id, rungs, drawn),
            gate=gate,
            worlds=register,
        )
        for gate in gates()
    )


def terminal_reach(
    seed: int = PREFLIGHT_SEED, worlds: Sequence[AdmissibleWorld] | None = None
) -> TerminalReach:
    """How many terminals P11H's conjunction can print over its own reachable set."""

    return measure_terminal_reach(gate_reaches(seed, worlds), label=TERMINAL_LABEL)


def preflight(seed: int = PREFLIGHT_SEED) -> dict[str, Any]:
    """The whole pre-run check, as the artifact that has to exist before execution.

    Raises :class:`~orion.programme.gate_attainability.UnattainableGate` if any
    threshold is outside its statistic's reach, if a hypothesis gate is satisfied
    by every admissible value, or if the conjunction has one reachable terminal.
    A P11H that cannot pass this has the P11G defect and must not be run for a
    result.
    """

    module = _runner()
    panel = threshold_panel(seed)
    require_supported_thresholds(panel)
    terminal = terminal_reach(seed)
    require_reachable(terminal)
    rungs = ladder_readings(seed)
    return {
        "schema": "ORION.P11H.PreflightAttainability.v1",
        "protocol": module.PROTOCOL,
        "preflight_seed": seed,
        "execution_seed": module.EXECUTION_SEED,
        "ladder": [list(cell) for cell in module.LADDER],
        "protected_regimes_drawn_per_run": module.N_PROTECTED,
        "universal_pool": list(module.UNIVERSAL_POOL),
        "thresholds": {
            "target_accuracy": module.TARGET_ACCURACY,
            "delta64": module.DELTA64_THRESHOLD,
            "inherited_from": "P11G_DETERMINISTIC_TREE_DECODER_PROTOCOL_V1.md, unedited",
        },
        "ladder_readings": [dict(row) for row in rungs],
        "threshold_panel": panel.as_json(),
        "terminal_reach": terminal.as_json(),
        "worlds_clearing_every_gate": list(terminal.clearing),
        "distinct_terminals": terminal.distinct_terminals,
    }


def successor_disposition() -> dict[str, Any]:
    """What P11H's recorded preflight and receipt say, read from disk without running either.

    The audit of P11G reads this to record where the
    ``UNWINNABLE_ATTACK_PREDETERMINED_SURVIVAL`` finding is discharged. It is a
    *reading*, not a verdict: nothing here makes P11G's attainability failure
    smaller, and :mod:`orion.study.p11.attack_audit` does not let it roll up.
    P11G's four gates hold in every world P11G admits, permanently; what a
    successor can do is ask the question again under a protocol whose attack has
    a reachable win, which is what ``retires`` reports.
    """

    disposition: dict[str, Any] = {
        "protocol": "ORION.P11H.PooledSparsityLadderAttack.v1",
        "preflight_recorded": P11H_PREFLIGHT.exists(),
        "executed": P11H_RESULT.exists(),
        "panel_outcome": None,
        "discriminating_hypothesis_gates": [],
        "distinct_terminals": None,
        "worlds_registered": None,
        "worlds_clearing_every_gate": None,
        "terminal": None,
        "protected_cells": None,
        "retires_unwinnable_attack_finding": False,
    }
    if disposition["preflight_recorded"]:
        recorded = json.loads(P11H_PREFLIGHT.read_text(encoding="utf-8"))
        panel = recorded["threshold_panel"]
        disposition["panel_outcome"] = panel["outcome"]
        disposition["discriminating_hypothesis_gates"] = list(panel["discriminating_hypotheses"])
        disposition["distinct_terminals"] = recorded["distinct_terminals"]
        disposition["worlds_registered"] = len(recorded["terminal_reach"]["worlds"])
        disposition["worlds_clearing_every_gate"] = len(recorded["worlds_clearing_every_gate"])
    if disposition["executed"]:
        receipt = json.loads(P11H_RESULT.read_text(encoding="utf-8"))
        disposition["terminal"] = receipt["terminal"]
        disposition["protected_cells"] = receipt["scientific_payload"]["protected_cells"]
    module = _runner()
    disposition["retires_unwinnable_attack_finding"] = bool(
        disposition["panel_outcome"] == "PASS"
        and disposition["discriminating_hypothesis_gates"]
        and (disposition["distinct_terminals"] or 0) >= 2
        and disposition["terminal"]
        in (module.SURVIVED_TERMINAL, module.PREVAILED_TERMINAL)
    )
    return disposition


def render(report: dict[str, Any]) -> str:
    panel = report["threshold_panel"]
    lines = [
        "P11H pre-run attainability preflight",
        "",
        f"  preflight seed: {report['preflight_seed']}   "
        f"execution seed: {report['execution_seed']} (not read here)",
        f"  ladder: {report['ladder']}",
        f"  protected regimes drawn per run: {report['protected_regimes_drawn_per_run']}",
        f"  universal pool: {', '.join(report['universal_pool'])}",
        f"  thresholds: {report['thresholds']['inherited_from']}",
        "",
        "  gate                                role          support"
        "                    threshold  reason",
    ]
    for entry in panel["gates"]:
        gate = entry["gate"]
        support = entry["support"]
        lines.append(
            f"  {gate['gate_id']:<34}{gate['role']:<14}"
            f"[{support['infimum']:.6f}, {support['supremum']:.6f}]"
            f"   {gate['direction']:>8} {gate['threshold']:<6} {entry['reason']}"
        )
    lines += [
        "",
        f"  panel outcome: {panel['outcome']}",
        f"    unattainable: {', '.join(panel['unattainable']) or 'none'}",
        f"    unconditional hypothesis gates: "
        f"{', '.join(panel['unconditional_hypotheses']) or 'none'}",
        f"    discriminating hypothesis gates: "
        f"{', '.join(panel['discriminating_hypotheses']) or 'none'}",
        "",
        f"  {report['terminal_reach']['label']}",
        f"    admissible worlds registered: {len(report['terminal_reach']['worlds'])}",
        f"    worlds clearing every gate: {len(report['worlds_clearing_every_gate'])}",
        f"    reachable terminals: {report['distinct_terminals']}",
        f"    outcome: {report['terminal_reach']['outcome']}",
    ]
    return "\n".join(lines)


def main(argv: Sequence[str]) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="P11H pre-run attainability preflight")
    parser.add_argument("--json", action="store_true", help="emit the preflight as JSON")
    parser.add_argument(
        "--write",
        action="store_true",
        help=f"write the preflight artifact to {P11H_PREFLIGHT.name}",
    )
    args = parser.parse_args(argv)

    report = preflight()
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.write:
        P11H_PREFLIGHT.write_text(text, encoding="utf-8")
    print(text if args.json else render(report))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI
    raise SystemExit(main(sys.argv[1:]))
