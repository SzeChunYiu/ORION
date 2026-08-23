"""P14B's published positive, asked how many of its eight gates could have said no.

``P14_GATE_ATTAINABILITY_ADJUDICATION_V1.json`` has a ``p14a`` key and a ``p14c``
key. Its own docstring says no P14B threshold "is edited, re-run or relabelled"
--- true, and P14B was never audited either.
``orion.programme.registry_coverage`` names that omission as its sharpest
example: the paper that *invented*
:mod:`orion.programme.gate_attainability` shipped a positive terminal
--- ``P14B_BALANCED_GOVERNANCE_SUPERIORITY_SUPPORTED``, eight gates all ``true``
--- that the instrument was never pointed at. This module points it.

The shipped generator is loaded and driven, never re-implemented:
``papers/paper-14-orion-rse/run_p14b_balanced_governance_v1.py``'s ``main()``
aggregation is replayed here with one thing lifted out as a parameter --- which
implementation occupies the graded ``ORION_RSE_FULL`` slot --- and every other
line of it, the stratified case generator, the gold adjudication, the nine arms,
the seven gate expressions and the terminal expression, taken from that file.
:func:`shipped_bench` reproduces the receipt's committed ``replay_sha256``
``784d57e6…d679e66`` byte for byte, so a verdict below is about the shipped
artifact and not about a local fixture written to come out a particular way.

**The terminal is sound.** P14B's conjunction prints two distinct words over the
worlds its protocol admits: the full contract clears all eight gates, and each of
the four registered component ablations, placed in the graded slot, fails at
least one. That is the property P14A's conjunction did not have, and no
measurement here disturbs it.

**Four of the eight gates could not have gone the other way.** A receipt
reporting "eight gates, all true" reads as eight pieces of evidence, and half of
them are arithmetic over the frozen protocol's whole reachable set:

* ``full_discovery_recall_one`` --- ``useful_discovery_recall`` is ``1.0`` for
  every one of the nine arms in every admissible run. Of the 256 assignments of
  the eight case facts exactly three have gold ``SUPPORTED_RESIDUAL``, and all
  nine registered policies return ``SUPPORTED_RESIDUAL`` on all three: the four
  rule baselines promote supersets of gold, and an ablation removes a check, so a
  policy that reads fewer facts promotes more rather than fewer. The published
  receipt shows the consequence on its face --- all five arms in its ``summary``
  report ``useful_discovery_recall`` of ``1.0``, and the gate reads exactly that.
  This is the same defect :mod:`specification_conformance` reports for P14C's
  identically-named gate; P14B carries it too and its receipt does not say so.
* ``matched_budget`` --- the runner assigns the literal ``BUDGET = 7`` to every
  arm, so the count of distinct decision-budget receipts is ``1`` before any case
  is drawn. This is P14A's ``matched_decision_budget``, and it is registered as a
  ``HYPOTHESIS`` here for the same reason
  :data:`orion.study.p14.governance_gates.GATES` registers it as one.
* ``strongest_baseline_false_promotion_ge_0_05`` --- a
  :class:`~orion.programme.gate_attainability.GateRole.PRECONDITION`, and
  unconditional is what a precondition is *supposed* to be. The strata are equal
  by construction, ``MULTI_REVIEW``'s only error is the ``RETAIN_NEGATIVE``
  stratum, so the statistic is exactly ``1/7 = 0.142857`` in every admissible run
  --- 2.9x its bar, against P14A's ceiling of ``0.042326`` for the same quantity,
  which is the whole reason P14B was frozen.
* ``byte_identical_replay`` --- also a ``PRECONDITION``: a determinism
  certificate about the instrument, the same shape as P14C's
  ``gold_stripped_from_policy_input``, not a finding about the governance
  contract.

So the eight gates carry four discriminating readings, not eight, and the two
questions are separate: the terminal could have gone either way, *and* the count
of gates supporting it is inflated by four. :func:`threshold_panel` returns
``FAIL`` on the two unconditional hypothesis gates while :func:`terminal_reach`
returns ``PASS``, and neither offsets the other.

A smaller thing the count makes visible: ``main()``'s terminal expression is a
conjunction of **seven** gates, not eight. ``byte_identical_replay`` is asserted
by the receipt beside the seven the runner emits and never enters
``all(gates.values())``, so the artifact's own terminal was never a function of
it. :func:`receipt_matches_replay` reports which gates the runner computes and
which the receipt adds; the eighth is registered here all the same, because it is
what the protocol froze and what the receipt publishes.

One further bound, reported and not rolled up. The coordinate P14B actually
leaves free at run time is the seed, and over it the terminal is a constant:
:func:`seed_only_terminal_reach` finds one reachable word across the shipped draw
and two alternate seeds, because the equal-stratum design makes every rate an
exact fraction that no draw can move. The terminal's two words come entirely from
substituting the subject, and the subject's own side of all four discriminating
gates is fixed by ``policy("ORION_RSE_FULL", c)`` being ``return gold(c)`` ---
:func:`graded_arm_divergence` measures ``0`` divergent points of 256, the
circularity ``P14B_PROTOCOL_CONFORMANCE_CORRECTION_V1.md`` already records.

Nothing frozen is touched. P14B's receipt, protocol, seed, thresholds, gold
labels, comparators, arms and terminal stand verbatim, as does its standing
``P14B_NON_AUTHORITATIVE_PROTOCOL_MISMATCH`` downgrade; what is added is the
measurement its own protocol could not supply.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Mapping, Sequence

import numpy as np

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
from orion.programme.refutation_capacity import ModelPoint, TheoryDivergence, divergence_of

REPO_ROOT = Path(__file__).resolve().parents[4]
PAPER = REPO_ROOT / "papers/paper-14-orion-rse"
P14B_SCRIPT = PAPER / "run_p14b_balanced_governance_v1.py"
P14B_RECEIPT = PAPER / "P14B_BALANCED_GOVERNANCE_RESULT_RECEIPT_V1.json"

#: The terminal the shipped P14B receipt publishes.
SHIPPED_TERMINAL = "P14B_BALANCED_GOVERNANCE_SUPERIORITY_SUPPORTED"

#: The other word the runner's conjunction can print.
NEGATIVE_TERMINAL = "P14B_BALANCED_GOVERNANCE_SUPERIORITY_GATE_NOT_MET"

#: The receipt's own ``replay_sha256``. The fidelity anchor.
SHIPPED_RESULT_DIGEST = "784d57e694b9a96828e72bc5e80dfc9e533cf738b568e45a71ce9fd08d679e66"

#: The four partial-governance rule baselines, in the order the runner registers
#: them. The comparator is ``max`` over this tuple by disposition accuracy.
BASELINE_ARMS: tuple[str, ...] = (
    "RAW_POSITIVE",
    "REFLECTION_CHECKLIST",
    "DONOR_AWARE_REVIEW",
    "MULTI_REVIEW",
)

#: The name of the graded slot. Which *implementation* occupies it is the
#: coordinate this module varies, exactly as P14C's audit varies its own.
SUBJECT_SLOT = "ORION_RSE_FULL"

#: The four component ablations, and the fact each one stops reading. The
#: protocol registers them as implementations of the same contract with one
#: component removed, which is what makes them admissible occupants of the
#: graded slot.
ABLATED_FACT: Mapping[str, str] = {
    "ABLATE_DONOR": "donor_owned",
    "ABLATE_FREEZE": "frozen",
    "ABLATE_INTERACTION": "interaction_only",
    "ABLATE_NEGATIVE_HISTORY": "live_negative_history",
}
ABLATION_ARMS: tuple[str, ...] = tuple(ABLATED_FACT)

#: The nine arms ``main()`` scores, in the order it writes them.
ARMS: tuple[str, ...] = BASELINE_ARMS + (SUBJECT_SLOT,) + ABLATION_ARMS

#: The implementations the frozen protocol admits in the graded slot.
SUBJECT_IMPLEMENTATIONS: tuple[str, ...] = (SUBJECT_SLOT,) + ABLATION_ARMS

#: The stratum whose disposition no partial-review contract can reach. Its share
#: of the table is the whole separation, exactly as one fact state was the whole
#: of P14A's --- but here the protocol fixes the share instead of sampling it.
DISCRIMINATING_STRATUM = "RETAIN_NEGATIVE"

#: The eight case facts, in the order ``base_case`` writes them.
FACT_FIELDS: tuple[str, ...] = (
    "positive",
    "evidence_integrity",
    "frozen",
    "identifiable",
    "donor_owned",
    "interaction_only",
    "live_negative_history",
    "material_new_evidence",
)

#: The gold disposition a promotion is scored against.
PROMOTED = "SUPPORTED_RESIDUAL"

#: Seeds registered alongside the shipped one. The protocol fixes seed
#: ``2026082115``, but nothing about the benchmark distinguishes it --- the same
#: admissibility argument :func:`orion.study.p14.governance_gates.declared_worlds`
#: makes for P14A's alternate draw.
ALTERNATE_SEEDS: tuple[int, ...] = (20260821, 2026082116)

_LOCAL_KEYS: tuple[str, ...] = ("n", "fp", "supported", "tp", "correct")
_TALLY_KEYS: tuple[str, ...] = _LOCAL_KEYS + ("retain", "retain_ok", "reopen", "reopen_ok")


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
    """The shipped P14B generator.

    Loaded rather than copied so ``gold``, ``policy``, ``case_for`` and
    ``base_case`` below are the functions that produced the committed receipt.
    Executing the file runs only its constants and definitions --- ``main()``
    sits behind a ``__name__`` guard and would write into ``papers/`` if it were
    called.
    """

    return _load(P14B_SCRIPT, "orion_p14b_balanced_governance")


def shipped_receipt() -> dict[str, Any]:
    return json.loads(P14B_RECEIPT.read_text(encoding="utf-8"))


@dataclass(frozen=True)
class BenchInput:
    """One run of the P14B benchmark: a seed, and the implementation being graded.

    Both coordinates are ones a reader can check against the freeze. The seed is
    the protocol's own ``Split`` section; the subject is its ``Policies and
    resources`` section, which registers the four component ablations as
    implementations of the contract.
    """

    seed: int
    subject: str = SUBJECT_SLOT

    def __post_init__(self) -> None:
        if self.subject not in SUBJECT_IMPLEMENTATIONS:
            raise ValueError(f"{self.subject} is not a registered occupant of the graded slot")


@lru_cache(maxsize=None)
def shipped_input() -> BenchInput:
    """The input that produced the committed receipt.

    A function rather than a module constant so importing this module does not
    read anything out of ``papers/``; the paper lane edits that tree.
    """

    return BenchInput(seed=runner_module().SEED)


def _run_payload(run: BenchInput) -> tuple[dict[str, Any], str]:
    """Replay ``main()``'s aggregation, returning its payload and canonical text.

    Every decision is delegated to the shipped module: ``case_for`` mints each
    stratum's case and consumes the RNG stream exactly as it does in the
    committed run, ``gold`` adjudicates, ``policy`` answers for each arm,
    ``rng.shuffle`` reorders. Only the occupant of the graded slot and the seed
    are ours, and at :func:`shipped_input` the emitted text hashes to
    :data:`SHIPPED_RESULT_DIGEST`.

    Uncached on purpose: ``byte_identical_replay`` is a gate about running the
    generator twice, and a memoized second run would report the cache rather
    than the benchmark.
    """

    module = runner_module()
    rng = np.random.default_rng(run.seed)
    counts = {arm: dict.fromkeys(_TALLY_KEYS, 0) for arm in ARMS}
    family_metrics: list[dict[str, Any]] = []
    for index in range(module.FAMILIES):
        cases: list[tuple[str, dict[str, bool]]] = []
        for stratum in module.STRATA:
            cases.extend((stratum, module.case_for(stratum, rng)) for _ in range(module.PER))
        rng.shuffle(cases)
        local = {arm: dict.fromkeys(_LOCAL_KEYS, 0) for arm in ARMS}
        for stratum, case in cases:
            label = module.gold(case)
            for arm in ARMS:
                pred = module.policy(run.subject if arm == SUBJECT_SLOT else arm, case)
                row = counts[arm]
                for tally in (row, local[arm]):
                    tally["n"] += 1
                    tally["fp"] += int(pred == PROMOTED and label != PROMOTED)
                    tally["supported"] += int(label == PROMOTED)
                    tally["tp"] += int(pred == PROMOTED and label == PROMOTED)
                    tally["correct"] += int(pred == label)
                if stratum == "RETAIN_NEGATIVE":
                    row["retain"] += 1
                    row["retain_ok"] += int(pred == label)
                if stratum == "SUPPORTED_REOPEN":
                    row["reopen"] += 1
                    row["reopen_ok"] += int(pred == label)
        family_metrics.append(
            {
                "family": index,
                "metrics": {
                    arm: {
                        "false_promotion_rate": row["fp"] / row["n"],
                        "disposition_accuracy": row["correct"] / row["n"],
                        "useful_discovery_recall": row["tp"] / row["supported"],
                    }
                    for arm, row in local.items()
                },
            }
        )

    summary = {
        arm: {
            "false_promotion_rate": row["fp"] / row["n"],
            "disposition_accuracy": row["correct"] / row["n"],
            "useful_discovery_recall": row["tp"] / row["supported"],
            "retain_negative_accuracy": row["retain_ok"] / row["retain"] if row["retain"] else 1.0,
            "supported_reopen_accuracy": row["reopen_ok"] / row["reopen"] if row["reopen"] else 1.0,
            "decision_budget_checks": module.BUDGET,
        }
        for arm, row in counts.items()
    }
    strongest = _strongest(summary)
    by_id = {gate.gate_id: gate for gate in GATES}
    gates = {
        gate_id: by_id[gate_id].satisfied_by(reading(summary))
        for gate_id, reading in READINGS.items()
    }
    terminal = SHIPPED_TERMINAL if all(gates.values()) else NEGATIVE_TERMINAL
    payload = {
        "schema": "ORION.P14B.BalancedGovernanceDiscriminator.v1",
        "protocol": "P14B_BALANCED_GOVERNANCE_PROTOCOL_V1.md",
        "seed": run.seed,
        "families": family_metrics,
        "summary": summary,
        "strongest_non_orion_baseline": strongest,
        "gates": gates,
        "terminal": terminal,
    }
    return payload, json.dumps(payload, indent=2, sort_keys=True) + "\n"


@lru_cache(maxsize=None)
def bench(run: BenchInput) -> dict[str, Any]:
    """One replayed run, with the digest ``main()`` would have printed for it."""

    payload, text = _run_payload(run)
    return {**payload, "result_sha256": hashlib.sha256(text.encode()).hexdigest()}


def shipped_bench() -> dict[str, Any]:
    return bench(shipped_input())


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


def replay_is_byte_identical(run: BenchInput) -> float:
    """``1.0`` when two independent executions of the generator emit identical bytes.

    The gate the protocol calls "two byte-identical runs" and the receipt
    publishes as ``byte_identical_replay``. It is the one gate ``main()`` does not
    compute for itself --- the receipt asserts it alongside the seven the runner
    emits --- so it is measured here by running the aggregation twice rather than
    by reading the receipt's own claim back to it.

    The boundary, stated rather than glossed: both executions happen in this
    process, so what is established is that the aggregation is a pure function of
    its seed and its registered policies. It is weaker than
    ``verify_p14c_protocol_adjudication_v2.py``'s two fresh subprocesses, which is
    the check P14C runs. It is enough for the attainability question --- whether
    any admissible world could have made this gate ``false`` --- and not enough to
    re-certify P14B's replay claim independently.
    """

    return float(_run_payload(run)[1] == _run_payload(run)[1])


#: Each gate's statistic, read off a run's ``summary``. Counts and rates rather
#: than the runner's booleans, so an attainability verdict carries the distance
#: to the threshold and not only which side of it a run landed.
READINGS: Mapping[str, Callable[[Mapping[str, Any]], float]] = {
    "full_zero_false_promotion": lambda s: s[SUBJECT_SLOT]["false_promotion_rate"],
    "full_discovery_recall_one": lambda s: s[SUBJECT_SLOT]["useful_discovery_recall"],
    "strongest_baseline_false_promotion_ge_0_05": lambda s: s[_strongest(s)][
        "false_promotion_rate"
    ],
    "accuracy_advantage_ge_0_08": lambda s: s[SUBJECT_SLOT]["disposition_accuracy"]
    - s[_strongest(s)]["disposition_accuracy"],
    "retain_and_reopen_exact": lambda s: min(
        s[SUBJECT_SLOT]["retain_negative_accuracy"], s[SUBJECT_SLOT]["supported_reopen_accuracy"]
    ),
    "each_ablation_worse": _ablations_worse,
    "matched_budget": lambda s: float(len({s[arm]["decision_budget_checks"] for arm in ARMS})),
}

#: The same statistics against a whole run rather than its summary, plus the one
#: gate that is not a function of the summary at all. ``byte_identical_replay``
#: reads two executions, so it cannot be phrased against a single tally.
RUN_READINGS: Mapping[str, Callable[[BenchInput], float]] = {
    **{
        gate_id: (lambda run, gate_id=gate_id: READINGS[gate_id](bench(run)["summary"]))
        for gate_id in READINGS
    },
    "byte_identical_replay": replay_is_byte_identical,
}

#: P14B's eight preregistered gates, transcribed from its protocol's "Endpoints
#: and gate" section and from the ``gates`` block its receipt publishes.
#: Thresholds are the frozen ones; nothing here is relaxed.
#:
#: Two are :data:`~orion.programme.gate_attainability.GateRole.PRECONDITION`.
#: "The strongest non-ORION baseline false-promotes at least 5% of the time" is a
#: statement about the benchmark, settled before a subject is chosen --- it is the
#: gate P14A could not satisfy in any admissible world, which is why P14B exists.
#: "Two byte-identical runs" is a determinism certificate about the instrument,
#: the same shape as P14C's ``gold_stripped_from_policy_input``. Neither asserts
#: anything about the governance contract, and a precondition that holds
#: everywhere is a benchmark built to be measurable.
#:
#: ``matched_budget`` is **not** relabelled. P14A registers the identical gate as
#: ``matched_decision_budget`` with the default ``HYPOTHESIS`` role and counts its
#: unconditional pass against P14A; moving P14B's copy into ``PRECONDITION``
#: would be exactly the relabelling
#: :class:`~orion.programme.gate_attainability.ThresholdPanel` exists to refuse.
GATES: tuple[PreregisteredGate, ...] = (
    PreregisteredGate(
        gate_id="full_zero_false_promotion",
        reads="graded implementation's false promotion rate over the 6,720 protected cases",
        threshold=0.0,
        direction=GateDirection.AT_MOST,
    ),
    PreregisteredGate(
        gate_id="full_discovery_recall_one",
        reads="graded implementation's useful discovery recall",
        threshold=1.0,
    ),
    PreregisteredGate(
        gate_id="strongest_baseline_false_promotion_ge_0_05",
        reads="strongest non-ORION baseline false promotion rate over the balanced strata",
        threshold=0.05,
        role=GateRole.PRECONDITION,
    ),
    PreregisteredGate(
        gate_id="accuracy_advantage_ge_0_08",
        reads="graded implementation's disposition accuracy minus the strongest baseline's",
        threshold=0.08,
    ),
    PreregisteredGate(
        gate_id="retain_and_reopen_exact",
        reads="the lower of the graded implementation's retained-negative and reopen accuracy",
        threshold=1.0,
    ),
    PreregisteredGate(
        gate_id="each_ablation_worse",
        reads="registered component ablations scoring below the graded implementation",
        threshold=4.0,
    ),
    PreregisteredGate(
        gate_id="matched_budget",
        reads="distinct decision-budget receipts across the nine arms",
        threshold=1.0,
        direction=GateDirection.AT_MOST,
    ),
    PreregisteredGate(
        gate_id="byte_identical_replay",
        reads="1.0 when two executions of the frozen generator emit identical bytes",
        threshold=1.0,
        role=GateRole.PRECONDITION,
    ),
)


def fact_space() -> tuple[ModelPoint, ...]:
    """Every assignment of the eight case facts: the space the policies are rules over."""

    return tuple(
        dict(zip(FACT_FIELDS, bits)) for bits in itertools.product((False, True), repeat=8)
    )


def promotable_states() -> tuple[ModelPoint, ...]:
    """The fact states whose gold disposition is a promotion.

    Three of the 256, and the reason ``full_discovery_recall_one`` cannot fail:
    the gate's denominator is exactly these, and no registered arm misses one.
    """

    gold = runner_module().gold
    return tuple(state for state in fact_space() if gold(dict(state)) == PROMOTED)


def arms_missing_a_promotable_state() -> dict[str, int]:
    """Promotable fact states each registered arm declines to promote.

    All zero, which is the derivation ``full_discovery_recall_one``'s declared
    support rests on: the four rule baselines promote supersets of gold, and an
    ablation flips one fact to its permissive value, which can only add
    promotions.
    """

    module = runner_module()
    states = promotable_states()
    return {
        arm: sum(1 for state in states if module.policy(arm, dict(state)) != PROMOTED)
        for arm in ARMS
    }


def graded_arm_divergence() -> TheoryDivergence:
    """How far the graded arm departs from the gold that grades it.

    ``policy("ORION_RSE_FULL", c)`` is ``return gold(c)``. Measured rather than
    quoted, because the number is what composes: zero divergent points is why the
    subject's own side of every gate that reads it is fixed before the run, and
    it is the circularity ``P14B_PROTOCOL_CONFORMANCE_CORRECTION_V1.md`` records.
    """

    module = runner_module()
    return divergence_of(
        lambda point: module.policy(SUBJECT_SLOT, dict(point)),
        theory_id=SUBJECT_SLOT,
        reference=lambda point: module.gold(dict(point)),
        space=fact_space(),
    )


def stratum_share() -> float:
    """Each stratum's share of the table --- ``1/7``, fixed by the protocol.

    P14A left its discriminator's prevalence to a Bernoulli mixture and capped it
    at ``0.042326``. P14B mints ``PER`` cases for each of the seven strata in
    every family, so the share is exact and identical in every admissible run.
    """

    return 1.0 / len(runner_module().STRATA)


class _BranchChoice:
    """An ``rng`` stand-in that takes ``case_for``'s nuisance branch by number.

    ``case_for`` consumes at most one ``integers`` draw --- the material-evidence
    coin for ``SUPPORTED_CLEAN`` and the failure subtype for ``CANNOT_CHECK`` ---
    so driving it once per branch value enumerates every case the stratum can
    mint, exactly, instead of sampling until the set stops growing.
    """

    def __init__(self, branch: int) -> None:
        self._branch = branch

    def integers(self, low: int, high: int) -> int:
        return low + self._branch % (high - low)


def stratum_states() -> dict[str, tuple[ModelPoint, ...]]:
    """Every case the frozen generator can mint for each protected stratum."""

    module = runner_module()
    out: dict[str, tuple[ModelPoint, ...]] = {}
    for stratum in module.STRATA:
        seen: dict[tuple[bool, ...], ModelPoint] = {}
        for branch in range(3):
            case = module.case_for(stratum, _BranchChoice(branch))
            point = {field: bool(case[field]) for field in FACT_FIELDS}
            seen[tuple(point[field] for field in FACT_FIELDS)] = point
        out[stratum] = tuple(seen.values())
    return out


def arm_error_strata() -> dict[str, tuple[str, ...]]:
    """The strata on which each registered arm can depart from gold.

    A stratum is listed when some case the protocol can mint for it is
    adjudicated differently by the arm and by gold. The four rule baselines nest
    --- ``MULTI_REVIEW`` errs only on :data:`DISCRIMINATING_STRATUM` --- which is
    why the comparator selection has nowhere else to land, and why the difficulty
    precondition's statistic is a constant.
    """

    module = runner_module()
    states = stratum_states()
    return {
        arm: tuple(
            stratum
            for stratum, points in states.items()
            if any(
                module.policy(arm, dict(point)) != module.gold(dict(point)) for point in points
            )
        )
        for arm in ARMS
    }


def declared_worlds() -> tuple[AdmissibleWorld, ...]:
    """Runs the frozen P14B protocol admits, over both coordinates it leaves free.

    The register has to be defensible in both directions. Too narrow and an
    unconditional gate is an artifact of the worlds nobody registered; one world
    outside the freeze and the gate is widened rather than measured. These seven
    are the shipped draw, two alternate seeds, and the four component ablations
    the protocol's own "Policies and resources" section registers, each placed in
    the graded slot in turn.
    """

    worlds = [
        AdmissibleWorld(
            world_id="shipped-run",
            admits="the committed run: the protocol's own seed 2026082115 with the full "
            "contract in the graded slot",
            payload=shipped_input(),
        )
    ]
    worlds += [
        AdmissibleWorld(
            world_id=f"alternate-seed-{seed}",
            admits="the same balanced design at another seed; the protocol fixes one seed "
            "but nothing about the benchmark distinguishes it",
            payload=BenchInput(seed=seed),
        )
        for seed in ALTERNATE_SEEDS
    ]
    worlds += [
        AdmissibleWorld(
            world_id=arm.lower().replace("_", "-"),
            admits=(
                f"the protocol registers {arm} as the contract with its {ABLATED_FACT[arm]} "
                "check removed and scores it on the same protected cases; an "
                "implementation that silently lost that check is what the graded slot "
                "would then hold"
            ),
            payload=BenchInput(seed=shipped_input().seed, subject=arm),
        )
        for arm in ABLATION_ARMS
    ]
    return tuple(worlds)


def seed_worlds() -> tuple[AdmissibleWorld, ...]:
    """The sub-register that varies only the draw: the coordinate a run actually has."""

    return tuple(
        world for world in declared_worlds() if world.payload.subject == SUBJECT_SLOT
    )


def _reaches(worlds: Sequence[AdmissibleWorld]) -> tuple[GateReach, ...]:
    return tuple(
        measure_gate_attainability(
            RUN_READINGS[gate.gate_id],
            gate=gate,
            worlds=worlds,
        )
        for gate in GATES
    )


def gate_reaches() -> tuple[GateReach, ...]:
    """Each of P14B's eight gates, measured across the seven admissible worlds."""

    return _reaches(declared_worlds())


def terminal_reach() -> TerminalReach:
    """How many terminals P14B's conjunction could print over its own register."""

    return measure_terminal_reach(
        gate_reaches(), label="P14B balanced governance superiority terminal"
    )


def seed_only_terminal_reach() -> TerminalReach:
    """The same conjunction over the draw alone, with the shipped subject fixed.

    Reported, never rolled up. It does not weaken :func:`terminal_reach` --- the
    ablations are admissible occupants of the graded slot and the terminal really
    does move over them --- but it locates where the movement comes from. The
    balanced design makes every rate an exact fraction of the table, so no seed
    the protocol permits changes a single gate.
    """

    return measure_terminal_reach(
        _reaches(seed_worlds()),
        label="P14B balanced governance terminal over the seed coordinate alone",
    )


def unexercised_hypothesis_gates() -> tuple[str, ...]:
    """Hypothesis gates every admissible world satisfies, so their ``true`` says nothing.

    Reported by name rather than folded into the terminal's verdict, because the
    two facts are different and only one of them blocks. The same discipline
    :func:`orion.study.p14.specification_conformance.unexercised_hypothesis_gates`
    applies to P14C's identically-named recall gate.
    """

    return tuple(
        reach.gate.gate_id
        for reach in gate_reaches()
        if reach.reason is GateReachReason.THRESHOLD_UNCONDITIONAL
        and reach.gate.role is GateRole.HYPOTHESIS
    )


def discriminating_gates() -> tuple[str, ...]:
    """The gates that could have gone either way, whatever their declared role.

    Role-free on purpose. How many of the eight are evidence is a different
    question from which of them block, and a reader counting "eight gates, all
    true" is asking this one.
    """

    return tuple(
        reach.gate.gate_id
        for reach in gate_reaches()
        if reach.reason is GateReachReason.BOTH_OUTCOMES_REACHABLE
    )


def declared_supports() -> dict[str, StatisticSupport]:
    """The interval each of the eight statistics can occupy under the frozen protocol.

    The pre-run half. Every one of these is derivable from the protocol and the
    runner before a seed is drawn --- which is the only moment at which an
    unconditional hypothesis gate is cheap to fix --- and each names the
    coordinate its interval is taken over, because a gate's support is not a
    property of the gate alone.
    """

    module = runner_module()
    share = stratum_share()
    strata = len(module.STRATA)
    subjects = "the implementations the frozen protocol admits in the graded slot"
    nesting = (
        "the seven strata are minted in equal numbers in every family, RAW_POSITIVE errs on "
        "four of them, REFLECTION_CHECKLIST on three, DONOR_AWARE_REVIEW on two and "
        f"MULTI_REVIEW only on {DISCRIMINATING_STRATUM}, so the baselines' error sets nest, "
        f"MULTI_REVIEW is the strongest comparator in every admissible run and its false "
        f"promotion rate is exactly 1/{strata}"
    )
    return {
        "full_zero_false_promotion": StatisticSupport(
            statistic=f"graded implementation's false promotion rate, over {subjects}",
            infimum=0.0,
            supremum=share,
            derivation=(
                "the full contract is the gold function and false-promotes nothing; dropping "
                "the donor, interaction or negative-history check makes the arm promote that "
                f"stratum entire, which is 1/{strata} of the table, and dropping the freeze "
                "check costs only the frozen-failure third of the CANNOT_CHECK stratum"
            ),
        ),
        "full_discovery_recall_one": StatisticSupport(
            statistic=(
                f"graded implementation's useful discovery recall, over {subjects} and over "
                "every seed the protocol permits"
            ),
            infimum=1.0,
            supremum=1.0,
            derivation=(
                "exactly three of the 256 assignments of the eight case facts are adjudicated "
                f"{PROMOTED} by gold, and all nine registered policies return {PROMOTED} on all "
                "three: the rule baselines promote supersets of gold, and an ablation flips one "
                "fact to its permissive value, which can only add promotions. The recall "
                "denominator is those states, so the statistic is 1.0 in every admissible run "
                "whatever occupies the graded slot -- see arms_missing_a_promotable_state"
            ),
        ),
        "strongest_baseline_false_promotion_ge_0_05": StatisticSupport(
            statistic=(
                "strongest non-ORION baseline false promotion rate, over the balanced tables "
                "the frozen protocol admits"
            ),
            infimum=share,
            supremum=share,
            derivation=nesting,
        ),
        "accuracy_advantage_ge_0_08": StatisticSupport(
            statistic=(
                "graded implementation's accuracy gain over the strongest partial contract, "
                f"over {subjects}"
            ),
            infimum=0.0,
            supremum=share,
            derivation=(
                f"{nesting}; the full contract is the gold function and scores 1.0, for a gain "
                f"of exactly 1/{strata}, while ABLATE_DONOR, ABLATE_INTERACTION and "
                "ABLATE_NEGATIVE_HISTORY each land on MULTI_REVIEW's own score for a gain of "
                "0.0, and ABLATE_FREEZE sits between them at whatever share of the "
                "CANNOT_CHECK stratum the draw gives the frozen-failure subtype"
            ),
        ),
        "retain_and_reopen_exact": StatisticSupport(
            statistic=(
                "lower of the graded implementation's retained-negative and reopen accuracy, "
                f"over {subjects}"
            ),
            infimum=0.0,
            supremum=1.0,
            derivation=(
                "the full contract is the gold function and is exact on both protected strata; "
                "ABLATE_NEGATIVE_HISTORY stops reading live_negative_history and is therefore "
                f"wrong on every case of the {DISCRIMINATING_STRATUM} stratum, taking the "
                "statistic to 0.0"
            ),
        ),
        "each_ablation_worse": StatisticSupport(
            statistic=(
                f"registered ablations scoring below the graded implementation, over {subjects}"
            ),
            infimum=0.0,
            supremum=float(len(ABLATION_ARMS)),
            derivation=(
                "the count is over the four registered ablations; the full contract scores 1.0 "
                "and every ablation is strictly below it, while an ablation in the graded slot "
                "is never strictly below itself and is not below the ones that score at least "
                "as well, so the count drops from four"
            ),
        ),
        "matched_budget": StatisticSupport(
            statistic=(
                "distinct decision-budget receipts across the nine arms, over every run the "
                "frozen protocol admits"
            ),
            infimum=1.0,
            supremum=1.0,
            derivation=(
                f"main() writes the module literal BUDGET = {module.BUDGET} into every arm's "
                "summary row; the set of distinct values has one element before any case is "
                "drawn, in every run, for every seed and every occupant of the graded slot"
            ),
        ),
        "byte_identical_replay": StatisticSupport(
            statistic=(
                "1.0 when two executions of the frozen generator emit identical bytes, over "
                "every run the protocol admits"
            ),
            infimum=1.0,
            supremum=1.0,
            derivation=(
                "the payload is a pure function of numpy.random.default_rng(SEED)'s stream and "
                "the registered policies, all of which are deterministic; two executions of the "
                "same input therefore serialize to the same bytes in every admissible run"
            ),
        ),
    }


def threshold_reaches() -> tuple[ThresholdReach, ...]:
    """All eight thresholds against the intervals P14B's own freeze declares."""

    supports = declared_supports()
    return tuple(assess_threshold_support(gate, support=supports[gate.gate_id]) for gate in GATES)


def threshold_panel() -> ThresholdPanel:
    """The pre-run verdict: how much of P14B's battery could have said two things?

    ``FAIL``, and not on an unattainable threshold --- every bar is inside reach,
    which is exactly what P14B was frozen to fix about P14A. It fails because two
    of its six hypothesis gates are satisfied by every value the protocol can
    produce, so the battery carries four claims and publishes eight.
    """

    return assess_threshold_panel(threshold_reaches(), label="P14B balanced governance thresholds")


def receipt_matches_replay() -> dict[str, Any]:
    """Whether the shipped receipt's published numbers are the ones the runner emits.

    The receipt is a hand-written wrapper: it publishes a curated subset of
    ``main()``'s summary and an eighth gate the runner never computes. Checked
    field by field so a verdict here is about P14B's own artifact.
    """

    published = shipped_receipt()
    result = shipped_bench()
    summary = result["summary"]
    mismatched = [
        (arm, key)
        for arm, rates in published["summary"].items()
        for key, value in rates.items()
        if summary[arm][key] != value
    ]
    mismatched += [
        (arm, key)
        for arm, rates in published["ablations"].items()
        for key, value in rates.items()
        if summary[arm][key] != value
    ]
    runner_gates = dict(result["gates"])
    return {
        "digest_reproduced": result["result_sha256"] == published["replay_sha256"],
        "terminal_matches": published["terminal"] == result["terminal"] == SHIPPED_TERMINAL,
        "summary_fields_mismatched": mismatched,
        "gates_the_runner_computes": sorted(runner_gates),
        "gates_only_the_receipt_asserts": sorted(set(published["gates"]) - set(runner_gates)),
        "runner_gates_match_receipt": all(
            published["gates"][gate_id] == value for gate_id, value in runner_gates.items()
        ),
    }


def audit_p14b_balanced_terminal() -> dict[str, Any]:
    """Measure the shipped positive, and roll the verdicts up without compensation."""

    terminal = terminal_reach()
    panel = threshold_panel()
    fidelity = receipt_matches_replay()
    divergence = graded_arm_divergence()

    digest_outcome = Outcome.PASS if fidelity["digest_reproduced"] else Outcome.FAIL
    # Zero divergent points is the P4 failure -- a graded arm recoverable from the
    # construction -- not a missing denominator, so it is a verdict, not a rate.
    grading_outcome = Outcome.PASS if divergence.applied else Outcome.FAIL

    # The seed-only reach is reported and does not roll up: letting a one-word
    # sub-register block would double-count the finding the panel already carries,
    # and letting the two-word full register clear it would be the compensation
    # `worst_outcome` exists to refuse.
    outcome = Outcome.PASS
    for other in (digest_outcome, terminal.outcome, panel.outcome, grading_outcome):
        if other.blocks and not outcome.blocks:
            outcome = other

    return {
        "digest_reproduced": fidelity["digest_reproduced"],
        "receipt_fidelity": fidelity,
        "terminal_reach": terminal,
        "seed_only_terminal_reach": seed_only_terminal_reach(),
        "threshold_panel": panel,
        "graded_arm_divergence": divergence,
        "grading_outcome": grading_outcome,
        "unexercised_hypothesis_gates": unexercised_hypothesis_gates(),
        "discriminating_gates": discriminating_gates(),
        "stratum_share": stratum_share(),
        "arms_missing_a_promotable_state": arms_missing_a_promotable_state(),
        "arm_error_strata": arm_error_strata(),
        "outcome": outcome,
    }


def report_as_json(report: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "digest_reproduced": report["digest_reproduced"],
        "receipt_fidelity": {
            key: (
                [list(item) for item in value]
                if key == "summary_fields_mismatched"
                else value
            )
            for key, value in report["receipt_fidelity"].items()
        },
        "terminal_reach": report["terminal_reach"].as_json(),
        "seed_only_terminal_reach": report["seed_only_terminal_reach"].as_json(),
        "threshold_panel": report["threshold_panel"].as_json(),
        "graded_arm_divergence": report["graded_arm_divergence"].as_json(),
        "grading_outcome": report["grading_outcome"].value,
        "unexercised_hypothesis_gates": list(report["unexercised_hypothesis_gates"]),
        "discriminating_gates": list(report["discriminating_gates"]),
        "stratum_share": report["stratum_share"],
        "arms_missing_a_promotable_state": dict(report["arms_missing_a_promotable_state"]),
        "arm_error_strata": {
            arm: list(strata) for arm, strata in report["arm_error_strata"].items()
        },
        "outcome": report["outcome"].value,
    }


def _render(report: Mapping[str, Any]) -> str:
    terminal = report["terminal_reach"]
    seeds = report["seed_only_terminal_reach"]
    panel = report["threshold_panel"]
    divergence = report["graded_arm_divergence"]
    lines = [
        "P14B balanced governance superiority terminal",
        "",
        f"  committed replay digest reproduced: {report['digest_reproduced']}",
        f"  each stratum's fixed share of the table: {report['stratum_share']:.6f}",
        f"  graded arm vs the gold that grades it: {divergence.points_changed}/"
        f"{divergence.points} points differ ({report['grading_outcome'].value})",
        "",
        f"  {terminal.label}",
        f"    admissible worlds registered: {len(terminal.world_ids)}",
        f"    worlds clearing every gate: {len(terminal.clearing)}",
        f"    reachable terminals: {terminal.distinct_terminals}",
        f"    no admissible world satisfies: {', '.join(terminal.unattainable) or 'none'}",
        f"    every admissible world satisfies: {', '.join(terminal.unconditional) or 'none'}",
        "",
        "    gate                                          best     margin  reason",
    ]
    for reach in terminal.reaches:
        lines.append(
            f"    {reach.gate.gate_id:<44} {reach.best_value:8.6f} "
            f"{reach.attainment_margin:+10.6f}  {reach.reason.value}"
        )
    lines += [
        "",
        f"  gates that could have gone either way: {len(report['discriminating_gates'])}"
        f"/{len(terminal.reaches)} "
        f"({', '.join(report['discriminating_gates']) or 'none'})",
        "  hypothesis gates no admissible world can fail: "
        + (", ".join(report["unexercised_hypothesis_gates"]) or "none"),
        "",
        f"  {seeds.label}: {seeds.distinct_terminals} reachable terminal(s) over "
        f"{len(seeds.world_ids)} draws (reported; does not roll up)",
        "",
        f"  {panel.label}, before the run: {panel.outcome.value}",
    ]
    for reach in panel.reaches:
        lines.append(
            f"    {reach.gate.gate_id:<44} reach "
            f"[{reach.support.infimum:.6f}, {reach.support.supremum:.6f}] "
            f"vs {reach.gate.threshold:<5} {reach.reason.value}"
        )
    lines += [
        "",
        f"  outcome: {report['outcome'].value}",
        "",
        "  P14B's receipt, protocol, seed, thresholds, gold labels, comparators and",
        "  terminal are retained verbatim; only the reading of what its eight gates",
        "  established changes.",
    ]
    return "\n".join(lines)


def main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit the audit as JSON")
    args = parser.parse_args(argv)

    report = audit_p14b_balanced_terminal()
    payload = report_as_json(report)
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else _render(report))
    return 3 if Outcome(payload["outcome"]).blocks else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))


__all__ = [
    "ABLATED_FACT",
    "ABLATION_ARMS",
    "ALTERNATE_SEEDS",
    "ARMS",
    "BASELINE_ARMS",
    "DISCRIMINATING_STRATUM",
    "FACT_FIELDS",
    "GATES",
    "NEGATIVE_TERMINAL",
    "PROMOTED",
    "READINGS",
    "RUN_READINGS",
    "SHIPPED_RESULT_DIGEST",
    "SHIPPED_TERMINAL",
    "SUBJECT_IMPLEMENTATIONS",
    "SUBJECT_SLOT",
    "BenchInput",
    "arm_error_strata",
    "arms_missing_a_promotable_state",
    "audit_p14b_balanced_terminal",
    "bench",
    "declared_supports",
    "declared_worlds",
    "discriminating_gates",
    "fact_space",
    "gate_reaches",
    "graded_arm_divergence",
    "main",
    "promotable_states",
    "receipt_matches_replay",
    "replay_is_byte_identical",
    "report_as_json",
    "runner_module",
    "seed_only_terminal_reach",
    "seed_worlds",
    "shipped_bench",
    "shipped_input",
    "shipped_receipt",
    "stratum_share",
    "stratum_states",
    "terminal_reach",
    "threshold_panel",
    "threshold_reaches",
    "unexercised_hypothesis_gates",
]
